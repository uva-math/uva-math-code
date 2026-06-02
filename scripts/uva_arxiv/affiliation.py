"""UVA affiliation evidence extraction from fetched arXiv sources."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable, TextIO

try:
    from . import env, sources
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.uva_arxiv import env, sources


DEFAULT_CACHE_NAME = "affiliation.sqlite"
MAX_TEXT_FILE_BYTES = 2_000_000


class AffiliationError(RuntimeError):
    """Raised when source-affiliation evidence cannot be scanned."""


@dataclass(frozen=True)
class AffiliationPatternSet:
    positive: tuple[str, ...]
    negative: tuple[str, ...]


@dataclass(frozen=True)
class AffiliationMatch:
    kind: str
    pattern: str
    file: str
    line_number: int
    snippet: str
    source: str


@dataclass(frozen=True)
class AffiliationScanResult:
    arxiv_id: str
    safe_id: str
    source_dir: str
    evidence: str
    checked_files: int
    positive_count: int
    negative_count: int
    matches: tuple[AffiliationMatch, ...]
    notes: str


def load_patterns(path: Path) -> AffiliationPatternSet:
    try:
        loaded = env.load_yaml_mapping_file(path)
    except env.ConfigError as exc:
        raise AffiliationError(str(exc)) from exc
    positive = tuple(str(item).strip() for item in loaded.get("positive", []) if str(item).strip())
    negative = tuple(str(item).strip() for item in loaded.get("negative", []) if str(item).strip())
    if not positive and not negative:
        raise AffiliationError(f"no affiliation patterns found in {path}")
    return AffiliationPatternSet(positive=positive, negative=negative)


def _compile_patterns(patterns: Iterable[str]) -> list[tuple[str, re.Pattern[str]]]:
    return [
        (pattern, re.compile(re.escape(pattern), re.IGNORECASE))
        for pattern in patterns
        if pattern
    ]


def _source_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".tex", ".ltx", ".sty", ".cls", ".bbl", ".bib"}:
        return "tex"
    if suffix == ".pdf":
        return "pdf"
    return "text"


def _read_text(path: Path) -> str | None:
    payload = path.read_bytes()
    if b"\x00" in payload[:4096]:
        return None
    for encoding in ("utf-8", "latin-1"):
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def _snippet(line: str, limit: int = 240) -> str:
    text = " ".join(line.strip().split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _evidence_state(positive_count: int, negative_count: int, missing_source: bool) -> str:
    if missing_source:
        return "missing_source"
    if negative_count:
        return "conflict"
    if positive_count:
        return "confirmed"
    return "absent"


def scan_source_dir(
    arxiv_id: str,
    source_dir: Path,
    patterns: AffiliationPatternSet,
) -> AffiliationScanResult:
    normalized_id = sources.normalize_arxiv_id(arxiv_id)
    safe_id = sources.safe_source_dir_name(normalized_id)
    positive_patterns = _compile_patterns(patterns.positive)
    negative_patterns = _compile_patterns(patterns.negative)

    if not source_dir.is_dir():
        return AffiliationScanResult(
            arxiv_id=normalized_id,
            safe_id=safe_id,
            source_dir=str(source_dir),
            evidence="missing_source",
            checked_files=0,
            positive_count=0,
            negative_count=0,
            matches=(),
            notes="source directory is missing; this is not a rejection reason",
        )

    matches: list[AffiliationMatch] = []
    checked_files = 0
    source_file_count = 0
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        source_file_count += 1
        if path.stat().st_size > MAX_TEXT_FILE_BYTES:
            continue
        text = _read_text(path)
        if text is None:
            continue
        checked_files += 1
        rel_path = str(path.relative_to(source_dir))
        source_kind = _source_kind(path)
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern, compiled in positive_patterns:
                if compiled.search(line):
                    matches.append(
                        AffiliationMatch(
                            kind="positive",
                            pattern=pattern,
                            file=rel_path,
                            line_number=line_number,
                            snippet=_snippet(line),
                            source=source_kind,
                        )
                    )
            for pattern, compiled in negative_patterns:
                if compiled.search(line):
                    matches.append(
                        AffiliationMatch(
                            kind="negative",
                            pattern=pattern,
                            file=rel_path,
                            line_number=line_number,
                            snippet=_snippet(line),
                            source=source_kind,
                        )
                    )

    positive_count = sum(1 for match in matches if match.kind == "positive")
    negative_count = sum(1 for match in matches if match.kind == "negative")
    if checked_files == 0:
        evidence = "unreadable_source" if source_file_count else "empty_source"
        notes = (
            "source directory has files, but none were readable text files"
            if source_file_count
            else "source directory contains no files"
        )
        return AffiliationScanResult(
            arxiv_id=normalized_id,
            safe_id=safe_id,
            source_dir=str(source_dir),
            evidence=evidence,
            checked_files=0,
            positive_count=0,
            negative_count=0,
            matches=(),
            notes=notes,
        )

    evidence = _evidence_state(positive_count, negative_count, missing_source=False)
    notes = (
        "absence of UVA evidence is an evidence state, not a rejection reason"
        if evidence == "absent"
        else "source affiliation evidence scanned"
    )
    return AffiliationScanResult(
        arxiv_id=normalized_id,
        safe_id=safe_id,
        source_dir=str(source_dir),
        evidence=evidence,
        checked_files=checked_files,
        positive_count=positive_count,
        negative_count=negative_count,
        matches=tuple(matches),
        notes=notes,
    )


def scan_affiliation(
    config: env.UvaArxivConfig,
    arxiv_id: str,
    sources_dir: Path | None = None,
    patterns_path: Path | None = None,
    cache_path: Path | None = None,
    write_cache: bool = True,
) -> AffiliationScanResult:
    patterns = load_patterns(patterns_path or config.data_dir / "affiliation_patterns.yml")
    source_dir = sources.source_dir_for_id(Path(sources_dir or config.arxiv_sources_dir), arxiv_id)
    result = scan_source_dir(arxiv_id, source_dir, patterns)
    if write_cache:
        store_scan_result(result, cache_path or config.cache_dir / DEFAULT_CACHE_NAME)
    return result


def _result_payload(result: AffiliationScanResult) -> str:
    data = asdict(result)
    data["matches"] = [asdict(match) for match in result.matches]
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def store_scan_result(result: AffiliationScanResult, cache_path: Path) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    scanned_at = datetime.now(UTC).isoformat(timespec="seconds")
    with sqlite3.connect(cache_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS affiliation_scans (
                arxiv_id TEXT PRIMARY KEY,
                evidence TEXT NOT NULL,
                scanned_at TEXT NOT NULL,
                source_dir TEXT NOT NULL,
                positive_count INTEGER NOT NULL,
                negative_count INTEGER NOT NULL,
                checked_files INTEGER NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            INSERT INTO affiliation_scans (
                arxiv_id,
                evidence,
                scanned_at,
                source_dir,
                positive_count,
                negative_count,
                checked_files,
                payload_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(arxiv_id) DO UPDATE SET
                evidence = excluded.evidence,
                scanned_at = excluded.scanned_at,
                source_dir = excluded.source_dir,
                positive_count = excluded.positive_count,
                negative_count = excluded.negative_count,
                checked_files = excluded.checked_files,
                payload_json = excluded.payload_json
            """,
            (
                result.arxiv_id,
                result.evidence,
                scanned_at,
                result.source_dir,
                result.positive_count,
                result.negative_count,
                result.checked_files,
                _result_payload(result),
            ),
        )


def print_scan_result(
    result: AffiliationScanResult,
    cache_path: Path | None = None,
    out: TextIO = sys.stdout,
) -> None:
    print(f"arxiv_id: {result.arxiv_id}", file=out)
    print(f"safe_id: {result.safe_id}", file=out)
    print(f"source_dir: {result.source_dir}", file=out)
    print(f"evidence: {result.evidence}", file=out)
    print(f"checked_files: {result.checked_files}", file=out)
    print(f"positive_matches: {result.positive_count}", file=out)
    print(f"negative_matches: {result.negative_count}", file=out)
    print(f"notes: {result.notes}", file=out)
    if cache_path is not None:
        print(f"cache_path: {cache_path}", file=out)
    for match in result.matches[:20]:
        print(
            "match: "
            f"{match.kind} {match.file}:{match.line_number} "
            f"{match.pattern} ({match.source})",
            file=out,
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan fetched arXiv sources for UVA affiliation evidence.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan = subparsers.add_parser("scan", help="Scan one fetched arXiv source directory.")
    scan.add_argument("--id", required=True, dest="arxiv_id", help="arXiv ID to scan.")
    scan.add_argument("--sources-dir", type=Path, help="Override configured shared source corpus.")
    scan.add_argument("--patterns", type=Path, help="Override affiliation pattern YAML.")
    scan.add_argument("--cache-path", type=Path, help="Override cache SQLite path.")
    scan.add_argument("--no-cache", action="store_true", help="Do not write the cache-side scan record.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    config = env.load_config(ensure_dirs=True)

    if args.command == "scan":
        cache_path = args.cache_path or config.cache_dir / DEFAULT_CACHE_NAME
        result = scan_affiliation(
            config=config,
            arxiv_id=args.arxiv_id,
            sources_dir=args.sources_dir,
            patterns_path=args.patterns,
            cache_path=cache_path,
            write_cache=not args.no_cache,
        )
        print_scan_result(result, None if args.no_cache else cache_path)
        return 0
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

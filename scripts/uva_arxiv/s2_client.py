"""Semantic Scholar smoke client and cache."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, TextIO

try:
    from . import env, sources
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.uva_arxiv import env, sources


S2_PAPER_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper"
DEFAULT_CACHE_NAME = "s2.sqlite"
DEFAULT_TIMEOUT_SECONDS = 30
S2_FIELDS = (
    "externalIds",
    "title",
    "year",
    "authors",
    "venue",
    "journal",
    "publicationVenue",
    "publicationDate",
    "openAccessPdf",
    "url",
)

HttpGet = Callable[[urllib.request.Request, int], bytes]


class SemanticScholarError(RuntimeError):
    """Raised when a Semantic Scholar request cannot be completed."""


class SemanticScholarRateLimitError(SemanticScholarError):
    """Raised when Semantic Scholar returns a rate-limit response."""

    def __init__(self, retry_after: str | None = None) -> None:
        self.retry_after = retry_after
        message = "Semantic Scholar rate limit reached"
        if retry_after:
            message += f"; retry_after={retry_after}"
        super().__init__(message)


@dataclass(frozen=True)
class MetadataConflict:
    field: str
    expected: str
    observed: str
    notes: str


@dataclass(frozen=True)
class SemanticScholarSmokeResult:
    arxiv_id: str
    status: str
    cache_hit: bool
    api_key_present: bool
    doi: str | None
    title: str | None
    year: int | None
    publication_date: str | None
    venue: str | None
    journal: str | None
    authors: tuple[dict[str, Any], ...]
    incomplete_fields: tuple[str, ...]
    conflicts: tuple[MetadataConflict, ...]
    raw_json: dict[str, Any] | None
    notes: str

    @property
    def incomplete_metadata(self) -> bool:
        return bool(self.incomplete_fields)


def normalize_arxiv_id(arxiv_id: str) -> str:
    return sources.normalize_arxiv_id(arxiv_id)


def default_http_get(request: urllib.request.Request, timeout: int) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise SemanticScholarRateLimitError(exc.headers.get("Retry-After")) from exc
        raise SemanticScholarError(
            f"Semantic Scholar request failed with HTTP {exc.code}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SemanticScholarError(f"Semantic Scholar request failed: {exc}") from exc


def build_s2_url(arxiv_id: str, endpoint: str = S2_PAPER_ENDPOINT) -> str:
    paper_id = urllib.parse.quote(f"arXiv:{normalize_arxiv_id(arxiv_id)}", safe=":")
    query = urllib.parse.urlencode({"fields": ",".join(S2_FIELDS)})
    return f"{endpoint.rstrip('/')}/{paper_id}?{query}"


def build_s2_request(url: str, api_key: str | None) -> urllib.request.Request:
    headers = {"User-Agent": "uva-math-arxiv-phase1-s2/0.1"}
    if api_key:
        headers["x-api-key"] = api_key
    return urllib.request.Request(url, headers=headers)


def _json_loads(payload: bytes) -> dict[str, Any]:
    try:
        loaded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SemanticScholarError("Semantic Scholar returned invalid JSON") from exc
    if not isinstance(loaded, dict):
        raise SemanticScholarError("Semantic Scholar returned non-object JSON")
    return loaded


def _normalize_compare_arxiv(value: str | None) -> str:
    if not value:
        return ""
    try:
        return normalize_arxiv_id(value).lower()
    except Exception:
        return value.strip().lower()


def _as_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _journal_name(raw: Any) -> str | None:
    if isinstance(raw, dict):
        return _as_text(raw.get("name"))
    return _as_text(raw)


def _publication_venue_name(raw: Any) -> str | None:
    if isinstance(raw, dict):
        return _as_text(raw.get("name"))
    return None


def _authors(raw: Any) -> tuple[dict[str, Any], ...]:
    if not isinstance(raw, list):
        return ()
    authors: list[dict[str, Any]] = []
    for author in raw:
        if not isinstance(author, dict):
            continue
        name = _as_text(author.get("name"))
        author_id = _as_text(author.get("authorId"))
        if name or author_id:
            authors.append({"name": name, "authorId": author_id})
    return tuple(authors)


def _status(incomplete_fields: tuple[str, ...], conflicts: tuple[MetadataConflict, ...]) -> str:
    if conflicts:
        return "conflict"
    if incomplete_fields:
        return "incomplete"
    return "complete"


def normalize_s2_payload(
    arxiv_id: str,
    payload: dict[str, Any],
    cache_hit: bool,
    api_key_present: bool,
) -> SemanticScholarSmokeResult:
    normalized_id = normalize_arxiv_id(arxiv_id)
    external_ids = payload.get("externalIds") if isinstance(payload.get("externalIds"), dict) else {}
    doi = _as_text(external_ids.get("DOI"))
    observed_arxiv = _as_text(external_ids.get("ArXiv"))
    title = _as_text(payload.get("title"))
    year = _as_int(payload.get("year"))
    publication_date = _as_text(payload.get("publicationDate"))
    journal = _journal_name(payload.get("journal"))
    venue = _as_text(payload.get("venue")) or _publication_venue_name(payload.get("publicationVenue"))
    authors = _authors(payload.get("authors"))

    conflicts: list[MetadataConflict] = []
    if observed_arxiv and _normalize_compare_arxiv(observed_arxiv) != normalized_id.lower():
        conflicts.append(
            MetadataConflict(
                field="arxiv_id",
                expected=normalized_id,
                observed=observed_arxiv,
                notes="Semantic Scholar externalIds.ArXiv does not match the requested arXiv ID",
            )
        )

    incomplete_fields = tuple(
        field
        for field, value in (
            ("doi", doi),
            ("title", title),
            ("authors", authors),
            ("venue_or_journal", venue or journal),
            ("publication_date", publication_date),
        )
        if not value
    )
    conflicts_tuple = tuple(conflicts)
    status = _status(incomplete_fields, conflicts_tuple)
    notes = "missing metadata is incomplete metadata, not publication or department-scope evidence"
    if conflicts_tuple:
        notes = "metadata conflict recorded for manual review; this is not a rejection decision"
    elif not api_key_present:
        notes += "; S2_API_KEY missing, request used unauthenticated access"

    return SemanticScholarSmokeResult(
        arxiv_id=normalized_id,
        status=status,
        cache_hit=cache_hit,
        api_key_present=api_key_present,
        doi=doi,
        title=title,
        year=year,
        publication_date=publication_date,
        venue=venue,
        journal=journal,
        authors=authors,
        incomplete_fields=incomplete_fields,
        conflicts=conflicts_tuple,
        raw_json=payload,
        notes=notes,
    )


def _connect_cache(cache_path: Path) -> sqlite3.Connection:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(cache_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_cache(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS s2_papers (
            arxiv_id TEXT PRIMARY KEY,
            fetched_at TEXT NOT NULL,
            status TEXT NOT NULL,
            doi TEXT,
            title TEXT,
            year INTEGER,
            publication_date TEXT,
            venue TEXT,
            journal TEXT,
            authors_json TEXT NOT NULL,
            incomplete_fields_json TEXT NOT NULL,
            conflicts_json TEXT NOT NULL,
            raw_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS metadata_conflicts (
            source TEXT NOT NULL,
            identifier TEXT NOT NULL,
            field TEXT NOT NULL,
            expected TEXT NOT NULL,
            observed TEXT NOT NULL,
            notes TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            PRIMARY KEY (source, identifier, field, expected, observed)
        )
        """
    )


def load_cached_result(
    cache_path: Path,
    arxiv_id: str,
    api_key_present: bool = False,
) -> SemanticScholarSmokeResult | None:
    normalized_id = normalize_arxiv_id(arxiv_id)
    if not cache_path.exists():
        return None
    with _connect_cache(cache_path) as conn:
        init_cache(conn)
        row = conn.execute(
            "SELECT * FROM s2_papers WHERE arxiv_id = ?",
            (normalized_id,),
        ).fetchone()
    if row is None:
        return None
    conflicts = tuple(
        MetadataConflict(**item) for item in json.loads(row["conflicts_json"])
    )
    return SemanticScholarSmokeResult(
        arxiv_id=row["arxiv_id"],
        status=row["status"],
        cache_hit=True,
        api_key_present=api_key_present,
        doi=row["doi"],
        title=row["title"],
        year=row["year"],
        publication_date=row["publication_date"],
        venue=row["venue"],
        journal=row["journal"],
        authors=tuple(json.loads(row["authors_json"])),
        incomplete_fields=tuple(json.loads(row["incomplete_fields_json"])),
        conflicts=conflicts,
        raw_json=json.loads(row["raw_json"]),
        notes="loaded from Semantic Scholar cache; missing metadata remains non-evidence",
    )


def store_result(result: SemanticScholarSmokeResult, cache_path: Path) -> None:
    if result.raw_json is None:
        return
    fetched_at = datetime.now(UTC).isoformat(timespec="seconds")
    with _connect_cache(cache_path) as conn:
        init_cache(conn)
        with conn:
            conn.execute(
                """
                INSERT INTO s2_papers (
                    arxiv_id,
                    fetched_at,
                    status,
                    doi,
                    title,
                    year,
                    publication_date,
                    venue,
                    journal,
                    authors_json,
                    incomplete_fields_json,
                    conflicts_json,
                    raw_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(arxiv_id) DO UPDATE SET
                    fetched_at = excluded.fetched_at,
                    status = excluded.status,
                    doi = excluded.doi,
                    title = excluded.title,
                    year = excluded.year,
                    publication_date = excluded.publication_date,
                    venue = excluded.venue,
                    journal = excluded.journal,
                    authors_json = excluded.authors_json,
                    incomplete_fields_json = excluded.incomplete_fields_json,
                    conflicts_json = excluded.conflicts_json,
                    raw_json = excluded.raw_json
                """,
                (
                    result.arxiv_id,
                    fetched_at,
                    result.status,
                    result.doi,
                    result.title,
                    result.year,
                    result.publication_date,
                    result.venue,
                    result.journal,
                    json.dumps(result.authors, ensure_ascii=False, sort_keys=True),
                    json.dumps(result.incomplete_fields, ensure_ascii=False, sort_keys=True),
                    json.dumps(
                        [asdict(conflict) for conflict in result.conflicts],
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    json.dumps(result.raw_json, ensure_ascii=False, sort_keys=True),
                ),
            )
            conn.execute(
                "DELETE FROM metadata_conflicts WHERE source = ? AND identifier = ?",
                ("semantic_scholar", result.arxiv_id),
            )
            for conflict in result.conflicts:
                conn.execute(
                    """
                    INSERT INTO metadata_conflicts (
                        source,
                        identifier,
                        field,
                        expected,
                        observed,
                        notes,
                        recorded_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "semantic_scholar",
                        result.arxiv_id,
                        conflict.field,
                        conflict.expected,
                        conflict.observed,
                        conflict.notes,
                        fetched_at,
                    ),
                )


def _error_result(
    arxiv_id: str,
    status: str,
    api_key_present: bool,
    notes: str,
) -> SemanticScholarSmokeResult:
    return SemanticScholarSmokeResult(
        arxiv_id=normalize_arxiv_id(arxiv_id),
        status=status,
        cache_hit=False,
        api_key_present=api_key_present,
        doi=None,
        title=None,
        year=None,
        publication_date=None,
        venue=None,
        journal=None,
        authors=(),
        incomplete_fields=(),
        conflicts=(),
        raw_json=None,
        notes=notes,
    )


def smoke_s2(
    arxiv_id: str,
    cache_path: Path,
    api_key: str | None = None,
    http_get: HttpGet = default_http_get,
    endpoint: str = S2_PAPER_ENDPOINT,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    use_cache: bool = True,
    refresh: bool = False,
    write_cache: bool = True,
) -> SemanticScholarSmokeResult:
    env.normalize_api_env()
    if api_key is None:
        api_key = os.environ.get("S2_API_KEY")
    api_key_present = bool(api_key)

    if use_cache and not refresh:
        cached = load_cached_result(cache_path, arxiv_id, api_key_present=api_key_present)
        if cached is not None:
            return cached

    url = build_s2_url(arxiv_id, endpoint=endpoint)
    request = build_s2_request(url, api_key)
    try:
        payload = _json_loads(http_get(request, timeout))
    except SemanticScholarRateLimitError as exc:
        return _error_result(
            arxiv_id,
            "rate_limited",
            api_key_present,
            str(exc),
        )
    except SemanticScholarError as exc:
        return _error_result(
            arxiv_id,
            "request_error",
            api_key_present,
            str(exc),
        )

    result = normalize_s2_payload(
        arxiv_id=arxiv_id,
        payload=payload,
        cache_hit=False,
        api_key_present=api_key_present,
    )
    if write_cache:
        store_result(result, cache_path)
    return result


def print_smoke_result(
    result: SemanticScholarSmokeResult,
    cache_path: Path,
    out: TextIO = sys.stdout,
) -> None:
    print(f"arxiv_id: {result.arxiv_id}", file=out)
    print(f"cache_path: {cache_path}", file=out)
    print(f"cache_hit: {'true' if result.cache_hit else 'false'}", file=out)
    print(f"S2_API_KEY: {'present' if result.api_key_present else 'missing'}", file=out)
    print(f"status: {result.status}", file=out)
    print(f"doi: {result.doi or 'missing'}", file=out)
    print(f"title: {result.title or 'missing'}", file=out)
    print(f"year: {result.year if result.year is not None else 'missing'}", file=out)
    print(f"publication_date: {result.publication_date or 'missing'}", file=out)
    print(f"venue: {result.venue or 'missing'}", file=out)
    print(f"journal: {result.journal or 'missing'}", file=out)
    print(f"authors_count: {len(result.authors)}", file=out)
    print(f"incomplete_metadata: {'true' if result.incomplete_metadata else 'false'}", file=out)
    if result.incomplete_fields:
        print(f"incomplete_fields: {','.join(result.incomplete_fields)}", file=out)
    print(f"conflicts_count: {len(result.conflicts)}", file=out)
    for conflict in result.conflicts:
        print(
            "conflict: "
            f"{conflict.field} expected={conflict.expected} observed={conflict.observed}",
            file=out,
        )
    print("publication_scope_evidence: not_evidence", file=out)
    print(f"notes: {result.notes}", file=out)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Semantic Scholar UVA arXiv smoke client.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    smoke = subparsers.add_parser("smoke", help="Fetch/cache one Semantic Scholar arXiv record.")
    smoke.add_argument("--id", required=True, dest="arxiv_id", help="arXiv ID to check.")
    smoke.add_argument("--cache-path", type=Path, help="Override cache SQLite path.")
    smoke.add_argument("--endpoint", default=S2_PAPER_ENDPOINT, help="Override Semantic Scholar endpoint.")
    smoke.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    smoke.add_argument("--refresh", action="store_true", help="Bypass an existing cache row.")
    smoke.add_argument("--no-cache", action="store_true", help="Do not read or write the cache.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    config = env.load_config(ensure_dirs=True)

    if args.command == "smoke":
        cache_path = args.cache_path or config.cache_dir / DEFAULT_CACHE_NAME
        result = smoke_s2(
            arxiv_id=args.arxiv_id,
            cache_path=cache_path,
            endpoint=args.endpoint,
            timeout=args.timeout,
            use_cache=not args.no_cache,
            refresh=args.refresh,
            write_cache=not args.no_cache,
        )
        print_smoke_result(result, cache_path)
        return 1 if result.status in {"rate_limited", "request_error"} else 0
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

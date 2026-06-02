"""CrossRef smoke client and cache."""

from __future__ import annotations

import argparse
import json
import os
import re
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
    from . import env
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.uva_arxiv import env


CROSSREF_WORKS_ENDPOINT = "https://api.crossref.org/works"
DEFAULT_CACHE_NAME = "crossref.sqlite"
DEFAULT_TIMEOUT_SECONDS = 30

HttpGet = Callable[[urllib.request.Request, int], bytes]


class CrossRefError(RuntimeError):
    """Raised when a CrossRef request cannot be completed."""


class CrossRefRateLimitError(CrossRefError):
    """Raised when CrossRef returns a rate-limit response."""

    def __init__(self, retry_after: str | None = None) -> None:
        self.retry_after = retry_after
        message = "CrossRef rate limit reached"
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
class CrossRefSmokeResult:
    doi: str
    status: str
    cache_hit: bool
    mailto_present: bool
    api_key_present: bool
    metadata_doi: str | None
    title: str | None
    container_title: str | None
    short_container_title: str | None
    published_date: str | None
    issued_date: str | None
    authors: tuple[dict[str, Any], ...]
    incomplete_fields: tuple[str, ...]
    conflicts: tuple[MetadataConflict, ...]
    raw_json: dict[str, Any] | None
    notes: str

    @property
    def incomplete_metadata(self) -> bool:
        return bool(self.incomplete_fields)


def normalize_doi(doi: str) -> str:
    value = doi.strip()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^doi:\s*", "", value, flags=re.IGNORECASE)
    value = value.strip()
    if not value:
        raise CrossRefError("DOI is required")
    return value.lower()


def default_http_get(request: urllib.request.Request, timeout: int) -> bytes:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise CrossRefRateLimitError(exc.headers.get("Retry-After")) from exc
        raise CrossRefError(f"CrossRef request failed with HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise CrossRefError(f"CrossRef request failed: {exc}") from exc


def build_crossref_url(
    doi: str,
    endpoint: str = CROSSREF_WORKS_ENDPOINT,
    mailto: str | None = None,
) -> str:
    quoted_doi = urllib.parse.quote(normalize_doi(doi), safe="")
    url = f"{endpoint.rstrip('/')}/{quoted_doi}"
    if mailto:
        url += "?" + urllib.parse.urlencode({"mailto": mailto})
    return url


def build_crossref_request(url: str, api_key: str | None) -> urllib.request.Request:
    headers = {"User-Agent": "uva-math-arxiv-phase1-crossref/0.1"}
    if api_key:
        headers["X-API-KEY"] = api_key
    return urllib.request.Request(url, headers=headers)


def _json_loads(payload: bytes) -> dict[str, Any]:
    try:
        loaded = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CrossRefError("CrossRef returned invalid JSON") from exc
    if not isinstance(loaded, dict):
        raise CrossRefError("CrossRef returned non-object JSON")
    return loaded


def _as_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        for item in value:
            text = _as_text(item)
            if text:
                return text
        return None
    text = str(value).strip()
    return text or None


def _date_from_parts(raw: Any) -> str | None:
    if not isinstance(raw, dict):
        return None
    parts = raw.get("date-parts")
    if not isinstance(parts, list) or not parts:
        return None
    first = parts[0]
    if not isinstance(first, list) or not first:
        return None
    values: list[int] = []
    for item in first[:3]:
        try:
            values.append(int(item))
        except (TypeError, ValueError):
            break
    if not values:
        return None
    if len(values) == 1:
        return f"{values[0]:04d}"
    if len(values) == 2:
        return f"{values[0]:04d}-{values[1]:02d}"
    return f"{values[0]:04d}-{values[1]:02d}-{values[2]:02d}"


def _best_published_date(message: dict[str, Any]) -> str | None:
    for key in ("published-print", "published-online", "published", "issued"):
        value = _date_from_parts(message.get(key))
        if value:
            return value
    return None


def _authors(raw: Any) -> tuple[dict[str, Any], ...]:
    if not isinstance(raw, list):
        return ()
    authors: list[dict[str, Any]] = []
    for author in raw:
        if not isinstance(author, dict):
            continue
        given = _as_text(author.get("given"))
        family = _as_text(author.get("family"))
        name = " ".join(part for part in (given, family) if part) or _as_text(author.get("name"))
        affiliations = []
        raw_affiliations = author.get("affiliation")
        if isinstance(raw_affiliations, list):
            affiliations = [
                text
                for item in raw_affiliations
                if isinstance(item, dict)
                for text in [_as_text(item.get("name"))]
                if text
            ]
        if name or author.get("ORCID"):
            authors.append(
                {
                    "name": name or None,
                    "orcid": _as_text(author.get("ORCID")),
                    "affiliations": affiliations,
                }
            )
    return tuple(authors)


def _message_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    message = payload.get("message")
    if not isinstance(message, dict):
        raise CrossRefError("CrossRef payload is missing message object")
    return message


def _status(incomplete_fields: tuple[str, ...], conflicts: tuple[MetadataConflict, ...]) -> str:
    if conflicts:
        return "conflict"
    if incomplete_fields:
        return "incomplete"
    return "complete"


def normalize_crossref_payload(
    doi: str,
    payload: dict[str, Any],
    cache_hit: bool,
    mailto_present: bool,
    api_key_present: bool,
) -> CrossRefSmokeResult:
    normalized_doi = normalize_doi(doi)
    message = _message_from_payload(payload)
    metadata_doi = _as_text(message.get("DOI"))
    title = _as_text(message.get("title"))
    container_title = _as_text(message.get("container-title"))
    short_container_title = _as_text(message.get("short-container-title"))
    published_date = _best_published_date(message)
    issued_date = _date_from_parts(message.get("issued"))
    authors = _authors(message.get("author"))

    conflicts: list[MetadataConflict] = []
    if metadata_doi and normalize_doi(metadata_doi) != normalized_doi:
        conflicts.append(
            MetadataConflict(
                field="doi",
                expected=normalized_doi,
                observed=metadata_doi,
                notes="CrossRef message.DOI does not match the requested DOI",
            )
        )

    incomplete_fields = tuple(
        field
        for field, value in (
            ("metadata_doi", metadata_doi),
            ("title", title),
            ("authors", authors),
            ("container_title", container_title),
            ("published_date", published_date),
        )
        if not value
    )
    conflicts_tuple = tuple(conflicts)
    status = _status(incomplete_fields, conflicts_tuple)
    notes = "missing journal/API metadata is incomplete metadata, not publication or department-scope evidence"
    if conflicts_tuple:
        notes = "metadata conflict recorded for manual review; this is not a rejection decision"
    elif not mailto_present:
        notes += "; CROSSREF_MAILTO missing, polite-pool mailto was omitted"

    return CrossRefSmokeResult(
        doi=normalized_doi,
        status=status,
        cache_hit=cache_hit,
        mailto_present=mailto_present,
        api_key_present=api_key_present,
        metadata_doi=metadata_doi,
        title=title,
        container_title=container_title,
        short_container_title=short_container_title,
        published_date=published_date,
        issued_date=issued_date,
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
        CREATE TABLE IF NOT EXISTS crossref_works (
            doi TEXT PRIMARY KEY,
            fetched_at TEXT NOT NULL,
            status TEXT NOT NULL,
            metadata_doi TEXT,
            title TEXT,
            container_title TEXT,
            short_container_title TEXT,
            published_date TEXT,
            issued_date TEXT,
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
    doi: str,
    mailto_present: bool = False,
    api_key_present: bool = False,
) -> CrossRefSmokeResult | None:
    normalized_doi = normalize_doi(doi)
    if not cache_path.exists():
        return None
    with _connect_cache(cache_path) as conn:
        init_cache(conn)
        row = conn.execute(
            "SELECT * FROM crossref_works WHERE doi = ?",
            (normalized_doi,),
        ).fetchone()
    if row is None:
        return None
    conflicts = tuple(
        MetadataConflict(**item) for item in json.loads(row["conflicts_json"])
    )
    return CrossRefSmokeResult(
        doi=row["doi"],
        status=row["status"],
        cache_hit=True,
        mailto_present=mailto_present,
        api_key_present=api_key_present,
        metadata_doi=row["metadata_doi"],
        title=row["title"],
        container_title=row["container_title"],
        short_container_title=row["short_container_title"],
        published_date=row["published_date"],
        issued_date=row["issued_date"],
        authors=tuple(json.loads(row["authors_json"])),
        incomplete_fields=tuple(json.loads(row["incomplete_fields_json"])),
        conflicts=conflicts,
        raw_json=json.loads(row["raw_json"]),
        notes="loaded from CrossRef cache; missing metadata remains non-evidence",
    )


def store_result(result: CrossRefSmokeResult, cache_path: Path) -> None:
    if result.raw_json is None:
        return
    fetched_at = datetime.now(UTC).isoformat(timespec="seconds")
    with _connect_cache(cache_path) as conn:
        init_cache(conn)
        with conn:
            conn.execute(
                """
                INSERT INTO crossref_works (
                    doi,
                    fetched_at,
                    status,
                    metadata_doi,
                    title,
                    container_title,
                    short_container_title,
                    published_date,
                    issued_date,
                    authors_json,
                    incomplete_fields_json,
                    conflicts_json,
                    raw_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(doi) DO UPDATE SET
                    fetched_at = excluded.fetched_at,
                    status = excluded.status,
                    metadata_doi = excluded.metadata_doi,
                    title = excluded.title,
                    container_title = excluded.container_title,
                    short_container_title = excluded.short_container_title,
                    published_date = excluded.published_date,
                    issued_date = excluded.issued_date,
                    authors_json = excluded.authors_json,
                    incomplete_fields_json = excluded.incomplete_fields_json,
                    conflicts_json = excluded.conflicts_json,
                    raw_json = excluded.raw_json
                """,
                (
                    result.doi,
                    fetched_at,
                    result.status,
                    result.metadata_doi,
                    result.title,
                    result.container_title,
                    result.short_container_title,
                    result.published_date,
                    result.issued_date,
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
                ("crossref", result.doi),
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
                        "crossref",
                        result.doi,
                        conflict.field,
                        conflict.expected,
                        conflict.observed,
                        conflict.notes,
                        fetched_at,
                    ),
                )


def _error_result(
    doi: str,
    status: str,
    mailto_present: bool,
    api_key_present: bool,
    notes: str,
) -> CrossRefSmokeResult:
    return CrossRefSmokeResult(
        doi=normalize_doi(doi),
        status=status,
        cache_hit=False,
        mailto_present=mailto_present,
        api_key_present=api_key_present,
        metadata_doi=None,
        title=None,
        container_title=None,
        short_container_title=None,
        published_date=None,
        issued_date=None,
        authors=(),
        incomplete_fields=(),
        conflicts=(),
        raw_json=None,
        notes=notes,
    )


def smoke_crossref(
    doi: str,
    cache_path: Path,
    mailto: str | None = None,
    api_key: str | None = None,
    http_get: HttpGet = default_http_get,
    endpoint: str = CROSSREF_WORKS_ENDPOINT,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    use_cache: bool = True,
    refresh: bool = False,
    write_cache: bool = True,
) -> CrossRefSmokeResult:
    if mailto is None:
        mailto = os.environ.get("CROSSREF_MAILTO")
    if api_key is None:
        api_key = os.environ.get("CROSSREF_API_KEY")
    mailto_present = bool(mailto)
    api_key_present = bool(api_key)

    if use_cache and not refresh:
        cached = load_cached_result(
            cache_path,
            doi,
            mailto_present=mailto_present,
            api_key_present=api_key_present,
        )
        if cached is not None:
            return cached

    url = build_crossref_url(doi, endpoint=endpoint, mailto=mailto)
    request = build_crossref_request(url, api_key)
    try:
        payload = _json_loads(http_get(request, timeout))
    except CrossRefRateLimitError as exc:
        return _error_result(doi, "rate_limited", mailto_present, api_key_present, str(exc))
    except CrossRefError as exc:
        return _error_result(doi, "request_error", mailto_present, api_key_present, str(exc))

    result = normalize_crossref_payload(
        doi=doi,
        payload=payload,
        cache_hit=False,
        mailto_present=mailto_present,
        api_key_present=api_key_present,
    )
    if write_cache:
        store_result(result, cache_path)
    return result


def print_smoke_result(
    result: CrossRefSmokeResult,
    cache_path: Path,
    out: TextIO = sys.stdout,
) -> None:
    print(f"doi: {result.doi}", file=out)
    print(f"cache_path: {cache_path}", file=out)
    print(f"cache_hit: {'true' if result.cache_hit else 'false'}", file=out)
    print(f"CROSSREF_MAILTO: {'present' if result.mailto_present else 'missing'}", file=out)
    print(f"CROSSREF_API_KEY: {'present' if result.api_key_present else 'missing'}", file=out)
    print(f"status: {result.status}", file=out)
    print(f"metadata_doi: {result.metadata_doi or 'missing'}", file=out)
    print(f"title: {result.title or 'missing'}", file=out)
    print(f"container_title: {result.container_title or 'missing'}", file=out)
    print(f"short_container_title: {result.short_container_title or 'missing'}", file=out)
    print(f"published_date: {result.published_date or 'missing'}", file=out)
    print(f"issued_date: {result.issued_date or 'missing'}", file=out)
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
    parser = argparse.ArgumentParser(description="CrossRef UVA arXiv smoke client.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    smoke = subparsers.add_parser("smoke", help="Fetch/cache one CrossRef DOI record.")
    smoke.add_argument("--doi", required=True, help="DOI to check.")
    smoke.add_argument("--cache-path", type=Path, help="Override cache SQLite path.")
    smoke.add_argument("--endpoint", default=CROSSREF_WORKS_ENDPOINT, help="Override CrossRef endpoint.")
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
        result = smoke_crossref(
            doi=args.doi,
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

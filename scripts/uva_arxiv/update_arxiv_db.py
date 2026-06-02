"""Full-arXiv shared database updater."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator, TextIO

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.uva_arxiv import arxiv_db, env


OAI_ENDPOINT = "https://export.arxiv.org/oai2"
API_ENDPOINT = "https://export.arxiv.org/api/query"
DEFAULT_OVERLAP_DAYS = 7

HttpGet = Callable[[str], bytes]
RecordFetcher = Callable[[dt.date, int | None], Iterable[arxiv_db.PaperRecord]]


class FetchError(RuntimeError):
    """Raised when arXiv metadata cannot be fetched or parsed."""


@dataclass(frozen=True)
class SinceUpdateResult:
    since: dt.date
    dry_run: bool
    db_count_before: int
    max_date_before: str | None
    fetched: int
    upserted: int


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD date, got {value!r}") from exc


def default_since_date(max_date: str | None, overlap_days: int, fallback: str) -> dt.date:
    if overlap_days < 0:
        raise ValueError("overlap_days must be non-negative")
    if max_date:
        return parse_date(max_date) - dt.timedelta(days=overlap_days)
    return parse_date(fallback)


def normalize_text(value: str | None) -> str:
    return " ".join((value or "").split())


def strip_version(arxiv_id: str) -> str:
    if "v" in arxiv_id:
        stem, version = arxiv_id.rsplit("v", 1)
        if version.isdigit():
            return stem
    return arxiv_id


def default_http_get(url: str, timeout: int = 30) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "uva-math-arxiv-phase1/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.URLError as exc:
        raise FetchError(f"request failed for {url}: {exc}") from exc


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _children(parent: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(parent) if _local_name(child.tag) == name]


def _child_text(parent: ET.Element, name: str) -> str:
    for child in _children(parent, name):
        return normalize_text(child.text)
    return ""


def _first_descendant(parent: ET.Element, name: str) -> ET.Element | None:
    for child in parent.iter():
        if _local_name(child.tag) == name:
            return child
    return None


def _oai_record_to_paper(record: ET.Element) -> arxiv_db.PaperRecord | None:
    header = _first_descendant(record, "header")
    if header is not None and header.attrib.get("status") == "deleted":
        return None

    metadata = _first_descendant(record, "arXiv")
    if metadata is None:
        return None

    arxiv_id = _child_text(metadata, "id")
    if not arxiv_id:
        return None

    authors: list[str] = []
    authors_node = _first_descendant(metadata, "authors")
    if authors_node is not None:
        for author in _children(authors_node, "author"):
            keyname = _child_text(author, "keyname")
            forenames = _child_text(author, "forenames")
            suffix = _child_text(author, "suffix")
            name = " ".join(part for part in (forenames, keyname, suffix) if part)
            if name:
                authors.append(name)

    date_value = _child_text(metadata, "created") or _child_text(metadata, "updated")
    return arxiv_db.PaperRecord(
        id=strip_version(arxiv_id),
        title=normalize_text(_child_text(metadata, "title")),
        abstract=normalize_text(_child_text(metadata, "abstract")),
        categories=normalize_text(_child_text(metadata, "categories")),
        authors=", ".join(authors),
        date=date_value,
    )


def fetch_oai_records(
    since: dt.date,
    limit: int | None = None,
    endpoint: str = OAI_ENDPOINT,
    http_get: HttpGet | None = None,
) -> Iterator[arxiv_db.PaperRecord]:
    http_get = http_get or default_http_get
    yielded = 0
    token: str | None = None

    while True:
        if token:
            params = {"verb": "ListRecords", "resumptionToken": token}
        else:
            params = {
                "verb": "ListRecords",
                "metadataPrefix": "arXiv",
                "from": since.isoformat(),
            }
        url = endpoint + "?" + urllib.parse.urlencode(params)
        root = ET.fromstring(http_get(url))

        error = _first_descendant(root, "error")
        if error is not None:
            code = error.attrib.get("code", "unknown")
            if code == "noRecordsMatch":
                return
            raise FetchError(f"OAI-PMH error {code}: {normalize_text(error.text)}")

        list_records = _first_descendant(root, "ListRecords")
        if list_records is None:
            return

        for record in _children(list_records, "record"):
            paper = _oai_record_to_paper(record)
            if paper is None:
                continue
            yield paper
            yielded += 1
            if limit is not None and yielded >= limit:
                return

        token_node = None
        for child in _children(list_records, "resumptionToken"):
            token_node = child
            break
        token = normalize_text(token_node.text if token_node is not None else None)
        if not token:
            return


def _api_entry_to_paper(entry: ET.Element) -> arxiv_db.PaperRecord | None:
    id_url = _child_text(entry, "id")
    if not id_url:
        return None
    arxiv_id = strip_version(id_url.rstrip("/").split("/")[-1])
    authors = [_child_text(author, "name") for author in _children(entry, "author")]
    categories = [
        child.attrib.get("term", "")
        for child in _children(entry, "category")
        if child.attrib.get("term")
    ]
    published = _child_text(entry, "published")
    return arxiv_db.PaperRecord(
        id=arxiv_id,
        title=normalize_text(_child_text(entry, "title")),
        abstract=normalize_text(_child_text(entry, "summary")),
        categories=" ".join(categories),
        authors=", ".join(author for author in authors if author),
        date=published[:10],
    )


def fetch_api_records(
    since: dt.date,
    limit: int | None = None,
    endpoint: str = API_ENDPOINT,
    http_get: HttpGet | None = None,
) -> Iterator[arxiv_db.PaperRecord]:
    if limit is None:
        raise FetchError("API fallback requires --limit to avoid broad unbounded queries")
    http_get = http_get or default_http_get
    submitted_start = since.strftime("%Y%m%d") + "0000"
    params = {
        "search_query": f"submittedDate:[{submitted_start} TO *]",
        "sortBy": "submittedDate",
        "sortOrder": "ascending",
        "start": "0",
        "max_results": str(min(limit, 100)),
    }
    root = ET.fromstring(http_get(endpoint + "?" + urllib.parse.urlencode(params)))
    yielded = 0
    for entry in _children(root, "entry"):
        paper = _api_entry_to_paper(entry)
        if paper is None:
            continue
        yield paper
        yielded += 1
        if yielded >= limit:
            return


def make_fetcher(
    source: str,
    endpoint: str | None = None,
    allow_api_fallback: bool = False,
) -> RecordFetcher:
    def fetcher(since: dt.date, limit: int | None) -> Iterable[arxiv_db.PaperRecord]:
        if source == "api":
            return fetch_api_records(since, limit, endpoint or API_ENDPOINT)
        try:
            return list(fetch_oai_records(since, limit, endpoint or OAI_ENDPOINT))
        except FetchError:
            if not allow_api_fallback:
                raise
            return fetch_api_records(since, limit, API_ENDPOINT)

    return fetcher


def run_since_update(
    config: env.UvaArxivConfig,
    db_path: Path | None = None,
    since: dt.date | None = None,
    overlap_days: int = DEFAULT_OVERLAP_DAYS,
    dry_run: bool = False,
    limit: int | None = None,
    fetcher: RecordFetcher | None = None,
    source: str = "oai",
    endpoint: str | None = None,
    allow_api_fallback: bool = False,
    out: TextIO = sys.stdout,
) -> SinceUpdateResult:
    db_path = Path(db_path or config.arxiv_db)
    connector = arxiv_db.connect_readonly if dry_run else arxiv_db.connect_readwrite
    with connector(db_path) as conn:
        arxiv_db.validate_papers_schema(conn)
        stats = arxiv_db.get_db_stats(conn)
        effective_since = since or default_since_date(
            stats.max_date,
            overlap_days,
            config.initial_arxiv_start_date,
        )

        print(f"arxiv_db: {db_path}", file=out)
        print(f"current_count: {stats.count}", file=out)
        print(f"current_min_date: {stats.min_date or 'none'}", file=out)
        print(f"current_max_date: {stats.max_date or 'none'}", file=out)
        print(f"since: {effective_since.isoformat()}", file=out)
        print(f"overlap_days: {overlap_days if since is None else 0}", file=out)
        print(f"limit: {limit if limit is not None else 'none'}", file=out)

        if dry_run:
            print("dry_run: true", file=out)
            print("writes: disabled", file=out)
            print("fetch: skipped", file=out)
            return SinceUpdateResult(
                since=effective_since,
                dry_run=True,
                db_count_before=stats.count,
                max_date_before=stats.max_date,
                fetched=0,
                upserted=0,
            )

        print("dry_run: false", file=out)
        fetch_records = fetcher or make_fetcher(source, endpoint, allow_api_fallback)
        records = list(fetch_records(effective_since, limit))
        upserted = arxiv_db.upsert_papers(conn, records)
        print(f"fetched: {len(records)}", file=out)
        print(f"upserted: {upserted}", file=out)
        return SinceUpdateResult(
            since=effective_since,
            dry_run=False,
            db_count_before=stats.count,
            max_date_before=stats.max_date,
            fetched=len(records),
            upserted=upserted,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Update the shared arXiv SQLite database.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    since_parser = subparsers.add_parser("since", help="Fetch and upsert arXiv records since a date.")
    since_parser.add_argument("--db", type=Path, help="Override the configured shared arXiv DB path.")
    since_parser.add_argument("--since", type=parse_date, help="Use an explicit YYYY-MM-DD start date.")
    since_parser.add_argument("--overlap-days", type=int, default=DEFAULT_OVERLAP_DAYS)
    since_parser.add_argument("--limit", type=int, help="Limit fetched records for smoke tests.")
    since_parser.add_argument("--dry-run", action="store_true", help="Report plan without fetching or writing.")
    since_parser.add_argument("--source", choices=("oai", "api"), default="oai")
    since_parser.add_argument("--endpoint", help="Override the source endpoint URL.")
    since_parser.add_argument(
        "--allow-api-fallback",
        action="store_true",
        help="Use the limited API fallback if OAI-PMH fails.",
    )
    args = parser.parse_args()

    config = env.load_config(ensure_dirs=True)
    if args.command == "since":
        run_since_update(
            config=config,
            db_path=args.db,
            since=args.since,
            overlap_days=args.overlap_days,
            dry_run=args.dry_run,
            limit=args.limit,
            source=args.source,
            endpoint=args.endpoint,
            allow_api_fallback=args.allow_api_fallback,
        )
        return 0
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

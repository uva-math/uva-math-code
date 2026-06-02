"""Journal/publication metadata sidecar for UVA arXiv candidates.

This module populates an ignored local cache and review reports. It does not
write public site output and does not make inclusion decisions.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable, TextIO

try:
    from . import crossref_client, env, sources
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.uva_arxiv import crossref_client, env, sources


DEFAULT_CACHE_NAME = "journal_refs.sqlite"
DEFAULT_INPUT_CSV = "reports/uva-arxiv-tt-confirmed-matches.csv"
DEFAULT_OUTPUT_PREFIX = "reports/uva-arxiv-tt-journal-metadata"
S2_BATCH_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/batch"
S2_BATCH_FIELDS = "title,externalIds,journal,venue,publicationVenue,year,publicationDate"
S2_BATCH_SIZE = 500
S2_RATE_LIMIT_SECONDS = 1.1
ARXIV_API_ENDPOINT = "https://export.arxiv.org/api/query"
ARXIV_BATCH_SIZE = 200
ARXIV_RATE_LIMIT_SECONDS = 3.5
CROSSREF_RATE_LIMIT_SECONDS = 0.05
TITLE_SIMILARITY_MIN = 0.65
DASH_RE = re.compile(r"[\u2010-\u2015\u2212]")
MULTI_SPACE_RE = re.compile(r"\s+")
JOURNAL_YEAR_RE = re.compile(r"\b((?:19|20)\d{2})\b")
JOURNAL_PAGES_RE = re.compile(r"\bpp\.\s*([^,()]+)", re.IGNORECASE)
ARXIV_NS = {
    "a": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


class JournalRefsError(RuntimeError):
    """Raised when journal metadata cannot be fetched or normalized."""


@dataclass(frozen=True)
class PaperInput:
    arxiv_id: str
    title: str
    authors: str
    date: str


@dataclass(frozen=True)
class JournalMetadata:
    arxiv_id: str
    status: str
    source: str
    journal_name: str
    journal_volume: str
    journal_pages: str
    journal_ref: str
    doi: str
    venue: str
    publication_year: int | None
    publication_date: str
    s2_status: str
    arxiv_status: str
    crossref_status: str
    title_similarity: float | None
    notes: str
    raw_json: dict[str, Any]


def normalize_title_for_match(title: str) -> str:
    text = (title or "").replace("\u00a0", " ").lower()
    text = re.sub(r"\\[a-zA-Z]+", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def title_similarity(expected: str, actual: str) -> float:
    expected_norm = normalize_title_for_match(expected)
    actual_norm = normalize_title_for_match(actual)
    if not expected_norm or not actual_norm:
        return 1.0
    return SequenceMatcher(None, expected_norm, actual_norm).ratio()


def normalize_pages(pages: str) -> str:
    if not pages:
        return ""
    normalized = DASH_RE.sub("-", pages.strip())
    normalized = re.sub(r"\s*-\s*", "-", normalized)
    return MULTI_SPACE_RE.sub(" ", normalized).strip()


def parse_arxiv_journal_ref(journal_ref: str) -> dict[str, Any]:
    """Parse common arXiv journal_ref strings into displayable pieces."""
    raw = MULTI_SPACE_RE.sub(" ", (journal_ref or "").strip())
    parsed: dict[str, Any] = {
        "journal_name": raw,
        "journal_volume": "",
        "journal_pages": "",
        "publication_year": None,
    }
    if not raw:
        return parsed

    years = JOURNAL_YEAR_RE.findall(raw)
    if years:
        parsed["publication_year"] = int(years[-1])

    work = re.sub(r",?\s*\([^)]*(?:19|20)\d{2}[^)]*\)\s*$", "", raw).strip(" ,")

    pages_match = JOURNAL_PAGES_RE.search(work)
    if pages_match:
        parsed["journal_pages"] = normalize_pages(pages_match.group(1))
        work = (work[: pages_match.start()] + work[pages_match.end() :]).strip(" ,")
    else:
        page_matches = list(re.finditer(r"\b\d+\s*[-–—]\s*\d+\b", work))
        if page_matches:
            match = page_matches[-1]
            parsed["journal_pages"] = normalize_pages(match.group(0))
            work = (work[: match.start()] + work[match.end() :]).strip(" ,")

    work = re.sub(r"\([^)]*\)", "", work).strip(" ,")
    vol_match = re.search(r"^(.*?)(?:,?\s+|,)(\d+[A-Za-z]?)\s*$", work)
    if vol_match:
        parsed["journal_name"] = vol_match.group(1).strip(" ,") or raw
        parsed["journal_volume"] = vol_match.group(2).strip()
    else:
        parsed["journal_name"] = work or raw
    return parsed


def format_journal_ref(info: dict[str, Any]) -> str:
    name = str(info.get("journal_name") or "").strip()
    if not name:
        return ""
    parts = [name]
    volume = str(info.get("journal_volume") or "").strip()
    if volume:
        parts.append(f"vol. {volume}")
    pages = str(info.get("journal_pages") or "").strip()
    if pages:
        parts.append(f"pp. {pages}")
    year = info.get("publication_year")
    if year:
        parts.append(f"({year})")
    return ", ".join(parts)


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        for item in value:
            text = _as_text(item)
            if text:
                return text
        return ""
    return str(value).strip()


def _as_int(value: Any) -> int | None:
    if value in {None, ""}:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _date_year(date_value: str) -> int | None:
    match = re.match(r"^((?:19|20)\d{2})", date_value or "")
    return int(match.group(1)) if match else None


def _is_arxiv_doi(doi: str) -> bool:
    return "48550/arxiv" in doi.lower()


def _clean_doi(doi: str) -> str:
    text = doi.strip()
    if not text or _is_arxiv_doi(text):
        return ""
    try:
        return crossref_client.normalize_doi(text)
    except Exception:
        return text.lower()


def _s2_journal_name(raw: Any) -> str:
    if isinstance(raw, dict):
        return _as_text(raw.get("name"))
    return _as_text(raw)


def _clean_venue(venue: str) -> str:
    text = venue.strip()
    if text.lower() in {"arxiv", "arxiv.org"} or text.lower().startswith("arxiv:"):
        return ""
    return text


def parse_s2_entry(
    entry: dict[str, Any] | None,
    arxiv_id: str,
    expected_title: str,
) -> tuple[dict[str, Any] | None, str, float | None, str]:
    if not entry:
        return None, "missing", None, "Semantic Scholar returned no record"

    external_ids = entry.get("externalIds") if isinstance(entry.get("externalIds"), dict) else {}
    s2_arxiv = _as_text(external_ids.get("ArXiv") or external_ids.get("arXiv"))
    if s2_arxiv and sources.normalize_arxiv_id(s2_arxiv) != sources.normalize_arxiv_id(arxiv_id):
        return None, "conflict", None, f"S2 externalIds.ArXiv={s2_arxiv!r} does not match"

    s2_title = _as_text(entry.get("title"))
    similarity = title_similarity(expected_title, s2_title)
    if expected_title and s2_title and similarity < TITLE_SIMILARITY_MIN:
        return None, "conflict", similarity, f"S2 title similarity {similarity:.2f} below threshold"

    journal = entry.get("journal") if isinstance(entry.get("journal"), dict) else {}
    journal_name = _s2_journal_name(journal)
    if journal_name.lower() in {"arxiv", "arxiv.org"} or journal_name.lower().startswith("arxiv:"):
        journal_name = ""
    journal_volume = _as_text(journal.get("volume")) if isinstance(journal, dict) else ""
    journal_pages = normalize_pages(_as_text(journal.get("pages"))) if isinstance(journal, dict) else ""
    if journal_volume.startswith("abs/"):
        journal_volume = ""

    venue = _as_text(entry.get("venue"))
    publication_venue = entry.get("publicationVenue")
    if not venue and isinstance(publication_venue, dict):
        venue = _as_text(publication_venue.get("name"))
    venue = _clean_venue(venue)
    doi = _clean_doi(_as_text(external_ids.get("DOI") or external_ids.get("doi")))
    publication_year = _as_int(entry.get("year"))
    publication_date = _as_text(entry.get("publicationDate"))
    if publication_date and not publication_year:
        publication_year = _date_year(publication_date)

    info = {
        "journal_name": journal_name,
        "journal_volume": journal_volume,
        "journal_pages": journal_pages,
        "doi": doi,
        "venue": venue,
        "publication_year": publication_year,
        "publication_date": publication_date,
    }
    status = "complete" if journal_name or doi or venue else "empty"
    return info, status, similarity, ""


def fetch_s2_batch(
    arxiv_ids: list[str],
    api_key: str | None,
    endpoint: str = S2_BATCH_ENDPOINT,
) -> list[dict[str, Any] | None]:
    payload = json.dumps({"ids": [f"ArXiv:{arxiv_id}" for arxiv_id in arxiv_ids]}).encode()
    headers = {"Content-Type": "application/json", "User-Agent": "uva-math-arxiv-journal-refs/0.1"}
    if api_key:
        headers["x-api-key"] = api_key
    request = urllib.request.Request(
        f"{endpoint}?fields={urllib.parse.quote(S2_BATCH_FIELDS, safe=',')}",
        data=payload,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            loaded = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise JournalRefsError(f"S2 batch failed with HTTP {exc.code}: {body[:200]}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise JournalRefsError(f"S2 batch request failed: {exc}") from exc
    if not isinstance(loaded, list):
        raise JournalRefsError("S2 batch returned non-list JSON")
    return [item if isinstance(item, dict) else None for item in loaded]


def fetch_arxiv_batch(
    arxiv_ids: list[str],
    endpoint: str = ARXIV_API_ENDPOINT,
) -> dict[str, dict[str, str]]:
    if not arxiv_ids:
        return {}
    query = urllib.parse.urlencode(
        {"id_list": ",".join(arxiv_ids), "max_results": str(len(arxiv_ids))}
    )
    request = urllib.request.Request(
        f"{endpoint}?{query}",
        headers={"User-Agent": "uva-math-arxiv-journal-refs/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise JournalRefsError(f"arXiv API request failed: {exc}") from exc
    try:
        tree = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise JournalRefsError("arXiv API returned invalid XML") from exc

    results: dict[str, dict[str, str]] = {}
    for entry in tree.findall(".//a:entry", ARXIV_NS):
        id_el = entry.find("a:id", ARXIV_NS)
        if id_el is None or not id_el.text:
            continue
        arxiv_id = sources.strip_version(id_el.text.strip().split("/")[-1])
        journal_ref_el = entry.find("arxiv:journal_ref", ARXIV_NS)
        doi_el = entry.find("arxiv:doi", ARXIV_NS)
        journal_ref = journal_ref_el.text.strip() if journal_ref_el is not None and journal_ref_el.text else ""
        doi = doi_el.text.strip() if doi_el is not None and doi_el.text else ""
        if journal_ref or doi:
            results[arxiv_id] = {"journal_ref_raw": journal_ref, "doi": doi}
    return results


def metadata_status(info: dict[str, Any]) -> str:
    """Classify useful journal metadata without treating S2's bare year as a publication."""
    if info.get("journal_name"):
        return "journal"
    if info.get("doi"):
        return "doi_only"
    if info.get("venue"):
        return "venue_only"
    return "missing"


def merge_sources(
    s2_info: dict[str, Any] | None,
    arxiv_info: dict[str, str] | None,
    crossref_info: crossref_client.CrossRefSmokeResult | None = None,
) -> tuple[dict[str, Any], str, str]:
    result: dict[str, Any] = {
        "journal_name": "",
        "journal_volume": "",
        "journal_pages": "",
        "doi": "",
        "venue": "",
        "publication_year": None,
        "publication_date": "",
    }
    source_bits: list[str] = []
    notes: list[str] = []

    s2_has_journal = bool(s2_info and s2_info.get("journal_name"))
    arxiv_ref = arxiv_info.get("journal_ref_raw") if arxiv_info else ""

    if s2_has_journal and s2_info:
        result.update({key: value for key, value in s2_info.items() if value})
        source_bits.append("s2")
    elif arxiv_ref:
        result.update({key: value for key, value in parse_arxiv_journal_ref(arxiv_ref).items() if value})
        source_bits.append("arxiv")
    elif s2_info:
        for key in ("doi", "venue", "publication_year", "publication_date"):
            if s2_info.get(key):
                result[key] = s2_info[key]
        if any(result.get(key) for key in ("doi", "venue", "publication_year", "publication_date")):
            source_bits.append("s2")

    if arxiv_info:
        arxiv_doi = _clean_doi(arxiv_info.get("doi", ""))
        if arxiv_doi:
            result["doi"] = arxiv_doi
            if "arxiv" not in source_bits:
                source_bits.append("arxiv")

    if not result.get("doi") and s2_info and s2_info.get("doi"):
        result["doi"] = s2_info["doi"]

    if crossref_info and crossref_info.status not in {"rate_limited", "request_error"}:
        if crossref_info.container_title and not result.get("journal_name"):
            result["journal_name"] = crossref_info.container_title
            source_bits.append("crossref")
        if crossref_info.published_date:
            result["publication_date"] = result.get("publication_date") or crossref_info.published_date
            result["publication_year"] = _date_year(crossref_info.published_date) or result.get("publication_year")
            if "crossref" not in source_bits:
                source_bits.append("crossref")
        elif crossref_info.issued_date:
            result["publication_date"] = result.get("publication_date") or crossref_info.issued_date
            result["publication_year"] = _date_year(crossref_info.issued_date) or result.get("publication_year")
            if "crossref" not in source_bits:
                source_bits.append("crossref")
    elif crossref_info:
        notes.append(f"CrossRef {crossref_info.status}: {crossref_info.notes}")

    if not source_bits:
        source = "none"
    else:
        source = "+".join(dict.fromkeys(source_bits))

    return result, source, "; ".join(notes) if notes else ""


def _connect_cache(cache_path: Path) -> sqlite3.Connection:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(cache_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_cache(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS journal_refs (
            arxiv_id TEXT PRIMARY KEY,
            fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
            status TEXT NOT NULL,
            source TEXT NOT NULL,
            journal_name TEXT NOT NULL,
            journal_volume TEXT NOT NULL,
            journal_pages TEXT NOT NULL,
            journal_ref TEXT NOT NULL,
            doi TEXT NOT NULL,
            venue TEXT NOT NULL,
            publication_year INTEGER,
            publication_date TEXT NOT NULL,
            s2_status TEXT NOT NULL,
            arxiv_status TEXT NOT NULL,
            crossref_status TEXT NOT NULL,
            title_similarity REAL,
            notes TEXT NOT NULL,
            raw_json TEXT NOT NULL
        )
        """
    )


def load_cached(conn: sqlite3.Connection, arxiv_ids: Iterable[str]) -> dict[str, JournalMetadata]:
    ids = list(dict.fromkeys(sources.normalize_arxiv_id(arxiv_id) for arxiv_id in arxiv_ids))
    if not ids:
        return {}
    init_cache(conn)
    cached: dict[str, JournalMetadata] = {}
    for index in range(0, len(ids), 500):
        batch = ids[index : index + 500]
        placeholders = ",".join("?" for _ in batch)
        rows = conn.execute(
            f"SELECT * FROM journal_refs WHERE arxiv_id IN ({placeholders})",
            batch,
        ).fetchall()
        for row in rows:
            row_venue = _clean_venue(row["venue"])
            raw_info = {
                "journal_name": row["journal_name"],
                "doi": row["doi"],
                "venue": row_venue,
                "publication_date": row["publication_date"],
            }
            cached[row["arxiv_id"]] = JournalMetadata(
                arxiv_id=row["arxiv_id"],
                status=metadata_status(raw_info),
                source=row["source"],
                journal_name=row["journal_name"],
                journal_volume=row["journal_volume"],
                journal_pages=row["journal_pages"],
                journal_ref=row["journal_ref"],
                doi=row["doi"],
                venue=row_venue,
                publication_year=row["publication_year"],
                publication_date=row["publication_date"],
                s2_status=row["s2_status"],
                arxiv_status=row["arxiv_status"],
                crossref_status=row["crossref_status"],
                title_similarity=row["title_similarity"],
                notes=row["notes"],
                raw_json=json.loads(row["raw_json"]),
            )
    return cached


def store_metadata(conn: sqlite3.Connection, rows: Iterable[JournalMetadata]) -> None:
    init_cache(conn)
    with conn:
        conn.executemany(
            """
            INSERT INTO journal_refs (
                arxiv_id,
                fetched_at,
                status,
                source,
                journal_name,
                journal_volume,
                journal_pages,
                journal_ref,
                doi,
                venue,
                publication_year,
                publication_date,
                s2_status,
                arxiv_status,
                crossref_status,
                title_similarity,
                notes,
                raw_json
            )
            VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(arxiv_id) DO UPDATE SET
                fetched_at = excluded.fetched_at,
                status = excluded.status,
                source = excluded.source,
                journal_name = excluded.journal_name,
                journal_volume = excluded.journal_volume,
                journal_pages = excluded.journal_pages,
                journal_ref = excluded.journal_ref,
                doi = excluded.doi,
                venue = excluded.venue,
                publication_year = excluded.publication_year,
                publication_date = excluded.publication_date,
                s2_status = excluded.s2_status,
                arxiv_status = excluded.arxiv_status,
                crossref_status = excluded.crossref_status,
                title_similarity = excluded.title_similarity,
                notes = excluded.notes,
                raw_json = excluded.raw_json
            """,
            [
                (
                    row.arxiv_id,
                    row.status,
                    row.source,
                    row.journal_name,
                    row.journal_volume,
                    row.journal_pages,
                    row.journal_ref,
                    row.doi,
                    row.venue,
                    row.publication_year,
                    row.publication_date,
                    row.s2_status,
                    row.arxiv_status,
                    row.crossref_status,
                    row.title_similarity,
                    row.notes,
                    json.dumps(row.raw_json, ensure_ascii=False, sort_keys=True),
                )
                for row in rows
            ],
        )


def load_paper_inputs(path: Path) -> list[PaperInput]:
    if not path.exists():
        raise JournalRefsError(f"input CSV does not exist: {path}")
    by_id: dict[str, PaperInput] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if "arxiv_id" not in (reader.fieldnames or ()):  # pragma: no cover - defensive
            raise JournalRefsError(f"input CSV lacks arxiv_id column: {path}")
        for row in reader:
            arxiv_id = sources.normalize_arxiv_id(row.get("arxiv_id", ""))
            if arxiv_id in by_id:
                continue
            by_id[arxiv_id] = PaperInput(
                arxiv_id=arxiv_id,
                title=row.get("title", ""),
                authors=row.get("authors", ""),
                date=row.get("date", ""),
            )
    return sorted(by_id.values(), key=lambda item: (item.date, item.arxiv_id))


def fetch_metadata(
    papers: list[PaperInput],
    cache_path: Path,
    crossref_cache_path: Path,
    refresh: bool = False,
    refresh_empty: bool = False,
    dry_run: bool = False,
    limit: int | None = None,
    no_crossref: bool = False,
    out: TextIO = sys.stdout,
) -> dict[str, JournalMetadata]:
    config = env.load_config(ensure_dirs=True)
    api_key = os.environ.get("S2_API_KEY")
    papers = papers[:limit] if limit is not None else papers
    paper_by_id = {paper.arxiv_id: paper for paper in papers}
    arxiv_ids = list(paper_by_id)

    with _connect_cache(cache_path) as conn:
        cached = load_cached(conn, arxiv_ids)
        if refresh:
            to_fetch = arxiv_ids
        elif refresh_empty:
            to_fetch = [
                arxiv_id for arxiv_id in arxiv_ids
                if arxiv_id not in cached or cached[arxiv_id].status in {"missing", "venue_only", "doi_only"}
            ]
        else:
            to_fetch = [arxiv_id for arxiv_id in arxiv_ids if arxiv_id not in cached]

        print(f"papers: {len(arxiv_ids)}", file=out)
        print(f"cached: {len(cached)}", file=out)
        print(f"to_fetch: {len(to_fetch)}", file=out)
        print(f"cache_path: {cache_path}", file=out)
        if dry_run:
            s2_batches = (len(to_fetch) + S2_BATCH_SIZE - 1) // S2_BATCH_SIZE
            arxiv_batches = (len(to_fetch) + ARXIV_BATCH_SIZE - 1) // ARXIV_BATCH_SIZE
            print(f"[dry-run] would make {s2_batches} S2 batch requests", file=out)
            print(f"[dry-run] would make {arxiv_batches} arXiv API batch requests", file=out)
            print("[dry-run] would make CrossRef requests for DOIs found during fetch", file=out)
            return cached

        fetched_rows: list[JournalMetadata] = []
        s2_by_id: dict[str, tuple[dict[str, Any] | None, str, float | None, str, dict[str, Any] | None]] = {}
        arxiv_by_id: dict[str, dict[str, str]] = {}

        if to_fetch:
            if not api_key:
                print("warning: S2_API_KEY missing; Semantic Scholar batch will use unauthenticated access", file=out)
            print("fetching Semantic Scholar...", file=out)
            for index in range(0, len(to_fetch), S2_BATCH_SIZE):
                batch = to_fetch[index : index + S2_BATCH_SIZE]
                print(f"  S2 batch {index // S2_BATCH_SIZE + 1}: {len(batch)}", file=out)
                entries = fetch_s2_batch(batch, api_key=api_key)
                for arxiv_id, entry in zip(batch, entries, strict=False):
                    paper = paper_by_id[arxiv_id]
                    info, status, similarity, notes = parse_s2_entry(entry, arxiv_id, paper.title)
                    s2_by_id[arxiv_id] = (info, status, similarity, notes, entry)
                if index + S2_BATCH_SIZE < len(to_fetch):
                    time.sleep(S2_RATE_LIMIT_SECONDS)

            print("fetching arXiv journal_ref/doi...", file=out)
            for index in range(0, len(to_fetch), ARXIV_BATCH_SIZE):
                batch = to_fetch[index : index + ARXIV_BATCH_SIZE]
                print(f"  arXiv batch {index // ARXIV_BATCH_SIZE + 1}: {len(batch)}", file=out)
                arxiv_by_id.update(fetch_arxiv_batch(batch))
                if index + ARXIV_BATCH_SIZE < len(to_fetch):
                    time.sleep(ARXIV_RATE_LIMIT_SECONDS)

            doi_candidates: dict[str, str] = {}
            for arxiv_id in to_fetch:
                s2_info = s2_by_id.get(arxiv_id, (None, "missing", None, "", None))[0]
                arxiv_info = arxiv_by_id.get(arxiv_id)
                doi = ""
                if arxiv_info:
                    doi = _clean_doi(arxiv_info.get("doi", ""))
                if not doi and s2_info:
                    doi = _clean_doi(str(s2_info.get("doi", "")))
                if doi:
                    doi_candidates[arxiv_id] = doi

            crossref_by_id: dict[str, crossref_client.CrossRefSmokeResult] = {}
            if doi_candidates and not no_crossref:
                print(f"fetching CrossRef for {len(set(doi_candidates.values()))} DOIs...", file=out)
                seen_dois: dict[str, crossref_client.CrossRefSmokeResult] = {}
                for idx, (arxiv_id, doi) in enumerate(doi_candidates.items(), start=1):
                    if doi in seen_dois:
                        crossref_by_id[arxiv_id] = seen_dois[doi]
                        continue
                    if idx == 1 or idx % 25 == 0 or idx == len(doi_candidates):
                        print(f"  CrossRef {idx}/{len(doi_candidates)}", file=out)
                    result = crossref_client.smoke_crossref(
                        doi=doi,
                        cache_path=crossref_cache_path,
                        use_cache=True,
                    )
                    seen_dois[doi] = result
                    crossref_by_id[arxiv_id] = result
                    if idx < len(doi_candidates):
                        time.sleep(CROSSREF_RATE_LIMIT_SECONDS)

            for arxiv_id in to_fetch:
                s2_info, s2_status, similarity, s2_notes, s2_raw = s2_by_id.get(
                    arxiv_id, (None, "missing", None, "", None)
                )
                arxiv_info = arxiv_by_id.get(arxiv_id)
                crossref_info = crossref_by_id.get(arxiv_id)
                merged, source, merge_notes = merge_sources(s2_info, arxiv_info, crossref_info)
                journal_ref = format_journal_ref(merged)
                status = metadata_status(merged)
                notes = "; ".join(part for part in (s2_notes, merge_notes) if part)
                raw = {
                    "s2": s2_raw,
                    "s2_parsed": s2_info,
                    "arxiv": arxiv_info,
                    "crossref": asdict(crossref_info) if crossref_info else None,
                }
                fetched_rows.append(
                    JournalMetadata(
                        arxiv_id=arxiv_id,
                        status=status,
                        source=source,
                        journal_name=str(merged.get("journal_name") or ""),
                        journal_volume=str(merged.get("journal_volume") or ""),
                        journal_pages=str(merged.get("journal_pages") or ""),
                        journal_ref=journal_ref,
                        doi=str(merged.get("doi") or ""),
                        venue=str(merged.get("venue") or ""),
                        publication_year=_as_int(merged.get("publication_year")),
                        publication_date=str(merged.get("publication_date") or ""),
                        s2_status=s2_status,
                        arxiv_status="found" if arxiv_info else "missing",
                        crossref_status=crossref_info.status if crossref_info else ("skipped" if no_crossref else "missing"),
                        title_similarity=similarity,
                        notes=notes,
                        raw_json=raw,
                    )
                )

            store_metadata(conn, fetched_rows)
            cached = load_cached(conn, arxiv_ids)
    return cached


def write_reports(
    papers: list[PaperInput],
    metadata_by_id: dict[str, JournalMetadata],
    output_prefix: Path,
) -> tuple[Path, Path]:
    csv_path = output_prefix.with_suffix(".csv")
    md_path = output_prefix.with_suffix(".md")
    fields = [
        "arxiv_id",
        "date",
        "title",
        "authors",
        "status",
        "source",
        "journal_name",
        "journal_ref",
        "doi",
        "venue",
        "publication_year",
        "publication_date",
        "s2_status",
        "arxiv_status",
        "crossref_status",
        "title_similarity",
        "notes",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for paper in papers:
            meta = metadata_by_id.get(paper.arxiv_id)
            writer.writerow(
                {
                    "arxiv_id": paper.arxiv_id,
                    "date": paper.date,
                    "title": paper.title,
                    "authors": paper.authors,
                    "status": meta.status if meta else "not_cached",
                    "source": meta.source if meta else "",
                    "journal_name": meta.journal_name if meta else "",
                    "journal_ref": meta.journal_ref if meta else "",
                    "doi": meta.doi if meta else "",
                    "venue": meta.venue if meta else "",
                    "publication_year": meta.publication_year if meta and meta.publication_year else "",
                    "publication_date": meta.publication_date if meta else "",
                    "s2_status": meta.s2_status if meta else "",
                    "arxiv_status": meta.arxiv_status if meta else "",
                    "crossref_status": meta.crossref_status if meta else "",
                    "title_similarity": f"{meta.title_similarity:.3f}" if meta and meta.title_similarity is not None else "",
                    "notes": meta.notes if meta else "",
                }
            )

    status_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    journal_counts: dict[str, int] = {}
    for paper in papers:
        meta = metadata_by_id.get(paper.arxiv_id)
        status = meta.status if meta else "not_cached"
        source = meta.source if meta else ""
        status_counts[status] = status_counts.get(status, 0) + 1
        source_counts[source] = source_counts.get(source, 0) + 1
        if meta and meta.journal_name:
            journal_counts[meta.journal_name] = journal_counts.get(meta.journal_name, 0) + 1

    lines = [
        "# UVA arXiv TT journal metadata",
        "",
        "Journal/publication metadata for confirmed TT arXiv matches. Missing metadata means incomplete API data or unpublished/preprint status; it is not a rejection reason.",
        "",
        f"- Papers: {len(papers)}",
        f"- With journal name: {sum(1 for p in papers if metadata_by_id.get(p.arxiv_id) and metadata_by_id[p.arxiv_id].journal_name)}",
        f"- With DOI: {sum(1 for p in papers if metadata_by_id.get(p.arxiv_id) and metadata_by_id[p.arxiv_id].doi)}",
        "",
        "## Status counts",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"| {status or '(blank)'} | {count} |")
    lines.extend(["", "## Source counts", "", "| Source | Count |", "|---|---:|"])
    for source, count in sorted(source_counts.items()):
        lines.append(f"| {source or '(blank)'} | {count} |")
    lines.extend(["", "## Top journals", "", "| Journal | Count |", "|---|---:|"])
    for journal, count in sorted(journal_counts.items(), key=lambda item: (-item[1], item[0].casefold()))[:40]:
        lines.append(f"| {journal.replace('|', '\\|')} | {count} |")
    lines.extend([
        "",
        "## Details",
        "",
        "| Date | arXiv | Title | Status | Journal/ref | DOI | Source |",
        "|---|---|---|---|---|---|---|",
    ])
    for paper in sorted(papers, key=lambda item: (item.date, item.arxiv_id)):
        meta = metadata_by_id.get(paper.arxiv_id)
        journal_ref = meta.journal_ref or meta.journal_name if meta else ""
        doi = meta.doi if meta else ""
        doi_link = f"[{doi}](https://doi.org/{doi})" if doi else ""
        lines.append(
            f"| {paper.date} | [{paper.arxiv_id}](https://arxiv.org/abs/{paper.arxiv_id}) | "
            f"{paper.title.replace('|', '\\|')} | {meta.status if meta else 'not_cached'} | "
            f"{journal_ref.replace('|', '\\|')} | {doi_link} | {meta.source if meta else ''} |"
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return csv_path, md_path


def print_stats(metadata_by_id: dict[str, JournalMetadata], total: int, out: TextIO = sys.stdout) -> None:
    statuses: dict[str, int] = {}
    for metadata in metadata_by_id.values():
        statuses[metadata.status] = statuses.get(metadata.status, 0) + 1
    print(f"total: {total}", file=out)
    print(f"cached: {len(metadata_by_id)}", file=out)
    for status, count in sorted(statuses.items()):
        print(f"{status}: {count}", file=out)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Populate journal metadata for UVA arXiv review rows.")
    parser.add_argument("--input", type=Path, default=Path(DEFAULT_INPUT_CSV), help="Confirmed matches CSV.")
    parser.add_argument("--cache-path", type=Path, help="Override journal metadata cache path.")
    parser.add_argument("--crossref-cache-path", type=Path, help="Override CrossRef cache path.")
    parser.add_argument("--output-prefix", type=Path, default=Path(DEFAULT_OUTPUT_PREFIX))
    parser.add_argument("--refresh", action="store_true", help="Refetch all input IDs.")
    parser.add_argument("--refresh-empty", action="store_true", help="Refetch only rows without a journal name.")
    parser.add_argument("--dry-run", action="store_true", help="Preview API work without writes.")
    parser.add_argument("--stats", action="store_true", help="Show cache stats for input IDs only.")
    parser.add_argument("--limit", type=int, help="Limit input IDs for smoke tests.")
    parser.add_argument("--no-crossref", action="store_true", help="Skip CrossRef enrichment.")
    parser.add_argument("--no-report", action="store_true", help="Do not write CSV/Markdown reports.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    config = env.load_config(ensure_dirs=True)
    cache_path = args.cache_path or config.cache_dir / DEFAULT_CACHE_NAME
    crossref_cache_path = args.crossref_cache_path or config.cache_dir / crossref_client.DEFAULT_CACHE_NAME
    papers = load_paper_inputs(args.input)
    if args.limit is not None:
        papers = papers[: args.limit]

    if args.stats:
        with _connect_cache(cache_path) as conn:
            cached = load_cached(conn, [paper.arxiv_id for paper in papers])
        print_stats(cached, len(papers))
        return 0

    metadata_by_id = fetch_metadata(
        papers=papers,
        cache_path=cache_path,
        crossref_cache_path=crossref_cache_path,
        refresh=args.refresh,
        refresh_empty=args.refresh_empty,
        dry_run=args.dry_run,
        limit=None,
        no_crossref=args.no_crossref,
    )
    if not args.dry_run and not args.no_report:
        csv_path, md_path = write_reports(papers, metadata_by_id, args.output_prefix)
        print(f"wrote: {csv_path}")
        print(f"wrote: {md_path}")
    print_stats(metadata_by_id, len(papers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

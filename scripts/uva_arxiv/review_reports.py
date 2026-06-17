"""Build reproducible UVA arXiv candidate/review reports.

This is an internal review generator. It does not write public site data.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping, TextIO

try:
    from . import affiliation, arxiv_db, env, roster, roster_history, sources
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.uva_arxiv import affiliation, arxiv_db, env, roster, roster_history, sources


DEFAULT_ROLE_GROUP = "faculty"
DEFAULT_LABEL = "tt"
DEFAULT_OUTPUT_DIR = Path("reports")
DEFAULT_REVIEW_ARCHIVE = Path("/Users/leo/Data/arxiv/uva-math-tt-candidate-sources")
DEFAULT_EXCLUDE_PERSON_IDS = ("rbh3vx",)
CANDIDATE_FIELDS = (
    "person_id",
    "display_name",
    "arxiv_id",
    "date",
    "title",
    "authors",
    "categories",
    "matched_author",
    "match_rule",
    "status",
    "note",
    "arxiv_url",
)
SOURCE_FIELDS = (
    "arxiv_id",
    "fetch_status",
    "source_format",
    "bytes_fetched",
    "files_written",
    "affiliation_evidence",
    "checked_files",
    "positive_count",
    "negative_count",
    "matched_people",
    "title",
    "categories",
    "source_dir",
    "error",
)
DECISION_FIELDS = (
    "person_id",
    "display_name",
    "arxiv_id",
    "date",
    "title",
    "authors",
    "categories",
    "matched_author",
    "match_rule",
    "status",
    "decision_source",
    "affiliation_evidence",
    "positive_count",
    "negative_count",
    "checked_files",
    "source_format",
    "source_dir",
    "arxiv_url",
    "note",
    "check_reason",
)


class ReviewReportError(RuntimeError):
    """Raised when review reports cannot be built."""


@dataclass(frozen=True)
class AliasSpec:
    alias: str
    match_rule: str
    normalized: str
    search_token: str


@dataclass(frozen=True)
class ReviewPerson:
    person_id: str
    display_name: str
    intervals: tuple[roster_history.AppointmentInterval, ...]
    aliases: tuple[AliasSpec, ...]


@dataclass(frozen=True)
class CandidateRow:
    person_id: str
    display_name: str
    arxiv_id: str
    date: str
    title: str
    authors: str
    categories: str
    matched_author: str
    match_rule: str
    status: str
    note: str
    arxiv_url: str

    def to_dict(self) -> dict[str, str]:
        return {field: str(getattr(self, field)) for field in CANDIDATE_FIELDS}


@dataclass(frozen=True)
class SourceEvidenceRow:
    arxiv_id: str
    fetch_status: str
    source_format: str
    bytes_fetched: int
    files_written: int
    affiliation_evidence: str
    checked_files: int
    positive_count: int
    negative_count: int
    matched_people: str
    title: str
    categories: str
    source_dir: str
    error: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "arxiv_id": self.arxiv_id,
            "fetch_status": self.fetch_status,
            "source_format": self.source_format,
            "bytes_fetched": str(self.bytes_fetched),
            "files_written": str(self.files_written),
            "affiliation_evidence": self.affiliation_evidence,
            "checked_files": str(self.checked_files),
            "positive_count": str(self.positive_count),
            "negative_count": str(self.negative_count),
            "matched_people": self.matched_people,
            "title": self.title,
            "categories": self.categories,
            "source_dir": self.source_dir,
            "error": self.error,
        }


def _date_from_string(value: str) -> date:
    return roster_history.parse_date(value, "paper date")


def _format_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/abs/{arxiv_id}"


def _markdown_escape(value: str) -> str:
    return value.replace("|", "\\|")


def _normalize_name(value: str) -> str:
    return roster.normalize_name(value)


def _normalized_author_names(authors: str) -> set[str]:
    """Split arXiv's author string into approximate individual author names."""
    text = " ".join((authors or "").split())
    text = re.sub(r"\s+and\s+", ",", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*;\s*", ",", text)
    names = set()
    for part in text.split(","):
        normalized = _normalize_name(part)
        if normalized:
            names.add(normalized)
    return names


def _contains_normalized_name(authors: str, normalized_alias: str) -> bool:
    # Match an individual author, not a substring across adjacent authors.
    # This avoids false positives like UVA "You Qi" matching "Jiangong You, Qi Zhou".
    return normalized_alias in _normalized_author_names(authors)


def _search_token_from_alias(alias: str) -> str:
    normalized = _normalize_name(alias)
    parts = normalized.split()
    if not parts:
        return ""
    # Last token is a good SQLite prefilter and avoids accent issues in names such as Földes.
    return parts[-1]


def _sql_like_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _paper_status(person_id: str, paper_date: date) -> str:
    # Keep the known Ono leave uncertainty visible in review output without dropping records.
    if person_id == "ko5wk" and paper_date >= date(2026, 1, 1):
        return "faculty_extended_leave_uncertain"
    return "faculty_active_window"


def _interval_contains(interval: roster_history.AppointmentInterval, paper_date: date) -> bool:
    end_date = interval.end_date or date.max
    return interval.start_date <= paper_date <= end_date


def _intervals_overlap_scan(
    intervals: Iterable[roster_history.AppointmentInterval],
    start_date: date,
    as_of_date: date,
) -> bool:
    for interval in intervals:
        end_date = interval.end_date or as_of_date
        if roster_history.intervals_overlap(interval.start_date, end_date, start_date, as_of_date):
            return True
    return False


def _load_manual_aliases(path: Path) -> dict[str, dict[str, Any]]:
    loaded = env.load_yaml_mapping_file(path)
    return {str(key): value for key, value in loaded.items() if isinstance(value, dict)}


def _load_decisions(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    loaded = env.load_yaml_file(path)
    if loaded is None:
        return {}
    if not isinstance(loaded, list):
        raise ReviewReportError(f"manual decisions must be a list: {path}")
    decisions: dict[tuple[str, str], dict[str, Any]] = {}
    for row in loaded:
        if not isinstance(row, dict):
            continue
        arxiv_id = str(row.get("arxiv_id", "")).strip()
        person_id = str(row.get("person_id", "")).strip()
        if arxiv_id and person_id:
            decisions[(sources.normalize_arxiv_id(arxiv_id), person_id)] = row
    return decisions


def _build_alias_specs(display_name: str, manual_entry: Mapping[str, Any] | None) -> tuple[AliasSpec, ...]:
    specs: list[AliasSpec] = []
    seen: set[str] = set()

    def add(alias: str, rule: str) -> None:
        alias = str(alias).strip()
        normalized = _normalize_name(alias)
        token = _search_token_from_alias(alias)
        if not alias or not normalized or not token or normalized in seen:
            return
        seen.add(normalized)
        specs.append(AliasSpec(alias=alias, match_rule=rule, normalized=normalized, search_token=token))

    add(display_name, "display_name")
    if manual_entry:
        for alias in manual_entry.get("arxiv_names", []) or []:
            add(str(alias), "manual_alias")
    return tuple(specs)


def build_review_people(
    history: roster_history.HistoryResult,
    config: env.UvaArxivConfig,
    role_group: str,
    scan_start: date,
    as_of_date: date,
    exclude_person_ids: Iterable[str] = DEFAULT_EXCLUDE_PERSON_IDS,
) -> list[ReviewPerson]:
    manual_aliases = _load_manual_aliases(config.data_dir / "aliases.yml")
    excluded = set(exclude_person_ids)
    people: list[ReviewPerson] = []
    for person_id, intervals in sorted(history.appointments.items()):
        if person_id in excluded:
            continue
        role_intervals = tuple(interval for interval in intervals if interval.role_group == role_group)
        if not role_intervals or not _intervals_overlap_scan(role_intervals, scan_start, as_of_date):
            continue
        summary = history.people.get(person_id, roster_history.PersonSummary(person_id, person_id))
        aliases = _build_alias_specs(summary.display_name, manual_aliases.get(person_id))
        if not aliases:
            continue
        people.append(
            ReviewPerson(
                person_id=person_id,
                display_name=summary.display_name,
                intervals=role_intervals,
                aliases=aliases,
            )
        )
    return sorted(people, key=lambda person: (person.display_name.split()[-1].casefold(), person.display_name.casefold()))


def _candidate_from_paper(
    person: ReviewPerson,
    paper: arxiv_db.PaperRecord,
    alias: AliasSpec,
) -> CandidateRow | None:
    paper_date = _date_from_string(paper.date)
    if not any(_interval_contains(interval, paper_date) for interval in person.intervals):
        return None
    if not _contains_normalized_name(paper.authors, alias.normalized):
        return None
    return CandidateRow(
        person_id=person.person_id,
        display_name=person.display_name,
        arxiv_id=paper.id,
        date=paper.date,
        title=paper.title,
        authors=paper.authors,
        categories=paper.categories,
        matched_author=alias.alias,
        match_rule=alias.match_rule,
        status=_paper_status(person.person_id, paper_date),
        note="",
        arxiv_url=_format_url(paper.id),
    )


def _fetch_papers_for_alias(
    conn: sqlite3.Connection,
    alias: AliasSpec,
    scan_start: date,
) -> list[arxiv_db.PaperRecord]:
    token = _sql_like_escape(alias.search_token)
    rows = conn.execute(
        """
        SELECT id, title, abstract, categories, authors, date
        FROM papers
        WHERE date >= ?
          AND categories LIKE '%math%'
          AND lower(authors) LIKE ? ESCAPE '\\'
        ORDER BY date, id
        """,
        (scan_start.isoformat(), f"%{token.casefold()}%"),
    ).fetchall()
    return [arxiv_db.PaperRecord.from_mapping(dict(row)) for row in rows]


def _add_candidate(
    candidates: dict[tuple[str, str], CandidateRow],
    candidate: CandidateRow,
) -> None:
    key = (candidate.person_id, candidate.arxiv_id)
    existing = candidates.get(key)
    if existing is None or _match_rule_priority(candidate.match_rule) < _match_rule_priority(existing.match_rule):
        candidates[key] = candidate


def _candidate_for_manual_accept(
    person: ReviewPerson,
    paper: arxiv_db.PaperRecord,
) -> CandidateRow | None:
    candidates = [
        candidate
        for alias in person.aliases
        if (candidate := _candidate_from_paper(person, paper, alias)) is not None
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda row: _match_rule_priority(row.match_rule))


def _add_manual_accept_candidates(
    conn: sqlite3.Connection,
    config: env.UvaArxivConfig,
    people_by_id: Mapping[str, ReviewPerson],
    candidates: dict[tuple[str, str], CandidateRow],
    scan_start: date,
) -> None:
    """Seed explicitly accepted rows that fall outside the normal math-category scan."""
    accepted = _load_decisions(config.data_dir / "accepted_matches.yml")
    for arxiv_id, person_id in sorted(accepted):
        key = (person_id, arxiv_id)
        if key in candidates:
            continue
        person = people_by_id.get(person_id)
        if person is None:
            continue
        row = conn.execute(
            """
            SELECT id, title, abstract, categories, authors, date
            FROM papers
            WHERE id = ? AND date >= ?
            """,
            (arxiv_id, scan_start.isoformat()),
        ).fetchone()
        if row is None:
            continue
        paper = arxiv_db.PaperRecord.from_mapping(dict(row))
        candidate = _candidate_for_manual_accept(person, paper)
        if candidate is not None:
            _add_candidate(candidates, candidate)


def build_candidates(
    config: env.UvaArxivConfig,
    people: Iterable[ReviewPerson],
    scan_start: date,
) -> list[CandidateRow]:
    people_list = list(people)
    people_by_id = {person.person_id: person for person in people_list}
    token_to_aliases: dict[str, list[tuple[ReviewPerson, AliasSpec]]] = defaultdict(list)
    for person in people_list:
        for alias in person.aliases:
            token_to_aliases[alias.search_token].append((person, alias))

    candidates: dict[tuple[str, str], CandidateRow] = {}
    with arxiv_db.connect_readonly(config.arxiv_db) as conn:
        arxiv_db.validate_papers_schema(conn)
        rows = conn.execute(
            """
            SELECT id, title, abstract, categories, authors, date
            FROM papers
            WHERE date >= ?
              AND categories LIKE '%math%'
            ORDER BY date, id
            """,
            (scan_start.isoformat(),),
        ).fetchall()
        for db_row in rows:
            paper = arxiv_db.PaperRecord.from_mapping(dict(db_row))
            normalized_authors = _normalize_name(paper.authors)
            author_tokens = set(normalized_authors.split())
            possible_aliases = [
                item
                for token in author_tokens
                for item in token_to_aliases.get(token, [])
            ]
            if not possible_aliases:
                continue
            for person, alias in possible_aliases:
                candidate = _candidate_from_paper(person, paper, alias)
                if candidate is not None:
                    _add_candidate(candidates, candidate)
        _add_manual_accept_candidates(conn, config, people_by_id, candidates, scan_start)
    return sorted(candidates.values(), key=lambda row: (row.display_name.split()[-1].casefold(), row.display_name.casefold(), row.date, row.arxiv_id))


def _match_rule_priority(rule: str) -> int:
    return {"display_name": 0, "manual_alias": 1}.get(rule, 9)


def _infer_source_format(source_dir: Path, files: tuple[str, ...]) -> str:
    if not source_dir.exists():
        return "missing"
    if not files:
        return "empty"
    if len(files) == 1 and files[0].lower().endswith(".pdf"):
        return "pdf"
    if len(files) == 1 and files[0].lower() == "source.tex":
        return "raw"
    return "existing"


def scan_sources_for_candidates(
    config: env.UvaArxivConfig,
    candidates: list[CandidateRow],
    fetch_missing: bool = False,
    force_fetch: bool = False,
    rate_limit: float = sources.DEFAULT_RATE_LIMIT_SECONDS,
    write_cache: bool = True,
    out: TextIO = sys.stdout,
) -> dict[str, SourceEvidenceRow]:
    by_id: dict[str, list[CandidateRow]] = defaultdict(list)
    for candidate in candidates:
        by_id[candidate.arxiv_id].append(candidate)
    patterns = affiliation.load_patterns(config.data_dir / "affiliation_patterns.yml")
    rows: dict[str, SourceEvidenceRow] = {}
    for index, (arxiv_id, candidate_rows) in enumerate(sorted(by_id.items()), start=1):
        if index == 1 or index % 25 == 0 or index == len(by_id):
            print(f"source scan {index}/{len(by_id)}: {arxiv_id}", file=out)
        source_dir = sources.source_dir_for_id(config.arxiv_sources_dir, arxiv_id)
        fetch_status = "not_fetched"
        source_format = "missing"
        bytes_fetched = 0
        files_written = 0
        error = ""
        try:
            if fetch_missing or force_fetch:
                result = sources.fetch_source(
                    config=config,
                    arxiv_id=arxiv_id,
                    force=force_fetch,
                    rate_limit_seconds=rate_limit,
                )
                fetch_status = result.status
                source_format = result.source_format
                bytes_fetched = result.bytes_fetched
                files_written = len(result.files_written)
            else:
                existing = sources.existing_source_files(source_dir)
                fetch_status = "exists" if existing else "missing_source"
                source_format = _infer_source_format(source_dir, existing)
                files_written = len(existing)
            scan_result = affiliation.scan_source_dir(arxiv_id, source_dir, patterns)
            if write_cache:
                affiliation.store_scan_result(scan_result, config.cache_dir / affiliation.DEFAULT_CACHE_NAME)
        except Exception as exc:  # noqa: BLE001 - report and continue for review.
            scan_result = affiliation.AffiliationScanResult(
                arxiv_id=sources.normalize_arxiv_id(arxiv_id),
                safe_id=sources.safe_source_dir_name(arxiv_id),
                source_dir=str(source_dir),
                evidence="scan_error",
                checked_files=0,
                positive_count=0,
                negative_count=0,
                matches=(),
                notes=str(exc),
            )
            error = str(exc)
        rows[arxiv_id] = SourceEvidenceRow(
            arxiv_id=arxiv_id,
            fetch_status=fetch_status,
            source_format=source_format,
            bytes_fetched=bytes_fetched,
            files_written=files_written,
            affiliation_evidence=scan_result.evidence,
            checked_files=scan_result.checked_files,
            positive_count=scan_result.positive_count,
            negative_count=scan_result.negative_count,
            matched_people="; ".join(
                f"{row.display_name} ({row.person_id})"
                for row in sorted(candidate_rows, key=lambda item: item.display_name)
            ),
            title=candidate_rows[0].title,
            categories=candidate_rows[0].categories,
            source_dir=str(source_dir),
            error=error,
        )
    return rows


def _decision_row(
    candidate: CandidateRow,
    source_row: SourceEvidenceRow | None,
    decision_source: str,
    check_reason: str = "",
    note: str | None = None,
) -> dict[str, str]:
    source_row = source_row or SourceEvidenceRow(
        arxiv_id=candidate.arxiv_id,
        fetch_status="missing_scan",
        source_format="",
        bytes_fetched=0,
        files_written=0,
        affiliation_evidence="missing_scan",
        checked_files=0,
        positive_count=0,
        negative_count=0,
        matched_people="",
        title=candidate.title,
        categories=candidate.categories,
        source_dir="",
        error="",
    )
    return {
        **candidate.to_dict(),
        "decision_source": decision_source,
        "affiliation_evidence": source_row.affiliation_evidence,
        "positive_count": str(source_row.positive_count),
        "negative_count": str(source_row.negative_count),
        "checked_files": str(source_row.checked_files),
        "source_format": source_row.source_format,
        "source_dir": source_row.source_dir,
        "note": candidate.note if note is None else note,
        "check_reason": check_reason,
    }


def apply_decisions(
    config: env.UvaArxivConfig,
    candidates: list[CandidateRow],
    source_rows: Mapping[str, SourceEvidenceRow],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    accepted = _load_decisions(config.data_dir / "accepted_matches.yml")
    rejected = _load_decisions(config.data_dir / "rejected_matches.yml")
    confirmed_rows: list[dict[str, str]] = []
    rejected_rows: list[dict[str, str]] = []
    to_check_rows: list[dict[str, str]] = []
    for candidate in sorted(candidates, key=lambda row: (row.display_name.split()[-1].casefold(), row.display_name.casefold(), row.date, row.arxiv_id)):
        key = (candidate.arxiv_id, candidate.person_id)
        source_row = source_rows.get(candidate.arxiv_id)
        if key in rejected:
            reason = str(rejected[key].get("reason", "manual reject"))
            rejected_rows.append(_decision_row(candidate, source_row, "manual_reject", check_reason=reason))
        elif source_row and source_row.positive_count > 0:
            confirmed_rows.append(_decision_row(candidate, source_row, "source_positive"))
        elif key in accepted:
            reason = str(accepted[key].get("reason", "manual accept"))
            confirmed_rows.append(_decision_row(candidate, source_row, "manual_accept", note=reason))
        else:
            reason = source_row.affiliation_evidence if source_row else "missing_scan"
            if source_row and source_row.error:
                reason += f": {source_row.error}"
            to_check_rows.append(_decision_row(candidate, source_row, "needs_check", check_reason=reason))
    return confirmed_rows, rejected_rows, to_check_rows


def _write_csv(path: Path, rows: Iterable[Mapping[str, str]], fieldnames: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(fieldnames), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _person_sort_key(item: tuple[tuple[str, str], list[Mapping[str, str]]]) -> tuple[str, str]:
    (name, _person_id), _rows = item
    return (name.split()[-1].casefold(), name.casefold())


def render_candidates_markdown(
    people: list[ReviewPerson],
    candidates: list[CandidateRow],
    config: env.UvaArxivConfig,
    scan_start: date,
) -> str:
    by_person: dict[str, list[CandidateRow]] = defaultdict(list)
    for candidate in candidates:
        by_person[candidate.person_id].append(candidate)
    matched_people = {candidate.person_id for candidate in candidates}
    lines = [
        "# UVA arXiv TT candidates",
        "",
        "Internal review candidates. Not public data.",
        "",
        "## Method",
        "",
        f"- arXiv DB: `{config.arxiv_db}`",
        f"- Date range: `{scan_start.isoformat()}` through DB contents",
        '- Category filter: `categories LIKE "%math%"`',
        "- People: faculty appointment intervals from roster history, with manual aliases.",
        f"- Excluded person IDs: {', '.join(DEFAULT_EXCLUDE_PERSON_IDS)}",
        "- Match rules: exact normalized display-name match plus manual `arxiv_names` aliases.",
        "- Appointment filter: paper date must fall inside a faculty appointment interval.",
        "",
        "## Summary",
        "",
        f"- TT people considered: {len(people)}",
        f"- matched people: {len(matched_people)}",
        f"- unmatched people: {len(people) - len(matched_people)}",
        f"- person-paper candidate rows: {len(candidates)}",
        "",
        "| Person | UVA id | candidates |",
        "|---|---|---:|",
    ]
    for person in people:
        lines.append(f"| {person.display_name} | `{person.person_id}` | {len(by_person.get(person.person_id, []))} |")
    lines.extend(["", "## Candidates by person", ""])
    for person in people:
        rows = sorted(by_person.get(person.person_id, []), key=lambda row: (row.date, row.arxiv_id))
        lines.append(f"### {person.display_name} (`{person.person_id}`) — {len(rows)}")
        lines.append("")
        if not rows:
            lines.append("No candidates found.")
            lines.append("")
            continue
        lines.append("| Date | arXiv | Title | Authors | Categories | Match | Status |")
        lines.append("|---|---|---|---|---|---|---|")
        for row in rows:
            lines.append(
                f"| {row.date} | [{row.arxiv_id}]({row.arxiv_url}) | {_markdown_escape(row.title)} | "
                f"{_markdown_escape(row.authors)} | {_markdown_escape(row.categories)} | "
                f"{_markdown_escape(row.matched_author)} / {row.match_rule} | {row.status} |"
            )
        lines.append("")
    return "\n".join(lines)


def render_source_markdown(source_rows: Iterable[SourceEvidenceRow]) -> str:
    rows = list(source_rows)
    evidence_counts = Counter(row.affiliation_evidence for row in rows)
    lines = [
        "# UVA arXiv TT source-affiliation evidence",
        "",
        "Internal source scan report. Absence of UVA evidence is not a rejection reason.",
        "",
        f"- Unique arXiv IDs: {len(rows)}",
        "",
        "## Evidence counts",
        "",
        "| Evidence | Count |",
        "|---|---:|",
    ]
    for evidence, count in sorted(evidence_counts.items()):
        lines.append(f"| {evidence} | {count} |")
    lines.extend([
        "",
        "## Details",
        "",
        "| arXiv | Evidence | + | - | Files | Source format | People | Title | Error |",
        "|---|---|---:|---:|---:|---|---|---|---|",
    ])
    for row in sorted(rows, key=lambda item: item.arxiv_id):
        lines.append(
            f"| [{row.arxiv_id}](https://arxiv.org/abs/{row.arxiv_id}) | {row.affiliation_evidence} | "
            f"{row.positive_count} | {row.negative_count} | {row.checked_files} | {row.source_format} | "
            f"{_markdown_escape(row.matched_people)} | {_markdown_escape(row.title)} | {_markdown_escape(row.error)} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_decision_markdown(
    title: str,
    rows: list[Mapping[str, str]],
    description: str,
    mode: str,
) -> str:
    by_person: dict[tuple[str, str], list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        by_person[(row["display_name"], row["person_id"])].append(row)
    lines = [
        f"# {title}",
        "",
        description,
        "",
        f"- Rows: {len(rows)}",
        f"- Unique arXiv IDs: {len({row['arxiv_id'] for row in rows})}",
        f"- People: {len(by_person)}",
        "",
        "## Decision source counts",
        "",
        "| Decision source | Count |",
        "|---|---:|",
    ]
    for decision_source, count in sorted(Counter(row["decision_source"] for row in rows).items()):
        lines.append(f"| {decision_source} | {count} |")
    lines.extend(["", "## Evidence counts", "", "| Evidence | Count |", "|---|---:|"])
    for evidence, count in sorted(Counter(row["affiliation_evidence"] for row in rows).items()):
        lines.append(f"| {evidence} | {count} |")
    lines.extend(["", "## By person", "", "| Person | UVA id | rows |", "|---|---|---:|"])
    for (name, person_id), person_rows in sorted(by_person.items(), key=lambda item: (item[0][0].split()[-1].casefold(), item[0][0].casefold())):
        lines.append(f"| {name} | `{person_id}` | {len(person_rows)} |")
    lines.extend(["", "## Details", ""])
    for (name, person_id), person_rows in sorted(by_person.items(), key=lambda item: (item[0][0].split()[-1].casefold(), item[0][0].casefold())):
        lines.append(f"### {name} (`{person_id}`) — {len(person_rows)}")
        lines.append("")
        if mode == "confirmed":
            lines.append("| Date | arXiv | Title | Authors | Decision | Evidence | + | - |")
            lines.append("|---|---|---|---|---|---|---:|---:|")
            for row in sorted(person_rows, key=lambda item: (item["date"], item["arxiv_id"])):
                lines.append(
                    f"| {row['date']} | [{row['arxiv_id']}]({row['arxiv_url']}) | {_markdown_escape(row['title'])} | "
                    f"{_markdown_escape(row['authors'])} | {row['decision_source']} | {row['affiliation_evidence']} | "
                    f"{row['positive_count']} | {row['negative_count']} |"
                )
        elif mode == "rejected":
            lines.append("| Date | arXiv | Title | Authors | Reason |")
            lines.append("|---|---|---|---|---|")
            for row in sorted(person_rows, key=lambda item: (item["date"], item["arxiv_id"])):
                lines.append(
                    f"| {row['date']} | [{row['arxiv_id']}]({row['arxiv_url']}) | {_markdown_escape(row['title'])} | "
                    f"{_markdown_escape(row['authors'])} | {_markdown_escape(row['check_reason'])} |"
                )
        else:
            lines.append("| Date | arXiv | Title | Authors | Evidence | Reason | Source format |")
            lines.append("|---|---|---|---|---|---|---|")
            for row in sorted(person_rows, key=lambda item: (item["date"], item["arxiv_id"])):
                lines.append(
                    f"| {row['date']} | [{row['arxiv_id']}]({row['arxiv_url']}) | {_markdown_escape(row['title'])} | "
                    f"{_markdown_escape(row['authors'])} | {row['affiliation_evidence']} | "
                    f"{_markdown_escape(row['check_reason'])} | {row['source_format']} |"
                )
        lines.append("")
    return "\n".join(lines)


def write_review_reports(
    config: env.UvaArxivConfig,
    people: list[ReviewPerson],
    candidates: list[CandidateRow],
    source_rows: Mapping[str, SourceEvidenceRow],
    confirmed_rows: list[dict[str, str]],
    rejected_rows: list[dict[str, str]],
    to_check_rows: list[dict[str, str]],
    output_dir: Path,
    label: str,
    scan_start: date,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "candidates_csv": output_dir / f"uva-arxiv-{label}-candidates.csv",
        "candidates_md": output_dir / f"uva-arxiv-{label}-candidates.md",
        "source_csv": output_dir / f"uva-arxiv-{label}-source-affiliation.csv",
        "source_md": output_dir / f"uva-arxiv-{label}-source-affiliation.md",
        "confirmed_csv": output_dir / f"uva-arxiv-{label}-confirmed-matches.csv",
        "confirmed_md": output_dir / f"uva-arxiv-{label}-confirmed-matches.md",
        "rejected_csv": output_dir / f"uva-arxiv-{label}-rejected-matches.csv",
        "rejected_md": output_dir / f"uva-arxiv-{label}-rejected-matches.md",
        "to_check_csv": output_dir / f"uva-arxiv-{label}-to-check.csv",
        "to_check_md": output_dir / f"uva-arxiv-{label}-to-check.md",
    }
    _write_csv(paths["candidates_csv"], [row.to_dict() for row in candidates], CANDIDATE_FIELDS)
    paths["candidates_md"].write_text(render_candidates_markdown(people, candidates, config, scan_start), encoding="utf-8")
    _write_csv(paths["source_csv"], [row.to_dict() for row in sorted(source_rows.values(), key=lambda item: item.arxiv_id)], SOURCE_FIELDS)
    paths["source_md"].write_text(render_source_markdown(source_rows.values()), encoding="utf-8")
    _write_csv(paths["confirmed_csv"], confirmed_rows, DECISION_FIELDS)
    paths["confirmed_md"].write_text(
        render_decision_markdown(
            "UVA arXiv TT confirmed matches",
            confirmed_rows,
            "Rows accepted as matches either because unpacked arXiv source has positive UVA affiliation evidence or because LP manually confirmed the row.",
            "confirmed",
        ),
        encoding="utf-8",
    )
    _write_csv(paths["rejected_csv"], rejected_rows, DECISION_FIELDS)
    paths["rejected_md"].write_text(
        render_decision_markdown(
            "UVA arXiv TT rejected candidate matches",
            rejected_rows,
            "Rows manually rejected as name collisions or otherwise out of scope.",
            "rejected",
        ),
        encoding="utf-8",
    )
    _write_csv(paths["to_check_csv"], to_check_rows, DECISION_FIELDS)
    paths["to_check_md"].write_text(
        render_decision_markdown(
            "UVA arXiv TT candidates to check",
            to_check_rows,
            "Rows with no positive UVA affiliation hit in the unpacked arXiv source and no manual accept/reject decision yet. These are not rejected; they need manual checking.",
            "check",
        ),
        encoding="utf-8",
    )
    return list(paths.values())


def sync_to_archive(paths: Iterable[Path], archive_dir: Path) -> None:
    archive_dir.mkdir(parents=True, exist_ok=True)
    for path in paths:
        if path.exists():
            shutil.copy2(path, archive_dir / path.name)


def build_review_reports(
    role_group: str = DEFAULT_ROLE_GROUP,
    label: str = DEFAULT_LABEL,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    as_of_date: date | None = None,
    fetch_sources: bool = False,
    force_fetch_sources: bool = False,
    no_source_cache: bool = False,
    sync_archive: Path | None = None,
    out: TextIO = sys.stdout,
) -> tuple[list[Path], dict[str, int]]:
    config = env.load_config(ensure_dirs=True)
    as_of_date = as_of_date or date.today()
    scan_start = roster_history.parse_date(config.initial_arxiv_start_date, "initial_arxiv_start_date")
    history = roster_history.build_from_repo(config, as_of_date)
    people = build_review_people(history, config, role_group, scan_start, as_of_date)
    print(f"review_people: {len(people)}", file=out)
    candidates = build_candidates(config, people, scan_start)
    print(f"candidate_rows: {len(candidates)}", file=out)
    print(f"candidate_unique_arxiv_ids: {len({row.arxiv_id for row in candidates})}", file=out)
    source_rows = scan_sources_for_candidates(
        config=config,
        candidates=candidates,
        fetch_missing=fetch_sources,
        force_fetch=force_fetch_sources,
        write_cache=not no_source_cache,
        out=out,
    )
    confirmed_rows, rejected_rows, to_check_rows = apply_decisions(config, candidates, source_rows)
    print(f"confirmed_rows: {len(confirmed_rows)}", file=out)
    print(f"rejected_rows: {len(rejected_rows)}", file=out)
    print(f"to_check_rows: {len(to_check_rows)}", file=out)
    paths = write_review_reports(
        config=config,
        people=people,
        candidates=candidates,
        source_rows=source_rows,
        confirmed_rows=confirmed_rows,
        rejected_rows=rejected_rows,
        to_check_rows=to_check_rows,
        output_dir=output_dir,
        label=label,
        scan_start=scan_start,
    )
    if sync_archive is not None:
        sync_to_archive(paths, sync_archive)
    counts = {
        "people": len(people),
        "candidates": len(candidates),
        "unique_arxiv_ids": len({row.arxiv_id for row in candidates}),
        "confirmed": len(confirmed_rows),
        "rejected": len(rejected_rows),
        "to_check": len(to_check_rows),
    }
    return paths, counts


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build UVA arXiv internal review reports.")
    parser.add_argument("--role", default=DEFAULT_ROLE_GROUP, choices=("faculty", "postdoc", "grad", "agfm_other", "emeritus"))
    parser.add_argument("--label", default=DEFAULT_LABEL, help="Output filename label, e.g. tt.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--as-of", help="As-of date for open appointments, YYYY-MM-DD.")
    parser.add_argument("--fetch-sources", action="store_true", help="Fetch missing e-print sources before scanning.")
    parser.add_argument("--force-fetch-sources", action="store_true", help="Replace existing e-print source directories.")
    parser.add_argument("--no-source-cache", action="store_true", help="Do not write affiliation scan cache rows.")
    parser.add_argument("--sync-archive", type=Path, nargs="?", const=DEFAULT_REVIEW_ARCHIVE, help="Copy reports to the private audit archive.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    as_of_date = roster_history.parse_date(args.as_of, "as-of date") if args.as_of else None
    paths, counts = build_review_reports(
        role_group=args.role,
        label=args.label,
        output_dir=args.output_dir,
        as_of_date=as_of_date,
        fetch_sources=args.fetch_sources,
        force_fetch_sources=args.force_fetch_sources,
        no_source_cache=args.no_source_cache,
        sync_archive=args.sync_archive,
    )
    print("wrote:")
    for path in paths:
        print(f"  {path}")
    print("counts:")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Appointment history and person-by-academic-year roster output."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, TextIO

try:
    from . import env, roles, roster
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.uva_arxiv import env, roles, roster


ACTIVE_DIRECTORY_KEYS = {"legacy", "faculty", "postdoc", "grad", "lecturer", "emeriti"}
DIRECTORY_KEYS = {
    "faculty": "faculty",
    "postdocs": "postdoc",
    "gradstudents": "grad",
    "lecturers": "lecturer",
    "emeriti": "emeriti",
    "_unpublished": "unpublished",
}
ROLE_GROUPS = tuple(roles.ROLE_GROUPS)
CSV_COLUMNS = (
    "person_id",
    "display_name",
    "academic_year",
    "start_date",
    "end_date",
    "role_group",
    "position",
    "source",
    "confidence",
    "current_active",
)


class RosterHistoryError(RuntimeError):
    """Raised when roster history cannot be reconstructed."""


@dataclass(frozen=True)
class HistoricalPersonRecord:
    person_id: str
    display_name: str
    role_group: str
    position: str
    published: bool
    path: str
    directory_key: str

    @property
    def active(self) -> bool:
        return (
            self.published
            and self.directory_key in ACTIVE_DIRECTORY_KEYS
            and self.role_group in roles.ROLE_GROUPS
        )


@dataclass(frozen=True)
class HistoryFileEvent:
    commit: str
    commit_date: date
    status: str
    path: str
    old_path: str | None = None
    record: HistoricalPersonRecord | None = None


@dataclass
class AppointmentInterval:
    start_date: date
    end_date: date | None
    role_group: str
    position: str
    source: str
    confidence: str
    start_commit: str | None = None
    end_commit: str | None = None
    start_path: str | None = None
    end_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_date": format_date(self.start_date),
            "end_date": format_date(self.end_date),
            "role_group": self.role_group,
            "position": self.position,
            "source": self.source,
            "confidence": self.confidence,
            "start_commit": self.start_commit,
            "end_commit": self.end_commit,
            "start_path": self.start_path,
            "end_path": self.end_path,
        }


@dataclass(frozen=True)
class PersonSummary:
    person_id: str
    display_name: str

    def to_dict(self) -> dict[str, str]:
        return {"person_id": self.person_id, "display_name": self.display_name}


@dataclass(frozen=True)
class HistoryNotice:
    person_id: str
    notice_type: str
    message: str
    path: str | None = None
    commit: str | None = None
    date: date | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "person_id": self.person_id,
            "type": self.notice_type,
            "message": self.message,
            "path": self.path,
            "commit": self.commit,
            "date": format_date(self.date),
        }


@dataclass(frozen=True)
class ActiveYearRow:
    person_id: str
    display_name: str
    academic_year: str
    start_date: date
    end_date: date
    role_group: str
    position: str
    source: str
    confidence: str
    current_active: bool

    def to_dict(self) -> dict[str, str]:
        return {
            "person_id": self.person_id,
            "display_name": self.display_name,
            "academic_year": self.academic_year,
            "start_date": format_date(self.start_date) or "",
            "end_date": format_date(self.end_date) or "",
            "role_group": self.role_group,
            "position": self.position,
            "source": self.source,
            "confidence": self.confidence,
            "current_active": "true" if self.current_active else "false",
        }


@dataclass(frozen=True)
class AppointmentOverride:
    display_name: str | None = None
    appointments: list[AppointmentInterval] = field(default_factory=list)


@dataclass(frozen=True)
class HistoryResult:
    people: dict[str, PersonSummary]
    appointments: dict[str, list[AppointmentInterval]]
    rows: list[ActiveYearRow]
    notices: list[HistoryNotice]
    initial_start_date: date
    as_of_date: date
    generated_at: str

    def counts_by_year_role(self) -> dict[str, dict[str, int]]:
        counts: dict[str, dict[str, int]] = {}
        for row in self.rows:
            year_counts = counts.setdefault(row.academic_year, {role_group: 0 for role_group in ROLE_GROUPS})
            year_counts[row.role_group] = year_counts.get(row.role_group, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        people = []
        for person_id in sorted(self.appointments):
            summary = self.people.get(person_id, PersonSummary(person_id, person_id))
            intervals = self.appointments[person_id]
            active_years = sorted(
                {
                    int(row.academic_year[:4])
                    for row in self.rows
                    if row.person_id == person_id
                }
            )
            people.append(
                {
                    **summary.to_dict(),
                    "appointments": [interval.to_dict() for interval in intervals],
                    "active_years": active_years,
                }
            )
        return {
            "generated_at": self.generated_at,
            "initial_start_date": format_date(self.initial_start_date),
            "as_of_date": format_date(self.as_of_date),
            "people": people,
            "rows": [row.to_dict() for row in self.rows],
            "counts_by_year_role": self.counts_by_year_role(),
            "notices": [notice.to_dict() for notice in self.notices],
        }


def parse_date(value: Any, field_name: str = "date") -> date:
    if isinstance(value, date):
        return value
    if value is None or str(value).strip() == "":
        raise RosterHistoryError(f"{field_name} is required")
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise RosterHistoryError(f"{field_name} must be YYYY-MM-DD: {value}") from exc


def format_date(value: date | None) -> str | None:
    return value.isoformat() if value else None


def directory_key_for_path(path: str) -> str:
    parts = Path(path).parts
    if len(parts) < 2 or parts[0] != "_departmentpeople":
        return "inactive"
    if len(parts) == 2:
        return "legacy"
    return DIRECTORY_KEYS.get(parts[1], "inactive")


def front_matter_from_text(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise RosterHistoryError("missing YAML front matter opening marker")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:index])
    raise RosterHistoryError("missing YAML front matter closing marker")


def parse_historical_record(text: str, repo_path: str) -> HistoricalPersonRecord:
    front_matter = roster.parse_front_matter(front_matter_from_text(text))
    person_id = roster.clean_text(front_matter.get("UVA_id") or front_matter.get("uva_id"))
    if not person_id:
        raise RosterHistoryError("missing UVA_id")

    directory_key = directory_key_for_path(repo_path)
    role_directory_key = None if directory_key in {"legacy", "inactive"} else directory_key
    classification = roles.classify_role(front_matter, role_directory_key)
    display_name, _first, _last = roster.display_name_from_front_matter(front_matter)

    return HistoricalPersonRecord(
        person_id=person_id,
        display_name=display_name or person_id,
        role_group=classification.role_group,
        position=roster.clean_text(front_matter.get("position")) or classification.rank_label,
        published=roster.parse_bool(front_matter.get("published"), default=True),
        path=repo_path,
        directory_key=directory_key,
    )


def _run_git(repo_root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def parse_git_name_status(text: str) -> list[tuple[str, date, str, list[str]]]:
    commits: list[tuple[str, date, str, list[str]]] = []
    current_commit: str | None = None
    current_date: date | None = None

    for line in text.splitlines():
        if not line.strip():
            continue
        if line.startswith("commit "):
            _label, commit_hash, commit_date = line.split(maxsplit=2)
            current_commit = commit_hash
            current_date = parse_date(commit_date, "commit date")
            continue
        if current_commit is None or current_date is None:
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            commits.append((current_commit, current_date, parts[0], parts[1:]))
    return commits


def git_history_events(repo_root: Path) -> tuple[list[HistoryFileEvent], list[HistoryNotice]]:
    log_text = _run_git(
        repo_root,
        [
            "log",
            "--reverse",
            "--date=short",
            "--pretty=format:commit %H %ad",
            "--name-status",
            "--find-renames",
            "--",
            "_departmentpeople",
        ],
    )
    events: list[HistoryFileEvent] = []
    notices: list[HistoryNotice] = []

    for commit, commit_date, raw_status, paths in parse_git_name_status(log_text):
        status = raw_status[:1]
        if status not in {"A", "M", "D", "R", "C"}:
            continue
        if status in {"R", "C"}:
            if len(paths) < 2:
                continue
            old_path, path = paths[0], paths[1]
        else:
            old_path, path = None, paths[0]
        if not path.endswith(".md"):
            continue

        record: HistoricalPersonRecord | None = None
        if status != "D":
            try:
                content = _run_git(repo_root, ["show", f"{commit}:{path}"])
                record = parse_historical_record(content, path)
            except (subprocess.CalledProcessError, RosterHistoryError, roster.RosterError) as exc:
                notices.append(
                    HistoryNotice(
                        person_id=Path(path).stem,
                        notice_type="history_parse_error",
                        message=str(exc),
                        path=path,
                        commit=commit,
                        date=commit_date,
                    )
                )
                continue

        events.append(
            HistoryFileEvent(
                commit=commit,
                commit_date=commit_date,
                status=status,
                path=path,
                old_path=old_path,
                record=record,
            )
        )
    return events, notices


def interval_from_record(event: HistoryFileEvent, record: HistoricalPersonRecord) -> AppointmentInterval:
    return AppointmentInterval(
        start_date=event.commit_date,
        end_date=None,
        role_group=record.role_group,
        position=record.position,
        source="git-history",
        confidence="commit-date",
        start_commit=event.commit,
        start_path=record.path,
    )


def close_interval(
    interval: AppointmentInterval,
    event: HistoryFileEvent,
    path: str | None = None,
) -> None:
    if interval.end_date is None:
        interval.end_date = event.commit_date
        interval.end_commit = event.commit
        interval.end_path = path or event.path


def infer_git_intervals(
    events: Iterable[HistoryFileEvent],
) -> tuple[dict[str, PersonSummary], dict[str, list[AppointmentInterval]], list[HistoryNotice]]:
    people: dict[str, PersonSummary] = {}
    appointments: dict[str, list[AppointmentInterval]] = defaultdict(list)
    open_intervals: dict[str, AppointmentInterval] = {}
    path_to_person: dict[str, str] = {}
    notices: list[HistoryNotice] = []

    for event in events:
        if event.status == "D":
            person_id = path_to_person.pop(event.path, None)
            if person_id and person_id in open_intervals:
                close_interval(open_intervals.pop(person_id), event)
            continue

        record = event.record
        if record is None:
            continue

        previous_person_id = None
        previous_path = event.old_path or event.path
        if event.old_path:
            previous_person_id = path_to_person.pop(event.old_path, None)
        else:
            previous_person_id = path_to_person.get(event.path)
        if previous_person_id and previous_person_id != record.person_id and previous_person_id in open_intervals:
            close_interval(open_intervals.pop(previous_person_id), event, previous_path)
            notices.append(
                HistoryNotice(
                    person_id=previous_person_id,
                    notice_type="path_person_id_change",
                    message=f"path now has a different UVA_id: {record.person_id}",
                    path=previous_path,
                    commit=event.commit,
                    date=event.commit_date,
                )
            )

        path_to_person[event.path] = record.person_id
        people[record.person_id] = PersonSummary(record.person_id, record.display_name)
        current = open_intervals.get(record.person_id)

        if not record.active:
            if current is not None:
                close_interval(open_intervals.pop(record.person_id), event)
                notices.append(
                    HistoryNotice(
                        person_id=record.person_id,
                        notice_type="inferred_inactive_boundary",
                        message=f"record became inactive via {record.directory_key or 'front matter'}",
                        path=record.path,
                        commit=event.commit,
                        date=event.commit_date,
                    )
                )
            continue

        if current is None:
            interval = interval_from_record(event, record)
            appointments[record.person_id].append(interval)
            open_intervals[record.person_id] = interval
            continue

        if current.role_group != record.role_group or current.position != record.position:
            close_interval(open_intervals.pop(record.person_id), event)
            notices.append(
                HistoryNotice(
                    person_id=record.person_id,
                    notice_type="inferred_role_or_position_boundary",
                    message=f"{current.role_group}/{current.position} -> {record.role_group}/{record.position}",
                    path=record.path,
                    commit=event.commit,
                    date=event.commit_date,
                )
            )
            interval = interval_from_record(event, record)
            appointments[record.person_id].append(interval)
            open_intervals[record.person_id] = interval

    return people, {person_id: list(intervals) for person_id, intervals in appointments.items()}, notices


def load_override_mapping(path: Path) -> dict[str, Any]:
    try:
        return env.load_yaml_mapping_file(path)
    except env.ConfigError as exc:
        raise RosterHistoryError(str(exc)) from exc


def load_appointment_overrides(path: Path) -> dict[str, AppointmentOverride]:
    loaded = load_override_mapping(path)
    overrides: dict[str, AppointmentOverride] = {}

    for person_id, raw_value in loaded.items():
        if raw_value in (None, ""):
            continue
        if not isinstance(raw_value, Mapping):
            raise RosterHistoryError(f"override for {person_id} must be a mapping")
        raw_appointments = raw_value.get("appointments") or []
        if not isinstance(raw_appointments, list):
            raise RosterHistoryError(f"appointments for {person_id} must be a list")

        intervals: list[AppointmentInterval] = []
        for item in raw_appointments:
            if not isinstance(item, Mapping):
                raise RosterHistoryError(f"appointment override for {person_id} must be a mapping")
            role_group = roster.clean_text(item.get("role_group"))
            if role_group not in roles.ROLE_GROUPS:
                raise RosterHistoryError(f"unknown role_group for {person_id}: {role_group}")
            source = roster.clean_text(item.get("source")) or "manual"
            confidence = roster.clean_text(item.get("confidence")) or ("exact" if source == "manual" else "year")
            end_value = item.get("end_date")
            intervals.append(
                AppointmentInterval(
                    start_date=parse_date(item.get("start_date"), f"{person_id}.start_date"),
                    end_date=None if end_value in (None, "", "null") else parse_date(end_value, f"{person_id}.end_date"),
                    role_group=role_group,
                    position=roster.clean_text(item.get("position")),
                    source=source,
                    confidence=confidence,
                )
            )
        overrides[str(person_id)] = AppointmentOverride(
            display_name=roster.clean_text(raw_value.get("display_name")) or None,
            appointments=intervals,
        )
    return overrides


def add_current_roster_context(
    people: dict[str, PersonSummary],
    appointments: dict[str, list[AppointmentInterval]],
    notices: list[HistoryNotice],
    current_roster: roster.RosterResult,
    initial_start_date: date,
    as_of_date: date,
) -> None:
    current_year_start = date(academic_year_start_year(as_of_date), 8, 1)
    fallback_start = max(initial_start_date, current_year_start)
    for record in current_roster.records.values():
        people[record.person_id] = PersonSummary(record.person_id, record.display_name)
        active = (
            record.published
            and record.directory_key != "unpublished"
            and record.role.role_group in roles.ROLE_GROUPS
        )
        has_open_interval = any(interval.end_date is None for interval in appointments.get(record.person_id, []))
        if active and not appointments.get(record.person_id):
            appointments.setdefault(record.person_id, []).append(
                AppointmentInterval(
                    start_date=fallback_start,
                    end_date=None,
                    role_group=record.role.role_group,
                    position=record.position,
                    source="current-roster",
                    confidence="current-only",
                    start_path=roster.format_path(record.current_file),
                )
            )
            notices.append(
                HistoryNotice(
                    person_id=record.person_id,
                    notice_type="current_roster_without_history",
                    message="current active record had no parseable git-history interval; using current academic-year fallback",
                    path=roster.format_path(record.current_file),
                )
            )
        elif active and not has_open_interval:
            appointments.setdefault(record.person_id, []).append(
                AppointmentInterval(
                    start_date=fallback_start,
                    end_date=None,
                    role_group=record.role.role_group,
                    position=record.position,
                    source="current-roster",
                    confidence="current-only",
                    start_path=roster.format_path(record.current_file),
                )
            )
            notices.append(
                HistoryNotice(
                    person_id=record.person_id,
                    notice_type="current_roster_reopened_history",
                    message="current active record did not have an open inferred interval; using current academic-year fallback",
                    path=roster.format_path(record.current_file),
                )
            )

    for notice in current_roster.notices():
        notices.append(
            HistoryNotice(
                person_id=notice.person_id,
                notice_type=f"current_{notice.notice_type}",
                message=notice.message,
                path=roster.format_path(notice.file),
            )
        )


def apply_overrides(
    people: dict[str, PersonSummary],
    appointments: dict[str, list[AppointmentInterval]],
    notices: list[HistoryNotice],
    overrides: Mapping[str, AppointmentOverride],
) -> None:
    for person_id, override in overrides.items():
        if override.display_name:
            people[person_id] = PersonSummary(person_id, override.display_name)
        elif person_id not in people:
            people[person_id] = PersonSummary(person_id, person_id)
        if override.appointments:
            appointments[person_id] = [copy_interval(interval) for interval in override.appointments]
            notices.append(
                HistoryNotice(
                    person_id=person_id,
                    notice_type="manual_override_applied",
                    message="manual appointment overrides replaced inferred intervals",
                )
            )
        elif override.display_name:
            notices.append(
                HistoryNotice(
                    person_id=person_id,
                    notice_type="manual_display_name_override_applied",
                    message="manual display-name override preserved inferred intervals",
                )
            )


def copy_interval(interval: AppointmentInterval) -> AppointmentInterval:
    return AppointmentInterval(
        start_date=interval.start_date,
        end_date=interval.end_date,
        role_group=interval.role_group,
        position=interval.position,
        source=interval.source,
        confidence=interval.confidence,
        start_commit=interval.start_commit,
        end_commit=interval.end_commit,
        start_path=interval.start_path,
        end_path=interval.end_path,
    )


def academic_year_start_year(value: date) -> int:
    return value.year if value.month >= 8 else value.year - 1


def academic_year_windows(initial_start_date: date, as_of_date: date) -> list[tuple[str, date, date]]:
    first_year = academic_year_start_year(initial_start_date)
    last_year = academic_year_start_year(as_of_date)
    windows: list[tuple[str, date, date]] = []
    for year in range(first_year, last_year + 1):
        windows.append((f"{year}-{year + 1}", date(year, 8, 1), date(year + 1, 7, 31)))
    return windows


def intervals_overlap(start_a: date, end_a: date, start_b: date, end_b: date) -> bool:
    return start_a <= end_b and start_b <= end_a


def expand_active_years(
    people: Mapping[str, PersonSummary],
    appointments: Mapping[str, list[AppointmentInterval]],
    initial_start_date: date,
    as_of_date: date,
    current_active_ids: set[str] | None = None,
) -> list[ActiveYearRow]:
    rows_by_key: dict[tuple[str, str, str], ActiveYearRow] = {}
    if current_active_ids is None:
        current_active_ids = {
            person_id
            for person_id, intervals in appointments.items()
            if any(interval.end_date is None for interval in intervals)
        }

    for person_id, intervals in appointments.items():
        display_name = people.get(person_id, PersonSummary(person_id, person_id)).display_name
        for interval in intervals:
            if interval.role_group not in roles.ROLE_GROUPS:
                continue
            interval_start = max(interval.start_date, initial_start_date)
            interval_end = interval.end_date or date(9999, 12, 31)
            if interval_end < initial_start_date:
                continue
            for academic_year, window_start, window_end in academic_year_windows(initial_start_date, as_of_date):
                if not intervals_overlap(interval_start, interval_end, window_start, window_end):
                    continue
                row_start = max(interval_start, window_start)
                row_end = min(interval_end, window_end)
                row = ActiveYearRow(
                    person_id=person_id,
                    display_name=display_name,
                    academic_year=academic_year,
                    start_date=row_start,
                    end_date=row_end,
                    role_group=interval.role_group,
                    position=interval.position,
                    source=interval.source,
                    confidence=interval.confidence,
                    current_active=person_id in current_active_ids,
                )
                key = (person_id, academic_year, interval.role_group)
                existing = rows_by_key.get(key)
                if existing is None or row_sort_key(row) > row_sort_key(existing):
                    rows_by_key[key] = row

    return sorted(
        rows_by_key.values(),
        key=lambda row: (row.academic_year, role_order(row.role_group), row.display_name.casefold(), row.person_id),
    )


def role_order(role_group: str) -> int:
    try:
        return ROLE_GROUPS.index(role_group)
    except ValueError:
        return len(ROLE_GROUPS)


def row_sort_key(row: ActiveYearRow) -> tuple[int, date, str]:
    source_priority = {"manual": 3, "git-history": 2, "current-roster": 1}.get(row.source, 0)
    return source_priority, row.start_date, row.position


def build_history_result(
    events: Iterable[HistoryFileEvent],
    current_roster: roster.RosterResult,
    overrides: Mapping[str, AppointmentOverride],
    initial_start_date: date,
    as_of_date: date,
    extra_notices: Iterable[HistoryNotice] = (),
) -> HistoryResult:
    people, appointments, notices = infer_git_intervals(events)
    notices.extend(extra_notices)
    add_current_roster_context(people, appointments, notices, current_roster, initial_start_date, as_of_date)
    apply_overrides(people, appointments, notices, overrides)

    current_active_ids = {
        person_id
        for person_id, intervals in appointments.items()
        if any(interval.end_date is None for interval in intervals)
    }
    rows = expand_active_years(people, appointments, initial_start_date, as_of_date, current_active_ids)
    return HistoryResult(
        people=people,
        appointments={person_id: sorted(intervals, key=lambda item: item.start_date) for person_id, intervals in appointments.items()},
        rows=rows,
        notices=notices,
        initial_start_date=initial_start_date,
        as_of_date=as_of_date,
        generated_at=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    )


def write_outputs(
    result: HistoryResult,
    cache_json_path: Path,
    csv_path: Path,
    markdown_path: Path,
) -> None:
    cache_json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    cache_json_path.write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in result.rows:
            writer.writerow(row.to_dict())

    markdown_path.write_text(render_markdown_report(result), encoding="utf-8")


def render_markdown_report(result: HistoryResult) -> str:
    counts = result.counts_by_year_role()
    notice_counts = Counter(notice.notice_type for notice in result.notices)
    lines = [
        "# UVA Math arXiv Active People By Academic Year",
        "",
        f"Generated: {result.generated_at}",
        f"Initial arXiv start date: {format_date(result.initial_start_date)}",
        f"As-of date: {format_date(result.as_of_date)}",
        f"Rows: {len(result.rows)}",
        "",
        "## Counts by Academic Year and Role",
        "",
        "| Academic year | faculty | postdoc | grad | agfm_other | emeritus |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for academic_year in sorted(counts):
        year_counts = counts[academic_year]
        lines.append(
            "| "
            + " | ".join(
                [
                    academic_year,
                    str(year_counts.get("faculty", 0)),
                    str(year_counts.get("postdoc", 0)),
                    str(year_counts.get("grad", 0)),
                    str(year_counts.get("agfm_other", 0)),
                    str(year_counts.get("emeritus", 0)),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Uncertainty and Conflict Notices", ""])
    if not notice_counts:
        lines.append("No uncertainty or conflict notices.")
    else:
        lines.extend(["| Notice type | Count |", "|---|---:|"])
        for notice_type, count in sorted(notice_counts.items()):
            lines.append(f"| {notice_type} | {count} |")
        lines.extend(["", "## Notice Details", ""])
        for notice in result.notices[:200]:
            detail = f"- {notice.notice_type}: {notice.person_id}: {notice.message}"
            if notice.path:
                detail += f" ({notice.path})"
            if notice.date:
                detail += f" [{notice.date.isoformat()}]"
            lines.append(detail)
        if len(result.notices) > 200:
            lines.append(f"- Additional notices omitted: {len(result.notices) - 200}")

    lines.append("")
    return "\n".join(lines)


def print_report(result: HistoryResult, dry_run: bool, out: TextIO = sys.stdout) -> None:
    counts = result.counts_by_year_role()
    notice_counts = Counter(notice.notice_type for notice in result.notices)
    print(f"dry_run: {'true' if dry_run else 'false'}", file=out)
    print("paper_scan: skipped", file=out)
    print(f"people_with_appointments: {len(result.appointments)}", file=out)
    print(f"active_people_by_year_rows: {len(result.rows)}", file=out)
    print("yearly_counts:", file=out)
    for academic_year in sorted(counts):
        year_counts = counts[academic_year]
        role_bits = " ".join(f"{role_group}={year_counts.get(role_group, 0)}" for role_group in ROLE_GROUPS)
        print(f"  {academic_year}: {role_bits}", file=out)
    print("notice_counts:", file=out)
    if notice_counts:
        for notice_type, count in sorted(notice_counts.items()):
            print(f"  {notice_type}: {count}", file=out)
    else:
        print("  none", file=out)


def build_from_repo(
    config: env.UvaArxivConfig,
    as_of_date: date,
) -> HistoryResult:
    current = roster.load_current_roster(config)
    overrides = load_appointment_overrides(config.data_dir / "appointments_overrides.yml")
    events, history_notices = git_history_events(config.repo_root)
    initial_start_date = parse_date(config.initial_arxiv_start_date, "initial_arxiv_start_date")
    return build_history_result(
        events=events,
        current_roster=current,
        overrides=overrides,
        initial_start_date=initial_start_date,
        as_of_date=as_of_date,
        extra_notices=history_notices,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build UVA Math appointment history support roster.")
    parser.add_argument("--dry-run", action="store_true", help="Print the history summary; no paper scan is performed.")
    parser.add_argument("--no-env", action="store_true", help="Do not load ignored .env values.")
    parser.add_argument("--no-write", action="store_true", help="Do not write JSON/CSV/Markdown support outputs.")
    parser.add_argument("--as-of", help="As-of date for current academic-year expansion, YYYY-MM-DD.")
    args = parser.parse_args()

    config = env.load_config(load_env_file=not args.no_env, ensure_dirs=True)
    as_of_date = parse_date(args.as_of, "as-of date") if args.as_of else date.today()
    result = build_from_repo(config, as_of_date)

    if not args.dry_run and not args.no_write:
        write_outputs(
            result,
            config.cache_dir / "active_people_by_year.json",
            config.repo_root / "reports" / "uva-arxiv-active-people-by-year.csv",
            config.repo_root / "reports" / "uva-arxiv-active-people-by-year.md",
        )
    print_report(result, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

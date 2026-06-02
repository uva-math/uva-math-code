"""Current UVA Math people roster parser."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, TextIO

try:
    from . import env, roles
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.uva_arxiv import env, roles


ACTIVE_DIRECTORY_KEYS = {"faculty", "postdoc", "grad", "lecturer"}


class RosterError(RuntimeError):
    """Raised when a people file cannot be parsed into a stable person record."""


@dataclass(frozen=True)
class RosterNotice:
    person_id: str
    notice_type: str
    message: str
    file: Path

    def to_dict(self, repo_root: Path = env.REPO_ROOT) -> dict[str, str]:
        return {
            "person_id": self.person_id,
            "type": self.notice_type,
            "message": self.message,
            "file": format_path(self.file, repo_root),
        }


@dataclass(frozen=True)
class PersonRecord:
    person_id: str
    uva_id: str
    display_name: str
    first: str
    last: str
    general_position: str
    position: str
    email: str
    personal_page: str
    research_tags: list[str]
    specialty: str
    published: bool
    current_file: Path
    directory_key: str
    role: roles.RoleClassification
    aliases: list[str]
    normalized_aliases: list[str]
    raw_front_matter: dict[str, Any] = field(repr=False)

    def to_dict(self, repo_root: Path = env.REPO_ROOT) -> dict[str, Any]:
        record = {
            "person_id": self.person_id,
            "uva_id": self.uva_id,
            "display_name": self.display_name,
            "first": self.first,
            "last": self.last,
            "general_position": self.general_position,
            "position": self.position,
            "email": self.email,
            "personal_page": self.personal_page,
            "research_tags": self.research_tags,
            "specialty": self.specialty,
            "published": self.published,
            "current_file": format_path(self.current_file, repo_root),
            "directory_key": self.directory_key,
            "aliases": self.aliases,
            "normalized_aliases": self.normalized_aliases,
        }
        record.update(self.role.to_dict())
        return record


@dataclass(frozen=True)
class RosterResult:
    records: dict[str, PersonRecord]
    conflicts: list[RosterNotice]
    unpublished: list[RosterNotice]
    active_directory_special_cases: list[RosterNotice]
    duplicates: list[RosterNotice]
    parse_errors: list[RosterNotice]

    def notices(self) -> list[RosterNotice]:
        return [
            *self.conflicts,
            *self.unpublished,
            *self.active_directory_special_cases,
            *self.duplicates,
            *self.parse_errors,
        ]


def format_path(path: Path, repo_root: Path = env.REPO_ROOT) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def as_string_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [clean_text(item) for item in value if clean_text(item)]
    return [clean_text(value)]


def parse_bool(value: Any, default: bool = True) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() not in {"false", "no", "0", "off"}


def extract_front_matter_text(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise RosterError("missing YAML front matter opening marker")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:index])
    raise RosterError("missing YAML front matter closing marker")


def parse_front_matter(text: str) -> dict[str, Any]:
    try:
        return env.load_yaml_mapping_text(text, "people front matter")
    except env.ConfigError as exc:
        raise RosterError(str(exc)) from exc


def display_name_from_front_matter(front_matter: Mapping[str, Any]) -> tuple[str, str, str]:
    first = clean_text(front_matter.get("name") or front_matter.get("first") or front_matter.get("firstname"))
    last = clean_text(front_matter.get("lastname") or front_matter.get("last"))
    display_name = clean_text(front_matter.get("display_name") or front_matter.get("title"))
    if not display_name:
        display_name = " ".join(part for part in (first, last) if part).strip()
    return display_name, first, last


def _strip_latex_name_markup(value: str) -> str:
    """Convert common TeX accent/name markup to plain text before matching."""
    text = value
    # TeX accent commands can be braced or unbraced: F\"oldes, F\"{o}ldes, F{\"o}ldes.
    accent_commands = r"[`'\"^~=.]"
    text = re.sub(rf"\\({accent_commands})\s*\{{\s*([A-Za-z])\s*\}}", r"\2", text)
    text = re.sub(rf"\\({accent_commands})\s*([A-Za-z])", r"\2", text)
    text = re.sub(r"\\([Hcuvrktbd])\s*\{\s*([A-Za-z])\s*\}", r"\2", text)
    text = re.sub(r"\\([Hcuvrktbd])\s*([A-Za-z])", r"\2", text)

    # Common TeX letter commands appearing in names.
    for command, replacement in {
        "ae": "ae",
        "AE": "AE",
        "oe": "oe",
        "OE": "OE",
        "aa": "a",
        "AA": "A",
        "o": "o",
        "O": "O",
        "l": "l",
        "L": "L",
        "ss": "ss",
    }.items():
        text = re.sub(rf"\\{command}\b", replacement, text)

    # Remove grouping braces left after accent replacement, so F{\"o}ldes -> Foldes.
    return text.replace("{", "").replace("}", "")


def normalize_name(value: str) -> str:
    plain_value = _strip_latex_name_markup(value)
    decomposed = unicodedata.normalize("NFKD", plain_value)
    ascii_value = "".join(char for char in decomposed if not unicodedata.combining(char))
    lowered = ascii_value.casefold()
    normalized = re.sub(r"[^a-z0-9]+", " ", lowered)
    return re.sub(r"\s+", " ", normalized).strip()


def build_aliases(display_name: str, first: str, last: str) -> tuple[list[str], list[str]]:
    aliases: list[str] = []
    for alias in (
        display_name,
        " ".join(part for part in (first, last) if part).strip(),
        f"{first[:1]}. {last}".strip() if first and last else "",
        f"{last}, {first}".strip(", ") if first and last else "",
    ):
        if alias and alias not in aliases:
            aliases.append(alias)

    normalized_aliases = sorted({normalize_name(alias) for alias in aliases if normalize_name(alias)})
    return aliases, normalized_aliases


def parse_person_file(path: Path, directory_key: str, repo_root: Path = env.REPO_ROOT) -> PersonRecord:
    front_matter = parse_front_matter(extract_front_matter_text(path))
    uva_id = clean_text(front_matter.get("UVA_id") or front_matter.get("uva_id"))
    if not uva_id:
        raise RosterError("missing UVA_id")

    display_name, first, last = display_name_from_front_matter(front_matter)
    classification = roles.classify_role(front_matter, directory_key)
    aliases, normalized_aliases = build_aliases(display_name, first, last)

    return PersonRecord(
        person_id=uva_id,
        uva_id=uva_id,
        display_name=display_name,
        first=first,
        last=last,
        general_position=clean_text(front_matter.get("general_position")),
        position=clean_text(front_matter.get("position")),
        email=clean_text(front_matter.get("email")),
        personal_page=clean_text(front_matter.get("personal_page")),
        research_tags=as_string_list(front_matter.get("research_tags")),
        specialty=clean_text(front_matter.get("specialty")),
        published=parse_bool(front_matter.get("published"), default=True),
        current_file=path,
        directory_key=directory_key,
        role=classification,
        aliases=aliases,
        normalized_aliases=normalized_aliases,
        raw_front_matter=front_matter,
    )


def load_current_roster(
    config: env.UvaArxivConfig | None = None,
    people_dirs: Mapping[str, Path] | None = None,
    repo_root: Path | None = None,
) -> RosterResult:
    if config is None and people_dirs is None:
        config = env.load_config()
    if config is not None:
        people_dirs = config.people_dirs
        repo_root = config.repo_root
    if people_dirs is None:
        raise RosterError("people_dirs is required")
    if repo_root is None:
        repo_root = env.REPO_ROOT

    records: dict[str, PersonRecord] = {}
    conflicts: list[RosterNotice] = []
    unpublished: list[RosterNotice] = []
    special_cases: list[RosterNotice] = []
    duplicates: list[RosterNotice] = []
    parse_errors: list[RosterNotice] = []

    for directory_key, directory in people_dirs.items():
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            try:
                record = parse_person_file(path, directory_key, repo_root)
            except RosterError as exc:
                parse_errors.append(
                    RosterNotice(
                        person_id=path.stem,
                        notice_type="parse_error",
                        message=str(exc),
                        file=path,
                    )
                )
                continue

            if record.person_id in records:
                duplicates.append(
                    RosterNotice(
                        person_id=record.person_id,
                        notice_type="duplicate_uva_id",
                        message=f"duplicate UVA_id also found in {format_path(records[record.person_id].current_file, repo_root)}",
                        file=path,
                    )
                )
                continue

            records[record.person_id] = record
            if roles.directory_conflict(record.role, directory_key):
                expected = roles.expected_role_group_for_directory(directory_key)
                conflicts.append(
                    RosterNotice(
                        person_id=record.person_id,
                        notice_type="directory_front_matter_conflict",
                        message=f"directory suggests {expected}; front matter classifies as {record.role.role_group}",
                        file=path,
                    )
                )
            if directory_key == "unpublished" or not record.published:
                unpublished.append(
                    RosterNotice(
                        person_id=record.person_id,
                        notice_type="unpublished_record",
                        message="record is unpublished or stored under _unpublished",
                        file=path,
                    )
                )
            if directory_key in ACTIVE_DIRECTORY_KEYS and record.role.role_group in {"agfm_other", "emeritus"}:
                special_cases.append(
                    RosterNotice(
                        person_id=record.person_id,
                        notice_type="active_directory_special_case",
                        message=f"{record.role.role_group} record appears under active {directory_key} directory",
                        file=path,
                    )
                )

    return RosterResult(
        records=records,
        conflicts=conflicts,
        unpublished=unpublished,
        active_directory_special_cases=special_cases,
        duplicates=duplicates,
        parse_errors=parse_errors,
    )


def print_report(result: RosterResult, out: TextIO = sys.stdout, repo_root: Path = env.REPO_ROOT) -> None:
    counts: dict[str, int] = {role_group: 0 for role_group in roles.ROLE_GROUPS}
    for record in result.records.values():
        counts[record.role.role_group] = counts.get(record.role.role_group, 0) + 1

    print(f"records: {len(result.records)}", file=out)
    for role_group in roles.ROLE_GROUPS:
        print(f"role_{role_group}: {counts.get(role_group, 0)}", file=out)
    print(f"conflicts: {len(result.conflicts)}", file=out)
    print(f"unpublished_records: {len(result.unpublished)}", file=out)
    print(f"active_directory_special_cases: {len(result.active_directory_special_cases)}", file=out)
    print(f"duplicates: {len(result.duplicates)}", file=out)
    print(f"parse_errors: {len(result.parse_errors)}", file=out)

    for notice in result.notices():
        print(
            f"{notice.notice_type}: {notice.person_id}: {notice.message}: {format_path(notice.file, repo_root)}",
            file=out,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse current UVA Math people roster.")
    parser.add_argument("--no-env", action="store_true", help="Do not load ignored .env values.")
    args = parser.parse_args()

    config = env.load_config(load_env_file=not args.no_env)
    result = load_current_roster(config)
    print_report(result, repo_root=config.repo_root)
    return 1 if result.parse_errors or result.duplicates else 0


if __name__ == "__main__":
    raise SystemExit(main())

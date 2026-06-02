"""Role/rank group classifier for UVA Math people records."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping


ROLE_GROUPS = ("faculty", "postdoc", "grad", "agfm_other", "emeritus")

GENERAL_POSITION_ROLE_MAP = {
    "faculty": "faculty",
    "postdoc": "postdoc",
    "gradstudent": "grad",
    "grad": "grad",
    "graduate student": "grad",
    "lecturer": "agfm_other",
    "emeritus": "emeritus",
    "emerita": "emeritus",
}

DIRECTORY_ROLE_HINTS = {
    "faculty": "faculty",
    "postdoc": "postdoc",
    "postdocs": "postdoc",
    "grad": "grad",
    "gradstudents": "grad",
    "lecturer": "agfm_other",
    "lecturers": "agfm_other",
    "emeriti": "emeritus",
    "emeritus": "emeritus",
}

AGFM_POSITION_RE = re.compile(
    r"\b(General Faculty|Lecturer|Instructor|Academic General Faculty)\b",
    re.IGNORECASE,
)
EMERITUS_POSITION_RE = re.compile(r"\b(Emeritus|Emerita)\b", re.IGNORECASE)


@dataclass(frozen=True)
class RoleClassification:
    role_group: str
    rank_label: str
    position_raw: str
    general_position: str
    source: str

    def to_dict(self) -> dict[str, str]:
        return {
            "role_group": self.role_group,
            "rank_label": self.rank_label,
            "position_raw": self.position_raw,
            "general_position": self.general_position,
            "role_source": self.source,
        }


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_general_position(value: Any) -> str:
    return clean_text(value).lower().replace("_", " ").replace("-", " ")


def expected_role_group_for_directory(directory_key: str | None) -> str | None:
    if not directory_key:
        return None
    key = directory_key.strip().lower().replace("_", "").replace("-", "")
    return DIRECTORY_ROLE_HINTS.get(key)


def classify_role(
    front_matter: Mapping[str, Any],
    directory_key: str | None = None,
) -> RoleClassification:
    """Classify a person record using front matter first and directory as fallback."""
    general_position_raw = clean_text(front_matter.get("general_position"))
    general_position = normalize_general_position(general_position_raw)
    position_raw = clean_text(front_matter.get("position"))

    if EMERITUS_POSITION_RE.search(position_raw) or general_position in {"emeritus", "emerita"}:
        role_group = "emeritus"
        source = "front-matter"
    elif general_position in {"postdoc", "gradstudent", "grad", "graduate student"}:
        role_group = GENERAL_POSITION_ROLE_MAP[general_position]
        source = "front-matter"
    elif AGFM_POSITION_RE.search(position_raw) or general_position == "lecturer":
        role_group = "agfm_other"
        source = "front-matter"
    elif general_position in GENERAL_POSITION_ROLE_MAP:
        role_group = GENERAL_POSITION_ROLE_MAP[general_position]
        source = "front-matter"
    else:
        directory_role = expected_role_group_for_directory(directory_key)
        role_group = directory_role or "agfm_other"
        source = "directory-fallback" if directory_role else "fallback"

    return RoleClassification(
        role_group=role_group,
        rank_label=rank_label(position_raw, role_group),
        position_raw=position_raw,
        general_position=general_position_raw,
        source=source,
    )


def rank_label(position_raw: str, role_group: str) -> str:
    position = position_raw.strip()
    if not position:
        return role_group
    if role_group == "faculty":
        if re.search(r"\bAssistant Professor\b", position, re.IGNORECASE):
            return "Assistant Professor"
        if re.search(r"\bAssociate Professor\b", position, re.IGNORECASE):
            return "Associate Professor"
        if re.search(r"\bProfessor\b", position, re.IGNORECASE):
            return "Professor"
    if role_group == "emeritus":
        if re.search(r"\bProfessor Emerita\b", position, re.IGNORECASE):
            return "Professor Emerita"
        if re.search(r"\bProfessor Emeritus\b", position, re.IGNORECASE):
            return "Professor Emeritus"
        return "Emeritus"
    if role_group == "agfm_other":
        if re.search(r"\bGeneral Faculty\b", position, re.IGNORECASE):
            return "General Faculty"
        if re.search(r"\bLecturer\b", position, re.IGNORECASE):
            return "Lecturer"
        if re.search(r"\bInstructor\b", position, re.IGNORECASE):
            return "Instructor"
    return position


def directory_conflict(
    classification: RoleClassification,
    directory_key: str | None,
) -> bool:
    expected = expected_role_group_for_directory(directory_key)
    if expected is None:
        return False
    if directory_key == "faculty" and classification.role_group in {"agfm_other", "emeritus"}:
        return False
    return expected != classification.role_group

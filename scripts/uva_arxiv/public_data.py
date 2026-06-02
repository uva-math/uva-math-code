"""Generate public-preview JSON data for the UVA arXiv page.

This consumes internal review outputs and writes public-safe assets. It never
includes local source paths, source snippets, or cache paths.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sqlite3
import sys
import unicodedata
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any, Iterable

try:
    from . import arxiv_db, env, sources
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.uva_arxiv import arxiv_db, env, sources


DEFAULT_CONFIRMED_CSV = Path("reports/uva-arxiv-tt-confirmed-matches.csv")
DEFAULT_JOURNAL_CSV = Path("reports/uva-arxiv-tt-journal-metadata.csv")
DEFAULT_JSON = Path("assets/data/uva-arxiv-papers.json")
ROLE_LABELS = {
    "faculty": "Tenured/tenure-track faculty",
    "postdoc": "Postdocs",
    "grad": "Graduate students",
    "agfm_other": "Academic general faculty / lecturers",
    "emeritus": "Emeriti",
}


class PublicDataError(RuntimeError):
    """Raised when public preview data cannot be generated."""


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise PublicDataError(f"required CSV does not exist: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _split_authors(authors: str) -> list[str]:
    text = " ".join((authors or "").split())
    text = re.sub(r"\s+and\s+", ",", text, flags=re.IGNORECASE)
    text = text.replace(";", ",")
    return [part.strip() for part in text.split(",") if part.strip()]


def _load_abstracts(config: env.UvaArxivConfig, arxiv_ids: Iterable[str]) -> dict[str, str]:
    ids = list(dict.fromkeys(arxiv_ids))
    if not ids:
        return {}
    abstracts: dict[str, str] = {}
    with arxiv_db.connect_readonly(config.arxiv_db) as conn:
        for index in range(0, len(ids), 500):
            batch = ids[index : index + 500]
            placeholders = ",".join("?" for _ in batch)
            rows = conn.execute(
                f"SELECT id, abstract FROM papers WHERE id IN ({placeholders})",
                batch,
            ).fetchall()
            for row in rows:
                abstracts[str(row["id"])] = " ".join(str(row["abstract"] or "").split())
    return abstracts


def _journal_by_id(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    return {sources.normalize_arxiv_id(row["arxiv_id"]): row for row in _read_csv(path)}


LOCAL_JOURNAL_NAME_OVERRIDES = {
    "analysis & pde": ("Anal. PDE", "Analysis & PDE"),
    "ann. pure appl. log.": ("Ann. Pure Appl. Logic", "Annals of Pure and Applied Logic"),
    "annals of k-theory": ("Ann. K-Theory", "Annals of K-Theory"),
    "annals of representation theory": ("Ann. Represent. Theory", "Annals of Representation Theory"),
    "annals of the academy of romanian scientists series on mathematics and its application": (
        "Ann. Acad. Rom. Sci.",
        "Annals of the Academy of Romanian Scientists Series on Mathematics and Its Application",
    ),
    "archiv der mathematik": ("Arch. Math.", "Archiv der Mathematik"),
    "bulletin of the australian mathematical society": ("Bull. Aust. Math. Soc.", "Bulletin of the Australian Mathematical Society"),
    "homology, homotopy and applications": ("Homology Homotopy Appl.", "Homology, Homotopy and Applications"),
    "journal of combinatorial theory, series a": ("JCTA", "Journal of Combinatorial Theory, Series A"),
    "journal of noncommutative geometry": ("J. Noncommut. Geom.", "Journal of Noncommutative Geometry"),
    "michigan mathematical journal": ("Michigan Math. J.", "Michigan Mathematical Journal"),
    "proceedings of the american mathematical society, series b": (
        "Proc. AMS Ser. B",
        "Proceedings of the American Mathematical Society, Series B",
    ),
    "proceedings of the edinburgh mathematical society": (
        "Proc. Edinb. Math. Soc.",
        "Proceedings of the Edinburgh Mathematical Society",
    ),
    "proc. am. math. soc.": ("Proc. AMS", "Proceedings of the American Mathematical Society"),
    "proc. sympos. pure math.": ("Proc. Sympos. Pure Math.", "Proceedings of Symposia in Pure Mathematics"),
    "publicacions matemàtiques": ("Publ. Mat.", "Publicacions Matemàtiques"),
    "research in number theory": ("Res. Number Theory", "Research in Number Theory"),
    "research in the mathematical sciences": ("Res. Math. Sci.", "Research in the Mathematical Sciences"),
    "topology and its applications": ("Topology Appl.", "Topology and its Applications"),
}

LOCAL_JOURNAL_NAME_PATTERNS = [
    (re.compile(r"^proc\.?\s+int\.?\s+cong\.?\s+math", re.IGNORECASE), "Proc. ICM", "Proceedings of the International Congress of Mathematicians"),
]


def _load_journal_normalizer(config: env.UvaArxivConfig) -> Callable[[str], tuple[str, str]]:
    scripts_dir = str(config.homepage_arxiv_scripts)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        from journal_names import normalize_journal_name as homepage_normalize_journal_name  # type: ignore
    except Exception:  # pragma: no cover - robust fallback if Homepage helper moves.
        def homepage_normalize_journal_name(raw_name: str) -> tuple[str, str]:
            name = re.sub(r"\s+", " ", raw_name or "").strip()
            return name, name

    def normalize_journal_name(raw_name: str) -> tuple[str, str]:
        name = re.sub(r"\s+", " ", raw_name or "").strip()
        override = LOCAL_JOURNAL_NAME_OVERRIDES.get(name.casefold())
        if override:
            return override
        for pattern, badge, full in LOCAL_JOURNAL_NAME_PATTERNS:
            if pattern.search(name):
                return badge, full
        return homepage_normalize_journal_name(name)

    return normalize_journal_name


LATEX_ACCENTS = {
    "'": "\u0301",
    "`": "\u0300",
    "^": "\u0302",
    '"': "\u0308",
    "~": "\u0303",
    "=": "\u0304",
    ".": "\u0307",
    "u": "\u0306",
    "v": "\u030c",
    "H": "\u030b",
    "r": "\u030a",
    "c": "\u0327",
    "k": "\u0328",
    "b": "\u0331",
    "d": "\u0323",
}
LATEX_SPECIAL_CHARS = {
    r"\i": "ı",
    r"\j": "ȷ",
    r"\o": "ø",
    r"\O": "Ø",
    r"\l": "ł",
    r"\L": "Ł",
    r"\aa": "å",
    r"\AA": "Å",
    r"\ae": "æ",
    r"\AE": "Æ",
    r"\oe": "œ",
    r"\OE": "Œ",
    r"\ss": "ß",
}
LATEX_ACCENT_RE = re.compile(
    r"\\(?P<accent>['`^\"~=.]|[uvHrckbd])\s*(?:\{(?P<braced>[^{}])\}|(?P<plain>[A-Za-z]))"
)


def _latex_to_unicode(value: str) -> str:
    text = value
    for macro, replacement in sorted(LATEX_SPECIAL_CHARS.items(), key=lambda item: -len(item[0])):
        text = text.replace(macro, replacement)

    def replace_accent(match: re.Match[str]) -> str:
        char = match.group("braced") or match.group("plain") or ""
        mark = LATEX_ACCENTS.get(match.group("accent"), "")
        if not char or not mark:
            return match.group(0)
        return unicodedata.normalize("NFC", char + mark)

    previous = None
    while previous != text:
        previous = text
        text = LATEX_ACCENT_RE.sub(replace_accent, text)
    text = text.replace(r"\'", "'")
    text = re.sub(r"\[{}]", lambda match: match.group(0)[1], text)
    text = text.replace("{", "").replace("}", "")
    return text


def _clean_text(value: Any) -> str:
    return _latex_to_unicode(html.unescape(str(value or "").strip()))


def _year_from_date(value: str) -> str:
    match = re.match(r"^((?:19|20)\d{2})", value or "")
    return match.group(1) if match else ""


def build_public_rows(
    confirmed_csv: Path,
    journal_csv: Path,
    config: env.UvaArxivConfig,
    role_group: str = "faculty",
) -> list[dict[str, Any]]:
    confirmed = _read_csv(confirmed_csv)
    journals = _journal_by_id(journal_csv)
    abstracts = _load_abstracts(config, [row["arxiv_id"] for row in confirmed])
    normalize_journal_name = _load_journal_normalizer(config)

    grouped: dict[str, dict[str, Any]] = {}
    people_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in confirmed:
        arxiv_id = sources.normalize_arxiv_id(row["arxiv_id"])
        people_by_id[arxiv_id].append(
            {
                "id": row["person_id"],
                "name": row["display_name"],
                "role": role_group,
                "role_label": ROLE_LABELS.get(role_group, role_group),
                "decision_source": row.get("decision_source", ""),
            }
        )
        if arxiv_id in grouped:
            continue
        journal = journals.get(arxiv_id, {})
        raw_journal_name = _clean_text(journal.get("journal_name", ""))
        journal_badge, journal_full = normalize_journal_name(raw_journal_name)
        categories = [part for part in row.get("categories", "").split() if part]
        grouped[arxiv_id] = {
            "id": arxiv_id,
            "date": row.get("date", ""),
            "year": _year_from_date(row.get("date", "")),
            "month": row.get("date", "")[:7],
            "title": _clean_text(row.get("title", "")),
            "authors": [_clean_text(author) for author in _split_authors(row.get("authors", ""))],
            "authors_text": _clean_text(row.get("authors", "")),
            "abstract": _clean_text(abstracts.get(arxiv_id, "")),
            "categories": categories,
            "primary_category": categories[0] if categories else "",
            "journal_name": _clean_text(journal_badge),
            "journal_full": _clean_text(journal_full),
            "journal_name_raw": raw_journal_name,
            "journal_ref": _clean_text(journal.get("journal_ref", "")),
            "doi": _clean_text(journal.get("doi", "")),
            "venue": _clean_text(journal.get("venue", "")),
            "publication_year": journal.get("publication_year", "") or "",
            "publication_date": journal.get("publication_date", "") or "",
            "journal_status": journal.get("status", "missing") or "missing",
            "journal_source": journal.get("source", "") or "",
            "decision_sources": sorted({row.get("decision_source", "")}),
            "affiliation_evidence": row.get("affiliation_evidence", ""),
        }

    for arxiv_id, paper in grouped.items():
        paper["people"] = sorted(
            people_by_id[arxiv_id],
            key=lambda person: (person["name"].split()[-1].casefold(), person["name"].casefold()),
        )
        paper["person_ids"] = [person["id"] for person in paper["people"]]
        paper["person_names"] = [person["name"] for person in paper["people"]]
        paper["roles"] = sorted({person["role"] for person in paper["people"]})
        paper["role_labels"] = sorted({person["role_label"] for person in paper["people"]})
        paper["decision_sources"] = sorted({person["decision_source"] for person in paper["people"] if person["decision_source"]})
    return sorted(grouped.values(), key=lambda row: (row["date"], row["id"]), reverse=True)


def write_public_data(
    rows: list[dict[str, Any]],
    json_path: Path,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "description": "UVA Mathematics arXiv tracker preview data generated from internal review decisions.",
        "generated_from": {
            "confirmed_matches": str(DEFAULT_CONFIRMED_CSV),
            "journal_metadata": str(DEFAULT_JOURNAL_CSV),
        },
        "counts": {
            "papers": len(rows),
            "with_journal": sum(1 for row in rows if row.get("journal_name")),
            "with_doi": sum(1 for row in rows if row.get("doi")),
        },
        "papers": rows,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate public-preview UVA arXiv JSON asset.")
    parser.add_argument("--confirmed", type=Path, default=DEFAULT_CONFIRMED_CSV)
    parser.add_argument("--journal", type=Path, default=DEFAULT_JOURNAL_CSV)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--role", default="faculty")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    config = env.load_config(ensure_dirs=True)
    rows = build_public_rows(args.confirmed, args.journal, config, role_group=args.role)
    write_public_data(rows, args.json)
    print(f"wrote: {args.json}")
    print(f"papers: {len(rows)}")
    print(f"with_journal: {sum(1 for row in rows if row.get('journal_name'))}")
    print(f"with_doi: {sum(1 for row in rows if row.get('doi'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

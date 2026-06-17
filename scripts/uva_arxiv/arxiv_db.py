"""Shared arXiv SQLite helpers for the UVA arXiv infrastructure."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import quote


PAPER_COLUMNS = ("id", "title", "abstract", "categories", "authors", "date")


class ArxivDatabaseError(RuntimeError):
    """Raised when the shared arXiv database is missing or incompatible."""


@dataclass(frozen=True)
class SchemaInfo:
    table: str
    columns: tuple[str, ...]
    primary_key: str | None


@dataclass(frozen=True)
class DatabaseStats:
    count: int
    min_date: str | None
    max_date: str | None


@dataclass(frozen=True)
class PaperRecord:
    id: str
    title: str
    abstract: str
    categories: str
    authors: str
    date: str

    def __post_init__(self) -> None:
        values = {
            "id": _as_text(self.id),
            "title": _as_text(self.title),
            "abstract": _as_text(self.abstract),
            "categories": _as_text(self.categories, separator=" "),
            "authors": _as_text(self.authors),
            "date": _as_text(self.date),
        }
        missing = [key for key in ("id", "date") if not values[key]]
        if missing:
            raise ArxivDatabaseError(f"Paper record missing required fields: {', '.join(missing)}")
        for key, value in values.items():
            object.__setattr__(self, key, value)

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "PaperRecord":
        missing = [key for key in ("id", "date") if not _as_text(mapping.get(key))]
        if missing:
            raise ArxivDatabaseError(f"Paper record missing required fields: {', '.join(missing)}")
        return cls(
            id=_as_text(mapping.get("id")),
            title=_as_text(mapping.get("title", "")),
            abstract=_as_text(mapping.get("abstract", "")),
            categories=_as_text(mapping.get("categories", ""), separator=" "),
            authors=_as_text(mapping.get("authors", "")),
            date=_as_text(mapping.get("date")),
        )

    def as_db_params(self) -> dict[str, str]:
        return {
            "id": self.id,
            "title": self.title,
            "abstract": self.abstract,
            "categories": self.categories,
            "authors": self.authors,
            "date": self.date,
        }


def _as_text(value: Any, separator: str = ", ") -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return separator.join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def _sqlite_uri(path: Path, mode: str) -> str:
    resolved = path.expanduser().resolve()
    return f"file:{quote(str(resolved), safe='/:')}?mode={mode}"


def connect_readonly(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path).expanduser()
    if not db_path.exists():
        raise ArxivDatabaseError(f"arXiv database does not exist: {db_path}")
    conn = sqlite3.connect(_sqlite_uri(db_path, "ro"), uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def connect_readwrite(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path).expanduser()
    if not db_path.exists():
        raise ArxivDatabaseError(f"arXiv database does not exist: {db_path}")
    conn = sqlite3.connect(_sqlite_uri(db_path, "rw"), uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def validate_papers_schema(conn: sqlite3.Connection) -> SchemaInfo:
    rows = conn.execute("PRAGMA table_info(papers)").fetchall()
    if not rows:
        raise ArxivDatabaseError("Required table papers is missing")

    columns = tuple(str(row["name"] if isinstance(row, sqlite3.Row) else row[1]) for row in rows)
    missing = [column for column in PAPER_COLUMNS if column not in columns]
    if missing:
        raise ArxivDatabaseError(
            "papers table is missing required columns: " + ", ".join(missing)
        )

    primary_keys = [
        str(row["name"] if isinstance(row, sqlite3.Row) else row[1])
        for row in rows
        if int(row["pk"] if isinstance(row, sqlite3.Row) else row[5]) > 0
    ]
    primary_key = primary_keys[0] if primary_keys else None
    if primary_key != "id":
        raise ArxivDatabaseError("papers.id must be the primary key")

    return SchemaInfo(table="papers", columns=columns, primary_key=primary_key)


def get_db_stats(conn: sqlite3.Connection) -> DatabaseStats:
    row = conn.execute("SELECT COUNT(*) AS count, MIN(date) AS min_date, MAX(date) AS max_date FROM papers").fetchone()
    if row is None:
        return DatabaseStats(count=0, min_date=None, max_date=None)
    if isinstance(row, sqlite3.Row):
        return DatabaseStats(
            count=int(row["count"]),
            min_date=row["min_date"],
            max_date=row["max_date"],
        )
    return DatabaseStats(count=int(row[0]), min_date=row[1], max_date=row[2])


def get_max_date(conn: sqlite3.Connection) -> str | None:
    row = conn.execute("SELECT MAX(date) FROM papers").fetchone()
    if row is None:
        return None
    return row[0]


def upsert_papers(
    conn: sqlite3.Connection,
    papers: Iterable[PaperRecord | Mapping[str, Any]],
    commit: bool = True,
) -> int:
    """Upsert paper records, optionally leaving transaction control to the caller."""
    records = [
        paper if isinstance(paper, PaperRecord) else PaperRecord.from_mapping(paper)
        for paper in papers
    ]
    if not records:
        return 0

    sql = """
        INSERT INTO papers (id, title, abstract, categories, authors, date)
        VALUES (:id, :title, :abstract, :categories, :authors, :date)
        ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            abstract = excluded.abstract,
            categories = excluded.categories,
            authors = excluded.authors,
            date = excluded.date
    """
    params = [record.as_db_params() for record in records]
    if commit:
        with conn:
            conn.executemany(sql, params)
    else:
        conn.executemany(sql, params)
    return len(records)


def delete_papers_by_id(
    conn: sqlite3.Connection,
    paper_ids: Iterable[str],
    commit: bool = True,
) -> int:
    """Delete paper records by arXiv ID, optionally leaving transaction control to the caller."""
    ids = tuple(dict.fromkeys(_as_text(paper_id) for paper_id in paper_ids if _as_text(paper_id)))
    if not ids:
        return 0

    def delete_rows() -> int:
        deleted = 0
        for paper_id in ids:
            cursor = conn.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
            if cursor.rowcount > 0:
                deleted += cursor.rowcount
        return deleted

    if commit:
        with conn:
            return delete_rows()
    return delete_rows()

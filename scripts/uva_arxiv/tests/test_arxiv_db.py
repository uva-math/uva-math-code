from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.uva_arxiv import arxiv_db


def create_papers_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE papers (
                id TEXT PRIMARY KEY,
                title TEXT,
                abstract TEXT,
                categories TEXT,
                authors TEXT,
                date TEXT
            )
            """
        )


class ArxivDatabaseTests(unittest.TestCase):
    def test_validate_stats_and_max_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "arxiv.sqlite"
            create_papers_db(db_path)
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    "INSERT INTO papers VALUES (?, ?, ?, ?, ?, ?)",
                    ("2501.00001", "Old", "Abstract", "math.PR", "A. Author", "2025-01-01"),
                )

            with arxiv_db.connect_readonly(db_path) as conn:
                schema = arxiv_db.validate_papers_schema(conn)
                stats = arxiv_db.get_db_stats(conn)

            self.assertEqual(schema.primary_key, "id")
            self.assertEqual(schema.columns, arxiv_db.PAPER_COLUMNS)
            self.assertEqual(stats.count, 1)
            self.assertEqual(stats.min_date, "2025-01-01")
            self.assertEqual(stats.max_date, "2025-01-01")

    def test_readonly_connection_rejects_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "arxiv.sqlite"
            create_papers_db(db_path)

            with arxiv_db.connect_readonly(db_path) as conn:
                with self.assertRaises(sqlite3.OperationalError):
                    conn.execute(
                        "INSERT INTO papers VALUES (?, ?, ?, ?, ?, ?)",
                        ("2501.00001", "Title", "", "math.PR", "A. Author", "2025-01-01"),
                    )

    def test_upsert_preserves_schema_and_updates_existing_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "arxiv.sqlite"
            create_papers_db(db_path)
            with arxiv_db.connect_readwrite(db_path) as conn:
                count = arxiv_db.upsert_papers(
                    conn,
                    [
                        {
                            "id": "2501.00001",
                            "title": "First",
                            "abstract": "Abstract",
                            "categories": ["math.PR", "math.CO"],
                            "authors": ["A. Author", "B. Author"],
                            "date": "2025-01-01",
                        }
                    ],
                )
                self.assertEqual(count, 1)

                count = arxiv_db.upsert_papers(
                    conn,
                    [
                        {
                            "id": "2501.00001",
                            "title": "Updated",
                            "abstract": "New abstract",
                            "categories": "math.PR",
                            "authors": "A. Author",
                            "date": "2025-01-02",
                        }
                    ],
                )
                self.assertEqual(count, 1)
                row = conn.execute(
                    "SELECT title, abstract, categories, authors, date FROM papers WHERE id = ?",
                    ("2501.00001",),
                ).fetchone()

            self.assertEqual(tuple(row), ("Updated", "New abstract", "math.PR", "A. Author", "2025-01-02"))

    def test_paper_record_validation_applies_to_direct_instances(self) -> None:
        record = arxiv_db.PaperRecord(
            id=" 2501.00001 ",
            title=" Title ",
            abstract=" Abstract ",
            categories=("math.PR", "math.CO"),
            authors=("A. Author", "B. Author"),
            date=" 2025-01-01 ",
        )

        self.assertEqual(record.id, "2501.00001")
        self.assertEqual(record.title, "Title")
        self.assertEqual(record.categories, "math.PR math.CO")
        self.assertEqual(record.authors, "A. Author, B. Author")
        self.assertEqual(record.date, "2025-01-01")
        with self.assertRaises(arxiv_db.ArxivDatabaseError):
            arxiv_db.PaperRecord(
                id="",
                title="Title",
                abstract="Abstract",
                categories="math.PR",
                authors="A. Author",
                date="2025-01-01",
            )
        with self.assertRaises(arxiv_db.ArxivDatabaseError):
            arxiv_db.PaperRecord(
                id="2501.00001",
                title="Title",
                abstract="Abstract",
                categories="math.PR",
                authors="A. Author",
                date="",
            )

    def test_mapping_records_reject_none_required_fields(self) -> None:
        with self.assertRaises(arxiv_db.ArxivDatabaseError):
            arxiv_db.PaperRecord.from_mapping(
                {
                    "id": None,
                    "title": "Title",
                    "abstract": "Abstract",
                    "categories": "math.PR",
                    "authors": "A. Author",
                    "date": "2025-01-01",
                }
            )

    def test_schema_validation_rejects_missing_required_column(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "bad.sqlite"
            with sqlite3.connect(db_path) as conn:
                conn.execute("CREATE TABLE papers (id TEXT PRIMARY KEY, title TEXT)")
                with self.assertRaises(arxiv_db.ArxivDatabaseError):
                    arxiv_db.validate_papers_schema(conn)


if __name__ == "__main__":
    unittest.main()

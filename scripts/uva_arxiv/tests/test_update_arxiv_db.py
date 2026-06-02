from __future__ import annotations

import datetime as dt
import io
import os
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from scripts.uva_arxiv import arxiv_db, check_env, env, update_arxiv_db


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


class SinceUpdaterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = env.load_config(load_env_file=False)

    def test_dry_run_uses_default_overlap_without_fetching_or_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "arxiv.sqlite"
            create_papers_db(db_path)
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    "INSERT INTO papers VALUES (?, ?, ?, ?, ?, ?)",
                    ("2605.00001", "Existing", "Abstract", "math.PR", "A. Author", "2026-05-29"),
                )

            called = False

            def fetcher(since: dt.date, limit: int | None) -> list[arxiv_db.PaperRecord]:
                nonlocal called
                called = True
                return []

            out = io.StringIO()
            result = update_arxiv_db.run_since_update(
                config=self.config,
                db_path=db_path,
                dry_run=True,
                fetcher=fetcher,
                out=out,
            )

            self.assertFalse(called)
            self.assertEqual(result.since, dt.date(2026, 5, 22))
            self.assertIn("dry_run: true", out.getvalue())
            with sqlite3.connect(db_path) as conn:
                count = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
            self.assertEqual(count, 1)

    def test_since_update_upserts_mocked_records_without_adding_indexes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "arxiv.sqlite"
            create_papers_db(db_path)
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    "INSERT INTO papers VALUES (?, ?, ?, ?, ?, ?)",
                    ("2605.00001", "Existing", "Abstract", "math.PR", "A. Author", "2026-05-29"),
                )

            def fetcher(since: dt.date, limit: int | None) -> list[arxiv_db.PaperRecord]:
                self.assertEqual(since, dt.date(2026, 5, 29))
                self.assertEqual(limit, 2)
                return [
                    arxiv_db.PaperRecord(
                        id="2605.00001",
                        title="Updated",
                        abstract="Updated abstract",
                        categories="math.PR",
                        authors="A. Author",
                        date="2026-05-29",
                    ),
                    arxiv_db.PaperRecord(
                        id="2605.00002",
                        title="New",
                        abstract="New abstract",
                        categories="math.CO",
                        authors="B. Author",
                        date="2026-05-30",
                    ),
                ]

            result = update_arxiv_db.run_since_update(
                config=self.config,
                db_path=db_path,
                since=dt.date(2026, 5, 29),
                limit=2,
                fetcher=fetcher,
                out=io.StringIO(),
            )

            self.assertEqual(result.fetched, 2)
            self.assertEqual(result.upserted, 2)
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute("SELECT id, title FROM papers ORDER BY id").fetchall()
                indexes = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'index' AND sql IS NOT NULL"
                ).fetchall()
            self.assertEqual(rows, [("2605.00001", "Updated"), ("2605.00002", "New")])
            self.assertEqual(indexes, [])

    def test_oai_fetch_parses_records_and_collects_deleted_records(self) -> None:
        payload = b"""<?xml version="1.0" encoding="UTF-8"?>
        <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
          <ListRecords>
            <record>
              <header><identifier>oai:arXiv.org:2605.00001</identifier></header>
              <metadata>
                <arXiv xmlns="http://arxiv.org/OAI/arXiv/">
                  <id>2605.00001</id>
                  <created>2026-05-30</created>
                  <authors>
                    <author><keyname>Smith</keyname><forenames>Alice</forenames></author>
                    <author><keyname>Jones</keyname><forenames>Bob</forenames></author>
                  </authors>
                  <title> A title
                  with whitespace </title>
                  <categories>math.PR math.CO</categories>
                  <abstract> An abstract. </abstract>
                </arXiv>
              </metadata>
            </record>
            <record>
              <header status="deleted"><identifier>oai:arXiv.org:2605.00002</identifier></header>
            </record>
          </ListRecords>
        </OAI-PMH>"""
        calls: list[str] = []

        def fake_get(url: str) -> bytes:
            calls.append(url)
            return payload

        deleted_records: list[update_arxiv_db.DeletedOaiRecord] = []
        records = list(
            update_arxiv_db.fetch_oai_records(
                dt.date(2026, 5, 29),
                http_get=fake_get,
                deleted_records=deleted_records,
            )
        )

        self.assertIn("from=2026-05-29", calls[0])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].id, "2605.00001")
        self.assertEqual(records[0].title, "A title with whitespace")
        self.assertEqual(records[0].authors, "Alice Smith, Bob Jones")
        self.assertEqual(records[0].date, "2026-05-30")
        self.assertEqual(deleted_records[0].id, "2605.00002")
        self.assertEqual(deleted_records[0].identifier, "oai:arXiv.org:2605.00002")

    def test_since_update_records_deleted_oai_records_in_sidecar_cache(self) -> None:
        payload = b"""<?xml version="1.0" encoding="UTF-8"?>
        <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
          <ListRecords>
            <record>
              <header status="deleted">
                <identifier>oai:arXiv.org:2605.00002</identifier>
                <datestamp>2026-05-31</datestamp>
              </header>
            </record>
          </ListRecords>
        </OAI-PMH>"""

        def fake_get(_url: str) -> bytes:
            return payload

        original_get = update_arxiv_db.default_http_get
        try:
            update_arxiv_db.default_http_get = fake_get
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                db_path = root / "arxiv.sqlite"
                cache_dir = root / "cache"
                create_papers_db(db_path)
                with sqlite3.connect(db_path) as conn:
                    conn.execute(
                        "INSERT INTO papers VALUES (?, ?, ?, ?, ?, ?)",
                        ("2605.00002", "Existing", "Abstract", "math.PR", "A. Author", "2026-05-30"),
                    )
                result = update_arxiv_db.run_since_update(
                    config=replace(self.config, cache_dir=cache_dir),
                    db_path=db_path,
                    since=dt.date(2026, 5, 29),
                    source="oai",
                    out=io.StringIO(),
                )

                with sqlite3.connect(cache_dir / "arxiv_update_state.sqlite") as conn:
                    deleted = conn.execute(
                        "SELECT id, datestamp, identifier FROM arxiv_deleted_records"
                    ).fetchall()
                with sqlite3.connect(db_path) as conn:
                    remaining = conn.execute("SELECT COUNT(*) FROM papers WHERE id = ?", ("2605.00002",)).fetchone()[0]

            self.assertEqual(result.deleted_recorded, 1)
            self.assertEqual(deleted, [("2605.00002", "2026-05-31", "oai:arXiv.org:2605.00002")])
            self.assertEqual(remaining, 1)
        finally:
            update_arxiv_db.default_http_get = original_get

    def test_oai_fetch_follows_resumption_tokens_and_handles_errors(self) -> None:
        first_page = b"""<?xml version="1.0" encoding="UTF-8"?>
        <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
          <ListRecords>
            <record>
              <metadata><arXiv xmlns="http://arxiv.org/OAI/arXiv/">
                <id>2605.00001</id><created>2026-05-30</created>
                <authors><author><keyname>Smith</keyname></author></authors>
                <title>First</title><categories>math.PR</categories><abstract>One</abstract>
              </arXiv></metadata>
            </record>
            <resumptionToken>next-token</resumptionToken>
          </ListRecords>
        </OAI-PMH>"""
        second_page = b"""<?xml version="1.0" encoding="UTF-8"?>
        <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
          <ListRecords>
            <record>
              <metadata><arXiv xmlns="http://arxiv.org/OAI/arXiv/">
                <id>2605.00002</id><created>2026-05-31</created>
                <authors><author><keyname>Jones</keyname></author></authors>
                <title>Second</title><categories>math.CO</categories><abstract>Two</abstract>
              </arXiv></metadata>
            </record>
          </ListRecords>
        </OAI-PMH>"""
        calls: list[str] = []

        def fake_get(url: str) -> bytes:
            calls.append(url)
            return second_page if "resumptionToken=next-token" in url else first_page

        records = list(update_arxiv_db.fetch_oai_records(dt.date(2026, 5, 29), http_get=fake_get))

        self.assertEqual([record.id for record in records], ["2605.00001", "2605.00002"])
        self.assertEqual(len(calls), 2)

        no_records = b"""<OAI-PMH><error code="noRecordsMatch">none</error></OAI-PMH>"""
        self.assertEqual(
            list(update_arxiv_db.fetch_oai_records(dt.date(2026, 5, 29), http_get=lambda url: no_records)),
            [],
        )
        bad_error = b"""<OAI-PMH><error code="badArgument">broken</error></OAI-PMH>"""
        with self.assertRaises(update_arxiv_db.FetchError):
            list(update_arxiv_db.fetch_oai_records(dt.date(2026, 5, 29), http_get=lambda url: bad_error))

    def test_xml_parse_errors_are_fetch_errors(self) -> None:
        with self.assertRaises(update_arxiv_db.FetchError):
            list(update_arxiv_db.fetch_oai_records(dt.date(2026, 5, 29), http_get=lambda url: b"<broken"))
        with self.assertRaises(update_arxiv_db.FetchError):
            list(update_arxiv_db.fetch_api_records(dt.date(2026, 5, 29), limit=1, http_get=lambda url: b"<broken"))

    def test_api_fallback_requires_limit(self) -> None:
        with self.assertRaises(update_arxiv_db.FetchError):
            list(update_arxiv_db.fetch_api_records(dt.date(2026, 5, 29), limit=None))

    def test_fetchers_reject_non_positive_limits_before_fetching(self) -> None:
        called = False

        def fake_get(_url: str) -> bytes:
            nonlocal called
            called = True
            return b"<OAI-PMH />"

        with self.assertRaises(update_arxiv_db.FetchError):
            list(update_arxiv_db.fetch_oai_records(dt.date(2026, 5, 29), limit=0, http_get=fake_get))
        self.assertFalse(called)
        with self.assertRaises(update_arxiv_db.FetchError):
            list(update_arxiv_db.fetch_api_records(dt.date(2026, 5, 29), limit=0, http_get=fake_get))
        self.assertFalse(called)

    def test_allow_api_fallback_streams_oai_success_without_preloading(self) -> None:
        first_page = b"""<?xml version="1.0" encoding="UTF-8"?>
        <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
          <ListRecords>
            <record>
              <metadata><arXiv xmlns="http://arxiv.org/OAI/arXiv/">
                <id>2605.00001</id><created>2026-05-30</created>
                <authors><author><keyname>Smith</keyname></author></authors>
                <title>First</title><categories>math.PR</categories><abstract>One</abstract>
              </arXiv></metadata>
            </record>
            <resumptionToken>next-token</resumptionToken>
          </ListRecords>
        </OAI-PMH>"""
        second_page = b"""<?xml version="1.0" encoding="UTF-8"?>
        <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
          <ListRecords>
            <record>
              <metadata><arXiv xmlns="http://arxiv.org/OAI/arXiv/">
                <id>2605.00002</id><created>2026-05-31</created>
                <authors><author><keyname>Jones</keyname></author></authors>
                <title>Second</title><categories>math.CO</categories><abstract>Two</abstract>
              </arXiv></metadata>
            </record>
          </ListRecords>
        </OAI-PMH>"""
        calls: list[str] = []
        original_get = update_arxiv_db.default_http_get
        try:
            def fake_get(url: str) -> bytes:
                calls.append(url)
                return second_page if "resumptionToken=next-token" in url else first_page

            update_arxiv_db.default_http_get = fake_get
            records = update_arxiv_db._source_records(
                dt.date(2026, 5, 29),
                limit=None,
                source="oai",
                endpoint="https://oai.test",
                allow_api_fallback=True,
            )
            record_iter = iter(records)

            self.assertEqual(calls, [])
            self.assertEqual(next(record_iter).id, "2605.00001")
            self.assertEqual(len(calls), 1)
            self.assertEqual(next(record_iter).id, "2605.00002")
            self.assertEqual(len(calls), 2)
        finally:
            update_arxiv_db.default_http_get = original_get

    def test_api_fetch_and_oai_failure_fallback_parse_records(self) -> None:
        api_payload = b"""<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <id>http://arxiv.org/abs/2605.00003v2</id>
            <published>2026-05-31T00:00:00Z</published>
            <title> API title </title>
            <summary> API abstract </summary>
            <author><name>Ada Author</name></author>
            <category term="math.NT" />
          </entry>
        </feed>"""
        calls: list[str] = []

        def fake_get(url: str) -> bytes:
            calls.append(url)
            return api_payload

        records = list(update_arxiv_db.fetch_api_records(dt.date(2026, 5, 29), limit=1, http_get=fake_get))

        self.assertIn("max_results=1", calls[0])
        self.assertEqual(records[0].id, "2605.00003")
        self.assertEqual(records[0].authors, "Ada Author")

        original_get = update_arxiv_db.default_http_get
        try:
            def fallback_get(url: str) -> bytes:
                if "oai.test" in url:
                    raise update_arxiv_db.FetchError("OAI unavailable")
                return api_payload

            update_arxiv_db.default_http_get = fallback_get
            with tempfile.TemporaryDirectory() as tmp:
                db_path = Path(tmp) / "arxiv.sqlite"
                create_papers_db(db_path)
                result = update_arxiv_db.run_since_update(
                    config=self.config,
                    db_path=db_path,
                    since=dt.date(2026, 5, 29),
                    limit=1,
                    endpoint="https://oai.test",
                    allow_api_fallback=True,
                    out=io.StringIO(),
                )
            self.assertEqual(result.fetched, 1)
            self.assertEqual(result.upserted, 1)
        finally:
            update_arxiv_db.default_http_get = original_get

    def test_check_env_reports_safe_status_without_secret_values(self) -> None:
        original_s2 = os.environ.get("S2_API_KEY")
        os.environ["S2_API_KEY"] = "do-not-print-this-value"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                db_path = root / "arxiv.sqlite"
                sources_dir = root / "sources"
                sources_dir.mkdir()
                create_papers_db(db_path)

                out = io.StringIO()
                exit_code = check_env.run_checks(
                    config=self.config,
                    db_path=db_path,
                    sources_dir=sources_dir,
                    out=out,
                )
                text = out.getvalue()

            self.assertEqual(exit_code, 0)
            self.assertIn("arxiv_db_status: ok", text)
            self.assertIn("papers_count: 0", text)
            self.assertIn("arxiv_sources_status: ok", text)
            self.assertIn("S2_API_KEY: present", text)
            self.assertNotIn("do-not-print-this-value", text)
        finally:
            if original_s2 is None:
                os.environ.pop("S2_API_KEY", None)
            else:
                os.environ["S2_API_KEY"] = original_s2

    def test_check_env_reports_corrupt_database_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "not-sqlite.db"
            sources_dir = root / "sources"
            sources_dir.mkdir()
            db_path.write_text("not a sqlite database", encoding="utf-8")

            out = io.StringIO()
            exit_code = check_env.run_checks(
                config=self.config,
                db_path=db_path,
                sources_dir=sources_dir,
                out=out,
            )
            text = out.getvalue()

        self.assertEqual(exit_code, 1)
        self.assertIn("arxiv_db_status: failed", text)
        self.assertNotIn("Traceback", text)


if __name__ == "__main__":
    unittest.main()

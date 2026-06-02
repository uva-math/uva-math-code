from __future__ import annotations

import io
import json
import os
import sqlite3
import tempfile
import unittest
import urllib.request
from pathlib import Path

from scripts.uva_arxiv import crossref_client, s2_client


def s2_payload(**overrides: object) -> bytes:
    payload: dict[str, object] = {
        "externalIds": {"DOI": "10.1000/s2-test", "ArXiv": "2501.01234"},
        "title": "A Semantic Scholar Paper",
        "year": 2025,
        "authors": [{"name": "Ada Author", "authorId": "12345"}],
        "venue": "Journal of Tests",
        "journal": {"name": "Journal of Tests", "volume": "1", "pages": "1-10"},
        "publicationVenue": {"name": "Journal of Tests"},
        "publicationDate": "2025-02-03",
        "url": "https://www.semanticscholar.org/paper/test",
    }
    payload.update(overrides)
    return json.dumps(payload).encode("utf-8")


def crossref_payload(message_overrides: dict[str, object] | None = None) -> bytes:
    message: dict[str, object] = {
        "DOI": "10.1000/crossref-test",
        "title": ["A CrossRef Paper"],
        "container-title": ["Journal of Tests"],
        "short-container-title": ["J. Tests"],
        "published-print": {"date-parts": [[2025, 2, 3]]},
        "issued": {"date-parts": [[2025]]},
        "author": [
            {
                "given": "Ada",
                "family": "Author",
                "ORCID": "https://orcid.org/0000-0000-0000-0001",
                "affiliation": [{"name": "University of Virginia"}],
            }
        ],
    }
    if message_overrides:
        message.update(message_overrides)
    return json.dumps({"status": "ok", "message": message}).encode("utf-8")


def header_value(request: urllib.request.Request, name: str) -> str | None:
    headers = {key.lower(): value for key, value in request.header_items()}
    return headers.get(name.lower())


class SemanticScholarClientTests(unittest.TestCase):
    def preserve_env(self, *keys: str) -> dict[str, str | None]:
        original = {key: os.environ.get(key) for key in keys}
        for key in keys:
            os.environ.pop(key, None)
        return original

    def restore_env(self, original: dict[str, str | None]) -> None:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_s2_cache_miss_fetches_and_stores_normalized_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "s2.sqlite"
            calls: list[str] = []

            def fake_get(request: urllib.request.Request, timeout: int) -> bytes:
                calls.append(request.full_url)
                self.assertEqual(header_value(request, "x-api-key"), "s2-secret")
                self.assertEqual(timeout, 30)
                return s2_payload()

            result = s2_client.smoke_s2(
                "2501.01234v2",
                cache_path=cache_path,
                api_key="s2-secret",
                http_get=fake_get,
            )

            self.assertEqual(result.status, "complete")
            self.assertFalse(result.cache_hit)
            self.assertTrue(result.api_key_present)
            self.assertEqual(result.arxiv_id, "2501.01234")
            self.assertEqual(result.doi, "10.1000/s2-test")
            self.assertEqual(result.publication_date, "2025-02-03")
            self.assertEqual(len(result.authors), 1)
            self.assertEqual(len(calls), 1)

            with sqlite3.connect(cache_path) as conn:
                row = conn.execute(
                    "SELECT status, doi, journal FROM s2_papers WHERE arxiv_id = ?",
                    ("2501.01234",),
                ).fetchone()
            self.assertEqual(row, ("complete", "10.1000/s2-test", "Journal of Tests"))

    def test_s2_cache_hit_avoids_network(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "s2.sqlite"
            s2_client.smoke_s2(
                "2501.01234",
                cache_path=cache_path,
                api_key="s2-secret",
                http_get=lambda request, timeout: s2_payload(),
            )

            def forbidden_get(request: urllib.request.Request, timeout: int) -> bytes:
                raise AssertionError(f"unexpected network call to {request.full_url}")

            result = s2_client.smoke_s2(
                "2501.01234",
                cache_path=cache_path,
                api_key="s2-secret",
                http_get=forbidden_get,
            )

            self.assertTrue(result.cache_hit)
            self.assertEqual(result.status, "complete")

    def test_s2_missing_key_is_reported_safely_and_metadata_is_incomplete(self) -> None:
        original = self.preserve_env("S2_API_KEY", "SEMANTIC_SCHOLAR_API_KEY")
        try:
            with tempfile.TemporaryDirectory() as tmp:
                cache_path = Path(tmp) / "s2.sqlite"

                def fake_get(request: urllib.request.Request, timeout: int) -> bytes:
                    self.assertIsNone(header_value(request, "x-api-key"))
                    return s2_payload(journal=None, publicationDate=None)

                result = s2_client.smoke_s2(
                    "2501.01234",
                    cache_path=cache_path,
                    http_get=fake_get,
                    use_cache=False,
                )
                out = io.StringIO()
                s2_client.print_smoke_result(result, cache_path, out=out)
                text = out.getvalue()

            self.assertFalse(result.api_key_present)
            self.assertEqual(result.status, "incomplete")
            self.assertIn("publication_date", result.incomplete_fields)
            self.assertIn("S2_API_KEY: missing", text)
            self.assertIn("publication_scope_evidence: not_evidence", text)
        finally:
            self.restore_env(original)

    def test_s2_rate_limit_is_reported_without_writing_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "s2.sqlite"

            def limited_get(request: urllib.request.Request, timeout: int) -> bytes:
                raise s2_client.SemanticScholarRateLimitError("5")

            result = s2_client.smoke_s2(
                "2501.01234",
                cache_path=cache_path,
                api_key="s2-secret",
                http_get=limited_get,
            )

            self.assertEqual(result.status, "rate_limited")
            self.assertIn("retry_after=5", result.notes)
            self.assertFalse(cache_path.exists())

    def test_s2_request_errors_do_not_write_cache(self) -> None:
        for payload in (b"{not json", b"[]"):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as tmp:
                    cache_path = Path(tmp) / "s2.sqlite"

                    result = s2_client.smoke_s2(
                        "2501.01234",
                        cache_path=cache_path,
                        api_key="s2-secret",
                        http_get=lambda request, timeout: payload,
                    )

                    self.assertEqual(result.status, "request_error")
                    self.assertFalse(cache_path.exists())

    def test_s2_metadata_conflict_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "s2.sqlite"
            result = s2_client.smoke_s2(
                "2501.01234",
                cache_path=cache_path,
                api_key="s2-secret",
                http_get=lambda request, timeout: s2_payload(
                    externalIds={"DOI": "10.1000/s2-test", "ArXiv": "2501.99999"}
                ),
            )

            self.assertEqual(result.status, "conflict")
            self.assertEqual(result.conflicts[0].field, "arxiv_id")
            with sqlite3.connect(cache_path) as conn:
                row = conn.execute(
                    "SELECT field, expected, observed FROM metadata_conflicts WHERE source = ?",
                    ("semantic_scholar",),
                ).fetchone()
            self.assertEqual(row, ("arxiv_id", "2501.01234", "2501.99999"))


class CrossRefClientTests(unittest.TestCase):
    def preserve_env(self, *keys: str) -> dict[str, str | None]:
        original = {key: os.environ.get(key) for key in keys}
        for key in keys:
            os.environ.pop(key, None)
        return original

    def restore_env(self, original: dict[str, str | None]) -> None:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_crossref_cache_miss_fetches_and_stores_normalized_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "crossref.sqlite"
            calls: list[str] = []

            def fake_get(request: urllib.request.Request, timeout: int) -> bytes:
                calls.append(request.full_url)
                self.assertEqual(
                    header_value(request, "Crossref-Plus-API-Token"),
                    "Bearer crossref-secret",
                )
                self.assertIn("mailto=math%40example.edu", request.full_url)
                return crossref_payload()

            result = crossref_client.smoke_crossref(
                "https://doi.org/10.1000/crossref-test",
                cache_path=cache_path,
                mailto="math@example.edu",
                api_key="crossref-secret",
                http_get=fake_get,
            )

            self.assertEqual(result.status, "complete")
            self.assertFalse(result.cache_hit)
            self.assertTrue(result.mailto_present)
            self.assertTrue(result.api_key_present)
            self.assertEqual(result.doi, "10.1000/crossref-test")
            self.assertEqual(result.container_title, "Journal of Tests")
            self.assertEqual(result.published_date, "2025-02-03")
            self.assertEqual(len(result.authors), 1)
            self.assertEqual(len(calls), 1)

            with sqlite3.connect(cache_path) as conn:
                row = conn.execute(
                    "SELECT status, metadata_doi, container_title FROM crossref_works WHERE doi = ?",
                    ("10.1000/crossref-test",),
                ).fetchone()
            self.assertEqual(row, ("complete", "10.1000/crossref-test", "Journal of Tests"))

    def test_crossref_cache_hit_avoids_network(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "crossref.sqlite"
            crossref_client.smoke_crossref(
                "10.1000/crossref-test",
                cache_path=cache_path,
                mailto="math@example.edu",
                http_get=lambda request, timeout: crossref_payload(),
            )

            def forbidden_get(request: urllib.request.Request, timeout: int) -> bytes:
                raise AssertionError(f"unexpected network call to {request.full_url}")

            result = crossref_client.smoke_crossref(
                "10.1000/crossref-test",
                cache_path=cache_path,
                mailto="math@example.edu",
                http_get=forbidden_get,
            )

            self.assertTrue(result.cache_hit)
            self.assertEqual(result.status, "complete")

    def test_crossref_missing_keys_are_reported_safely_and_metadata_is_incomplete(self) -> None:
        original = self.preserve_env("CROSSREF_MAILTO", "CROSSREF_API_KEY")
        try:
            with tempfile.TemporaryDirectory() as tmp:
                cache_path = Path(tmp) / "crossref.sqlite"

                def fake_get(request: urllib.request.Request, timeout: int) -> bytes:
                    self.assertIsNone(header_value(request, "Crossref-Plus-API-Token"))
                    self.assertNotIn("mailto=", request.full_url)
                    return crossref_payload(
                        {
                            "container-title": [],
                            "published-print": None,
                            "published-online": None,
                            "published": None,
                        }
                    )

                result = crossref_client.smoke_crossref(
                    "10.1000/crossref-test",
                    cache_path=cache_path,
                    http_get=fake_get,
                    use_cache=False,
                )
                out = io.StringIO()
                crossref_client.print_smoke_result(result, cache_path, out=out)
                text = out.getvalue()

            self.assertFalse(result.mailto_present)
            self.assertFalse(result.api_key_present)
            self.assertEqual(result.status, "incomplete")
            self.assertIn("container_title", result.incomplete_fields)
            self.assertIn("CROSSREF_MAILTO: missing", text)
            self.assertIn("CROSSREF_API_KEY: missing", text)
            self.assertIn("publication_scope_evidence: not_evidence", text)
        finally:
            self.restore_env(original)

    def test_crossref_rate_limit_is_reported_without_writing_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "crossref.sqlite"

            def limited_get(request: urllib.request.Request, timeout: int) -> bytes:
                raise crossref_client.CrossRefRateLimitError("3")

            result = crossref_client.smoke_crossref(
                "10.1000/crossref-test",
                cache_path=cache_path,
                mailto="math@example.edu",
                http_get=limited_get,
            )

            self.assertEqual(result.status, "rate_limited")
            self.assertIn("retry_after=3", result.notes)
            self.assertFalse(cache_path.exists())

    def test_crossref_request_errors_do_not_write_cache(self) -> None:
        for payload in (b"{not json", b"[]", json.dumps({"status": "ok"}).encode("utf-8")):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as tmp:
                    cache_path = Path(tmp) / "crossref.sqlite"

                    result = crossref_client.smoke_crossref(
                        "10.1000/crossref-test",
                        cache_path=cache_path,
                        mailto="math@example.edu",
                        http_get=lambda request, timeout: payload,
                    )

                    self.assertEqual(result.status, "request_error")
                    self.assertFalse(cache_path.exists())

    def test_crossref_metadata_conflict_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "crossref.sqlite"
            result = crossref_client.smoke_crossref(
                "10.1000/crossref-test",
                cache_path=cache_path,
                mailto="math@example.edu",
                http_get=lambda request, timeout: crossref_payload(
                    {"DOI": "10.1000/different-doi"}
                ),
            )

            self.assertEqual(result.status, "conflict")
            self.assertEqual(result.conflicts[0].field, "doi")
            with sqlite3.connect(cache_path) as conn:
                row = conn.execute(
                    "SELECT field, expected, observed FROM metadata_conflicts WHERE source = ?",
                    ("crossref",),
                ).fetchone()
            self.assertEqual(row, ("doi", "10.1000/crossref-test", "10.1000/different-doi"))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import gzip
import io
import sqlite3
import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts.uva_arxiv import affiliation, env, sources


def make_tar(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, content in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


class SourceFetchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = env.load_config(load_env_file=False)

    def test_safe_source_dir_names_normalize_versions_and_old_ids(self) -> None:
        self.assertEqual(sources.safe_source_dir_name("2501.01234v2"), "2501.01234")
        self.assertEqual(sources.safe_source_dir_name("math/0301234"), "math__0301234")

    def test_fetch_dry_run_does_not_create_target_or_call_network(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def forbidden_get(url: str) -> bytes:
                raise AssertionError(f"unexpected network call to {url}")

            result = sources.fetch_source(
                self.config,
                "2501.01234",
                sources_dir=root,
                dry_run=True,
                http_get=forbidden_get,
                rate_limit_seconds=0,
            )

            self.assertEqual(result.status, "would_fetch")
            self.assertFalse((root / "2501.01234").exists())

    def test_fetch_retries_and_unpacks_tar_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = make_tar({"main.tex": b"University of Virginia\n"})
            calls = 0

            def flaky_get(url: str) -> bytes:
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise sources.SourceFetchError("temporary failure")
                return payload

            result = sources.fetch_source(
                self.config,
                "2501.01234",
                sources_dir=root,
                dry_run=False,
                http_get=flaky_get,
                retries=1,
                rate_limit_seconds=0,
            )

            self.assertEqual(calls, 2)
            self.assertEqual(result.status, "fetched")
            self.assertEqual(result.source_format, "tar")
            self.assertEqual((root / "2501.01234" / "main.tex").read_text(), "University of Virginia\n")

    def test_unpack_gzip_raw_tex_and_raw_pdf_fallbacks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gzip_dir = root / "gzip"
            raw_dir = root / "raw"
            pdf_dir = root / "pdf"

            gzip_format, gzip_files = sources.unpack_source_bytes(
                gzip.compress(b"\\documentclass{article}\n"),
                gzip_dir,
            )
            raw_format, raw_files = sources.unpack_source_bytes(
                b"\\documentclass{article}\n",
                raw_dir,
            )
            pdf_format, pdf_files = sources.unpack_source_bytes(
                b"%PDF-1.7\n% raw pdf fallback\n",
                pdf_dir,
            )

            self.assertEqual((gzip_format, gzip_files), ("gzip", ("source.tex",)))
            self.assertEqual((raw_format, raw_files), ("raw", ("source.tex",)))
            self.assertEqual((pdf_format, pdf_files), ("pdf", ("source.pdf",)))
            self.assertTrue((gzip_dir / "source.tex").exists())
            self.assertTrue((raw_dir / "source.tex").exists())
            self.assertTrue((pdf_dir / "source.pdf").exists())


class AffiliationScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = env.load_config(load_env_file=False)
        self.patterns = affiliation.AffiliationPatternSet(
            positive=("University of Virginia", "@virginia.edu"),
            negative=("Virginia Tech", "West Virginia University"),
        )

    def scan_text(self, text: str) -> affiliation.AffiliationScanResult:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_dir = root / "2501.01234"
            source_dir.mkdir()
            (source_dir / "main.tex").write_text(text, encoding="utf-8")
            return affiliation.scan_source_dir("2501.01234", source_dir, self.patterns)

    def test_positive_source_evidence_is_confirmed(self) -> None:
        result = self.scan_text("Department of Mathematics, University of Virginia\n")

        self.assertEqual(result.evidence, "confirmed")
        self.assertEqual(result.positive_count, 1)
        self.assertEqual(result.negative_count, 0)
        self.assertFalse(result.is_rejection)

    def test_negative_source_evidence_is_conflict_not_rejection(self) -> None:
        result = self.scan_text("Current affiliation: Virginia Tech\n")

        self.assertEqual(result.evidence, "conflict")
        self.assertEqual(result.positive_count, 0)
        self.assertEqual(result.negative_count, 1)
        self.assertFalse(result.is_rejection)

    def test_conflicting_source_evidence_records_both_sides(self) -> None:
        result = self.scan_text("University of Virginia and Virginia Tech\n")

        self.assertEqual(result.evidence, "conflict")
        self.assertEqual(result.positive_count, 1)
        self.assertEqual(result.negative_count, 1)

    def test_absent_source_evidence_is_an_evidence_state(self) -> None:
        result = self.scan_text("No affiliation line is present here.\n")

        self.assertEqual(result.evidence, "absent")
        self.assertEqual(result.positive_count, 0)
        self.assertEqual(result.negative_count, 0)
        self.assertIn("not a rejection", result.notes)
        self.assertFalse(result.is_rejection)

    def test_missing_source_is_recorded_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = affiliation.scan_source_dir(
                "2501.01234",
                Path(tmp) / "2501.01234",
                self.patterns,
            )

        self.assertEqual(result.evidence, "missing_source")
        self.assertEqual(result.checked_files, 0)
        self.assertFalse(result.is_rejection)

    def test_scan_affiliation_writes_ignored_cache_database(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources_root = root / "sources"
            source_dir = sources_root / "2501.01234"
            source_dir.mkdir(parents=True)
            (source_dir / "main.tex").write_text("@virginia.edu\n", encoding="utf-8")
            patterns_path = root / "patterns.yml"
            patterns_path.write_text('positive:\n  - "@virginia.edu"\nnegative:\n  - "Virginia Tech"\n')
            cache_path = root / "cache" / "affiliation.sqlite"

            result = affiliation.scan_affiliation(
                self.config,
                "2501.01234",
                sources_dir=sources_root,
                patterns_path=patterns_path,
                cache_path=cache_path,
            )

            self.assertEqual(result.evidence, "confirmed")
            self.assertTrue(cache_path.exists())
            with sqlite3.connect(cache_path) as conn:
                row = conn.execute(
                    "SELECT evidence, positive_count, negative_count, payload_json "
                    "FROM affiliation_scans WHERE arxiv_id = ?",
                    ("2501.01234",),
                ).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], "confirmed")
            self.assertEqual(row[1], 1)
            self.assertEqual(row[2], 0)
            self.assertIn('"is_rejection": false', row[3])


if __name__ == "__main__":
    unittest.main()

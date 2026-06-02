from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MAKEFILE = REPO_ROOT / "Makefile"
PHASE_ONE_TARGETS = (
    "uva-arxiv-check",
    "uva-arxiv-db-since",
    "uva-arxiv-db-since-dry",
    "uva-arxiv-roster-history",
    "uva-arxiv-source-smoke",
    "uva-arxiv-api-smoke",
)


def make_dry_run(*args: str) -> str:
    result = subprocess.run(
        ["make", "-n", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


class MakefileTargetTests(unittest.TestCase):
    def test_phase_one_targets_are_declared_phony(self) -> None:
        text = MAKEFILE.read_text(encoding="utf-8")
        phony_targets: set[str] = set()
        for line in text.splitlines():
            if line.startswith(".PHONY:"):
                phony_targets.update(line.split(":", 1)[1].split())

        for target in PHASE_ONE_TARGETS:
            self.assertIn(target, phony_targets)

    def test_db_since_dry_omits_since_when_not_set(self) -> None:
        output = make_dry_run("uva-arxiv-db-since-dry")

        self.assertIn("scripts/uva_arxiv/update_arxiv_db.py since", output)
        self.assertIn("--dry-run", output)
        self.assertNotIn("--since", output)

    def test_db_since_targets_pass_since_and_args_when_set(self) -> None:
        output = make_dry_run(
            "uva-arxiv-db-since-dry",
            "SINCE=2026-05-29",
            "ARGS=--limit 3",
        )

        self.assertIn('--since "2026-05-29"', output)
        self.assertIn("--dry-run", output)
        self.assertIn("--limit 3", output)

    def test_source_and_api_smoke_targets_pass_id_and_args(self) -> None:
        source_output = make_dry_run(
            "uva-arxiv-source-smoke",
            "ID=2501.01234",
            "ARGS=--rate-limit 0",
        )
        api_output = make_dry_run(
            "uva-arxiv-api-smoke",
            "ID=2501.01234",
            "ARGS=--no-cache",
        )

        self.assertIn('scripts/uva_arxiv/sources.py fetch --id "2501.01234"', source_output)
        self.assertIn("--dry-run", source_output)
        self.assertIn("--rate-limit 0", source_output)
        self.assertIn('scripts/uva_arxiv/s2_client.py smoke --id "2501.01234"', api_output)
        self.assertIn("--no-cache", api_output)

    def test_roster_history_target_is_dry_run_with_args_passthrough(self) -> None:
        output = make_dry_run("uva-arxiv-roster-history", "ARGS=--as-of 2026-06-02")

        self.assertIn("scripts/uva_arxiv/roster_history.py --dry-run", output)
        self.assertIn("--no-write", output)
        self.assertIn("--as-of 2026-06-02", output)

    def test_representative_targets_execute_with_temp_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "arxiv.sqlite"
            sources_dir = root / "sources"
            sources_dir.mkdir()
            with sqlite3.connect(db_path) as conn:
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
                conn.execute(
                    "INSERT INTO papers VALUES (?, ?, ?, ?, ?, ?)",
                    ("2605.00001", "Existing", "Abstract", "math.PR", "A. Author", "2026-05-29"),
                )
            env = os.environ.copy()
            env.update(
                {
                    "ARXIV_DB": str(db_path),
                    "ARXIV_SOURCES_DIR": str(sources_dir),
                    "UVA_ARXIV_PYTHON": sys.executable,
                }
            )

            for args in (
                ["uva-arxiv-check"],
                ["uva-arxiv-db-since-dry", "ARGS=--limit 1"],
                ["uva-arxiv-source-smoke", "ID=2501.01234", "ARGS=--rate-limit 0"],
            ):
                with self.subTest(args=args):
                    result = subprocess.run(
                        ["make", *args],
                        cwd=REPO_ROOT,
                        env=env,
                        check=True,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    self.assertNotIn("Traceback", result.stderr + result.stdout)

    def test_phase_one_targets_do_not_generate_public_paper_outputs(self) -> None:
        text = MAKEFILE.read_text(encoding="utf-8")

        self.assertNotIn("assets/data/uva-arxiv-papers.json", text)
        self.assertNotIn("embedding", text.lower())
        self.assertNotIn("related-paper", text.lower())
        self.assertNotIn("vectors", text.lower())


class PlaceholderPageTests(unittest.TestCase):
    def test_arxiv_placeholder_is_unlinked_and_not_in_sitemap(self) -> None:
        page = REPO_ROOT / "arxiv" / "index.md"
        text = page.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        front_matter = text.split("---\n", 2)[1]

        self.assertIn("permalink: /arxiv/", front_matter)
        self.assertIn("sitemap: false", front_matter)
        self.assertNotIn("nav_id", front_matter)
        self.assertNotIn("nav_weight", front_matter)
        self.assertIn("Data is not loaded yet", text)


if __name__ == "__main__":
    unittest.main()

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
OLD_UVA_ARXIV_TARGETS = (
    "uva-arxiv-check",
    "uva-arxiv-db-since",
    "uva-arxiv-db-since-dry",
    "uva-arxiv-roster-history",
    "uva-arxiv-source-smoke",
    "uva-arxiv-api-smoke",
    "uva-arxiv-journal-refs",
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
    def test_only_one_uva_arxiv_make_target_is_declared_phony(self) -> None:
        text = MAKEFILE.read_text(encoding="utf-8")
        phony_targets: set[str] = set()
        for line in text.splitlines():
            if line.startswith(".PHONY:"):
                phony_targets.update(line.split(":", 1)[1].split())

        self.assertIn("uva-arxiv", phony_targets)
        for target in OLD_UVA_ARXIV_TARGETS:
            self.assertNotIn(target, phony_targets)

    def test_single_target_forwards_args_to_dispatcher(self) -> None:
        output = make_dry_run("uva-arxiv", "ARGS=journal-refs --dry-run --limit 3")

        self.assertIn("scripts/uva_arxiv/cli.py journal-refs --dry-run --limit 3", output)

    def test_cli_help_lists_representative_subcommands(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/uva_arxiv/cli.py", "help"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertIn("journal-refs", result.stdout)
        self.assertIn("db-since", result.stdout)
        self.assertIn("source-fetch", result.stdout)
        self.assertNotIn("Traceback", result.stderr + result.stdout)

    def test_representative_dispatcher_commands_execute_with_temp_overrides(self) -> None:
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
                ["uva-arxiv"],
                ["uva-arxiv", "ARGS=db-since --dry-run --limit 1"],
                ["uva-arxiv", "ARGS=source-fetch --id 2501.01234 --dry-run --rate-limit 0"],
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

    def test_uva_arxiv_target_does_not_generate_public_paper_outputs(self) -> None:
        text = MAKEFILE.read_text(encoding="utf-8")

        self.assertNotIn("assets/data/uva-arxiv-papers.json", text)
        self.assertNotIn("embedding", text.lower())
        self.assertNotIn("related-paper", text.lower())
        self.assertNotIn("vectors", text.lower())


class ArxivPageTests(unittest.TestCase):
    def test_arxiv_page_is_unlinked_not_in_sitemap_and_loads_preview_ui(self) -> None:
        page = REPO_ROOT / "arxiv" / "index.md"
        text = page.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        front_matter = text.split("---\n", 2)[1]

        self.assertIn("permalink: /arxiv/", front_matter)
        self.assertIn("sitemap: false", front_matter)
        self.assertNotIn("nav_id", front_matter)
        self.assertNotIn("nav_weight", front_matter)
        self.assertIn("id=\"uva-arxiv-app\"", text)
        self.assertIn("assets/data/uva-arxiv-papers.json", text)
        self.assertIn("assets/js/uva-arxiv.js", text)


if __name__ == "__main__":
    unittest.main()

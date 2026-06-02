from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from scripts.uva_arxiv import env


class ScaffoldConfigTests(unittest.TestCase):
    def test_config_loads_expected_phase_one_values(self) -> None:
        config = env.load_config(load_env_file=False)

        self.assertEqual(config.initial_arxiv_start_date, "2021-08-01")
        self.assertEqual(config.site_endpoint, "/arxiv/")
        self.assertEqual(config.arxiv_db, Path("/Users/leo/Data/arxiv/arxiv-metadata.db"))
        self.assertEqual(
            config.arxiv_sources_dir,
            Path("/Users/leo/Homepage/_scripts/arxiv/sources"),
        )
        self.assertIn("faculty", config.people_dirs)
        self.assertIn("agfm_other", config.role_groups)
        self.assertEqual(
            config.role_groups["faculty"]["include_general_position"],
            ["faculty"],
        )

    def test_required_data_files_exist(self) -> None:
        self.assertEqual(env.missing_data_files(), [])

    def test_ensure_local_dirs_creates_cache_and_data_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_dir, data_dir = env.ensure_local_dirs(root / "cache", root / "data")

            self.assertTrue(cache_dir.is_dir())
            self.assertTrue(data_dir.is_dir())

    def test_dotenv_loading_and_status_do_not_expose_secret_values(self) -> None:
        original_s2 = os.environ.pop("S2_API_KEY", None)
        original_alias = os.environ.pop("SEMANTIC_SCHOLAR_API_KEY", None)
        try:
            env_key = "SEMANTIC" + "_SCHOLAR_API_KEY"
            token_value = "placeholder-token-value"
            with tempfile.TemporaryDirectory() as tmp:
                dotenv = Path(tmp) / ".env"
                dotenv.write_text(
                    f'{env_key}="{token_value}"\n',
                    encoding="utf-8",
                )

                loaded = env.load_dotenv(dotenv)
                env.normalize_api_env()
                status = env.safe_env_status()

                self.assertEqual(loaded, {"SEMANTIC_SCHOLAR_API_KEY": True})
                self.assertEqual(os.environ["S2_API_KEY"], token_value)
                self.assertTrue(status["S2_API_KEY"])
                self.assertTrue(status["SEMANTIC_SCHOLAR_API_KEY"])
                self.assertNotIn(token_value, repr(status))
        finally:
            os.environ.pop("S2_API_KEY", None)
            os.environ.pop("SEMANTIC_SCHOLAR_API_KEY", None)
            if original_s2 is not None:
                os.environ["S2_API_KEY"] = original_s2
            if original_alias is not None:
                os.environ["SEMANTIC_SCHOLAR_API_KEY"] = original_alias

    def test_dotenv_is_gitignored(self) -> None:
        self.assertTrue(env.dotenv_is_gitignored())


if __name__ == "__main__":
    unittest.main()

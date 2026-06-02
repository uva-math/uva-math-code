"""Environment and shared-path smoke checks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.uva_arxiv import arxiv_db, env


def _format_path(path: Path) -> str:
    try:
        return str(path.relative_to(env.REPO_ROOT))
    except ValueError:
        return str(path)


def run_checks(
    config: env.UvaArxivConfig | None = None,
    db_path: Path | None = None,
    sources_dir: Path | None = None,
    out: TextIO = sys.stdout,
) -> int:
    config = config or env.load_config(ensure_dirs=True)
    db_path = Path(db_path or config.arxiv_db)
    sources_dir = Path(sources_dir or config.arxiv_sources_dir)

    ok = True
    print(f"repo_root: {_format_path(config.repo_root)} ({'ok' if config.repo_root.exists() else 'missing'})", file=out)
    if not config.repo_root.exists():
        ok = False

    dotenv_exists = env.DOTENV_PATH.exists()
    dotenv_ignored = env.dotenv_is_gitignored(config.repo_root)
    print(f"dotenv_file: {'present' if dotenv_exists else 'absent'}", file=out)
    print(f"dotenv_ignored: {dotenv_ignored}", file=out)
    if dotenv_exists and not dotenv_ignored:
        ok = False

    print(f"arxiv_db: {db_path}", file=out)
    if not db_path.exists():
        print("arxiv_db_status: missing", file=out)
        ok = False
    else:
        try:
            with arxiv_db.connect_readonly(db_path) as conn:
                schema = arxiv_db.validate_papers_schema(conn)
                stats = arxiv_db.get_db_stats(conn)
            print("arxiv_db_status: ok", file=out)
            print(f"papers_schema: {','.join(schema.columns)}", file=out)
            print(f"papers_count: {stats.count}", file=out)
            print(f"papers_min_date: {stats.min_date or 'none'}", file=out)
            print(f"papers_max_date: {stats.max_date or 'none'}", file=out)
        except arxiv_db.ArxivDatabaseError as exc:
            print(f"arxiv_db_status: failed ({exc})", file=out)
            ok = False

    print(f"arxiv_sources_dir: {sources_dir}", file=out)
    if sources_dir.is_dir():
        print("arxiv_sources_status: ok", file=out)
    else:
        print("arxiv_sources_status: missing", file=out)
        ok = False

    for key, present in env.safe_env_status().items():
        print(f"{key}: {'present' if present else 'missing'}", file=out)

    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Check UVA arXiv shared paths and environment.")
    parser.add_argument("--db", type=Path, help="Override the configured shared arXiv DB path.")
    parser.add_argument(
        "--sources-dir",
        type=Path,
        help="Override the configured shared arXiv source corpus path.",
    )
    args = parser.parse_args()
    return run_checks(db_path=args.db, sources_dir=args.sources_dir)


if __name__ == "__main__":
    raise SystemExit(main())

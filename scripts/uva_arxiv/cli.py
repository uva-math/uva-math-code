"""Single command dispatcher for UVA arXiv maintenance tasks."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class CommandSpec:
    description: str
    script: str
    prefix_args: tuple[str, ...] = ()


COMMANDS: dict[str, CommandSpec] = {
    "check": CommandSpec("check paths, DB schema, ignored .env, and API-key presence", "check_env.py"),
    "db-since": CommandSpec("update/dry-run the shared full-arXiv DB since a date", "update_arxiv_db.py", ("since",)),
    "roster-history": CommandSpec("rebuild/dry-run active roster history reports", "roster_history.py"),
    "source-fetch": CommandSpec("fetch/unpack one arXiv e-print source", "sources.py", ("fetch",)),
    "affiliation-scan": CommandSpec("scan one unpacked source directory for UVA affiliation evidence", "affiliation.py", ("scan",)),
    "s2-smoke": CommandSpec("fetch/cache one Semantic Scholar arXiv metadata record", "s2_client.py", ("smoke",)),
    "crossref-smoke": CommandSpec("fetch/cache one CrossRef DOI metadata record", "crossref_client.py", ("smoke",)),
    "review-reports": CommandSpec("rebuild candidate/source/decision reports from DB, roster, sources, and decisions", "review_reports.py"),
    "journal-refs": CommandSpec("populate journal/publication metadata for confirmed review rows", "journal_refs.py"),
    "public-data": CommandSpec("generate public-preview JSON/BibTeX assets from confirmed review rows", "public_data.py"),
}


USAGE_EXAMPLES = """Usage:
  make uva-arxiv
  make uva-arxiv ARGS="check"
  make uva-arxiv ARGS="review-reports --sync-archive"
  make uva-arxiv ARGS="journal-refs"
  make uva-arxiv ARGS="journal-refs --refresh-empty"
  make uva-arxiv ARGS="public-data"
  make uva-arxiv ARGS="db-since --dry-run --limit 1"
  make uva-arxiv ARGS="source-fetch --id 2501.01234 --dry-run"
  make uva-arxiv ARGS="affiliation-scan --id 2501.01234 --no-cache"
  make uva-arxiv ARGS="s2-smoke --id 2501.01234"
  make uva-arxiv ARGS="crossref-smoke --doi 10.1000/example"
"""


def print_help() -> None:
    print("UVA arXiv maintenance dispatcher")
    print()
    print(USAGE_EXAMPLES.strip())
    print()
    print("Commands:")
    for name, spec in sorted(COMMANDS.items()):
        print(f"  {name:18s} {spec.description}")
    print()
    print("With no ARGS, the dispatcher runs `check`.")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in {"-h", "--help", "help"}:
        print_help()
        return 0

    command = args.pop(0) if args else "check"
    spec = COMMANDS.get(command)
    if spec is None:
        print(f"unknown UVA arXiv command: {command}", file=sys.stderr)
        print("", file=sys.stderr)
        print_help()
        return 2

    script_path = SCRIPT_DIR / spec.script
    completed = subprocess.run(
        [sys.executable, str(script_path), *spec.prefix_args, *args],
        cwd=SCRIPT_DIR.parents[1],
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())

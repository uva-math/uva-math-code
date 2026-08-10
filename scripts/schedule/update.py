#!/usr/bin/env python3
"""Update the printable term class-schedule sheet end to end.

Pulls the current numbers from HoosList, rewrites the cells it can rewrite
mechanically, recompiles schedule.pdf, restages the archival per-term copy, and
refreshes the link blocks. Everything it cannot decide -- new sections, cancelled
sections, retitled courses, split meeting patterns -- is reported for a human.

A bare run is a dry run: it fetches, reports what would change, and touches nothing.

Usage:
    python3 scripts/schedule/update.py                  # report only
    python3 scripts/schedule/update.py --write          # apply, rebuild, restage
    python3 scripts/schedule/update.py --write --data sections.json   # reuse a dump

Since August 2026 HoosList answers plain HTTP clients with a Cloudflare challenge, so
the fetch falls back to reading the page out of a running Chrome; --chrome skips
straight to that.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import schedule_build                                     # noqa: E402
from hooslist_fetch import fetch_sections                 # noqa: E402
from schedule_refresh import refresh, report              # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--write", action="store_true",
                   help="apply the changes, recompile, and restage")
    p.add_argument("--semester", help='override the term read off the sheet, e.g. "Spring 2027"')
    p.add_argument("--data", help="reuse a hooslist_fetch.py dump instead of fetching")
    p.add_argument("--chrome", action="store_true",
                   help="read the page out of a running Chrome, skipping the HTTP "
                        "attempt the challenge will refuse (it falls back to this "
                        "anyway)")
    p.add_argument("--site", default=str(REPO), help="repository root")
    args = p.parse_args()

    site = pathlib.Path(args.site)
    tex_path = site / "schedule.tex"
    if not tex_path.is_file():
        raise SystemExit(f"no such file: {tex_path}")

    tex = tex_path.read_text()
    schedule_build.assert_room_free(tex, tex_path)
    semester = args.semester or schedule_build.detect_semester(tex)

    data = (json.load(open(args.data)) if args.data
            else fetch_sections(semester=semester, chrome=args.chrome))

    result, changes, notes = refresh(tex, data)
    report(data, changes, notes)

    if not args.write:
        print("\n(dry run -- pass --write to apply, rebuild, and restage)")
        return 0

    schedule_build.assert_room_free(result, tex_path)
    tex_path.write_text(result)
    print(f"\nwrote {tex_path.name}\n")
    try:
        return schedule_build.build_and_stage(site, semester)
    except BaseException:
        # The build is what validates the refresh. If it fails the sheet must go back
        # as it was, or the tree is left holding a rewritten source that was never
        # compiled and never checked.
        tex_path.write_text(tex)
        print(f"restored {tex_path.name} — the refresh was not applied", file=sys.stderr)
        raise


if __name__ == "__main__":
    sys.exit(main())

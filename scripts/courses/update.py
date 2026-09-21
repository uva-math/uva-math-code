#!/usr/bin/env python3
"""Rebuild _data/courses.yml from the UVA SIS course catalog.

The file feeds one thing: the `course` include, which prints "MATH 3351 (Elementary
Linear Algebra)" wherever a page cites a course. So it carries titles, units and the
graduate flag, and nothing else -- descriptions and prerequisites are the registrar's
text, live in SIS and the Undergraduate Record, and are linked, not mirrored.

A bare run is a dry run: it fetches, reports what would change, and touches nothing.

Usage:
    python3 scripts/courses/update.py            # report only
    python3 scripts/courses/update.py --write    # rewrite _data/courses.yml

A course that a published page cites but SIS no longer lists is kept, flagged
`sis_missing: true`, and reported: dropping it would leave a hole in that page's
sentence, and whether the page should still name it is a question for a human.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[2]
CATALOG = ("https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/"
           "WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Safari/605.1.15")
UNPUBLISHED = {"_site", "_UNPUBLISHED", "vendor", "venv", "node_modules", ".git",
               "_includes_backup", "_layouts_backup"}
CITATION = re.compile(r"include\s+course\s+number\s*=\s*(\d+)")

HEADER = """\
# Course titles, generated from the UVA SIS course catalog by scripts/courses/update.py.
# Do not edit by hand: `make courses ARGS=--write` rewrites this file.
# Read by _includes/course, which prints the title and drops the trailing units.

"""


def sis_opener():
    # PeopleSoft answers a first request with a 302 that sets a session cookie; a
    # client without a cookie jar is bounced to that redirect forever and concludes
    # the API needs a login. It does not.
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    opener.addheaders = [("User-Agent", UA)]
    return opener


def fetch_catalog(subject: str = "MATH") -> list[dict]:
    opener = sis_opener()

    def get(script: str, **params) -> dict:
        url = CATALOG + script + "?" + urllib.parse.urlencode(params)
        with opener.open(url, timeout=40) as r:
            return json.loads(r.read().decode("utf-8"))

    courses = []
    for c in get("IScript_SubjectCourses", institution="UVA01", subject=subject)["courses"]:
        if not c["catalog_nbr"].isdigit():        # 1001T and the like: transfer credit
            continue
        d = get("IScript_CatalogCourseDetails", institution="UVA01",
                course_id=c["crse_id"], effdt=c["effdt"],
                crse_offer_nbr=c["crse_offer_nbr"], use_catalog_print="Y")["course_details"]
        number = int(c["catalog_nbr"])
        courses.append({"number": number,
                        "name": f"{clean(d['course_title'])} ({units(d)})",
                        "graduate": number >= 5000})
    return sorted(courses, key=lambda c: c["number"])


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def units(d: dict) -> str:
    def fmt(x):
        return str(int(x)) if float(x) == int(x) else str(x)
    lo, hi = d["units_minimum"], d["units_maximum"]
    return fmt(lo) if lo == hi else f"{fmt(lo)} - {fmt(hi)}"


def read_existing(path: pathlib.Path) -> dict[int, dict]:
    """Parse the flat list this script (and its Lou's List predecessor) writes."""
    out: dict[int, dict] = {}
    entry: dict | None = None
    for line in path.read_text().splitlines():
        m = re.match(r"^(- |  )(\w+):\s*(.*)$", line)
        if not m:
            continue
        lead, key, value = m.groups()
        if lead == "- ":
            entry = {}
        if entry is None:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        entry[key] = clean(value)
        if key == "number":
            out[int(value)] = entry
    for number, e in out.items():
        e["number"] = number
        e["graduate"] = e.get("graduate") == "true"
    return out


def cited_numbers(site: pathlib.Path) -> dict[int, list[str]]:
    cited: dict[int, list[str]] = {}
    for path in site.rglob("*"):
        rel = path.relative_to(site)
        if (rel.parts[0] in UNPUBLISHED or any(part.startswith(".") for part in rel.parts)
                or path.suffix not in {".md", ".html"} or not path.is_file()):
            continue
        for n in CITATION.findall(path.read_text(errors="ignore")):
            cited.setdefault(int(n), [])
            if str(rel) not in cited[int(n)]:
                cited[int(n)].append(str(rel))
    return cited


def render(courses: list[dict]) -> str:
    def q(s: str) -> str:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    out = [HEADER]
    for c in courses:
        out.append(f"- name: {q(c['name'])}\n  number: {c['number']}\n")
        if c["graduate"]:
            out.append("  graduate: true\n")
        if c.get("sis_missing"):
            out.append("  sis_missing: true\n")
    return "".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--write", action="store_true", help="rewrite _data/courses.yml")
    p.add_argument("--site", default=str(REPO), help="repository root")
    args = p.parse_args()

    site = pathlib.Path(args.site)
    target = site / "_data" / "courses.yml"
    old = read_existing(target)
    cited = cited_numbers(site)
    new = {c["number"]: c for c in fetch_catalog()}

    for number in sorted(set(old) - set(new)):
        if number in cited:
            new[number] = {**old[number], "sis_missing": True}
    courses = [new[n] for n in sorted(new)]

    retitled = [(n, old[n]["name"], new[n]["name"]) for n in sorted(set(old) & set(new))
                if old[n]["name"] != new[n]["name"] and not new[n].get("sis_missing")]
    print(f"SIS lists {sum(not c.get('sis_missing') for c in courses)} MATH courses; "
          f"{target.relative_to(site)} has {len(old)}.")
    for n, a, b in retitled:
        print(f"  retitled  MATH {n}: {a}  ->  {b}")
    for n in sorted(set(new) - set(old)):
        print(f"  added     MATH {n}: {new[n]['name']}")
    for n in sorted(set(old) - set(new)):
        print(f"  dropped   MATH {n}: {old[n]['name']}  (not in SIS, cited nowhere)")
    for c in courses:
        if c.get("sis_missing"):
            print(f"  KEPT      MATH {c['number']}: {c['name']}  -- not in SIS, but cited by "
                  f"{', '.join(cited[c['number']])}; decide whether the page should still name it")
    for n in sorted(set(cited) - set(new)):
        print(f"  BROKEN    MATH {n} is cited by {', '.join(cited[n])} but is in neither "
              f"SIS nor the old file: the include prints nothing there")

    text = render(courses)
    if text == target.read_text():
        print("\nNo change.")
        return 0
    if not args.write:
        print("\n(dry run -- pass --write to rewrite the file)")
        return 0
    target.write_text(text)
    print(f"\nWrote {target.relative_to(site)}: {len(courses)} courses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Pull the public HoosList class schedule for one subject group and normalize it.

HoosList (hooslist.virginia.edu) replaced Lou's List; louslist.org now 301s to the
HoosList home page, losing the subject path, so every URL here targets HoosList
directly.

Every section is server-rendered into a `js-section-link` anchor carrying the whole
record in data-* attributes, so no login and no JS execution is needed. Rooms are the
one field the public view withholds ("Login Required"), which is why the sheet this
feeds carries no rooms -- see --room-note.

Usage:
    python3 scripts/schedule/hooslist_fetch.py --semester "Fall 2026" -o sections.json
    python3 scripts/schedule/hooslist_fetch.py --term 1268 --group Mathematics
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.request

BASE = "https://hooslist.virginia.edu"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) hooslist_fetch.py"

# Surnames the last-token rule gets wrong. Extend as new instructors appear; the
# script refuses to guess and reports anything unfamiliar that looks compound.
SURNAME_OVERRIDES = {
    "Fausto Navarro Cepeda": "Navarro Cepeda",
}

SEASON_DIGIT = {"spring": "2", "summer": "6", "fall": "8", "january": "1"}

DAY_CODES = {"Mo": "Mo", "Tu": "Tu", "We": "We", "Th": "Th", "Fr": "Fr",
             "Sa": "Sa", "Su": "Su"}


def term_code(semester: str) -> str:
    """'Fall 2026' -> '1268'. UVA term codes are 1 + YY + season digit."""
    m = re.match(r"\s*([A-Za-z]+)\s+(\d{4})\s*$", semester)
    if not m:
        raise SystemExit(f"cannot parse semester {semester!r}; use e.g. 'Fall 2026'")
    season, year = m.group(1).lower(), int(m.group(2))
    if season not in SEASON_DIGIT:
        raise SystemExit(f"unknown season {season!r}")
    return f"1{year % 100:02d}{SEASON_DIGIT[season]}"


def term_slug(semester: str) -> str:
    """'Fall 2026' -> 'f26'. The basename of the archival PDF."""
    m = re.match(r"\s*([A-Za-z]+)\s+(\d{4})\s*$", semester)
    if not m:
        raise SystemExit(f"cannot parse semester {semester!r}; use e.g. 'Fall 2026'")
    season, year = m.group(1).lower(), int(m.group(2))
    prefix = {"fall": "f", "spring": "s", "summer": "su", "january": "j"}[season]
    return f"{prefix}{year % 100:02d}"


def fetch(term: str, group: str) -> str:
    url = f"{BASE}/{term}/Group/{group}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        if r.status != 200:
            raise SystemExit(f"{url} returned HTTP {r.status}")
        return r.read().decode("utf-8", "replace")


def parse_attrs(anchor: str) -> dict:
    out = {}
    for m in re.finditer(r"""data-([A-Za-z_]+)=("|')(.*?)\2""", anchor, re.S):
        out[m.group(1).lower()] = html.unescape(m.group(3))
    return out


def norm_days(days: str) -> str:
    """'Tu|Th' -> 'TuTh'; 'Mo|We|Fr' -> 'MWF' (the sheet's own convention)."""
    parts = [p for p in days.split("|") if p]
    if parts == ["Mo", "We", "Fr"]:
        return "MWF"
    return "".join(DAY_CODES.get(p, p) for p in parts)


def norm_time(t: str) -> str:
    """'12:15 PM' -> '12:15'. The sheet drops the meridiem; evening classes are
    unambiguous in context and it buys a lot of horizontal room."""
    return re.sub(r"\s*(AM|PM)\s*$", "", t.strip())


def norm_meeting(m: dict) -> dict:
    days = norm_days(m.get("days") or "")
    start, end = norm_time(m.get("start") or ""), norm_time(m.get("end") or "")
    when = f"{days} {start}--{end}" if days and start else ""
    return {"days": days, "start": start, "end": end, "when": when,
            "date_range": m.get("dateRange") or "",
            "room": m.get("buildingAndRoom") or ""}


def norm_enrollment(raw: str) -> str:
    """'<span...>1 / 18</span> <span...>(9 / 18)</span>' -> '1/18 (9/18)'."""
    labels = re.findall(r"<span[^>]*>(.*?)</span>", raw, re.S)
    parts = [re.sub(r"\s*/\s*", "/", html.unescape(x)).strip() for x in labels]
    return " ".join(p for p in parts if p)


def surname(full: str, ambiguous: set[str]) -> str:
    """Last name as the sheet prints it, with a first initial only where two
    instructors share a surname (that is where 'W. Wang' / 'O. Wang' come from)."""
    full = full.strip()
    if full in ("", "-", "TBD"):
        return ""
    if full in SURNAME_OVERRIDES:
        last = SURNAME_OVERRIDES[full]
    else:
        last = full.split()[-1]
    if last in ambiguous:
        return f"{full.split()[0][0]}. {last}"
    return last


def collect(page: str) -> list[dict]:
    anchors = re.findall(r"""<a href="#"\s+class="js-section-link.*?>""", page, re.S)
    raw = [parse_attrs(a) for a in anchors]

    # A surname is ambiguous when two different full names share it.
    seen: dict[str, set[str]] = {}
    for r in raw:
        name = (r.get("instructors") or "").strip()
        if name in ("", "-", "TBD"):
            continue
        last = SURNAME_OVERRIDES.get(name, name.split()[-1])
        seen.setdefault(last, set()).add(name)
    ambiguous = {k for k, v in seen.items() if len(v) > 1}

    out = []
    for r in raw:
        meetings = [norm_meeting(m) for m in json.loads(r.get("meetings") or "[]")]
        meetings = [m for m in meetings if m["when"]]
        instructor = (r.get("instructors") or "").strip()
        out.append({
            "class_number": r.get("classnumber", ""),
            "subject": r.get("subject", ""),
            "catalog": r.get("catalog", ""),
            "section": r.get("sectioncode", ""),
            "title": r.get("title", ""),
            "topic": r.get("topic", ""),
            "component": r.get("component", ""),
            "credits": r.get("credits", ""),
            "units": r.get("credits", "").split()[0] if r.get("credits") else "",
            "status": r.get("status", ""),
            "seats": norm_enrollment(r.get("enrollment", "")),
            "waitlist": (r.get("waitlistcount") or "").strip(),
            "instructor_full": instructor,
            "instructor": surname(instructor, ambiguous),
            "dates": r.get("dates", ""),
            "session": r.get("session_long", ""),
            "combined": r.get("combined", ""),
            "meetings": meetings,
            "when": meetings[0]["when"] if meetings else "",
        })
    return out


def fetch_sections(semester: str | None = None, term: str | None = None,
                   group: str = "Mathematics") -> dict:
    """Fetch and normalize one subject group; returns the document written by -o."""
    code = term or term_code(semester)
    sections = collect(fetch(code, group))
    if not sections:
        raise SystemExit(f"no sections found for term {code} group {group}; check the "
                         "term code against https://hooslist.virginia.edu/ClassSchedule/")

    stamp = dt.datetime.now().astimezone()
    doc = {
        "term_code": code,
        "term": semester or "",
        "group": group,
        "source": f"{BASE}/{code}/Group/{group}",
        "fetched_at": stamp.isoformat(timespec="seconds"),
        "fetched_date": stamp.strftime("%Y-%m-%d"),
        "fetched_time": stamp.strftime("%H:%M %Z"),
        "section_count": len(sections),
        "sections": sections,
    }
    if semester:
        doc["term_slug"] = term_slug(semester)
    return doc


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--semester", help='e.g. "Fall 2026"')
    g.add_argument("--term", help="raw UVA term code, e.g. 1268")
    p.add_argument("--group", default="Mathematics", help="HoosList subject group")
    p.add_argument("-o", "--out", help="write JSON here (default: stdout)")
    p.add_argument("--room-note", action="store_true",
                   help="report how many sections expose a room (public view: none)")
    args = p.parse_args()

    doc = fetch_sections(args.semester, args.term, args.group)

    text = json.dumps(doc, indent=1, ensure_ascii=False)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text + "\n")
        print(f"{doc['section_count']} sections -> {args.out}  ({doc['fetched_time']})",
              file=sys.stderr)
    else:
        print(text)

    if args.room_note:
        with_room = sum(1 for s in doc["sections"] for m in s["meetings"] if m["room"])
        print(f"meetings exposing a room: {with_room} "
              "(0 is expected -- the public view withholds rooms)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

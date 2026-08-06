#!/usr/bin/env python3
"""Refresh the enrollment/instructor/meeting numbers in schedule.tex from a
hooslist_fetch.py dump, and report everything it could not do mechanically.

Sections are matched on class number, which is stable for the life of a term. Only
three cells are ever rewritten: the meeting time, the seat count, and the instructor.
The room cell is never written and is empty throughout the sheet -- rooms are not
public data and must not be added.

Anything needing judgment (new sections, cancelled sections, retitled courses,
split meeting patterns, unfamiliar instructor names) is reported, not applied.

Usage:
    python3 scripts/schedule/schedule_refresh.py --tex schedule.tex --data sections.json
    python3 scripts/schedule/schedule_refresh.py --tex schedule.tex --data sections.json --write
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# Components that get their own line in the body of the sheet. Special Session
# (0-unit exam nights) and Independent Study are collapsed into hand-written blocks
# at the end, so they are compared but never rewritten in place.
INLINE = {"Lecture", "Seminar", "Discussion"}

STAMP_RE = re.compile(r"(\\newcommand\{\\SnapshotStamp\}\{)(.*?)(\})")

# Too generic to identify a course; every listing has some of these.
STOPWORDS = {"the", "and", "for", "with", "new", "course", "mathematics", "math",
             "topics", "seminar", "introduction", "advanced", "elementary"}


def words(title: str) -> set[str]:
    return {w for w in re.findall(r"[A-Za-z]{4,}", title.lower())
            if w not in STOPWORDS}


def split_args(text: str, start: int, n: int):
    """Read n brace groups starting at text[start]; return (args, end_index)."""
    args, i = [], start
    for _ in range(n):
        if i >= len(text) or text[i] != "{":
            return None, start
        depth, j = 1, i + 1
        while j < len(text) and depth:
            if text[j] == "{" and text[j - 1] != "\\":
                depth += 1
            elif text[j] == "}" and text[j - 1] != "\\":
                depth -= 1
            j += 1
        args.append(text[i + 1:j - 1])
        i = j
    return args, i


def scan(tex: str):
    """Yield (macro, args, span) for every \\Sx and \\Dx line."""
    for m in re.finditer(r"\\(Sx|Dx)(?=\{)", tex):
        n = 6 if m.group(1) == "Sx" else 5
        args, end = split_args(tex, m.end(), n)
        if args is None:
            continue
        yield m.group(1), args, (m.start(), end)


def rebuild(macro: str, args: list[str]) -> str:
    return "\\" + macro + "".join("{" + a + "}" for a in args)


def instructor_cell(existing: str, name: str) -> tuple[str, str | None]:
    """Return (new cell, note). Hand-authored cells -- the seminar labels like
    'Probability (Gromoll)' -- are preserved as long as they still name the person."""
    new = name if name else r"\tbd"
    if existing.strip() == new:
        return existing, None
    if "(" in existing or "\\" in existing.replace(r"\tbd", ""):
        if name and name.split()[-1] in existing:
            return existing, None
        return existing, f"hand-written instructor cell {existing!r} vs HoosList {new!r}"
    return new, None


def refresh(tex: str, data: dict) -> tuple[str, list[str], list[str]]:
    """Return (new source, applied changes, items needing a human)."""
    by_num = {s["class_number"]: s for s in data["sections"]}

    changes, notes, seen = [], [], set()
    out, cursor = [], 0

    for macro, a, (s0, s1) in scan(tex):
        out.append(tex[cursor:s0])
        cursor = s1
        num = a[1].strip()
        if not num:                       # continuation row for a split meeting
            out.append(tex[s0:s1])
            continue
        sec = by_num.get(num)
        if sec is None:
            notes.append(f"DROPPED  {a[0] or '?':>4} class {num} is in the sheet but "
                         "not in HoosList (cancelled, or moved to another subject)")
            out.append(tex[s0:s1])
            continue
        seen.add(num)
        new = list(a)
        label = f"{sec['catalog']}-{sec['section']} ({num})"

        # meeting time: only when the section still has exactly one meeting pattern
        if len(sec["meetings"]) == 1 and sec["when"] and new[2].strip() != sec["when"]:
            changes.append(f"  time  {label}: {new[2]} -> {sec['when']}")
            new[2] = sec["when"]
        elif len(sec["meetings"]) > 1:
            pats = "; ".join(m["when"] for m in sec["meetings"])
            notes.append(f"SPLIT    {label} has {len(sec['meetings'])} meeting "
                         f"patterns ({pats}); left alone")

        # seats (\Sx only -- discussions inherit the lecture's count, so the sheet
        # deliberately leaves that cell empty)
        if macro == "Sx" and sec["seats"] and new[4].strip() != sec["seats"]:
            changes.append(f"  seats {label}: {new[4] or '(empty)'} -> {sec['seats']}")
            new[4] = sec["seats"]

        idx = 5 if macro == "Sx" else 4
        cell, note = instructor_cell(new[idx], sec["instructor"])
        if note:
            notes.append(f"INSTR    {label}: {note}")
        elif cell != new[idx]:
            changes.append(f"  instr {label}: {new[idx]} -> {cell}")
            new[idx] = cell

        out.append(rebuild(macro, new))

    out.append(tex[cursor:])
    result = "".join(out)

    # sections HoosList has that the sheet does not. The room argument stays empty:
    # the sheet carries no rooms.
    for sec in data["sections"]:
        if sec["class_number"] in seen or sec["component"] not in INLINE:
            continue
        macro = "Dx" if sec["component"] == "Discussion" else "Sx"
        line = (f"\\{macro}{{{sec['section']}}}{{{sec['class_number']}}}"
                f"{{{sec['when']}}}{{}}"
                + (f"{{{sec['seats']}}}" if macro == "Sx" else "")
                + "{" + (sec["instructor"] or r"\tbd") + "}")
        notes.append(f"NEW      MATH {sec['catalog']}-{sec['section']} "
                     f"\"{sec['title']}\" ({sec['credits']}) -- insert in catalog "
                     f"order:\n           {line}")

    # course headers: catch a genuinely retitled course. The sheet abbreviates
    # freely ("PDE and Applied Mathematics") and replaces the placeholder title of
    # a xx59 listing with its topic, so equality is the wrong test -- share one
    # substantive word with any of the title/topic candidates and it is the same
    # course.
    titles = {}
    for sec in data["sections"]:
        cands = {sec["title"]}
        if sec["topic"]:
            cands |= {sec["topic"], f"{sec['title']} {sec['topic']}"}
        titles.setdefault(sec["catalog"], set()).update(cands)
    for m in re.finditer(r"\\Ch(?=\{)", result):
        ch, _ = split_args(result, m.end(), 3)
        if not ch:
            continue
        cm = re.match(r"MATH (\d{4})", ch[0])
        if not cm:
            continue
        known = titles.get(cm.group(1), set())
        if known and not (words(ch[1]) & set().union(*(words(t) for t in known))):
            notes.append(f"TITLE    MATH {cm.group(1)}: sheet says {ch[1]!r}, "
                         f"HoosList says {sorted(known)}")

    # Kept short deliberately: the header is one line on a landscape page and a
    # longer phrasing wraps, orphaning the date.
    stamp = (f"manual HoosList snapshot, {data['fetched_date']} "
             f"{data['fetched_time']}")
    if STAMP_RE.search(result):
        old = STAMP_RE.search(result).group(2)
        result = STAMP_RE.sub(lambda m: m.group(1) + stamp + m.group(3), result, count=1)
        if old != stamp:
            changes.append(f"  stamp {old!r} -> {stamp!r}")
    else:
        notes.append(r"STAMP    no \newcommand{\SnapshotStamp}{...} line in the sheet; "
                     f"add one and put \\SnapshotStamp in the header. Value: {stamp}")

    return result, changes, notes


def report(data: dict, changes: list[str], notes: list[str]) -> None:
    print(f"HoosList {data['group']} {data.get('term') or data['term_code']} "
          f"({data['section_count']} sections), fetched {data['fetched_time']} "
          f"{data['fetched_date']}")
    print(f"\n{len(changes)} cell change(s):")
    print("\n".join(changes) if changes else "  (none -- the sheet is current)")
    if notes:
        print(f"\n{len(notes)} item(s) needing a human:")
        for n in notes:
            print("  " + n)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tex", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--write", action="store_true", help="apply changes in place")
    args = p.parse_args()

    data = json.load(open(args.data))
    result, changes, notes = refresh(open(args.tex).read(), data)
    report(data, changes, notes)

    if args.write:
        open(args.tex, "w").write(result)
        print(f"\nwrote {args.tex}")
    else:
        print("\n(dry run -- pass --write to apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

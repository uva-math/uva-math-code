#!/usr/bin/env python3
"""Refresh the enrollment/instructor/meeting numbers in schedule.tex from a
hooslist_fetch.py dump, and report everything it could not do mechanically.

Sections are matched on class number, which is stable for the life of a term. Three
cells are rewritten in place -- the meeting time, the seat count, and the instructor
-- and the sheet gains the rows HoosList has added and loses the ones it no longer
lists, so the PDF stays a faithful snapshot without hand editing. The room cell is
never written and is empty throughout the sheet -- rooms are not public data and
must not be added.

The few things a cell cannot express are still reported rather than guessed: a
retitled course, a section meeting at two different times, an unfamiliar instructor
name, and a new section whose topic block is ambiguous.

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


CH_RE = re.compile(r"^\\Ch\{MATH (\d{4})\}")
ROW_RE = re.compile(r"^\\(?:Sx|Dx)\{(\d+)\}")
NUM_RE = re.compile(r"^\\(?:Sx|Dx)\{[^}]*\}\{(\d+)\}")
CONT_RE = re.compile(r"^\\(?:Sx|Dx)\{[^}]*\}\{\s*\}")


DAY_ORDER = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def merge_meetings(meetings: list[dict]) -> str:
    """Fold patterns that share a time into one cell: HoosList lists 'We 2:00--3:15'
    and 'Mo 2:00--3:15' separately for what the sheet writes 'MoWe 2:00--3:15'.
    Return '' when the times differ, which no single cell can express."""
    times = {(m["start"], m["end"]) for m in meetings if m["start"]}
    if len(times) != 1 or not all(m["days"] for m in meetings):
        return ""
    days = set()
    for m in meetings:
        days |= ({"Mo", "We", "Fr"} if m["days"] == "MWF"
                 else set(re.findall(r"[A-Z][a-z]", m["days"])))
    order = [d for d in DAY_ORDER if d in days]
    if not order:
        return ""
    start, end = times.pop()
    return f"{'MWF' if order == ['Mo', 'We', 'Fr'] else ''.join(order)} {start}--{end}"


def section_line(sec: dict) -> str:
    """The sheet row for a section. The room argument stays empty: the sheet
    carries no rooms. `when` is only the first pattern, so a section split across
    days has to be folded the same way an existing row would be."""
    macro = "Dx" if sec["component"] == "Discussion" else "Sx"
    when = sec["when"] if len(sec["meetings"]) == 1 else merge_meetings(sec["meetings"])
    return (f"\\{macro}{{{sec['section']}}}{{{sec['class_number']}}}"
            f"{{{when or sec['when']}}}{{}}"
            + (f"{{{sec['seats']}}}" if macro == "Sx" else "")
            + "{" + (sec["instructor"] or r"\tbd") + "}")


def remove_sections(tex: str, dropped: list[str]) -> tuple[str, list[str]]:
    """Delete the rows for class numbers HoosList no longer lists, along with any
    continuation rows they carry, and any course header left with no rows."""
    lines, changes = tex.split("\n"), []
    keep, i = [], 0
    while i < len(lines):
        m = NUM_RE.match(lines[i])
        if m and m.group(1) in dropped:
            changes.append(f"  -row  class {m.group(1)}: {lines[i]}")
            i += 1
            while i < len(lines) and CONT_RE.match(lines[i]):
                i += 1
            continue
        keep.append(lines[i])
        i += 1

    lines, keep = keep, []
    for i, line in enumerate(lines):
        m = CH_RE.match(line)
        if m and not (i + 1 < len(lines) and ROW_RE.match(lines[i + 1])):
            changes.append(f"  -course MATH {m.group(1)}: no sections left")
            continue
        keep.append(line)

    return "\n".join(keep), changes


def insert_sections(tex: str, missing: list[dict]) -> tuple[str, list[str], list[str]]:
    """Add sections HoosList has that the sheet does not, in catalog and section
    order. Return (new source, applied changes, items needing a human).

    A section of a course already on the sheet goes into that course's block. A
    course the sheet has never carried gets a new block, which needs a later \\Ch
    to anchor it -- the tail of the sheet is hand-written prose and notes, so
    appending past the last block would land in the wrong place.
    """
    lines = tex.split("\n")
    changes, notes = [], []

    for sec in sorted(missing, key=lambda s: (s["catalog"], s["section"])):
        row = section_line(sec)
        label = f"MATH {sec['catalog']}-{sec['section']}"
        heads = [(i, m.group(1)) for i, l in enumerate(lines) if (m := CH_RE.match(l))]
        same = [i for i, cat in heads if cat == sec["catalog"]]

        # An xx59 topics number carries one block per topic, so the catalog number
        # alone does not identify the block; pick the one whose title shares a
        # substantive word with this section's topic.
        if len(same) > 1:
            want = words(sec["topic"] or sec["title"])
            best = max(len(want & words(lines[i])) for i in same)
            same = [i for i in same if len(want & words(lines[i])) == best] if best else same
            if len(same) > 1:
                notes.append(f"NEW      {label} \"{sec['topic'] or sec['title']}\" "
                             f"matches {len(same)} MATH {sec['catalog']} blocks; add "
                             f"it to the right one by hand:\n           {row}")
                continue
        hdr = same[0] if same else None

        if hdr is not None:
            end = hdr + 1
            while end < len(lines) and ROW_RE.match(lines[end]):
                end += 1
            at = next((i for i in range(hdr + 1, end)
                       if ROW_RE.match(lines[i]).group(1) > sec["section"]), end)
            changes.append(f"  +row  {label}: {row}")
        else:
            at = next((i for i, cat in heads if cat > sec["catalog"]), None)
            if at is None:
                notes.append(f"NEW      {label} \"{sec['title']}\" ({sec['credits']}) "
                             "sorts after every course on the sheet; add its block by "
                             f"hand:\n           {row}")
                continue
            credits = re.sub(r"\bUnits?\b", lambda m: m.group(0).lower(), sec["credits"])
            lines[at:at] = [f"\\Ch{{MATH {sec['catalog']}}}{{{sec['title']}}}"
                            f"{{{credits}}}", row, ""]
            changes.append(f"  +course {label} \"{sec['title']}\" ({credits})")
            continue

        lines.insert(at, row)

    return "\n".join(lines), changes, notes


def refresh(tex: str, data: dict) -> tuple[str, list[str], list[str]]:
    """Return (new source, applied changes, items needing a human)."""
    by_num = {s["class_number"]: s for s in data["sections"]}

    changes, notes, seen, dropped = [], [], set(), []
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
            dropped.append(num)
            out.append(tex[s0:s1])
            continue
        seen.add(num)
        new = list(a)
        label = f"{sec['catalog']}-{sec['section']} ({num})"

        # meeting time. Several patterns at one time are the same meeting split
        # across days, so they fold back into one cell; genuinely different times
        # cannot go in a one-line cell and are left for a human.
        when = sec["when"] if len(sec["meetings"]) == 1 else merge_meetings(sec["meetings"])
        if when and new[2].strip() != when:
            changes.append(f"  time  {label}: {new[2]} -> {when}")
            new[2] = when
        elif not when:
            pats = "; ".join(m["when"] for m in sec["meetings"])
            notes.append(f"SPLIT    {label} meets at {len(sec['meetings'])} different "
                         f"times ({pats}); left alone")

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

    # sections the sheet carries that HoosList no longer lists
    if dropped:
        result, removed = remove_sections(result, dropped)
        changes.extend(removed)

    # sections HoosList has that the sheet does not
    missing = [s for s in data["sections"]
               if s["class_number"] not in seen and s["component"] in INLINE]
    if missing:
        result, added, blocked = insert_sections(result, missing)
        changes.extend(added)
        notes.extend(blocked)

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

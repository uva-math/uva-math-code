#!/usr/bin/env python3
"""Compile schedule.tex, stage the archival per-term copies, and refresh the link
blocks that point at the sheet.

Three things happen here, in order:

  1. schedule.tex is checked for room data. Rooms are not public and must never
     appear in the sheet; every room argument has to be empty and \\PublicSchedule
     has to be defined, which is what makes the room macros expand to nothing.
  2. pdflatex runs in a scratch directory (so no .aux/.log lands in the repo) and
     the result is written to schedule.pdf plus the archival name, e.g. f26.pdf.
  3. Every

         <!-- term-schedule-pdf --> ... <!-- /term-schedule-pdf -->

     block on the site is rewritten. Pages link only at schedule.pdf, which always
     holds the current term, so a rollover needs no link edits; the rewrite is there
     to keep the visible term name and the HoosList term link honest.

Usage:
    python3 scripts/schedule/schedule_build.py
    python3 scripts/schedule/schedule_build.py --semester "Spring 2027"
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from hooslist_fetch import term_code, term_slug          # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]

BLOCK = re.compile(r"(<!-- term-schedule-pdf -->)(.*?)(<!-- /term-schedule-pdf -->)", re.S)
SEMESTER_RE = re.compile(r"UVA Mathematics --- ([A-Z][a-z]+ \d{4})")

TEMPLATE = """
<p class="mt-3"><a href="{{{{ site.url }}}}/schedule.pdf"><b>{semester} Mathematics class schedule (PDF)</b></a>
&mdash; every Mathematics section on two printable pages: meeting times, enrollment,
and instructors. This is a manual snapshot of
<a href="https://hooslist.virginia.edu/{term}/Group/Mathematics">HoosList</a>; the date and
time it was taken are printed in the header of the sheet.</p>

<p><b>The PDF is a print-only convenience sheet.</b> For an accessible version, and for
live enrollment numbers, use
<a href="https://hooslist.virginia.edu/{term}/Group/Mathematics">HoosList</a> or
<a href="https://sisuva.admin.virginia.edu/ihprd/signon.html">SIS</a>, which work with
screen readers and can be resized.</p>
"""

BODY_MARK = "\\begin{document}"

# \Sx takes six arguments and \Dx five, the room fourth in both; \Room and \GridRoom
# take the room alone. The arguments are brace-matched rather than pattern-matched so
# that a row the checker cannot read is an error, never a pass -- see assert_room_free.
ROW_ARITY = {"Sx": 6, "Dx": 5}
ROOM_ARG = 3
ROOM_MACROS = ("GridRoom", "Room")


def _group(text: str, i: int):
    """Brace-match one {...} starting at text[i]; return (inner, end) or None."""
    if i >= len(text) or text[i] != "{":
        return None
    depth, j = 1, i + 1
    while j < len(text) and depth:
        if text[j] == "\\":
            j += 2
            continue
        depth += (text[j] == "{") - (text[j] == "}")
        j += 1
    return (text[i + 1:j - 1], j) if not depth else None


def _args(text: str, i: int, n: int):
    """Read n brace groups from text[i], tolerating whitespace between them."""
    out = []
    for _ in range(n):
        while i < len(text) and text[i] in " \t\r\n":
            i += 1
        got = _group(text, i)
        if got is None:
            return None
        arg, i = got
        out.append(arg)
    return out


def detect_semester(tex: str) -> str:
    """Read the term off the sheet's own printed header."""
    hits = SEMESTER_RE.findall(tex)
    body = [h for h in hits[1:]] or hits
    if not body:
        raise SystemExit("cannot find 'UVA Mathematics --- <Season> <Year>' in the "
                         "sheet header; pass --semester")
    if len(set(body)) > 1:
        raise SystemExit(f"the sheet names more than one term {sorted(set(body))}; "
                         "make the header comment and the printed header agree")
    if hits[0] != body[0]:
        raise SystemExit(f"header comment says {hits[0]!r} but the printed header says "
                         f"{body[0]!r}; make them agree")
    return body[0]


def assert_room_free(tex: str, path: pathlib.Path) -> None:
    """Refuse to publish a sheet carrying room assignments.

    Fails closed: a row whose arguments cannot be read is an error, because a checker
    that silently skips what it cannot parse would clear exactly the rows most likely
    to have been pasted in from a room-bearing working copy.
    """
    if "\\def\\PublicSchedule" not in tex:
        raise SystemExit(f"{path} does not define \\PublicSchedule; the room macros "
                         "would typeset their argument")
    if BODY_MARK not in tex:
        raise SystemExit(f"{path} has no {BODY_MARK}; refusing to guess where the "
                         "sheet body starts")
    body = tex.split(BODY_MARK, 1)[1]

    def bad(what: str, where: int) -> str:
        line = body.count("\n", 0, where) + tex.count("\n", 0, tex.index(BODY_MARK)) + 1
        return f"{path}:{line}: {what}"

    for m in re.finditer(r"\\(Sx|Dx)\s*(?=\{)", body):
        args = _args(body, m.end(), ROW_ARITY[m.group(1)])
        if args is None:
            raise SystemExit(bad(f"cannot read the arguments of \\{m.group(1)}; the "
                                 "room check will not clear a row it cannot parse",
                                 m.start()))
        if args[ROOM_ARG].strip():
            raise SystemExit(bad(f"\\{m.group(1)} carries a room assignment "
                                 f"{args[ROOM_ARG]!r}; rooms are not public data",
                                 m.start()))

    for name in ROOM_MACROS:
        for m in re.finditer(rf"\\{name}\s*(?=\{{)", body):
            args = _args(body, m.end(), 1)
            if args is None:
                raise SystemExit(bad(f"cannot read the argument of \\{name}", m.start()))
            if args[0].strip():
                raise SystemExit(bad(f"\\{name} carries a room assignment "
                                     f"{args[0]!r}; rooms are not public data",
                                     m.start()))


# Rooms as they are actually written: a building abbreviation or name followed by a
# number. Checked against the *rendered* text, which is the only place that catches a
# room typed as free text somewhere the argument-level check does not look.
PDF_ROOM = re.compile(
    r"\b(?:NCH|KER|MEC|OLS|RIC|CLK|GIL|WIL|MON|PHY|CHM|NAU|DEL|THN|CAB|BRN)\s*-?\s*\d{2,4}\b"
    r"|\b(?:Kerchof|New Cabell|Olsson|Gilmer|Thornton|Monroe Hall|Nau Hall|Rice Hall|"
    r"Clark Hall)\b")

# The public build prints this in place of the building legend. Its absence means the
# sheet was compiled without \PublicSchedule, i.e. as the room-bearing variant.
PUBLIC_MARK = "rooms omitted"


def pdf_text(pdf: bytes) -> str | None:
    """Rendered text of a PDF, or None if pdftotext is unavailable."""
    try:
        r = subprocess.run(["pdftotext", "-", "-"], input=pdf,
                           capture_output=True, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def assert_pdf_room_free(pdf: bytes, what: str) -> None:
    """Refuse a rendered sheet that shows rooms.

    The source check reads the arguments the sheet is supposed to use. This one reads
    what a reader actually sees, so it also catches a room written as ordinary text
    into the weekly grid or a course header -- fields public mode does not discard.
    """
    text = pdf_text(pdf)
    if text is None:
        print(f"warning: pdftotext unavailable, so {what} was not checked for rooms "
              "in its rendered output", file=sys.stderr)
        return
    hit = PDF_ROOM.search(text)
    if hit:
        raise SystemExit(f"{what} shows a room in its rendered output: {hit.group(0)!r}\n"
                         "rooms are not public data and must not be published")
    if PUBLIC_MARK not in text:
        raise SystemExit(f"{what} does not print {PUBLIC_MARK!r} in its header, so it "
                         "was not built as the public sheet; refusing to publish it")


def build_pdf(tex_path: pathlib.Path) -> tuple[bytes, int]:
    """Compile in a scratch directory; return (pdf bytes, page count)."""
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp)
        r = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", str(out), str(tex_path)],
            capture_output=True, text=True, cwd=tex_path.parent)
        pdf = out / (tex_path.stem + ".pdf")
        log = out / (tex_path.stem + ".log")
        if r.returncode != 0 or not pdf.is_file():
            tail = (log.read_text(errors="replace").splitlines()[-25:]
                    if log.is_file() else r.stdout.splitlines()[-25:])
            raise SystemExit("pdflatex failed:\n  " + "\n  ".join(tail))
        # pdflatex hard-wraps the log at 79 columns, so the "Output written on
        # <long temp path> (2 pages, N bytes)" line arrives split; flatten first.
        flat = log.read_text(errors="replace").replace("\n", "")
        m = re.search(r"Output written on .*?\((\d+) pages?,", flat)
        return pdf.read_bytes(), int(m.group(1)) if m else 0


def rewrite_blocks(site: pathlib.Path, semester: str, term: str) -> list[pathlib.Path]:
    body = TEMPLATE.format(semester=semester, term=term)
    touched = []
    for path in sorted(site.rglob("*")):
        if path.suffix not in (".md", ".html") or not path.is_file():
            continue
        if any(part in ("_site", "venv", "vendor", "node_modules") for part in path.parts):
            continue
        text = path.read_text(errors="replace")
        if "<!-- term-schedule-pdf -->" not in text:
            continue
        # A rendered page, not documentation that merely quotes the markers.
        if not text.startswith("---"):
            continue
        new = BLOCK.sub(lambda m: m.group(1) + body + m.group(3), text)
        if new != text:
            path.write_text(new)
            touched.append(path.relative_to(site))
    return touched


def build_and_stage(site: pathlib.Path, semester: str | None = None) -> int:
    """Compile the sheet, write both PDF names and the archival source, relink."""
    tex_path = site / "schedule.tex"
    if not (site / "_config.yml").is_file():
        raise SystemExit(f"{site} does not look like the website repo")
    if not tex_path.is_file():
        raise SystemExit(f"no such file: {tex_path}")

    tex = tex_path.read_text()
    assert_room_free(tex, tex_path)
    semester = semester or detect_semester(tex)
    term, slug = term_code(semester), term_slug(semester)

    pdf, pages = build_pdf(tex_path)
    assert_pdf_room_free(pdf, "the sheet just built from schedule.tex")
    if pages != 2:
        print(f"warning: the sheet came out {pages} pages, not 2", file=sys.stderr)
    for name in ("schedule.pdf", f"{slug}.pdf"):
        (site / name).write_bytes(pdf)
        print(f"wrote  -> {name}  ({len(pdf)} bytes, {pages} pages)")
    (site / f"{slug}.tex").write_text(tex)
    print(f"wrote  -> {slug}.tex")

    touched = rewrite_blocks(site, semester, term)
    print(f"\n{len(touched)} page(s) rewritten:" if touched
          else "\nno page needed rewriting (term name already current)")
    for t in touched:
        print("  " + str(t))
    print(f"\nlive after push:\n  https://math.virginia.edu/schedule.pdf"
          f"\n  https://math.virginia.edu/{slug}.pdf")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--semester", help='override the term read off the sheet, e.g. "Spring 2027"')
    p.add_argument("--site", default=str(REPO), help="repository root")
    args = p.parse_args()
    return build_and_stage(pathlib.Path(args.site), args.semester)


if __name__ == "__main__":
    sys.exit(main())

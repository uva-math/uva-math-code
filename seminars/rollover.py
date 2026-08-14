#!/usr/bin/env python3
"""Roll the seminar pages over to a new academic year.

    python3 seminars/rollover.py 2025-26 2026-27          # report, touch nothing
    python3 seminars/rollover.py 2025-26 2026-27 --write  # apply

For each seminar it creates <sem><new>.html from <sem><old>.html, fixing the
title, permalink and the show_from/show_to window, then adds the new year to
the archive line of every page in the seminar directory. Both steps are
idempotent: a page that already lists the new year is left alone, and an
existing archive page is never overwritten.

This replaces update_sems_year.zsh, which hardcoded its year pair, copied each
new archive page without rewriting its title, permalink or date window (a
trailing space after each line-continuation backslash split that sed call into
separate commands; it errored to stderr but still exited 0), and globbed only
*.html, so it never reached the Operator Theory main page,
seminars/sotoa/sotoa.md. Its archive-link pass did work.
"""
import pathlib
import re
import sys

SEMS = ["algebra", "colloq", "diffeq", "galois", "geometry", "gradsem",
        "mathclub", "mathphys", "ntsem", "probability", "sotoa", "topology"]
ROOT = pathlib.Path(__file__).resolve().parent


def read(path):
    # newline="" keeps CRLF intact; a few old archive pages still use it, and
    # rewriting them to LF would bury the one real edit in a whole-file diff.
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def slug(year):
    """'2026-27' -> '26_27', the archive filename infix."""
    m = re.fullmatch(r"(\d{4})-(\d{2})", year)
    if not m:
        raise SystemExit(f"bad academic year {year!r}; use e.g. 2026-27")
    return f"{m.group(1)[2:]}_{m.group(2)}"


def add_year(text, sem, new):
    """Insert the new archive link just after the 'upcoming' link.

    Returns the text and one of 'current', 'added' or 'no anchor'. The caller
    reports 'no anchor' rather than passing over it, so a page whose archive
    line this cannot parse is never skipped in silence.
    """
    if f"/seminars/{sem}/{new}/" in text:
        return text, "current"
    # Some old archive pages wrap the line, leaving the pipe that follows the
    # 'upcoming' link at the start of the next line, so the gap is not a space.
    anchor = re.compile(rf'<a href="/seminars/{re.escape(sem)}/">upcoming</a>\s*\|')
    if not anchor.search(text):
        return text, "no anchor"
    link = f'<a href="/seminars/{sem}/{new}/">{new}</a> |'
    return anchor.sub(lambda m: f"{m.group(0)} {link}", text, count=1), "added"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        raise SystemExit(__doc__)
    old, new = args
    do_write = "--write" in sys.argv
    # An academic year runs 1 July to 1 July, so its window starts in the first
    # of the two calendar years the label names.
    old_from, new_from = int(old[:4]), int(new[:4])
    log = []

    for sem in SEMS:
        d = ROOT / sem
        src, dst = d / f"{sem}{slug(old)}.html", d / f"{sem}{slug(new)}.html"
        if not src.exists():
            log.append(("NO SOURCE", src))
        elif dst.exists():
            log.append(("exists, kept", dst))
        else:
            t, _ = add_year(read(src), sem, new)
            t = re.sub(rf"^(title:.*){re.escape(old)}\s*$", rf"\g<1>{new}", t, flags=re.M)
            t = re.sub(rf"^permalink: /seminars/{sem}/{re.escape(old)}/\s*$",
                       f"permalink: /seminars/{sem}/{new}/", t, flags=re.M)
            t = t.replace(f"show_from='1 July {old_from}'", f"show_from='1 July {new_from}'")
            t = t.replace(f"show_to='1 July {old_from + 1}'", f"show_to='1 July {new_from + 1}'")
            log.append(("CREATE", dst))
            if do_write:
                write(dst, t)

        for f in sorted(d.iterdir()):
            if f.suffix not in (".html", ".md") or f.name == dst.name:
                continue
            t, status = add_year(read(f), sem, new)
            if status == "added":
                log.append(("add year", f))
                if do_write:
                    write(f, t)
            elif status == "no anchor" and "upcoming</a>" in t:
                log.append(("NO ANCHOR", f))

    for kind, path in log:
        print(f"{kind:14s} {path.relative_to(ROOT)}")
    created = sum(1 for k, _ in log if k == "CREATE")
    touched = sum(1 for k, _ in log if k == "add year")
    missed = sum(1 for k, _ in log if k == "NO ANCHOR")
    print(f"\n{'APPLIED' if do_write else 'DRY RUN'}: {created} new archive pages, "
          f"{touched} pages given the new year, "
          f"{missed} pages whose archive line could not be parsed")


if __name__ == "__main__":
    main()

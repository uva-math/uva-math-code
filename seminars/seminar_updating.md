# Rolling the seminar pages over to a new academic year

Each seminar has one live page showing upcoming talks, plus one archive page per
academic year. Without the yearly rollover the previous year's archive keeps
collecting new talks and the new year never appears in the archive list.

## Active seminars

`algebra`, `colloq` (Colloquium), `diffeq` (Harmonic Analysis and PDE), `galois`
(Galois-Grothendieck), `geometry`, `gradsem` (Graduate Students), `mathclub`
(Undergraduate Math Club), `mathphys` (Mathematical Physics), `ntsem`
(Ramanujan-Serre, number theory), `probability`, `sotoa` (Operator Theory) and
`topology`.

`ancommons` (Analysis Commons) is discontinued — its archives stop at 2021-22 —
and is deliberately left out of the rollover.

## Running it

From the repository root, giving the old and the new academic year:

```bash
python3 seminars/rollover.py 2025-26 2026-27          # report, touch nothing
python3 seminars/rollover.py 2025-26 2026-27 --write  # apply
```

For each seminar this creates `<sem>26_27.html` from `<sem>25_26.html`, fixing
the `title`, the `permalink` and the `show_from`/`show_to` window, then adds the
new year to the archive line of every page in the seminar directory.

Both steps are idempotent, so a re-run is safe: a page that already lists the new
year is skipped, and an existing archive page is never overwritten. A dry run
that reports `0 new archive pages, 0 pages given the new year` means the rollover
is already done.

## What to check afterwards

Build the site and confirm, on a few seminars:

- the archive line lists the new year first, right after `upcoming`;
- `/seminars/<sem>/<new year>/` resolves, and so does the `upcoming` link;
- the new archive page's window is 1 July of the first year to 1 July of the
  second;
- the previous year's page still lists its own talks and has not been
  overwritten.

Then update the **Last done** line for this item in
[`SEASONAL.md`](../SEASONAL.md).

## Notes

Some seminars carry very old archives — `mathphys` goes back to 1999-00 — and
`algebra` has a separate `algebra_old.html` covering 2002-07. These are ordinary
pages in the seminar directory, so they pick up the new archive link like any
other.

The archive line comes in more than one shape. Most are a single long line; some
wrap, and a few old pages put the pipe that follows the `upcoming` link at the
start of the next line. The script tolerates any whitespace there. If it still
cannot parse a page's archive line it prints `NO ANCHOR` for that file and counts
it in the summary, so a page is never skipped in silence — which is how
`colloq/colloq09_10.md` quietly missed the 2025-26 rollover.

This replaces `update_sems_year.zsh`, which was removed in August 2026. It
hardcoded the year pair it was last run with, and a trailing space after each
line-continuation backslash split its `sed` invocation into separate commands, so
each new archive page was copied but kept the previous year's title, permalink
and date window — and the script still exited 0. It also globbed only `*.html`,
so it never reached `sotoa/sotoa.md`. Its archive-link pass did work.

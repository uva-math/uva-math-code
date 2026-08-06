---
name: uva-class-schedule
description: Refresh the printable UVA Mathematics term class-schedule sheet (schedule.pdf / schedule.tex) from HoosList, recompile it, and restage the archival per-term copy. Use whenever Leonid asks to update, refresh, recompile, or repost the class schedule / course schedule sheet, to pull current enrollment or instructor assignments from HoosList (or Lou's List, which no longer exists), or to roll the sheet over to a new semester. - Trigger phrases: update the class schedule, refresh the schedule PDF, new enrollment numbers, pull from hooslist, louslist, repost the schedule, f26.pdf, schedule.pdf, math.virginia.edu schedule, roll the schedule to spring.
---

# UVA Mathematics term class-schedule sheet

A two-page landscape sheet listing every MATH section for a term: meeting time,
class number, enrollment, instructor. It lives in this repository as LaTeX, builds
with one `pdflatex` pass and no external files, and is linked from five pages.

**Lou's List is gone.** `louslist.org` now 301-redirects to the HoosList home page and
drops the subject path, so any old URL silently lands on a generic landing page.
Everything here targets `hooslist.virginia.edu` directly.

## Files

| What | Path |
|---|---|
| Sheet source (the source of record) | `schedule.tex` |
| Published PDF, always the current term | `schedule.pdf` |
| Archival per-term copies | `f26.pdf`, `f26.tex` (`s27`, `f27`, … later) |
| End-to-end updater | `scripts/schedule/update.py` |
| HoosList fetch | `scripts/schedule/hooslist_fetch.py` |
| Cell refresh | `scripts/schedule/schedule_refresh.py` |
| Compile, stage, relink | `scripts/schedule/schedule_build.py` |

Published URLs: **`https://math.virginia.edu/schedule.pdf`** is what every page links
to and always holds the current term; **`https://math.virginia.edu/f26.pdf`** is the
archival per-term copy.

## The update run

One command. A bare run fetches and reports without touching anything; `--write`
applies the cells it can decide, recompiles the PDF, rewrites the archival copies,
and refreshes the link blocks.

```bash
python3 scripts/schedule/update.py             # report only
python3 scripts/schedule/update.py --write     # apply, rebuild, restage
```

`make schedule` and `make schedule ARGS=--write` do the same thing.

There is also a **daily refresh on commit**. `scripts/schedule/post-commit` runs the
full update on your first commit of each day and commits the result *separately*, so it
never lands inside an unrelated commit. It does not push — the refresh goes out with
your next push. If the only thing that moved is the snapshot stamp, it rolls the sheet
back rather than committing a fresh 200KB PDF for no change in the data. Anything the
refresh could not decide is printed with a `NEEDS A HUMAN` prefix, so watch for that
after a commit. (`SPLIT` is not in that list — MATH 2559-200 is permanently split and
would cry wolf every single day.)

It **skips entirely if `schedule.tex`, either archival copy, or any of the five link
pages has uncommitted changes**, and says so. This is the important safety property:
everything the hook does works on the working tree, so running over a half-finished
edit would either publish that draft under a commit message claiming it is a HoosList
refresh, or destroy it in the rollback. Skipping does not burn the day's slot — it runs
on your next commit once the tree is clean. It also skips on a detached HEAD, where the
commit would be orphaned.

Because it hangs off commits, the sheet is only as current as your commit habit; a
refresh that runs whether or not you commit would need a launchd job instead.

Always read the dry-run report first — the `--write` run applies only the mechanical
cells and reports the rest identically, but a `NEW`, `DROPPED`, or `TITLE` line means
the sheet needs hand editing that no flag will do for you.

Then commit and push — Leonid has said to push without asking. The push is what makes
it live (~5 minutes).

Confirm afterwards that the sheet is still two pages (the build prints the count and
warns if it is not) and that the header stamp did not wrap onto a second line:

```bash
pdftotext -f 1 -l 1 -layout schedule.pdf - | head -2
```

The header is tight. If a longer stamp ever wraps, shorten the phrasing in
`schedule_refresh.py` rather than letting the date orphan.

## Rooms are the thing to be careful about

**The sheet carries no rooms and must never carry any.** Room assignments are not
public data; the public HoosList view reports every room as "Login Required", and the
only way to obtain them is a logged-in SIS pull. Every room argument in `schedule.tex`
is empty, `\PublicSchedule` is defined so the room macros expand to nothing, and the
header prints "rooms omitted".

There are two independent checks, because either one alone has a blind spot.

**On the source.** `assert_room_free` refuses if `\PublicSchedule` is missing or if any
room argument is non-empty. It brace-matches the `\Sx`/`\Dx` arguments rather than
pattern-matching them, so a row it cannot read is an error rather than a pass — a
checker that skipped what it could not parse would clear exactly the rows most likely
to have been pasted in from a room-bearing copy.

**On the rendered PDF.** `assert_pdf_room_free` reads the built sheet back with
`pdftotext` and refuses if it shows anything shaped like a room, or if the header does
not say `rooms omitted`. This is the check that matters, because the source check only
inspects the fields public mode is supposed to discard: a room typed as ordinary text
into the weekly grid or a course header is invisible to it and lands in the PDF anyway.
It also catches a PDF compiled from the private room-bearing variant.

Do not work around either, and do not add rooms.

The same check runs as a **pre-commit hook**, against the staged content, because a
sheet can be hand-edited and committed without ever being built:

```bash
ln -sf ../../scripts/schedule/pre-commit  .git/hooks/pre-commit
ln -sf ../../scripts/schedule/post-commit .git/hooks/post-commit
```

It exits immediately unless a staged file both looks like a schedule sheet by name and
proves to be one by content, so it costs nothing on an unrelated commit. It checks
staged **PDFs** as well as sources — the PDF is the artifact actually served, and a
room-bearing PDF can otherwise be committed alongside a perfectly clean `.tex`. Hooks
are not cloned, so both need installing once per working copy.

## What the refresh decides and what it reports

Sections match on **class number**, stable for the life of a term. Three cells get
rewritten: meeting time, seat count, instructor. Everything else is reported:

- `NEW` — a section HoosList has that the sheet lacks. The report prints a
  ready-to-paste `\Sx`/`\Dx` line; insert it in catalog order.
- `DROPPED` — a section in the sheet that HoosList no longer lists (cancelled).
- `SPLIT` — a section whose meeting pattern broke into several rows. MATH 2559-200 is
  permanently in this state and is expected in every run.
- `TITLE` — a course whose name no longer shares a substantive word with HoosList. The
  sheet abbreviates freely ("PDE and Applied Mathematics") and substitutes the topic
  for the placeholder title of `xx59` listings, so this fires only on a genuine retitle.
- `INSTR` — a hand-authored instructor cell, i.e. the seminar labels like
  `Probability (Gromoll)`. Preserved as long as it still names the right person.

The independent-study block (4900, 4993, 5896, 8998–9999) and the 0-unit evening
exam-session block are hand-collapsed prose, not generated. Compare them against the
fetch by hand when a term is new; mid-term they rarely move.

Waitlist counts are deliberately omitted from the sheet — too volatile to print.

## Instructor names

The sheet prints surnames. `hooslist_fetch.py` derives them from HoosList's full names
and adds a first initial only where two people share a surname — that is where
`W. Wang` and `O. Wang` come from, automatically. Compound surnames the last-token rule
gets wrong live in `SURNAME_OVERRIDES` at the top of the script (currently
`Fausto Navarro Cepeda → Navarro Cepeda`). Add to it when a new one appears; do not let
the script guess.

## Rolling over to a new term

1. Edit `schedule.tex`: the term in the header comment **and** in the printed header
   (`UVA Mathematics --- Spring 2027`) — the build refuses if the two disagree — plus
   the term dates. Everything downstream reads the term off that printed header, so the
   term code (`1272`) and archival slug (`s27`) are derived, not configured.
2. Most `\Sx` lines will be `NEW`, since class numbers change every term. Building the
   body is a fresh pass, not a refresh; the dry-run report is the checklist.
3. Run the updater. It writes the new `s27.pdf` / `s27.tex` alongside `schedule.pdf`
   and rewrites the term name and HoosList link in every link block, so no page needs
   editing — they all point at the stable `schedule.pdf`.
4. Refresh the graduate weekly grid and its clash list at the end of the sheet by hand;
   nothing generates those.

## Where it is linked

Five pages carry a `<!-- term-schedule-pdf -->` block, all rewritten by the build:

- `undergraduate/degree_requirements.md` → /undergraduate/requirements/
- `undergraduate/undergraduate_main_page.md` → /undergraduate/
- `undergraduate/all_courses.md` → /courses/
- `undergraduate/undergraduate_courses.html` → /courses/undergrad/
- `graduate/graduate_courses.html` → /courses/graduate/

Never hand-edit inside those markers — the next build overwrites the body. Headings and
surrounding prose go outside them.

The rewrite claims any file that has YAML front matter and contains the **complete**
marker pair, and it descends into `.claude/` as readily as into the site pages. So a
complete pair must never appear anywhere but those five pages — this file included.
Documentation quotes the opening marker on its own, which is the only reason this file
survives a build; paste a full example block in here and the next run silently eats it.

The block says in as many words that the PDF is a print-only convenience sheet and
sends anyone who needs an accessible version to HoosList or SIS. A two-page 8pt
landscape sheet of `\makebox` columns is not screen-reader material and will not become
so; the accessible route is the live system, and the link text has to say that. Keep
that sentence in `TEMPLATE` in `schedule_build.py` through every rollover.

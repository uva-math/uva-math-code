# Seasonal maintenance registry

Pages on this site carry dates that silently expire. Nothing breaks when they do — the
page just keeps serving last year's information, which is worse than an error because
nobody notices. This file lists every recurring item, when it comes due, and what has to
be verified.

**If you are an agent working in this repository between July and October, read this file
and tell Leo which items are due.** Do not perform a rollover unless asked; the point of
the registry is the reminder, not the automation.

When an item is refreshed, update its **Last done** line in the same commit.

---

## Seminar academic-year rollover

**Due:** every August, before fall classes begin.
**Last done:** August 2026 (for 2026-27).

Each seminar has one live page plus one archive page per academic year. Without the
rollover, the previous year's archive keeps collecting new talks and the new year never
appears in the archive list.

The procedure is in [`seminars/seminar_updating.md`](seminars/seminar_updating.md). It now
takes the old and the new year as arguments — `python3 seminars/rollover.py 2026-27
2027-28` — so there is no year string left to bump. It reports by default and applies with
`--write`, and it is idempotent, so a re-run is safe. It also reports any page whose archive
line it cannot parse, instead of passing over it. The old `seminars/update_sems_year.zsh` was
removed in August 2026: it hardcoded its year pair and, because of a trailing space after each
line-continuation backslash, copied each new archive page without rewriting its title,
permalink or date window — while still exiting 0.

Verify afterwards that each seminar's main page lists the new year first in its archive
line, that `show_from` and `show_to` bracket the correct July-to-July window, and that the
"upcoming" link still resolves.

---

## Seminar organizers, times and rooms

**Due:** every August, once the seminars settle their slots for the fall.
**Last done:** never as a sweep; the entries in
[`_data/seminars.yml`](_data/seminars.yml) drift one seminar at a time.

Each entry in `_data/seminars.yml` carries a `contact` list of computing IDs and a
`regular_times` string holding the day, the time and the **room**. Both go stale
silently: a departed organizer stays listed because nothing in the build checks that the
ID still resolves to a current person, and a room changes without anyone editing the file.
The August 2026 audit found three dead contacts (`dku8jc` Slonim, gone 2023; `pfy7cf`
Shapiro, postdoc ended 2026; `wbt4qn` Lu, moved to `_UNPUBLISHED`) and a
`regular_times` still labelled "(Spring 2026)".

**Ask the organizers; do not copy HoosList.** The rooms are visible on HoosList, but only
to a logged-in session: `data-location` reads `Login Required` for every section when
`scripts/schedule/hooslist_fetch.py` runs logged out, and carries the real room when the
same fetch runs against a live HoosList login. That is worth knowing, and it is still not
the source for this page. What HoosList shows is the **registrar's booking for the
MATH 9xxx course**, which is routinely longer than the talk and can sit in a room the
seminar does not actually use — in August 2026 it gave Operator Theory a 3:30 start
against the seminar's real 3:45, and a 3:30–6:00 block for Galois-Grothendieck. Treat a
HoosList/`seminars.yml` disagreement as a **question for the organizer**, never as a
correction to apply. Mail all faculty, postdocs and the graduate-seminar student
organizers the current listing, ask each seminar to confirm organizers, day, time and
room, and edit only on an answer.

Check every `contact` ID against `_departmentpeople/`: an ID under `recent-postdocs/`,
`emeriti/` or `_UNPUBLISHED/`, or one with no file at all, is a stale organizer.

**Retiring a seminar.** `ancommons` (Analysis Commons) was retired in August 2026. The way
to do it is `defunct: true` on its `_data/seminars.yml` entry, **not** deleting the entry
or the pages. The archive pages render their title and pull their past talks through that
entry's `google_cal_id`, so removing it blanks the archives it is meant to preserve.
`defunct` drops the seminar from the "List of seminars" and from the week-view calendar in
`_includes/seminar_main_page.html`; `published_in_nav: false` keeps it out of the navbar.
Blank the seminar's slot in the calendar arrays in `_includes/cal_main.js` and
`kiosk/kiosk.md` by replacing the id with `"empty@virginia.edu"` — those arrays are
positional, so deleting a line shifts every seminar after it.

---

## Competitions page

**Due:** every August, before the Putnam registration window opens in September.
**Last done:** August 2026.

[`undergraduate/competitions.md`](undergraduate/competitions.md) is entirely composed of
one-year dates. Every entry has to be re-checked against its primary source, not against
last year's copy of this page:

| Item | Source |
|---|---|
| Putnam date, format, registration window | <https://maa.org/putnam/> (blocks automated fetching; a peer department's Putnam page works as a cross-check) |
| MCM/ICM contest window, fee, team size | <https://www.contest.comap.com/undergraduate/contests/mcm/instructions.html> |
| AWM Student Essay Contest | <https://awm-math.org/awards/student-essay-contest/> |
| USPROC deadlines | <https://www.causeweb.org/usproc/> (serves a bad TLS chain; `curl -k` if a fetch tool refuses it) |
| AWM Schafer Prize nomination window | <https://awm-math.org/awards/schafer-prize-for-undergraduates/> |
| JMM poster session deadline | the AMS call for papers, `https://meetings.ams.org/math/jmmYYYY/cfp.cgi` |

Competitions do get discontinued. The Virginia Tech Regional Mathematics Contest ran every
October for decades and ended after 2022; this page advertised it for three years after it
stopped existing. Confirm each contest is still running before carrying it forward, and
delete the ones that are not rather than leaving them as history.

Also check the Putnam coach names against
[`undergraduate/contacts.md`](undergraduate/contacts.md), and re-check whether the Putnam
paragraph in [`undergraduate/academic_life.md`](undergraduate/academic_life.md) still
duplicates this page.

---

## Contacts pages

**Due:** every August, once teaching assignments are settled.
**Last done:** August 2026 (for 2026-27, from the final service roster; satellite pages
below swept the same day).

[`undergraduate/contacts.md`](undergraduate/contacts.md) carries an explicit academic year
in its heading, so a stale one is visible to any reader. It lists the DUS, course
coordinators, Putnam coaches, the AWM / Math Club committee, and the Math Circle
organizers — all of which rotate. [`graduate/contacts.md`](graduate/contacts.md) is
year-stamped the same way. Transfer-of-credit advising sits with the DUP, so that row
tracks the DUS line rather than a separate assignment.

**Satellite pages that carry service assignments but no year stamp.** Each of these had
gone stale invisibly before the August 2026 sweep; check every one against the new
roster in the same pass as the contacts pages:

- [`awm/index.md`](awm/index.md) — faculty mentors appear in **three** places: the top
  email line, the mailing-list sentence, and the leadership list. Since 2026-27 this is
  the merged AWM / Math Club committee, not a separate pair of AWM mentors.
- [`drp/committee.md`](drp/committee.md) — the sponsoring faculty line, plus a
  graduate-student committee list that rotates on its own schedule.
- [`graduate/admissions.md`](graduate/admissions.md) — the "Admissions, Department of
  Mathematics" e-mail contact near the bottom is the Graduate Admissions chair.
- [`_data/seminars.yml`](_data/seminars.yml) — the `colloq` contact list is the
  Colloquium committee, and the `mathclub` contact is the Math Club face of the
  AWM / Math Club committee.
- [`mathcircle/index.md`](mathcircle/index.md) — the organizers under Contact, and the
  program description (fall-only vs. full-year varies by year).
- [`graduate/graduate_teaching.md`](graduate/graduate_teaching.md) — the GTA Committee
  chair and the same course-coordinator slate as the undergraduate contacts page.
- [`undergraduate/competitions.md`](undergraduate/competitions.md) — the Putnam coaches
  (also on the competitions rollover item above).
- [`mathexlab/contact.md`](mathexlab/contact.md) and
  [`mathexlab/index.md`](mathexlab/index.md) — the lab's faculty contact.

---

## Major intake advisors

**Due:** twice a year — every August for the fall, and early January for the spring.
**Last done:** August 2026 (fall only; the spring 2027 reshuffle is outstanding).

[`_includes/CONTACTS/major_intake.md`](_includes/CONTACTS/major_intake.md) splits major
declaration advising across the intake circle by student last name. It is included by
[`undergraduate/contacts.md`](undergraduate/contacts.md) and
[`undergraduate/degree_requirements.md`](undergraduate/degree_requirements.md), so one edit
serves both pages.

The membership comes from the chair's service assignments for the year, not from last
year's copy of this file. The 2026-27 circle is Abdesselam, Abramenko, Do, Gromoll, Hayes,
Qi, and W. Wang.

**Leaves drive the reshuffle.** The circle is rarely present in full for both terms. In
2026-27 Abdesselam and Hayes are fall-only and Abramenko is spring-only, so the fall list
has six advisors and the spring list will have five. The page therefore carries one term at
a time, and the letter ranges are recut whenever the roster changes — a five-way split is
not a six-way split with one range deleted.

**Recutting the ranges.** The ranges are balanced by student volume, not by letter count.
UVA math majors run roughly 25-40% Asian surnames, which makes C, L, W, and Z far heavier
than a general US surname distribution predicts, and T-Z a full-weight bucket rather than
the scrap it usually is. The August 2026 six-way cut (A-C, D-H, I-L, M-P, Q-S, T-Z) came
from brute-forcing all 53,130 contiguous splits against a mixed model, and holds to within
2.5 points of even across the whole 25-40% band. Redo that arithmetic for whatever number
of advisors the new term has; do not eyeball it. If a real major roster can be pulled from
SIS, count it instead of modelling it.

Advisors are deliberately not seated in the range containing their own initial, and the
assignment is shuffled rather than alphabetical.

---

## Job postings

**Due:** at the start of each hiring season, early fall.
**Last done:** August 2026 (commit 242e4b66, filter bumped to 2026).

[`current-jobs.html`](current-jobs.html) selects posts with `post.job-year >= 2026`. That
year is hardcoded in two places in the file. If it is not bumped, the page keeps showing
the previous cycle's advertisements; if it is bumped before the new ads are posted, the
page correctly falls back to its "no open positions" message.

New postings go in `_posts/jobs/` and need a `job-year` field to appear here at all.

---

## Adding an entry

Anything with a date that expires on a yearly cycle belongs here: a hardcoded year in a
Liquid filter, an academic year in a page heading, an external deadline quoted on a page.
Give it a **Due** line, a **Last done** line, and — most importantly — the primary source
that has to be re-read, so the next refresh is a verification rather than a guess.

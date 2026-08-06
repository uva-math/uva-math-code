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
**Last done:** August 2025 (for 2025-26).

Each seminar has one live page plus one archive page per academic year. Without the
rollover, the previous year's archive keeps collecting new talks and the new year never
appears in the archive list.

The procedure is in [`seminars/seminar_updating.md`](seminars/seminar_updating.md). Note
that both that document and `seminars/update_sems_year.zsh` hardcode the year pair they
were last used for — the year strings inside the script must be bumped before it is run,
or it will recreate the previous year's files.

Verify afterwards that each seminar's main page lists the new year first in its archive
line, that `show_from` and `show_to` bracket the correct July-to-July window, and that the
"upcoming" link still resolves.

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
**Last done:** unknown; currently stamped 2025-26.

[`undergraduate/contacts.md`](undergraduate/contacts.md) carries an explicit academic year
in its heading, so a stale one is visible to any reader. It lists the DUS, course
coordinators, Putnam coaches, Math Club and AWM advisors, and the Math Circle organizers —
all of which rotate. [`graduate/contacts.md`](graduate/contacts.md) is year-stamped the
same way.

---

## Job postings

**Due:** at the start of each hiring season, early fall.
**Last done:** unknown; the filter currently reads 2026.

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

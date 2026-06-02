# Plan: UVA Math arXiv Infrastructure, Phase 1 Only

Goal: set up the infrastructure for a permanent UVA Mathematics arXiv tracker at `math.virginia.edu/arxiv/`, using the same full-arXiv SQLite/Kaggle database and source-fetching corpus as the Homepage arXiv feed. Phase 1 is **prep only**: paths, commands, roster-history extraction, API/cache scaffolding, source-affiliation extraction, and disambiguation/review data structures. It must **not** build the UVA publication database yet.

Hard constraints from LP:

- Use the shared full-arXiv database, not a new scraped database:
  - `/Users/leo/Data/arxiv/arxiv-metadata.db`
  - table: `papers(id, title, abstract, categories, authors, date)`
  - checked 2026-06-02: 3,058,358 papers, dates `1986-04-25` through `2026-05-29`
- Use the shared arXiv source corpus and fetching logic:
  - `/Users/leo/Homepage/_scripts/arxiv/sources/`
  - checked 2026-06-02: 4,425 local source directories
- Final public endpoint: `https://math.virginia.edu/arxiv/`, **not linked from the site yet**.
- No “related papers” feature for UVA Math.
- Need filters by department role/rank group:
  - `faculty` = tenure-track / tenured faculty
  - `postdoc`
  - `grad`
  - `agfm_other` = AGFM / general faculty / lecturers / other active non-TT appointments
  - `emeritus`
- Include papers if **either** the paper has UVA affiliation evidence **or** the matched person’s paper date falls within a UVA Math appointment interval. Current directory membership is insufficient; reconstruct people by appointment year from `uva-math-code` people history.
- For year-level appointment data, use academic-year windows: August 1 through July 31.
- UVA affiliation evidence in a paper is useful, but absence is **not** a rejection reason. Authors sometimes omit UVA; those papers still need to be present if person identity and active appointment-date overlap are confirmed.
- Cross-check against arXiv source text, Semantic Scholar, and CrossRef. API keys are available, but must be read from environment / ignored `.env`, never committed.
- Need a `since` command to update the shared arXiv SQLite database with new papers.

Initial operational scope:

- Start the first pass with academic years from `2021-08-01` through present.
- Treat appointment years as academic years, August 1 through July 31.
- First priority is current active `faculty`; then add `postdoc`, `grad`, `agfm_other`, and `emeritus`.
- First concrete data product is the person-by-academic-year roster, not papers.
- For the initial public-quality dataset, every included paper should have a manual approval record; automation and AI only pre-triage and prepare evidence.
- Initial paper scan is strictly `arxiv_date >= 2021-08-01`. Do not chase older arXiv records in the first pass.
- Store `journal_publication_date` when available, but it is secondary metadata for the first pass.
- Missing journal metadata is not evidence that a paper is unpublished; recent years will be arXiv-heavy because of publication lag and incomplete metadata.
- Deeper backfill by journal publication date can be a later phase if needed.

## 0. Phase 1 non-goals

Phase 1 does **not**:

- scan the full DB for UVA matches;
- generate `assets/data/uva-arxiv-papers.json`;
- generate reports;
- populate journal metadata for all candidates;
- expose a complete public page;
- classify journal tiers;
- build embeddings or related-paper vectors;
- infer final disambiguation decisions.

Allowed in Phase 1:

- create scripts, configs, schemas, cache directories, and Makefile targets;
- create dry-run / smoke-test commands;
- create roster-history extraction that can emit a small preview/support file;
- create a placeholder unlinked `/arxiv/` page if desired, clearly saying data is not loaded yet;
- create the `since` updater command, but do not run a bulk update unless LP explicitly asks.

## 1. Functionality comparison with Homepage arXiv feed

Homepage reference implementation:

- site page: `/Users/leo/Homepage/arxiv/index.html`
- JS: `/Users/leo/Homepage/assets/js/arxiv-feed.js`
- scripts: `/Users/leo/Homepage/_scripts/arxiv/`
- current feed size checked 2026-06-02: 5,752 `_arxiv/*.md` posts and 5,752 search-index entries

| Area | Homepage arXiv feed | UVA Math arXiv tracker decision |
|---|---|---|
| Scope | Integrable probability community, broadly construed. Tracks selected papers by a curated author list plus semantic search. Not all papers by tracked authors are included. | UVA Math active appointments. No topic filter. A paper is in scope if a matched person was active in UVA Math at submission/publication time, subject to disambiguation. |
| Primary data store | Jekyll collection `_arxiv/*.md`; compact client index `assets/data/arxiv-index.json`; shared Kaggle/SQLite DB as full-arXiv backing store. | Shared `/Users/leo/Data/arxiv/arxiv-metadata.db` remains the backing store. UVA outputs later should be generated JSON under `assets/data/`, not per-paper Jekyll posts. |
| DB update | `fetch_arxiv.py` fetches recent papers by category/author and inserts accepted papers into the shared DB. `import_kaggle_to_sqlite.py` builds the base DB. | Add a dedicated `since` updater that updates the shared full-arXiv DB globally since a date. Do not rebuild Kaggle DB in Phase 1. Keep schema compatible with Homepage. |
| Source fetching | `download_sources.py` fetches e-print sources for feed papers into Homepage source corpus; source viewer uses S3/file manifests. | Reuse the same local source corpus. Phase 1 adds source-fetch/extract helpers for candidate IDs and affiliation evidence. No bulk source fetch yet. |
| Source viewer | Public `/arxiv/source/?id=...` page shows TeX/files. | Optional later. Phase 1 only ensures source paths and extraction infrastructure. If ported later, use `/arxiv/source/` and UVA styling. |
| Matching | `authors.yml` with arXiv-name aliases; surname+initial matching; high-ambiguity flags; AI topic/person filter; review TUI. | Dynamic people roster from `_departmentpeople` plus git history; manual aliases keyed by UVA_id; active-appointment windows; no topic filter. AI may assist review later, but deterministic evidence and manual YAML are primary. |
| Disambiguation | Mostly “is this integrable-prob author / is the topic right?”; common names get AI/review. | Harder: identity + active appointment + possibly missing affiliation. Need rarity priors, external IDs, coauthor history, category compatibility, source affiliation evidence, and explicit accept/reject overrides. |
| Search UI | Search operators `au:`, `in:`, `cat:`, `y:`, secret `TOP`; date dropdown; category buttons; author/journal/category badge clicks; abstracts; BibTeX copy/download; RSS; source badges; related-paper dropdown. | Keep/adapt search, date/year, category, author/person, journal, abstracts, source/arXiv/PDF/DOI links, BibTeX export if useful. Add filters `role:faculty|postdoc|grad|agfm_other|emeritus`, exact person, active year, UVA-evidence. Drop `Related`. `TOP` optional later, not Phase 1. |
| Progressive loading | Initial page embeds a limited batch, then JS loads overflow/search index and appends results in batches. | Yes: use Homepage-style progressive loading for `/arxiv/`, but from UVA JSON/chunks rather than Jekyll `_arxiv` posts. Keep initial render small, then hydrate full search/filter data asynchronously. |
| Related papers / embeddings | `build_arxiv_embeddings.py`, `arxiv-vectors.npy`, related IDs and dropdowns. | Do not copy. Not needed for UVA page and not in Phase 1. |
| Journal metadata | `fetch_journal_refs.py` combines Semantic Scholar, arXiv API, CrossRef; caches in `.journal-refs-cache.db`; updates post front matter and search index. | Reuse the idea/client code, but store in UVA sidecar cache keyed by arXiv ID. S2/CrossRef are cross-check sources, not hard gates. |
| Manual operations | `add_paper.py`, `delete_paper.py`, `processed.json`, `review.json`, Go TUI. | Need analogous accept/reject/alias/manual-identity infrastructure, but Phase 1 only defines files and command skeletons. |
| Site output | Homepage `/arxiv/` is linked in nav (`nav_id`, `nav_weight`) and has RSS. | UVA `/arxiv/` should be unlinked: no nav entry, optionally `sitemap: false` until validated. |

Bottom line: borrow the robust pieces (shared DB, source download/unpack, journal metadata clients, search UI ideas, review queue pattern), but change the core object from “topic-selected community feed” to “active-appointment UVA Math author identity tracker.”

## 2. Proposed repository layout

Use a distinct `scripts/uva_arxiv/` namespace so this does not look like generic news/publications plumbing.

```text
scripts/uva_arxiv/
  README.md
  config.yml
  env.py
  arxiv_db.py
  update_arxiv_db.py        # implements the since command
  roster.py                 # parse current _departmentpeople front matter
  roster_history.py         # reconstruct appointments from git history
  roles.py                  # faculty/postdoc/grad/agfm_other classification
  sources.py                # fetch/unpack source bundles into shared source corpus
  affiliation.py            # grep/extract UVA and negative affiliation evidence
  s2_client.py              # Semantic Scholar cache/client scaffolding
  crossref_client.py        # CrossRef cache/client scaffolding
  arxiv_api.py              # arXiv API/OAI helpers
  disambiguation.py         # scoring skeleton; no final matching in Phase 1
  review_schema.py          # accepted/rejected/review queue schemas
  check_env.py              # smoke-test paths, DB schema, API env vars
  data/
    aliases.yml
    appointments_overrides.yml
    people_manual.yml
    affiliation_patterns.yml
    accepted_matches.yml
    rejected_matches.yml
    ambiguous_people.yml
  cache/
    .gitkeep
```

Future generated outputs, not Phase 1:

```text
assets/data/uva-arxiv-papers.json
assets/data/uva-arxiv-summary.json
assets/data/uva-arxiv-people.json
assets/data/uva-arxiv-index.json
reports/uva-arxiv-*.csv
reports/uva-arxiv-*.md
```

Future unlinked page, not a data build:

```text
arxiv/index.md              # permalink: /arxiv/, no nav_id/nav_weight
assets/js/uva-arxiv.js
```

## 3. Shared paths and configuration

`config.yml` should make shared paths explicit and overridable:

```yaml
arxiv_db: /Users/leo/Data/arxiv/arxiv-metadata.db
arxiv_sources_dir: /Users/leo/Homepage/_scripts/arxiv/sources
homepage_arxiv_scripts: /Users/leo/Homepage/_scripts/arxiv
initial_arxiv_start_date: 2021-08-01
# First pass filters by arXiv date only. Journal-publication-date backfill is optional later.
site_endpoint: /arxiv/

people_dirs:
  faculty: _departmentpeople/faculty
  postdoc: _departmentpeople/postdocs
  grad: _departmentpeople/gradstudents
  lecturer: _departmentpeople/lecturers
  emeriti: _departmentpeople/emeriti
  unpublished: _departmentpeople/_unpublished

role_groups:
  faculty:
    include_general_position: [faculty]
    exclude_position_regex: "General Faculty|Emeritus|Emerita"
  postdoc:
    include_general_position: [postdoc]
  grad:
    include_general_position: [gradstudent]
  agfm_other:
    include_general_position: [lecturer]
    include_position_regex: "General Faculty|Lecturer|Instructor|Academic General Faculty"
  emeritus:
    include_general_position: [emeritus]
    include_position_regex: "Emeritus|Emerita"
```

Environment variables:

```text
ARXIV_DB=/Users/leo/Data/arxiv/arxiv-metadata.db
ARXIV_SOURCES_DIR=/Users/leo/Homepage/_scripts/arxiv/sources
S2_API_KEY=...
SEMANTIC_SCHOLAR_API_KEY=...   # accepted alias; normalize internally to S2_API_KEY
CROSSREF_MAILTO=...
CROSSREF_API_KEY=...           # optional if available
OPENALEX_EMAIL=...             # optional later
```

`.env` is already gitignored. Scripts may load it for local use, but must never commit secrets or derived key material.

## 4. The `since` command for updating the shared arXiv DB

Need a dedicated full-arXiv updater, not just Homepage’s category/author fetcher.

Command shape:

```bash
python3 scripts/uva_arxiv/update_arxiv_db.py since --dry-run
python3 scripts/uva_arxiv/update_arxiv_db.py since --since 2026-05-29 --dry-run
python3 scripts/uva_arxiv/update_arxiv_db.py since --since 2026-05-29
make uva-arxiv-db-since SINCE=2026-05-29
```

Default behavior:

1. Open shared `arxiv-metadata.db`.
2. Read `SELECT max(date) FROM papers`.
3. Use `since = max(date) - overlap_days` unless explicit `--since` is provided.
4. Fetch new/changed arXiv records from arXiv OAI-PMH (`https://export.arxiv.org/oai2`) or an API fallback.
5. Normalize to the existing Homepage-compatible schema only:
   ```sql
   papers(id TEXT PRIMARY KEY, title TEXT, abstract TEXT, categories TEXT, authors TEXT, date TEXT)
   ```
6. Upsert by arXiv ID with a transaction.
7. Do not add columns to `papers`; write updater bookkeeping to a sidecar cache under `scripts/uva_arxiv/cache/`.
8. Preserve Homepage compatibility.

Preferred source: arXiv OAI-PMH, because it can update the whole archive since a date. API fallback can query broad category groups only if OAI fails.

Safety details:

- Always use an overlap window, e.g. 7 days, to catch delayed records and date parsing issues.
- `--dry-run` prints planned date range, estimated request count if known, current DB stats, and no writes.
- `--limit N` for smoke tests.
- `--backup` optional later; do not silently copy multi-GB DBs.
- Add `idx_date` only behind `--ensure-indexes` or an explicit Makefile target; do not surprise-modify the shared DB during smoke checks.
- Withdrawn/deleted arXiv records: keep existing row if already present; mark only in sidecar state unless schema policy changes later.

Phase 1 deliverable: command exists and passes dry-run/small-limit tests. Do **not** run a full update unless asked.

## 5. Roster and active appointment history

Current people files alone are not enough. Need active appointments by year/date, including people who were active during the period but are no longer current.

Current directories checked 2026-06-02:

```text
_departmentpeople/faculty      35 files, but includes at least one emeritus in faculty/
_departmentpeople/postdocs      7 files
_departmentpeople/gradstudents 83 files
_departmentpeople/lecturers     6 files
_departmentpeople/emeriti      16 files
```

### 5.0 First milestone: person-by-year roster

Before touching papers, build the list of people with appointment years.

Output for the first milestone:

```text
reports/uva-arxiv-active-people-by-year.csv
reports/uva-arxiv-active-people-by-year.md
scripts/uva_arxiv/cache/active_people_by_year.json
```

Rows should be keyed by `person_id`, academic year, and `role_group`:

```csv
person_id,display_name,academic_year,start_date,end_date,role_group,position,source,confidence,current_active
lap5r,Leonid Petrov,2021-2022,2021-08-01,2022-07-31,faculty,Professor,manual,exact,true
```

For the first pass, generate academic years from `2021-08-01` onward. Current active faculty are the priority; missing/uncertain historical intervals for students/postdocs can be flagged for later overrides.

### 5.1 Current roster parser

`roster.py` parses YAML front matter into stable people records keyed by `UVA_id`, never by display name.

Example target shape:

```json
{
  "person_id": "lap5r",
  "uva_id": "lap5r",
  "display_name": "Leonid Petrov",
  "first": "Leonid",
  "last": "Petrov",
  "general_position": "faculty",
  "position": "Professor",
  "email": "petrov@virginia.edu",
  "personal_page": "http://lpetrov.cc/",
  "research_tags": ["PR", "CO"],
  "specialty": "Integrable Probability, Algebraic Combinatorics",
  "published": true,
  "current_file": "_departmentpeople/faculty/lap5r.md"
}
```

Rules:

- `published: false` means not public/current for the site; keep the record in history but do not treat as active without override.
- `general_position: emeritus` or position containing `Emeritus/Emerita` is classified as `emeritus`, not discarded. It gets its own appointment interval/category.
- Front matter wins over directory name when they conflict, but conflicts must be reported.
- Names with diacritics need normalized search aliases but display names retain diacritics.

### 5.2 Role/rank group classifier

`roles.py` assigns:

```text
faculty      tenure-track / tenured faculty
postdoc      postdocs / visiting postdocs with active postdoc appointment
grad         graduate students / Bridge-to-Doctorate if active and public unless override
agfm_other   general faculty, lecturers, instructors, other active non-TT academic appointments
emeritus     emeritus/emerita appointments
```

Faculty directory caveat: files in `_departmentpeople/faculty` can be TT faculty, general faculty, or emeriti. Classification must inspect `general_position` and `position`, not directory alone.

Examples from current files:

- `position: Assistant Professor, General Faculty` -> `agfm_other`
- `position: Professor, General Faculty` -> `agfm_other`
- `general_position: lecturer` -> `agfm_other`
- `general_position: emeritus` or `Professor Emeritus` -> `emeritus`
- `position: Professor`, `Associate Professor`, `Assistant Professor`, named chairs -> `faculty` unless General Faculty/Emeritus appears

Store both coarse group and exact position:

```json
{
  "role_group": "faculty",
  "rank_label": "Professor",
  "position_raw": "Gordon Whyburn Professor of Mathematics"
}
```

### 5.3 Appointment history from git

`roster_history.py` reconstructs active intervals from repository history.

Inputs:

- current files under `_departmentpeople/`
- `git log --follow --name-status -- _departmentpeople`
- historical file contents via `git show <commit>:<path>`
- moves between `faculty`, `postdocs`, `gradstudents`, `lecturers`, `emeriti`, `_unpublished`
- manual overrides in `appointments_overrides.yml`

Target output shape for a support file/cache:

```json
{
  "person_id": "bug4bt",
  "display_name": "Sarah Blackwell",
  "appointments": [
    {
      "start_date": "2023-08-01",
      "end_date": null,
      "role_group": "postdoc",
      "position": "NSF Postdoctoral Research Fellow",
      "source": "git-history",
      "confidence": "month"
    }
  ],
  "active_years": [2023, 2024, 2025, 2026]
}
```

Heuristic interval rules:

- File first appears in an active people directory -> appointment start approximately commit date unless override gives better date.
- File moves to `emeriti` -> close the previous appointment interval and open an `emeritus` interval at approximately the commit date unless override gives better dates.
- File moves to `_unpublished` or disappears -> appointment end approximately commit date unless override gives better date.
- Role changes are interval boundaries.
- If a file remains current and active -> `end_date: null`.
- If only year is knowable, store `confidence: year`; if commit date is the only evidence, store `confidence: commit-date`.
- Manual overrides always beat inferred dates.

Manual override example:

```yaml
lap5r:
  appointments:
    - start_date: 2017-08-25
      end_date: null
      role_group: faculty
      position: Professor
      source: manual

some_old_postdoc:
  appointments:
    - start_date: 2020-09-01
      end_date: 2023-08-31
      role_group: postdoc
      source: manual
```

Paper-date / appointment policy for matching later:

- Use the arXiv submission date from the shared DB as the first-pass `paper_date`. Later journal publication dates can be stored separately but should not replace the arXiv date for appointment overlap.
- A paper is in UVA scope if at least one matched person satisfies either:
  - UVA affiliation evidence appears in the source/API metadata; or
  - `paper_date` overlaps a recorded UVA Math appointment interval, including `emeritus` intervals.
- If only year-level history is known, expand each academic year to August 1 through July 31 and mark the overlap lower precision.
- Current people’s pre-UVA papers are not department-scope by default unless the paper itself has UVA affiliation evidence.
- If a person was active at UVA on the paper date and the paper omits UVA affiliation, keep the paper and mark `uva_affiliation_evidence: absent`, not rejected.

Phase 1 deliverable: history extractor + dry-run report, not a paper scan.

## 6. Source fetching and UVA affiliation evidence

arXiv metadata in the shared SQLite DB does not include affiliations. Use source extraction as evidence, not as a gate.

Shared source corpus:

```text
/Users/leo/Homepage/_scripts/arxiv/sources/<arxiv-id>/
```

Phase 1 source commands:

```bash
python3 scripts/uva_arxiv/sources.py fetch --id 2501.01234 --dry-run
python3 scripts/uva_arxiv/sources.py fetch --id 2501.01234
python3 scripts/uva_arxiv/affiliation.py scan --id 2501.01234
```

Borrow from Homepage `download_sources.py`:

- fetch `https://arxiv.org/e-print/<id>`;
- unpack tar.gz / gz / raw TeX / PDF fallback;
- write into shared source dir;
- safe directory names for old IDs with `/`;
- rate limit and retry.

Do not create a second source corpus in `uva-math-code`.

`affiliation_patterns.yml`:

```yaml
positive:
  - "University of Virginia"
  - "Department of Mathematics, University of Virginia"
  - "Dept. of Mathematics, University of Virginia"
  - "@virginia.edu"
  - "virginia.edu"
  - "Charlottesville, VA"

negative:
  - "Virginia Tech"
  - "West Virginia University"
  - "Virginia Commonwealth University"
  - "George Mason University"
```

Evidence record:

```json
{
  "arxiv_id": "2501.01234",
  "person_id": "lap5r",
  "source": "tex",
  "file": "main.tex",
  "match": "Department of Mathematics, University of Virginia",
  "evidence": "confirmed",
  "notes": "line/snippet stored in cache, not necessarily public"
}
```

Affiliation policy:

- `confirmed`: positive UVA evidence in source/API metadata.
- `probable`: active appointment + name identity strong, no explicit affiliation.
- `absent`: checked source and no UVA evidence found.
- `conflict`: negative/other institution evidence appears for a matched person; send to review, do not auto-drop.
- Absence of UVA evidence is never by itself a rejection.

## 7. Semantic Scholar and CrossRef cross-checking

Use external APIs for cross-checks and journal/DOI metadata, not as the primary source of truth for inclusion.

Phase 1 clients:

```bash
python3 scripts/uva_arxiv/s2_client.py smoke --id 2501.01234
python3 scripts/uva_arxiv/crossref_client.py smoke --doi 10.xxxx/yyyy
```

Semantic Scholar fields to cache:

- external IDs: DOI, arXiv, CorpusId
- title, year
- authors and S2 author IDs
- venue, journal, publication venue
- publication date if available
- open access / URL if useful later

CrossRef fields to cache:

- DOI
- canonical title
- author list
- issued / published-print / published-online years
- container-title, short-container-title
- volume, issue, pages
- institution/affiliation fields if present

Cache design:

```text
scripts/uva_arxiv/cache/s2.sqlite
scripts/uva_arxiv/cache/crossref.sqlite
scripts/uva_arxiv/cache/source_affiliation.sqlite
```

No API keys in cache filenames or logs. Store raw JSON if useful, but keep caches out of git.

Cross-check policy:

- Treat journal metadata as laggy/incomplete. Especially for 2024--2026, many valid arXiv papers will have no journal data yet.
- First pass does not query older arXiv records for journal-date backfill; it only enriches arXiv records dated `2021-08-01` or later.
- If arXiv, S2, and CrossRef disagree on DOI/title/journal, record conflict for review.
- S2 author IDs can become strong identity evidence after manual association in `aliases.yml`.
- CrossRef/S2 affiliation absence is weak; many records omit affiliations.
- CrossRef/S2 should not remove an active-UVA paper unless they reveal a clear name collision and manual review confirms rejection.

## 8. Disambiguation strategy

This is the hard part. Keep identity matching, active appointment, and UVA-affiliation evidence separate.

### 8.1 Person identity evidence

For each candidate paper/person pair, score evidence dimensions independently:

1. **Name exactness**
   - exact full name match;
   - first-initial + surname;
   - initials-only;
   - diacritic-normalized match;
   - known alias from `aliases.yml`.
2. **Name rarity in full arXiv**
   - count exact full-name occurrences in `papers.authors`;
   - count surname+initial occurrences;
   - mark common names as high risk.
3. **Appointment overlap**
   - paper date within active UVA Math interval;
   - approximate year overlap;
   - outside interval -> review/reject for department scope unless manual override.
4. **External IDs**
   - S2 author ID, ORCID, personal-page publication list, known arXiv author spelling.
5. **Coauthor priors**
   - coauthor with another active UVA Math person;
   - coauthor with known advisor/student/collaborator from accepted matches;
   - coauthor network from previous accepted papers.
6. **Subject compatibility**
   - arXiv categories compatible with research tags/specialty;
   - category mismatch is a review signal, not automatic rejection.
7. **Affiliation/source evidence**
   - UVA source evidence strengthens;
   - no evidence does not kill;
   - conflicting institution evidence forces review.

### 8.2 Alias file keyed by UVA_id

Do not key manual data only by display name.

```yaml
lap5r:
  display_name: Leonid Petrov
  arxiv_names:
    - Leonid Petrov
    - L. Petrov
  normalized_names:
    - leonid petrov
  semantic_scholar_author_ids: []
  orcid: []
  safe_match: true
  notes: "Rare enough; still check active appointment."

tmark:
  display_name: Thomas Mark
  arxiv_names:
    - Thomas Mark
    - T. Mark
  safe_match: false
  require_review_if_no_affiliation: true
  notes: "Common-ish; use categories/coauthors/source evidence."
```

### 8.3 Confidence levels

Use conservative labels:

```text
identity_confidence:
  confirmed_manual
  confirmed_external_id
  high_name_rare_active
  medium_name_active
  low_initials_or_common
  rejected_manual
  rejected_collision

affiliation_evidence:
  confirmed
  probable
  absent
  conflict
  unchecked

scope_status:
  department_scope       # UVA affiliation evidence OR appointment-date overlap
  current_person_external # optional future bucket, not counted for dept
  out_of_scope
  needs_review
```

For the initial public-quality dataset, “auto-accept” means “safe suggested acceptance,” not “publish without review.” Every included paper should still get a manual approval record, possibly by batch-approving a low-risk queue.

Suggested-accept rules should require identity confidence and either appointment-date overlap or explicit UVA affiliation evidence. They should not require explicit UVA text when appointment overlap is clear.

Suggested-accept examples later:

- rare full name + active appointment overlap + math category compatible;
- full name + S2 author ID manually linked + active appointment;
- initials-only but coauthored with another confirmed UVA person and manually accepted pattern.

Pre-triage buckets:

- `ready_to_accept`: deterministic evidence strong; batch approval should be safe.
- `quick_check`: likely correct but needs one human glance.
- `needs_research`: common name, weak identity evidence, conflicting source/API data, or weird subject area.
- `likely_reject`: probable collision or out-of-scope, but keep evidence until manually rejected.

Review examples:

- common name;
- initials-only;
- source says another Virginia institution;
- paper date just before/after appointment interval;
- grad/postdoc names without external IDs;
- multiple UVA people could match the same name string;
- S2 author cluster inconsistent with known person.

Reject examples:

- manual rejected collision;
- no active appointment overlap, no UVA affiliation evidence, and no manual override;
- impossible field/coauthors/source after review.

### 8.4 AI-assisted checks via pi

Use AI only where it reduces human review load. It is not a source of truth and should not silently create accepted matches.

Good uses for `pi`:

- summarize evidence for ambiguous review-queue entries;
- compare a paper’s title/authors/categories/source-affiliation snippets against a person’s profile, specialty, aliases, and appointment dates;
- flag likely name collisions;
- suggest missing aliases or external IDs;
- explain conflicts between arXiv/S2/CrossRef metadata;
- prioritize review items by risk;
- put candidates into `ready_to_accept`, `quick_check`, `needs_research`, or `likely_reject` buckets.

Bad uses:

- auto-accept common-name matches without deterministic evidence;
- use model knowledge instead of cached public metadata;
- hide decisions outside YAML;
- classify journal prestige or identity from vibes.

Implementation later:

```bash
python3 scripts/uva_arxiv/validate_matches.py --ai-review --limit 50
```

The command should call `pi --no-session --no-tools --no-context-files -p` with a constrained prompt and require JSON output like:

```json
{
  "arxiv_id": "2501.01234",
  "person_id": "abc1de",
  "recommendation": "accept|reject|needs_human",
  "confidence": "high|medium|low",
  "reason": "short evidence-based reason",
  "suggested_yaml": null
}
```

Even high-confidence AI recommendations go into the review queue. For the first validated dataset, the final output should include only papers with a human approval record in `accepted_matches.yml`.

## 9. Manual decision files

All curation must be inspectable YAML, not hidden agent memory. Initial policy: every paper that appears in the public/generated paper list must be represented in `accepted_matches.yml`; rejected/collision candidates go in `rejected_matches.yml`; undecided items remain in the review queue.

```text
scripts/uva_arxiv/data/accepted_matches.yml
scripts/uva_arxiv/data/rejected_matches.yml
scripts/uva_arxiv/data/ambiguous_people.yml
scripts/uva_arxiv/data/aliases.yml
scripts/uva_arxiv/data/appointments_overrides.yml
```

Accepted match example:

```yaml
- arxiv_id: "2501.01234"
  person_id: "lap5r"
  decision: accept
  identity_confidence: confirmed_manual
  department_scope: true
  reason: "Full-name match; active UVA appointment; source omits affiliation but identity is clear."
  decided_by: leo
  decided_at: "2026-06-02"
```

Rejected match example:

```yaml
- arxiv_id: "2501.01234"
  person_id: "abc1de"
  decision: reject
  reason: "Name collision; S2 author cluster is different person."
  decided_by: leo
  decided_at: "2026-06-02"
```

## 10. Future generated paper schema

Not generated in Phase 1, but infrastructure should aim at this shape.

```json
{
  "arxiv_id": "2501.01234",
  "title": "...",
  "authors": ["..."],
  "arxiv_date": "2025-01-15",
  "arxiv_year": 2025,
  "journal_publication_date": null,
  "categories": ["math.PR", "math.CO"],
  "abstract": "...",
  "matched_people": [
    {
      "person_id": "lap5r",
      "display_name": "Leonid Petrov",
      "role_group": "faculty",
      "rank_label": "Professor",
      "appointment_overlap": "confirmed",
      "identity_confidence": "high_name_rare_active",
      "affiliation_evidence": "absent",
      "department_scope": true
    }
  ],
  "journal": {
    "doi": "...",
    "name_raw": "...",
    "name_canonical": "...",
    "volume": "...",
    "pages": "...",
    "publication_year": 2025,
    "sources": ["semantic_scholar", "crossref", "arxiv"]
  },
  "links": {
    "arxiv": "https://arxiv.org/abs/2501.01234",
    "pdf": "https://arxiv.org/pdf/2501.01234",
    "doi": "..."
  },
  "review": {
    "status": "manual|suggested_accept|needs_review",
    "triage": "ready_to_accept|quick_check|needs_research|likely_reject",
    "notes": ""
  }
}
```

Deduplicate by arXiv ID. If multiple UVA people match the same paper, one paper record has multiple `matched_people`. Aggregate reports later must distinguish unique papers from person-paper incidences.

## 11. Future `/arxiv/` page functionality

Endpoint: `math.virginia.edu/arxiv/`, unlinked until validated.

Borrow from Homepage:

- compact searchable list;
- Homepage-style progressive loading: small initial render, async full index/chunks, batched DOM insertion;
- date/year filter;
- category buttons;
- clickable author/person badges;
- clickable journal badges;
- arXiv/PDF/DOI links;
- abstract toggle;
- BibTeX export/copy if straightforward;
- source badge only if source is fetched and exposing sources is approved.

Add UVA-specific filters:

```text
role:faculty
role:postdoc
role:grad
role:agfm_other
role:emeritus
triage:needs_research
person:"Leonid Petrov"
uva:confirmed
uva:absent
status:manual
status:needs_review       # internal-only if public page hides review status
active:2024
cat:math.PR
y:2021-2026
in:"Ann. Probab."
```

Do not include:

- related-paper dropdowns;
- embedding vectors;
- Homepage’s integrable-prob topic language;
- nav link before validation.

Potential page front matter:

```yaml
---
title: UVA Math arXiv
layout: default
permalink: /arxiv/
published: true
sitemap: false
---
```

No `nav_id`, no `nav_weight`.

## 12. Makefile targets for Phase 1

Add targets only for infrastructure/smoke tests; no full build target yet unless it intentionally says not implemented.

```make
uva-arxiv-check:
	python3 scripts/uva_arxiv/check_env.py

uva-arxiv-db-since:
	python3 scripts/uva_arxiv/update_arxiv_db.py since --since $(SINCE) $(ARGS)

uva-arxiv-db-since-dry:
	python3 scripts/uva_arxiv/update_arxiv_db.py since --since $(SINCE) --dry-run $(ARGS)

uva-arxiv-roster-history:
	python3 scripts/uva_arxiv/roster_history.py --dry-run $(ARGS)

uva-arxiv-source-smoke:
	python3 scripts/uva_arxiv/sources.py fetch --id $(ID) --dry-run

uva-arxiv-api-smoke:
	python3 scripts/uva_arxiv/s2_client.py smoke --id $(ID)
```

If `SINCE` is omitted, the updater defaults to DB max date minus overlap days.

## 13. Phase 1 implementation tasks

### Task 1: Create UVA arXiv scaffold and configuration

- [x] create the `scripts/uva_arxiv/` namespace with `README.md`, `cache/.gitkeep`, and the planned module/script files needed for Phase 1
- [x] add `scripts/uva_arxiv/config.yml` with the shared DB/source paths, initial arXiv start date, people directories, and role-group rules from this plan
- [x] add `.gitignore` entries for `scripts/uva_arxiv/cache/*` while preserving `scripts/uva_arxiv/cache/.gitkeep`
- [x] create the manual YAML data files under `scripts/uva_arxiv/data/` with documented examples and no accepted/rejected paper data
- [x] add lightweight config/env loading helpers that support ignored local `.env` files without ever logging API key values
- [x] add tests or smoke checks for config loading and cache/data path creation

### Task 2: Implement shared arXiv DB checks and the `since` updater

- [x] implement `scripts/uva_arxiv/arxiv_db.py` with read-only/read-write SQLite connections, schema validation, max-date lookup, and schema-preserving upsert helpers
- [x] implement `scripts/uva_arxiv/check_env.py` to confirm repo root, shared DB existence/schema/count/min/max dates, shared source directory, safe API-key presence reporting, and ignored `.env` status
- [x] implement `scripts/uva_arxiv/update_arxiv_db.py since` with `--dry-run`, explicit/default `--since`, overlap-days handling, `--limit`, and transaction upserts
- [x] add OAI-PMH fetch plumbing for whole-archive updates and a conservative API fallback/skeleton without changing the `papers` schema
- [x] add tests using a temporary SQLite database and mocked fetch responses for validation, dry-run, and upsert behavior
- [x] verify the updater does not run a full shared-DB update or add indexes unless explicitly requested

### Task 3: Parse current people records and classify role groups

- [x] implement `scripts/uva_arxiv/roles.py` to assign `faculty`, `postdoc`, `grad`, `agfm_other`, and `emeritus` from front matter rather than directory alone
- [x] implement `scripts/uva_arxiv/roster.py` to parse `_departmentpeople` YAML front matter into stable records keyed by `UVA_id`
- [x] preserve display names with diacritics while adding normalized search aliases where useful
- [x] report directory/front-matter conflicts, unpublished records, and emeriti/general-faculty records found in active directories
- [x] add fixture-based tests for TT faculty, general faculty, lecturers, postdocs, graduate students, emeriti, unpublished records, and directory/front-matter conflicts

### Task 4: Build appointment history and person-by-year roster output

- [x] implement `scripts/uva_arxiv/roster_history.py` to inspect git history, file additions/removals/moves, and historical front matter under `_departmentpeople`
- [x] apply `appointments_overrides.yml` before inferred intervals and record interval source/confidence
- [x] infer active appointment intervals across role changes, moves to `_unpublished`, and moves to `emeriti`
- [x] expand intervals from `2021-08-01` onward into academic-year windows running August 1 through July 31
- [x] write the first milestone outputs: `scripts/uva_arxiv/cache/active_people_by_year.json`, `reports/uva-arxiv-active-people-by-year.csv`, and `reports/uva-arxiv-active-people-by-year.md`
- [x] add dry-run output with yearly counts by role group and clear uncertainty/conflict reporting
- [x] add tests or fixture smoke checks for interval inference, manual overrides, academic-year expansion, and role changes

### Task 5: Add source fetch and UVA affiliation evidence tooling

- [x] implement `scripts/uva_arxiv/sources.py fetch --id ...` with dry-run support, safe arXiv-ID directory names, shared source-corpus output, rate limiting, retry hooks, and archive unpacking for tar/gzip/raw TeX/PDF fallback cases
- [x] implement `scripts/uva_arxiv/affiliation.py scan --id ...` using `affiliation_patterns.yml` positive/negative patterns and the shared source corpus
- [x] store affiliation evidence in a cache-side record/database without committing fetched sources or generated cache data
- [x] keep absence of UVA evidence as an evidence state rather than a rejection reason
- [x] add tests with temporary source trees for positive, negative, conflicting, absent, and missing-source cases

### Task 6: Add Semantic Scholar and CrossRef smoke clients

- [x] implement `scripts/uva_arxiv/s2_client.py smoke --id ...` with environment-key normalization, safe logging, rate-limit-aware request handling, and `scripts/uva_arxiv/cache/s2.sqlite`
- [x] implement `scripts/uva_arxiv/crossref_client.py smoke --doi ...` with `CROSSREF_MAILTO`/optional key support, safe logging, and `scripts/uva_arxiv/cache/crossref.sqlite`
- [x] cache raw JSON or normalized fields useful for DOI, journal, publication-date, author, venue, and conflict checks
- [x] treat missing journal/API metadata as incomplete metadata, not publication or scope evidence
- [x] add mocked-HTTP tests for cache hits, cache misses, missing keys, rate limits, and metadata-conflict recording

### Task 7: Wire Makefile targets and optional unlinked placeholder page

- [x] add the Phase 1 Makefile targets from this plan: `uva-arxiv-check`, `uva-arxiv-db-since`, `uva-arxiv-db-since-dry`, `uva-arxiv-roster-history`, `uva-arxiv-source-smoke`, and `uva-arxiv-api-smoke`
- [x] ensure the `SINCE`, `ID`, and `ARGS` variables work as documented and omitted `SINCE` falls back to DB max date minus overlap days
- [x] optionally add an unlinked `/arxiv/` placeholder page with `permalink: /arxiv/`, `sitemap: false`, and no `nav_id`/`nav_weight`
- [x] verify no Phase 1 target generates `assets/data/uva-arxiv-papers.json`, performs a full candidate scan, or creates related-paper/embedding files
- [x] add or update tests/smoke checks for the Makefile targets and placeholder page metadata if the page is created

### Task 8: Verify Phase 1 acceptance criteria and guardrails

- [ ] run `make uva-arxiv-check` and confirm DB schema, DB date stats, source-corpus path, and API-key presence reporting are safe and correct
- [ ] run `make uva-arxiv-db-since-dry` and confirm it reports the planned date range without writing to the shared DB
- [ ] run `make uva-arxiv-roster-history` and confirm yearly active counts by role group plus the person-by-year support outputs are produced
- [ ] run `make uva-arxiv-source-smoke ID=2501.01234` and confirm it is a dry-run smoke command unless explicitly overridden
- [ ] verify no secrets, fetched sources, SQLite caches, generated publication data, or scratch artifacts are staged for commit
- [ ] verify this plan still parses as a ralphex task plan with `### Task N:` headers and checkboxes only inside Task sections

## 14. Phase 1 acceptance criteria

After Phase 1, these should work:

```bash
make uva-arxiv-check
make uva-arxiv-db-since-dry
make uva-arxiv-roster-history
make uva-arxiv-source-smoke ID=2501.01234
```

Expected outcomes:

- shared DB schema verified;
- current DB max date printed;
- source corpus path verified;
- API key presence reported safely;
- active roster/history dry-run reports counts by year and role group;
- no `assets/data/uva-arxiv-papers.json` is generated;
- no full candidate scan occurs;
- no generated publication/report data is committed;
- no related-paper/embedding files are created.

## 15. Later phases, deliberately out of scope now

Phase 2: build candidate retrieval and matching over the shared SQLite DB using roster-history windows and alias/disambiguation scoring.

Phase 3: fetch source evidence and S2/CrossRef metadata for candidates; produce review queue; manual curation.

Phase 4: generate validated `assets/data/uva-arxiv-*.json` and internal reports.

Phase 5: build the unlinked `/arxiv/` page and test filters/UI.

Phase 6: decide whether/when to link from the site, add RSS/BibTeX, and schedule monthly `since` updates.

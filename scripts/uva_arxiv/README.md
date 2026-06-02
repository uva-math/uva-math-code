# UVA Math arXiv Tracker Infrastructure

This directory contains infrastructure for the permanent UVA Mathematics arXiv
tracker at `/arxiv/`.

The current build is still an internal-review prototype. It should not publish a
public paper page until candidate generation is made reproducible and the public
output is generated only from accepted manual decisions.

## Data/storage split

The tracker intentionally separates public/repo data from private audit data.

### Tracked repo data

Manual, durable decisions live under `scripts/uva_arxiv/data/` and should be
committed:

- `aliases.yml` — manual name aliases and safe matching hints keyed by UVA id.
- `accepted_matches.yml` — paper/person rows approved for public use.
- `rejected_matches.yml` — paper/person rows rejected as name collisions or out
  of scope.
- `appointments_overrides.yml`, `people_manual.yml`, `ambiguous_people.yml` —
  roster/manual review inputs.
- `affiliation_patterns.yml` — source-affiliation scan patterns.

Public-quality paper inclusion later requires an accepted row in
`accepted_matches.yml`. Source absence is not a rejection reason by itself; it
only sends a candidate to manual review.

### Ignored local caches

Local caches live in `scripts/uva_arxiv/cache/` and are ignored except for
`.gitkeep`. They may include SQLite caches and generated JSON review inputs.
These are reproducible/scratch artifacts and should not be committed.

### External source/evidence corpora

arXiv source files are needed locally for checking affiliation evidence, but they
must remain outside this website repository and outside public output.

Configured shared source corpus:

```text
/Users/leo/Homepage/_scripts/arxiv/sources/
```

Current TT-candidate audit archive:

```text
/Users/leo/Data/arxiv/uva-math-tt-candidate-sources/
```

That archive contains unpacked source directories, manifests, and review reports.
It is private audit/provenance data. The public `/arxiv/` page should not expose
source files, local paths, source snippets, or cache paths.

The intended pipeline is:

```text
sources/private evidence -> accepted/rejected YAML -> generated public page
```

## Current TT prototype status

For the tenured/tenure-track prototype run:

- unique candidate arXiv IDs: 234
- source directories fetched/unpacked in the audit archive: 234
- confirmed matches: 226
  - source-positive UVA affiliation evidence: 213
  - manual accepts after source/PDF review: 13
- rejected matches: 8
  - all 8 are Weiqiang Wang name collisions with non-UVA affiliations/topics
- remaining to-check rows: 0
- journal metadata populated for confirmed rows: 226
  - rows with journal name: 106
  - venue-only rows: 1
  - missing journal metadata: 119

Main current review reports:

```text
reports/uva-arxiv-tt-confirmed-matches.md
reports/uva-arxiv-tt-rejected-matches.md
reports/uva-arxiv-tt-to-check.md
reports/uva-arxiv-tt-journal-metadata.md
```

Older `prototype` and `source-confirmed` reports are intermediate snapshots and
should be consolidated before finalizing the workflow.

## Configuration

Shared inputs are configured in `config.yml` and can be overridden locally with
environment variables:

- `ARXIV_DB`
- `ARXIV_SOURCES_DIR`
- `S2_API_KEY` or `SEMANTIC_SCHOLAR_API_KEY`
- `CROSSREF_MAILTO`
- `CROSSREF_API_KEY`
- `OPENALEX_EMAIL`

Local `.env` files are ignored by git. Helpers in `env.py` may load them for
local runs, but they report only whether a key is present and never print key
values.

## Useful commands

There is intentionally only one Makefile target for this infrastructure:

```bash
make uva-arxiv
```

Pass subcommands through `ARGS`:

```bash
python3 -m unittest discover -s scripts/uva_arxiv/tests
make uva-arxiv ARGS="check"
make uva-arxiv ARGS="db-since --dry-run --limit 1"
make uva-arxiv ARGS="review-reports --sync-archive"
make uva-arxiv ARGS="journal-refs --refresh-empty"
make uva-arxiv ARGS="public-data"
make uva-arxiv ARGS="roster-history --dry-run --no-write --as-of YYYY-MM-DD"
make uva-arxiv ARGS="source-fetch --id 2501.01234 --dry-run"
make uva-arxiv ARGS="affiliation-scan --id 2501.01234 --no-cache"
make uva-arxiv ARGS="s2-smoke --id 2501.01234 --refresh"
make uva-arxiv ARGS="crossref-smoke --doi 10.xxxx/example --no-cache"
```

## Next cleanup needed

Before this becomes public:

1. Use `review-reports` as the reproducible internal review build; keep generated
   report files ignored by git and sync private copies to the audit archive when
   useful.
2. Retire old local `prototype` and `source-confirmed` snapshots once we no
   longer need to compare against them.
3. Tighten the public data gate if needed; the preview page currently uses the
   confirmed internal review rows and does not expose source paths/snippets.
4. Add the Bubble Tea/manual review UI as another subcommand behind the single
   `make uva-arxiv ARGS="..."` entry point.
5. Clean remaining SQLite ResourceWarnings in the test suite.

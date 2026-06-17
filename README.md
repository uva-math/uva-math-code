# Mathematics at the University of Virginia

[Official website of Department of Mathematics at the University of Virginia](https://math.virginia.edu/).

The [**documentation**](https://math.virginia.edu/doc/) (including howtos on updating content) is a part of the website.

## UVA Math arXiv Tracker

Phase 1 adds an unlinked `/arxiv/` placeholder and infrastructure for a UVA Mathematics arXiv tracker. It includes shared arXiv DB checks, roster-history extraction, arXiv source-affiliation evidence, and Semantic Scholar/CrossRef smoke caches. It does not publish paper data yet.

Useful commands:

- `make uva-arxiv-check` verifies the configured shared SQLite DB, source corpus path, and API-key presence without printing secret values.
- `make uva-arxiv-db-since-dry` reports the planned `since` update without fetching or writing; set `SINCE=YYYY-MM-DD` and pass extra script flags through `ARGS=...`.
- `make uva-arxiv-db-since` runs the updater; use `ARGS="--limit N"` for smoke updates.
- `make uva-arxiv-roster-history` prints roster-history counts without writing outputs.
- `make uva-arxiv-source-smoke ID=2501.01234` dry-runs one arXiv source fetch.
- `make uva-arxiv-api-smoke ID=2501.01234` runs one Semantic Scholar smoke check.

Direct scripts expose the underlying smoke flags: `update_arxiv_db.py since --db --since --overlap-days --limit --dry-run --source --endpoint`, `sources.py fetch --id --sources-dir --force --dry-run --endpoint`, `roster_history.py --dry-run --no-write --as-of`, and the API clients' `--cache-path`, `--refresh`, and `--no-cache`.

The scripts use Python 3.11+, `git`, `make`, and SQLite. Shared defaults live in `scripts/uva_arxiv/config.yml` and can be overridden with `ARXIV_DB` and `ARXIV_SOURCES_DIR`; ignored `.env` files may also provide `S2_API_KEY`, `SEMANTIC_SCHOLAR_API_KEY`, `CROSSREF_MAILTO`, and `CROSSREF_API_KEY`.

External metadata and evidence caches are stored under `scripts/uva_arxiv/cache/` and are ignored except for `.gitkeep`. Missing Semantic Scholar/CrossRef metadata is incomplete metadata, not publication evidence. Missing or absent UVA source-affiliation evidence is also an evidence state, not a rejection decision.

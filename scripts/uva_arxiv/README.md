# UVA Math arXiv Tracker Infrastructure

This directory contains Phase 1 scaffolding for a permanent UVA Mathematics
arXiv tracker at `/arxiv/`.

Phase 1 is infrastructure only. It prepares configuration, shared-path checks,
roster-history extraction, source-affiliation tooling, API cache clients, and
review data structures. It must not generate the public UVA arXiv paper data,
scan the full arXiv database for candidates, or create related-paper vectors.

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

The manual YAML files under `data/` are intentionally empty or pattern-only in
Phase 1. Public-quality paper inclusion later requires explicit manual approval
records in `accepted_matches.yml`.

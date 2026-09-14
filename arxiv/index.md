---
title: UVA Math arXiv
layout: static_page_no_right_menu
permalink: /arxiv/
published: true
sitemap: false
---

<h1 class="mb-3">UVA Math arXiv</h1>

<div id="uva-arxiv-app" data-data-url="/assets/data/uva-arxiv-papers.json">
  <div class="jumbotron py-3 mb-4">
    <p class="mb-2">
      A preview tracker for arXiv papers by UVA Mathematics faculty, built from the department roster, arXiv metadata, source-affiliation checks, and manual review.
      The page is not linked from site navigation yet while the data workflow is being validated.
    </p>
    <p class="mb-0 small text-muted">
      Source files are used only for private audit checks. Public data here contains arXiv metadata, UVA people, journal metadata when available, and links to arXiv/DOI.
    </p>
  </div>

  <form id="uva-arxiv-search-form" role="search" aria-label="UVA Math arXiv search and filters">
    <label for="uva-arxiv-search-input" class="form-label">Search UVA Math arXiv papers</label>
    <p id="uva-arxiv-search-instructions">Search by author, title, or keyword. Open Search help for advanced filters. Press Escape in the search field to clear.</p>
    <div class="input-group mb-3">
      <input type="search" id="uva-arxiv-search-input" class="form-control" aria-describedby="uva-arxiv-search-instructions" autocomplete="off">
      <button class="btn btn-secondary" type="button" id="uva-arxiv-search-help-btn" aria-expanded="false" aria-controls="uva-arxiv-search-help">Search help</button>
      <button class="btn btn-secondary" type="button" id="uva-arxiv-search-clear" aria-label="Clear search and filters">Clear</button>
    </div>

    <div id="uva-arxiv-search-help" class="uva-arxiv-search-help" hidden>
      <strong>Search operators</strong> &mdash; combine freely with keywords<br>
      <code>au:Morse</code> or <code>au:"Jennifer Morse"</code> &mdash; filter by author<br>
      <code>in:Annals</code> or <code>in:"Advances in Mathematics"</code> &mdash; filter by journal/venue<br>
      <code>cat:math.PR</code> &mdash; filter by arXiv category<br>
      <code>y:2024</code> or <code>y:2021-2024</code> &mdash; filter by arXiv year<br>
      <code>role:faculty</code>, <code>id:2401.12345</code>, <code>doi:10.</code> are also supported.<br>
      Click any author, journal, or category badge to filter. Press Esc to clear.
    </div>

    <div class="d-flex flex-wrap gap-2 mb-3 align-items-center">
      <div>
        <label for="uva-arxiv-date-select" class="form-label">Filter by date</label>
        <select class="form-select" id="uva-arxiv-date-select">
          <option value="all">All time</option>
          <option value="this-week">This week</option>
          <option value="last-week">Last week</option>
          <option value="this-month">This month</option>
          <option value="last-month">Last month</option>
          <option value="this-year">This year</option>
          <option value="last-year">Last year</option>
          <option value="custom">Custom year range</option>
        </select>
      </div>
      <fieldset id="uva-arxiv-year-range" hidden>
        <legend class="h5">Custom year range</legend>
        <p id="uva-arxiv-year-error" role="alert" hidden></p>
        <div class="d-flex flex-wrap gap-2 align-items-end">
          <div><label for="uva-arxiv-year-from">From year</label><input type="number" id="uva-arxiv-year-from" class="form-control" min="1900" max="2099" inputmode="numeric"></div>
          <div><label for="uva-arxiv-year-to">To year</label><input type="number" id="uva-arxiv-year-to" class="form-control" min="1900" max="2099" inputmode="numeric"></div>
          <button class="btn btn-secondary" id="uva-arxiv-year-range-apply" type="button">Apply year range</button>
        </div>
      </fieldset>

      <button id="uva-arxiv-cat-toggle" class="btn btn-sm btn-secondary" type="button" aria-expanded="false" aria-controls="uva-arxiv-cat-panel">
        <span id="uva-arxiv-cat-toggle-label">Filter by category</span>
      </button>
    </div>

    <div id="uva-arxiv-cat-panel" class="mb-3" hidden>
      <div id="uva-arxiv-cat-buttons" class="d-flex flex-wrap gap-2" role="group" aria-label="Filter by arXiv category"></div>
    </div>
  </form>

  <div id="uva-arxiv-status" class="visually-hidden" role="status" aria-live="polite" aria-atomic="true"></div>
  <div id="uva-arxiv-loading" class="alert alert-info" role="status">Loading UVA Math arXiv data…</div>

  <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-2">
    <p id="uva-arxiv-count" class="text-muted mb-0 small">Showing 0 of 0 papers</p>
    <p class="text-muted mb-0 small">First pass: tenured/tenure-track faculty since August 2021.</p>
  </div>

  <ul id="uva-arxiv-list" class="uva-arxiv-list" style="list-style:none;padding-left:0" aria-label="UVA Math arXiv papers"></ul>

  <div id="uva-arxiv-no-results" class="alert alert-info mt-4" hidden>
    No results found. Try adjusting your search or filters.
  </div>

  <div class="text-center my-4">
    <button type="button" id="uva-arxiv-load-more" class="btn btn-secondary" hidden>Load more papers</button>
  </div>
</div>

<button type="button" class="btn btn-secondary uva-arxiv-back-top" id="uva-arxiv-back-top" >Back to search</button>


<style>
  .uva-arxiv-month-header {
    padding: .6rem .4rem .2rem;
    border-bottom: 2px solid var(--border-color, #767676);
    margin-top: 1rem;
  }
  .uva-arxiv-month-header h2 { margin: 0; font-size: 1.25rem; }
  .uva-arxiv-list li[data-id] {
    border-bottom: 1px solid var(--border-color, #767676);
    padding: 1rem .5rem;
  }
  .uva-arxiv-list li[data-id]:nth-child(odd) { background: var(--card-bg, #f8f9fa); }
  .uva-arxiv-entry { display: flex; gap: 1rem; }
  .uva-arxiv-date-col { flex: 0 0 10rem; font-size: 1rem; }
  .uva-arxiv-id-label { overflow-wrap: anywhere; }
  .uva-arxiv-body { flex: 1; min-width: 0; }
  .uva-arxiv-title { font-size: 1.2rem; text-transform: none; }
  .uva-arxiv-tags, .uva-arxiv-people, .uva-arxiv-links {
    display: flex; flex-wrap: wrap; gap: .4rem; margin: .5rem 0;
  }
  .uva-arxiv-link-badge, .uva-arxiv-cat-badge, .uva-arxiv-person-badge {
    font-size: 1rem; line-height: 1.5; font-weight: normal;
    padding: .25rem .5rem; min-height: 24px;
    color: #fff !important; background: #232d4b;
    white-space: normal; text-align: left; overflow-wrap: anywhere;
  }
  .uva-arxiv-link-badge { text-decoration: underline !important; }
  .uva-arxiv-cat-badge, button.uva-arxiv-link-badge { border: 1px solid currentColor; }
  .uva-arxiv-author-name {
    font: inherit; min-height: 24px; border: 0; padding: 0 .15rem;
    background: transparent; color: var(--link-color, #245d91);
    text-decoration: underline;
  }
  .uva-arxiv-abstract-toggle { display: list-item; cursor: pointer; font-size: 1rem; }
  .uva-arxiv-abstract { padding: .5rem .75rem; border-left: 3px solid var(--border-color, #767676); }
  .uva-arxiv-journal-ref { margin-top: .75rem; }
  .uva-arxiv-search-help { padding: 1rem; border: 1px solid var(--border-color, #767676); margin-bottom: 1rem; }
  .uva-arxiv-cat-count { font-size: 1rem; }
  .uva-arxiv-cat-count::before { content: "("; }
  .uva-arxiv-cat-count::after { content: ")"; }
  #uva-arxiv-year-range input { width: 8rem; }
  @media (max-width: 767px) {
    .uva-arxiv-entry { display: block; }
    .uva-arxiv-date-col { margin-bottom: .5rem; }
    #uva-arxiv-search-form .input-group { flex-wrap: wrap; }
    #uva-arxiv-search-input { flex-basis: 100%; }
  }
</style>

<script src="/assets/js/uva-arxiv.js" defer></script>

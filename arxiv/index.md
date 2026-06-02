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

  <search aria-label="UVA Math arXiv search and filters">
    <div class="input-group mb-3">
      <label for="uva-arxiv-search-input" class="visually-hidden">Search UVA Math arXiv papers</label>
      <input type="text" id="uva-arxiv-search-input" class="form-control" placeholder="Search… au:Morse in:Advances cat:math.AG y:2024 (Esc to clear)" aria-label="Search UVA Math arXiv papers" autocomplete="off">
      <button class="btn btn-outline-secondary" type="button" id="uva-arxiv-search-help-btn" aria-label="Search help" aria-expanded="false" title="Search syntax help">?</button>
      <button class="btn btn-outline-secondary" type="button" id="uva-arxiv-search-clear" aria-label="Clear search and filters">Clear</button>
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
      <div id="uva-arxiv-date-filter" class="uva-arxiv-dropdown">
        <button class="btn btn-sm btn-outline-secondary uva-arxiv-dropdown-btn" type="button" id="uva-arxiv-date-btn" aria-haspopup="true" aria-expanded="false">
          <span id="uva-arxiv-date-label">All time</span> <span class="uva-arxiv-dropdown-arrow" aria-hidden="true">&#9662;</span>
        </button>
        <div class="uva-arxiv-dropdown-menu" id="uva-arxiv-date-menu" role="menu">
          <button class="uva-arxiv-dropdown-item active" role="menuitem" data-date="all">All time</button>
          <hr class="uva-arxiv-dropdown-divider">
          <button class="uva-arxiv-dropdown-item" role="menuitem" data-date="this-week">This week</button>
          <button class="uva-arxiv-dropdown-item" role="menuitem" data-date="last-week">Last week</button>
          <button class="uva-arxiv-dropdown-item" role="menuitem" data-date="this-month">This month</button>
          <button class="uva-arxiv-dropdown-item" role="menuitem" data-date="last-month">Last month</button>
          <button class="uva-arxiv-dropdown-item" role="menuitem" data-date="this-year">This year</button>
          <button class="uva-arxiv-dropdown-item" role="menuitem" data-date="last-year">Last year</button>
          <hr class="uva-arxiv-dropdown-divider">
          <div class="uva-arxiv-dropdown-custom" role="menuitem">
            <span class="uva-arxiv-dropdown-custom-label">Custom year range</span>
            <div class="uva-arxiv-dropdown-custom-inputs">
              <input type="text" id="uva-arxiv-year-from" class="form-control form-control-sm" placeholder="From" maxlength="4" size="4" aria-label="From year">
              <span>&ndash;</span>
              <input type="text" id="uva-arxiv-year-to" class="form-control form-control-sm" placeholder="To" maxlength="4" size="4" aria-label="To year">
              <button class="btn btn-sm btn-outline-primary" id="uva-arxiv-year-range-apply" type="button">Go</button>
            </div>
          </div>
        </div>
      </div>

      <button id="uva-arxiv-cat-toggle" class="btn btn-sm btn-outline-secondary" type="button" aria-expanded="false" aria-controls="uva-arxiv-cat-panel">
        <span id="uva-arxiv-cat-toggle-label">Filter by category</span>
      </button>
    </div>

    <div id="uva-arxiv-cat-panel" class="mb-3" hidden>
      <div id="uva-arxiv-cat-buttons" class="d-flex flex-wrap gap-2" role="group" aria-label="Filter by arXiv category"></div>
    </div>
  </search>

  <div id="uva-arxiv-status" class="visually-hidden" role="status" aria-live="polite"></div>
  <div id="uva-arxiv-loading" class="alert alert-info" role="status">Loading UVA Math arXiv data…</div>

  <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-2">
    <p id="uva-arxiv-count" class="text-muted mb-0 small">Showing 0 of 0 papers</p>
    <p class="text-muted mb-0 small">First pass: tenured/tenure-track faculty since August 2021.</p>
  </div>

  <ul id="uva-arxiv-list" class="uva-arxiv-list" style="list-style:none;padding-left:0" aria-label="UVA Math arXiv papers"></ul>

  <div id="uva-arxiv-no-results" class="alert alert-info mt-4" role="alert" hidden>
    No results found. Try adjusting your search or filters.
  </div>

  <div class="text-center my-4">
    <button type="button" id="uva-arxiv-load-more" class="btn btn-outline-secondary" hidden>Load more papers</button>
  </div>
</div>

<button class="uva-arxiv-back-top" id="uva-arxiv-back-top" aria-label="Back to top">&#9650;</button>

<style>
  .uva-arxiv-month-header {
    padding: 0.6em 6px 0.2em;
    border-bottom: 2px solid #ccc;
    margin-top: 0.5em;
  }
  .uva-arxiv-month-header h2 {
    margin: 0;
    font-size: 1.15em;
    color: #002F6C;
  }
  .uva-arxiv-list li[data-id]:nth-child(odd) {
    background-color: var(--bg-secondary, #f8f9fa);
  }
  .uva-arxiv-list li[data-id] {
    border-bottom: 1px solid #e9ecef;
    padding: 10px 8px;
  }
  .uva-arxiv-entry {
    display: flex;
    gap: 1em;
  }
  .uva-arxiv-date-col {
    flex-shrink: 0;
    width: 7.5em;
    font-weight: bold;
    color: #222;
    font-size: 0.95em;
    padding-top: 1px;
  }
  a.uva-arxiv-id-label {
    font-size: 0.78em;
    font-weight: normal;
    color: #767676;
    text-decoration: underline;
  }
  a.uva-arxiv-id-label:hover { color: #b31b1b; }
  .uva-arxiv-body { flex: 1; min-width: 0; }
  .uva-arxiv-body strong { font-weight: 500; color: #111; }
  .uva-arxiv-tags { margin-bottom: 0.15rem; }
  .uva-arxiv-link-badge,
  .uva-arxiv-cat-badge,
  .uva-arxiv-person-badge {
    color: #fff !important;
    font-size: 0.75em;
    font-weight: normal;
    margin-right: 3px;
    text-decoration: none !important;
    border: 0;
    vertical-align: middle;
  }
  .uva-arxiv-cat-badge { background-color: #495057; cursor: pointer; }
  .uva-arxiv-cat-badge:hover { opacity: 0.82; }
  .uva-arxiv-person-badge { background-color: #002F6C; cursor: pointer; }
  .uva-arxiv-person-badge:hover { background-color: #001f49; }
  .uva-arxiv-author-name {
    border: 0;
    padding: 0;
    background: transparent;
    color: inherit;
    font-weight: 500;
    cursor: pointer;
  }
  .uva-arxiv-author-name:hover { text-decoration: underline; color: #2A69A6; }
  .uva-arxiv-link-badge { margin-left: 3px; }
  .uva-arxiv-link-abs { background-color: #b31b1b; }
  .uva-arxiv-link-pdf { background-color: #1a5276; }
  .uva-arxiv-link-html { background-color: #0e7c86; }
  .uva-arxiv-link-doi { background-color: #2e7d32; }
  .uva-arxiv-link-journal {
    background-color: #2e7d32;
    max-width: 22em;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    cursor: pointer;
  }
  button.uva-arxiv-link-journal { border: 0; }
  .uva-arxiv-title { cursor: pointer; }
  .uva-arxiv-title:hover { text-decoration: underline; }
  .uva-arxiv-title:focus-visible {
    outline: 2px solid #e57200;
    outline-offset: 2px;
    border-radius: 2px;
  }
  .uva-arxiv-abstract-toggle {
    cursor: pointer;
    color: #1a5276;
    text-decoration: underline;
    display: inline;
    font-size: 0.9em;
  }
  .uva-arxiv-abstract {
    margin-top: 0.5em;
    padding: 0.5em 0.75em;
    border-left: 3px solid #ccc;
    font-size: 0.92em;
    line-height: 1.5;
  }
  .uva-arxiv-journal-ref {
    margin-top: 0.5em;
    font-size: 0.9em;
    color: #555;
  }
  .uva-arxiv-dropdown-btn,
  #uva-arxiv-cat-toggle {
    display: inline-flex;
    align-items: center;
    gap: 0.4em;
    min-height: 34px;
    white-space: nowrap;
    font-size: 0.88em;
    color: #232d4b !important;
    border-color: #232d4b !important;
    background: transparent;
  }
  .uva-arxiv-dropdown-btn:hover,
  #uva-arxiv-cat-toggle:hover {
    background: #232d4b !important;
    color: #fff !important;
  }
  .uva-arxiv-dropdown { position: relative; display: inline-block; }
  .uva-arxiv-dropdown-arrow { font-size: 0.7em; }
  .uva-arxiv-dropdown-menu {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    z-index: 100;
    min-width: 220px;
    margin-top: 2px;
    padding: 4px 0;
    background: #fff;
    border: 1px solid #bbb;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }
  .uva-arxiv-dropdown-menu.open { display: block; }
  .uva-arxiv-dropdown-item {
    display: block;
    width: 100%;
    padding: 7px 14px;
    text-align: left;
    background: none;
    border: none;
    font-size: 0.92em;
    cursor: pointer;
    color: #222;
  }
  .uva-arxiv-dropdown-item:hover { background: #e9ecef; }
  .uva-arxiv-dropdown-item.active { font-weight: 700; color: #b45309; }
  .uva-arxiv-dropdown-divider { margin: 4px 0; border: none; border-top: 1px solid #ddd; }
  .uva-arxiv-dropdown-custom { padding: 7px 14px; }
  .uva-arxiv-dropdown-custom-label { font-size: 0.85em; color: #555; display: block; margin-bottom: 4px; }
  .uva-arxiv-dropdown-custom-inputs { display: flex; align-items: center; gap: 6px; }
  .uva-arxiv-dropdown-custom-inputs input { width: 60px; text-align: center; }
  #uva-arxiv-cat-toggle.has-filter,
  .uva-arxiv-dropdown-btn.has-filter {
    background: #e57200 !important;
    color: #fff !important;
    border-color: #e57200 !important;
  }
  .uva-arxiv-cat-count { font-size: 0.78em; font-weight: normal; opacity: 0.8; }
  .uva-arxiv-cat-count::before { content: "("; }
  .uva-arxiv-cat-count::after { content: ")"; }
  .uva-arxiv-search-help {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 10px 14px;
    margin-bottom: 12px;
    font-size: 0.9em;
    line-height: 1.7;
  }
  .uva-arxiv-search-help code { background: #e9ecef; padding: 1px 5px; border-radius: 3px; font-size: 0.95em; }
  #uva-arxiv-search-help-btn { font-weight: bold; min-width: 2.2em; }
  .uva-arxiv-back-top { display: none; }
  @media (max-width: 767px) {
    .uva-arxiv-date-col { width: 5.5em; font-size: 0.88em; }
    .uva-arxiv-entry { gap: 0.5em; }
    .uva-arxiv-abstract-toggle,
    .uva-arxiv-dropdown-btn,
    #uva-arxiv-cat-toggle { min-height: 44px; }
    .uva-arxiv-back-top.visible {
      display: block;
      position: fixed;
      top: 10px;
      right: 10px;
      z-index: 200;
      width: 36px;
      height: 36px;
      border: none;
      border-radius: 50%;
      background: rgba(35,45,75,0.75);
      color: #fff;
      font-size: 18px;
      line-height: 36px;
      text-align: center;
      cursor: pointer;
      box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }
  }
  [data-theme="dark"] #uva-arxiv-app {
    color: var(--text-color, #e8e8e8);
  }
  [data-theme="dark"] #uva-arxiv-app .jumbotron {
    background: #1a2a3f;
    color: #e8e8e8;
  }
  [data-theme="dark"] #uva-arxiv-app .text-muted,
  [data-theme="dark"] .uva-arxiv-dropdown-custom-label {
    color: #b8c4d6 !important;
  }
  [data-theme="dark"] .uva-arxiv-month-header h2,
  [data-theme="dark"] .uva-arxiv-date-col,
  [data-theme="dark"] .uva-arxiv-body strong,
  [data-theme="dark"] .uva-arxiv-author-name { color: #f1f5f9; }
  [data-theme="dark"] a.uva-arxiv-id-label { color: #7fb3ff; }
  [data-theme="dark"] .uva-arxiv-list li[data-id] {
    background: transparent;
    border-bottom-color: #33445c;
  }
  [data-theme="dark"] .uva-arxiv-list li[data-id]:nth-child(odd) {
    background: #162133;
  }
  [data-theme="dark"] .uva-arxiv-list li[data-id]:hover {
    background: #1a2a3f;
  }
  [data-theme="dark"] #uva-arxiv-search-input,
  [data-theme="dark"] .uva-arxiv-dropdown-custom-inputs input {
    background: #162133;
    border-color: #50647f;
    color: #f1f5f9;
  }
  [data-theme="dark"] #uva-arxiv-search-input::placeholder,
  [data-theme="dark"] .uva-arxiv-dropdown-custom-inputs input::placeholder {
    color: #9fb0c5;
    opacity: 1;
  }
  [data-theme="dark"] #uva-arxiv-search-help-btn,
  [data-theme="dark"] #uva-arxiv-search-clear,
  [data-theme="dark"] #uva-arxiv-load-more,
  [data-theme="dark"] #uva-arxiv-app .btn-outline-secondary,
  [data-theme="dark"] .uva-arxiv-dropdown-btn,
  [data-theme="dark"] #uva-arxiv-cat-toggle {
    color: #dce8f8 !important;
    border-color: #7d91ad !important;
    background: #162133;
  }
  [data-theme="dark"] #uva-arxiv-search-help-btn:hover,
  [data-theme="dark"] #uva-arxiv-search-clear:hover,
  [data-theme="dark"] #uva-arxiv-load-more:hover,
  [data-theme="dark"] #uva-arxiv-app .btn-outline-secondary:hover,
  [data-theme="dark"] .uva-arxiv-dropdown-btn:hover,
  [data-theme="dark"] #uva-arxiv-cat-toggle:hover {
    background: #243448 !important;
    color: #fff !important;
  }
  [data-theme="dark"] .uva-arxiv-dropdown-menu,
  [data-theme="dark"] .uva-arxiv-search-help {
    background: #162133;
    border-color: #50647f;
    color: #e8e8e8;
  }
  [data-theme="dark"] .uva-arxiv-dropdown-item { color: #e8e8e8; }
  [data-theme="dark"] .uva-arxiv-dropdown-item:hover,
  [data-theme="dark"] .uva-arxiv-search-help code { background: #243448; }
  [data-theme="dark"] .uva-arxiv-dropdown-divider,
  [data-theme="dark"] .uva-arxiv-month-header { border-color: #50647f; }
  [data-theme="dark"] .uva-arxiv-author-name:hover,
  [data-theme="dark"] .uva-arxiv-abstract-toggle { color: #7fb3ff; }
  [data-theme="dark"] .uva-arxiv-abstract { border-left-color: #50647f; }
  [data-theme="dark"] .uva-arxiv-journal-ref { color: #cbd5e1; }
</style>

<script src="/assets/js/uva-arxiv.js" defer></script>

(function () {
  'use strict';

  var state = {
    papers: [],
    filtered: [],
    rendered: 0,
    activeCategory: 'all',
    activeDate: 'all',
    customFrom: null,
    customTo: null,
    searchTimer: null,
    batchSize: 40,
    initialBatch: 80
  };

  function $(id) { return document.getElementById(id); }

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function normalizeText(value) {
    return String(value || '')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/[^a-z0-9.:-]+/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function monthLabel(ym) {
    if (!ym || ym.length < 7) return '';
    var d = new Date(ym + '-02T00:00:00');
    if (isNaN(d.getTime())) return ym;
    return d.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
  }

  function yearOf(dateString) {
    var m = String(dateString || '').match(/^((?:19|20)\d{2})/);
    return m ? parseInt(m[1], 10) : null;
  }

  function parseDate(dateString) {
    var d = new Date(String(dateString || '') + 'T00:00:00');
    return isNaN(d.getTime()) ? null : d;
  }

  function addDays(date, days) {
    var d = new Date(date.getTime());
    d.setDate(d.getDate() + days);
    return d;
  }

  function inDateFilter(paper) {
    if (state.activeDate === 'all') return true;
    var d = parseDate(paper.date);
    if (!d) return true;
    var now = new Date();
    now.setHours(0, 0, 0, 0);
    var y = now.getFullYear();
    var start, end;
    if (state.activeDate === 'this-week') {
      var day = now.getDay() || 7;
      start = addDays(now, 1 - day);
      end = addDays(start, 7);
    } else if (state.activeDate === 'last-week') {
      var day2 = now.getDay() || 7;
      end = addDays(now, 1 - day2);
      start = addDays(end, -7);
    } else if (state.activeDate === 'this-month') {
      start = new Date(y, now.getMonth(), 1);
      end = new Date(y, now.getMonth() + 1, 1);
    } else if (state.activeDate === 'last-month') {
      start = new Date(y, now.getMonth() - 1, 1);
      end = new Date(y, now.getMonth(), 1);
    } else if (state.activeDate === 'this-year') {
      start = new Date(y, 0, 1);
      end = new Date(y + 1, 0, 1);
    } else if (state.activeDate === 'last-year') {
      start = new Date(y - 1, 0, 1);
      end = new Date(y, 0, 1);
    } else if (state.activeDate === 'custom') {
      var py = yearOf(paper.date);
      if (!py) return true;
      if (state.customFrom && py < state.customFrom) return false;
      if (state.customTo && py > state.customTo) return false;
      return true;
    }
    return start && end ? d >= start && d < end : true;
  }

  function tokenizeQuery(query) {
    var tokens = [];
    var re = /([a-zA-Z]+):"([^"]*)"|([a-zA-Z]+):([^\s]+)|"([^"]*)"|(\S+)/g;
    var m;
    while ((m = re.exec(query || '')) !== null) {
      if (m[1]) tokens.push({ op: m[1].toLowerCase(), value: m[2] || '' });
      else if (m[3]) tokens.push({ op: m[3].toLowerCase(), value: m[4] || '' });
      else tokens.push({ op: null, value: m[5] || m[6] || '' });
    }
    return tokens;
  }

  function parseYearFilter(value) {
    var m = String(value || '').match(/^((?:19|20)\d{2})(?:-((?:19|20)\d{2}))?$/);
    if (!m) return null;
    var a = parseInt(m[1], 10);
    var b = m[2] ? parseInt(m[2], 10) : a;
    return { from: Math.min(a, b), to: Math.max(a, b) };
  }

  function paperSearchText(paper) {
    return normalizeText([
      paper.id,
      paper.title,
      paper.authors_text,
      (paper.authors || []).join(' '),
      paper.abstract,
      (paper.categories || []).join(' '),
      paper.journal_name,
      paper.journal_full,
      paper.journal_name_raw,
      paper.journal_ref,
      paper.doi,
      (paper.person_names || []).join(' '),
      (paper.person_ids || []).join(' '),
      (paper.role_labels || []).join(' ')
    ].join(' '));
  }

  function matchesOperator(paper, token) {
    var op = token.op;
    var val = normalizeText(token.value);
    if (!val && op !== 'published' && op !== 'preprint') return true;
    if (op === 'au') return normalizeText((paper.authors || []).join(' ')).indexOf(val) !== -1;
    if (op === 'role') return normalizeText((paper.roles || []).join(' ') + ' ' + (paper.role_labels || []).join(' ')).indexOf(val) !== -1;
    if (op === 'in' || op === 'j') return normalizeText((paper.journal_name || '') + ' ' + (paper.journal_full || '') + ' ' + (paper.journal_name_raw || '') + ' ' + (paper.journal_ref || '') + ' ' + (paper.venue || '')).indexOf(val) !== -1;
    if (op === 'cat' || op === 'category') return normalizeText((paper.categories || []).join(' ')).indexOf(val) !== -1;
    if (op === 'id') return normalizeText(paper.id).indexOf(val) !== -1;
    if (op === 'doi') return normalizeText(paper.doi).indexOf(val) !== -1;
    if (op === 'y' || op === 'year') {
      var range = parseYearFilter(token.value);
      var py = yearOf(paper.date);
      return !range || !py ? true : py >= range.from && py <= range.to;
    }
    if (op === 'status') return normalizeText(paper.journal_status).indexOf(val) !== -1;
    return paperSearchText(paper).indexOf(normalizeText(token.value)) !== -1;
  }

  function paperMatches(paper, tokens) {
    if (state.activeCategory !== 'all' && (paper.categories || []).indexOf(state.activeCategory) === -1) return false;
    if (!inDateFilter(paper)) return false;
    for (var i = 0; i < tokens.length; i++) {
      if (!matchesOperator(paper, tokens[i])) return false;
    }
    return true;
  }

  function setSearch(value) {
    var input = $('uva-arxiv-search-input');
    if (!input) return;
    input.value = value;
    applyFilters(true);
    input.focus();
  }

  function appendSearch(value) { setSearch(value); }

  function categoryCounts() {
    var counts = {};
    state.papers.forEach(function (paper) {
      (paper.categories || []).forEach(function (cat) { counts[cat] = (counts[cat] || 0) + 1; });
    });
    return counts;
  }

  function buildCategoryButtons() {
    var wrap = $('uva-arxiv-cat-buttons');
    if (!wrap) return;
    var counts = categoryCounts();
    var cats = Object.keys(counts).sort(function (a, b) {
      if (counts[b] !== counts[a]) return counts[b] - counts[a];
      return a.localeCompare(b);
    });
    var focusedCategory = wrap.contains(document.activeElement) ? document.activeElement.dataset.category : null;
    wrap.innerHTML = '';
    var all = document.createElement('button');
    all.type = 'button';
    all.dataset.category = 'all';
    all.setAttribute('aria-pressed', String(state.activeCategory === 'all'));
    all.className = 'btn btn-sm category-btn ' + (state.activeCategory === 'all' ? 'btn-primary active' : 'btn-secondary');
    all.textContent = 'All categories (' + state.papers.length + ')';
    all.addEventListener('click', function () { state.activeCategory = 'all'; buildCategoryButtons(); applyFilters(true); });
    wrap.appendChild(all);
    cats.forEach(function (cat) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.dataset.category = cat;
      btn.setAttribute('aria-pressed', String(state.activeCategory === cat));
      btn.className = 'btn btn-sm category-btn ' + (state.activeCategory === cat ? 'btn-primary active' : 'btn-secondary');
      btn.innerHTML = escapeHtml(cat) + ' <span class="uva-arxiv-cat-count">' + counts[cat] + '</span>';
      btn.addEventListener('click', function () { state.activeCategory = cat; buildCategoryButtons(); applyFilters(true); });
      wrap.appendChild(btn);
    });
    if (focusedCategory) Array.from(wrap.children).find(function (button) { return button.dataset.category === focusedCategory; })?.focus();
  }

  function authorHtml(paper) {
    var authors = paper.authors && paper.authors.length ? paper.authors : [paper.authors_text || ''];
    return authors.map(function (author) {
      var label = escapeHtml(author);
      return '<button type="button" class="uva-arxiv-author-name" aria-label="Filter papers by author ' + escapeHtml(author) + '" data-author="' + escapeHtml(author) + '">' + label + '</button>';
    }).join(', ');
  }

  function peopleHtml(paper) {
    if (!paper.people || !paper.people.length) return '';
    return paper.people.map(function (person) {
      return '<span class="badge uva-arxiv-person-badge">UVA: ' + escapeHtml(person.name) + '</span>';
    }).join(' ');
  }

  function categoryHtml(paper) {
    return (paper.categories || []).map(function (cat) {
      return '<button type="button" class="badge uva-arxiv-cat-badge" aria-label="Filter papers by category ' + escapeHtml(cat) + '" data-cat="' + escapeHtml(cat) + '">' + escapeHtml(cat) + '</button>';
    }).join(' ');
  }

  function journalBadgeHtml(paper) {
    if (!paper.journal_name) return '';
    var label = paper.journal_name;
    if (paper.publication_year && label.indexOf(String(paper.publication_year)) === -1) label += ' ' + paper.publication_year;
    var filterName = paper.journal_full || paper.journal_name;
    var title = paper.journal_ref || paper.journal_full || paper.journal_name;
    var attrs = ' class="badge uva-arxiv-link-badge uva-arxiv-link-journal" data-journal="' + escapeHtml(filterName) + '" aria-label="Filter papers by journal: ' + escapeHtml(title) + '"';
    return '<button type="button"' + attrs + '>' + escapeHtml(label) + '</button>';
  }

  function linkBadgesHtml(paper) {
    var title = escapeHtml(paper.title);
    var html = '<a href="https://arxiv.org/pdf/' + encodeURIComponent(paper.id) + '" aria-label="PDF: ' + title + '" class="badge uva-arxiv-link-badge uva-arxiv-link-pdf">PDF</a>';
    html += '<a href="https://arxiv.org/html/' + encodeURIComponent(paper.id) + '" aria-label="HTML: ' + title + '" class="badge uva-arxiv-link-badge uva-arxiv-link-html">HTML</a>';
    if (paper.doi) html += '<a href="https://doi.org/' + encodeURIComponent(paper.doi) + '" aria-label="Published version: ' + title + '" class="badge uva-arxiv-link-badge uva-arxiv-link-doi">Published version</a>';
    return html;
  }

  function renderPaper(paper) {
    var li = document.createElement('li');
    li.className = 'mb-1';
    li.dataset.id = paper.id;
    li.dataset.month = paper.month;
    li.innerHTML =
      '<article class="uva-arxiv-entry">' +
      '  <div class="uva-arxiv-date-col"><time datetime="' + escapeHtml(paper.date) + '">' + escapeHtml(paper.date) + '</time><br><span class="uva-arxiv-id-label">arXiv:' + escapeHtml(paper.id) + '</span></div>' +
      '  <div class="uva-arxiv-body">' +
      '    <h3 class="uva-arxiv-title"><a href="https://arxiv.org/abs/' + encodeURIComponent(paper.id) + '">' + escapeHtml(paper.title) + '</a></h3>' +
      '    <p>' + authorHtml(paper) + '</p>' +
      '    <div class="uva-arxiv-tags">' + categoryHtml(paper) + ' ' + journalBadgeHtml(paper) + '</div>' +
      '    <p class="uva-arxiv-links">' + linkBadgesHtml(paper) + '</p>' +
      '    <div class="uva-arxiv-people mt-1">' + peopleHtml(paper) + '</div>' +
      (paper.abstract ? '    <details class="uva-arxiv-abstract-wrap"><summary class="uva-arxiv-abstract-toggle" aria-label="Abstract: ' + escapeHtml(paper.title) + '">Abstract</summary><div class="uva-arxiv-abstract">' + escapeHtml(paper.abstract) + (paper.journal_ref ? '<p class="uva-arxiv-journal-ref">Published in: ' + escapeHtml(paper.journal_ref) + '</p>' : '') + '</div></details>' : '') +
      '  </div>' +
      '</article>';
    return li;
  }

  function renderMath(root) {
    if (!window.renderMathInElement) return;
    try {
      window.renderMathInElement(root, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true }
        ],
        output: 'htmlAndMathml',
        trust: false,
        errorColor: 'inherit',
        throwOnError: false
      });
    } catch (e) { /* ignore rendering errors */ }
  }

  function renderList(reset) {
    var list = $('uva-arxiv-list');
    if (!list) return;
    if (reset) {
      list.innerHTML = '';
      state.rendered = 0;
      list.dataset.lastMonth = '';
    }
    var target = Math.min(state.filtered.length, state.rendered + (state.rendered ? state.batchSize : state.initialBatch));
    var lastMonth = list.dataset.lastMonth || '';
    var frag = document.createDocumentFragment();
    for (var i = state.rendered; i < target; i++) {
      var paper = state.filtered[i];
      if (paper.month !== lastMonth) {
        lastMonth = paper.month;
        var header = document.createElement('li');
        header.className = 'uva-arxiv-month-header';
        header.innerHTML = '<h2>' + escapeHtml(monthLabel(paper.month)) + '</h2>';
        frag.appendChild(header);
      }
      frag.appendChild(renderPaper(paper));
    }
    list.dataset.lastMonth = lastMonth;
    list.appendChild(frag);
    state.rendered = target;
    renderMath(list);
    updateLoadMore();
  }

  function updateLoadMore() {
    var btn = $('uva-arxiv-load-more');
    var count = $('uva-arxiv-count');
    var noResults = $('uva-arxiv-no-results');
    if (btn) btn.hidden = state.rendered >= state.filtered.length;
    if (count) count.textContent = 'Showing ' + state.rendered + ' of ' + state.filtered.length + ' papers';
    if (noResults) noResults.hidden = state.filtered.length !== 0;
    var status = $('uva-arxiv-status');
    if (status) status.textContent = state.filtered.length ? 'Showing ' + state.rendered + ' of ' + state.filtered.length + ' matching papers.' : 'No papers match the current filters.';
  }

  function applyFilters(reset) {
    var input = $('uva-arxiv-search-input');
    var tokens = tokenizeQuery(input ? input.value : '');
    state.filtered = state.papers.filter(function (paper) { return paperMatches(paper, tokens); });
    renderList(reset !== false);
    updateFilterButtons();
  }

  function updateFilterButtons() {
    var catToggle = $('uva-arxiv-cat-toggle');
    if (catToggle) {
      catToggle.classList.toggle('has-filter', state.activeCategory !== 'all');
      var label = $('uva-arxiv-cat-toggle-label');
      if (label) label.textContent = state.activeCategory === 'all' ? 'Filter by category' : 'Category: ' + state.activeCategory;
    }
  }

  function setDateFilter(value, label) {
    state.activeDate = value;
    var dateLabel = $('uva-arxiv-date-label');
    if (dateLabel) dateLabel.textContent = label;
    var select = $('uva-arxiv-date-select');
    if (select) select.value = value;
    applyFilters(true);
  }


  function wireEvents() {
    var input = $('uva-arxiv-search-input');
    var searchForm = $('uva-arxiv-search-form');
    if (searchForm) searchForm.addEventListener('submit', function (event) { event.preventDefault(); applyFilters(true); });
    var dateSelect = $('uva-arxiv-date-select');
    if (dateSelect) dateSelect.addEventListener('change', function () {
      $('uva-arxiv-year-range').hidden = this.value !== 'custom';
      if (this.value !== 'custom') setDateFilter(this.value, this.options[this.selectedIndex].text);
    });
    var clear = $('uva-arxiv-search-clear');
    var helpBtn = $('uva-arxiv-search-help-btn');
    var help = $('uva-arxiv-search-help');
    var catToggle = $('uva-arxiv-cat-toggle');
    var catPanel = $('uva-arxiv-cat-panel');
    var dateBtn = $('uva-arxiv-date-btn');
    var yearFrom = $('uva-arxiv-year-from');
    var yearTo = $('uva-arxiv-year-to');
    var yearApply = $('uva-arxiv-year-range-apply');
    var yearError = $('uva-arxiv-year-error');
    [yearFrom, yearTo].forEach(function (field) {
      if (field) field.addEventListener('input', function () { yearError.hidden = true; yearFrom.removeAttribute('aria-invalid'); yearTo.removeAttribute('aria-invalid'); });
    });
    var loadMore = $('uva-arxiv-load-more');
    var list = $('uva-arxiv-list');
    var backTop = $('uva-arxiv-back-top');

    if (input) {
      input.addEventListener('input', function () {
        clearTimeout(state.searchTimer);
        state.searchTimer = setTimeout(function () { applyFilters(true); }, 120);
      });
    }
    function clearAllAndFocus() {
      if (input) {
        input.value = '';
        input.focus();
      }
      state.activeCategory = 'all';
      state.activeDate = 'all';
      state.customFrom = null;
      state.customTo = null;
      var label = $('uva-arxiv-date-label');
      if (label) label.textContent = 'All time';
      if (dateSelect) dateSelect.value = 'all';
      if (yearFrom) yearFrom.value = '';
      if (yearTo) yearTo.value = '';
      $('uva-arxiv-year-range').hidden = true;
      yearError.hidden = true;
      yearFrom.removeAttribute('aria-invalid');
      yearTo.removeAttribute('aria-invalid');
      buildCategoryButtons();
      applyFilters(true);
    }
    if (clear) clear.addEventListener('click', clearAllAndFocus);
    if (input) input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        e.preventDefault();
        clearAllAndFocus();
      }
    });
    if (helpBtn && help) helpBtn.addEventListener('click', function () {
      help.hidden = !help.hidden;
      helpBtn.setAttribute('aria-expanded', help.hidden ? 'false' : 'true');
    });
    if (catToggle && catPanel) catToggle.addEventListener('click', function () {
      catPanel.hidden = !catPanel.hidden;
      catToggle.setAttribute('aria-expanded', catPanel.hidden ? 'false' : 'true');
    });
    if (yearApply) yearApply.addEventListener('click', function () {
      state.customFrom = yearFrom && yearFrom.value ? parseInt(yearFrom.value, 10) : null;
      state.customTo = yearTo && yearTo.value ? parseInt(yearTo.value, 10) : null;
      if (!yearFrom.checkValidity() || !yearTo.checkValidity() || (state.customFrom && state.customTo && state.customFrom > state.customTo)) {
        yearError.textContent = 'Enter years from 1900 to 2099, with the first year no later than the last year.';
        yearError.hidden = false;
        yearFrom.setAttribute('aria-invalid', 'true');
        yearFrom.focus();
        return;
      }
      var label = (state.customFrom || '…') + '–' + (state.customTo || '…');
      setDateFilter('custom', label);
    });
    if (loadMore) loadMore.addEventListener('click', function () {
      var firstNew = state.rendered;
      renderList(false);
      var papers = list.querySelectorAll('li[data-id] .uva-arxiv-title a');
      if (papers[firstNew]) papers[firstNew].focus();
    });
    if (list) list.addEventListener('click', function (e) {
      var author = e.target.closest('.uva-arxiv-author-name');
      var cat = e.target.closest('.uva-arxiv-cat-badge');
      var journal = e.target.closest('.uva-arxiv-link-journal');
      if (author) appendSearch('au:"' + author.dataset.author + '"');
      else if (cat) { state.activeCategory = cat.dataset.cat; buildCategoryButtons(); applyFilters(true); if (catToggle) catToggle.focus(); }
      else if (journal) appendSearch('in:"' + journal.dataset.journal + '"');

    });

    if (backTop) {
      backTop.addEventListener('click', function () { if (input) input.focus(); window.scrollTo({ top: 0, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }); });
    }
  }

  function updateSummary(payload) {
    var total = $('uva-arxiv-total-count');
    var journal = $('uva-arxiv-journal-count');
    var doi = $('uva-arxiv-doi-count');
    if (total) total.textContent = payload.counts && payload.counts.papers ? payload.counts.papers : state.papers.length;
    if (journal) journal.textContent = payload.counts && payload.counts.with_journal ? payload.counts.with_journal : 0;
    if (doi) doi.textContent = payload.counts && payload.counts.with_doi ? payload.counts.with_doi : 0;
  }

  function init() {
    var root = $('uva-arxiv-app');
    if (!root) return;
    var dataUrl = root.dataset.dataUrl || window.UVA_ARXIV_DATA_URL || '/assets/data/uva-arxiv-papers.json';
    wireEvents();
    fetch(dataUrl, { credentials: 'same-origin' })
      .then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      })
      .then(function (payload) {
        state.papers = (payload.papers || []).slice().sort(function (a, b) {
          if (a.date === b.date) return a.id < b.id ? 1 : -1;
          return a.date < b.date ? 1 : -1;
        });
        state.papers.forEach(function (paper) { paper._search = paperSearchText(paper); });
        state.papersById = {};
        state.papers.forEach(function (paper) { state.papersById[paper.id] = paper; });
        updateSummary(payload);
        buildCategoryButtons();
        applyFilters(true);
        var loading = $('uva-arxiv-loading');
        if (loading) loading.hidden = true;
      })
      .catch(function (err) {
        var loading = $('uva-arxiv-loading');
        if (loading) loading.textContent = 'Could not load arXiv data: ' + err.message;
      });
  }

  document.addEventListener('DOMContentLoaded', init);
})();

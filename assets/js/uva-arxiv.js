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

  function appendSearch(value) {
    var input = $('uva-arxiv-search-input');
    if (!input) return;
    input.value = value;
    applyFilters(true);
  }

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
    wrap.innerHTML = '';
    var all = document.createElement('button');
    all.type = 'button';
    all.className = 'btn btn-sm category-btn ' + (state.activeCategory === 'all' ? 'btn-primary active' : 'btn-outline-secondary');
    all.textContent = 'All categories (' + state.papers.length + ')';
    all.addEventListener('click', function () { state.activeCategory = 'all'; buildCategoryButtons(); applyFilters(true); });
    wrap.appendChild(all);
    cats.forEach(function (cat) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-sm category-btn ' + (state.activeCategory === cat ? 'btn-primary active' : 'btn-outline-secondary');
      btn.innerHTML = escapeHtml(cat) + ' <span class="uva-arxiv-cat-count">' + counts[cat] + '</span>';
      btn.addEventListener('click', function () { state.activeCategory = cat; buildCategoryButtons(); applyFilters(true); });
      wrap.appendChild(btn);
    });
  }

  function authorHtml(paper) {
    var authors = paper.authors && paper.authors.length ? paper.authors : [paper.authors_text || ''];
    return authors.map(function (author) {
      var label = escapeHtml(author);
      return '<button type="button" class="uva-arxiv-author-name" data-author="' + escapeHtml(author) + '">' + label + '</button>';
    }).join(', ');
  }

  function peopleHtml(paper) {
    if (!paper.people || !paper.people.length) return '';
    return paper.people.map(function (person) {
      return '<button type="button" class="badge uva-arxiv-person-badge" data-person="' + escapeHtml(person.name) + '">' + escapeHtml(person.name) + '</button>';
    }).join(' ');
  }

  function categoryHtml(paper) {
    return (paper.categories || []).map(function (cat) {
      return '<button type="button" class="badge uva-arxiv-cat-badge" data-cat="' + escapeHtml(cat) + '">' + escapeHtml(cat) + '</button>';
    }).join(' ');
  }

  function journalBadgeHtml(paper) {
    if (!paper.journal_name) return '';
    var label = paper.journal_name;
    if (paper.publication_year && label.indexOf(String(paper.publication_year)) === -1) label += ' ' + paper.publication_year;
    var filterName = paper.journal_full || paper.journal_name;
    var title = paper.journal_ref || paper.journal_full || paper.journal_name;
    var attrs = ' class="badge uva-arxiv-link-badge uva-arxiv-link-journal" data-journal="' + escapeHtml(filterName) + '" title="' + escapeHtml(title) + '"';
    return '<button type="button"' + attrs + '>' + escapeHtml(label) + '</button>';
  }

  function linkBadgesHtml(paper) {
    var html = '';
    html += '<a href="https://arxiv.org/abs/' + encodeURIComponent(paper.id) + '" target="_blank" rel="noopener" class="badge uva-arxiv-link-badge uva-arxiv-link-abs">arXiv<span class="visually-hidden"> (opens in new tab)</span></a>';
    html += '<a href="https://arxiv.org/pdf/' + encodeURIComponent(paper.id) + '" target="_blank" rel="noopener" class="badge uva-arxiv-link-badge uva-arxiv-link-pdf">pdf<span class="visually-hidden"> (opens in new tab)</span></a>';
    html += '<a href="https://arxiv.org/html/' + encodeURIComponent(paper.id) + '" target="_blank" rel="noopener" class="badge uva-arxiv-link-badge uva-arxiv-link-html">html<span class="visually-hidden"> (opens in new tab)</span></a>';
    if (paper.doi) html += '<a href="https://doi.org/' + encodeURIComponent(paper.doi) + '" target="_blank" rel="noopener" class="badge uva-arxiv-link-badge uva-arxiv-link-doi">doi<span class="visually-hidden"> (opens in new tab)</span></a>';
    return html;
  }

  function renderPaper(paper) {
    var li = document.createElement('li');
    li.className = 'mb-1';
    li.dataset.id = paper.id;
    li.dataset.month = paper.month;
    li.innerHTML =
      '<div class="uva-arxiv-entry">' +
      '  <div class="uva-arxiv-date-col"><time datetime="' + escapeHtml(paper.date) + '">' + escapeHtml(paper.date) + '</time><br><a href="https://arxiv.org/abs/' + encodeURIComponent(paper.id) + '" target="_blank" rel="noopener" class="uva-arxiv-id-label">' + escapeHtml(paper.id) + '<span class="visually-hidden"> (opens in new tab)</span></a></div>' +
      '  <div class="uva-arxiv-body">' +
      '    <div class="uva-arxiv-tags">' + categoryHtml(paper) + ' ' + journalBadgeHtml(paper) + '</div>' +
      '    <div><strong>' + authorHtml(paper) + '</strong>, "<em class="uva-arxiv-title" role="button" tabindex="0" aria-label="Toggle abstract for ' + escapeHtml(paper.id) + '">' + escapeHtml(paper.title) + '</em>" <span class="uva-arxiv-links">' + linkBadgesHtml(paper) + '</span></div>' +
      '    <div class="uva-arxiv-people mt-1">' + peopleHtml(paper) + '</div>' +
      (paper.abstract ? '    <details class="uva-arxiv-abstract-wrap"><summary class="uva-arxiv-abstract-toggle">Abstract</summary><div class="uva-arxiv-abstract">' + escapeHtml(paper.abstract) + (paper.journal_ref ? '<div class="uva-arxiv-journal-ref">Published in: ' + (paper.doi ? '<a href="https://doi.org/' + encodeURIComponent(paper.doi) + '" target="_blank" rel="noopener">' + escapeHtml(paper.journal_ref) + '</a>' : escapeHtml(paper.journal_ref)) + '</div>' : '') + '</div></details>' : '') +
      '  </div>' +
      '</div>';
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
    if (status) status.textContent = state.filtered.length + ' papers match the current filters.';
  }

  function applyFilters(reset) {
    var input = $('uva-arxiv-search-input');
    var tokens = tokenizeQuery(input ? input.value : '');
    state.filtered = state.papers.filter(function (paper) { return paperMatches(paper, tokens); });
    renderList(reset !== false);
    updateFilterButtons();
  }

  function updateFilterButtons() {
    var dateBtn = $('uva-arxiv-date-btn');
    var catToggle = $('uva-arxiv-cat-toggle');
    if (dateBtn) dateBtn.classList.toggle('has-filter', state.activeDate !== 'all');
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
    var items = document.querySelectorAll('.uva-arxiv-dropdown-item[data-date]');
    for (var i = 0; i < items.length; i++) items[i].classList.toggle('active', items[i].dataset.date === value);
    closeDateMenu();
    applyFilters(true);
  }

  function closeDateMenu() {
    var menu = $('uva-arxiv-date-menu');
    var btn = $('uva-arxiv-date-btn');
    if (menu) menu.classList.remove('open');
    if (btn) btn.setAttribute('aria-expanded', 'false');
  }

  function wireEvents() {
    var input = $('uva-arxiv-search-input');
    var clear = $('uva-arxiv-search-clear');
    var helpBtn = $('uva-arxiv-search-help-btn');
    var help = $('uva-arxiv-search-help');
    var catToggle = $('uva-arxiv-cat-toggle');
    var catPanel = $('uva-arxiv-cat-panel');
    var dateBtn = $('uva-arxiv-date-btn');
    var dateMenu = $('uva-arxiv-date-menu');
    var yearFrom = $('uva-arxiv-year-from');
    var yearTo = $('uva-arxiv-year-to');
    var yearApply = $('uva-arxiv-year-range-apply');
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
      buildCategoryButtons();
      applyFilters(true);
    }
    if (clear) clear.addEventListener('click', clearAllAndFocus);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        e.preventDefault();
        closeDateMenu();
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
    if (dateBtn && dateMenu) dateBtn.addEventListener('click', function () {
      var open = !dateMenu.classList.contains('open');
      dateMenu.classList.toggle('open', open);
      dateBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function (e) {
      if (dateMenu && dateBtn && !dateMenu.contains(e.target) && !dateBtn.contains(e.target)) closeDateMenu();
    });
    var dateItems = document.querySelectorAll('.uva-arxiv-dropdown-item[data-date]');
    for (var i = 0; i < dateItems.length; i++) {
      dateItems[i].addEventListener('click', function () { setDateFilter(this.dataset.date, this.textContent.trim()); });
    }
    if (yearApply) yearApply.addEventListener('click', function () {
      state.customFrom = yearFrom && yearFrom.value ? parseInt(yearFrom.value, 10) : null;
      state.customTo = yearTo && yearTo.value ? parseInt(yearTo.value, 10) : null;
      var label = (state.customFrom || '…') + '–' + (state.customTo || '…');
      setDateFilter('custom', label);
    });
    if (loadMore) loadMore.addEventListener('click', function () { renderList(false); });
    if (list) list.addEventListener('click', function (e) {
      var author = e.target.closest('.uva-arxiv-author-name');
      var person = e.target.closest('.uva-arxiv-person-badge');
      var cat = e.target.closest('.uva-arxiv-cat-badge');
      var journal = e.target.closest('.uva-arxiv-link-journal');
      var title = e.target.closest('.uva-arxiv-title');
      if (author) appendSearch('au:"' + author.dataset.author + '"');
      else if (person) appendSearch('au:"' + person.dataset.person + '"');
      else if (cat) { state.activeCategory = cat.dataset.cat; buildCategoryButtons(); applyFilters(true); }
      else if (journal) appendSearch('in:"' + journal.dataset.journal + '"');
      else if (title) {
        var details = title.closest('li[data-id]').querySelector('.uva-arxiv-abstract-wrap');
        if (details) details.open = !details.open;
      }
    });
    if (list) list.addEventListener('keydown', function (e) {
      var title = e.target.closest('.uva-arxiv-title');
      if (title && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        var details = title.closest('li[data-id]').querySelector('.uva-arxiv-abstract-wrap');
        if (details) details.open = !details.open;
      }
    });
    if (backTop) {
      window.addEventListener('scroll', function () { backTop.classList.toggle('visible', window.scrollY > 500); });
      backTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
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

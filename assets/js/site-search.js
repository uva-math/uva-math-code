(function () {
  'use strict';
  const form = document.getElementById('content-search');
  const input = document.getElementById('content-search-query');
  const status = document.getElementById('search-status');
  const results = document.getElementById('search-results');
  let documents;
  let request = 0;
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

  async function search() {
    const current = ++request;
    const query = input.value.trim();
    results.replaceChildren();
    if (!query) { status.textContent = 'Enter a search term.'; return; }
    status.textContent = 'Searching…';
    try {
      if (!documents) {
        const response = await fetch('/search-index.json');
        if (!response.ok) throw new Error('Search index unavailable');
        documents = await response.json();
      }
      if (request !== current) return;
      const words = normalize(query).split(/\s+/);
      const seen = new Set();
      const matches = documents.map(item => {
        const title = normalize(item.title);
        const body = normalize(item.text);
        const score = words.reduce((sum, word) => sum + (title.includes(word) ? 10 : body.includes(word) ? 1 : 0), 0);
        return { ...item, score, matches: words.every(word => title.includes(word) || body.includes(word)) };
      }).filter(item => item.matches && !seen.has(item.url) && seen.add(item.url))
        .sort((a, b) => b.score - a.score || a.title.localeCompare(b.title));
      status.textContent = matches.length ? `${matches.length} result${matches.length === 1 ? '' : 's'} for “${query}”.` : `No results for “${query}”. Try fewer words or browse the site map.`;
      for (const item of matches) {
        const li = document.createElement('li');
        const heading = document.createElement('h2');
        const link = document.createElement('a');
        link.href = item.url;
        link.textContent = item.title;
        heading.append(link);
        li.append(heading);
        const summary = document.createElement('p');
        summary.textContent = item.text.slice(0, 240) + (item.text.length > 240 ? '…' : '');
        li.append(summary);
        results.append(li);
      }
    } catch (error) {
      if (request === current) status.textContent = 'Search is temporarily unavailable. Please use the site map linked above.';
    }
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    const url = new URL(location.href);
    url.searchParams.set('q', input.value.trim());
    history.pushState({}, '', url);
    search();
  });
  function restoreQuery() {
    input.value = new URLSearchParams(location.search).get('q') || '';
    search();
  }
  window.addEventListener('popstate', restoreQuery);
  restoreQuery();
})();

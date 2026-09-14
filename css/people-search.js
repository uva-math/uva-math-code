document.addEventListener('DOMContentLoaded', function () {
  'use strict';
  const form = document.getElementById('people-search-form');
  const input = document.getElementById('people-search-input');
  if (!form || !input) return;
  const clear = document.getElementById('people-search-clear');
  const filters = document.getElementById('people-cat-buttons');
  const status = document.getElementById('people-results-status');
  const containers = Array.from(document.querySelectorAll('.people-directory'));
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const labels = {
    all: 'All', faculty: 'Faculty', postdoc: 'Postdocs', lecturer: 'Lecturers',
    emeritus: 'Emeritus', gradstudent: 'Graduate students', staff: 'Staff',
    'recent-postdoc': 'Recent postdocs'
  };
  let category = 'all';
  let announceTimer;
  const sections = containers.map(container => ({
    container,
    heading: container.previousElementSibling?.tagName === 'H2' ? container.previousElementSibling : null,
    category: container.dataset.category,
    rows: Array.from(container.children).filter(row => row.classList.contains('row')).map(row => ({
      element: row,
      search: normalize(row.textContent + ' ' + (row.querySelector('a.nonupper-h5')?.getAttribute('href') || ''))
    }))
  }));

  function filterPeople() {
    const query = normalize(input.value.trim());
    let count = 0;
    sections.forEach(section => {
      let sectionCount = 0;
      section.rows.forEach(row => {
        const visible = (category === 'all' || category === section.category) && row.search.includes(query);
        row.element.hidden = !visible;
        row.element.style.display = visible ? '' : 'none';
        if (visible) sectionCount++;
      });
      section.container.hidden = sectionCount === 0;
      if (section.heading) section.heading.hidden = sectionCount === 0;
      count += sectionCount;
    });
    filters?.querySelectorAll('button').forEach(button => {
      const selected = button.dataset.category === category;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    clearTimeout(announceTimer);
    announceTimer = setTimeout(() => {
      const scope = category === 'all' ? '' : ' in ' + labels[category];
      status.textContent = count ? count + ' ' + (count === 1 ? 'person' : 'people') + ' found' + scope + '.' : 'No people found. Try adjusting your search or filters.';
    }, 150);
  }

  function clearSearch() {
    input.value = '';
    category = 'all';
    filterPeople();
    input.focus();
  }
  form.addEventListener('submit', event => { event.preventDefault(); filterPeople(); });
  input.addEventListener('input', filterPeople);
  input.addEventListener('keydown', event => {
    if (event.key === 'Escape') { event.preventDefault(); clearSearch(); }
  });
  clear.addEventListener('click', clearSearch);
  if (filters) {
    const categories = new Set(['all', ...sections.map(section => section.category)]);
    categories.forEach(value => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn btn-secondary category-btn';
      button.dataset.category = value;
      button.textContent = labels[value] || value;
      button.addEventListener('click', () => { category = value; filterPeople(); });
      filters.appendChild(button);
    });
  }
  filterPeople();
});

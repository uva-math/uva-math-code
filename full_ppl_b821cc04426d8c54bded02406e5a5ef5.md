---
layout: static_page_no_right_menu
title: Department People List
permalink: /people-id/
redirect_from:
  - /people-list/b821cc04426d8c54bded02406e5a5ef5/
---

<h1>Department people and UVA IDs</h1>
<form id="id-search" role="search" aria-label="Department names and UVA IDs">
  <label for="id-search-input">Filter by name or UVA ID</label>
  <input class="form-control" type="search" id="id-search-input" aria-describedby="id-search-hint">
  <p id="id-search-hint">Results update as you type. Press Escape in the search field to clear it. Use an ID button to copy that ID.</p>
</form>
<p id="id-search-status" role="status" aria-live="polite" aria-atomic="true"></p>
<p id="copy-id-status" role="status" aria-live="polite" aria-atomic="true"></p>
<div class="table-responsive" role="region" aria-label="Department people and IDs" tabindex="0">
<table id="people-ids" class="table table-striped">
  <caption>Department members, computing IDs, and profile links</caption>
  <thead><tr><th scope="col">Name</th><th scope="col">UVA ID</th><th scope="col">Profile</th></tr></thead>
  <tbody>
  {% assign sorted_people = site.departmentpeople | sort: "lastname" %}
  {% for person in sorted_people %}
    <tr>
      <th scope="row">{{ person.name }} {{ person.lastname }}</th>
      <td><button type="button" class="btn btn-secondary copy-uva-id" data-uva-id="{{ person.UVA_id }}" aria-label="Copy UVA ID {{ person.UVA_id }} for {{ person.name | escape }} {{ person.lastname | escape }}">{{ person.UVA_id }}</button></td>
      <td><a href="{{ site.url }}/people/{{ person.UVA_id }}/">{{ person.name }} {{ person.lastname }} profile</a></td>
    </tr>
  {% endfor %}
  </tbody>
</table>
</div>
<script>
document.addEventListener('DOMContentLoaded', function () {
  const input = document.getElementById('id-search-input');
  const rows = Array.from(document.querySelectorAll('#people-ids tbody tr'));
  const status = document.getElementById('id-search-status');
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  function filter() {
    const term = normalize(input.value.trim());
    let count = 0;
    rows.forEach(row => { row.hidden = !normalize(row.textContent).includes(term); if (!row.hidden) count++; });
    status.textContent = count ? count + ' people found.' : 'No people found. Try another name or UVA ID.';
  }
  document.getElementById('id-search').addEventListener('submit', event => { event.preventDefault(); filter(); });
  input.addEventListener('input', filter);
  input.addEventListener('keydown', event => { if (event.key === 'Escape') { input.value = ''; filter(); } });
  document.querySelectorAll('.copy-uva-id').forEach(button => {
    button.addEventListener('click', async () => {
      const id = button.dataset.uvaId;
      const feedback = document.getElementById('copy-id-status');
      try { await navigator.clipboard.writeText(id); feedback.textContent = 'Copied UVA ID ' + id + '.'; }
      catch (_) { feedback.textContent = 'Could not copy automatically. Select and copy UVA ID ' + id + '.'; }
    });
  });
  filter();
});
</script>

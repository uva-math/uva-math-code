---
layout: static_page_no_right_menu
title: Department People List
permalink: /people-id/
redirect_from:
  - /people-list/b821cc04426d8c54bded02406e5a5ef5/
---

<div class="container">
<div class="row">

<div class="col-md-6">
<!-- Search bar HTML -->
<div id="search-container">
  <input type="text" id="search-input" placeholder="Search by name or UVA ID...">
  <button id="search-button">Search</button>
</div>

<!-- CSS Styles -->
<style>
  #search-container {
    margin: 20px 0;
    text-align: center;
  }
  #search-input {
    padding: 8px;
    width: 300px;
    font-size: 16px;
  }
  #search-button {
    padding: 8px 15px;
    font-size: 16px;
    background-color: #232D4B;
    color: white;
    border: none;
    cursor: pointer;
  }
  #search-button:hover {
    background-color: #0E1836;
  }
  .highlight {
    background-color: yellow;
  }
</style>

<!-- JavaScript for search functionality -->
<script>
document.addEventListener('DOMContentLoaded', (event) => {
  const searchInput = document.getElementById('search-input');
  const searchButton = document.getElementById('search-button');
  const table = document.querySelector('table');
  const rows = table.querySelectorAll('tr');

  function removeAccents(str) {
    return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  function performSearch() {
    const searchTerm = removeAccents(searchInput.value.toLowerCase());
    
    rows.forEach((row, index) => {
      if (index === 0) return; // Skip header row
      
      const name = removeAccents(row.cells[0].textContent.toLowerCase());
      const uvaId = row.cells[1].textContent.toLowerCase();
      
      if (name.includes(searchTerm) || uvaId.includes(searchTerm)) {
        row.style.display = '';
        highlightText(row, searchTerm);
      } else {
        row.style.display = 'none';
      }
    });
  }

  function highlightText(row, searchTerm) {
    [0, 1].forEach(cellIndex => {
      const cell = row.cells[cellIndex];
      const originalText = cell.textContent;
      const normalizedText = removeAccents(originalText);
      let highlightedText = '';
      let lastIndex = 0;

      const regex = new RegExp(searchTerm, 'gi');
      let match;
      while ((match = regex.exec(normalizedText)) !== null) {
        highlightedText += originalText.slice(lastIndex, match.index);
        highlightedText += `<span class="highlight">${originalText.slice(match.index, match.index + match[0].length)}</span>`;
        lastIndex = match.index + match[0].length;
      }
      highlightedText += originalText.slice(lastIndex);

      cell.innerHTML = highlightedText;
    });
  }

  searchButton.addEventListener('click', performSearch);
  searchInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      performSearch();
    }
  });

  // Add a reset functionality
  searchInput.addEventListener('input', function() {
    if (this.value === '') {
      rows.forEach(row => {
        row.style.display = '';
        row.cells[0].innerHTML = row.cells[0].textContent;
        row.cells[1].innerHTML = row.cells[1].textContent;
      });
    }
  });
});
</script>
</div>
<div class="col-md-6">
<table class="table table-striped">
  <thead>
    <tr>
      <th>Name</th>
      <th>UVA ID</th>
      <th>Dept link</th>
    </tr>
  </thead>
  <tbody>
    {% assign sorted_people = site.departmentpeople | sort: "lastname" %}
    {% for person in sorted_people %}
      <tr>
        <td>{{ person.name }} {{ person.lastname }}</td>
        <td>{{ person.UVA_id }}</td>
        <td><a href="{{ site.url }}/people/{{ person.UVA_id }}/">Page</a></td>
      </tr>
    {% endfor %}
  </tbody>
</table>
</div>

</div></div>
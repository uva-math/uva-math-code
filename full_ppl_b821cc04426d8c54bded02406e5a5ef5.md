---
layout: static_page_no_right_menu
title: Department People List
permalink: /people-list/b821cc04426d8c54bded02406e5a5ef5/
---

<div class="col-md-4">
<table class="table table-striped">
  <thead>
    <tr>
      <th>Name</th>
      <th>UVA ID</th>
    </tr>
  </thead>
  <tbody>
    {% assign sorted_people = site.departmentpeople | sort: "lastname" %}
    {% for person in sorted_people %}
      <tr>
        <td>{{ person.name }} {{ person.lastname }}</td>
        <td>{{ person.UVA_id }}</td>
      </tr>
    {% endfor %}
  </tbody>
</table>
</div>
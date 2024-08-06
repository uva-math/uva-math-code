---
layout: static_page_no_right_menu
title: Department People List
permalink: /people-list/
---

<h1>Department People List</h1>

<ul>
{% assign sorted_people = site.departmentpeople | sort: "lastname" %}
{% for person in sorted_people %}
  <li>{{ person.name }} {{ person.lastname }} - {{ person.UVA_id }}</li>
{% endfor %}
</ul>
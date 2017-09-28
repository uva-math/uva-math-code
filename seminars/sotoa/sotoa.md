---
layout: seminar
permalink: /seminars/sotoa/
nav_parent: Seminars
events: false
sem_page: true
title: Seminar in operator theory and operator algebras
---


{% assign xx = page.permalink | split: '/' %}
{% for word in xx %}{% if forloop.last %}{% assign cur_shortname = word %}{%endif%}{% endfor %}
{% for sem in site.data.seminars %}
{%if sem.shortname == cur_shortname %}

{% if page.title == null %}
  <h1 class="mt-2 mb-4">University of Virginia {{sem.name}}</h1>
{% else %}
  <h1 class="mt-2 mb-4">{{page.title}}</h1>
{% endif %}

{{sem.shortname}}

<div class="list-group-sm">
  <a class="list-group-item list-group-item-action h5 orange-item" href="http://www.people.virginia.edu/~des5e/sotoa/sotoa.html">Click here to proceed to the standalone seminar page</a>
</div>

<br>

{% if sem.image != null %}
  <div class="row">
    <div class="col-md-3">
      <img src="{{ sem.image | replace: '__SITE_URL__', site.url }}" style="max-width:100%;max-height:400px;height:auto;width:auto;padding:10px" alt="{{sem.name}} image" title="{{sem.name}} image"/>
    </div>
    <div class="col-md-9">
      <b>Regular time and location: {{sem.regular_times}}</b>
      {% if sem.information != null %}<details class="mb-3"><summary>Description</summary>
        {{ sem.information }}
      </details>
      {% endif %}
    </div>
  </div>
{% else %}
  <b>Regular time and location: {{sem.regular_times}}</b>
  {% if sem.information != null %}<details class="mb-3"><summary>Description</summary>
    {{ sem.information }}
  </details>
  {% endif %}
{% endif %}


<h2 class="mt-4 mb-3">Upcoming talks</h2>

{% include cal_single.js google_cal_id = 'ftc1mbjbp95irpj6t9e2tfl020@group.calendar.google.com' current="true" max_sem=50 %}



<hr />

<b>Contact:</b> {% for cnt in sem.contact %}<br />{% include person_info_email_only.html UVA_id = cnt.UVA_id %}{% endfor %}


{%endif%}
{% endfor %}

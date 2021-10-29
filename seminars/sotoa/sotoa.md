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

{% include cal_single.js google_cal_id = sem.google_cal_id current="true" max_sem=50 %}

<hr />

<b>Contact:</b> {% for cnt in sem.contact %}<br />{% include person_info_email_only.html UVA_id = cnt.UVA_id %}{% endfor %}

<hr />
<h3 class="mb-3">Archives</h3>

<p><a href="/seminars/sotoa/">upcoming</a> | <a href="/seminars/sotoa/2021-22/">2021-22</a> | <a href="/seminars/sotoa/2020-21/">2020-21</a> | <a href="/seminars/sotoa/2019-20/">2019-20</a> | <a href="/seminars/sotoa/2018-19/">2018-19</a> | <a href="/seminars/sotoa/2017-18/">2017-18</a></p>

<div class="list-group-sm">
  <a class="list-group-item list-group-item-action h5 orange-item" href="https://dshermanmath.github.io/base/sotoa/sotoa.html">Old seminar page with pre-2017 talks</a>
</div>


{%endif%}
{% endfor %}

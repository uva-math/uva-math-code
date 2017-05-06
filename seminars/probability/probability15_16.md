---
title: Probability Seminar 2015-16
permalink: "/seminars/probability/2015-16/"
layout: seminar
events: false
sem_page: true
sem_archive: true
---

{% assign xx = page.permalink | split: '/' %}
{% assign cur_shortname = xx[2] %}

{% for sem in site.data.seminars %}
{%if sem.shortname == cur_shortname %}

{% if page.title == null %}
  <h1 class="mt-2 mb-4">University of Virginia {{sem.name}}</h1>
{% else %}
  <h1 class="mt-2 mb-4">{{page.title}}</h1>
{% endif %}

{% if sem.image != null %}
  <div class="row">
    <div class="col-md-3">
      <img src="{{ sem.image | replace: '__SITE_URL__', site.url }}" style="max-width:100%;max-height:400px;height:auto;width:auto;padding:10px" alt="{{sem.name}} image" title="{{sem.name}} image"/>
    </div>
  </div>
{% endif %}

{% include cal_single.js google_cal_id = sem.google_cal_id current=false max_sem=100
show_from='1 July 2015'
show_to='1 July 2016' %}


---

**Contact:** {% for cnt in sem.contact %}{{cnt.name}} ([*{{cnt.email}}*](mailto:{{cnt.email}})){% if forloop.last == false %},{% endif %} {% endfor %}

**[Old webpage link]({{sem.webpage}})**

{%endif%}
{% endfor %}

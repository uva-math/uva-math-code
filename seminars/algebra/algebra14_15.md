---
title: Algebra Seminar 2014-15
layout: seminar
permalink: /seminars/algebra/2014-15/
events: false
sem_page: true
sem_archive: true
nav_parent: Seminars
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
show_from='1 July 2014'
show_to='1 July 2015' %}

<hr />
<h3 class="mb-3">Archives</h3>
<a href="/seminars/algebra/">current</a> |
[2016-17](/seminars/algebra/2016-17/) \|
[2015-16](/seminars/algebra/2015-16/) \|
[2014-15](/seminars/algebra/2014-15/) \|
[2013-14](/seminars/algebra/2013-14/) \|
[2012-13](/seminars/algebra/2012-13/) \|
[2011-12](/seminars/algebra/2011-12/) \|
[2010-11](/seminars/algebra/2010-11/) \|
[2009-10](/seminars/algebra/2009-10/) \|
[2008-09](/seminars/algebra/2008-09/) \|
[2007-08](/seminars/algebra/2007-08/) \|
[2002-07](/seminars/algebra/AlgSeminarOld/)

---

**Contact:** {% for cnt in sem.contact %}<br />{% include person_info_email_only.html UVA_id = cnt.UVA_id %} {% endfor %}

<br>**[Old webpage link]({{sem.webpage}})**

{%endif%}
{% endfor %}

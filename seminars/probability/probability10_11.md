---
title: Probability Seminar Spring 2011
layout: seminar
permalink: /seminars/probability/2010-11/
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
show_from='1 July 2010'
show_to='1 July 2011' %}


<hr />
<h3 class="mb-3">Archives</h3>


<p><a href="/seminars/probability/2016-17/">2016-17</a> |
    <a href="/seminars/probability/2015-16/">2015-16</a> |
    <a href="/seminars/probability/2014-15/">2014-15</a> |
    <a href="/seminars/probability/2013-14/">2013-14</a> |
    <a href="/seminars/probability/2012-13/">2012-13</a> |
    <a href="/seminars/probability/2011-12/">2011-12</a> <br />
    <a href="/seminars/probability/2010-11/">Spring 2011</a> |
    <a href="/seminars/probability/Fall2010/">Fall 2010</a> |
    <a href="/seminars/probability/Spring2007/">Spring 2007</a></p>
    
---

**Contact:** {% for cnt in sem.contact %}<br />{% include person_info_email_only.html UVA_id = cnt.UVA_id %} {% endfor %}

<br>**[Old webpage link]({{sem.webpage}})**

{%endif%}
{% endfor %}

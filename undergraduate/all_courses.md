---
title: Courses
layout: static_page_no_right_menu
permalink: /courses/
---

<h1 class="mb-3">Course descriptions</h1>

Please refer to <a href="https://sisuva.admin.virginia.edu/ihprd/signon.html">SIS</a> or <a href="https://louslist.org/CC/Mathematics.html">Lou's list</a> for details about courses offered.

<!-- 
<br>

{% assign courses = site.data.courses %}
{% for added_course in site.data.courses_added_manually %}
  {% assign courses = courses | push: added_course %}
{% endfor %}
{% assign sorted_courses = courses | sort: "number" %}

<div class="my-row-zebra">
{% for crs in sorted_courses %}
{% assign maskedflag = 0 %}
    {% for maskcrs in site.data.masked_courses %}
      {% if crs.number == maskcrs.number %}
        {% assign maskedflag = 1 %}
      {% endif %}
    {% endfor %}
{% if maskedflag == 0 %}
  <div class="row" style="padding:10px 0px">
    <div class="col-12">
       <div class="mt-1 mb-1"><code class="highlighter-rouge" style="background:inherit; padding:0px"><a name="{{crs.number}}">MATH {{crs.number}}</a></code>&nbsp;&nbsp;&nbsp;<b>{{crs.name}}</b>{% if crs.offered %}<div class="float-right hidden-sm-down">
         <code class="highlighter-rouge" style="background:inherit; padding:0px">Offered {{crs.offered}}</code>
       </div><span class="hidden-md-up">
         &bull; <b>(Offered {{crs.offered}})</b>
       </span>
     {% endif %}</div>
       {{crs.descr}}
    </div>
  </div>
{% endif %}
{% endfor %}
</div> -->

---
title: Courses
layout: static_page_no_right_menu
permalink: /courses/
---

<h1 class="mb-3">Course descriptions &bull; (<a href="{{site.url}}/courses/undergrad/">undergraduate</a>) &bull; (<a href="{{site.url}}/courses/graduate/">graduate</a>)</h1>

This is a list of courses automatically generated from the [Lou's list](http://rabi.phys.virginia.edu/mySIS). Please refer there for details about instructors and current enrollment numbers.


<br>

{% assign sorted_courses = site.data.courses | sort: "number" %}

<div class="my-row-zebra">
{% for crs in sorted_courses %}
  <div class="row" style="padding:10px 0px">
    <div class="col-12">
       <div class="mt-1 mb-1"><code class="highlighter-rouge" style="background:inherit; padding:0px">MATH {{crs.number}}</code>&nbsp;&nbsp;&nbsp;<b>{{crs.name}}</b>{% if crs.offered %}<div class="float-right hidden-sm-down">
         <code class="highlighter-rouge" style="background:inherit; padding:0px">Offered {{crs.offered}}</code>
       </div><span class="hidden-md-up">
         &bull; <b>(Offered {{crs.offered}})</b>
       </span>
     {% endif %}</div>
       {{crs.descr}}
    </div>
  </div>
{% endfor %}
</div>

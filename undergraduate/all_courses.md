---
title: Courses
layout: static_page_no_right_menu
permalink: /courses/
---

<h1 class="mb-4">Course descriptions &bull; (<a href="{{site.url}}/courses/undergrad/">undergraduate</a>) &bull; (<a href="{{site.url}}/courses/graduate/">graduate</a>)</h1>



{% assign sorted_courses = site.data.courses | sort: "number" %}

<div class="my-row-zebra">
{% for crs in sorted_courses %}
  <div class="row" style="padding:10px 0px">
    <div class="col-12">
       <div class="mt-1 mb-1"><code class="highlighter-rouge" style="background:inherit; padding:0px">MATH {{crs.number}}</code>&nbsp;&nbsp;&nbsp;<b>{{crs.name}}</b>{% if crs.offered %}<div class="float-right">
         <code class="highlighter-rouge" style="background:inherit; padding:0px">Offered {{crs.offered}}</code>
       </div>
     {% endif %}</div>
       {{crs.descr}}
    </div>
  </div>
{% endfor %}
</div>

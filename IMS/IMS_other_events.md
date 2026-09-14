---
title: IMS special events
layout: static_page_no_right_menu
permalink: /ims/special-events/
nav_id: 'IMS special events'
nav_weight: 5
nav_nesting: true
nav_parent: IMS
---

<h1 class="mb-5">Upcoming and past IMS special events</h1>


---

<div class="row">
{% for post in site.posts %}
  {% if post.categories contains "ims-special" %}
    <div class="col-12">
        {% include news_snippet.html post=post %}
  </div>
  {% endif %}
{% endfor %}
</div>

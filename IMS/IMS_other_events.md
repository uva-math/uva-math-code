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


<div class="row">
{% for post in site.posts %}
  {% if post.categories contains "ims-special" %}
    <div class="col-12">
        <h2 class="mb-2 mt-3"><a href="{{site.url }}{{ post.url }}" style="color:inherit;">{{ post.title }}</a></h2>

        {% if post.event-date != null and post.multi-day-event %}
        <h6>Event start date: {{ post.event-date |  date: "%A, %B %-d, %Y" }}</h6>{% endif %}
        {% if post.event-date != null and post.multi-day-event != true %}
        <h6>Event date: {{ post.event-date |  date: "%A, %B %-d, %Y" }}</h6>{% endif %}

        {% if post.image != null %} {% if post.image-address != null %}<a href="{{ post.image-address | replace: '__SITE_URL__', site.url }}">{% else %}<a href="{{site.url }}{{ post.url }}">{% endif %}<img src="{{ post.image | replace: '__SITE_URL__', site.url }}" alt="{{ post.image-alt }}" title="{{ post.image-alt }}" style="max-width:240px;height:auto;width:auto;" class="mb-3 mt-2"></a>
        {% endif %}

        {{ post.excerpt | markdownify }}

        <p><a class="btn btn-secondary h5" href="{{site.url }}{{ post.url }}" style="white-space: normal" role="button">{% if post.more-text == null %}View details{% else %}{{ post.more-text }}{% endif %} &raquo;</a></p>
        <hr />
  </div>
  {% endif %}
{% endfor %}
</div>

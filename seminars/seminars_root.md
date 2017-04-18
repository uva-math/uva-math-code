---
title: Seminars
layout: seminar
permalink: /seminars/
nav_id: Seminars
nav_weight: 15
nav_nesting: true
events: true
---

{% assign sorted_pages = site.pages | sort: "nav_weight" %}
{% for p in sorted_pages %}
{% if p.permalink contains '/seminars/' and p.permalink != '/seminars/' %}
- ### [{{p.nav_id}}]({{site.url}}{{p.url}})
{% endif %}
{% endfor %}

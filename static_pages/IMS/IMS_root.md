---
title: IMS
permalink: "/ims/"
layout: static_page_no_right_menu
nav_id: IMS
nav_weight: 1000
nav_nesting: true
---

# Institute of Mathematical Science

<br>

{% assign sorted_pages = site.pages | sort: "nav_weight" %}
{% for p in sorted_pages %}
{% if p.permalink contains '/ims/' and p.permalink != '/ims/' %}
- ### [{{p.nav_id}}]({{site.url}}{{p.url}})
{% endif %}
{% endfor %}

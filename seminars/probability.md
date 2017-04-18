---
layout: seminar
permalink: /seminars/probability/
nav_parent: Seminars
events: false
sem_page: true
---


{% assign xx = page.permalink | split: '/' %}
{% for word in xx %}{% if forloop.last %}{% assign cur_shortname = word %}{%endif%}{% endfor %}
{% for sem in site.data.seminars %}
{%if sem.shortname == cur_shortname %}

# University of Virginia {{sem.name}}

##### Regular time and location: {{sem.regular_times}}

{% if sem.information != null %}<details class="mb-3"><summary>Description</summary>
  {{ sem.information }}
</details>
{% endif %}

## Upcoming talks



---

**Contact:** {% for cnt in sem.contact %}{{cnt.name}} ([*{{cnt.email}}*](mailto:{{cnt.email}})){% if forloop.last == false %},{% endif %} {% endfor %}

**[Old webpage link]({{sem.webpage}})**

{%endif%}
{% endfor %}

---
layout: seminar
permalink: /seminars/algebra/
nav_parent: Seminars
events: false
sem_page: true
---

{% assign xx = page.permalink | split: '/' %}
{% for word in xx %}{% if forloop.last %}{% assign cur_shortname = word %}{%endif%}{% endfor %}
{% for sem in site.data.seminars %}
{%if sem.shortname == cur_shortname %}

# University of Virginia {{sem.name}}

#### [Old webpage link]({{sem.webpage}})

---

Regular time and location: {{sem.regular_times}}

{% if sem.information != null %}
  {{ sem.information }}
{% endif %}


---

Contact: {% for cnt in sem.contact %}{{cnt.name}} ([*{{cnt.email}}*](mailto:{{cnt.email}})){% if forloop.last == false %},{% endif %} {% endfor %}



{%endif%}
{% endfor %}

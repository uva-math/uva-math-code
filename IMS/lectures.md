---
title: Virginia Mathematics Lectures
layout: static_page_no_right_menu
permalink: /ims/lectures/
nav_id: 'Virginia Mathematics Lectures (2014-)'
nav_weight: 2
# nav_nesting: true
nav_parent: IMS
---

<h1 class="mb-5">Virginia Mathematics Lectures</h1>


<div class="row">
<div class="col-md-10">
In 2014, the IMS established the Distinguished Lecture Series "Virginia Mathematics Lectures." The inaugural speaker was Professor Alex Lubotzky from the Hebrew University of Jerusalem. Each semester thereafter brought us another speaker in the series, including Vaughan Jones (Vanderbilt), Ian Agol (UC Berkeley), and – most recently – Benedict H. Gross (Harvard).

<br><br>

These lecture series were enthusiastically met by the audience which included undergraduate and graduate students, faculty members and guests from other departments and institutions. Given the success of the lectures, the IMS will continue to organize two such series every year.
</div>
</div>

<br>

### Past lectures

- Benedict H. Gross (Harvard University), Spring 2017
- James Arthur (University of Toronto), Fall 2016
- Karen Smith (University of Michigan), Spring 2016
- Ian Agol (University of California Berkeley), Fall 2015
- Vaughan Jones (Vanderbilt University), Spring 2015
- Alex Lubotzky (Hebrew University of Jerusalem), Fall 2014

<br>

<div class="row my-col-12-zebra">
{% for post in site.posts %}
{% if post.categories contains "virginia-mathematics-lectures" %}
<div class="col-12 my-bordered-news-snippets">
<h2 class="mb-2 mt-3"><a href="{{site.url }}{{ post.url }}" style="color:inherit;">{{ post.title }}</a></h2> {% if post.event-date != null %}
<h6>{{ post.event-date |  date: "%A, %B %-d, %Y" }}</h6>{% endif %} {% if post.image != null %} {% if post.image-address != null %}<a href="{{ post.image-address | replace: '__SITE_URL__', site.url }}">{% else %}<a href="{{site.url }}{{ post.url }}">{% endif %}<img src="{{ post.image | replace: '__SITE_URL__', site.url }}" alt="{{ post.image-alt }}" title="{{ post.image-alt }}" style="max-width:240px;height:auto;width:auto;" class="mb-3 mt-2"></a>
{% endif %} {{ post.excerpt | markdownify }}
<p><a class="btn btn-secondary h5" href="{{site.url }}{{ post.url }}" role="button">{% if post.more-text == null %}View details{% else %}{{ post.more-text }}{% endif %} &raquo;</a></p>
</div>
<!--/span-->
{% endif %}
{% endfor %}
</div>

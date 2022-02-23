---
title: About IMS
layout: static_page_no_right_menu
permalink: /ims/about/
nav_id: 'About Institute of Mathematical Science '
nav_weight: 1
nav_nesting: true
nav_parent: IMS
---


<h1 class="mb-5">Institute of Mathematical Science</h1>

<div class="row">
    <div class="col-12">
The Institute of Mathematical Science (IMS) will bring together--in a centralized physical space--an internationally recognized group of distinguished scholars together with invited postdoctoral fellows and advanced graduate students to work collaboratively on targeted area of fundamental research in mathematical science. The Institute's aims are two-fold: the production of world-class scientific research and the raising of mathematical awareness through public outreach. The Institute will enhance its research mission through research seminars directed at faculty and graduate students in a number of departments and schools within the University, a program of monthly research colloquia, a year-end international conference, and undergraduate colloquia. It will carry out the outreach aspect of its mission through a series of distinguished lectures aimed at the broader community on aspects of mathematical science as well as through programs for high school teachers and students designed to stimulate and deepen mathematical understanding.
</div>
<div class="col-12 col-lg-6">
            <img class="mt-3 mb-2" src="{{site.url}}/img/Routunda.jpg"
            style="max-width:100%;max-height:400px;height:auto;width:auto;" alt="UVa Rotunda" title="UVa Rotunda">            
    </div>
</div>  
---

<ul>
{% assign sorted_pages = site.pages | sort: "nav_weight" %}
{% for p in sorted_pages %}
{% unless p.permalink contains "/ims/workshop-fall-2018/" %}
    {% if p.nav_parent == "IMS" and p.permalink != "/ims/about/" and p.permalink != "/ims/analysis2015/"  %}
    <li><h3><a href="{{site.url}}{{p.url}}">{{p.nav_id}}</a></h3></li>
    {% endif %}
{% endunless %}
{% endfor %}
</ul>

<img src="{{site.url}}/img/Routunda.jpg" class="clear-right" style="max-width:45%; padding:20px" alt="Rotunda">

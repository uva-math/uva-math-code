---
title: News Pages
layout: documentation_page
permalink: /doc/news/
nav_parent: Info
doc_page: true
nav_weight: 103
---

# News, events, posts

---

## Post entry

### Categories currently present on the website:

{% assign sorted_cats = site.categories | sort %}
{% for category in sorted_cats %}
{{ category | first }}{% unless forloop.last %}{% endunless %}
{% endfor %}













---

### Main department page

The main department page [{{site.url}}]({{site.url}}) is set to display up to 5 posts with category `news`. If among them there is a post with category `major-news` then it is displayed on top with a larger picture.

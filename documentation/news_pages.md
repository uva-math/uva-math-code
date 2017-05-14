---
title: News, Events, and Other Posts
layout: documentation_page
permalink: /doc/news/
nav_parent: Info
doc_page: true
nav_weight: 103
---

# News, events, and Other Posts

---

## Overview

The "posts" mechanism powers all regularly updated items except seminar talks (those a powered by google calendars, see [here]({{site.url}}/doc/seminars/) for details). Examples of these include:

- Event announcements (such as graduation)
- Conference announcements
- Award announcements
- Job opportunities
- IMS lecture announcements
- Any other department news

Each post corresponds to a file located in the `_posts/` folder or one of its subfolders (subfolders in `_posts/` are there purely for convenience and do not affect the resulting website). The file has a certain structure described below. The filename has to follow an exact pattern, namely, it **must** look like

{% highlight yml %}
YYYY-MM-DD-name-of-the-post.md
{% endhighlight %}

---

## Post variables

### Categories currently present on the website:

{% assign sorted_cats = site.categories | sort %}
{% for category in sorted_cats %}
{{ category | first }}{% unless forloop.last %}{% endunless %}
{% endfor %}








---

## Where posts are displayed

The posts are automatically displayed in a number of pages, including the following.

**Note.** This information is current as of May 14, 2017, and more pages displaying posts might be added.

### [Department main page]({{site.url}})

The main department page [{{site.url}}]({{site.url}})
displays up to 5 posts with category `news`. If a post does not have category `news` then it will not
be displayed on the main page. Most posts thus should have category `news`.

If among them there is a post with category `major-news` then it is displayed on top with a larger picture.

### ["All news" page]({{site.url}}/allnews/)

This page collects and displays all posts on the website, and features "pagination", i.e.,
creates pages which show 8 posts each, with navigation on the right.
The subsequent pages have addresses like [{{site.url}}/allnews/page2/]({{site.url}}/allnews/page2/).

### Pages displaying posts by category

##### [IMS lectures]({{site.url}}/ims/lectures/)

This page

##### [Virginia math Bulletin]({{site.url}}/newsletter/)

##### [Awards]({{site.url}}/awards/)

##### [Conferences]({{site.url}}/conferences/)

##### [Job opportunities]({{site.url}}/job-opportunities/)

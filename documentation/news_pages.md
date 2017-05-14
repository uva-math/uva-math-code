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

Here `YYYY-MM-DD` better correspond to `date:` configuration variable in the post. 
The post itself has its own page. By default, its address is formatted as 
`{{site.url}}/YYYY/MM/name-of-the-post`, where `YYYY`, `MM`, and `name-of-the-post` 
come from the file name. This default address can be changed by setting the 
`permalink:`  configuration variable.

---

## Post file

### Example of a post file

{% highlight markdown linenos %}
---
layout: post
title: Benedict Gross - Virginia Mathematics Lectures - March 27-29, 2017
date: 2017-03-27 13:30:00
event-date: 2017-03-27 13:30:00
multi-day-event: true
permalink: /ims/lectures/benedict-gross/
comments: false
categories: news virginia-mathematics-lectures ims events
published: true
image: __SITE_URL__/img/IMS/Gross_poster.jpg
image-alt: Benedict H. Gross Poster
image-address: __SITE_URL__/img/IMS/Gross_poster.jpg
image-tall: true
more-text: Abstracts
---

<h3 class="mt-3 mb-4"> Benedict H. Gross (Harvard)</h3>

- Lecture 1: The rank of elliptic curves
- Lecture 2: The arithmetic of hyperelliptic curves
- Lecture 3: Heegner points on modular curves

<!--more-->

#### Lecture 1: The rank of elliptic curves

[FURTHER_CONTENT]
{% endhighlight %}

### Content

The first 16 lines define many configuration variables for the post. The
rest of the file (after the second `---`) is the content of the post. 
Note the separator `<!--more-->`. The content above it is the 
post excerpt which is displayed in all post rolls, and the content below it is displayed
only on the page of the post, cf. [the post roll]({{site.url}}/newsletter/) and a [page
of the post]({{site.url}}/2016/06/bulletin/).

One image to the post can be added to be handled automatically (to be displayed in nice size in both post rolls
and on the post page). More images can be added manually as needed, both above and below the excerpt separator.

The syntax of the content (both above and below the excerpt separator) is [markdown](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet). Math formulas are also [supported]({{site.url}}/doc/math/). 
As usual, plain HTML is supported inside markdown.

### Configuration variables

Let us now describe the configuration variables (not all of them are present above),
and how they affect the presentation of the post.

##### published

Setting `published: false` will remove the post from the website
completely (but it will stay in the [GitHub source](https://github.com/uva-math/uva-math-code)). By default this variable is set to `published: true`, so it can as well be omitted.

##### layout

Should be set to `layout: post`, simple as that. By the way, the post layout `_layouts/post.html`
determines how the individual post page looks like.

##### comments

The comments feature is not yet implemented, but if it will be implemented then
`comments: false` will disable comments (this will be the default setting),
and only manually setting `comments: true` will enable comments.
Therefore, this variable can simply be not present in posts.

##### title

Well, this is the title of the post which is displayed in both post rolls and 
on the post page.

##### date

This is the published date of the post which may not coincide with the 
actual date of the event. 
It should coincide with the date in the filename of the post `.md` file. 
It is also displayed as "date published" at the bottom of the post page

**Note.** The `date` (and `event-date` below) should be formatted with hours, minutes and seconds, as in
`date: 2017-03-27 13:30:00`. Hours, minutes, and seconds are displayed nowhere, 
and they are used only to determine the ordering of the posts when they are shown in a roll.

##### event-date and multi-day-event

These two variables allow to indicate the date of an event, if a post is announcing 
an event such as IMS lectures or a conference. If the post is not about an event, 
simply do not include these variables.

The value `event-date` is displayed under the title of the post. If `multi-day-event` is set to `true`, 
the text before the date says "Event start date", otherwise the text says "Event date".

##### permalink

If you do not like the default address `{{site.url}}/YYYY/MM/name-of-the-post`
of the post page, you can manually set it to something else, as 
in `permalink: /ims/lectures/benedict-gross/`. 
You can include any subfolder names in the permalink. 

##### categories 

This is an important variable because it determines where the post is displayed.
The currently used categories on the website are (the list below is generated automatically):

{% assign sorted_cats = site.categories | sort %}
<ul>
{% for category in sorted_cats %}
<li><code class="highlighter-rouge">{{ category | first }}</code></li>
{% endfor %}
</ul>

A post can have several categories.

By default, all published posts (i.e., not with `published: false`) are displayed
on the ["all news" page]({{site.url}}/allnews/). If you add `news`, then the post
will be displayed on the main page (note that the main page displays only 5 most recent posts).
And so on, see [below](#displaying-posts) for a detailed description.

##### variables related to image

Posts look nicely with images. If you do not want an image, simply omit these variables.






image: __SITE_URL__/img/IMS/Gross_poster.jpg
image-alt: Benedict H. Gross Poster
image-address: __SITE_URL__/img/IMS/Gross_poster.jpg
image-tall: true

##### more-text




---

## <a name="displaying-posts">Where posts are displayed</a>

The posts are automatically displayed in a number of pages, including the following.

**Note.** This information is current as of May 14, 2017, and more pages displaying posts might have been added.

### [Department main page]({{site.url}})

The main department page [{{site.url}}]({{site.url}})
displays up to 5 posts with category `news`. If a post does not have category `news` then it will not
be displayed on the main page. Most posts thus should have category `news`.

If among the posts displayed on the main page 
there is a post with category `major-news`, 
then it is displayed on top with a larger picture. 
Only one `major-news` will be displayed like this, even if there are 
several such posts on the main page. 
If one wants to highlight a particular post then one should
add `major-news` category to it, and remove this category
from the other posts on the main page. 
The `major-news` category only affects posts displayed on the main page.

### ["All news" page]({{site.url}}/allnews/)

This page collects and displays **all** posts on the website, and features "pagination", i.e.,
creates pages which show 8 posts each, with navigation on the right.
The subsequent pages have addresses like [{{site.url}}/allnews/page2/]({{site.url}}/allnews/page2/).
Even if a post does not have category `news` it will be displayed here.
To remove a post from the website set the configuration variable `published: false`.

### Pages displaying posts by category

These pages are displaying every post having a certain category. 
They do not have the "pagination", that is, they can grow up to dozens of entries over
time. This issue will be addressed in the future as needed. 
One possible immediate solution is to have an `archive` category or a configuration variable, 
and not display 
archived posts there.

Again, even if a post does not have category `news` it will be displayed in the corresponding
page below if it has a suitable category.
To remove a post from the website set the configuration variable `published: false`.

##### [IMS lectures]({{site.url}}/ims/lectures/)

This page has some general information on the IMS Virginia Mathematics Lectures,
and also an archive of all the IMS lectures posts. 
Posts having category `virginia-mathematics-lectures` appear there.

##### [Virginia math Bulletin]({{site.url}}/newsletter/)

This page collects issues of Virginia Math Bulletin.
Posts having category `virginia-math-bulletin` appear there.

##### [Awards]({{site.url}}/awards/)

This page collects information on awards in the department (both faculty and student). 
Posts having category `awards` appear there.

##### [Conferences]({{site.url}}/conferences/)

This page collects conference announcements.
Posts having category `conferences` appear there.

##### [Job opportunities]({{site.url}}/job-opportunities/)

This page collects postings of job opportunities.
Posts having category `jobs` appear there.

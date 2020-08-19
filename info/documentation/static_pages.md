---
title: Static Pages and Navigation Bar
layout: documentation_page
permalink: /doc/static/
nav_parent: Info
doc_page: true
nav_weight: 105
---

# Static pages and Navigation Bar

---

## Overview

The navigation bar
(which is between the UVA brand and the main content of the page and contains the core hierarchy of the website)
is built automatically.
There are 3 types of pages which interact with the navigation bar:

##### 1. First level label pages

Their navigation id's appear in the collapsed navigation bar. Examples: "About" or "Seminars".

##### 2. Second level pages

Their navigation id's are nested under a first level label, and
whose links are shown in the dropdown menus visible when clicking on the first level labels. Example: "Algebra Seminar".

##### 3. Highlighted pages

Their links are not shown in dropdown menus as second level ones, but which are clearly related to a certain first- or second-level page. At these pages the corresponding links in the navigation bar are highlighted. Example: seminar archive pages, click [here]({{site.url}}/seminars/algebra/2008-09/) to see the highlighting of the corresponding first- and second-level labels.

**Note.** Special code is required in the case of seminars to automatically highlight the second level labels.
Since these labels are anyway in the dropdown menu, this special code should not be used for other purposes, and
thus in general only the first-level labels will be highlighted. This behavior is intended and should be enough for good
navigation.

**Note.** Details of the interaction with the navigation bar are described [below](#conf_var).
There are of course other pages which do not interact with the navigation bar,
and they typically can be reached by clicking through links on the website.

---

## <a name="conf_var">Details on configuration variables</a>

There numerous configuration variables one can put in the beginning of the page.
Here we focus only on those interacting with the navigation bar, or, more broadly, with
the URL structure of the website.

For example, here is the page for listing all postdocs in the department.
The page's location in the code is `/people/postdocs.html`.

{% highlight markdown linenos %}
{%raw%}
---
title: Postdoctoral Scholars
layout: static_page_no_right_menu
permalink: /postdocs/
nav_id: Postdocs
nav_weight: 2
nav_nesting: true
nav_parent: People
---

<h1 class="mb-4">Postdoctoral Scholars</h1>

{% include people_roll.html type='postdoc' %}
{%endraw%}
{%endhighlight%}

Lines 10-13 are the content of the page, it contains the title and
a piece of code which automatically generates the list of the postdocs.
Let us discuss other variables in this particular case.

<span class="nonupper-h5">title</span>

The page's title, simple as that.

<span class="nonupper-h5">layout</span>

The layout `static_page_no_right_menu` is the simplest layout possible,
see [below](#empty_layout).

<span class="nonupper-h5">permalink</span>

This is the (relative) URL which will be used in the generated website.
For many pages, specifying `permalink` is often a good idea. Note that the
`permalink` has nothing to do with the filename associated
with the page (which is `/people/postdocs.html` in this particular case).

<span class="nonupper-h5">nav\_parent</span>

If this variable is defined then the page cannot be first-level.
Setting this variable as above highlights the corresponding first-level entry.
Thus, this variable is used in second-level or highlighted pages.

<span class="nonupper-h5">nav\_id</span>

Setting this variable means that the page is first- or second-level,
and this is the name which will appear in the navigation bar
(which thus can be shorter than the page title).

<span class="nonupper-h5">nav\_nesting</span>

If this is set to true then the page is either
first- or second-level, depending on
whether `nav_parent` is set or not.
If `nav\_nesting` is `false` and `nav_parent` is not set,
then the page would be rendered into an isolated first-level page
(examples: "About" and "Support us")

<span class="nonupper-h5">nav\_weight</span>

This is used to order the menu entries in the navigation bar
(the first- and the second-level entries under each first-level entry are
sorted separately) and sometimes in the right sidebar menu.
The general rule is that the smaller `nav_weight`, the
closer the page is to the beginning of the sorted list.

### A note on first-level label pages

First-level pages only produce headers for the dropdown menus in the navigation
bar (except "About" and "Support us" which is an isolated first-level page not having any dropdown menu).
However, there are actual pages associated with each entry.
These first-level label pages cannot be accessed by clicking
but they still exist. Here is the list of them:

<ul>
{% assign sorted_pages = site.pages | sort: "nav_weight" %}
{% for p in sorted_pages%}
{% if p.nav_id != null and p.nav_parent == null %}
<li><a href="{{site.url}}{{p.url}}">{{ p.nav_id }}</a></li>
{% endif %}
{% endfor %}
<li><a href="{{site.url}}/support/">Support us</a></li>
</ul>

The first-level isolated pages are completely meaningful.
Some of the other pages are redirects, and some contain
certain quick links. The non-isolated first-level pages
should not typically be accessed as there are no links pointing to them.

---

## Static pages

A vast number of pages in the website are generated automatically
(examples: news rolls, people pages, etc.).
However, important static information could also be put into
static pages. The examples are the "About" page `{{site.url}}/about/`
and pages with information for undergraduate and graduate students.
The documentation pages are also static.
Overall, editing static pages is much like editing usual HTML websites.

The static pages (coming from files with `.md` or `.html` extension)
can be put anywhere in the source code of the website,
so having subfolders brings convenience.
Since the pages are static, their `permalink` variables can be
specified manually to bring convenience.
If `permalink` is not specified the URL of the page is generated automatically
based on which subfolder it is in.

**Note.** The rendering of the
website ignores
(for the purposes of static pages generation)
subfolders starting with `_` like `/_posts/`.

### To create a static page

#### 1.

Create `.md` or `.html` file somewhere in the code of the website, and
specify the configuration variables in the beginning of the file. A minimal collection of the configuration
variables is the following:
{%highlight yaml linenos %}
---
title: [YOUR_PAGE_TITLE]
layout: static_page_no_right_menu
permalink: [YOUR_PAGEs_PERMALINK]
nav_parent: [TO_HIGHLIGHT_A_NAVIGATION_BAR_ENTRY]
---
{%endhighlight%}

<a name="empty_layout">The layout</a> `static_page_no_right_menu` corresponds to a completely empty static page
only having the top brand bar, the navigation bar, and the footer element.
[Here]({{site.url}}/emptypage/) is an example of such a page, [file on GitHub](https://raw.githubusercontent.com/uva-math/uva-math-code/master/emptypage.md).

The `nav_parent` variable is also optional. If it is not specified then
no navigation bar entry is highlighted.

#### 2.

Then edit the content of the page in
[markdown](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
or plain HTML.
Math formulas are also [supported]({{site.url}}/doc/math/).

#### 3.

The static page just added can be linked on existing website pages
using its permalink. [Remember]({{site.url}}/doc/reminders/) to use
`{%raw%}{{ site.url }}{%endraw%}`
instead of an actual URL of the website to create internal links.

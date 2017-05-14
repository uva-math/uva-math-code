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
title: Postdoctoral Visitors
layout: static_page_no_right_menu
permalink: /visitors/
nav_id: Postdocs
nav_weight: 2
nav_nesting: true
nav_parent: People
---

<h1 class="mb-4">Postdoctoral Visitors</h1>

{% include people_roll.html type='postdoc' %}
{%endraw%}
{%endhighlight%}

Lines 10-13 are the content of the page, it contains the title and 
a code which 


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

The layout `static_page_no_right_menu` corresponds to a completely empty static page
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

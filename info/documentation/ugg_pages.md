---
title: Undergraduate and Graduate Information Pages
layout: documentation_page
permalink: /doc/ugg/
nav_parent: Info
doc_page: true
nav_weight: 106
published: true
---

# Undergraduate and Graduate Information Pages

---

## Overview

The undergraduate and graduate information pages are a particular case of
static pages. Here we briefly describe their structure,
focusing on undergraduate pages (the structure of the graduate pages
is very similar and we will not discuss it). 

---

## Static pages

All pages in the undergraduate/graduate category are of three types:

- main pages
- information pages
- policy pages

There are two main pages, one called `undergraduate_main_page.md` with permalink
`/undergraduate/`, and the other called `undergraduate_policy_page.md`
with permalink `/undergraduate/policies/`. These pages
are orange headers in the sidebar and they also correspond to the subentries
in the top navigation bar, under the "Undergraduate" dropdown menu.

The information and policy pages can be added 
as needed. Their top configuration variables look as follows, for example (the file is `DMP.md`):
{% highlight yaml linenos %}
---
title: Distinguished Major Program (DMP)
layout: ug_page
ug_policy: true
permalink: /content/distinguished-major-program-dmp/
nav_parent: Undergraduate
nav_weight: 10
---
{%endhighlight%}

All fields are self-explanatory, but just in case let us describe them.

- `title` is shown in the sidebar and in the page title
- `layout: ug_page` means that the page will be grouped under the undergraduate pages
- `ug_policy: true` shows that this is an undergraduate policy page (`ug_info` would correspond to an information page)
- `permalink` in this case is chosen for compatibility with the old website
- `nav_parent: Undergraduate` highlights the corresponding top navigation bar entry
- `nav_weight: 10` corresponds to the ordering in the sidebar (as always, smaller `nav_weight` corresponds
to higher position)

After the top configuration variables there is the main content of the page,
which can be either in markdown or in HTML. Math formulas are supported, as usual. 
The extension can be either `.md` or `.html`, there are slight differences between them
but both are supported.


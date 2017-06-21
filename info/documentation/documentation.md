---
title: General principles
layout: documentation_page
permalink: /doc/
nav_parent: Info
nav_nesting: true
nav_weight: 100
nav_id: Website Documentation
doc_page: true
---

## Purpose of the documentation pages

The purpose of these pages is to help understand the structure of the department
website, and to invite everyone at the department [contribute]({{site.url}}/doc/contribute/) to the content
of our website.



<h1 class="mt-5">General principles of the website organization</h1>

---

### 1. Collaborative editing powered by [GitHub](https://github.com)

Edits to the website are tested automatically so are unlikely to break anything.
Moreover, any edit can be reverted. Therefore, *you* are welcome to
participate in editing the content. The first step is to sign up on [GitHub.com](https://github.com)
and send your username to [L. Petrov](mailto:petrov@virginia.edu) to be added as a collaborator.
See [here]({{site.url}}/doc/contribute/) for more details on how to contribute.

There are two main ways to edit the website content:

- **On the web**: Smaller edits can be made directly on the web at [GitHub](https://github.com/uva-math/uva-math-code). The GitHub icon in the lower right corner of each page points to the source file associated with this page, for quicker and simpler editing of existing content on the web.
- **Locally**: Clone the website code to your local machine, make edits, and then sync the changes back to [GitHub](https://github.com/uva-math/uva-math-code). For this we recommend installing the [GitHub Desktop app](https://desktop.github.com/) and the [Atom text editor](https://atom.io/). Both are available for both Windows and Mac, and Atom is also available for Linux.

In both cases, the changes in the code will trigger the website to automatically update, this takes about 5 minutes.

Having a local copy of the website allows to preview your edits locally using [Jekyll](https://jekyllrb.com/) (only on Mac and Linux). This procedure is described in detail in Jekyll documentation, see for example [here](https://jekyllrb.com/docs/installation/) and [here](https://jekyllrb.com/docs/usage/). **Note that due to API limitations seminar google calendars will not work in local previews**.

The website building (and testing) are powered by [Travis CI](https://travis-ci.org/). The current build status is&nbsp;&nbsp;[![Build Status](https://travis-ci.org/uva-math/uva-math-code.svg?branch=master)](https://travis-ci.org/uva-math/uva-math-code)

---

### 2. Simple content structure powered by [Jekyll](https://jekyllrb.com/)

- Any simple change in content should require editing in only one place. More complicated edits (such as adding a new seminar) might need changes in up to three places. Typical editing scenarios are documented on these pages.
- The content is text file based, with no databases or complicated CMSs
- The simply structured content is then built (using [Travis CI](https://travis-ci.org/)) into a static HTML website (plus a little client-side javascript for google calendar interaction, math rendering, and responsive design)

---

### 3. Flexible design powered by [Bootstrap](http://getbootstrap.com/)

- Most design elements can be tweaked independently of content (and most changes require editing only in one file)
- Design is fully customizable

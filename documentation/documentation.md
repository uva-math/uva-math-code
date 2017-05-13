---
title: Main principles | Documentation
layout: documentation_page
permalink: /doc/
nav_parent: Info
nav_nesting: true
nav_weight: 100
nav_id: Website Documentation
---

# Main principles

## Collaborative editing powered by [GitHub](https://github.com)

Edits to the website are tested automatically so are unlikely to break anything.
Moreover, any edit can be reverted. Therefore, *you* are welcome to
participate in editing the content. To do this, sign up on [GitHub](https://github.com)
and send your username and any questions to [L. Petrov](mailto:petrov@virginia.edu) to be added as a collaborator.

There are two main ways to edit the website content:

- **On the web** - Smaller edits can be made on the web at [GitHub](https://github.com/uva-math/uva-math-code).
- **Locally** - One can clone a local copy of the website code, make edits, and then sync the changes back to [GitHub](https://github.com/uva-math/uva-math-code). For this we recommend installing the [GitHub Desktop app](https://desktop.github.com/) and the [Atom text editor](https://atom.io/). Both are available for both Windows and Mac.

In both cases, the changes in the code will trigger the website to automatically update, this takes about 5 minutes.

Having a local copy of the website allows to preview your edits locally using [Jekyll](https://jekyllrb.com/), only on Mac. This is described in detail in Jekyll documentation, see for example [here](https://jekyllrb.com/docs/installation/) and [here](https://jekyllrb.com/docs/usage/).

## Simple content structure powered by [Jekyll](https://jekyllrb.com/)

- Any simple change in content requires editing in only one place. More complicated edits (such as adding a new seminar) might need changes in up to two places.
- The content is text file based, with no databases or complicated CMSs
- The simply structured content is then built into a static HTML website (plus a little client-side javascript for google calendar interaction, math rendering, and responsive design)

## Flexible design powered by [Bootstrap](http://getbootstrap.com/)

- Most design elements can be tweaked independently of content (and most changes require editing only in one file)
- Design is fully customizable

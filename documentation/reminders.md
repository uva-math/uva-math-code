---
title: Important reminders
layout: documentation_page
permalink: /doc/reminders/
nav_parent: Info
doc_page: true
nav_weight: 1000
reminders_page: true
---

# Important reminders before making edits to the website

## [This file's code on GitHub](https://raw.githubusercontent.com/uva-math/uva-math-code/master/documentation/reminders.md)

---

### 1. GitHub sync

*(This does not apply if you're making changes in the web editor)*

If using a local copy of the website code, **make sure to sync before your first edit**. This will help avoid git conflicts.
Also remember that the website will be built and updated only upon syncing with the GitHub.

### 2. Internal links

For internal links (when referencing a page on the department website)
please use `{%raw%}{{ site.url }}{%endraw%}`
**instead of an actual URL of the website**.
The tag
`{%raw%}{{ site.url }}{%endraw%}`
will be built into the actual URL which is `{{ site.url }}`.

For example, the current page should be referenced as

{%highlight Liquid%}{%raw%}
{{ site.url }}/doc/reminders/
{%endraw%}{%endhighlight%}

It can also be referenced as

{%highlight Liquid%}{%raw%}
{{ site.url }}{{ page.url }}
{%endraw%}{%endhighlight%}

Both expressions are built into the correct address of the current page, which is `{{ site.url }}{{ page.url }}`.
See [Jekyll documentation](https://jekyllrb.com/docs/variables/) for more details.

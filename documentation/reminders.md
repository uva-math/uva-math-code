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

---

### 1. Tip for web editing on GitHub

To get started it is helpful to view the code of the current page.
To launch the GitHub web editor for this page (and any other page of the website)
click on the GitHub icon in the lower right corner.
If you understand what's going on you can try editing this page.
However, if the source contains includes (such as `{%raw%}{% include seminar_main_page.html %}{%endraw%}`)
then you typically should not edit this page.

### 2. Do not forget to sync with GitHub when editing locally

*(This does not apply if you're making changes in the web editor)*

If using a local copy of the website code, **make sure to sync before your first edit**. This will help avoid git conflicts.
Also remember that the website will be built and updated with your local changes only upon syncing with the GitHub.

**Remember!** If you edit on the web then the web changes should also be synced with the local ones.

### 3. Formatting of internal links

For internal links (when referencing a page on the department website)
in pages' contents
please use `{%raw%}{{site.url}}{%endraw%}`
**instead of an actual URL of the website or
relative paths**.
The expression
`{%raw%}{{site.url}}{%endraw%}`
will become the actual website URL which is `{{site.url}}`.

For example, the current page should be referenced as

{%highlight Liquid%}{%raw%}
{{ site.url }}/doc/reminders/
{%endraw%}{%endhighlight%}

It can also be referenced as

{%highlight Liquid%}{%raw%}
{{ site.url }}{{ page.url }}
{%endraw%}{%endhighlight%}

Both expressions turn into the correct address of the current page which is `{{ site.url }}{{ page.url }}`.
See [Jekyll documentation](https://jekyllrb.com/docs/variables/) for more details.

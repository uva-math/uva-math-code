---
title: Help update the website
layout: documentation_page
permalink: /doc/contribute/
nav_parent: Info
doc_page: true
nav_weight: 999
---

# How you can contribute to updating the content at the Math Department website

---

## Overview: why?

The structure of the Math Department website
allows everyone to contribute to updating its contents.
Here are several examples:

- Every member of the Department can update own personal information, such as
research interests, selected publications, link to personal page, etc. See [here]({{site.url}}/doc/people/) for details.

- One can add news about conferences or seminar series being organized, and it will be displayed on the Department main page.
See [here]({{site.url}}/doc/news/) for details.

- The website contains lots of information that should be kept up-to-date, including
undergraduate and graduate policies, etc. This can be updated by people in charge of these subjects.
See [here]({{site.url}}/doc/ugg/) for details.

- Dedicated static pages can be created within the website, for example,
to host Collaborative Learning Center information, etc. In this case, person(s) in charge would need to keep the information
up to date. This brings an advantage of uniform style of all official pages, and includes version control of the source as a bonus.

Surely one can think of more examples and reasons why multiple people should edit the content on the website.
Below we discuss several ways one can interact with the website. All of them (except the number zero one)
require signing up at [GitHub](https://www.github.com)  - but the process is very simple and you need to only do this once.

---

## 0. Good old email or personal conversation

You can send an email to
{% include person_info_email_only.html UVA_id="lap5r" %}, {% include person_info_email_only.html UVA_id="hcg3m" %}, or {% include person_info_email_only.html UVA_id="raj3e" %}, or talk to one of them, and explain what needs to be updated.

This way of communication is **by no means discouraged**, as the head goal is that the website
contains up-to-date and relevant information.
However, the next three ways of updating the website involve various levels of automating the
update process, and thus could potentially lead to the website being more up to date, and
containing more of the relevant information.

---

## 1. GitHub issues

Having a [GitHub](https://www.github.com) account, one can add an **issue**. Current issues for the website are
located here: [`https://github.com/uva-math/uva-math-code/issues`](https://github.com/uva-math/uva-math-code/issues). There si also wiki page at [`https://github.com/uva-math/uva-math-code/wiki/Issues-extended`](https://github.com/uva-math/uva-math-code/wiki/Issues-extended) for issues with longer turnaround.
A new issue can be added by anyone. **Issues are public** (but after all we're talking about editing a public website, right?).

The advantage of issues is that they can easily reference code, can be discussed and commented on, and ultimately be resolved and closed
(though closed issues also stay public). To view the source code for any page click on the
GitHub icon <a {% if paginator.page %}href="https://github.com/uva-math/uva-math-code/blob/master/allnews/index.html"
{% else %}href="https://github.com/uva-math/uva-math-code/blob/master/{{page.path}}"{% endif %} title="Contribute to the website's content on GitHub" target="_blank"><span class="fa fa-github-square fa-2x"></span></a> in the lower right corner. Then there is a link to
issues on top of the resulting GitHub page.

---

## 2. Suggesting changes ("pull-requests")

A more automated way of editing the website is to suggest changes to a particular page via editing its source code
and creating a so-called "**pull-request**" (so you ask the code
owner to "pull", or incorporate, your changes into the main code). This is done as follows.

Suppose you want to edit a simple piece of
information, e.g. correct a typo, or add your new publication (for adding/changing the picture resort to way number 0 above, or create a local fork of the website code,
make changes there, and create a pull-request). Here are the steps:

1. Go to your page such as [`{{site.url}}/people/aso9t/`]({{site.url}}/people/aso9t/),
and click on the
GitHub icon <a {% if paginator.page %}href="https://github.com/uva-math/uva-math-code/blob/master/allnews/index.html"
{% else %}href="https://github.com/uva-math/uva-math-code/blob/master/{{page.path}}"{% endif %} title="Contribute to the website's content on GitHub" target="_blank"><span class="fa fa-github-square fa-2x"></span></a> in the lower right corner.

2.
You will see the source of the page.
To edit the source, click on the pen icon in this panel on the right:<br>
<img src="{{site.url}}/img/github_editing.png" alt="GitHub editing" title="GitHub editing">

3. Make the necessary changes in browser. Hint: for formatting tips, check other webpages,
click on the GitHub icon, and click `Raw` on the same panel as above to see the actual source code.

4. Click the green button `Propose file change` on the bottom. Then click `Create pull request`. You may describe your changes in more detail in these text fields,
or just leave this as is.

5. Click `Create pull request` on the bottom again after describing the nature of the changes.

The administrator(s) will be notified and can approve or decline (or edit and then approve) your pull request.
You should then be notified of the outcome by email, and the changes will appear on the webpage.

**Note**: Pull requests are public, and existing open pull requests are seen on GitHub
at [`https://github.com/uva-math/uva-math-code/pulls`](https://github.com/uva-math/uva-math-code/pulls)


---

## 3. Full edit access

Faculty members can receive full editing access from the administrators.
This allows to edit any source file, on the web as explained above,
or you can download a local copy of the source and then push changes to GitHub.
Upon committing the changes to the GitHub the webpage will be automatically
updated (this takes about 5 minutes).
Any change can be reverted, and changes that break the website will not
appear on the actual webpage. Therefore, do not hesitate to ask
{% include person_info_email_only.html UVA_id="lap5r" %} or {% include person_info_email_only.html UVA_id="hcg3m" %}
for full edit access and relevant training.

**Note**: Unfortunately, GitHub does not provide partial editing access (of only specific files).
However, this restriction is natural because any file can in principle change name and/or location.

**Note**: Having full edit rights is nice but this can lead to edit conflicts (when the file is changed by
at least two people at the same time). Pull requests does not lead to conflicts as easily, and
allow numerous people edit the website at the same time, if needed.

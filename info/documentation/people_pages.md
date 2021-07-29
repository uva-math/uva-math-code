---
title: People Pages and Research Areas
layout: documentation_page
permalink: /doc/people/
nav_parent: Info
doc_page: true
nav_weight: 102
---

# People pages and research areas

---

## Structure of people pages

### One person - one file

Each person's page corresponds to a single file in the `_departmentpeople/` folder called `[UVA_COMPUTING_ID].md` (all these files are here on [GitHub](https://github.com/uva-math/uva-math-code/tree/master/_departmentpeople)). This naming is for the purposes of consistency with links in the old website. This file corresponds to the page `{{site.url}}/people/[UVA_COMPUTING_ID]/`. The people listings such as [{{site.url}}/faculty/]({{site.url}}/faculty/) and listings by research areas are generated automatically.

**Note.** The subfolders in `_departmentpeople/` are purely for convenience - they do not affect anything in the actual website.

Here's an example of such a file for a particular faculty member. The page itself is at [{{site.url}}/people/aso9t/]({{site.url}}/people/aso9t/).

{% highlight markdown linenos %}
---
UVA_id: aso9t
lastname: Obus
name: Andrew
general_position: faculty
position: Assistant Professor
office: 208 Kerchof Hall
phone: 434-924-4930
email: obus@virginia.edu
image: __SITE_URL__/img/people/Obus.jpg
personal_page: http://people.virginia.edu/~aso9t/
areas:
  - Algebra&nbsp;$$\cup$$&nbsp;Arithmetic Geometry/Number Theory&nbsp;$$\cup$$&nbsp;Representation Theory
  - Geometry&nbsp;$$\cup$$&nbsp;Topology
grad_general_areas:
  - algebra
grad_special_areas:
  - algebraic_geometry
---


##### Selected Publications
- Cyclic extensions and the local lifting problem (with S. Wewers), Ann. of Math. **180**, No. 1 (2014), 233--284.
- Fields of moduli of three-point $G$-covers with cyclic $p$-Sylow, I, Algebra Number Theory **6**, No. 5 (2012), 833--883.
{% endhighlight %}

### Referencing a person on the website by UVA computing ID

Having all data on people in one place allows to quickly reference them by
UVA computing ID. For example, the code
`{% raw %}{% include person_info.html UVA_id="aso9t" %}{% endraw %}`
produces the following nice listing of information about a
faculty member with computing ID `aso9t`:

{% include person_info.html UVA_id="aso9t" %}

This is powered by [this include file](https://github.com/uva-math/uva-math-code/blob/master/_includes/person_info.html) on GitHub, and one can create similar files to get, for example, reference without office number. All links are also taken from the person's data and are handled correctly in case, say, personal page or phone is missing:&nbsp; {% include person_info.html UVA_id="ds5nd" %}

If there is no such computing ID (e.g. if a person left), then one space is displayed: {% include person_info.html UVA_id="no_such_id" %}. (Code: `{% raw %}{% include person_info.html UVA_id="no_such_id" %}{% endraw %}`)

### Fields in the people pages

#### Content

The first 15 lines in this file are for configuration, separated by two `---`. The lines after line 15 (after the second `---`) can be any content the person would like on their page, such as
- Selected publications
- More detailed description of research interests
- Any links, pictures, and so on

The syntax is [markdown](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet). Math formulas are also [supported]({{site.url}}/doc/math/).
As usual, plain HTML is supported inside markdown.

#### Configuration

Most configuration fields are self-evident, except the following:

<span class="nonupper-h5">general\_position</span>

This field is used to put the person in a correct listing such as [{{site.url}}/postdocs/]({{site.url}}/postdocs/) or [{{site.url}}/gradstudents/]({{site.url}}/gradstudents/). Possible values are:

- `emeritus`
- `faculty` (tenure-track or tenured)
- `gradstudent`
- `lecturer`
- `postdoc`
- `staff`

This field is also used in automatically counting the number of faculty/postdocs/etc on pages like [about]({{site.url}}/about/).

The exact title of the position is under `position:` configuration field, as in `position: Assistant Professor`.

<span class="nonupper-h5">image</span>

Put the image file (`jpg` or `png`, any size/dimensions, but square and up to `600x600` preferred) into the folder `/img/people/` in the source code, and link it in a configuration field like `image: __SITE_URL__/img/people/Obus.jpg`.

**Important!** keep the `__SITE_URL__` prefix as is, this is needed for correct automatic generation of the website.

<span class="nonupper-h5">office_hours</span>

If you'd like, you can add office hours to be displayed on the website.
They will be shown in the list of people and on the person's page at the department website.
However, this information should be kept up to date, and so office
hours should probably not be added for all facutly.

<span class="nonupper-h5">areas</span>

This is a field which determines how people are displayed by research area
in the general lists of the people in the department (for example, [here]({{site.url}}/research/analysis/)).
See [below](#research_areas_pages) for details.

<span class="nonupper-h5">grad\_general\_areas and grad\_special\_areas</span>

These fields determine only where the person is displayed in the [graduate research areas information page]({{site.url}}/graduate/research-areas/).

### Adding/removing people

To *add a person*, make a new file and fill all the fields in. The person's page will appear on the website on correct pages.

To *remove a person*, either delete the file, or remove it from the building of the website by adding `published: false`, say, before the `areas:` line.

<div class="orange-item mb-2" style="padding:10px">
<b>[update: April 24, 2018]</b>
<br> 
The setting <code class="highlighter-rouge">published: false</code> appears to be broken in a new version of Jekyll, 
so please manually move the source files to a special folder <code class="highlighter-rouge">/_UNPUBLISHED/</code> in the source
</div>

---

## <a name="research_areas_pages">Research areas</a>

### Adding research areas to people

The listings of people by research area such as [{{site.url}}/research/analysis/]({{site.url}}/research/analysis/) are generated automatically. To ensure correct generation of the website, one needs to add the exact research areas to each person's configuration, as in the example above:

{% highlight html %}
areas:
  - Algebra&nbsp;$$\cup$$&nbsp;Arithmetic Geometry/Number Theory&nbsp;$$\cup$$&nbsp;Representation Theory
  - Geometry&nbsp;$$\cup$$&nbsp;Topology
{% endhighlight %}

Possible values for research areas are quite broad and include the cup signs $$\cup$$ to indicate this. Here are the possible values for research areas one can put into a person's `.md` page:

<ul>
{% for area in site.data.research_areas %}
<li><code class="highlighter-rouge">{{area.name | replace: '&nbsp;$$\cup$$&nbsp;', '&amp;nbsp;$$\cup$$&amp;nbsp;'}}</code></li>
{% endfor %}
</ul>

The list of these values is in the file `_data/research_areas.yml` ([GitHub link](https://github.com/uva-math/uva-math-code/blob/master/_data/research_areas.yml)), here is an example of one entry (the dash in the first line and indentation are important):

{% highlight html %}
-
  name: Analysis&nbsp;$$\cup$$&nbsp;PDE&nbsp;$$\cup$$&nbsp;Operator Algebras
  h-name: Analysis &cup; PDE &cup; Operator Algebras
  shortname: analysis
{% endhighlight %}

### Changing global research areas

For correct display of research areas, three conditions must be met:

1. The research area is described in `_data/research_areas.yml` as above
2. A simple file corresponding to the research area with permalink corresponding to the area's `shortname` must be manually created. These files are in `people/research/` folder, see an [example file on GitHub](https://github.com/uva-math/uva-math-code/blob/master/people/research/analysis.md).
2. In the people's pages, the research area should be listed exactly, according to its `name` field.

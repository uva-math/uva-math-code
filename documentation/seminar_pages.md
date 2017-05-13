---
title: Seminar Pages
layout: documentation_page
permalink: /doc/seminars/
nav_parent: Info
doc_page: true
nav_weight: 101
---

# Seminar pages

The main code for a seminar page located at `seminars/[SEMINAR_NAME]/[SEMINAR_NAME].md` ([example on GitHub](https://github.com/uva-math/uva-math-code/blob/master/seminars/colloq/colloq.md)) looks quite simple. Here is an example (symbols `%` and `{}` are together in the actual page, but for correct rendering here they are separated by a space; also in the actual page there are more links to archives):

{% highlight markdown linenos %}
---
layout: seminar
permalink: /seminars/colloq/
nav_parent: Seminars
events: false
sem_page: true
title: University of Virginia Mathematics Colloquium #override the default title in <h1> on the page
# title: CAN OVERRIDE the title in <h1> on the page; the title of the page itself is hardcoded from seminars.yml
---

{ % include seminar_page.html
  content=""
  contacts=""
  archives="[2016-17](/seminars/colloq/2016-17/) \|
    [2015-16](/seminars/colloq/2015-16/) \|
    [2014-15](/seminars/colloq/2014-15/) \|
    [2013-14](/seminars/colloq/2013-14/) \|
    ...
    "
% }
{% endhighlight %}

### Core functionality

The main day-to-day content in the seminar pages is taken from google calendars. Each seminar has its own google calendar, and a javascript code on the page pulls the seminar entries and displays them in a nice format on a seminar page. The seminar organizers continue to update their seminar's google calendars as usual.

The fields `content=""` and `contacts=""` allow to add some extra content into specific places on the automatically generated seminar page: the first field adds before `UPCOMING TALKS` list, and the second field - before the `Contact:` information at the bottom of the page.

### Archives

###### Recent

The recent archives using google calendars are displayed year by year, semi-automatically: one simply needs to create archive pages each year - these can be copied from a previous example like at [this GitHub link](https://github.com/uva-math/uva-math-code/blob/master/seminars/colloq/colloq15_16.md).

**Note:** Links from google calendar entries displayed on seminar pages can be broken over time (i.e. when the linked external URL becomes unavailable). There is currently no way implemented to control this because these links are grabbed by javascript. This issue does not affect the displaying of more recent seminar talks, and will likely not be fixed.


###### Older

Older archives not using google calendar have to be moved manually from the old seminar pages. See [this GitHub issue](https://github.com/uva-math/uva-math-code/issues/16) on which archives have already been moved.

### Where is the magic

The key to how this works is in the field `permalink: /seminars/colloq/` which tells the builder that this page corresponds to the Colloquium. Similarly, for the seminar archive pages the key field is something like `permalink: /seminars/colloq/2015-16/` which tells the builder to look at the Colloquium. The `title:` field in both cases is not essential and can be changed.

The main information on seminars is contained in `_data/seminars.yml` ([this file on GitHub](https://github.com/uva-math/uva-math-code/blob/master/_data/seminars.yml)). Its structure is explained below.

## Seminars data file `_data/seminars.yml`

This is the main file which contains all information 


### Changing seminar information


### Adding/removing a seminar globally

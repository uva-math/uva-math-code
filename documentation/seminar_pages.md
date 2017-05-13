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

###### More recent

The recent archives using google calendars are displayed year by year, semi-automatically: one simply needs to create archive pages each year - these can be copied from a previous example like at [this GitHub link](https://github.com/uva-math/uva-math-code/blob/master/seminars/colloq/colloq15_16.md).

**Note:** Links from google calendar entries displayed on seminar pages can be broken over time (i.e. when the linked external URL becomes unavailable). There is currently no way implemented to control this because these links are grabbed by javascript. This issue does not affect the displaying of more recent seminar talks, and will likely not be fixed.


###### Older

Older archives not using google calendar have to be moved manually from the old seminar pages. See [this GitHub issue](https://github.com/uva-math/uva-math-code/issues/16) on which archives have already been moved.

### Where the magic happens

The key to how this works is in the field `permalink: /seminars/colloq/` which tells the builder that this page corresponds to the Colloquium. Similarly, for the seminar archive pages the key field is something like `permalink: /seminars/colloq/2015-16/` which tells the builder to look at the Colloquium. The `title:` field in both cases is not essential and can be changed.

The main information on seminars is contained in `_data/seminars.yml` ([this file on GitHub](https://github.com/uva-math/uva-math-code/blob/master/_data/seminars.yml)). Its structure is explained below.

The javascript code which generates talks lists is in the files `_includes/cal_main.js` (for the main page unified list of talks; [file on GitHub](https://github.com/uva-math/uva-math-code/blob/master/_includes/cal_main.js)) and `_includes/cal_single.js` (for individual seminar pages and archives; [file on GitHub](https://github.com/uva-math/uva-math-code/blob/master/_includes/cal_single.js)).

---

## Seminars data file

`_data/seminars.yml` ([file on GitHub](https://github.com/uva-math/uva-math-code/blob/master/_data/seminars.yml)) is the main file which contains all information about seminars. An example of a seminar entry is below:
{% highlight yaml linenos %}
- cal_number: '7'
  name: Probability Seminar
  shortname: probability
  image: __SITE_URL__/img/seminars/tiling_v.png
  webpage: 'http://faculty.virginia.edu/Probability/'
  google_cal_id: 'f0un05c36pdv08n0m90bi99jmk@group.calendar.google.com'
  seminar_weight: 9
  regular_times: Wednesdays at 4:35
  information: |
    The Probability Seminar is the place to see talks on active research topics in probability theory, as well as informal discussions of basic notions of probability.  We typically have invited speakers every 2-3 weeks presenting a wide array of research in probability. Most other weeks are informal discussions led by local participants, often graduate students discussing recently studied topics. The seminar is open to all. Feel free to attend regularly or occasionally.
  contact:
    - name: Christian Gromoll
      email: gromoll@virginia.edu
    - name: Tai Melcher
      email: melcher@virginia.edu
    - name: Leonid Petrov
      email: petrov@virginia.edu
    - name: Axel Saenz
      email: ais6a@virginia.edu
{% endhighlight %}

Some configuration fields are self-evident. Here are explanations for the rest:

##### cal\_number

Do not touch this entry, it is needed for correct identification of the seminar in the list of upcoming talks
on the main page.

##### shortname

This is the main seminar identifier which is used in permalinks is seminar pages.

##### image

Put the image file (`jpg` or `png`, any size/dimensions, but square and up to `600x600` preferred) into the folder `/img/seminars/` in the source code, and link it in a configuration field as above.

**Important!** keep the `__SITE_URL__` prefix as is, this is needed for correct automatic generation of the website.

##### webpage

This is a link to the old seminar webpage, if needed. Once all archives are moved, this field can be eliminated which will eliminate the link from the seminar page

##### google\_cal\_id

Identifier of the goolge calendar associated with the seminar, for display on the website.

##### seminar\_weight

The bigger this parameter the lower is the seminar in the list of seminars (in the navigation bar and on the
  seminar pages).

#####  information: \|

### Changing seminar information


### Adding/removing a seminar globally

1. seminar yml
2. seminar pages and archives
3. change in google calendar javascript

if removing a seminar, keep the archives and link them maybe on the "all seminars" page, or create a special page

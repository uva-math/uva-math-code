# Mathematics at the University of Virginia

Official website of Department of Mathematics at the University of Virginia (under construction: see the current website [here](http://www.math.virginia.edu/)). Below is a working notebook associated with the initial stage of the website project.

## Implementation needed of subpages from old website:

- [ ] http://www.math.virginia.edu/directory
- [ ] http://www.math.virginia.edu/faculty
- [ ] http://www.math.virginia.edu/gradstudents
- [ ] http://www.math.virginia.edu/staff
- [ ] http://www.math.virginia.edu/news
- [ ] http://www.math.virginia.edu/calendar
- [ ] http://www.math.virginia.edu/conferences
- [ ] http://www.math.virginia.edu/awards
- [ ] http://www.math.virginia.edu/newsletter
- [ ] http://www.math.virginia.edu/content/final-exercises-ceremony-college-and-graduate-school-arts-and-sciences-0
- [ ] http://www.math.virginia.edu/content/job-opportunities
- [ ] http://www.math.virginia.edu/research
- [ ] http://www.math.virginia.edu/facultyresearch
- [ ] http://www.math.virginia.edu/seminarguide
- [ ] http://www.math.virginia.edu/academics
- [ ] http://www.math.virginia.edu/graduate
- [ ] http://www.math.virginia.edu/undergraduate
- [ ] http://www.math.virginia.edu/summer
- [ ] http://www.math.virginia.edu/courses
- [ ] http://www.math.virginia.edu/resources
- [ ] http://www.math.virginia.edu/sites/math.virginia.edu/files/Virginia%20Math%20Bulletin%2C%20June%202016.pdf


## Notes on progress and ToDos

- Two main sources of updates - google calendars of seminars, plus in-site posts for news and other things
- The posts feature is straightforward. "Categories" everywhere
- The sources of other less frequently updated information will be "seminars" and "people" in \_data and maybe other database-like structures (but not for courses I hope!.. but one can mine courses from Lou's list eventually :))
- Pages which are the most static will be just coded as html's with layouts. Hopefully there will not be many of them, and we'll need to assign some responsibility for updating those..
- There will be several layouts: main page (with special navbar?), posts page, and other pages with usual navbar; and the layouts will differ by the presence of the right-pane links!
- Need to figure out navbar conventions, too
- RSS feed for department news? (it should be easy)
- Maybe think about optimizing for small screens (so that on very small screen you first get 5 talks and then the rest?

# Conventions and guidelines on adding and modifying content

## 1. How to collaborate on the content of the Math Department website

ToDo: Levels of access; modifying in browser; pull requests; setting up local copy; previewing the website locally

## 2. Adding news/announcements entries

The following functionality is supported to display news on the main page.
To create a new news/announcement entry,
add a file with name `YYYY-MM-DD-title.md`
to the subfolder `_posts`, having the following preamble:

	---
	layout: post
	comments: false
	events: false
	published: true
	title: YOUR_TITLE
	date: YYYY-MM-DD HH:MM:SS
	categories: YOUR_CATEGORIES
	image: IMAGE_ADDRESS
	image-alt: IMAGE_ALT_TEXT
	---

Make sure to put the preamble on top of the file.

### Main parameters

- The `comments` feature is not implemented for now
-	`events: false` means that there is no list of upcoming events. Change to true in a rare case you want to add the list of upcoming events to a post. Not specified `events` means the same as `events: false`
- `published: true` is to publish the entry; replace by `false` to not publish
- Replace `YOUR_TITLE` with your title. It is helpful if the title is relatively short
- The date's HH:MM:SS is the time of publication. It is not displayed anywhere but is used to sort posts from the same day

### Categories

- In categories, put `news` to display the entry, `major-news` to display the entry in a larger format on the top page (up to one `major-news` entry will be displayed). So `categories: news major-news` will display this entry in a larger format

### Images

- In `image`, put an URL address of an external image or an address of a local image from the `img` subfolder (the image should be put into this subfolder beforehand). If using a local address, prepend it with `__SITE_URL__`, like in `image: __SITE_URL__/img/Routunda.jpg`
- `image-alt` is the alternate text for the image entered, like in `image-alt: Rotunda`
- One main image per entry is supported. If needed, other images can be added in the main text using the usual `img` tag, or in a markdown fashion
- If `image` and `image-alt` are not present then no image will be displayed, this will not cause error

### Main text of an entry

- After the above preamble ending with `---`,
write the body of the post in markdown.
A couple of guides
are [here](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
and [here in pdf](https://guides.github.com/pdfs/markdown-cheatsheet-online.pdf).
Also the use of the usual HTML is possible, e.g., for entering images and
links.

- News excerpts are supported: enter `<!--more-->`,
and the text above will be an excerpt
(displayed on the main page and the news page).
The text below will only be displayed on a separate page
dedicated to this news entry.

## 2. Adding new static pages

ToDo: static page folder; navigation in front matter; etc

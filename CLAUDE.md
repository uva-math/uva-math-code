# UVA Math Website Content Management Guidelines

This document provides comprehensive guidelines for maintaining content on the UVA Mathematics Department website.

---

## Content Structure

The website uses [Jekyll](https://jekyllrb.com/) to generate static content from markdown files. All website edits are managed through [GitHub](https://github.com/uva-math/uva-math-code), with changes taking approximately 5 minutes to appear on the live site.

---

## Post Creation and Management

### File Location

- All post files must be placed in the `_posts/` directory or one of its subdirectories
- Subdirectories (e.g., `_posts/conferences/`, `_posts/events/`, `_posts/IMS/`) are for organization only and don't affect the URL structure

### File Naming Convention

**CRITICAL**: Post filenames MUST follow this exact pattern:
```
YYYY-MM-DD-name-of-the-post.md
```

Where `YYYY-MM-DD` is **the date the file is created** (not the event date):

#### Examples:

**Correct:**
- `2023-11-15-announcing-upcoming-holiday-party.md` (created on Nov 15, 2023)
- `2025-03-12-james-teaching.md` (created on March 12, 2025, even if it announces a future event)
- `2025-04-08-AWM-mathclub-colloq.md` (created on April 8, 2025, even if the colloquium is on a different date)

**Incorrect:**
- `2023-12-20-announcing-upcoming-holiday-party.md` (using the future event date rather than creation date)
- `2025-05-17-final-exercises.md` (if created before May 17, this should use the creation date instead)

### Front Matter

Every post begins with YAML front matter, delimited by triple dashes (`---`):

```yaml
---
layout: post
title: "Title of Your Announcement"
event-date: 2025-05-09 12:00:00
multi-day-event: true
comments: false
categories: news events conferences
published: true
image: __SITE_URL__/img/news_events/example-image.jpg
image-alt: "Description of the image for accessibility"
image-tall: true
more-text: "Details and Schedule"
---
```

#### Required Front Matter Fields

- `layout: post` - Always use this for announcements
- `title` - The title displayed on both post rolls and the post page
- `categories` - Determines where the post appears (see Categories section below)

#### Recommended Front Matter Fields

- `event-date` - The actual date of the event (format: YYYY-MM-DD HH:MM:SS)
- `multi-day-event` - Set to `true` for events spanning multiple days
- `published` - Set to `true` by default. Set to `false` to hide a post completely

#### Optional Front Matter Fields

- `image` - Path to the post image (use `__SITE_URL__` prefix: `__SITE_URL__/img/news_events/image.jpg`)
- `image-alt` - Alternative text for the image (for accessibility)
- `image-tall` or `image-wide` - Add if your image has unusual dimensions
- `image-address` - URL where clicking the image leads (defaults to post page if omitted)
- `more-text` - Custom text for the "read more" button (defaults to "View details")
- `hide-this-item: true` - Hides post from main page but not from category pages or all news
- `permalink` - Custom URL for the post (default is `/YYYY/MM/name-of-the-post`)

### Categories

Categories determine where posts appear on the website. Always include appropriate categories:

```yaml
categories: news events conferences
```

#### Key Categories:

- `news` - Required for posts to appear on the main page (up to 5 most recent)
- `events` - Use for all event announcements
- `conferences` - **Required** for all workshop, symposium, and conference announcements
- `major-news` - Makes the post appear larger at the top of the main page
- `virginia-mathematics-lectures` - For IMS lecture announcements
- `awards` - For award announcements
- `jobs` - For job opportunity posts
- `virginia-math-bulletin` - For Virginia Math Bulletin issues

#### Category Usage Examples:

- Conference announcement: `categories: news events conferences`
- Major department event: `categories: news events major-news`
- Award announcement: `categories: news awards`
- IMS lecture: `categories: news events virginia-mathematics-lectures ims`

### Post Content

- Use markdown for post content
- Place `<!--more-->` to separate the excerpt (shown in list views) from full content
- Include key details in the excerpt for visibility in post rolls
- Math formulas are supported using LaTeX syntax

### Images

- Store images in `/img/news_events/` or an appropriate subfolder of `/img/`
- Reference images with the `__SITE_URL__` prefix: `__SITE_URL__/img/news_events/image.jpg`
- For the main post image, use the `image` front matter field
- Additional images can be added manually in the post content using markdown

---

## Internal Links

Always use `{% raw %}{{site.url}}{% endraw %}` prefix for internal links instead of absolute or relative paths:

```
{% raw %}[Link text]({{site.url}}/path/to/page){% endraw %}
```

This ensures links work correctly across different environments.

---

## Publishing Workflow

1. Create a new file with the correct naming convention in the appropriate subfolder
2. Add all required front matter with appropriate categories
3. Write your content, separating excerpt with `<!--more-->`
4. Commit changes to GitHub
5. Wait approximately 5 minutes for changes to appear on the live site

---

## Page Visibility

- **Main Department Page**: Shows 5 most recent posts with the `news` category
- **All News Page**: Shows all published posts regardless of category
- **Category Pages**: Show all posts with specific categories (e.g., conferences page)

Use `hide-this-item: true` to hide items from the main page after they're no longer timely, while keeping them in archives.

---

For more detailed documentation, see the [website documentation pages](https://math.virginia.edu/doc/).

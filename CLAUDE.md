# UVA Math Website Content Management Guidelines

This document provides comprehensive guidelines for maintaining content on the UVA Mathematics Department website.

## Common Tasks

Many content management requests come via email from department colleagues. These typically include:
- Posting seminar/colloquium abstracts
- Announcing conferences and workshops
- Updating speaker information
- Publishing award and defense announcements
- Adding job postings

When processing email requests, extract the key information (speaker names, titles, abstracts, dates, locations) and format according to the guidelines below.

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
categories: news events conferences swiper-news
published: true
image: __SITE_URL__/img/news_events/example-image.jpg
image-alt: "Description of the image for accessibility"
image-tall: true
more-text: "Details and Schedule"
good-md: true
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
- `good-md: true` - Indicates that the markdown in the post is well-formed (affects rendering)

### Categories

Categories determine where posts appear on the website. Always include appropriate categories:

```yaml
categories: news events conferences
```

#### Key Categories:

- `news` - Required for posts to appear on the main page (up to 5 most recent)
- `events` - Use for all event announcements
- `conferences` - **Required** for all workshop, symposium, and conference announcements
- `major-news` - Makes the post appear larger at the top of the main page (for non-swiper posts)
- `swiper-news` - Includes post in the carousel/slider on the main page (limited to 6 posts)
- `virginia-mathematics-lectures` - For IMS lecture announcements
- `awards` - For award announcements
- `jobs` - For job opportunity posts
- `virginia-math-bulletin` - For Virginia Math Bulletin issues
- `ims` - For IMS-related announcements
- `ims-special` - For special IMS events

#### Category Usage Examples:

- Conference announcement: `categories: news events conferences`
- Featured award announcement: `categories: news awards swiper-news`
- Major department event: `categories: news events major-news`
- IMS lecture: `categories: news events virginia-mathematics-lectures ims`

### Content Display Controls

- **Carousel/Swiper**: Add `swiper-news` category to include a post in the main page carousel (limited to 6 posts)
- **Featured Box**: Posts with `major-news` that don't have `swiper-news` appear in a larger gray box below the carousel
- **Standard Display**: Other posts with the `news` category appear in the main news grid

### Post Content

- Use markdown for post content
- Place `<!--more-->` to separate the excerpt (shown in list views) from full content
- Include key details in the excerpt for visibility in post rolls
- Add `good-md: true` to front matter if your post contains well-formatted markdown
- Math formulas are supported using LaTeX syntax

### Images

- Store images in `/img/news_events/` or an appropriate subfolder of `/img/`
- Reference images with the `__SITE_URL__` prefix: `__SITE_URL__/img/news_events/image.jpg`
- For carousel/swiper posts, use an image with aspect ratio around 16:9 for best results
- For the main post image, use the `image` front matter field
- Additional images can be added manually in the post content using markdown

#### Combining Multiple Images

To combine multiple photos into a single wider image for carousel posts, use ImageMagick:
```bash
magick image1.png image2.png +append combined-output.png
```
This creates a horizontally combined image. Add `image-wide: true` to the front matter when using wide combined images.

---

## Internal Links

Always use `{% raw %}{{site.url}}{% endraw %}` prefix for internal links instead of absolute or relative paths:

```
{% raw %}[Link text]({{site.url}}/path/to/page){% endraw %}
```

This ensures links work correctly across different environments.

---

## People References

### Finding People Files

People profile files are named by UVA computing ID (e.g., `ntr2qp.md`), not by person's name. To find someone's profile:
1. Search (grep) for their first or last name within `_departmentpeople/` to locate the file
2. Common fields to update: `personal_page`, `office`, `phone`, `image`

### Referencing People in Posts

To reference department members, use the person_info include rather than hardcoding names:

```
{% raw %}{% include person_info_just_name.html UVA_id="cc2wn" %}{% endraw %}
```

Available include formats:
- `person_info.html` - Full name, title, email, phone
- `person_info_just_name.html` - Just the person's name
- `person_info_email_only.html` - Name with email
- `person_info_no_phone.html` - Name, title, email (no phone)

---

## Publishing Workflow

1. Create a new file with the correct naming convention in the appropriate subfolder
2. Add all required front matter with appropriate categories
3. Write your content, separating excerpt with `<!--more-->`
4. Commit and push changes to GitHub (push immediately after committing, do NOT include AI attribution in commit messages)
5. Wait approximately 5 minutes for changes to appear on the live site

---

## Page Visibility

- **Main Page Carousel**: Shows up to 6 posts with `swiper-news` category
- **Main Page Featured Box**: Shows 1 post with `major-news` (without `swiper-news`)
- **Main Page News Grid**: Shows up to 6 regular posts with `news` category
- **All News Page**: Shows all published posts regardless of category
- **Category Pages**: Show all posts with specific categories (e.g., conferences page)

Use `hide-this-item: true` to hide items from the main page after they're no longer timely, while keeping them in archives.

---

## Special Post Types

### Defenses

PhD and DMP defense announcements should be created in `_posts/defenses/` with format:
```
YYYY-MM-DD-lastname-defense.md
```

Example categories: `categories: news events defenses`

### Job Postings

Job postings should be created in `_posts/jobs/` with format:
```
YYYY-MM-DD-jobs-YYYY.md
```

Example categories: `categories: news jobs`

---

For more detailed documentation, see the [website documentation pages](https://math.virginia.edu/doc/).

---

## Repository Structure Overview

This repository contains the source code for the University of Virginia Mathematics Department website (math.virginia.edu). It's a Jekyll-based static site that serves comprehensive information about the department's academic programs, people, research, and events.

### Key Technology Stack
- **Jekyll** - Static site generator that converts markdown to HTML
- **GitHub Pages** - Hosting and deployment
- **Markdown** - Primary content format
- **YAML** - Configuration and structured data

### Major Content Areas

1. **News & Events** (`_posts/`)
   - Organized by type: conferences, awards, defenses, jobs, events
   - Date-based naming: `YYYY-MM-DD-title.md`
   - Categories control where posts appear on the site

2. **People Profiles** (`_departmentpeople/`)
   - Separate folders for faculty, students, postdocs, staff
   - Files named by UVA computing ID (e.g., `ko5wk.md`)
   - Standardized profile format with front matter

3. **Academic Programs**
   - `undergraduate/` - Degree requirements, courses, advising
   - `graduate/` - PhD program, exams, funding
   - `seminars/` - Weekly seminar schedules

4. **Special Programs**
   - `IMS/` - Institute of Mathematical Sciences
   - `RTG_geomtop/` - NSF-funded Research Training Group
   - `awm/` - Women in Mathematics chapter
   - `drp/` - Directed Reading Program
   - `mathcircle/` - K-12 outreach

5. **Data Files** (`_data/`)
   - `courses.yml` - Course catalog
   - `seminars.yml` - Seminar configurations
   - `research_areas.yml` - Research group definitions

### Content Management Patterns
- Posts must include front matter with title, categories, and layout
- Internal links use `{% raw %}{{site.url}}{% endraw %}` prefix
- People references use include files rather than hardcoded names
- Categories determine post visibility on different pages
- Changes take ~5 minutes to appear on live site after GitHub commit

---

## Dark Mode Implementation

The website features a comprehensive dark mode that automatically adapts to user preferences and can be manually toggled.

### Key Features

1. **Automatic OS Detection**: The site respects the user's operating system dark mode preference on first visit
2. **Manual Toggle**: Users can override the OS preference using a toggle button in the navbar
3. **Persistent Preference**: User's choice is saved in localStorage and persists across sessions
4. **Smooth Transitions**: All color changes animate smoothly when switching themes

### Toggle Button Design

- **Location**: Main navbar, positioned to the left of "Support us" link
- **Mobile**: Remains visible on small screens, positioned to the left of the vertical dots menu on special pages
- **Design**: Dual-icon toggle showing both cloud-sun (day) and moon (night) icons with a sliding indicator
- **Interaction**: Click anywhere on the button to toggle between light and dark modes

### Technical Implementation

#### CSS Architecture

The dark mode uses CSS custom properties (variables) defined in `/css/main.css`:

```css
:root {
  --bg-color: #ffffff;
  --text-color: #212529;
  --card-bg: #ffffff;
  /* ... other light mode variables */
}

[data-theme="dark"] {
  --bg-color: #0a1628;  /* Very dark navy blue */
  --text-color: #e8e8e8;
  --card-bg: #1a2a3f;  /* Dark navy blue */
  /* ... other dark mode variables */
}
```

#### Color Scheme

The dark mode uses a sophisticated navy blue color palette aligned with UVA branding:
- **Background**: `#0a1628` (very dark navy)
- **Cards/Panels**: `#1a2a3f` (dark navy)
- **Hover States**: `#243448` (slightly lighter navy)
- **Active States**: `#003d7a` (UVA blue variation)
- **Text**: `#e8e8e8` (light gray)
- **Links**: `#4da3ff` (lighter blue for contrast)

#### JavaScript Functionality

Located in `_includes/footer.html`, the dark mode script:
1. Checks localStorage for saved preference
2. Falls back to OS preference if no saved preference
3. Applies theme by setting `data-theme` attribute on `<html>`
4. Handles toggle button clicks and touch events
5. Listens for OS theme changes (respects if user hasn't manually set preference)

### Component-Specific Styling

#### Navigation
- **Navbar**: Background remains light with adjusted toggle button colors
- **Hamburger/Dots**: Icons turn light gray (#e8e8e8) in dark mode
- **Dropdowns**: Dark backgrounds with appropriate contrast

#### Sidebars
- **List Groups**: Dark gray (#243448) backgrounds instead of white
- **Orange Headers**: Adjusted orange tones for visibility
- **Active Items**: UVA blue variation (#003d7a) for selected items

#### Content Areas
- **Cards**: All use dark navy backgrounds
- **Jumbotrons**: Special handling for major-news sections
- **Zebra Striping**: Alternating rows use darker navy (#162133)
- **Code Blocks**: Dark backgrounds with syntax highlighting

#### Forms
- **Search Bar**: Semi-transparent backgrounds with light borders
- **Input Fields**: Dark backgrounds with light text
- **Buttons**: Appropriate contrast adjustments

### Best Practices for Content Creators

1. **Images**: Ensure images have sufficient contrast for both light and dark modes
2. **Colors**: Avoid hardcoding colors in inline styles; use CSS classes instead
3. **Backgrounds**: Test content visibility in both modes before publishing
4. **Icons**: Use Font Awesome icons which automatically adapt to the theme

### Testing Dark Mode

To test dark mode functionality:
1. Click the toggle button in the navbar
2. Check that all text remains readable
3. Verify interactive elements maintain proper contrast
4. Ensure images and media display correctly
5. Test on both desktop and mobile devices

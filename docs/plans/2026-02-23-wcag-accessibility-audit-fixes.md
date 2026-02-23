# WCAG 2.1 AA Accessibility Audit and Fixes

## Overview

Site-wide accessibility audit of the UVA Mathematics Department website (Jekyll-based) identified 18+ issues across critical, major, and minor severity levels. This plan addresses all critical and major issues, plus selected minor issues, organized into logical tasks by component area. The local site at localhost:4000 will be used with the agentic browser for live verification of each fix.

## Audit Summary

### Critical Issues

- C1: Course tooltip `<span>` elements are not keyboard-accessible (invalid `href` on span, no tabindex, no role) - affects every page with course references
- C2: Icon-only email links have no accessible name in all person_info includes - affects nearly every page
- C3: Duplicate `<title>` elements in `<head>` (layout sets one, header.html sets another) - affects ug_page, g_page, and other layouts
- C4: Seminar separator rendered as a navigable link "---" in navbar dropdown

### Major Issues

- M1: Focus indicator suppressed on `.navbar-toggler:focus` without proper fallback
- M2: Duplicate sidebar `<nav>` landmarks with identical `aria-label` (mobile + desktop)
- M3: Active sidebar items lack `aria-current="page"` attribute
- M4: `.my-tooltip` border uses black with no dark mode override (invisible in dark mode)
- M5: `summary:hover/focus` background has no dark mode override (text becomes unreadable)
- M6: Heading hierarchy broken across multiple undergraduate content pages
- M7: Placement exam HTML files lack `lang="en"` attribute
- M8: Tables in placement.md lack proper `<th scope>` and `<thead>` markup
- M9: Non-descriptive link text ("is here", "link") in undergraduate content pages
- M10: `target="_blank"` links in footer missing `rel="noopener noreferrer"`
- M11: Carousel post titles use `<span class="h4">` instead of real heading elements

## Context

- Files involved: `_includes/course`, `_includes/person_info*.html`, `_includes/DUS.html`, `_includes/navbar.html`, `_includes/header.html`, `_includes/footer.html`, `_includes/ug_sidebar.html`, `_includes/g_sidebar.html`, `_includes/top_brand.html`, `_includes/details_header.html`, `_layouts/ug_page.html`, `_layouts/g_page.html`, `_layouts/post.html`, `css/main.css`, `index.html`, `undergraduate/placement.md`, `undergraduate/diagnostic.md`, `undergraduate/MCLC/MCLC.md`, `undergraduate/placement-files/*.html`, `_data/seminars.yml`
- Related patterns: Site already has good skip-link, ARIA labels on nav, visually-hidden class, reduced-motion support, dark mode toggle with aria-pressed
- Dependencies: None (pure HTML/CSS/Jekyll changes)
- Testing: Local Jekyll site at localhost:4000 with agentic browser for live verification

## Development Approach

- Complete each task fully before moving to the next
- After each task, use the agentic browser to verify the fix at localhost:4000
- Verify both light mode and dark mode for CSS changes using the browser
- Test keyboard navigation using the browser where applicable

## Implementation Steps

### Task 1: Fix course tooltip accessibility (C1)

**Files:**
- Modify: `_includes/course`
- Modify: `css/main.css`

- [ ] Change `<span>` to `<a>` element in `_includes/course` so the `href` attribute works and the element is keyboard-focusable
- [ ] Ensure the tooltip still triggers on hover/focus for the `<a>` element
- [ ] Add dark mode override for `.my-tooltip` border-bottom color (M4: change from `black` to use a visible color in dark mode)
- [ ] Use agentic browser to visit localhost:4000/undergraduate/ and verify course tooltips are visible, keyboard-focusable, and display correctly in both light and dark mode

### Task 2: Fix icon-only email links in person_info includes (C2)

**Files:**
- Modify: `_includes/person_info_email_only.html`
- Modify: `_includes/person_info.html`
- Modify: `_includes/person_info_no_phone.html`
- Modify: `_includes/DUS.html`

- [ ] Add `aria-label="Email {{ ppl.name }} {{ ppl.lastname }}"` to each `<a href="mailto:...">` that wraps an icon-only envelope
- [ ] In DUS.html, use appropriate aria-label for the hardcoded math-dus email address
- [ ] Use agentic browser to visit localhost:4000/undergraduate/contacts/ and inspect that email icon links have accessible names

### Task 3: Fix duplicate title and navbar issues (C3, C4)

**Files:**
- Modify: `_layouts/ug_page.html`
- Modify: `_layouts/g_page.html` (same pattern)
- Modify: `_includes/navbar.html`
- Modify: `_data/seminars.yml`

- [ ] Remove the `<title>` tag from layout files that also include header.html (header.html already sets `<title>`), OR remove from header.html and keep in layouts. Choose whichever preserves the more descriptive title (layouts have section info like "| Undergraduate Program |")
- [ ] Check all other layouts for the same duplicate title pattern and fix
- [ ] In `_includes/navbar.html`, filter out seminar entries with shortname "separator" and render a `<div class="dropdown-divider" role="separator"></div>` instead of a link
- [ ] Alternatively, add `published_in_nav: false` to the separator entry in `_data/seminars.yml` if the existing `unless` logic handles it
- [ ] Use agentic browser to visit localhost:4000/undergraduate/ and inspect the page source to confirm only one `<title>` element exists; also check the Seminars navbar dropdown for proper separator rendering

### Task 4: Fix navbar focus and footer link accessibility (M1, M10)

**Files:**
- Modify: `css/main.css`
- Modify: `_includes/footer.html`

- [ ] Change `.navbar-toggler:focus { box-shadow: none; }` to `.navbar-toggler:focus:not(:focus-visible) { box-shadow: none; }` so keyboard-only focus still shows an indicator
- [ ] Add `rel="noopener noreferrer"` to all `target="_blank"` links in footer.html
- [ ] Fix the copyright link: change `target="new"` to `target="_blank"` and add rel attribute
- [ ] Update `http://` URLs in footer to `https://` where possible (twitter, copyright)
- [ ] Use agentic browser to visit localhost:4000/ and verify footer links open correctly; tab through the page to verify focus indicators are visible on the navbar hamburger button

### Task 5: Fix duplicate sidebar landmarks and add aria-current (M2, M3)

**Files:**
- Modify: `_layouts/ug_page.html`
- Modify: `_layouts/g_page.html`
- Modify: `_includes/ug_sidebar.html`
- Modify: `_includes/g_sidebar.html`

- [ ] In ug_page.html (and g_page.html), add `aria-hidden="true"` to the mobile-collapsed duplicate sidebar, OR give the two instances distinct aria-labels
- [ ] Add `aria-current="page"` to active sidebar links: where `{% if page.permalink == pg.permalink %}active{% endif %}` appears, also add `aria-current="page"` conditionally
- [ ] Apply the same pattern to g_sidebar.html
- [ ] Use agentic browser to visit localhost:4000/undergraduate/ and localhost:4000/content/distinguished-major-program-dmp/ to verify sidebar landmarks are distinct and active item has aria-current

### Task 6: Fix dark mode contrast issues (M5)

**Files:**
- Modify: `_includes/details_header.html`
- Modify: `css/main.css`

- [ ] Add dark mode override for `summary:hover, summary:focus` in details_header.html inline style block: use a dark-appropriate background color (e.g., `#243448`) when `[data-theme="dark"]`
- [ ] Use agentic browser to visit localhost:4000/undergraduate/ in dark mode, hover/focus on summary/details elements and verify text remains readable

### Task 7: Fix heading hierarchy in undergraduate content pages (M6)

**Files:**
- Modify: `undergraduate/degree_requirements.md`
- Modify: `undergraduate/contacts.md`
- Modify: `undergraduate/where_go.md`
- Modify: `undergraduate/tutoring_grader.md`
- Modify: `undergraduate/competitions.md`

- [ ] In degree_requirements.md: replace `#####` (h5) headings with `###` (h3), and fix any `<h1>` that appears below h3 to be `##` (h2)
- [ ] In contacts.md: replace `<h5>` section headings with `##` (h2), and remove `<h5>` from inside `<li>` elements
- [ ] In where_go.md: ensure single h1, demote second `<h1>` to `##`, fix h1-to-h3 skip
- [ ] In tutoring_grader.md and competitions.md: add an h1 or h2 page title if missing, ensure headings don't start at h3
- [ ] Use agentic browser to visit each page at localhost:4000 and verify heading hierarchy renders correctly (visually inspect heading sizes and structure)

### Task 8: Fix placement page accessibility (M7, M8)

**Files:**
- Modify: `undergraduate/placement-files/1210.html`
- Modify: `undergraduate/placement-files/1220.html`
- Modify: `undergraduate/placement-files/1310.html`
- Modify: `undergraduate/placement-files/1320.html`
- Modify: `undergraduate/placement-files/CP_ExamA.html`
- Modify: `undergraduate/placement-files/CP_ExamB.html`
- Modify: `undergraduate/placement-files/CP_ExamC.html`
- Modify: `undergraduate/placement-files/diagnostic_1210_1220.html`
- Modify: `undergraduate/placement-files/diagnostic_1310_1320.html`
- Modify: `undergraduate/placement-files/diagnostic_1320_2310.html`
- Modify: `undergraduate/placement-backup.html`
- Modify: `undergraduate/placement.md`

- [ ] Add `lang="en"` to all `<html>` tags in placement-files/*.html and placement-backup.html
- [ ] In placement.md: convert the "AP Test and Score" table header row from `<td><p><strong>` to proper `<th scope="col">` inside a `<thead>`
- [ ] Ensure both tables in placement.md have `<thead>` with `<th scope="col">` for column headers
- [ ] Use agentic browser to visit localhost:4000/undergraduate/placement/ and verify tables render correctly with proper header semantics

### Task 9: Fix non-descriptive link text (M9)

**Files:**
- Modify: `undergraduate/diagnostic.md`
- Modify: `undergraduate/MCLC/MCLC.md`

- [ ] In diagnostic.md: replace "is here" link text with descriptive text (e.g., "Path 1 diagnostic" / "Path 2 diagnostic" / "Path 3 diagnostic")
- [ ] In MCLC/MCLC.md: replace bare "link" text with descriptive text; also update the YouTube iframe title from "YouTube video player" to something descriptive like "Introduction to the Math Collaborative Learning Center"
- [ ] Use agentic browser to visit localhost:4000/undergraduate/diagnostic/ and localhost:4000/undergraduate/MCLC/MCLC/ to verify links have descriptive text

### Task 10: Fix carousel heading semantics (M11)

**Files:**
- Modify: `index.html`

- [ ] In the carousel section, change `<span class="h4 mb-3">` to an actual `<h3>` (or appropriate heading level) for post titles
- [ ] Ensure the heading styling is preserved via CSS class
- [ ] Use agentic browser to visit localhost:4000/ and verify carousel titles render with proper heading elements

### Task 11: Fix image alt text fallback

**Files:**
- Modify: `_layouts/post.html`
- Modify: `index.html`

- [ ] Add fallback alt text when `page.image-alt` is not provided: use `{{ page.title }}` as default
- [ ] Apply the same pattern in index.html carousel where `post.image-alt` is used
- [ ] Use agentic browser to visit localhost:4000/ and inspect carousel images to verify alt text is present

### Task 12: Final verification with agentic browser

- [ ] Use agentic browser to visit localhost:4000/undergraduate/ - check page title, heading hierarchy, course tooltips, sidebar landmarks, skip navigation
- [ ] Use agentic browser to visit localhost:4000/content/distinguished-major-program-dmp/ - check sidebar, heading hierarchy, person info email links
- [ ] Use agentic browser to visit localhost:4000/ - check carousel headings, image alt text, navbar separator, footer links
- [ ] Toggle dark mode via the browser and verify tooltip borders, summary hover states, and general contrast on the above pages
- [ ] Tab through interactive elements on localhost:4000/undergraduate/ to verify keyboard accessibility of course tooltips and email links

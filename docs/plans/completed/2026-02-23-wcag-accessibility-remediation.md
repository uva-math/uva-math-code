# WCAG 2.1 AA Accessibility Remediation - Critical and Major Issues

## Overview

Fix the 16 highest-severity WCAG 2.1 AA accessibility violations found in the UVA Mathematics Department Jekyll website, covering all 6 critical issues (skip navigation, main landmark, carousel accessibility, focus indicators) and all 10 major issues (ARIA labels, form accessibility, sr-only class, HTML parsing, motion preferences, navigation landmarks).

## Context

- Files involved:
  - `_layouts/default.html`, `_layouts/post.html`, `_layouts/ug_page.html`, `_layouts/g_page.html`, `_layouts/static_page_no_right_menu.html` (landmark structure)
  - `index.html` (carousel, main page structure, malformed HTML)
  - `_includes/navbar.html` (dark mode toggle, sr-only class, focus)
  - `_includes/top_brand.html` (search form)
  - `_includes/footer.html` (social links, touch handlers, footer nav)
  - `_includes/ug_sidebar.html`, `_includes/g_sidebar.html` (sidebar landmarks)
  - `css/main.css` (focus indicators, reduced motion, visually-hidden class)
- Related patterns: Bootstrap 5 utility classes, Font Awesome icons, Swiper.js carousel
- Dependencies: None (all changes are to existing HTML, CSS, and JS)
- Testing tools: `agent-browser` CLI (installed at /opt/homebrew/bin/agent-browser) with site running at http://localhost:4000
  - `agent-browser snapshot` - produces an accessibility tree for verifying landmarks, ARIA labels, roles
  - `agent-browser eval <js>` - run JavaScript for programmatic checks
  - `agent-browser press <key>` - test keyboard navigation (Tab, Enter, arrow keys)
  - `agent-browser screenshot [path]` - capture visual state for focus indicator checks

## Development Approach

- No automated test suite exists for this Jekyll site
- Verify each task using `agent-browser` against http://localhost:4000:
  - Use `agent-browser snapshot` to check accessibility tree structure after each task
  - Use `agent-browser press Tab` and `agent-browser screenshot` to verify keyboard focus
  - Use `agent-browser eval` for programmatic DOM and ARIA state checks
- Complete each task fully before moving to the next
- Test in both light and dark modes after CSS changes

## Implementation Steps

### Task 1: Add Skip Navigation Link and Main Landmark

**Files:**
- Modify: `_layouts/default.html`
- Modify: `_layouts/post.html`
- Modify: `_layouts/ug_page.html`
- Modify: `_layouts/g_page.html`
- Modify: `_layouts/static_page_no_right_menu.html`
- Modify: `index.html`
- Modify: `css/main.css`

Addresses: C1 (no skip-to-content link), C2 (no main landmark)

- [x] Add CSS class for visually-hidden-focusable skip link in `css/main.css` (only visible on focus)
- [x] Add `<a href="#main-content" class="skip-link">Skip to main content</a>` as the first child of `<body>` in each layout file
- [x] Wrap the primary content area in `<main id="main-content">` in each layout file and `index.html`
- [x] Verify with agent-browser: `agent-browser open http://localhost:4000 && agent-browser snapshot` - confirm `main` landmark appears in accessibility tree
- [x] Verify with agent-browser: `agent-browser press Tab && agent-browser screenshot /tmp/skip-link.png` - confirm skip link is visible on focus

### Task 2: Carousel Pause Control and Keyboard Navigation

**Files:**
- Modify: `index.html` (Swiper initialization and slide markup)
- Modify: `css/main.css` (button styling)

Addresses: C3 (no pause button), C4 (not keyboard accessible)

- [x] Add a visible pause/play toggle button near the carousel with `aria-label="Pause carousel"` and update label dynamically
- [x] Add previous/next navigation buttons with `aria-label="Previous slide"` and `aria-label="Next slide"`
- [x] Configure Swiper to use keyboard navigation (`keyboard: { enabled: true }`)
- [x] Ensure pagination bullets are keyboard-focusable (configure Swiper `pagination.clickable` and add ARIA labels)
- [x] Add JavaScript to toggle autoplay on pause button click, updating `aria-pressed` state
- [x] Verify with agent-browser: `agent-browser open http://localhost:4000 && agent-browser snapshot` - confirm pause button and slide navigation appear in tree with correct labels
- [x] Verify with agent-browser: `agent-browser press Tab` repeatedly to reach carousel controls, then `agent-browser press Enter` to activate pause

### Task 3: Restore Focus Indicators

**Files:**
- Modify: `css/main.css`
- Modify: `_includes/navbar.html` (remove shadow-none if present)

Addresses: C5 (dark mode toggle focus removed), C6 (hamburger toggle focus removed)

- [x] Replace `.theme-toggle-dual:focus { outline: none; }` with a visible focus indicator (e.g., `outline: 2px solid #002F6C; outline-offset: 2px;`)
- [x] Replace `.navbar-toggler:focus { box-shadow: none; }` with a visible focus style
- [x] Remove `shadow-none` from navbar toggler elements in `_includes/navbar.html` if it suppresses focus
- [x] Ensure focus indicators meet 3:1 contrast ratio in both light and dark modes
- [x] Verify with agent-browser: Tab to dark mode toggle, take screenshot to confirm focus ring: `agent-browser open http://localhost:4000 && agent-browser focus ".theme-toggle-dual" && agent-browser screenshot /tmp/focus-toggle.png`
- [x] Verify with agent-browser: Tab to hamburger (at mobile viewport), take screenshot: `agent-browser focus ".navbar-toggler" && agent-browser screenshot /tmp/focus-hamburger.png`

### Task 4: ARIA Labels and Accessible Names

**Files:**
- Modify: `_includes/footer.html` (social media links)
- Modify: `_includes/top_brand.html` (search form)
- Modify: `_includes/navbar.html` (dark mode toggle buttons)

Addresses: M1 (social links missing names), M2 (search input no label), M3 (search form no role), M4 (toggle missing state)

- [x] Add `aria-label` to the Twitter/X social media link in footer (both mobile and desktop instances)
- [x] Add `aria-label` to all other social links that rely only on `title` attribute
- [x] Add `aria-label="Search the UVA website"` to the search input field
- [x] Add `role="search"` and `aria-label="Site search"` to the search `<form>` element
- [x] Add `aria-label="Toggle dark mode"` and `aria-pressed="false"` to both dark mode toggle buttons
- [x] Update the `applyTheme()` JavaScript function in footer.html to dynamically set `aria-pressed` to `"true"` or `"false"` based on current theme
- [x] Verify with agent-browser: `agent-browser open http://localhost:4000 && agent-browser snapshot` - confirm social links, search form, and toggle all have accessible names
- [x] Verify with agent-browser: `agent-browser eval "document.querySelector('.theme-toggle-dual').getAttribute('aria-pressed')"` - confirm returns "false" or "true" matching current theme

### Task 5: Fix sr-only Class and Malformed HTML

**Files:**
- Modify: `_includes/navbar.html` (sr-only to visually-hidden)
- Modify: `index.html` (malformed span/a nesting)
- Modify: `css/main.css` (ensure visually-hidden class exists as fallback)

Addresses: M5 (sr-only class undefined), M6 (span closed after anchor)

- [x] Replace all `sr-only` class references with `visually-hidden` in `_includes/navbar.html`
- [x] Search the entire codebase for other `sr-only` usages and replace them
- [x] Fix the malformed `<a>...<span>...</a></span>` nesting on index.html line 57 to `<a><span>...</span></a>`
- [x] Ensure Bootstrap 5's `visually-hidden` class is available (or add a CSS definition if the Bootstrap build does not include it)
- [x] Verify with agent-browser: `agent-browser open http://localhost:4000 && agent-browser eval "document.querySelectorAll('.sr-only').length"` - confirm returns 0
- [x] Verify with agent-browser: `agent-browser eval "document.querySelector('#main-content').outerHTML"` to spot-check no malformed nesting remains

### Task 6: Event Handling and Reduced Motion

**Files:**
- Modify: `_includes/footer.html` (remove touchstart handler)
- Modify: `css/main.css` (add prefers-reduced-motion)
- Modify: `index.html` (respect reduced motion in Swiper config)

Addresses: M7 (duplicate touch/click handlers), M8 (no prefers-reduced-motion)

- [x] Remove the `touchstart` event listeners from the dark mode toggle buttons in footer.html; keep only the `click` handler
- [x] Add `@media (prefers-reduced-motion: reduce)` block to `css/main.css` that disables transitions and animations site-wide
- [x] Add JavaScript check for `prefers-reduced-motion` to disable Swiper autoplay for users who prefer reduced motion
- [x] Verify with agent-browser: `agent-browser open http://localhost:4000 && agent-browser click ".theme-toggle-dual"` - confirm toggle works via click event
- [x] Verify with agent-browser: `agent-browser eval "window.matchMedia('(prefers-reduced-motion: reduce)').matches"` - check reduced motion detection is wired up

### Task 7: Navigation Landmark Labels

**Files:**
- Modify: `_includes/top_brand.html` (add aria-label to nav)
- Modify: `_includes/navbar.html` (add aria-label to nav)
- Modify: `_includes/footer.html` (wrap social links in nav)
- Modify: `_includes/ug_sidebar.html` (wrap in nav)
- Modify: `_includes/g_sidebar.html` (wrap in nav)

Addresses: M9 (footer social links not in nav), M10 (sidebars lack nav landmark)

- [x] Add `aria-label="University brand and search"` to the `<nav>` in `top_brand.html`
- [x] Add `aria-label="Main navigation"` to the `<nav>` in `navbar.html`
- [x] Wrap the social media links section in `_includes/footer.html` with `<nav aria-label="Social media">`
- [x] Wrap `_includes/ug_sidebar.html` content in `<nav aria-label="Undergraduate program">`
- [x] Wrap `_includes/g_sidebar.html` content in `<nav aria-label="Graduate program">`
- [x] Verify with agent-browser: `agent-browser open http://localhost:4000 && agent-browser snapshot` - confirm all navigation landmarks appear with distinct labels
- [x] Verify with agent-browser: `agent-browser open http://localhost:4000/undergraduate && agent-browser snapshot` - confirm sidebar nav landmark appears

### Task 8: Verify Acceptance Criteria

All verification against http://localhost:4000 using agent-browser:

- [x] Full keyboard navigation test: `agent-browser open http://localhost:4000` then repeatedly `agent-browser press Tab` through skip link, navbar, carousel controls, content, footer - confirm all interactive elements are reachable
- [x] Accessibility tree completeness: `agent-browser snapshot` on home page - confirm main landmark, all nav landmarks with labels, carousel controls, search form
- [x] Dark mode toggle test: `agent-browser click ".theme-toggle-dual"` then `agent-browser eval "document.documentElement.getAttribute('data-theme')"` - confirm theme switches and `aria-pressed` updates
- [x] Carousel pause test: click pause button, wait 5 seconds, verify slide did not advance
- [x] Focus indicators: `agent-browser focus` on key interactive elements + `agent-browser screenshot` - confirm visible focus rings in both themes
- [x] Reduced motion: `agent-browser eval "CSS.supports('(prefers-reduced-motion: reduce)')"` - confirm media query is supported in the stylesheet
- [x] Run Lighthouse accessibility audit: `agent-browser eval` to inject and run axe-core, or use `agent-browser snapshot` to manually verify tree
- [x] Test a post page: `agent-browser open http://localhost:4000/2026/02/...` (a recent post) and `agent-browser snapshot` - confirm main landmark and skip link work on post layout
- [x] Verify no HTML validation errors related to the changes

### Task 9: Update Documentation

- [x] Update CLAUDE.md to note accessibility patterns (skip link, aria-label conventions, visually-hidden class usage)
- [x] Move this plan to `docs/plans/completed/`

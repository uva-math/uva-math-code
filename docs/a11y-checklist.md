# WCAG 2.1 Level AA Accessibility Checklist

Comprehensive checklist derived from accessibility work on lpetrov.cc (commits d44ded7b through b4f5e47b). Use this to audit and fix other websites.

---

## 1. Page Structure & Landmarks

- [ ] `<html lang="en">` set on root element
- [ ] Single `<h1>` per page (use `sr-only` class if visually hidden)
- [ ] Heading hierarchy is sequential: H1 → H2 → H3 (no skipping levels)
- [ ] `<main id="main-content">` wraps page content
- [ ] `<nav aria-label="Main navigation">` on primary nav
- [ ] `<footer>` wraps footer content
- [ ] Skip navigation link: `<a class="skip-link" href="#main-content">Skip to main content</a>` as first child of `<body>`

## 2. Semantic HTML

- [ ] Use `<strong>` instead of `<b>` for emphasis (screen readers announce `<strong>`)
- [ ] Use `<em>` instead of `<i>` for italic emphasis (except icon fonts with `aria-hidden="true"`)
- [ ] `<li>` elements only appear inside `<ul>` or `<ol>` parents
- [ ] Use `<table>` with `aria-label` for data tables; add `<th>` headers
- [ ] `<details>/<summary>` for collapsible content (semantically accessible)
- [ ] Lists (`<ul>`, `<ol>`) used for groups of related items, not `<div>` sequences

## 3. Links

### External links (`target="_blank"`)
- [ ] Every `target="_blank"` link has `<span class="sr-only"> (opens in new tab)</span>` before `</a>`
- [ ] Template/layout files fixed (covers dynamically generated links for all pages)

### Downloadable files (PDF, TeX, etc.)
- [ ] Link text indicates file type: "CV (PDF)", "Syllabus (PDF)", "TeX source"
- [ ] Or use `aria-label="PDF of [title]"` on the link

### Link text clarity
- [ ] No "click here" or "read more" as sole link text
- [ ] Links distinguishable from surrounding text (underline or other non-color indicator)
- [ ] `aria-label` added when link text alone is ambiguous (e.g., bare numbers like "1664617")

## 4. Images

- [ ] Every `<img>` has an `alt` attribute
- [ ] Decorative images: `alt=""` (empty) or `aria-hidden="true"`
- [ ] Meaningful images: descriptive alt text (200-400 chars for complex visuals)
- [ ] Icon fonts (`<i class="fas fa-*">`) have `aria-hidden="true"`
- [ ] Adjacent text link + image link to same URL are combined into one `<a>`
- [ ] SVG icons have `aria-hidden="true"` when decorative

## 5. Forms & Interactive Controls

- [ ] Every `<input>` has an associated `<label>` or `aria-label`
- [ ] Every `<button>` has visible text or `aria-label`
- [ ] Icon-only buttons have `aria-label` describing the action
- [ ] `<select>` elements have `<label>` or `aria-label`
- [ ] `<canvas>` elements have `role="img"` and `aria-label`
- [ ] Toggle buttons use `aria-pressed` state
- [ ] Search inputs have `aria-label="Search [context]"`

## 6. Color & Contrast

- [ ] Text contrast ratio ≥ 4.5:1 against background (normal text)
- [ ] Large text (18px+ or 14px+ bold) contrast ratio ≥ 3:1
- [ ] Links distinguishable by more than color alone (underline, weight, icon)
- [ ] Focus indicators visible in both light and dark modes
- [ ] Active/selected states meet contrast requirements
- [ ] Dark mode: verify all text/background combinations independently

### CSS patterns used on lpetrov.cc:
```css
/* Skip link */
.skip-link { position: absolute; left: -9999px; z-index: 999; }
.skip-link:focus { left: 50%; transform: translateX(-50%); top: 0; }

/* Focus visibility */
*:focus-visible { outline: 3px solid #E57200; outline-offset: 2px; }

/* Screen reader only */
.sr-only { position: absolute; width: 1px; height: 1px;
  padding: 0; margin: -1px; overflow: hidden;
  clip: rect(0,0,0,0); border: 0; }
```

## 7. Dynamic Content & ARIA

- [ ] Live regions for dynamic updates: `role="status" aria-live="polite"` on status/count elements
- [ ] Search results count announced: `<div id="status" class="sr-only" role="status" aria-live="polite">`
- [ ] Loading/progress states communicated: `aria-live="polite"` on progress indicators
- [ ] `aria-current="page"` on active navigation links
- [ ] `aria-expanded="true/false"` on collapsible toggles
- [ ] `aria-controls` connects toggle to controlled element
- [ ] Cookie/consent banners have `role="region"` and `aria-label="Cookie notice"`

## 8. Keyboard Navigation

- [ ] All interactive elements reachable via Tab key
- [ ] Logical tab order follows visual reading order
- [ ] No keyboard traps (can Tab out of any component)
- [ ] Escape key closes modals/overlays
- [ ] Focus visible on all interactive elements (`:focus-visible` outline)
- [ ] Skip link works and is visible on focus

## 9. Motion & Animation

- [ ] `@media (prefers-reduced-motion: reduce)` disables non-essential animations
- [ ] No auto-playing content that can't be paused
- [ ] CSS transitions respect reduced-motion preference:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 10. Simulation/Interactive Page Specifics

- [ ] Each simulation page has `a11y-description` front matter (rendered as sr-only text)
- [ ] Description is 200-400 chars, concrete (not generic "simulation of X")
- [ ] All `<canvas>` elements: `role="img"` + descriptive `aria-label`
- [ ] All `<svg>` visualizations: `role="img"` + `aria-label`
- [ ] Skip-link past controls to main visualization canvas
- [ ] Slider/range inputs have `aria-label` describing the parameter
- [ ] Status/sample-count displays use `aria-live="polite"`
- [ ] Start/stop/reset buttons have clear `aria-label` if icon-only

## 11. Template Checklist (for Jekyll/static sites)

Fix these once in templates to cover all generated pages:

- [ ] **`_layouts/default.html`**: `<html lang>`, skip-link, `<main>`, landmarks
- [ ] **`_layouts/post.html`**: sr-only on `target="_blank"` arXiv/journal links
- [ ] **`_layouts/sim_page.html`**: sr-only on paper reference links, a11y-description rendering
- [ ] **`_includes/navbar.html`**: `aria-label`, `aria-current`, toggle `aria-expanded`
- [ ] **`_includes/footer.html`**: sr-only on all external links, `aria-hidden` on icons
- [ ] **Research listing template**: sr-only on arXiv, journal-web, PDF links; `aria-label` on PDF/TeX links
- [ ] **Search components**: live region for result counts, `aria-label` on inputs

## 12. Automated Testing

Run these tools to catch remaining issues:

1. **AudioEye / axe DevTools** — browser extension scan
2. **Lighthouse Accessibility audit** — Chrome DevTools → Lighthouse → Accessibility
3. **WAVE** (wave.webaim.org) — visual overlay of issues
4. **Manual keyboard test** — Tab through entire page, verify all controls reachable
5. **Screen reader test** — VoiceOver (macOS: Cmd+F5) to verify announcements

### Common false positives to ignore:
- `aria-label` on non-interactive elements (tables, regions) flagged as "mismatch" — valid if no visible text
- Icon font `<i>` tags flagged as "non-semantic emphasis" — valid with `aria-hidden="true"`

---

## Quick-Fix Priority Order

1. **Skip link + landmarks** (biggest screen reader impact, one-time fix)
2. **Heading hierarchy** (H1→H2→H3, no skipping)
3. **Image alt text** (every `<img>` needs `alt`)
4. **`<b>` → `<strong>`** (site-wide find-replace)
5. **`target="_blank"` sr-only text** (fix templates first, then individual files)
6. **Orphaned `<li>` elements** (wrap in `<ul>` or change to `<div>`/`<span>`)
7. **Color contrast** (check dark mode separately)
8. **Form labels** (`aria-label` on all inputs)
9. **ARIA live regions** (dynamic content announcements)
10. **Keyboard navigation** (manual Tab-through test)

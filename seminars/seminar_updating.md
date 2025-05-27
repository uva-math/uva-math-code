# Seminar Update Instructions for 2025-26 Academic Year

## Overview
The UVA Math website requires annual updates to seminar pages when transitioning to a new academic year. This document provides comprehensive instructions for updating all seminars from 2024-25 to 2025-26.

## Active Seminars to Update

The following seminars need yearly archive updates:

1. **Algebra Seminar** (`algebra`)
2. **Colloquium** (`colloq`)
3. **Harmonic Analysis and PDE Seminar** (`diffeq`)
4. **Galois-Grothendieck Seminar** (`galois`)
5. **Geometry Seminar** (`geometry`)
6. **Graduate Students Seminar** (`gradsem`)
7. **Undergraduate Math Club** (`mathclub`)
8. **Mathematical Physics Seminar** (`mathphys`)
9. **Ramanujan-Serre Seminar (Number Theory)** (`ntsem`)
10. **Probability Seminar** (`probability`)
11. **Operator Theory Seminar** (`sotoa`)
12. **Topology Seminar** (`topology`)

Note: Analysis Commons (`ancommons`) appears to be inactive/discontinued as it only has archives through 2021-22.

## Update Process

### Step 1: Run the Update Script

Execute the provided script from the `/seminars/` directory:
```bash
cd /Users/leo/uva-math-code/seminars
./update_sems_year.zsh
```

This script automatically:
- Creates new `[seminar]25_26.html` files for each seminar
- Copies content from `[seminar]24_25.html` files
- Updates permalinks, dates, and archive links

### Step 2: Manual Updates Required

For each seminar's main page (`[seminar].html`), verify the archives line includes all years. The format should be:

```html
archives='<a href="/seminars/[seminar]/">upcoming</a> | <a href="/seminars/[seminar]/2025-26/">2025-26</a> | <a href="/seminars/[seminar]/2024-25/">2024-25</a> | [previous years...]'
```

Note that there could be line breaks. One has to manually search for all previous years in each seminar archive page.

### Step 3: File Structure for Each Seminar

Each seminar directory should contain:
- `[seminar].html` - Main page showing upcoming talks
- `[seminar]25_26.html` - New archive for 2025-26
- `[seminar]24_25.html` - Archive for 2024-25
- Previous year archives...

## Archive Page Structure

Each new archive page (`[seminar]YY_YY.html`) should have:

```yaml
---
title: [Seminar Name] 2025-26
layout: seminar
permalink: /seminars/[seminar]/2025-26/
events: false
sem_page: true
sem_archive: true
nav_parent: Seminars
---
```

Then include the seminar display logic with date filters:

```liquid
{% include seminar_main_page.html sem_shortname="[seminar]" show_from='1 July 2025' show_to='1 July 2026' %}
```

## Important Notes

1. The script handles most updates automatically, but always verify:
   - Archive links are properly ordered (newest first)
   - Date ranges are correct (July 1, 2025 to July 1, 2026)
   - Permalinks match the expected format

2. Special cases:
   - Some seminars have very old archives (e.g., mathphys goes back to 1999-00)
   - Some seminars have special archive pages (e.g., algebra has "AlgSeminarOld" for 2002-07)

3. After running updates:
   - Test navigation between archive years in _site folder after building jekyll site
   - Verify the "upcoming" link still works correctly
   - Check that the current year (2025-26) appears in archive lists

## Troubleshooting

If archive links don't update properly:
1. Check for line breaks in the archives string
2. Ensure no extra spaces in the sed commands
3. Verify file permissions allow editing

For manual fixes, the archive link pattern is:
```
<a href="/seminars/[seminar]/">upcoming</a> | <a href="/seminars/[seminar]/2025-26/">2025-26</a> | [continue pattern...]
```

## Completion Checklist

- [ ] Run update_sems_year.zsh script
- [ ] Verify all 12 active seminars have 25_26.html files
- [ ] Check archive links updated in all main seminar pages
- [ ] Test navigation on a few seminar pages
- [ ] Commit changes to GitHub
- [ ] Wait ~5 minutes for changes to appear on live site

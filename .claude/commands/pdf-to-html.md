---
description: Convert any PDF document to an accessible HTML version
argument-hint: <path-to-pdf>
model: sonnet
---

Convert the specified PDF document into an accessible standalone HTML version.

**Task:** Create an HTML version of the PDF document: `$ARGUMENTS`

## Instructions:

1. **Locate the PDF**:
   - Search for the PDF file in the repository using the provided path or filename
   - If just a filename is provided, search the entire repository for it
   - Common locations include: `graduate/docs/`, `undergraduate/docs/`, `img/`, etc.

2. **Extract content**:
   - If the user has provided the text content, use that
   - Otherwise, read any existing markdown or text versions of the document in the repository
   - The user may paste the content directly in their message

3. **Create HTML version**: Generate a standalone HTML page with:
   - Jekyll front matter with appropriate layout, title, and permalink
   - Embedded CSS using CSS variables for dark mode support (--text-color, --card-bg, --bg-color)
   - Semantic HTML5 structure with proper headings (h1, h2, h3)
   - ARIA attributes for accessibility (role, aria-label, aria-labelledby)
   - Responsive design that works on mobile and desktop
   - UVA branding colors (orange accent: #e57200)
   - Preserve all content exactly as in the PDF
   - **Use MathML for all mathematical notation** (Greek letters, superscripts, subscripts, fractions, etc.)

4. **Save the file**:
   - Save the HTML file in the same directory as the PDF
   - Use a kebab-case filename (e.g., `algebra-general-exam-syllabus.html`)
   - The permalink should match the directory structure

5. **Update links**: Find and update the relevant include or page file that links to this PDF to add an HTML version link:
   - Search for references to the PDF filename in the repository
   - Add ` &bull; <a href="{{ site.url }}/path/to/html">HTML version</a>` after the PDF link
   - Use "HTML version" not "accessible HTML version"

6. **Verify**: Confirm the file structure matches the site's standards and uses proper Jekyll conventions.

## Example output structure:

```html
---
layout: g_page
title: Document Title
permalink: /graduate/docs/document-name/
nav_parent: Graduate
---

<style>
  .container {
    /* CSS using var(--text-color), var(--card-bg) for dark mode */
  }
</style>

<article class="container" role="main">
  <h1>Document Title</h1>
  <!-- Content here -->
</article>
```

Ask the user if they need to provide the PDF text content first, or if you should search for it in the repository.

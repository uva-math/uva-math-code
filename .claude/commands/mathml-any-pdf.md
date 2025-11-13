---
description: Convert any PDF to accessible HTML with MathML using Mathpix API - comprehensive validation
---

You are going to convert ANY PDF file to accessible HTML with MathML using the Mathpix API. This is a comprehensive, production-grade conversion with extensive automated checks.

## Requirements
- The PDF path will be provided as an argument to this command
- Optionally, the source page path (where link should be added) can be provided
- Use Mathpix API credentials from environment variables (MATHPIX_APP_ID and MATHPIX_API_KEY)
- **This command is CONCURRENT-SAFE**: Multiple instances can run simultaneously
- Generate accessible HTML with:
  - Actual MathML markup (NOT SVG, NOT Unicode characters)
  - Proper ARIA attributes (role="math", aria-label with LaTeX)
  - Proper semantic heading hierarchy (H1 for title, H2 for sections)
  - Table of contents detection and linking
  - Minimal CSS (Jekyll will handle styling)
  - Maximum accessibility (WCAG 2.1 Level AA)

## Workflow

### Step 1: Analyze PDF Structure
**Before uploading**, read the ENTIRE PDF to understand its structure:

```bash
Read <PDF_PATH>
```

Analyze for:
- **Document type**: (exam, lecture notes, paper, book chapter, etc.)
- **Title**: Extract the main title
- **Structure**: Does it have:
  - Table of contents?
  - Numbered sections/chapters?
  - Appendices?
  - Bibliography?
  - Figures/diagrams?
  - Tables?
- **Mathematics content**: Heavy math, light math, or no math?
- **Page count**: (affects processing time)
- **Special features**: Colored text, multi-column layout, footnotes, etc.

**Document this analysis** - it will guide the conversion process.

### Step 2: Upload PDF to Mathpix
Use the Mathpix v3/pdf API endpoint to upload the PDF (SINGLE LINE - no backslashes):
```bash
curl -X POST "https://api.mathpix.com/v3/pdf" -H "app_id: $MATHPIX_APP_ID" -H "app_key: $MATHPIX_API_KEY" -F "file=@<PDF_PATH>" -F 'options_json={"conversion_formats": {"html.zip": true, "tex.zip": true}}'
```

Extract the `pdf_id` from the response.

### Step 3: Check conversion status
Poll the status endpoint until conversion is complete (SINGLE LINE - no backslashes):
```bash
curl -X GET "https://api.mathpix.com/v3/pdf/<PDF_ID>" -H "app_id: $MATHPIX_APP_ID" -H "app_key: $MATHPIX_API_KEY"
```

Wait until `"status":"completed"`.

**Check for errors** in the response - document any warnings.

### Step 4: Download and Extract TeX Format
Download the tex.zip format (NOT .html, as it uses SVG) - SINGLE LINE for curl, then unzip:
```bash
curl -X GET "https://api.mathpix.com/v3/pdf/<PDF_ID>.tex.zip" -H "app_id: $MATHPIX_APP_ID" -H "app_key: $MATHPIX_API_KEY" -o /tmp/<PDF_ID>.tex.zip
```

Then extract:
```bash
cd /tmp && unzip -o <PDF_ID>.tex.zip
```

**Verify extraction**:
```bash
ls -la /tmp/<PDF_ID>/
```

The extracted .tex file will be in a subdirectory named with the PDF_ID.

**Read the TeX source** to verify quality:
```bash
Read /tmp/<PDF_ID>/<PDF_ID>.tex
```

Check for:
- Proper structure
- Section headings
- Math formulas look correct
- Any obvious OCR errors

### Step 5: Convert to HTML with MathML using Pandoc
```bash
pandoc /tmp/<PDF_ID>/<PDF_ID>.tex -f latex -t html --mathml --standalone -o /tmp/<PDF_ID>_mathml.html
```

**Check for Pandoc errors** - document any warnings.

### Step 6: Post-process for accessibility and formatting
Use the Python script `scripts/fix_mathml.py` to apply all fixes:

```bash
python3 scripts/fix_mathml.py /tmp/<PDF_ID>_mathml.html /tmp/<PDF_ID>_fixed.html
```

This script handles:
1. Replace all Unicode mathematical characters with HTML/MathML entities
2. Fix heading hierarchy (first H1 stays as title, subsequent H1s become H2)
3. Add ARIA attributes to all math elements
4. Add lang="en" attribute
5. Extract title and set descriptive page title
6. Add breadcrumb navigation
7. Add back button navigation
8. Wrap main content in `<main>` landmark element

**Verify the script ran successfully** - check exit code and output.

### Step 7: Handle Images (Diagrams, Figures, Tables)
**IMPORTANT**: Check for extracted images and handle them properly.

1. **Check for extracted images**:
   ```bash
   ls -la /tmp/<PDF_ID>/images/
   ```

2. **If images exist**:
   - Determine output directory based on PDF path
   - Create images directory:
     ```bash
     mkdir -p <OUTPUT_DIR>/images
     ```

   - Copy ALL image files:
     ```bash
     cp /tmp/<PDF_ID>/images/*.jpg <OUTPUT_DIR>/images/ 2>/dev/null || cp /tmp/<PDF_ID>/images/*.png <OUTPUT_DIR>/images/ 2>/dev/null || true
     ```

   - **Update image paths in HTML** using Edit tool:
     - Find all `<img src="...">` tags
     - Change to `<img src="images/FILENAME.jpg"`
     - Add descriptive alt text
     - Add responsive styling:
       ```html
       <img src="images/FILENAME.jpg" alt="Descriptive alt text here" style="max-width: 100%; height: auto; display: block; margin: 1em auto;" />
       ```

### Step 8: Detect and Structure Table of Contents
**CRITICAL**: If the document has a table of contents, make it navigable.

1. **Read the processed HTML** to check for TOC:
   ```bash
   Read /tmp/<PDF_ID>_fixed.html
   ```

2. **Look for TOC patterns**:
   - "Contents", "Table of Contents" heading
   - List of section titles with page numbers
   - Links to sections

3. **If TOC exists**:
   - Convert to proper HTML navigation structure:
     ```html
     <nav aria-label="Table of Contents" class="toc">
       <h2>Contents</h2>
       <ol>
         <li><a href="#section-1">Section Title</a></li>
         <li><a href="#section-2">Section Title</a></li>
       </ol>
     </nav>
     ```

   - Ensure all TOC links point to correct section IDs
   - Remove page numbers (they don't apply to HTML)
   - Add skip-to-content link at top

4. **Validate TOC**:
   - All links resolve to actual sections
   - Proper nesting for subsections
   - Keyboard navigable
   - Screen reader accessible

### Step 9: Add Proper Section Headings
**CRITICAL**: Ensure proper semantic heading structure.

1. **Read the processed HTML** at `/tmp/<PDF_ID>_fixed.html`

2. **Identify document structure** based on Step 1 analysis:
   - For exams: H2 for each problem
   - For papers: H2 for sections, H3 for subsections
   - For books: H2 for chapters, H3 for sections
   - For lecture notes: H2 for lectures/topics

3. **Add appropriate headings**:
   ```html
   <h2 class="unnumbered" id="section-identifier">Section Title</h2>
   ```

4. **Verify heading hierarchy**:
   - Exactly ONE H1 (document title)
   - H2 for major sections
   - H3 for subsections (if applicable)
   - No skipped levels
   - Each heading has unique ID

### Step 10: Minimal CSS Cleanup
The HTML should use **minimal inline CSS** since Jekyll will handle styling.

**Remove or minimize**:
- Complex Pandoc CSS
- Fixed widths
- Specific fonts
- Heavy styling

**Keep**:
- Responsive image styling
- Basic spacing
- Accessibility-critical styles (focus indicators, skip links)

Use Edit tool to:
1. Simplify `<style>` section
2. Remove Pandoc-specific classes
3. Ensure mobile-responsive viewport

### Step 11: Determine Output Location and Breadcrumb
Based on the PDF path, determine where the HTML should be saved and the appropriate breadcrumb navigation.

**Pattern matching**:
- If path contains `/graduate/exams/algebra/` → Same directory, breadcrumb: Home / Graduate / General Exams / [Title]
- If path contains `/graduate/exams/analysis/` → Same directory, breadcrumb: Home / Graduate / General Exams / [Title]
- If path contains `/graduate/exams/topology/` → Same directory, breadcrumb: Home / Graduate / General Exams / [Title]
- If path contains `/graduate/docs/` → Same directory, breadcrumb: Home / Graduate / [Title]
- If path contains `/IMS/` → Same directory, breadcrumb: Home / IMS / [Title]
- If path contains `/RTG_geomtop/` → Same directory, breadcrumb: Home / RTG / [Title]
- If path contains `/seminars/` → Same directory, breadcrumb: Home / Seminars / [Title]
- If path contains `/undergraduate/` → Same directory, breadcrumb: Home / Undergraduate / [Title]
- If in `_posts/` → Keep markdown, don't convert
- Otherwise → Same directory as PDF, breadcrumb: Home / [Title]

**Output filename**: Same name as PDF but with `.html` extension

**Breadcrumb structure**:
```html
<nav aria-label="Breadcrumb" style="margin-bottom: 1em;">
  <ol style="list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; align-items: center; gap: 0.5em;">
    <li><a href="/">Home</a></li>
    <li aria-hidden="true" style="color: #999;">/</li>
    <li><a href="/SECTION/">Section Name</a></li>
    <li aria-hidden="true" style="color: #999;">/</li>
    <li aria-current="page" style="color: #666;">[Document Title]</li>
  </ol>
</nav>
```

**Back button** (adjust based on context):
- For exams: Back to General Exams → `/graduate/generals/`
- For IMS: Back to IMS → `/IMS/`
- For RTG: Back to RTG → `/RTG_geomtop/`
- For seminars: Back to Seminars → `/seminars/`
- For undergraduate: Back to Undergraduate → `/undergraduate/`

### Step 12: Add Jekyll Front Matter (if applicable)
**Only if** the HTML will be used as a Jekyll page/post:

Determine if Jekyll front matter is needed:
- In `_posts/` → YES (but shouldn't convert PDFs here)
- Direct content pages → NO (linked from other pages)
- Standalone documents → NO

For most PDFs, **NO Jekyll front matter needed** - they're linked from existing pages.

### Step 13: Save to final location
Save the processed HTML file (from `/tmp/<PDF_ID>_fixed.html`) to the determined output location.

```bash
cp /tmp/<PDF_ID>_fixed.html <OUTPUT_PATH>
```

**Verify the file was saved correctly**:
```bash
ls -lh <OUTPUT_PATH>
```

### Step 14: Update Source Page Link
If a source page path was provided, update the link there. Otherwise, automatically find the source page.

**Automatically find source page** (if not provided):
```bash
# Search for the PDF filename in markdown files
grep -r "$(basename <PDF_PATH>)" /Users/leo/uva-math-code --include="*.md" --include="*.html"
```

This will show which page(s) link to the PDF.

**Common source pages**:
- `graduate/general_exams.md` → Exam links
- `IMS/lectures.html` → IMS lecture notes
- `RTG_geomtop/reading.html` → RTG reading materials
- `seminars/*.md` → Seminar notes

**Link format** (HTML primary, PDF secondary):
```markdown
# Before (PDF only):
[Link Text]({{site.url}}/path/to/file.pdf)

# After (HTML primary, PDF secondary):
[Link Text]({{site.url}}/path/to/file.html) &bull; <a href="{{site.url}}/path/to/file.pdf" aria-label="PDF version for printing">PDF</a>
```

**Examples**:

**Exam link**:
```markdown
# Before:
- [01/2025, complex]({{site.url}}/graduate/exams/analysis/2025Jan_complex.pdf)

# After:
- [01/2025, complex]({{site.url}}/graduate/exams/analysis/2025Jan_complex.html) &bull; <a href="{{site.url}}/graduate/exams/analysis/2025Jan_complex.pdf" aria-label="PDF version for printing">PDF</a>
```

**General document link**:
```markdown
# Before:
[Syllabus for Analysis General Exam]({{site.url}}/graduate/docs/Syllabus for Analysis General Exam 2.pdf)

# After:
[Syllabus for Analysis General Exam]({{site.url}}/graduate/docs/Syllabus for Analysis General Exam 2.html) &bull; <a href="{{site.url}}/graduate/docs/Syllabus for Analysis General Exam 2.pdf" aria-label="PDF version for printing">PDF</a>
```

**If no source page found**:
- Document this in the quality report
- The HTML is still accessible by direct URL
- User may manually add link later

### Step 15: COMPREHENSIVE VALIDATION - Read FULL PDF and HTML
**⚠️ MANDATORY**: You MUST read the COMPLETE PDF and COMPLETE HTML for comparison.

```bash
Read <PDF_PATH>
Read <HTML_PATH>
```

**Compare side-by-side**:
- [ ] All content present in HTML
- [ ] All formulas correctly converted
- [ ] All figures/diagrams included
- [ ] All tables properly formatted
- [ ] Heading structure matches document structure
- [ ] TOC (if present) is navigable
- [ ] No missing sections
- [ ] No garbled text
- [ ] No broken math formulas

**Document any discrepancies** and fix them immediately.

### Step 16: AUTOMATED WCAG 2.1 LEVEL AA COMPLIANCE AUDIT
**⚠️ CRITICAL**: Comprehensive accessibility audit with automated checks.

#### A. Document Structure (WCAG 1.3.1, 2.4.1)
```bash
# Check DOCTYPE
grep -c '<!DOCTYPE html>' <HTML_PATH>  # Must be 1

# Check lang attribute
grep -c 'lang="en"' <HTML_PATH>  # Must be >= 1

# Check charset
grep -c 'charset.*utf-8' <HTML_PATH>  # Must be >= 1

# Check viewport
grep -c 'viewport' <HTML_PATH>  # Must be >= 1
```

**Checklist**:
- [ ] Valid HTML5 DOCTYPE
- [ ] `lang="en"` on `<html>` element
- [ ] UTF-8 encoding
- [ ] Viewport meta tag

#### B. Page Title (WCAG 2.4.2)
```bash
# Extract title
grep '<title>' <HTML_PATH>
```

**Checklist**:
- [ ] Descriptive `<title>` tag present
- [ ] Title format: "[Document Title] - UVA Mathematics"
- [ ] Title accurately describes content

#### C. Semantic Heading Hierarchy (WCAG 1.3.1, 2.4.6) **[CRITICAL]**
```bash
# Count H1 tags (must be exactly 1)
grep -c '<h1' <HTML_PATH>

# Count H2 tags (should match major sections)
grep -c '<h2' <HTML_PATH>

# Check for H3 tags (if document has subsections)
grep -c '<h3' <HTML_PATH>

# Verify no H4+ without proper hierarchy
grep -c '<h4' <HTML_PATH>
```

**Checklist**:
- [ ] Exactly ONE H1 heading (document title)
- [ ] H2 headings for all major sections
- [ ] H3 for subsections (if applicable)
- [ ] No skipped heading levels
- [ ] Each heading has unique `id` attribute
- [ ] Heading count matches document structure

#### D. Landmark Elements (WCAG 1.3.1, 2.4.1)
```bash
# Check for landmarks
grep -c 'aria-label="Breadcrumb"' <HTML_PATH>  # Must be 1
grep -c 'aria-label="Page navigation"' <HTML_PATH>  # Must be 1
grep -c '<main>' <HTML_PATH>  # Must be 1
grep -c '</main>' <HTML_PATH>  # Must be 1
```

**Checklist**:
- [ ] Breadcrumb `<nav>` with `aria-label="Breadcrumb"`
- [ ] Page navigation `<nav>` with `aria-label="Page navigation"`
- [ ] Main content wrapped in `<main>` element
- [ ] Proper opening/closing tags for all landmarks
- [ ] TOC `<nav>` with `aria-label="Table of Contents"` (if applicable)

#### E. Navigation Accessibility (WCAG 2.4.4, 2.4.8, 4.1.2)
```bash
# Check breadcrumb structure
grep -A5 'aria-label="Breadcrumb"' <HTML_PATH>

# Check for aria-current
grep -c 'aria-current="page"' <HTML_PATH>  # Must be 1
```

**Checklist**:
- [ ] Breadcrumb uses ordered list (`<ol>`)
- [ ] Breadcrumb separators have `aria-hidden="true"`
- [ ] Current page marked with `aria-current="page"`
- [ ] Back button is semantic `<a>` with descriptive text
- [ ] All links have clear, descriptive text
- [ ] Skip-to-content link (if TOC present)

#### F. MathML Accessibility (WCAG 1.3.1, 1.4.5, 4.1.2) **[CRITICAL]**
```bash
# Count math elements
grep -c '<math' <HTML_PATH>

# Check role="math" (count should match <math> count)
grep -c 'role="math"' <HTML_PATH>

# Check aria-label presence
grep -c 'aria-label=' <HTML_PATH>

# Check MathML namespace
grep -c 'xmlns="http://www.w3.org/1998/Math/MathML"' <HTML_PATH>

# Sample 5 random math elements for detailed inspection
grep -A10 '<math' <HTML_PATH> | head -60
```

**Checklist**:
- [ ] All `<math>` elements have `role="math"`
- [ ] All `<math>` elements have `aria-label` with LaTeX
- [ ] All use MathML namespace
- [ ] All use `<semantics>` wrapper
- [ ] All have `<annotation encoding="application/x-tex">`
- [ ] Math element count matches expected formula count

#### G. Unicode Character Verification **[LAWSUIT RISK - CRITICAL]**
**NO Unicode mathematical characters allowed. All MUST be HTML entities.**

**This check is AUTOMATED by the verify_wcag.py script in Step 17.**

The script automatically detects Unicode violations in range U+1D400-U+1D7FF (mathematical alphanumeric symbols, including blackboard bold).

**Common violations and fixes**:
- 𝔻 → `&Dopf;`, ℝ → `&Ropf;`, ℂ → `&Copf;`, ℕ → `&Nopf;`, ℤ → `&Zopf;`, ℚ → `&Qopf;`
- 𝔸 → `&Aopf;`, 𝔹 → `&Bopf;`, 𝔼 → `&Eopf;`, 𝔽 → `&Fopf;`, 𝕋 → `&Topf;`
- → → `&rarr;`, ← → `&larr;`, ⇒ → `&rArr;`, ⇐ → `&lArr;`, ↦ → `&map;`
- ∈ → `&isin;`, ∉ → `&notin;`, ∞ → `&infin;`, ≤ → `&le;`, ≥ → `&ge;`
- α → `&alpha;`, β → `&beta;`, π → `&pi;`, θ → `&theta;`, φ → `&phi;`

**If violations found by the script**:
1. Read the HTML file to locate violations
2. Use Edit tool to replace each Unicode character with its HTML entity
3. Re-run verify_wcag.py until it passes

**Checklist** (verified by automated script):
- [ ] NO Unicode mathematical alphanumeric (U+1D400-U+1D7FF)
- [ ] All blackboard bold use HTML entities (&Dopf;, &Ropf;, etc.)
- [ ] All special characters properly encoded

#### H. Table of Contents Validation (if applicable)
```bash
# Check for TOC
grep -i 'table of contents\|aria-label="Table of Contents"' <HTML_PATH>

# If TOC exists, validate links
grep -oP 'href="#[^"]*"' <HTML_PATH> | sort | uniq
```

**Checklist (if TOC present)**:
- [ ] TOC wrapped in `<nav aria-label="Table of Contents">`
- [ ] Uses ordered or unordered list
- [ ] All links are valid anchor references
- [ ] All anchor targets exist in document
- [ ] Page numbers removed
- [ ] Proper nesting for subsections
- [ ] Skip-to-content link at top

#### I. Image Accessibility (if applicable)
```bash
# Check for images
grep -c '<img' <HTML_PATH>

# Check all images have alt text
grep '<img' <HTML_PATH> | grep -v 'alt=' && echo "⚠️ Missing alt text" || echo "✓ All images have alt"

# Sample image tags
grep '<img' <HTML_PATH> | head -5
```

**Checklist (if images present)**:
- [ ] All `<img>` tags have `alt` attribute
- [ ] Alt text is descriptive (not "image" or filename)
- [ ] Images have proper paths (images/filename.jpg)
- [ ] Images have responsive styling
- [ ] Decorative images have `alt=""`
- [ ] Complex diagrams have extended descriptions

#### J. Table Accessibility (if applicable)
```bash
# Check for tables
grep -c '<table' <HTML_PATH>

# Check for table headers
grep -c '<th' <HTML_PATH>
```

**Checklist (if tables present)**:
- [ ] All tables have `<caption>` or heading
- [ ] Table headers use `<th>` elements
- [ ] Headers have `scope` attribute
- [ ] Complex tables use `headers` attribute
- [ ] Tables are responsive (scrollable on mobile)

### Step 17: Run Automated WCAG Verification Script
```bash
python3 scripts/verify_wcag.py <HTML_PATH>
```

**Expected output**:
```
✅ <HTML_PATH>: PASS
```

**If failures reported**:
1. STOP immediately
2. Fix all violations
3. Re-run validation
4. Only proceed when you see `✅ PASS`

### Step 18: Final Quality Report
After all validation passes, provide a comprehensive quality report:

```markdown
## ✅ Conversion Complete: [Document Title]

**PDF**: `<PDF_PATH>`
**HTML**: `<HTML_PATH>`
**Status**: PRODUCTION READY ✅

---

### Document Analysis
- **Type**: [exam/paper/notes/etc.]
- **Pages**: [N]
- **Math intensity**: [Heavy/Medium/Light/None]
- **Special features**: [TOC/Figures/Tables/etc.]
- **Conversion quality**: [Excellent/Good/Fair]

---

### WCAG 2.1 Level AA Compliance

#### ✅ All Checks Passed

**Document Structure**:
- ✅ Valid HTML5 DOCTYPE
- ✅ lang="en" attribute
- ✅ UTF-8 encoding
- ✅ Responsive viewport

**Page Title**:
- ✅ Descriptive title: "[Title] - UVA Mathematics"

**Heading Hierarchy**:
- ✅ 1 H1 heading (document title)
- ✅ [N] H2 headings (major sections)
- ✅ [N] H3 headings (subsections, if applicable)
- ✅ No skipped levels
- ✅ All headings have unique IDs

**Landmarks**:
- ✅ Breadcrumb navigation
- ✅ Page navigation (back button)
- ✅ Main landmark element
- ✅ [TOC navigation, if applicable]

**Navigation**:
- ✅ Breadcrumb uses ordered list
- ✅ aria-current="page" present
- ✅ All links descriptive
- ✅ Keyboard accessible

**MathML**:
- ✅ [N] math elements with role="math"
- ✅ All have aria-label with LaTeX
- ✅ Proper MathML namespace
- ✅ Semantic markup with <semantics>

**Unicode Verification**:
- ✅ No Unicode operators
- ✅ No blackboard bold violations
- ✅ No Unicode Greek letters
- ✅ No Unicode arrows/symbols
- ✅ All use HTML entities

**Images** [if applicable]:
- ✅ [N] images with descriptive alt text
- ✅ Proper paths and responsive styling

**Tables** [if applicable]:
- ✅ [N] tables with headers and captions
- ✅ Proper scope attributes

**Table of Contents** [if applicable]:
- ✅ Navigable TOC structure
- ✅ All links resolve correctly
- ✅ Proper ARIA labels

---

### Content Verification

**PDF vs HTML Comparison**:
- ✅ All text content present
- ✅ All formulas correctly converted
- ✅ All figures/diagrams included
- ✅ All tables properly formatted
- ✅ Heading structure matches
- ✅ No missing sections
- ✅ No OCR errors detected

---

### Legal Compliance Summary

✅ **PRODUCTION READY**
- All WCAG 2.1 Level AA requirements met
- ADA Title II & III compliant
- Section 508 compliant
- Lawsuit risk: **MINIMAL**
- File is legally defensible

---

### Files Updated
- ✅ HTML saved: `<HTML_PATH>`
- ✅ [Images copied: N files, if applicable]
- ✅ Source page updated: `<SOURCE_PAGE>`

**The HTML is ready for public deployment.**
```

---

## Important Notes

### Concurrent Execution
- This command uses unique PDF_ID-based filenames in `/tmp/`
- Multiple instances can run simultaneously without conflicts
- Source page editing may fail if concurrent - retry after re-reading

### Minimal CSS Philosophy
- The HTML should have minimal inline CSS
- Jekyll website handles all styling
- Only keep accessibility-critical and responsive styles
- Remove Pandoc-specific CSS classes

### Table of Contents Priority
- If TOC detected, make it fully navigable
- Remove page numbers (not applicable to HTML)
- Add skip-to-content link
- Ensure all TOC links resolve

### Full Document Validation
- MUST read COMPLETE PDF (all pages)
- MUST read COMPLETE HTML (all content)
- Side-by-side comparison required
- Document any discrepancies

### Automated Checks
- More checks than exam command
- Automated grep-based validation
- Python verification script
- Comprehensive checklist

---

## Success Criteria

The conversion is complete when:

✓ Full PDF read and analyzed
✓ Full HTML read and verified
✓ All WCAG 2.1 Level AA checks pass
✓ No Unicode mathematical characters
✓ Proper heading hierarchy
✓ TOC navigable (if present)
✓ All images accessible (if present)
✓ All tables accessible (if present)
✓ MathML properly labeled
✓ Automated verification passes
✓ Source page link updated
✓ Quality report provided
✓ **PRODUCTION READY status confirmed**

**If any criterion fails, fix immediately before declaring complete.**

---

## Usage Examples

### Example 1: Convert a general exam
```
/mathml-any-pdf @graduate/exams/topology/2023-08.pdf
```

**Expected outcome**:
- HTML saved to: `graduate/exams/topology/2023-08.html`
- Breadcrumb: Home / Graduate / General Exams / TOPOLOGY GENERAL EXAM AUGUST 2023
- Back button: "Back to General Exams" → `/graduate/generals/`
- Source page: `graduate/general_exams.md` (automatically detected)
- Link format: `[08/2023]({{site.url}}/graduate/exams/topology/2023-08.html) &bull; <a href="...">PDF</a>`

### Example 2: Convert a graduate program document
```
/mathml-any-pdf @graduate/docs/Syllabus for Topology General Exam 3.pdf
```

**Expected outcome**:
- HTML saved to: `graduate/docs/Syllabus for Topology General Exam 3.html`
- Breadcrumb: Home / Graduate / SYLLABUS FOR TOPOLOGY GENERAL EXAM
- Back button: "Back to Graduate" → `/graduate/`
- Source page: Search automatically with grep
- Title should be descriptive: "Syllabus for Topology General Exam - UVA Mathematics"

### Example 3: Convert IMS lecture notes
```
/mathml-any-pdf @IMS/files/LectureNotes_Spring2024.pdf
```

**Expected outcome**:
- HTML saved to: `IMS/files/LectureNotes_Spring2024.html`
- Breadcrumb: Home / IMS / [Document Title from PDF]
- Back button: "Back to IMS" → `/IMS/`
- Source page: Check `IMS/lectures.html` or relevant workshop page

### Example 4: Convert RTG reading materials
```
/mathml-any-pdf @RTG_geomtop/workshop_fall_2023/notes.pdf
```

**Expected outcome**:
- HTML saved to: `RTG_geomtop/workshop_fall_2023/notes.html`
- Breadcrumb: Home / RTG / [Document Title from PDF]
- Back button: "Back to RTG" → `/RTG_geomtop/`
- Source page: Check workshop page or reading list

### Example 5: Document with table of contents
```
/mathml-any-pdf @undergraduate/docs/UndergraduateHandbook.pdf
```

**Special handling**:
- Detect and structure table of contents
- Create navigable TOC with anchor links
- Remove page numbers from TOC
- Add skip-to-content link at top
- Each section gets proper heading with ID
- All TOC links validated

### Example 6: Document with complex diagrams
```
/mathml-any-pdf @graduate/docs/CommutativeDiagramsNotes.pdf
```

**Special handling**:
- Images extracted to `graduate/docs/images/`
- Each image gets descriptive alt text
- Images have responsive styling
- Complex diagrams may need extended descriptions

---

## Command Arguments

**Basic usage** (PDF path only):
```
/mathml-any-pdf @path/to/file.pdf
```

**With source page** (if known):
```
/mathml-any-pdf @path/to/file.pdf @graduate/general_exams.md
```

The command will:
1. Analyze PDF structure
2. Convert to accessible HTML with MathML
3. Handle images, TOC, tables appropriately
4. Determine breadcrumb based on path
5. Find or update source page link
6. Run comprehensive WCAG validation
7. Read FULL PDF and HTML for comparison
8. Provide detailed quality report

---

## Differences from /mathml-general-exam

| Feature | /mathml-general-exam | /mathml-any-pdf |
|---------|---------------------|-----------------|
| **Scope** | Exams only | Any PDF document |
| **TOC detection** | No | Yes, with navigation |
| **Breadcrumb** | Fixed (General Exams) | Dynamic based on path |
| **Back button** | Fixed (General Exams) | Dynamic based on path |
| **Section headings** | H2 for problems | H2/H3 based on structure |
| **Source page** | Always `general_exams.md` | Auto-detect with grep |
| **Full PDF read** | Sample only | FULL document required |
| **Full HTML read** | Sample only | FULL document required |
| **Validation** | Standard checklist | Enhanced with grep checks |
| **Examples** | No | Multiple usage examples |
| **Image handling** | Basic | Enhanced with descriptions |
| **Table handling** | Basic | Enhanced with headers/scope |

---

## Success Indicators

When complete, you should see:

```markdown
## ✅ Conversion Complete: [Document Title]

**PDF**: `/Users/leo/uva-math-code/path/to/file.pdf`
**HTML**: `/Users/leo/uva-math-code/path/to/file.html`
**Status**: PRODUCTION READY ✅

[Comprehensive quality report with all checks passed]
```

If you see this, the conversion is complete and the HTML is ready for deployment.

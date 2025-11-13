---
description: OCR a general exam PDF to accessible HTML with MathML using Mathpix API
---

You are going to OCR a general exam PDF file to accessible HTML with MathML using the Mathpix API. Follow these steps precisely:

## Requirements
- The PDF path will be provided as an argument to this command
- Use Mathpix API credentials from environment variables (MATHPIX_APP_ID and MATHPIX_API_KEY)
- **This command is CONCURRENT-SAFE**: Multiple instances can run simultaneously without conflicts
  - All files use unique PDF_ID-based names in `/tmp/` (e.g., `/tmp/<PDF_ID>_fixed.html`)
  - Each instance processes its own PDF independently
  - Only Step 9 (editing `general_exams.md`) requires retry logic if running concurrently
- Generate accessible HTML with:
  - Actual MathML markup (NOT SVG, NOT Unicode characters)
  - Proper ARIA attributes (role="math", aria-label with LaTeX)
  - Proper semantic heading hierarchy (H1 for title, H2 for sections/problems)

## Workflow

### Step 1: Upload PDF to Mathpix
Use the Mathpix v3/pdf API endpoint to upload the PDF (SINGLE LINE - no backslashes):
```bash
curl -X POST "https://api.mathpix.com/v3/pdf" -H "app_id: $MATHPIX_APP_ID" -H "app_key: $MATHPIX_API_KEY" -F "file=@<PDF_PATH>" -F 'options_json={"conversion_formats": {"html.zip": true, "tex.zip": true}}'
```

Extract the `pdf_id` from the response.

### Step 2: Check conversion status
Poll the status endpoint until conversion is complete (SINGLE LINE - no backslashes):
```bash
curl -X GET "https://api.mathpix.com/v3/pdf/<PDF_ID>" -H "app_id: $MATHPIX_APP_ID" -H "app_key: $MATHPIX_API_KEY"
```

Wait until `"status":"completed"`.

### Step 3: Download and Extract TeX Format
Download the tex.zip format (NOT .html, as it uses SVG) - SINGLE LINE for curl, then unzip:
```bash
curl -X GET "https://api.mathpix.com/v3/pdf/<PDF_ID>.tex.zip" -H "app_id: $MATHPIX_APP_ID" -H "app_key: $MATHPIX_API_KEY" -o /tmp/<PDF_ID>.tex.zip
```

Then extract:
```bash
cd /tmp && unzip -o <PDF_ID>.tex.zip
```

The extracted .tex file will be in a subdirectory named with the PDF_ID.

### Step 4: Convert to HTML with MathML using Pandoc
```bash
pandoc /tmp/<PDF_ID>/<PDF_ID>.tex -f latex -t html --mathml --standalone -o /tmp/<PDF_ID>_mathml.html
```

### Step 5: Post-process for accessibility and formatting
Use the Python script `scripts/fix_mathml.py` to apply all fixes in one step:

```bash
python3 scripts/fix_mathml.py /tmp/<PDF_ID>_mathml.html /tmp/<PDF_ID>_fixed.html
```

This script does everything:
1. Replace all Unicode mathematical characters with HTML/MathML entities (&rarr;, &infin;, &Copf;, &epsilon;, etc.)
2. Fix heading hierarchy (first H1 stays as title, subsequent H1s become H2)
3. Add ARIA attributes to all math elements (role="math", aria-label with LaTeX source)
4. Add lang="en" attribute to the <html> element
5. Extract title from H1 and set descriptive page title (e.g., "REAL ANALYSIS GENERAL EXAM FALL 2022 - UVA Mathematics")
6. Add breadcrumb navigation at the top of the page
7. Add a back button navigation below the breadcrumb
8. Wrap main content in <main> landmark element
9. Add proper spacing between main problems:
   - Vertical spacing (double line breaks) between numbered problems
   - CSS class for consistent problem spacing

**Breadcrumb navigation** should:
- Have aria-label="Breadcrumb"
- Use ordered list with no bullets
- Include: Home / Graduate / General Exams / [Current Page Title]
- Mark current page with aria-current="page"
- Style separators with aria-hidden="true"

**Back button** should:
- Link to `/graduate/generals/`
- Have aria-label="Page navigation"
- Be styled as a button
- Include a left arrow (&larr;) and text "Back to General Exams"

**Main landmark** should:
- Wrap all content from H1 to the end
- Start with `<main>` before the H1
- Close with `</main>` before `</body>`

Use this entity mapping:
- Arrows: → (&rarr;), ← (&larr;), ↔ (&harr;), ⇒ (&rArr;), ⇐ (&lArr;), ⇔ (&hArr;), ↦ (&map;)
- Set theory: ∈ (&isin;), ∉ (&notin;), ∋ (&ni;), ⊂ (&sub;), ⊃ (&sup;), ⊆ (&sube;), ⊇ (&supe;), ∪ (&cup;), ∩ (&cap;), ∖ (&setminus;), ∅ (&empty;)
- Relations: ≤ (&le;), ≥ (&ge;), ≠ (&ne;), ≈ (&approx;), ≡ (&equiv;), ⟂ (&perp;), ∥ (&parallel;)
- Calculus: ∂ (&part;), ∫ (&int;), ∮ (&conint;), ∑ (&sum;), ∏ (&prod;), ∇ (&nabla;), √ (&radic;)
- Logic: ∀ (&forall;), ∃ (&exist;), ¬ (&not;), ∧ (&and;), ∨ (&or;)
- Number sets: ℝ (&Ropf;), ℂ (&Copf;), ℕ (&Nopf;), ℤ (&Zopf;), ℚ (&Qopf;), **𝔻 (&Dopf;)**, 𝔸 (&Aopf;), 𝔹 (&Bopf;), 𝔼 (&Eopf;), 𝔽 (&Fopf;), 𝔾 (&Gopf;), ℍ (&Hopf;), 𝕀 (&Iopf;), 𝕁 (&Jopf;), 𝕂 (&Kopf;), 𝕃 (&Lopf;), 𝕄 (&Mopf;), 𝕆 (&Oopf;), ℙ (&Popf;), 𝕊 (&Sopf;), 𝕋 (&Topf;), 𝕌 (&Uopf;), 𝕍 (&Vopf;), 𝕎 (&Wopf;), 𝕏 (&Xopf;), 𝕐 (&Yopf;)
- Greek letters: α (&alpha;), β (&beta;), γ (&gamma;), δ (&delta;), ε (&epsilon;), η (&eta;), θ (&theta;), λ (&lambda;), μ (&mu;), ν (&nu;), π (&pi;), σ (&sigma;), τ (&tau;), φ (&phi;), ψ (&psi;), χ (&chi;), ω (&omega;), Γ (&Gamma;), Δ (&Delta;), Θ (&Theta;), Λ (&Lambda;), Σ (&Sigma;), Φ (&Phi;), Ψ (&Psi;), Ω (&Omega;)
- Other: ∞ (&infin;), × (&times;), ⋅ (&sdot;), ± (&plusmn;), ∠ (&ang;), ⊕ (&oplus;), ⊗ (&otimes;)

**CRITICAL**: Blackboard bold letters (especially **𝔻**) frequently appear in exams and MUST be converted to HTML entities. This is a common source of accessibility violations.

### Step 6: Handle Images (Diagrams, Figures)
**IMPORTANT**: Many exams contain diagrams (commutative diagrams, geometric figures, knot diagrams, etc.) that are extracted by Mathpix.

1. **Check for extracted images**:
   ```bash
   ls -la /tmp/<PDF_ID>/images/
   ```

2. **If images exist**:
   - Create the images directory if it doesn't exist:
     ```bash
     mkdir -p <EXAM_DIR>/images
     ```

   - Copy ALL image files to the exam images directory:
     ```bash
     cp /tmp/<PDF_ID>/images/*.jpg <EXAM_DIR>/images/
     ```

   - **Update ALL image paths in the HTML**:
     - Find all `<img src="...">` tags in the HTML
     - Change from `<img src="FILENAME"` to `<img src="images/FILENAME.jpg"`
     - Add proper alt text describing what the diagram shows
     - Add styling for responsive images:
       ```html
       <img src="images/FILENAME.jpg" alt="Descriptive alt text here" style="max-width: 100%; height: auto; display: block; margin: 1em auto;" />
       ```

3. **Common exam diagrams to look for**:
   - Commutative diagrams (arrows between mathematical objects)
   - Pushout/pullback squares
   - Geometric figures (M\u00f6bius bands, knots, surfaces)
   - Graphs and plots
   - Function diagrams

4. **Alt text guidelines**:
   - Be descriptive but concise
   - Examples:
     - "Commutative diagram showing maps between groups A1, A2, B1, B2, and C"
     - "Trefoil knot diagram"
     - "Möbius band diagram showing the curve γ as its boundary"
     - "Pushout diagram showing the construction of Xf"

**Example transformation:**
```html
<!-- Before: Broken image path -->
<img src="2025_11_13_abc123-1" alt="image" />

<!-- After: Fixed path with descriptive alt text -->
<img src="images/2025_11_13_abc123-1.jpg" alt="Commutative diagram showing the exact sequence" style="max-width: 100%; height: auto; display: block; margin: 1em auto;" />
```

### Step 7: Add H2 Problem Headings
**CRITICAL**: After handling images, you MUST manually add H2 headings for each problem.

1. Read the processed HTML file at `/tmp/<PDF_ID>_fixed.html`
2. Identify each problem in the exam (usually numbered 1, 2, 3, etc.)
3. For each problem, add an H2 heading immediately before the problem content:
   ```html
   <h2 class="unnumbered" id="problem-N">Problem N</h2>
   ```

**Why this matters:**
- H2 headings provide semantic structure for screen readers
- Users can navigate between problems using heading navigation
- WCAG 2.1 requires proper heading hierarchy for accessibility

**Example transformation:**
```html
<!-- Before: Problem without heading -->
<p><span class="problem-number">(1)</span> Let f: R → R be a continuous function...</p>

<!-- After: Problem with proper H2 heading -->
<h2 class="unnumbered" id="problem-1">Problem 1</h2>
<p>Let f: R → R be a continuous function...</p>
```

**Important notes:**
- Each problem MUST have its own H2 heading
- Remove any inline problem numbering like `<span class="problem-number">(1)</span>` or `<br /><br />(1)` when adding the H2
- Use the pattern: `<h2 class="unnumbered" id="problem-N">Problem N</h2>`
- The ID should match the problem number for anchor linking

### Step 8: Save to final location
Save the processed HTML file (from `/tmp/<PDF_ID>_fixed.html`) next to the original PDF with the same name but .html extension.

### Step 9: Add accessible HTML link to the generals page
After saving the HTML file, you MUST update the link in `graduate/general_exams.md` to follow accessibility best practices:

**IMPORTANT FOR CONCURRENT EXECUTION:**
- If running multiple instances concurrently, this step may fail with "File has been modified since read"
- If this happens, simply re-read the file and retry the edit
- Alternatively, you can defer this step and update all links at once after all conversions complete

1. Read the file `graduate/general_exams.md`
2. Find the line that references the PDF you just processed
3. Replace that line to make HTML the primary link and PDF secondary
4. **If the Edit fails** due to concurrent modification: re-read the file and try again

**IMPORTANT: HTML must be the PRIMARY link (accessible version), PDF must be SECONDARY (for printing only)**

**Link Format:**
```markdown
# Before (PDF only):
- [08/2022, real]({{site.url}}/graduate/exams/analysis/2022Aug_real.pdf)

# After (HTML primary, PDF secondary):
- [08/2022, real]({{site.url}}/graduate/exams/analysis/2022Aug_real.html) &bull; <a href="{{site.url}}/graduate/exams/analysis/2022Aug_real.pdf" aria-label="PDF version for printing">PDF</a>
```

**Key requirements:**
- Primary link text (e.g., "08/2022, real") links to the HTML version
- Use `&bull;` as separator
- PDF link must have `aria-label="PDF version for printing"`
- PDF link text is simply "PDF"

**Rationale:** This follows WCAG 2.1 Level AA guidelines by:
- Making the accessible format (HTML) primary and most prominent
- Clearly labeling the PDF as "for printing" to indicate its purpose
- Using ARIA labels to communicate that PDFs may have accessibility limitations

### Step 10: COMPREHENSIVE LEGAL COMPLIANCE AUDIT
**⚠️ CRITICAL**: This step is MANDATORY as accessibility violations expose the website to ADA lawsuits. All items must pass.

After completing all processing steps, you MUST:
1. Read both the original PDF and the generated HTML file
2. Perform a thorough WCAG 2.1 Level AA compliance audit
3. Fix any violations immediately before declaring the file production-ready

```bash
# Read both files
Read <PATH_TO_PDF>
Read <PATH_TO_HTML>
```

## WCAG 2.1 Level AA Compliance Checklist

### 1. Document Structure (WCAG 1.3.1, 2.4.1)
- [ ] Valid HTML5 DOCTYPE present
- [ ] `lang="en"` attribute on `<html>` element
- [ ] UTF-8 character encoding declared
- [ ] Viewport meta tag for mobile accessibility

### 2. Page Title (WCAG 2.4.2)
- [ ] Descriptive `<title>` tag present (e.g., "Analysis General Exam August 2017 - UVA Mathematics")
- [ ] Title accurately describes page content

### 3. Semantic Heading Hierarchy (WCAG 1.3.1, 2.4.6) **[CRITICAL]**
- [ ] Exactly ONE H1 heading (exam title)
- [ ] H2 heading for EVERY problem (e.g., `<h2 class="unnumbered" id="problem-1">Problem 1</h2>`)
- [ ] No skipped heading levels (H1 → H2, never H1 → H3)
- [ ] Each heading has unique `id` attribute
- [ ] Count problems in PDF = count of H2 headings in HTML

### 4. Landmark Elements (WCAG 1.3.1, 2.4.1)
- [ ] Breadcrumb `<nav>` with `aria-label="Breadcrumb"`
- [ ] Page navigation `<nav>` with `aria-label="Page navigation"`
- [ ] Main content wrapped in `<main>` element
- [ ] Proper opening/closing tags for all landmarks

### 5. Navigation Accessibility (WCAG 2.4.4, 2.4.8, 4.1.2)
- [ ] Breadcrumb uses ordered list (`<ol>`)
- [ ] Breadcrumb separators have `aria-hidden="true"`
- [ ] Current page marked with `aria-current="page"`
- [ ] Back button is semantic `<a>` element with descriptive text
- [ ] All links have clear, descriptive text

### 6. MathML Accessibility (WCAG 1.3.1, 1.4.5, 4.1.2) **[CRITICAL]**
**Audit ALL math elements - check a representative sample:**
- [ ] All have `role="math"`
- [ ] All have `aria-label` with LaTeX source
- [ ] All have `xmlns="http://www.w3.org/1998/Math/MathML"`
- [ ] All use `<semantics>` wrapper
- [ ] All have `<annotation encoding="application/x-tex">`

### 7. Unicode Character Verification **[LAWSUIT RISK - CRITICAL]**
**NO Unicode mathematical characters allowed. All MUST be HTML entities.**

Run these verification commands:
```bash
# Check for Unicode mathematical operators (U+2200-U+22FF)
grep -P '[\x{2200}-\x{22FF}]' <PATH_TO_HTML>

# Check for Unicode mathematical alphanumeric symbols (U+1D400-U+1D7FF)
# This includes blackboard bold: 𝔸 𝔹 ℂ 𝔻 𝔼 𝔽 𝔾 ℍ 𝕀 𝕁 𝕂 𝕃 𝕄 ℕ 𝕆 ℙ ℚ ℝ 𝕊 𝕋 𝕌 𝕍 𝕎 𝕏 𝕐 ℤ
grep -P '[\x{1D400}-\x{1D7FF}]' <PATH_TO_HTML>

# Check for common Greek letters
grep -P '[α-ωΑ-Ω]' <PATH_TO_HTML>
```

**If ANY Unicode characters are found, FIX IMMEDIATELY:**
- **Most common violation**: 𝔻 (U+1D53B) → Must be `&Dopf;`
- ℝ → `&Ropf;`, ℂ → `&Copf;`, ℕ → `&Nopf;`, ℤ → `&Zopf;`, ℚ → `&Qopf;`
- → → `&rarr;`, ≥ → `&ge;`, ≤ → `&le;`, ∈ → `&isin;`, ∞ → `&infin;`
- α → `&alpha;`, β → `&beta;`, π → `&pi;`, φ → `&phi;`, ψ → `&psi;`, χ → `&chi;`

**Manual inspection required for:**
- [ ] Check `<mi>` elements inside `<math>` tags for raw Unicode
- [ ] Verify blackboard bold letters (𝔻, ℝ, ℂ, ℕ, ℤ, ℚ) use entities
- [ ] Verify Greek letters use entities
- [ ] Verify mathematical operators use entities

### 8. Color Contrast (WCAG 1.4.3)
- [ ] Body text has minimum 4.5:1 contrast ratio (7:1 for AA)
- [ ] Link colors have sufficient contrast
- [ ] Navigation elements have sufficient contrast

### 9. Keyboard Accessibility (WCAG 2.1.1, 2.4.3, 2.4.7)
- [ ] All interactive elements keyboard accessible
- [ ] Logical tab order (breadcrumb → back → main content)
- [ ] No keyboard traps

### 10. Mobile/Responsive (WCAG 1.4.4, 1.4.10)
- [ ] Responsive meta viewport tag present
- [ ] Flexible layout (no fixed widths)
- [ ] Mobile-specific CSS (@media queries)

### 11. Content Quality (WCAG 3.1.1, 3.1.2)
- [ ] Language declared: `lang="en"`
- [ ] All content is in declared language

## Legal Compliance Summary

After completing the audit, provide:

**✅ PASS / ❌ FAIL Summary:**
- Document Structure: [PASS/FAIL]
- Page Title: [PASS/FAIL]
- Heading Hierarchy: [PASS/FAIL]
- Landmark Elements: [PASS/FAIL]
- Navigation: [PASS/FAIL]
- MathML: [PASS/FAIL]
- **Unicode Verification: [PASS/FAIL]** ← CRITICAL
- Color Contrast: [PASS/FAIL]
- Keyboard: [PASS/FAIL]
- Mobile: [PASS/FAIL]
- Content: [PASS/FAIL]

**Final Verdict:**
- ✅ **PRODUCTION READY** - All WCAG 2.1 Level AA requirements met. Lawsuit risk: MINIMAL.
- ❌ **NOT PRODUCTION READY** - Fix violations immediately before deployment.

**If ANY items fail: FIX THEM IMMEDIATELY. Do not proceed until all items pass.**

This comprehensive audit ensures legal compliance and protects the university from ADA lawsuits.

---

### AUTOMATED WCAG VERIFICATION (REQUIRED)

**After completing your manual audit, IMMEDIATELY run the automated verification script:**

```bash
python3 scripts/verify_wcag.py <PATH_TO_HTML_FILE>
```

**This script automatically checks:**
- ✓ Unicode violations (U+1D400-U+1D7FF range)
- ✓ H1 tag presence
- ✓ `<main>` landmark presence
- ✓ MathML `role="math"` attributes
- ✓ Breadcrumb navigation

**Example:**
```bash
python3 scripts/verify_wcag.py graduate/exams/analysis/2017Aug.html
```

**Expected output if compliant:**
```
✅ graduate/exams/analysis/2017Aug.html: PASS
```

**If the script reports ANY failures:**
1. **STOP immediately**
2. Fix the violations
3. Re-run the script
4. Only proceed when you see `✅ PASS`

**This automated check is MANDATORY** - it catches violations that manual review may miss and ensures consistent compliance across all exam files.

---

## Important Notes
- **CONCURRENT EXECUTION**: This command uses unique PDF_ID-based filenames in `/tmp/`, so multiple instances can run simultaneously without conflicts
  - **Concurrent safety**: All processing steps (Mathpix API, file conversion, HTML generation) are fully isolated per PDF
  - **File editing caveat**: Step 9 (updating `general_exams.md`) may fail if multiple instances edit simultaneously - if this happens, retry after re-reading the file
  - **Batch workflow tip**: When processing many PDFs, you can skip Step 9 in concurrent runs and update all `general_exams.md` links together at the end
- Do NOT use the direct .html download from Mathpix - it uses MathJax SVG rendering
- Always use the tex.zip → pandoc → post-processing pipeline
- Verify that NO Unicode mathematical characters remain in the final output
- Verify proper heading hierarchy (use grep or check a sample)
- The final HTML should be fully accessible with screen readers

## Success Criteria - WCAG 2.1 Level AA Compliance

The output HTML must meet ALL of these criteria to be production-ready:

### Technical Requirements
✓ Actual MathML elements (`<math>`, `<mrow>`, `<mi>`, `<mo>`, etc.)
✓ **NO Unicode characters** - all replaced with HTML/MathML entities (especially **𝔻 → &Dopf;**)
✓ Proper heading hierarchy (ONE H1, H2 for EVERY problem, no skipped levels)
✓ H2 heading for each problem (e.g., `<h2 class="unnumbered" id="problem-1">Problem 1</h2>`)
✓ ARIA attributes on all math elements (`role="math"`, `aria-label` with LaTeX)
✓ `lang="en"` attribute on `<html>` element
✓ Descriptive page title (e.g., "Analysis General Exam August 2017 - UVA Mathematics")
✓ Breadcrumb navigation with `aria-label="Breadcrumb"`
✓ Back button navigation with `aria-label="Page navigation"`
✓ Main content wrapped in `<main>` landmark element
✓ Valid, well-formed HTML5 document with proper semantic structure
✓ Proper vertical spacing between main problems
✓ HTML file saved next to the PDF with .html extension
✓ Link in `graduate/general_exams.md` updated (HTML primary, PDF secondary with aria-label)

### Legal Compliance Requirements
✓ **WCAG 2.1 Level AA compliant** - All 11 checklist items pass
✓ **Unicode verification passed** - No raw Unicode mathematical characters
✓ **Screen reader compatible** - All math properly labeled with ARIA
✓ **Keyboard accessible** - Logical tab order, no traps
✓ **Mobile responsive** - Viewport meta tag, flexible layout
✓ **Color contrast compliant** - Minimum 4.5:1 ratio for text
✓ **Semantic structure** - Proper landmarks, headings, lists
✓ **ADA Title II & III compliant** - Ready for public deployment
✓ **Section 508 compliant** - Federal accessibility standards met

### Final Review Completed
✓ Both PDF and HTML reviewed side-by-side
✓ Comprehensive WCAG 2.1 Level AA audit performed
✓ All violations fixed immediately
✓ Legal compliance summary provided
✓ **Lawsuit risk: MINIMAL** - File is legally defensible

**If any criterion fails, the file is NOT production-ready and must be fixed immediately.**

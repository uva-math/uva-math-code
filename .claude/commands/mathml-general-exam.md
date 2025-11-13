---
description: OCR a general exam PDF to accessible HTML with MathML using Mathpix API
---

You are going to OCR a general exam PDF file to accessible HTML with MathML using the Mathpix API. Follow these steps precisely:

## Requirements
- The PDF path will be provided as an argument to this command
- Use Mathpix API credentials from environment variables (MATHPIX_APP_ID and MATHPIX_API_KEY)
- Generate accessible HTML with:
  - Actual MathML markup (NOT SVG, NOT Unicode characters)
  - Proper ARIA attributes (role="math", aria-label with LaTeX)
  - Proper semantic heading hierarchy (H1 for title, H2 for sections/problems)

## Workflow

### Step 1: Upload PDF to Mathpix
Use the Mathpix v3/pdf API endpoint to upload the PDF:
```bash
curl -X POST "https://api.mathpix.com/v3/pdf" \
  -H "app_id: $MATHPIX_APP_ID" \
  -H "app_key: $MATHPIX_API_KEY" \
  -F "file=@<PDF_PATH>" \
  -F 'options_json={"conversion_formats": {"html.zip": true, "tex.zip": true}}'
```

Extract the `pdf_id` from the response.

### Step 2: Check conversion status
Poll the status endpoint until conversion is complete:
```bash
curl -X GET "https://api.mathpix.com/v3/pdf/<PDF_ID>" \
  -H "app_id: $MATHPIX_APP_ID" \
  -H "app_key: $MATHPIX_API_KEY"
```

Wait until `"status":"completed"`.

### Step 3: Download and Extract TeX Format
Download the tex.zip format (NOT .html, as it uses SVG):
```bash
curl -X GET "https://api.mathpix.com/v3/pdf/<PDF_ID>.tex.zip" \
  -H "app_id: $MATHPIX_APP_ID" \
  -H "app_key: $MATHPIX_API_KEY" \
  -o /tmp/output.tex.zip

cd /tmp && unzip -o output.tex.zip
```

The extracted .tex file will be in a subdirectory named with the PDF_ID.

### Step 4: Convert to HTML with MathML using Pandoc
```bash
pandoc /tmp/<PDF_ID>/<PDF_ID>.tex -f latex -t html --mathml --standalone -o /tmp/output_mathml.html
```

### Step 5: Post-process to fix Unicode and improve accessibility
Use the Python script `scripts/fix_mathml.py` to:
1. Replace all Unicode mathematical characters with HTML/MathML entities (&rarr;, &infin;, &Copf;, &epsilon;, etc.)
2. Fix heading hierarchy (first H1 stays as title, subsequent H1s become H2)
3. Add ARIA attributes to all math elements (role="math", aria-label with LaTeX source)
4. Add lang="en" attribute to the <html> element
5. Extract title from H1 and set descriptive page title (e.g., "REAL ANALYSIS GENERAL EXAM FALL 2022 - UVA Mathematics")
6. Add breadcrumb navigation at the top of the page
7. Add a back button navigation below the breadcrumb
8. Wrap main content in <main> landmark element

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
- Number sets: ℝ (&Ropf;), ℂ (&Copf;), ℕ (&Nopf;), ℤ (&Zopf;), ℚ (&Qopf;)
- Greek letters: α (&alpha;), β (&beta;), γ (&gamma;), δ (&delta;), ε (&epsilon;), η (&eta;), θ (&theta;), λ (&lambda;), μ (&mu;), ν (&nu;), π (&pi;), σ (&sigma;), τ (&tau;), φ (&phi;), ω (&omega;), Γ (&Gamma;), Δ (&Delta;), Θ (&Theta;), Λ (&Lambda;), Σ (&Sigma;), Φ (&Phi;), Ω (&Omega;)
- Other: ∞ (&infin;), × (&times;), ⋅ (&sdot;), ± (&plusmn;), ∠ (&ang;), ⊕ (&oplus;), ⊗ (&otimes;)

### Step 6: Save to final location
Save the processed HTML file next to the original PDF with the same name but .html extension.

### Step 7: Add accessible HTML link to the generals page
After saving the HTML file, you MUST update the link in `graduate/general_exams.md` to follow accessibility best practices:

1. Read the file `graduate/general_exams.md`
2. Find the line that references the PDF you just processed
3. Replace that line to make HTML the primary link and PDF secondary

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

## Important Notes
- Do NOT use the direct .html download from Mathpix - it uses MathJax SVG rendering
- Always use the tex.zip → pandoc → post-processing pipeline
- Verify that NO Unicode mathematical characters remain in the final output
- Verify proper heading hierarchy (use grep or check a sample)
- The final HTML should be fully accessible with screen readers

## Success Criteria
The output HTML must have:
✓ Actual MathML elements (<math>, <mrow>, <mi>, <mo>, etc.)
✓ NO Unicode characters - all replaced with HTML/MathML entities
✓ Proper heading hierarchy (H1 for title, H2 for problems/sections)
✓ ARIA attributes on all math elements (role="math", aria-label)
✓ lang="en" attribute on <html> element
✓ Descriptive page title derived from H1 content (e.g., "TITLE - UVA Mathematics")
✓ Breadcrumb navigation with aria-label="Breadcrumb" at top
✓ Back button navigation with aria-label="Page navigation" below breadcrumb
✓ Main content wrapped in <main> landmark element
✓ Valid, well-formed HTML5 document with proper semantic structure
✓ HTML file saved next to the PDF with .html extension
✓ Link in graduate/general_exams.md updated with HTML as primary, PDF as secondary with aria-label

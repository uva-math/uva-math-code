# UVA Math Website - PDF to HTML Conversion Scripts

This directory contains automated validation scripts for converting PDFs to accessible HTML with MathML.

## Scripts Overview

The legacy Python conversion validators listed below use the Python standard library. Browser, PDF export, and schedule tools have separate dependencies documented in their own sections.

### Master Validation Script

**`validate_conversion.py`** - Runs the four legacy conversion checks listed below
```bash
python3 scripts/validate_conversion.py path/to/file.html
```

Outputs a report with an overall PASS/FAIL result for the implemented checks. A passing result does not establish WCAG conformance; inspect the rendered document and compare it with the source PDF.

### Individual Validation Scripts

**`verify_wcag.py`** - Limited HTML structure checks
- H1 tag presence
- `<main>` landmark element

Mathematical Unicode is valid inside native MathML. An explicit `role="math"`
and breadcrumb navigation are not universal accessibility requirements. The
historical script name does not imply a WCAG certification.

```bash
python3 scripts/verify_wcag.py path/to/file.html
```

**`check_heading_hierarchy.py`** - Semantic heading structure
- Exactly one H1 heading
- No skipped heading levels (H1→H2→H3, never H1→H3)
- All headings have unique IDs
- No duplicate IDs

```bash
python3 scripts/check_heading_hierarchy.py path/to/file.html
```

**`check_links_images.py`** - Links and images validation
- Broken internal anchor links (#id references)
- Missing image files (relative paths)
- Images without alt attributes
- Empty links without text or aria-label

```bash
python3 scripts/check_links_images.py path/to/file.html
```

**`check_mathml.py`** - MathML structure checks
- Rejects `aria-label` values copied from the LaTeX annotation, which override native math semantics
- Reports missing namespaces, `<semantics>` wrappers, and source annotations as warnings
- Reports inline/block counts and optional ARIA attributes as statistics

Native `<math>` has implicit math semantics. Preserve its structured content and
mathematical Unicode; do not add a raw LaTeX label. A source `<annotation>` keeps
TeX available without making it the accessible name. Verify mathematical meaning
and assistive-technology output separately.

```bash
python3 scripts/check_mathml.py path/to/file.html
```

### Processing Scripts

**`fix_mathml.py`** - Legacy standalone exam post-processing
- Preserves native MathML and mathematical Unicode
- Removes existing math labels copied from source TeX; retains authored speech labels
- Applies its legacy heading, exam navigation, title, and `<main>` helpers

Use this helper only on a fresh standalone exam conversion. Existing Jekyll
`document_page` content already receives shared navigation and landmarks from its
layout; do not apply the standalone wrapper helpers to it.

```bash
python3 scripts/fix_mathml.py input.html output.html
```

Run the native-MathML regression fixtures with
`python3 scripts/test_fix_mathml.py`. They cover Unicode preservation, removal of
copied TeX labels, retained authored speech labels, and the command-line pipeline.

**`fix_unicode_violations.py`** - Legacy entity serialization utility
- Converts selected Unicode mathematical characters to HTML entities in batches
- This is not an accessibility repair and is not needed for native MathML

Do not use this utility as a conversion validation or compliance requirement.

```bash
python3 scripts/fix_unicode_violations.py
```

## Usage in Workflow

### Step-by-step conversion process:

1. **Upload PDF** to Mathpix API
2. **Download** TeX format
3. **Convert** with Pandoc: `pandoc input.tex -f latex -t html --mathml -o content.html` (add `--standalone` only for the legacy `fix_mathml.py` standalone route)
4. **Prepare the page** with the shared `document_page` layout, or use `fix_mathml.py` for a fresh standalone exam as described above. Preserve native MathML; do not add raw-TeX ARIA labels.
5. **Validate the rendered HTML**: `python3 scripts/validate_conversion.py path/to/rendered.html`
6. **Fix reported issues** and rerun the affected checks.
7. **Compare against the original PDF** for complete prose, formulas, figures, captions, and reading order; review image descriptions, keyboard access, both themes, reflow, and assistive-technology behavior. Automated PASS results cover only their implemented checks.

### Expected output (when all checks pass):

```
================================================================================
PDF TO HTML CONVERSION VALIDATION REPORT
================================================================================

File: graduate/exams/analysis/2025Jan_complex.html

1. AUTOMATED ACCESSIBILITY STRUCTURE CHECKS
   ✅ PASS

2. HEADING HIERARCHY
   ✅ PASS

3. LINKS AND IMAGES
   ✅ PASS

4. MATHML ACCESSIBILITY
   ✅ PASS

   Statistics:
      Total math elements: 47
      With role="math": 0
      With aria-label: 0
      Inline/Block: 32/15

================================================================================
OVERALL VERDICT
================================================================================
All implemented conversion checks passed.
These checks do not certify WCAG conformance or legal compliance.
Review content, keyboard behavior, visual presentation, and assistive technology manually.
```

## Accessibility regression checks

Run `bundle exec ruby scripts/audit_accessibility.rb _site /tmp/accessibility.json`
after a full Jekyll build to check every rendered HTML page for document titles,
language, main landmarks, skip links, heading structure, duplicate IDs, image
alternatives, frame titles, form labels, unnamed controls, and new-window links.
The JSON report lists paths, rendered line numbers, and individual findings.

For a browser scan, run `npm ci`, then `npx playwright install chromium`, serve the
built site locally, and run:

```bash
npm run accessibility:browser -- --site _site --url http://127.0.0.1:4173 --report /tmp/browser-accessibility.json
node scripts/test_dynamic_accessibility.cjs
node scripts/test_table_accessibility.cjs _site http://127.0.0.1:4173
```

Build with a local `url` override matching the preview server so assets and links
remain on the local site. The browser scanner supports `--width 320`, `--theme dark`,
and `--paths /tmp/pages.json` (a JSON list of paths relative to the build directory).
It checks rendered axe rules, page overflow, and JavaScript errors. The dynamic
checks exercise keyboard controls, carousel state, search feedback, and calendar
success/error cases with deterministic fixtures.

The table check visits every built page containing a table at 320, 400 and 1280px.
It checks for words split across lines, page overflow, named keyboard-accessible
scroll containers, and arrow-key scrolling on the schedule and a legacy archive.
Wrap wide tables in a labeled `.table-responsive` region with `tabindex="0"` so
columns can scroll without compressing words or widening the whole page.
Name the region from its caption or nearby heading, using `aria-labelledby` when
possible. Avoid generic names such as "Table 1" in the screen reader's landmark list.

These are limited automated checks. Neither they nor the conversion scripts
establish WCAG conformance or legal compliance. They cannot verify the accuracy
of image descriptions, complete mathematical content, keyboard task completion,
screen-reader usability, or PDF tagging. Review those separately.

## Python Version

The legacy Python conversion validators require **Python 3.6+**. Other tools have their own runtime requirements.

## Legacy Validator Dependencies

The legacy Python conversion validators use only the Python standard library:
- `re` - Regular expressions
- `os` - File system operations
- `sys` - System-specific parameters
- Built-in data structures (dict, list, set)

No `pip install` is required for these legacy validators. See [accessibility/README.md](accessibility/README.md) for the PDF exporter dependencies.

## Virtual Environment (Optional)

While not required, you can use a virtual environment:

```bash
# Create venv (already gitignored)
python3 -m venv venv

# Activate (optional - scripts work without activation)
source venv/bin/activate

# No packages to install - all standard library!
```

## Exit Codes

The conversion validators follow these exit codes:
- **0** = All checks passed (success)
- **1** = One or more checks failed (failure)

This allows integration with CI/CD pipelines.

## Contributing

When adding new validation checks:
1. Use only Python standard library (no external dependencies)
2. Return `(passed: bool, details: list)` tuple
3. Provide clear, actionable error messages
4. Add to `validate_conversion.py` master script
5. Document in this README

## Related Documentation

- See `/.claude/commands/mathml-general-exam.md` for exam conversion workflow
- See `/.claude/commands/mathml-any-pdf.md` for general PDF conversion workflow
- See `/CLAUDE.md` for website content management guidelines

## Public class schedule

`schedule.tex` feeds both the reflowable `/schedule/` snapshot and the compact tagged
landscape PDF. `python3 scripts/schedule/schedule_build.py` validates the room-free
source, exports and validates the PDF, updates `schedule.html`, stages both current and
term-specific PDF/TeX files, and refreshes the five page link blocks. Use `--site PATH`
with a copied `schedule.tex` and `_config.yml` to test staging outside the repository.
The HTML renderer retains all section rows, independent-study and exam notes, and the
graduate weekly grid; it rejects unknown source markup instead of dropping text.

The tagged exporter needs the pinned Node/Python tooling, Chromium, veraPDF, and
Poppler described in [accessibility/README.md](accessibility/README.md). A direct
LaTeX preview does not replace this validated publishing workflow. For enrollment
refresh commands and the room safeguards, see the schedule section of `CLAUDE.md`.

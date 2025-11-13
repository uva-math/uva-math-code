# UVA Math Website - PDF to HTML Conversion Scripts

This directory contains automated validation scripts for converting PDFs to accessible HTML with MathML.

## Scripts Overview

All scripts use **Python 3 standard library only** - no external dependencies required.

### Master Validation Script

**`validate_conversion.py`** - Comprehensive validation suite that runs all checks
```bash
python3 scripts/validate_conversion.py path/to/file.html
```

Outputs a complete report with overall PASS/FAIL verdict.

### Individual Validation Scripts

**`verify_wcag.py`** - WCAG 2.1 Level AA compliance
- Unicode violations (U+1D400-U+1D7FF mathematical alphanumeric symbols)
- H1 tag presence
- `<main>` landmark element
- MathML `role="math"` attributes
- Breadcrumb navigation

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

**`check_mathml.py`** - MathML accessibility
- All `<math>` elements have `role="math"`
- All `<math>` elements have `aria-label` with LaTeX
- Proper `<semantics>` wrappers
- LaTeX `<annotation>` elements
- Statistics: inline vs block display mode

```bash
python3 scripts/check_mathml.py path/to/file.html
```

### Processing Scripts

**`fix_mathml.py`** - Post-processing for accessibility
- Replace Unicode mathematical characters with HTML entities
- Fix heading hierarchy
- Add ARIA attributes to math elements
- Add breadcrumb and back button navigation
- Wrap content in `<main>` landmark
- Extract title and set page title

```bash
python3 scripts/fix_mathml.py input.html output.html
```

**`fix_unicode_violations.py`** - Batch fix Unicode violations
- Converts Unicode mathematical characters to HTML entities
- Designed for fixing multiple files

```bash
python3 scripts/fix_unicode_violations.py
```

## Usage in Workflow

### Step-by-step conversion process:

1. **Upload PDF** to Mathpix API
2. **Download** TeX format
3. **Convert** with Pandoc: `pandoc input.tex -f latex -t html --mathml --standalone -o output.html`
4. **Post-process**: `python3 scripts/fix_mathml.py output.html fixed.html`
5. **Validate**: `python3 scripts/validate_conversion.py fixed.html`
6. **Fix violations** if needed
7. **Re-validate** until PASS

### Expected output (when all checks pass):

```
================================================================================
PDF TO HTML CONVERSION VALIDATION REPORT
================================================================================

File: graduate/exams/analysis/2025Jan_complex.html

1. WCAG 2.1 LEVEL AA COMPLIANCE
   ✅ PASS

2. HEADING HIERARCHY
   ✅ PASS

3. LINKS AND IMAGES
   ✅ PASS

4. MATHML ACCESSIBILITY
   ✅ PASS

   Statistics:
      Total math elements: 47
      With role="math": 47
      With aria-label: 47
      Inline/Block: 32/15

================================================================================
OVERALL VERDICT
================================================================================
✅ PRODUCTION READY - All checks passed
✅ WCAG 2.1 Level AA compliant
✅ ADA Title II & III compliant
✅ Lawsuit risk: MINIMAL
```

## Legal Compliance

These scripts ensure:
- **WCAG 2.1 Level AA** compliance
- **ADA Title II & III** compliance (public entities, places of public accommodation)
- **Section 508** compliance (federal accessibility standards)
- **Minimized lawsuit risk** from accessibility violations

## Python Version

All scripts require **Python 3.6+** (uses f-strings and type hints).

## No External Dependencies

All scripts use only Python standard library:
- `re` - Regular expressions
- `os` - File system operations
- `sys` - System-specific parameters
- Built-in data structures (dict, list, set)

No `pip install` required!

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

All scripts follow standard Unix exit codes:
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

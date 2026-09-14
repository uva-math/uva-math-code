---
description: Convert a general exam PDF into a reviewed shared-layout HTML companion with native MathML
---

Convert the general exam PDF supplied as the command argument. Follow the source inspection, Mathpix TeX/Pandoc conversion, shared document layout, rendered validation, and PDF staging workflow in [mathml-any-pdf.md](mathml-any-pdf.md). This document adds the exam-specific requirements; the general workflow is the single source for conversion commands and validation limits.

## Preserve the complete examination

Read every source page and record its title, date, subject, instructions, problem numbers, subparts, diagrams, and any answer spaces. Prefer an available complete TeX source; use Mathpix OCR when needed. Check the conversion against the original for missing page continuations, omitted questions, sign/subscript errors, and missing matrix or fill-in rows. Read long archives in tracked batches; file size does not justify skipping their originals.

Preserve distinct historical versions. Repeated dates or titles do not prove that two exams are duplicates. For combined archives, retain the full text and figures of every constituent exam in the manifest, not just the links on the archive index page.

## Use the shared document layout

Save the HTML beside its PDF, retaining the filename and case with an explicit permalink. Short exams use the same `document_page` layout as longer documents:

```html
---
layout: document_page
title: "Real Analysis General Exam, August 2022"
permalink: "/graduate/exams/analysis/2022Aug_real.html"
---

{% raw %}
<h1>Real Analysis General Exam, August 2022</h1>
<p>Preserved examination instructions.</p>
<h2 id="problem-1">Problem 1</h2>
<p>Reviewed problem text and native MathML.</p>
{% endraw %}
```

Provide one visible H1, navigable problem headings, and correctly nested subparts. Preserve the source numbering; avoid duplicating a problem number in both a heading and a separate decorative label. The layout supplies the single main landmark, shared navigation, skip link, title metadata, and responsive styles. Do not add a standalone HTML shell, another `<main>`, or the legacy `fix_mathml.py` navigation wrappers.

Use native MathML from Pandoc's `--mathml` output and retain source annotations when available. Mathematical Unicode is valid. Explicit `role="math"` is optional, and raw TeX must not be placed in `aria-label` to override structured math. Review diagrams visually; describe the relevant mathematical objects, labels, and relationships, using an extended description when a short alt cannot express them.

## Update the exam listing

Update the corresponding entry in `graduate/general_exams.md` with descriptive links to both versions:

```markdown
- [Real Analysis General Exam, August 2022]({{site.url}}/graduate/exams/analysis/2022Aug_real.html) · [Real Analysis General Exam, August 2022 (PDF)]({{site.url}}/graduate/exams/analysis/2022Aug_real.pdf)
```

When several conversions run concurrently, isolate temporary files and assign the shared exam listing and PDF manifest to one editor, or re-read them before each edit. Avoid overwriting another conversion's changes.

## Verify and report

Build the site, check the real `.html` URL and expected examination content, run the current rendered structural/browser checks, and compare all questions and illustrations against the PDF. Check keyboard access, both themes, reflow, focus visibility, and representative mathematical output with assistive technology. Report which checks were actually performed.

For a regenerated PDF, add the complete source and original hash/page count to `scripts/accessibility/pdf-manifest.json`, then use the staging and review workflow in [scripts/accessibility/README.md](../../scripts/accessibility/README.md). Inspect formula descriptions and printed content as well as the PDF/UA-1 validation result. Preserve historical files that do not have complete accessible sources and record that limitation honestly.

A script PASS covers only its implemented checks. It does not certify complete mathematical content, screen-reader usability, WCAG conformance, or legal compliance. Report the corrected files, source-comparison coverage, validation results, and remaining issues without those unsupported claims.

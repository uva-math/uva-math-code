---
description: Convert a PDF to reviewed HTML with native MathML and validate its accessible PDF companion
---

Convert the PDF supplied as the command argument into a complete HTML companion. An optional second argument identifies the page linking to the PDF. Use the shared `document_page` layout for every published companion, including short exams. Preserve the original content and existing public URLs.

## 1. Inspect and preserve the source

Record the PDF path, title, page count, original SHA-256, and existing HTML or TeX sources. Prefer complete editable sources when available. Otherwise use the Mathpix TeX workflow below. Work in a unique temporary directory for each conversion.

Read the source PDF, using extracted text and rendered pages together. Inventory its sections, questions, appendices, tables, photographs, diagrams, captions, footnotes, and references. For a large document, review it in page batches and record coverage; file size is not a reason to skip source comparison. Image-only pages and scanned formulas require visual inspection.

Keep the original PDF available during conversion and review. Historical variants may have distinct questions or diagrams: compare them before consolidating anything. An index linking to separate documents is not the full content of a combined archive.

## 2. Obtain TeX and illustrations

Use `MATHPIX_APP_ID` and `MATHPIX_API_KEY` from the environment without printing their values. Upload the complete PDF, retaining the returned `pdf_id` and any processing warnings:

```sh
PDF_WORK=$(mktemp -d)
curl --fail-with-body -X POST 'https://api.mathpix.com/v3/pdf' -H "app_id: $MATHPIX_APP_ID" -H "app_key: $MATHPIX_API_KEY" -F "file=@<PDF_PATH>" -F 'options_json={"conversion_formats":{"tex.zip":true}}'
```

Poll the returned job until it reports `status: completed`; handle an error response before continuing:

```sh
curl --fail-with-body 'https://api.mathpix.com/v3/pdf/<PDF_ID>' -H "app_id: $MATHPIX_APP_ID" -H "app_key: $MATHPIX_API_KEY"
```

Download and extract the TeX archive into that conversion's working directory:

```sh
curl --fail-with-body 'https://api.mathpix.com/v3/pdf/<PDF_ID>.tex.zip' -H "app_id: $MATHPIX_APP_ID" -H "app_key: $MATHPIX_API_KEY" -o "$PDF_WORK/source.tex.zip"
unzip "$PDF_WORK/source.tex.zip" -d "$PDF_WORK/source"
```

Locate and read the extracted TeX and image files. Check OCR against the PDF, especially minus signs, subscripts, matrices, accented names, equations, page continuations, and text embedded in images. Preserve meaningful illustrations of every image format; do not rely on a JPEG-only copy command or on OCR's image count.

Convert the reviewed TeX to an HTML fragment with native MathML:

```sh
pandoc '<EXTRACTED_TEX_PATH>' -f latex -t html --mathml -o "$PDF_WORK/content.html"
```

Inspect Pandoc warnings and the generated structure. Use this TeX-to-MathML route for the web companion rather than importing an SVG-only math rendering.

## 3. Build the shared document page

Save the companion next to the PDF with the same basename and an explicit `.html` permalink. A file with spaces or mixed case must retain its real public path. For example:

```html
---
layout: document_page
title: "Analysis General Exam, January 2025"
permalink: "/graduate/exams/analysis/2025Jan_complex.html"
---

{% raw %}
<h1>Analysis General Exam, January 2025</h1>
<h2 id="problem-1">Problem 1</h2>
<p>Reviewed problem text and native MathML go here.</p>
{% endraw %}
```

The layout supplies the HTML shell, document title metadata, language, skip link, single main landmark, navigation, footer, shared styles, and document helpers. The content supplies one visible H1 and its own logical section headings. Remove imported `<html>`, `<head>`, `<body>`, and `<main>` wrappers, duplicate site navigation, and standalone Pandoc CSS. Do not run the legacy standalone wrapping pipeline in `fix_mathml.py` on a Jekyll document fragment.

Use H2 for major sections or individual exam problems and H3 for their subsections when appropriate. Preserve problem numbers, part labels, and original cross-references. Use real lists, not lines of text separated by `<br>`. Keep a document table of contents inside the content as a labeled `<nav>` with links to unique section IDs; adapt page references to working section links without losing their meaning.

Keep mathematical Unicode inside native MathML: `ℝ`, `α`, and `≤` are valid characters. HTML entities and the corresponding Unicode characters have the same decoded meaning. Native `<math>` has implicit mathematical semantics, so explicit `role="math"` is optional. Do not copy raw TeX into `aria-label`; it overrides the navigable math structure. Retain source TeX in `<annotation encoding="application/x-tex">` where available, and preserve the actual structured expression. The current `check_mathml.py` flags copied TeX labels; its ARIA counts are statistics, not required targets.

Place each photograph or figure with the correct surrounding section and caption. Write alt text after inspecting the actual image and the original caption; verify identities from those captions. A portrait is not a decorative divider. Complex mathematical diagrams need enough accompanying description to convey their objects, labels, arrows, and relationships. Use empty alt text only for actual decoration. Keep image paths valid and use the shared responsive styling.

Give data tables captions or clear associated headings, real header cells, and the appropriate header associations. Preserve all rows, blank answer spaces, and explanatory notes. Keep form controls labeled and use native controls. Mark passages in another language with the appropriate `lang` attribute. Avoid local font, fixed-width, or color overrides that defeat the shared light/dark and responsive styles.

## 4. Update links and the document inventory

Use the provided source page or find references with `rg -n -F 'filename.pdf'` in the relevant content directories. Put the descriptive HTML link first and keep a descriptive PDF link alongside it:

```markdown
[Analysis General Exam, January 2025]({{site.url}}/graduate/exams/analysis/2025Jan_complex.html) · [Analysis General Exam, January 2025 (PDF)]({{site.url}}/graduate/exams/analysis/2025Jan_complex.pdf)
```

Preserve real `.html` and `.pdf` destinations. Avoid repeated generic accessible names such as “PDF version for printing.” Re-read shared listing files before editing them, or assign their updates to one agent; unique temporary directories do not make concurrent edits to shared files safe.

For PDF regeneration, record the complete companion sources, original hash/page count, and honest review status in `scripts/accessibility/pdf-manifest.json`. A combined PDF needs the complete contents of every constituent document in source order. Retained historical files without a complete accessible source must remain explicitly classified as such; an HTML summary is not an equivalent replacement.

## 5. Validate the rendered document and its content

Build Jekyll and inspect the rendered `.html` URL. Verify HTTP 200 and the expected document title/content so a server error page cannot count as a passing accessibility test.

Run the available structural checks on rendered output:

```sh
python3 scripts/validate_conversion.py '<BUILT_HTML_PATH>'
bundle exec ruby scripts/audit_accessibility.rb '<BUILD_DIRECTORY>' /tmp/document-structure-review.json
```

See [scripts/README.md](../../scripts/README.md) for the current checks and browser commands. `verify_wcag.py` checks only a few structural features. `check_mathml.py` checks selected MathML patterns and warns about missing source metadata. Neither verifies the mathematical meaning, image-description accuracy, or complete source content.

Compare the full companion against the original, including every source page and each meaningful figure. Check text extraction for missing prose and inspect rendered math for OCR substitutions, missing rows, clipped symbols, or incorrect grouping. For a large document, divide the review into tracked batches rather than replacing source review with an automated PASS.

In the browser, test keyboard order and task completion, visible focus, links, disclosures and forms, narrow-screen reflow, zoom, both themes, image loading, and mathematical scrolling. Verify representative formulas and dynamic announcements with assistive technology and state the coverage of that check. Fix confirmed issues and rerun the affected checks.

## 6. Stage and review accessible PDF exports

Use the current exporter and validation workflow in [scripts/accessibility/README.md](../../scripts/accessibility/README.md). Install its pinned dependencies as documented, build/serve the reviewed HTML, and export to a temporary candidate path:

```sh
node scripts/accessibility/export_pdf.cjs --url 'http://127.0.0.1:4175/path/to/document.html' --output /tmp/document-candidate.pdf --python scripts/accessibility/.venv/bin/python
verapdf --flavour ua1 --format json /tmp/document-candidate.pdf
```

The exporter creates speech alternatives and Formula tags in the temporary print representation while leaving native MathML on the website intact. It preserves reviewed illustrations, removes site chrome, resolves links to public URLs, and writes the destination only after PDF/UA-1 validation. Review the PDF's text, figures, reading order, formula descriptions, and representative printed pages as well as its validation receipt.

Use `prepare_pdfs.rb`, `batch_export.py`, and the review stage of `install_pdfs.py` for the catalog and combined archives, following their README. Do not bypass missing-source, hash, content, or validation failures. A validated PDF still requires content review; the validator cannot establish that OCR or mathematical speech is correct.

## Completion report

Report the source/companion paths, links updated, document and figure coverage, corrections made, checks performed, and any remaining limitations. Distinguish structural/browser/PDF validation results from manual content and assistive-technology review. These checks do not certify WCAG conformance, ADA compliance, or legal protection. Do not claim an unperformed review or label an incomplete transcription as a complete accessible alternative.

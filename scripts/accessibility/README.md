# Accessible PDF exports

The exporter prints a reviewed HTML companion into a reflowed PDF, preserves its illustrations, and validates the result against PDF/UA-1. The destination PDF is written only after validation succeeds. Start from a complete HTML companion; a page containing links to individual exams is not a substitute for the contents of a combined archive.

Install the local tooling:

```sh
npm ci --prefix scripts/accessibility
npx --prefix scripts/accessibility playwright install chromium
python3 -m venv scripts/accessibility/.venv
scripts/accessibility/.venv/bin/pip install -r scripts/accessibility/requirements.txt
brew install verapdf
```

Build and serve the Jekyll site, then export one page:

```sh
node scripts/accessibility/export_pdf.cjs \
  --url http://127.0.0.1:4175/undergraduate/placement-files/ExamB_Solutions.html \
  --output /tmp/ExamB_Solutions.pdf \
  --python scripts/accessibility/.venv/bin/python
```

`--public-base` defaults to `https://math.virginia.edu`; PDF links never point to the local preview server. `--verapdf` selects a different validator executable. `--keep-work` retains the temporary print PDF and semantic metadata. Python selection uses `--python`, then `PDF_PYTHON`, then the local `scripts/accessibility/.venv/bin/python` when installed, then `python3`. `VERAPDF` can supply the validator default. A failed export retains diagnostic files and leaves an existing destination PDF untouched.

The public class schedule has a dedicated compact landscape layout generated from its
TeX source. Build and validate the PDF, update `/schedule/`, and stage the term archive
with `python3 scripts/schedule/schedule_build.py`. To inspect only its print HTML:

```sh
python3 scripts/schedule/schedule_html.py --print-output /tmp/schedule-print.html
node scripts/accessibility/export_pdf.cjs \
  --url file:///tmp/schedule-print.html --landscape --output /tmp/schedule-preview.pdf
```

`file://` input accepts self-contained print documents; use public absolute links in
them. `--landscape` enables landscape Letter and respects the document's CSS page size
and margins. Schedule tables use scoped course and column headers, preserve the complete
source including supplementary notes and the weekly grid, and keep 8pt section rows.
The schedule helper also requires Poppler's `pdfinfo` and `pdftotext` (on macOS,
`brew install poppler`). It refuses a failed PDF/UA validation, room data, or more than
four pages before writing either published PDF.

The CLI writes `OUTPUT.validation.json` with the complete veraPDF result and `OUTPUT.export.json` with counts and a summary. An independent validation uses:

```sh
verapdf --flavour ua1 --format json /tmp/ExamB_Solutions.pdf
```

The browser retains the document's main content, opens disclosures, uses the light print presentation, waits for fonts and every image, and removes the website navigation and footer. Document tables of contents remain in the main content. Link destinations become public absolute URLs. HTML print styles continue to control forms and document-specific formatting.

Chromium currently exports native MathML as unstructured glyph runs. In the temporary print DOM, MathJax therefore converts each MathML expression into an SVG image. Speech Rule Engine derives its spoken alternative directly from MathML. The PDF postprocessor changes those uniquely marked image tags to `Formula` and verifies that every expression occurs exactly once and every meaningful source image description survives. Native MathML on the website is unchanged. PDF formulas have spoken alternatives; the HTML remains the version with navigable mathematical structure.

The postprocessor also creates PDF list bodies, maps emphasis roles, labels link annotations, supplies language/title metadata, corrects nested figure containers, and marks untagged presentation operations as artifacts. It fails on unfamiliar list structures or missing mathematical/image tags. veraPDF runs afterward, and a failure prevents replacement of the destination.

Before replacing an existing PDF, compare the companion's complete text, figures, tables, and mathematical expressions with that PDF. Review representative printed pages and reading order as well as the validator report. Automated PDF/UA validation does not establish that a transcription is complete or a generated mathematical description is correct.

The reviewed samples include Placement Exam B Solutions, all eight Virginia Math Bulletins, the three combined exam archives, and lecture posters. Original poster layout is not reproduced by a text companion; event information and meaningful illustrations are preserved in the reflowed export. The installation record contains final formula and figure counts for each PDF.

For the complete inventory, `pdf-manifest.json` records original hashes, complete HTML sources, combined archive parts and retained historical lecture decks. `prepare_pdfs.rb` assembles the complete print documents, resolving image/link paths and retaining the contents of every constituent exam:

```sh
ruby scripts/accessibility/prepare_pdfs.rb --site /tmp/uva-a11y-final --output /tmp/uva-pdf-source
python3 -m http.server 4180 --bind 127.0.0.1 --directory /tmp/uva-pdf-source
```

Leave that local server running, then stage candidates in another terminal:

```sh
python3 scripts/accessibility/batch_export.py \
  --jobs /tmp/uva-pdf-source/jobs.json --output /tmp/uva-pdf-candidates \
  --python scripts/accessibility/.venv/bin/python --workers 3
```

This command only stages candidates. Its cache requires matching HTML and exporter hashes. Errors retain logs and prevent a success receipt. Empty table values use a dash in the reflowed print version so the browser does not drop their cells from the PDF structure tree.

`tag_artwork.py` preserves the visible contents of a reviewed one-page illustration and tags the page as one described Figure. It is used only for the two poster-template artwork assets; it is not a way to tag ordinary document pages as images.

After content, visual and validation review, check the entire catalog before installing:

```sh
python3 scripts/accessibility/install_pdfs.py \
  --jobs /tmp/uva-pdf-source/jobs.json --candidates /tmp/uva-pdf-candidates \
  --report /tmp/uva-pdf-install-review.json
```

Add `--write` to install reviewed candidates. The installer verifies every source against the inventory's original hash and every document against its current receipt and validation report before copying any PDF. It leaves historical originals unchanged. The manifest is the September 2026 baseline; a later document revision requires an updated inventory and renewed review, not bypassing a hash failure.

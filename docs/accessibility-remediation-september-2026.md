# UVA Mathematics accessibility remediation — September 2026

Implementation record for `UVA Math Website Accessibility Review September 2026.docx` in Downloads. All 24 embedded review screenshots were extracted and visually inspected. Changes apply to shared components and the public content inventory, including pages beyond the examples in the review.

## Scope and implementation

- Shared navigation, header, footer, page layouts and sidebars: visible focus, responsive navigation, correct landmarks and headings, readable supporting text, sufficient theme contrast, descriptive links, consistent social-link order and same-tab navigation.
- Home/news carousel: visible controls with generous targets, stop on hover and keyboard focus, reduced-motion handling, and inactive slides excluded from keyboard and assistive-technology navigation. News snippets expose one meaningful destination link.
- Local search and complete sitemap: content search includes department pages, people, news and document text; empty-result feedback and query handling are accessible. The error page offers useful routes back into the site.
- People, arXiv tracker, seminar calendars and archives: persistent labels, announced filter results, native disclosures, safe external calendar descriptions, visible loading/failure states and keyboard-operable controls. Fixed-width historical event tables became dated event sections. Current calendar text retains Eastern Time.
- HTML documents: common site shell with stable original `.html` URLs; preserved MathML, document headings, figure descriptions, semantic exam numbering, table captions/headers, keyboard-scrollable wide equations and tables, and printable labeled forms. Native MathML supplies mathematical structure; raw TeX labels that overrode it were removed. Malformed nested MathML tokens were repaired without changing their text.
- Schedule: a generated, searchable HTML alternative contains all 44 courses and 129 sections, independent-study entries, evening exams, semester dates and the graduate weekly grid. The existing update workflow refreshes the HTML and validates a compact three-page tagged PDF automatically; both still reject room data.
- Posters, newsletters, programs and handouts: complete HTML companions, including the 42-speaker Selie program, historical seminar abstracts, handwritten topology notes, defense posters, conference programs and the 2020 graduation program. Source images and diagrams were inspected rather than relying only on extracted PDF text. Final newsletter review corrected 26 additional image descriptions, restored Jonathan Simone's missing portrait and placed Anna Pun and Charlotte Ure's portraits in their correct profiles. Exam review restored omitted May 1978 questions and a table row. The MCLC introduction includes the recording's published English transcript.

See [the content matrix](accessibility-content-september-2026.md) for review-specific source paths and image work.

## Downloadable PDFs

The manifest inventories all 227 public PDF files, including files missed by an initial link-only crawl. The remediation covers 207 complete document companions and two standalone poster artwork assets. Reflowed document PDFs preserve their complete text, meaningful illustrations and equations; original poster layout and artwork may differ. The two artwork assets retain their original visual content.

The exporter checks every formula and meaningful image description, supplies document language and title, creates PDF structure, converts preview links to public URLs, and runs veraPDF against PDF/UA-1. Blank table values appear as dashes in print. PDF equations have spoken alternatives; HTML retains navigable MathML. Combined exam archives include every constituent exam, not merely their table of contents.

The replacement process checks all candidates and original file hashes before changing any source PDF. The final machine-readable installation record is `accessibility-pdf-results-september-2026.json`. Reproduction instructions are in `scripts/accessibility/README.md`; the complete original-file inventory is `scripts/accessibility/pdf-manifest.json`.

## Retained historical material and source limitations

- LP explicitly requested that the three Barry Simon decks remain public as historical archives. The same retention preference is applied to 15 additional historical lecture decks discovered in the full file inventory. These 18 originals total 1,929 pages and remain publicly available, with their accessibility limitations recorded in the manifest. They have not been fully remediated; retention is not a claim of accessibility or a legal exemption.
- The 1993 real-analysis exam's question 4 lacks its characteristic-function curve in both the original PDF (combined archive, page 43) and the existing image. The accessible description reports the visible axes and points. A complete original is required to recover the missing mathematical data.
- Graduation recordings and other external services remain under their owners' control. Descriptive links and the MCLC transcript address the website presentation; they do not certify every external recording, registration form or calendar service.
- Original scanned notes contain occasional tentative statements or source typos. Companions identify uncertainty or explicit transcription corrections rather than silently inventing missing mathematics.

## MRBS

Deferred separately at LP's request. **Significant, high-priority usability barriers** affect calendar/date focus, room selection, color-only booking types and login errors. Authenticated booking tasks were not covered by the original review. The source/deployment investigation and ordered fixes are recorded in [the MRBS handoff](mrbs-accessibility-september-2026.md). No MRBS server files or reservations were changed.

## Verification and release status

Local verification on September 13, 2026:

- Structural audit: 1,235 pages, zero findings. Checks cover language/titles, landmarks, heading order, links, images, lists, disclosures, form labels and native MathML.
- Browser coverage: a full 1,225-page crawl at 320px in dark mode passed with zero axe findings, horizontal page overflow or JavaScript errors. The subsequent 42 new/changed pages and five final content corrections passed at both 320px/dark and 1280px/light. Earlier desktop and focused component checks covered the shared layouts, forms, code and equation scrolling.
- Local references: 22,982 links, images, scripts and styles checked across 1,254 HTML files including redirects, with zero missing destinations or fragments. Expected Jekyll destination capitalization was checked independently for the case-sensitive server.
- Interaction fixtures: keyboard navigation, carousel pause/focus/inactive slides, filters, search feedback, arXiv validation, calendar loading/error handling and mathematical descriptions passed. Calendar date tests covered Eastern-midnight events viewed in New York, Istanbul and Honolulu.
- PDF catalog: all 207 document exports and both artwork assets passed veraPDF PDF/UA-1 validation. Document exports preserve 20,044 formula alternatives and 308 meaningful illustrations; the two artwork assets are additional. Text bounds and embedded links were checked across all 209 candidates (1,126 pages), with no text outside a page and no local-preview or filesystem links. Visual samples included dense mathematics, figures, newsletters, programs, forms and all three schedule pages.
- Schedule generation: all 129 section rows, 44 headings, 14 supplementary paragraphs and seven weekly-grid rows were checked against the printed text. The complete update helper passed in an isolated directory and produced matching current/term PDFs and the expected HTML.
- JavaScript, Python and Ruby syntax checks and `git diff --check` passed. Four regression fixtures verify that the legacy conversion helper preserves native MathML and does not reintroduce raw-TeX labels.

Reproduce rendered-page and interaction checks with the commands in `scripts/README.md`; PDF reproduction and validation are documented in `scripts/accessibility/README.md`. The installation record records original and final hashes for the complete PDF inventory.

Automated results supplement manual content and keyboard review. They do not establish blanket WCAG conformance or replace a screen-reader acceptance test on the deployed site. This work has not been committed, pushed or deployed; the live website requires release and post-deployment verification.

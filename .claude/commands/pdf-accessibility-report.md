# PDF Accessibility Report Generator

Generate a comprehensive report of PDF files on the UVA Math website that lack accessible HTML versions.

## Task Overview

1. **Build the Jekyll site** to ensure the `_site` folder is up-to-date
2. **Find all PDF links** in the generated `_site` folder
3. **Check for HTML alternatives** - for each PDF, determine if a corresponding HTML version exists (typically linked from the same page and located near the PDF file)
4. **Create a report** listing PDFs without HTML versions, grouped by parent location
5. **Save the report** to `~/downloads/pdf-accessibility-report-YYYY-MM-DD-HHMMSS.md`

## Implementation Details

### Step 1: Build the Site
Run `jekyll build` to generate the latest `_site` folder.

### Step 2: Find PDF Links
Search through all HTML files in `_site` to find:
- All `<a>` tags with `href` attributes pointing to `.pdf` files
- Extract both the PDF file path and the page that links to it

### Step 3: Check for HTML Alternatives
For each PDF found:
- Check if there's a corresponding `.html` file with a similar name in the same directory
- Check if the same page that links to the PDF also links to an HTML version
- A PDF is considered "accessible" if it has a corresponding HTML version

### Step 4: Group Results
Group PDFs without HTML versions by their parent directory/location (e.g., graduate/exams/, undergraduate/docs/, etc.)

### Step 5: Generate Report
Create a markdown report with:
- Title and generation timestamp
- Summary statistics (total PDFs found, PDFs without HTML, percentage)
- Detailed listing grouped by location
- For each PDF, include:
  - PDF filename
  - Full path
  - Pages that link to it

## Report Format

```markdown
# PDF Accessibility Report
Generated: YYYY-MM-DD HH:MM:SS

## Summary
- Total PDF files found: X
- PDFs without HTML versions: Y
- Percentage missing accessible versions: Z%

## PDFs Missing HTML Versions

### Location: /graduate/exams/
- **filename.pdf**
  - Path: /graduate/exams/filename.pdf
  - Linked from: /graduate/exams/index.html

### Location: /undergraduate/docs/
- **another.pdf**
  - Path: /undergraduate/docs/another.pdf
  - Linked from: /undergraduate/index.html, /undergraduate/docs/index.html
```

## Output Location
Save the report to: `~/downloads/pdf-accessibility-report-YYYY-MM-DD-HHMMSS.md`

## Notes
- Use appropriate tools for searching HTML content (grep, python, etc.)
- Consider that HTML versions might have slightly different names (e.g., exam.pdf → exam-accessible.html)
- Be thorough in checking for HTML alternatives before marking a PDF as "missing" accessible version

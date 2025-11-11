---
description: Extract text and images from a PDF to prepare for accessible HTML conversion
argument-hint: <path-to-pdf>
model: sonnet
---

Prepare a PDF document for conversion to accessible HTML by splitting it into individual page images that Claude can OCR.

**Task:** Split PDF into individual pages for OCR: `$ARGUMENTS`

## Instructions:

1. **Locate the PDF**:
   - Search for the PDF file in the repository using the provided path or filename
   - If just a filename is provided, search the entire repository for it
   - Common locations include: `graduate/docs/`, `undergraduate/docs/`, `img/`, etc.
   - Get the absolute path to the PDF file

2. **Check Dependencies**:
   - Verify that either `poppler-utils` or `imagemagick` is installed
   - **Option 1 - poppler-utils** (provides `pdftocairo` and `pdfinfo`):
     - Ubuntu/Debian: `sudo apt-get install poppler-utils`
     - Fedora: `sudo dnf install poppler-utils`
     - Arch: `sudo pacman -S poppler`
   - **Option 2 - imagemagick** (provides `convert` command):
     - Ubuntu/Debian: `sudo apt-get install imagemagick`
     - Fedora: `sudo dnf install ImageMagick`
     - Arch: `sudo pacman -S imagemagick`

3. **Create Page Extraction Script**:
   - Create a bash script called `split_pdf_pages.sh` in the same directory as the PDF
   - The script should:
     - Accept the PDF filename as an argument
     - Create output directory: `pdf_pages/`
     - Extract each page as a high-quality PNG image using `pdftocairo`
     - Handle the `-1` suffix that `pdftocairo` adds to single-page extractions
     - Save images as `page_1.png`, `page_2.png`, etc.

4. **Script Template**:
   ```bash
   #!/bin/bash

   if [ $# -eq 0 ]; then
       echo "Usage: $0 <pdf_file>"
       exit 1
   fi

   PDF_FILE="$1"

   if [ ! -f "$PDF_FILE" ]; then
       echo "Error: File '$PDF_FILE' not found"
       exit 1
   fi

   OUTPUT_DIR="pdf_pages"

   # Create output directory
   mkdir -p "$OUTPUT_DIR"

   # Check which tool is available
   if command -v pdftocairo &> /dev/null && command -v pdfinfo &> /dev/null; then
       # Use poppler-utils
       NUM_PAGES=$(pdfinfo "$PDF_FILE" | grep "Pages:" | awk '{print $2}')
       echo "Using pdftocairo to split $NUM_PAGES pages from $PDF_FILE..."

       for (( i=1; i<=$NUM_PAGES; i++ ))
       do
           echo "Extracting page $i of $NUM_PAGES..."
           pdftocairo -png -r 300 -f "$i" -l "$i" "$PDF_FILE" "$OUTPUT_DIR/page_$i"

           # Handle pdftocairo's -1 suffix for single page extractions
           if [ -f "$OUTPUT_DIR/page_${i}-1.png" ]; then
               mv "$OUTPUT_DIR/page_${i}-1.png" "$OUTPUT_DIR/page_${i}.png"
           fi
       done

   elif command -v convert &> /dev/null; then
       # Use ImageMagick
       echo "Using ImageMagick to split PDF: $PDF_FILE..."
       convert -density 300 "$PDF_FILE" "$OUTPUT_DIR/page_%d.png"

       # Rename files to start from page_1 instead of page_0
       for file in "$OUTPUT_DIR"/page_*.png; do
           if [ -f "$file" ]; then
               num=$(echo "$file" | grep -o '[0-9]*' | tail -1)
               new_num=$((num + 1))
               mv "$file" "$OUTPUT_DIR/page_$new_num.png"
           fi
       done

       NUM_PAGES=$(ls "$OUTPUT_DIR"/page_*.png | wc -l)
   else
       echo "Error: Neither pdftocairo nor ImageMagick convert found."
       echo "Please install poppler-utils or imagemagick."
       exit 1
   fi

   echo ""
   echo "PDF split complete!"
   echo "Page images saved to: $OUTPUT_DIR/"
   echo ""
   echo "Total pages: $NUM_PAGES"
   echo ""
   echo "Next: Use /pdf-to-html or process each page image with Claude's OCR"
   ```

5. **Execute the Script**:
   - Make the script executable with `chmod +x split_pdf_pages.sh`
   - Run the script with the PDF file as an argument
   - Monitor the output for any errors

6. **Verify Page Extraction**:
   - Check that `pdf_pages/` contains PNG images for each page
   - Count the files to ensure all pages were extracted
   - Verify image quality is sufficient for OCR

7. **Summary Report**:
   Provide a summary including:
   - PDF filename and location
   - Total number of pages extracted
   - Output directory location
   - File sizes of extracted images
   - Confirmation that pages are ready for Claude's OCR

## Notes:

- **Why Split Into Individual Pages?**:
  - Claude's OCR works best on individual page images rather than full PDFs
  - For complex mathematical content, single-page images give more accurate results
  - Allows Claude to focus on one page at a time for detailed analysis
  - More manageable chunks for processing long documents

- **Claude's Image OCR Capabilities**:
  - Claude has excellent OCR for mathematical notation when given page images
  - Can visually parse complex equations, symbols, and formulas
  - Converts mathematical content to LaTeX or MathML format
  - No external OCR services or MathML converters needed
  - Handles integrals, summations, matrices, and complex notation accurately

- **Tool Options**:
  - **pdftocairo** (from poppler-utils): Preferred for precise page-by-page extraction
  - **ImageMagick convert**: Simpler one-liner, works well for most PDFs
  - Script automatically detects and uses whichever tool is available
  - Both produce equivalent quality at 300 DPI

- **Image Quality Settings**:
  - Using 300 DPI (`-density 300` or `-r 300`) for high-quality OCR results
  - PNG format preserves quality without compression artifacts
  - Higher resolution helps with small mathematical symbols
  - Adjust DPI higher (e.g., 600) if OCR struggles with tiny text

- **Storage Considerations**:
  - PNG images at 300 DPI can be 1-3 MB per page
  - For a 78-page document, expect 100-200 MB total
  - These are temporary files and can be deleted after HTML conversion

- **Next Steps**:
  - After splitting, use `/pdf-to-html` which will:
    - Process each page image with Claude's OCR
    - Extract text and mathematical notation as LaTeX
    - Generate fully accessible HTML with semantic structure
    - Convert LaTeX to MathML for screen reader compatibility
    - Add proper ARIA labels and alt text
    - Ensure WCAG compliance for mathematical content

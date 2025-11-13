#!/usr/bin/env python3
"""
Add proper indentation to exam HTML by wrapping sub-problems in styled divs.
"""

import re
import sys

def add_indentation(html):
    """Wrap sub-problems (a), (b), etc. in divs with indentation class."""

    # Add CSS if not present
    if '.subproblem' not in html:
        css_insert = """    /* Exam problem styling */
    .problem {
      margin-bottom: 1.5em;
    }
    .problem-number {
      display: block;
      margin-top: 1.5em;
      margin-bottom: 0.5em;
    }
    .subproblem {
      margin-left: 2em;
      margin-top: 0.5em;
      display: block;
    }
  </style>"""
        html = html.replace('  </style>', css_insert)

    # Find the main content
    main_match = re.search(r'<main>(.*?)</main>', html, re.DOTALL)
    if not main_match:
        print("Warning: No <main> element found")
        return html

    content = main_match.group(1)

    # Separate instructions from problems
    content = re.sub(
        r'(<p>Instructions:.*?points\.)</p>\s*<div class="problem">\s*<p>(\(\d+\))',
        r'\1</p>\n\n<div class="problem">\n<p>\2',
        content,
        flags=re.DOTALL
    )

    # Wrap problem numbers (1), (2), etc. with spacing class
    # But not when they're at the start of the content (first problem)
    content = re.sub(
        r'<br\s*/?\>[\s\n]*(\(\d+\))',
        r'<br /><br /><span class="problem-number">\1</span>',
        content
    )

    # Wrap sub-problems (a), (b), etc. with indentation divs
    # Pattern: <br />WHITESPACE(a) or (b) or (c) followed by content until next <br /> or end
    content = re.sub(
        r'<br\s*/?\>[\s\n]*(\([a-z]\)\s+.*?)(?=<br\s*/?\>[\s\n]*(?:\([a-z]\)|\(\d+\)|$)|</p>)',
        r'<br /><span class="subproblem">\1</span>',
        content,
        flags=re.DOTALL
    )

    # Replace in original HTML
    html = html[:main_match.start(1)] + content + html[main_match.end(1):]

    return html

def main():
    if len(sys.argv) != 3:
        print("Usage: add_exam_indentation.py input.html output.html")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()

    fixed_html = add_indentation(html)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_html)

    print(f"Indentation added, written to {output_file}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Fix indentation in exam HTML files.
Restructure content to properly indent sub-problems (a), (b), etc.
"""

import re
import sys
from bs4 import BeautifulSoup

def fix_indentation(html):
    """Add proper indentation structure to exam problems."""
    soup = BeautifulSoup(html, 'html.parser')

    # Find the main content area
    main = soup.find('main')
    if not main:
        print("Warning: No <main> element found")
        return html

    # Find all paragraphs in main
    paragraphs = main.find_all('p', recursive=False)

    for p in paragraphs:
        # Get the HTML content
        content = str(p)

        # Check if this paragraph contains numbered problems
        if re.search(r'<br\s*/?>[\s\n]*\(\d+\)', content):
            # Split by problem numbers
            problems = re.split(r'(<br\s*/?>[\s\n]*\(\d+\))', content)

            # Reconstruct with proper structure
            new_html = problems[0]  # Keep initial content (instructions)

            i = 1
            while i < len(problems):
                if re.match(r'<br\s*/?>[\s\n]*\(\d+\)', problems[i]):
                    # This is a problem number marker
                    problem_start = problems[i]
                    if i + 1 < len(problems):
                        problem_content = problems[i + 1]

                        # Split sub-problems (a), (b), etc.
                        subparts = re.split(r'(<br\s*/?>[\s\n]*\([a-z]\))', problem_content)

                        # Problem main part (before first sub-problem)
                        new_html += '</p><div class="problem">' + problem_start[len('<br />'):].strip()
                        if subparts[0].strip():
                            new_html += subparts[0]

                        # Sub-problems
                        j = 1
                        while j < len(subparts):
                            if re.match(r'<br\s*/?>[\s\n]*\([a-z]\)', subparts[j]):
                                subproblem_marker = subparts[j]
                                if j + 1 < len(subparts):
                                    subproblem_content = subparts[j + 1]
                                    new_html += '<div class="subproblem">' + subproblem_marker[len('<br />'):].strip() + subproblem_content.rstrip() + '</div>'
                                j += 2
                            else:
                                j += 1

                        new_html += '</div><p>'
                    i += 2
                else:
                    i += 1

            new_html += '</p>'

            # Replace the original paragraph
            new_p = BeautifulSoup(new_html, 'html.parser')
            p.replace_with(new_p)

    return str(soup)

def main():
    if len(sys.argv) != 3:
        print("Usage: fix_exam_indentation.py input.html output.html")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()

    fixed_html = fix_indentation(html)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_html)

    print(f"Fixed indentation written to {output_file}")

if __name__ == '__main__':
    main()

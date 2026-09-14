#!/usr/bin/env python3
"""
Post-process standalone exam HTML while preserving native MathML.
- Preserve mathematical Unicode and structured math semantics
- Remove legacy raw-TeX labels that override MathML
- Apply the legacy exam heading, navigation, and landmark helpers
"""

import re
import sys
from html import unescape

# Legacy serialization helper; Unicode is valid MathML and needs no replacement.
UNICODE_TO_ENTITY = {
    '∞': '&infin;',
    '→': '&rarr;',
    '←': '&larr;',
    '↔': '&harr;',
    '⇒': '&rArr;',
    '⇐': '&lArr;',
    '⇔': '&hArr;',
    '∈': '&isin;',
    '∉': '&notin;',
    '∋': '&ni;',
    '⊂': '&sub;',
    '⊃': '&sup;',
    '⊆': '&sube;',
    '⊇': '&supe;',
    '∪': '&cup;',
    '∩': '&cap;',
    '∖': '&setminus;',
    '×': '&times;',
    '⋅': '&sdot;',
    '±': '&plusmn;',
    '∓': '&mp;',
    '≤': '&le;',
    '≥': '&ge;',
    '≠': '&ne;',
    '≈': '&approx;',
    '≡': '&equiv;',
    '⟂': '&perp;',
    '∥': '&parallel;',
    '∠': '&ang;',
    '∇': '&nabla;',
    '∂': '&part;',
    '∫': '&int;',
    '∮': '&conint;',
    '∑': '&sum;',
    '∏': '&prod;',
    '√': '&radic;',
    '∀': '&forall;',
    '∃': '&exist;',
    '∄': '&nexist;',
    '¬': '&not;',
    '∧': '&and;',
    '∨': '&or;',
    '⊕': '&oplus;',
    '⊗': '&otimes;',
    '∅': '&empty;',
    'ℝ': '&Ropf;',
    'ℂ': '&Copf;',
    'ℕ': '&Nopf;',
    'ℤ': '&Zopf;',
    'ℚ': '&Qopf;',
    'α': '&alpha;',
    'β': '&beta;',
    'γ': '&gamma;',
    'δ': '&delta;',
    'ε': '&epsilon;',
    'ζ': '&zeta;',
    'η': '&eta;',
    'θ': '&theta;',
    'ι': '&iota;',
    'κ': '&kappa;',
    'λ': '&lambda;',
    'μ': '&mu;',
    'ν': '&nu;',
    'ξ': '&xi;',
    'π': '&pi;',
    'ρ': '&rho;',
    'σ': '&sigma;',
    'τ': '&tau;',
    'υ': '&upsilon;',
    'φ': '&phi;',
    'χ': '&chi;',
    'ψ': '&psi;',
    'ω': '&omega;',
    'Α': '&Alpha;',
    'Β': '&Beta;',
    'Γ': '&Gamma;',
    'Δ': '&Delta;',
    'Ε': '&Epsilon;',
    'Ζ': '&Zeta;',
    'Η': '&Eta;',
    'Θ': '&Theta;',
    'Ι': '&Iota;',
    'Κ': '&Kappa;',
    'Λ': '&Lambda;',
    'Μ': '&Mu;',
    'Ν': '&Nu;',
    'Ξ': '&Xi;',
    'Π': '&Pi;',
    'Ρ': '&Rho;',
    'Σ': '&Sigma;',
    'Τ': '&Tau;',
    'Υ': '&Upsilon;',
    'Φ': '&Phi;',
    'Χ': '&Chi;',
    'Ψ': '&Psi;',
    'Ω': '&Omega;',
    '↦': '&map;',
    '∘': '&SmallCircle;',
    '⊆': '&sube;',
}

def replace_unicode_with_entities(text):
    """Replace Unicode math characters with HTML/MathML entities."""
    for unicode_char, entity in UNICODE_TO_ENTITY.items():
        text = text.replace(unicode_char, entity)
    return text

def fix_heading_hierarchy(html):
    """Fix heading hierarchy: first H1 stays, rest become H2."""
    lines = html.split('\n')
    h1_count = 0
    result = []

    for line in lines:
        if '<h1' in line:
            if h1_count == 0:
                # Keep first H1 (main title)
                result.append(line)
                h1_count += 1
            else:
                # Convert subsequent H1s to H2
                line = line.replace('<h1', '<h2').replace('</h1>', '</h2>')
                result.append(line)
        else:
            result.append(line)

    return '\n'.join(result)

def preserve_native_mathml(html):
    """Remove labels copied from TeX; retain MathML and authored speech labels."""
    def remove_tex_label(match):
        attributes = match.group('attributes')
        body = match.group('body')
        annotation = re.search(
            r"<annotation\b[^>]*\bencoding\s*=\s*['\"]application/x-tex['\"][^>]*>(.*?)</annotation\s*>",
            body, re.DOTALL | re.IGNORECASE
        )
        if not annotation:
            return match.group(0)

        def normalized(value):
            return re.sub(r'\s+', ' ', unescape(value)).strip()

        source = normalized(annotation.group(1))
        if not source:
            return match.group(0)

        def keep_authored_label(label):
            return '' if normalized(label.group('value')) == source else label.group(0)

        attributes = re.sub(
            r"\s+aria-label\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
            keep_authored_label, attributes, flags=re.DOTALL | re.IGNORECASE
        )
        return '<math' + attributes + '>' + body + '</math>'

    return re.sub(
        r"<math\b(?P<attributes>(?:[^>\"']|\"[^\"]*\"|'[^']*')*)>(?P<body>.*?)</math\s*>",
        remove_tex_label, html, flags=re.DOTALL | re.IGNORECASE
    )

def add_lang_attribute(html):
    """Add lang='en' attribute to <html> element."""
    # First, remove any empty or existing lang attributes
    html = re.sub(r'\s+lang=""', '', html)
    html = re.sub(r'\s+lang="[^"]*"', '', html)
    # Then add lang="en" to the html tag
    html = re.sub(
        r'<html([^>]*)>',
        r'<html lang="en"\1>',
        html
    )
    return html

def improve_title(html):
    """Extract title from H1 and set as page title."""
    # Extract text from first H1
    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    if h1_match:
        h1_text = h1_match.group(1).strip()
        # Replace the title
        html = re.sub(
            r'<title>[^<]*</title>',
            f'<title>{h1_text} - UVA Mathematics</title>',
            html
        )
    return html

def add_breadcrumb_navigation(html):
    """Add breadcrumb navigation at the top of the page."""
    # Extract the title from H1 for the current page breadcrumb
    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    current_page_title = h1_match.group(1).strip() if h1_match else "Current Exam"

    breadcrumb_html = '''<nav aria-label="Breadcrumb" style="margin-bottom: 1em;">
  <ol style="list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 0.5em; font-size: 0.9em;">
    <li><a href="/">Home</a></li>
    <li aria-hidden="true" style="color: #999;">/</li>
    <li><a href="/graduate/">Graduate</a></li>
    <li aria-hidden="true" style="color: #999;">/</li>
    <li><a href="/graduate/generals/">General Exams</a></li>
    <li aria-hidden="true" style="color: #999;">/</li>
    <li aria-current="page" style="color: #666;">''' + current_page_title + '''</li>
  </ol>
</nav>

'''

    # Insert after <body> tag
    html = html.replace('<body>', '<body>\n' + breadcrumb_html)
    return html

def add_back_button(html):
    """Add a back button navigation below breadcrumb."""
    back_button_html = '''<nav aria-label="Page navigation" style="margin-bottom: 2em;">
  <a href="/graduate/generals/" style="display: inline-block; padding: 0.5em 1em; background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 4px; text-decoration: none; color: #333;">&larr; Back to General Exams</a>
</nav>

'''

    # Insert after first </nav> (breadcrumb) before <main>
    # First, find the position of the first </nav>
    nav_close = html.find('</nav>')
    if nav_close != -1:
        # Find where to insert (after </nav> and any whitespace, before <main> or <h1>)
        insert_pos = nav_close + len('</nav>')
        # Skip any whitespace
        while insert_pos < len(html) and html[insert_pos] in '\n ':
            insert_pos += 1
        # Insert the back button
        html = html[:insert_pos] + '\n' + back_button_html + html[insert_pos:]

    return html

def wrap_content_in_main(html):
    """Wrap main content in <main> landmark element."""
    # Find the first H1 (start of main content)
    h1_match = re.search(r'(<h1[^>]*>.*?</h1>)', html, re.DOTALL)
    if h1_match:
        # Insert <main> before the H1
        html = html.replace(h1_match.group(1), '<main>\n' + h1_match.group(1))

        # Insert </main> before </body>
        html = html.replace('</body>', '</main>\n</body>')

    return html

def add_exam_spacing(html):
    """Add proper spacing between exam problems."""

    # Add CSS if not present
    if '.problem-number' not in html:
        css_insert = """    /* Exam problem styling */
    .problem-number {
      display: block;
      margin-top: 1.5em;
      margin-bottom: 0.5em;
    }
  </style>"""
        html = html.replace('  </style>', css_insert)

    # Try to find content in <main>, otherwise work on <body>
    main_match = re.search(r'<main>(.*?)</main>', html, re.DOTALL)
    if main_match:
        content = main_match.group(1)
        start_pos = main_match.start(1)
        end_pos = main_match.end(1)
    else:
        # No main element, work on body content
        body_match = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
        if not body_match:
            return html
        content = body_match.group(1)
        start_pos = body_match.start(1)
        end_pos = body_match.end(1)

    # Add spacing between problem numbers (2), (3), etc.
    # Add double line breaks before numbered problems
    content = re.sub(
        r'<br\s*/?\>[\s\n]*(\(\d+\))',
        r'<br /><br /><span class="problem-number">\1</span>',
        content
    )

    # Replace in original HTML
    html = html[:start_pos] + content + html[end_pos:]

    return html

def main():
    if len(sys.argv) != 3:
        print("Usage: fix_mathml.py input.html output.html")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Apply fixes
    html = fix_heading_hierarchy(html)
    html = preserve_native_mathml(html)
    html = add_lang_attribute(html)
    html = improve_title(html)
    html = add_breadcrumb_navigation(html)
    html = add_back_button(html)
    html = wrap_content_in_main(html)
    html = add_exam_spacing(html)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Fixed HTML written to {output_file}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Validate MathML structure and accessibility.
Checks for proper MathML elements, ARIA attributes, and semantics.
"""

import sys
import re
from html import unescape

def check_mathml(filepath):
    """
    Check MathML structure and accessibility.
    Returns: (passed: bool, issues: list, warnings: list, stats: dict)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = []
    warnings = []
    stats = {
        'total_math': 0,
        'with_role': 0,
        'with_aria_label': 0,
        'with_semantics': 0,
        'with_annotation': 0,
        'inline': 0,
        'block': 0
    }

    # Find all math elements using regex
    math_pattern = r'<math[^>]*>(.*?)</math>'
    math_elements = re.finditer(math_pattern, content, re.DOTALL | re.IGNORECASE)

    math_list = list(re.finditer(math_pattern, content, re.DOTALL | re.IGNORECASE))
    stats['total_math'] = len(math_list)

    if stats['total_math'] == 0:
        warnings.append("No math elements found (this may be expected)")
        return (True, issues, warnings, stats)

    for i, math_match in enumerate(math_list, 1):
        math_tag = math_match.group(0)
        math_content = math_match.group(1)

        # Native MathML has implicit math semantics; an explicit role is optional.
        if re.search(r'role="math"', math_tag):
            stats['with_role'] += 1
        # A raw TeX label must not override the structured mathematical content.
        if re.search(r'aria-label="[^"]+"', math_tag):
            stats['with_aria_label'] += 1
        label = re.search(r'aria-label="([^"]+)"', math_tag)
        annotation = re.search(r'<annotation[^>]+encoding="application/x-tex"[^>]*>(.*?)</annotation>', math_content, re.DOTALL)
        if label and annotation and unescape(label.group(1)).strip() == unescape(annotation.group(1)).strip():
            issues.append(f"Math element #{i} has a raw TeX label overriding MathML")

        # Check 3: xmlns namespace
        if 'xmlns' not in math_tag:
            warnings.append(f"Math element #{i} missing xmlns namespace")

        # Check 4: display attribute
        display_match = re.search(r'display="(inline|block)"', math_tag)
        if display_match:
            if display_match.group(1) == 'inline':
                stats['inline'] += 1
            elif display_match.group(1) == 'block':
                stats['block'] += 1
        else:
            stats['inline'] += 1  # Default is inline

        # Check 5: <semantics> wrapper
        if '<semantics' in math_content:
            stats['with_semantics'] += 1
        else:
            warnings.append(f"Math element #{i} missing <semantics> wrapper")

        # Check 6: <annotation> with LaTeX
        if re.search(r'<annotation[^>]+encoding="application/x-tex"', math_content):
            stats['with_annotation'] += 1
        else:
            warnings.append(f"Math element #{i} missing LaTeX annotation")

    return (len(issues) == 0, issues, warnings, stats)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_mathml.py <html_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    passed, issues, warnings, stats = check_mathml(filepath)

    # Print statistics
    print(f"\nMathML Statistics for {filepath}:")
    print(f"  Total math elements: {stats['total_math']}")
    if stats['total_math'] > 0:
        print(f"  With role=\"math\": {stats['with_role']}/{stats['total_math']}")
        print(f"  With aria-label: {stats['with_aria_label']}/{stats['total_math']}")
        print(f"  With <semantics>: {stats['with_semantics']}/{stats['total_math']}")
        print(f"  With LaTeX annotation: {stats['with_annotation']}/{stats['total_math']}")
        print(f"  Display mode: {stats['inline']} inline, {stats['block']} block")
    print()

    # Print results
    if passed:
        print(f"✅ {filepath}: MathML PASS")
        if warnings:
            print("\n⚠️  Warnings (non-critical):")
            for warning in warnings:
                print(f"  - {warning}")
        return 0
    else:
        print(f"❌ {filepath}: MathML FAIL")
        for issue in issues:
            print(f"  - {issue}")
        if warnings:
            print("\n⚠️  Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

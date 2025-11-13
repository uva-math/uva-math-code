#!/usr/bin/env python3
"""
Validate MathML structure and accessibility.
Checks for proper MathML elements, ARIA attributes, and semantics.
"""

import sys
import re
from bs4 import BeautifulSoup

def check_mathml(filepath):
    """
    Check MathML structure and accessibility.
    Returns: (passed: bool, issues: list, warnings: list, stats: dict)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

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

    # Find all math elements
    math_elements = soup.find_all('math')
    stats['total_math'] = len(math_elements)

    if stats['total_math'] == 0:
        warnings.append("No math elements found (this may be expected)")
        return (True, issues, warnings, stats)

    for i, math in enumerate(math_elements, 1):
        # Check 1: role="math"
        if math.get('role') == 'math':
            stats['with_role'] += 1
        else:
            issues.append(f"Math element #{i} missing role=\"math\"")

        # Check 2: aria-label with LaTeX
        if math.get('aria-label'):
            stats['with_aria_label'] += 1
        else:
            issues.append(f"Math element #{i} missing aria-label")

        # Check 3: xmlns namespace
        if 'xmlns' not in math.attrs:
            warnings.append(f"Math element #{i} missing xmlns namespace")

        # Check 4: display attribute
        display = math.get('display', 'inline')
        if display == 'inline':
            stats['inline'] += 1
        elif display == 'block':
            stats['block'] += 1

        # Check 5: <semantics> wrapper
        if math.find('semantics'):
            stats['with_semantics'] += 1
        else:
            warnings.append(f"Math element #{i} missing <semantics> wrapper")

        # Check 6: <annotation> with LaTeX
        annotation = math.find('annotation', {'encoding': 'application/x-tex'})
        if annotation:
            stats['with_annotation'] += 1
        else:
            warnings.append(f"Math element #{i} missing LaTeX annotation")

    # Summary checks
    if stats['with_role'] < stats['total_math']:
        issues.append(
            f"{stats['total_math'] - stats['with_role']}/{stats['total_math']} "
            "math elements missing role=\"math\""
        )

    if stats['with_aria_label'] < stats['total_math']:
        issues.append(
            f"{stats['total_math'] - stats['with_aria_label']}/{stats['total_math']} "
            "math elements missing aria-label"
        )

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

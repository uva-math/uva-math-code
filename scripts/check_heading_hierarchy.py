#!/usr/bin/env python3
"""
Check heading hierarchy in HTML files.
Ensures proper H1/H2/H3 structure for WCAG 2.1 Level AA compliance.
"""

import sys
import re

def check_heading_hierarchy(filepath):
    """
    Check heading hierarchy in an HTML file.
    Returns: (passed: bool, issues: list)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = []

    # Extract all headings with their levels using regex
    heading_pattern = r'<h([1-6])([^>]*)>(.*?)</h\1>'
    heading_matches = re.finditer(heading_pattern, content, re.DOTALL | re.IGNORECASE)

    headings = []
    for match in heading_matches:
        level = int(match.group(1))
        attributes = match.group(2)
        text = re.sub(r'<[^>]+>', '', match.group(3)).strip()  # Remove HTML tags

        # Extract id from attributes
        id_match = re.search(r'id="([^"]*)"', attributes)
        id_attr = id_match.group(1) if id_match else ''

        headings.append({
            'level': level,
            'text': text,
            'id': id_attr
        })

    if not headings:
        issues.append("No headings found in document")
        return (False, issues)

    # Check 1: Exactly one H1
    h1_count = sum(1 for h in headings if h['level'] == 1)
    if h1_count == 0:
        issues.append("No H1 heading found (must have exactly one)")
    elif h1_count > 1:
        issues.append(f"Multiple H1 headings found ({h1_count}), must have exactly one")

    # Check 2: No skipped levels
    for i in range(1, len(headings)):
        prev_level = headings[i-1]['level']
        curr_level = headings[i]['level']

        # Heading level can only increase by 1
        if curr_level > prev_level + 1:
            issues.append(
                f"Skipped heading level: H{prev_level} → H{curr_level} "
                f"('{headings[i-1]['text'][:50]}' → '{headings[i]['text'][:50]}')"
            )

    # Check 3: All headings have IDs
    headings_without_ids = [h for h in headings if not h['id']]
    if headings_without_ids:
        issues.append(f"{len(headings_without_ids)} headings without id attributes")
        for h in headings_without_ids[:3]:  # Show first 3
            issues.append(f"  Missing id: H{h['level']}: '{h['text'][:50]}'")

    # Check 4: Duplicate IDs
    ids = [h['id'] for h in headings if h['id']]
    duplicate_ids = set([id for id in ids if ids.count(id) > 1])
    if duplicate_ids:
        issues.append(f"Duplicate heading IDs: {duplicate_ids}")

    return (len(issues) == 0, issues)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_heading_hierarchy.py <html_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    passed, issues = check_heading_hierarchy(filepath)

    if passed:
        print(f"✅ {filepath}: Heading hierarchy PASS")
        return 0
    else:
        print(f"❌ {filepath}: Heading hierarchy FAIL")
        for issue in issues:
            print(f"  - {issue}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

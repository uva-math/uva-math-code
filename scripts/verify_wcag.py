#!/usr/bin/env python3
"""
Legacy structural checks for rendered HTML documents.
Use audit_accessibility.rb and audit_browser.cjs for the current site checks.
This script does not certify WCAG conformance.
"""

import os
import re
import sys

def check_unicode_violations(filepath):
    """Check for Unicode mathematical characters (U+1D400-U+1D7FF)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(r'[\U0001D400-\U0001D7FF]', content)
        return matches

def check_h1_tag(filepath):
    """Check for H1 tag."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        return '<h1' in content

def check_main_landmark(filepath):
    """Check for <main> landmark."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        return '<main' in content

def check_mathml_role(filepath):
    """Check if all <math> tags have role='math'."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        math_tags = len(re.findall(r'<math[^>]*>', content))
        role_math = len(re.findall(r'role="math"', content))
        return (math_tags, role_math, math_tags == role_math or math_tags == 0)

def check_breadcrumb(filepath):
    """Check for breadcrumb navigation."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        return 'aria-label="Breadcrumb"' in content

def verify_file(filepath, verbose=True):
    """
    Run limited structural checks on one rendered file.
    Returns: (passed: bool, violations: list)
    """
    violations = []

    # Mathematical Unicode inside native MathML is valid. Neither an explicit
    # math role nor breadcrumb navigation is a universal accessibility requirement.

    # Check 2: H1 tag
    if not check_h1_tag(filepath):
        violations.append("Missing H1 tag")

    # Check 3: <main> landmark
    if not check_main_landmark(filepath):
        violations.append("Missing <main> landmark")

    return (len(violations) == 0, violations)

def verify_directory(directory, verbose=True):
    """Verify all HTML files in a directory."""
    html_files = [f for f in os.listdir(directory) if f.endswith('.html')]

    if not html_files:
        return (True, 0, 0, [])

    passed_files = 0
    failed_files = 0
    all_violations = {}

    for filename in sorted(html_files):
        filepath = os.path.join(directory, filename)
        passed, violations = verify_file(filepath, verbose=verbose)

        if passed:
            passed_files += 1
        else:
            failed_files += 1
            all_violations[filename] = violations

    return (failed_files == 0, passed_files, failed_files, all_violations)

def main():
    """Main entry point for standalone verification."""
    import argparse

    parser = argparse.ArgumentParser(description='Run limited structure checks on rendered HTML files')
    parser.add_argument('path', nargs='?', help='File or directory to check')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')
    args = parser.parse_args()

    if args.path:
        # Check specific file or directory
        if os.path.isfile(args.path):
            passed, violations = verify_file(args.path, verbose=not args.quiet)
            if passed:
                print(f"✅ {args.path}: PASS")
                return 0
            else:
                print(f"❌ {args.path}: FAIL")
                for v in violations:
                    print(f"  - {v}")
                return 1
        elif os.path.isdir(args.path):
            passed, passed_count, failed_count, violations = verify_directory(args.path, verbose=not args.quiet)
            if passed:
                print(f"✅ All {passed_count} files PASS")
                return 0
            else:
                print(f"❌ {failed_count} files FAIL, {passed_count} files PASS")
                for filename, file_violations in violations.items():
                    print(f"\n{filename}:")
                    for v in file_violations:
                        print(f"  - {v}")
                return 1
    else:
        # Check all exam directories
        exam_dirs = [
            'graduate/exams/algebra',
            'graduate/exams/analysis',
            'graduate/exams/topology'
        ]

        total_passed = 0
        total_failed = 0
        all_violations = {}

        for directory in exam_dirs:
            if not os.path.exists(directory):
                continue

            passed, passed_count, failed_count, violations = verify_directory(directory, verbose=not args.quiet)
            total_passed += passed_count
            total_failed += failed_count

            if violations:
                for filename, file_violations in violations.items():
                    all_violations[f"{directory}/{filename}"] = file_violations

        print("=" * 80)
        print("HTML STRUCTURE CHECKS (NOT A WCAG CERTIFICATION)")
        print("=" * 80)
        print()
        print(f"Total files checked: {total_passed + total_failed}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_failed}")
        print()

        if all_violations:
            print("VIOLATIONS:")
            print()
            for filepath, violations in sorted(all_violations.items()):
                print(f"{filepath}:")
                for v in violations:
                    print(f"  - {v}")
                print()
            return 1
        else:
            print("All implemented structural checks passed.")
            print("Manual accessibility and assistive-technology testing is still required.")
            return 0

if __name__ == '__main__':
    sys.exit(main())

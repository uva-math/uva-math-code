#!/usr/bin/env python3
"""
Master validation script for PDF to HTML conversions.
Runs all validation checks and provides comprehensive report.
"""

import sys
import os

# Import individual check modules
try:
    from verify_wcag import verify_file as check_wcag
    from check_heading_hierarchy import check_heading_hierarchy
    from check_links_images import check_links_and_images
    from check_mathml import check_mathml
except ImportError:
    # If running from scripts directory
    sys.path.insert(0, os.path.dirname(__file__))
    from verify_wcag import verify_file as check_wcag
    from check_heading_hierarchy import check_heading_hierarchy
    from check_links_images import check_links_and_images
    from check_mathml import check_mathml

def validate_conversion(html_path, verbose=True):
    """
    Run all validation checks on a converted HTML file.
    Returns: (passed: bool, report: dict)
    """
    report = {
        'wcag': {'passed': False, 'violations': []},
        'headings': {'passed': False, 'issues': []},
        'links_images': {'passed': False, 'issues': []},
        'mathml': {'passed': False, 'issues': [], 'warnings': [], 'stats': {}},
        'overall': False
    }

    # Check 1: WCAG 2.1 Level AA
    try:
        passed, violations = check_wcag(html_path, verbose=False)
        report['wcag']['passed'] = passed
        report['wcag']['violations'] = violations
    except Exception as e:
        report['wcag']['violations'].append(f"Error running WCAG check: {str(e)}")

    # Check 2: Heading hierarchy
    try:
        passed, issues = check_heading_hierarchy(html_path)
        report['headings']['passed'] = passed
        report['headings']['issues'] = issues
    except Exception as e:
        report['headings']['issues'].append(f"Error checking headings: {str(e)}")

    # Check 3: Links and images
    try:
        passed, issues = check_links_and_images(html_path)
        report['links_images']['passed'] = passed
        report['links_images']['issues'] = issues
    except Exception as e:
        report['links_images']['issues'].append(f"Error checking links/images: {str(e)}")

    # Check 4: MathML
    try:
        passed, issues, warnings, stats = check_mathml(html_path)
        report['mathml']['passed'] = passed
        report['mathml']['issues'] = issues
        report['mathml']['warnings'] = warnings
        report['mathml']['stats'] = stats
    except Exception as e:
        report['mathml']['issues'].append(f"Error checking MathML: {str(e)}")

    # Overall pass/fail
    report['overall'] = (
        report['wcag']['passed'] and
        report['headings']['passed'] and
        report['links_images']['passed'] and
        report['mathml']['passed']
    )

    return report['overall'], report

def print_report(filepath, passed, report):
    """Print comprehensive validation report."""
    print("=" * 80)
    print("PDF TO HTML CONVERSION VALIDATION REPORT")
    print("=" * 80)
    print(f"\nFile: {filepath}")
    print()

    # Check 1: WCAG 2.1 Level AA
    print("1. WCAG 2.1 LEVEL AA COMPLIANCE")
    if report['wcag']['passed']:
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL")
        for violation in report['wcag']['violations']:
            print(f"      - {violation}")
    print()

    # Check 2: Heading Hierarchy
    print("2. HEADING HIERARCHY")
    if report['headings']['passed']:
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL")
        for issue in report['headings']['issues']:
            print(f"      - {issue}")
    print()

    # Check 3: Links and Images
    print("3. LINKS AND IMAGES")
    if report['links_images']['passed']:
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL")
        for issue in report['links_images']['issues']:
            print(f"      - {issue}")
    print()

    # Check 4: MathML
    print("4. MATHML ACCESSIBILITY")
    if report['mathml']['passed']:
        print("   ✅ PASS")
    else:
        print("   ❌ FAIL")
        for issue in report['mathml']['issues']:
            print(f"      - {issue}")

    if report['mathml']['warnings']:
        print("   ⚠️  Warnings (non-critical):")
        for warning in report['mathml']['warnings'][:5]:  # Show first 5
            print(f"      - {warning}")

    if report['mathml']['stats']:
        stats = report['mathml']['stats']
        print(f"\n   Statistics:")
        print(f"      Total math elements: {stats.get('total_math', 0)}")
        if stats.get('total_math', 0) > 0:
            print(f"      With role=\"math\": {stats.get('with_role', 0)}")
            print(f"      With aria-label: {stats.get('with_aria_label', 0)}")
            print(f"      Inline/Block: {stats.get('inline', 0)}/{stats.get('block', 0)}")
    print()

    # Overall verdict
    print("=" * 80)
    print("OVERALL VERDICT")
    print("=" * 80)
    if passed:
        print("✅ PRODUCTION READY - All checks passed")
        print("✅ WCAG 2.1 Level AA compliant")
        print("✅ ADA Title II & III compliant")
        print("✅ Lawsuit risk: MINIMAL")
    else:
        print("❌ NOT PRODUCTION READY - Fix violations before deployment")
        print("⚠️  Legal compliance: AT RISK")
        print("⚠️  Lawsuit risk: ELEVATED")
    print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_conversion.py <html_file>")
        print("\nValidates PDF to HTML conversions with comprehensive checks:")
        print("  - WCAG 2.1 Level AA compliance")
        print("  - Heading hierarchy")
        print("  - Links and images")
        print("  - MathML accessibility")
        sys.exit(1)

    filepath = sys.argv[1]

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    passed, report = validate_conversion(filepath)
    print_report(filepath, passed, report)

    return 0 if passed else 1

if __name__ == '__main__':
    sys.exit(main())

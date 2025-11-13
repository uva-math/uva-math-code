#!/usr/bin/env python3
"""
Fix Unicode violations in graduate exam HTML files.
Converts raw Unicode mathematical characters to HTML entities for WCAG 2.1 Level AA compliance.
"""

import os
import re
import shutil
from datetime import datetime

# Unicode to HTML entity mapping
UNICODE_FIXES = {
    '𝔻': '&Dopf;',      # U+1D53B - Blackboard bold D
    '𝔽': '&Fopf;',      # U+1D53D - Blackboard bold F
    '𝒜': '&Ascr;',      # U+1D49C - Script A
    '𝐑': '&Rfr;',       # U+1D411 - Bold R (should use &Ropf; if blackboard bold)
    '𝒞': '&Cscr;',      # U+1D49E - Script C
    '𝔛': '&Xfr;',       # U+1D51B - Fraktur X
    '𝔜': '&Yfr;',       # U+1D51C - Fraktur Y
    '𝕋': '&Topf;',      # U+1D54B - Blackboard bold T
    '𝒢': '&Gscr;',      # U+1D4A2 - Script G
    '𝐊': '&Kfr;',       # U+1D40A - Bold K
    '𝔞': '&afr;',       # U+1D51E - Fraktur lowercase a
}

FILES_TO_FIX = [
    'graduate/exams/algebra/2021-08.html',
    'graduate/exams/algebra/2022-01.html',
    'graduate/exams/algebra/2022-08.html',
    'graduate/exams/algebra/2023-08.html',
    'graduate/exams/algebra/2024-01.html',
    'graduate/exams/algebra/2024-08.html',
]

def fix_file(filepath, dry_run=False):
    """Fix Unicode violations in a single file."""

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False

    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    fixes_applied = {}

    # Apply each fix
    for unicode_char, html_entity in UNICODE_FIXES.items():
        count = content.count(unicode_char)
        if count > 0:
            content = content.replace(unicode_char, html_entity)
            fixes_applied[unicode_char] = count

    # Check if any changes were made
    if content == original_content:
        print(f"✅ {os.path.basename(filepath)}: No violations found")
        return True

    if dry_run:
        print(f"🔍 {os.path.basename(filepath)}: Would fix {sum(fixes_applied.values())} violations:")
        for char, count in fixes_applied.items():
            entity = UNICODE_FIXES[char]
            print(f"    {char} → {entity} ({count}x)")
        return True

    # Skip backup - files are in git
    # backup_path = filepath + '.backup-' + datetime.now().strftime('%Y%m%d-%H%M%S')
    # shutil.copy2(filepath, backup_path)

    # Write fixed content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ {os.path.basename(filepath)}: Fixed {sum(fixes_applied.values())} violations:")
    for char, count in fixes_applied.items():
        entity = UNICODE_FIXES[char]
        print(f"    {char} → {entity} ({count}x)")

    return True

def main():
    """Main execution."""

    print("=" * 80)
    print("WCAG 2.1 Level AA Unicode Violation Fix Script")
    print("=" * 80)
    print()

    # Get repository root
    repo_root = '/Users/leo/uva-math-code'
    os.chdir(repo_root)

    print(f"📁 Working directory: {os.getcwd()}")
    print(f"📋 Files to process: {len(FILES_TO_FIX)}")
    print()

    # Process all files
    success_count = 0
    fail_count = 0

    for filepath in FILES_TO_FIX:
        if fix_file(filepath):
            success_count += 1
        else:
            fail_count += 1

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully processed: {success_count}/{len(FILES_TO_FIX)}")
    if fail_count > 0:
        print(f"❌ Failed: {fail_count}/{len(FILES_TO_FIX)}")
    print()
    print("🔍 To verify fixes, run:")
    print("    python3 scripts/verify_wcag.py")
    print()

if __name__ == '__main__':
    main()

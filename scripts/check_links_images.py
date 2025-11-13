#!/usr/bin/env python3
"""
Check for broken internal links and image references.
Validates all href and src attributes for local resources.
"""

import sys
import os
import re

def check_links_and_images(filepath):
    """
    Check all internal links and image references.
    Returns: (passed: bool, issues: list)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    basedir = os.path.dirname(os.path.abspath(filepath))
    issues = []

    # Check 1: Internal anchor links
    # Find all anchor links with href="#..."
    anchor_pattern = r'<a[^>]+href="#([^"]+)"[^>]*>'
    anchor_links = re.findall(anchor_pattern, content, re.IGNORECASE)

    # Find all IDs in document
    id_pattern = r'\bid="([^"]+)"'
    all_ids = set(re.findall(id_pattern, content))

    # Check for broken anchor links
    broken_anchors = [link for link in anchor_links if link not in all_ids]
    if broken_anchors:
        unique_broken = list(set(broken_anchors))[:5]
        issues.append(f"{len(broken_anchors)} broken internal anchor links:")
        for anchor in unique_broken:
            issues.append(f"  #{anchor} → target not found")

    # Check 2: Image references
    img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
    img_srcs = re.findall(img_pattern, content, re.IGNORECASE)

    for src in img_srcs:
        # Skip external images
        if src.startswith(('http://', 'https://', '//')):
            continue

        # Check if local file exists (relative paths only)
        if not src.startswith('/'):
            img_path = os.path.join(basedir, src)
            if not os.path.exists(img_path):
                issues.append(f"Missing image: {src}")

    # Check 3: Images without alt text
    img_no_alt_pattern = r'<img(?![^>]*\balt=)[^>]*>'
    imgs_without_alt = re.findall(img_no_alt_pattern, content, re.IGNORECASE)

    if imgs_without_alt:
        issues.append(f"{len(imgs_without_alt)} images missing alt attribute")

    # Check 4: Links without text content or aria-label
    # This is complex with regex, so we'll do a simpler check
    link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
    links = re.findall(link_pattern, content, re.DOTALL | re.IGNORECASE)

    empty_links = []
    for href, link_content in links:
        # Check if link has aria-label
        aria_label_pattern = r'aria-label="[^"]+"'
        has_aria = re.search(aria_label_pattern, link_content)

        # Remove HTML tags and check if there's text
        text = re.sub(r'<[^>]+>', '', link_content).strip()

        if not text and not has_aria:
            empty_links.append(href)

    if empty_links:
        unique_empty = list(set(empty_links))[:3]
        issues.append(f"{len(empty_links)} links without text or aria-label:")
        for href in unique_empty:
            issues.append(f"  {href}")

    return (len(issues) == 0, issues)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_links_images.py <html_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    passed, issues = check_links_and_images(filepath)

    if passed:
        print(f"✅ {filepath}: Links and images PASS")
        return 0
    else:
        print(f"❌ {filepath}: Links and images FAIL")
        for issue in issues:
            print(f"  - {issue}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

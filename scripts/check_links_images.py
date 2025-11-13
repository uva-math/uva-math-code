#!/usr/bin/env python3
"""
Check for broken internal links and image references.
Validates all href and src attributes for local resources.
"""

import sys
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def check_links_and_images(filepath):
    """
    Check all internal links and image references.
    Returns: (passed: bool, issues: list)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    basedir = os.path.dirname(os.path.abspath(filepath))

    issues = []

    # Check 1: Internal anchor links
    # Find all anchor links
    anchor_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('#'):
            anchor_links.append(href[1:])  # Remove #

    # Find all IDs in document
    all_ids = set()
    for tag in soup.find_all(id=True):
        all_ids.add(tag['id'])

    # Check for broken anchor links
    broken_anchors = [link for link in anchor_links if link not in all_ids]
    if broken_anchors:
        issues.append(f"{len(broken_anchors)} broken internal anchor links:")
        for anchor in broken_anchors[:5]:  # Show first 5
            issues.append(f"  #{anchor} → target not found")

    # Check 2: Image references
    for img in soup.find_all('img', src=True):
        src = img['src']

        # Skip external images
        if src.startswith(('http://', 'https://', '//')):
            continue

        # Check if local file exists
        if src.startswith('/'):
            # Absolute path from site root - can't verify without full site context
            continue
        else:
            # Relative path
            img_path = os.path.join(basedir, src)
            if not os.path.exists(img_path):
                issues.append(f"Missing image: {src}")

    # Check 3: Images without alt text
    imgs_without_alt = []
    for img in soup.find_all('img'):
        if not img.get('alt') and img.get('alt') != '':  # alt="" is valid for decorative
            imgs_without_alt.append(img.get('src', 'unknown'))

    if imgs_without_alt:
        issues.append(f"{len(imgs_without_alt)} images missing alt attribute:")
        for src in imgs_without_alt[:3]:  # Show first 3
            issues.append(f"  {src}")

    # Check 4: Links without text content
    empty_links = []
    for a in soup.find_all('a'):
        text = a.get_text().strip()
        aria_label = a.get('aria-label', '').strip()
        if not text and not aria_label:
            empty_links.append(a.get('href', 'no-href'))

    if empty_links:
        issues.append(f"{len(empty_links)} links without text or aria-label:")
        for href in empty_links[:3]:
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

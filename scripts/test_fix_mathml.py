#!/usr/bin/env python3
"""Regression fixtures for native MathML in the legacy exam processor."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_mathml import check_mathml
from fix_mathml import preserve_native_mathml


class NativeMathMLTest(unittest.TestCase):
    def test_native_structure_and_unicode_are_unchanged(self):
        markup = '<math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msup><mi>ℝ</mi><mn>2</mn></msup><annotation encoding="application/x-tex">\\mathbb{R}^2</annotation></semantics></math>'
        self.assertEqual(preserve_native_mathml(markup), markup)

    def test_removes_only_labels_copied_from_tex(self):
        for quote in ('"', "'"):
            with self.subTest(quote=quote):
                markup = '<math display="inline" aria-label=' + quote + 'x &lt; y' + quote + '><semantics><mi>x</mi><mo>&lt;</mo><mi>y</mi><annotation encoding="application/x-tex">\n x &lt; y \n</annotation></semantics></math>'
                fixed = preserve_native_mathml(markup)
                self.assertNotIn('aria-label', fixed)
                self.assertIn('<mi>x</mi><mo>&lt;</mo><mi>y</mi>', fixed)
                self.assertIn('<annotation encoding="application/x-tex">\n x &lt; y \n</annotation>', fixed)
                self.assertEqual(preserve_native_mathml(fixed), fixed)

    def test_preserves_authored_speech_and_math_without_annotations(self):
        markup = '<math aria-label="x squared"><semantics><msup><mi>x</mi><mn>2</mn></msup><annotation encoding="application/x-tex">x^2</annotation></semantics></math><math aria-label="a variable"><mi>x</mi></math>'
        self.assertEqual(preserve_native_mathml(markup), markup)

    def test_cli_preserves_unicode_and_passes_mathml_check(self):
        markup = '<!doctype html><html><head><title>Exam</title></head><body><h1>Exam</h1><math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="\\mathbb{R}"><semantics><mi>ℝ</mi><annotation encoding="application/x-tex">\\mathbb{R}</annotation></semantics></math></body></html>'
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'input.html'
            output = Path(directory) / 'output.html'
            source.write_text(markup, encoding='utf-8')
            subprocess.run([sys.executable, str(Path(__file__).with_name('fix_mathml.py')), str(source), str(output)], check=True, capture_output=True)
            fixed = output.read_text(encoding='utf-8')
            self.assertIn('<mi>ℝ</mi>', fixed)
            self.assertNotIn('aria-label="\\mathbb{R}"', fixed)
            self.assertNotIn('role="math"', fixed)
            passed, issues, _, _ = check_mathml(output)
            self.assertTrue(passed, issues)


if __name__ == '__main__':
    unittest.main()

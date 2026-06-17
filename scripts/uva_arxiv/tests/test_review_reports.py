from __future__ import annotations

import unittest

from scripts.uva_arxiv import review_reports


class ReviewReportMatchingTests(unittest.TestCase):
    def test_author_matching_does_not_cross_author_boundaries(self) -> None:
        self.assertFalse(
            review_reports._contains_normalized_name(
                "Xueyin Wang, Jiangong You, Qi Zhou",
                "you qi",
            )
        )
        self.assertFalse(
            review_reports._contains_normalized_name(
                "You-Qi Zhao, Cheng-Yu Pai",
                "you qi",
            )
        )
        self.assertTrue(
            review_reports._contains_normalized_name(
                "A. Author, You Qi and B. Author",
                "you qi",
            )
        )

    def test_author_matching_handles_common_arxiv_separators(self) -> None:
        self.assertTrue(
            review_reports._contains_normalized_name(
                "Renjun Duan, Weiqiang Wang and Yong Wang",
                "weiqiang wang",
            )
        )
        self.assertTrue(
            review_reports._contains_normalized_name(
                "Thomas Koberda and Yash Lodha",
                "thomas koberda",
            )
        )

    def test_author_matching_handles_tex_accents(self) -> None:
        self.assertTrue(
            review_reports._contains_normalized_name(
                'Jean-baptiste Casteras, Juraj F\\"oldes, Itamar Oliveira',
                "juraj foldes",
            )
        )
        self.assertTrue(
            review_reports._contains_normalized_name(
                'Juraj F{\\"o}ldes and David P. Herzog',
                "juraj foldes",
            )
        )


if __name__ == "__main__":
    unittest.main()

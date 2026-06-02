from __future__ import annotations

import unittest

from scripts.uva_arxiv import journal_refs


class JournalRefsTests(unittest.TestCase):
    def test_parse_arxiv_journal_ref_extracts_common_fields(self) -> None:
        parsed = journal_refs.parse_arxiv_journal_ref(
            "Ann. Probab. 52 (4), 1225-1252 (2024)"
        )

        self.assertEqual(parsed["journal_name"], "Ann. Probab.")
        self.assertEqual(parsed["journal_volume"], "52")
        self.assertEqual(parsed["journal_pages"], "1225-1252")
        self.assertEqual(parsed["publication_year"], 2024)

    def test_metadata_status_does_not_treat_bare_s2_date_as_journal_data(self) -> None:
        self.assertEqual(
            journal_refs.metadata_status(
                {
                    "journal_name": "",
                    "doi": "",
                    "venue": "",
                    "publication_date": "2024-01-01",
                }
            ),
            "missing",
        )
        self.assertEqual(journal_refs.metadata_status({"venue": "Topology and its Applications"}), "venue_only")
        self.assertEqual(journal_refs.metadata_status({"doi": "10.1000/example"}), "doi_only")
        self.assertEqual(journal_refs.metadata_status({"journal_name": "Advances in Mathematics"}), "journal")

    def test_parse_s2_entry_rejects_arxiv_only_venue(self) -> None:
        info, status, similarity, notes = journal_refs.parse_s2_entry(
            {
                "title": "The site linkage spectrum of data arrays",
                "externalIds": {"ArXiv": "2401.04827"},
                "publicationVenue": {"name": "arXiv.org"},
                "publicationDate": "2024-01-09",
                "year": 2024,
            },
            "2401.04827",
            "The site linkage spectrum of data arrays",
        )

        self.assertEqual(status, "empty")
        self.assertEqual(similarity, 1.0)
        self.assertEqual(notes, "")
        self.assertEqual(info["venue"], "")
        self.assertEqual(journal_refs.metadata_status(info), "missing")


if __name__ == "__main__":
    unittest.main()

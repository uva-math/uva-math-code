from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.uva_arxiv import roles, roster


def write_person(directory: Path, filename: str, front_matter: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    path.write_text(
        "---\n"
        + textwrap.dedent(front_matter).strip()
        + "\n---\n\nBody text is ignored.\n",
        encoding="utf-8",
    )
    return path


class RoleClassificationTests(unittest.TestCase):
    def test_role_groups_use_front_matter_before_directory(self) -> None:
        self.assertEqual(
            roles.classify_role(
                {
                    "general_position": "faculty",
                    "position": "Assistant Professor, General Faculty",
                },
                "faculty",
            ).role_group,
            "agfm_other",
        )
        self.assertEqual(
            roles.classify_role(
                {
                    "general_position": "emeritus",
                    "position": "Professor Emeritus",
                },
                "faculty",
            ).role_group,
            "emeritus",
        )
        self.assertEqual(
            roles.classify_role(
                {
                    "general_position": "faculty",
                    "position": "Gordon Whyburn Professor of Mathematics",
                },
                "faculty",
            ).role_group,
            "faculty",
        )

    def test_role_groups_cover_non_faculty_directories(self) -> None:
        self.assertEqual(
            roles.classify_role(
                {"general_position": "postdoc", "position": "Research Associate and Lecturer"},
                "postdoc",
            ).role_group,
            "postdoc",
        )
        self.assertEqual(
            roles.classify_role(
                {"general_position": "gradstudent", "position": "Graduate Student"},
                "grad",
            ).role_group,
            "grad",
        )
        self.assertEqual(
            roles.classify_role(
                {"general_position": "lecturer", "position": "Lecturer"},
                "lecturer",
            ).role_group,
            "agfm_other",
        )


class RosterParserTests(unittest.TestCase):
    def test_parse_roster_records_roles_aliases_and_notices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            people_dirs = {
                "faculty": root / "_departmentpeople" / "faculty",
                "postdoc": root / "_departmentpeople" / "postdocs",
                "grad": root / "_departmentpeople" / "gradstudents",
                "lecturer": root / "_departmentpeople" / "lecturers",
                "emeriti": root / "_departmentpeople" / "emeriti",
                "unpublished": root / "_departmentpeople" / "_unpublished",
            }

            write_person(
                people_dirs["faculty"],
                "faculty.md",
                """
                UVA_id: abc1de
                lastname: Curie
                name: Marie
                general_position: faculty
                position: Associate Professor
                email: curie@virginia.edu
                research_tags:
                - AN
                specialty: Analysis
                """,
            )
            write_person(
                people_dirs["faculty"],
                "general-faculty.md",
                """
                UVA_id: gf1aa
                lastname: Wang
                name: Caelan
                general_position: faculty
                position: Assistant Professor, General Faculty
                """,
            )
            write_person(
                people_dirs["faculty"],
                "emeritus-in-faculty.md",
                """
                UVA_id: em1aa
                lastname: Pitt
                name: Loren
                general_position: emeritus
                position: Professor Emeritus
                """,
            )
            write_person(
                people_dirs["postdoc"],
                "postdoc.md",
                """
                UVA_id: pd1aa
                lastname: Blackwell
                name: Sarah
                general_position: postdoc
                position: NSF Postdoctoral Research Fellow
                """,
            )
            write_person(
                people_dirs["grad"],
                "grad.md",
                """
                UVA_id: gr1aa
                lastname: Noether
                name: Emmy
                general_position: gradstudent
                position: Graduate Student
                published: true
                """,
            )
            write_person(
                people_dirs["lecturer"],
                "lecturer.md",
                """
                UVA_id: lec1a
                lastname: Beamer
                name: Zachary
                general_position: lecturer
                position: Lecturer
                """,
            )
            write_person(
                people_dirs["emeriti"],
                "emeriti.md",
                """
                UVA_id: emer1
                lastname: Germain
                name: Sophie
                general_position: emeritus
                position: Professor Emerita
                """,
            )
            write_person(
                people_dirs["unpublished"],
                "hidden.md",
                """
                UVA_id: hid1a
                lastname: Hidden
                name: Person
                general_position: gradstudent
                position: Graduate Student
                published: false
                """,
            )
            write_person(
                people_dirs["postdoc"],
                "conflict.md",
                """
                UVA_id: con1a
                lastname: Conflict
                name: Pat
                general_position: gradstudent
                position: Graduate Student
                """,
            )

            result = roster.load_current_roster(people_dirs=people_dirs, repo_root=root)

        self.assertEqual(result.records["abc1de"].role.role_group, "faculty")
        self.assertEqual(result.records["gf1aa"].role.role_group, "agfm_other")
        self.assertEqual(result.records["pd1aa"].role.role_group, "postdoc")
        self.assertEqual(result.records["gr1aa"].role.role_group, "grad")
        self.assertEqual(result.records["lec1a"].role.role_group, "agfm_other")
        self.assertEqual(result.records["emer1"].role.role_group, "emeritus")
        self.assertEqual(result.records["hid1a"].published, False)
        self.assertIn("marie curie", result.records["abc1de"].normalized_aliases)
        self.assertIn("m curie", result.records["abc1de"].normalized_aliases)
        self.assertEqual(result.records["abc1de"].display_name, "Marie Curie")
        self.assertEqual(result.records["abc1de"].research_tags, ["AN"])
        self.assertEqual({notice.person_id for notice in result.unpublished}, {"hid1a"})
        self.assertEqual({notice.person_id for notice in result.conflicts}, {"con1a"})
        self.assertEqual(
            {notice.person_id for notice in result.active_directory_special_cases},
            {"em1aa", "gf1aa", "lec1a"},
        )

    def test_display_names_preserve_diacritics_and_normalized_aliases_remove_them(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            people_dirs = {"faculty": root / "_departmentpeople" / "faculty"}
            write_person(
                people_dirs["faculty"],
                "diacritics.md",
                """
                UVA_id: dia1a
                lastname: Brézin
                name: Élise
                general_position: faculty
                position: Professor
                """,
            )

            result = roster.load_current_roster(people_dirs=people_dirs, repo_root=root)

        record = result.records["dia1a"]
        self.assertEqual(record.display_name, "Élise Brézin")
        self.assertIn("elise brezin", record.normalized_aliases)

    def test_duplicate_uva_ids_are_reported_without_name_keying(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            people_dirs = {
                "faculty": root / "_departmentpeople" / "faculty",
                "postdoc": root / "_departmentpeople" / "postdocs",
            }
            write_person(
                people_dirs["faculty"],
                "first.md",
                """
                UVA_id: dup1a
                lastname: First
                name: Person
                general_position: faculty
                position: Professor
                """,
            )
            write_person(
                people_dirs["postdoc"],
                "second.md",
                """
                UVA_id: dup1a
                lastname: Second
                name: Person
                general_position: postdoc
                position: Postdoctoral Fellow
                """,
            )

            result = roster.load_current_roster(people_dirs=people_dirs, repo_root=root)

        self.assertEqual(list(result.records), ["dup1a"])
        self.assertEqual(len(result.duplicates), 1)
        self.assertEqual(result.duplicates[0].person_id, "dup1a")


if __name__ == "__main__":
    unittest.main()

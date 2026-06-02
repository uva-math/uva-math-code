from __future__ import annotations

import contextlib
import csv
import io
import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from scripts.uva_arxiv import env, roles, roster, roster_history


def empty_roster_result() -> roster.RosterResult:
    return roster.RosterResult(
        records={},
        conflicts=[],
        unpublished=[],
        active_directory_special_cases=[],
        duplicates=[],
        parse_errors=[],
    )


def current_roster_result(*records: roster.PersonRecord) -> roster.RosterResult:
    return roster.RosterResult(
        records={record.person_id: record for record in records},
        conflicts=[],
        unpublished=[],
        active_directory_special_cases=[],
        duplicates=[],
        parse_errors=[],
    )


def current_person(
    person_id: str,
    display_name: str,
    role_group: str = "faculty",
    position: str = "Professor",
    directory_key: str = "faculty",
    published: bool = True,
) -> roster.PersonRecord:
    first, *rest = display_name.split()
    last = rest[-1] if rest else ""
    return roster.PersonRecord(
        person_id=person_id,
        uva_id=person_id,
        display_name=display_name,
        first=first,
        last=last,
        general_position=role_group,
        position=position,
        email="",
        personal_page="",
        research_tags=[],
        specialty="",
        published=published,
        current_file=Path(f"_departmentpeople/{directory_key}/{person_id}.md"),
        directory_key=directory_key,
        role=roles.RoleClassification(
            role_group=role_group,
            rank_label=position,
            position_raw=position,
            general_position=role_group,
            source="test",
        ),
        aliases=[],
        normalized_aliases=[],
        raw_front_matter={},
    )


def record(
    person_id: str,
    display_name: str,
    role_group: str,
    position: str,
    path: str,
    directory_key: str,
    published: bool = True,
) -> roster_history.HistoricalPersonRecord:
    return roster_history.HistoricalPersonRecord(
        person_id=person_id,
        display_name=display_name,
        role_group=role_group,
        position=position,
        published=published,
        path=path,
        directory_key=directory_key,
    )


def event(
    commit: str,
    commit_date: str,
    status: str,
    path: str,
    event_record: roster_history.HistoricalPersonRecord | None,
    old_path: str | None = None,
) -> roster_history.HistoryFileEvent:
    return roster_history.HistoryFileEvent(
        commit=commit,
        commit_date=roster_history.parse_date(commit_date),
        status=status,
        path=path,
        old_path=old_path,
        record=event_record,
    )


def write_history_person(path: Path, person_id: str, position: str, general_position: str = "faculty") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        + textwrap.dedent(
            f"""
            UVA_id: {person_id}
            lastname: Person
            name: Test
            general_position: {general_position}
            position: {position}
            """
        ).strip()
        + "\n---\n",
        encoding="utf-8",
    )


def run_git(repo_root: Path, *args: str, date_value: str | None = None) -> None:
    env = os.environ.copy()
    if date_value:
        env["GIT_AUTHOR_DATE"] = f"{date_value}T12:00:00Z"
        env["GIT_COMMITTER_DATE"] = f"{date_value}T12:00:00Z"
    subprocess.run(
        ["git", *args],
        cwd=repo_root,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class RosterHistoryInferenceTests(unittest.TestCase):
    def test_interval_inference_handles_role_change_unpublished_and_emeritus_moves(self) -> None:
        faculty_path = "_departmentpeople/faculty/abc1de.md"
        emeritus_path = "_departmentpeople/emeriti/abc1de.md"
        grad_path = "_departmentpeople/gradstudents/gr1aa.md"
        hidden_path = "_departmentpeople/_unpublished/gr1aa.md"
        events = [
            event(
                "c1",
                "2021-08-10",
                "A",
                faculty_path,
                record("abc1de", "Ada Curie", "faculty", "Assistant Professor", faculty_path, "faculty"),
            ),
            event(
                "c2",
                "2023-08-15",
                "M",
                faculty_path,
                record("abc1de", "Ada Curie", "faculty", "Associate Professor", faculty_path, "faculty"),
            ),
            event(
                "c3",
                "2025-08-01",
                "R",
                emeritus_path,
                record("abc1de", "Ada Curie", "emeritus", "Professor Emeritus", emeritus_path, "emeriti"),
                old_path=faculty_path,
            ),
            event(
                "c4",
                "2021-09-01",
                "A",
                grad_path,
                record("gr1aa", "Grace Student", "grad", "Graduate Student", grad_path, "grad"),
            ),
            event(
                "c5",
                "2022-05-01",
                "R",
                hidden_path,
                record("gr1aa", "Grace Student", "grad", "Graduate Student", hidden_path, "unpublished", published=False),
                old_path=grad_path,
            ),
        ]

        result = roster_history.build_history_result(
            events=events,
            current_roster=empty_roster_result(),
            overrides={},
            initial_start_date=date(2021, 8, 1),
            as_of_date=date(2026, 6, 2),
        )

        intervals = result.appointments["abc1de"]
        self.assertEqual([interval.role_group for interval in intervals], ["faculty", "faculty", "emeritus"])
        self.assertEqual(intervals[0].end_date, date(2023, 8, 15))
        self.assertEqual(intervals[1].end_date, date(2025, 8, 1))
        self.assertIsNone(intervals[2].end_date)
        grad_interval = result.appointments["gr1aa"][0]
        self.assertEqual(grad_interval.end_date, date(2022, 5, 1))
        notice_types = {notice.notice_type for notice in result.notices}
        self.assertIn("inferred_role_or_position_boundary", notice_types)
        self.assertIn("inferred_inactive_boundary", notice_types)

        rows = {(row.person_id, row.academic_year, row.role_group): row for row in result.rows}
        self.assertEqual(rows[("abc1de", "2021-2022", "faculty")].start_date, date(2021, 8, 10))
        self.assertTrue(rows[("abc1de", "2021-2022", "faculty")].current_active)
        self.assertEqual(rows[("abc1de", "2025-2026", "emeritus")].start_date, date(2025, 8, 1))
        self.assertTrue(rows[("abc1de", "2025-2026", "emeritus")].current_active)
        self.assertEqual(rows[("gr1aa", "2021-2022", "grad")].end_date, date(2022, 5, 1))
        self.assertNotIn(("gr1aa", "2022-2023", "grad"), rows)

    def test_manual_overrides_replace_inferred_intervals(self) -> None:
        faculty_path = "_departmentpeople/faculty/abc1de.md"
        events = [
            event(
                "c1",
                "2021-08-10",
                "A",
                faculty_path,
                record("abc1de", "Ada Curie", "faculty", "Assistant Professor", faculty_path, "faculty"),
            )
        ]
        overrides = {
            "abc1de": roster_history.AppointmentOverride(
                display_name="Ada C.",
                appointments=[
                    roster_history.AppointmentInterval(
                        start_date=date(2022, 8, 1),
                        end_date=date(2023, 7, 31),
                        role_group="postdoc",
                        position="Visiting Postdoc",
                        source="manual",
                        confidence="exact",
                    )
                ],
            )
        }

        result = roster_history.build_history_result(
            events=events,
            current_roster=empty_roster_result(),
            overrides=overrides,
            initial_start_date=date(2021, 8, 1),
            as_of_date=date(2024, 6, 1),
        )

        self.assertEqual(result.people["abc1de"].display_name, "Ada C.")
        self.assertEqual(len(result.appointments["abc1de"]), 1)
        self.assertEqual(result.appointments["abc1de"][0].role_group, "postdoc")
        self.assertEqual([(row.academic_year, row.role_group, row.source) for row in result.rows], [("2022-2023", "postdoc", "manual")])
        self.assertIn("manual_override_applied", {notice.notice_type for notice in result.notices})

    def test_display_name_only_override_preserves_inferred_intervals(self) -> None:
        faculty_path = "_departmentpeople/faculty/abc1de.md"
        events = [
            event(
                "c1",
                "2021-08-10",
                "A",
                faculty_path,
                record("abc1de", "Ada Curie", "faculty", "Assistant Professor", faculty_path, "faculty"),
            )
        ]
        overrides = {
            "abc1de": roster_history.AppointmentOverride(
                display_name="Ada C.",
                appointments=[],
            )
        }

        result = roster_history.build_history_result(
            events=events,
            current_roster=empty_roster_result(),
            overrides=overrides,
            initial_start_date=date(2021, 8, 1),
            as_of_date=date(2022, 6, 1),
        )

        self.assertEqual(result.people["abc1de"].display_name, "Ada C.")
        self.assertEqual(len(result.appointments["abc1de"]), 1)
        self.assertEqual(result.rows[0].display_name, "Ada C.")
        self.assertIn(
            "manual_display_name_override_applied",
            {notice.notice_type for notice in result.notices},
        )

    def test_current_roster_without_history_uses_current_academic_year_only(self) -> None:
        result = roster_history.build_history_result(
            events=[],
            current_roster=current_roster_result(current_person("abc1de", "Ada Curie")),
            overrides={},
            initial_start_date=date(2021, 8, 1),
            as_of_date=date(2026, 6, 2),
        )

        self.assertEqual(len(result.appointments["abc1de"]), 1)
        interval = result.appointments["abc1de"][0]
        self.assertEqual(interval.source, "current-roster")
        self.assertEqual(interval.start_date, date(2025, 8, 1))
        self.assertIsNone(interval.end_date)
        self.assertEqual([row.academic_year for row in result.rows], ["2025-2026"])
        self.assertTrue(result.rows[0].current_active)
        self.assertIn("current_roster_without_history", {notice.notice_type for notice in result.notices})

    def test_same_path_person_id_change_closes_previous_identity(self) -> None:
        faculty_path = "_departmentpeople/faculty/person.md"
        events = [
            event(
                "c1",
                "2021-08-01",
                "A",
                faculty_path,
                record("oldid", "Ada Curie", "faculty", "Professor", faculty_path, "faculty"),
            ),
            event(
                "c2",
                "2021-09-01",
                "M",
                faculty_path,
                record("newid", "Ada Curie", "faculty", "Professor", faculty_path, "faculty"),
            ),
        ]

        people, appointments, notices = roster_history.infer_git_intervals(events)

        self.assertEqual(people["newid"].display_name, "Ada Curie")
        self.assertEqual(appointments["oldid"][0].end_date, date(2021, 9, 1))
        self.assertIsNone(appointments["newid"][0].end_date)
        self.assertIn("path_person_id_change", {notice.notice_type for notice in notices})

    def test_override_yaml_loader_supports_manual_appointment_examples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "appointments_overrides.yml"
            path.write_text(
                """
abc1de:
  display_name: Ada Curie
  appointments:
    - start_date: 2021-08-01
      end_date: null
      role_group: faculty
      position: Professor
      source: manual
""",
                encoding="utf-8",
            )

            overrides = roster_history.load_appointment_overrides(path)

        interval = overrides["abc1de"].appointments[0]
        self.assertEqual(overrides["abc1de"].display_name, "Ada Curie")
        self.assertEqual(interval.start_date, date(2021, 8, 1))
        self.assertIsNone(interval.end_date)
        self.assertEqual(interval.confidence, "exact")

    def test_override_yaml_loader_accepts_comment_then_empty_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "appointments_overrides.yml"
            path.write_text("# no overrides yet\n{}\n", encoding="utf-8")

            overrides = roster_history.load_appointment_overrides(path)

        self.assertEqual(overrides, {})

    def test_git_history_events_parse_real_temp_repo_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_git(root, "init")
            run_git(root, "config", "user.email", "math@example.edu")
            run_git(root, "config", "user.name", "Math Test")
            run_git(root, "config", "commit.gpgsign", "false")

            faculty_path = root / "_departmentpeople" / "faculty" / "abc1de.md"
            write_history_person(faculty_path, "abc1de", "Assistant Professor")
            run_git(root, "add", "_departmentpeople/faculty/abc1de.md")
            run_git(root, "commit", "-m", "add faculty", date_value="2021-08-10")

            write_history_person(faculty_path, "abc1de", "Associate Professor")
            run_git(root, "add", "_departmentpeople/faculty/abc1de.md")
            run_git(root, "commit", "-m", "promote faculty", date_value="2023-08-15")

            emeritus_rel = "_departmentpeople/emeriti/abc1de.md"
            (root / "_departmentpeople" / "emeriti").mkdir(parents=True)
            run_git(root, "mv", "_departmentpeople/faculty/abc1de.md", emeritus_rel)
            run_git(root, "commit", "-m", "move emeritus", date_value="2025-08-01")

            write_history_person(root / emeritus_rel, "abc1de", "Professor Emeritus", "emeritus")
            run_git(root, "add", emeritus_rel)
            run_git(root, "commit", "-m", "mark emeritus", date_value="2025-08-02")

            events, notices = roster_history.git_history_events(root)

        self.assertEqual(notices, [])
        self.assertEqual([item.status for item in events], ["A", "M", "R", "M"])
        self.assertEqual(events[-2].old_path, "_departmentpeople/faculty/abc1de.md")
        self.assertEqual(events[-2].path, "_departmentpeople/emeriti/abc1de.md")
        self.assertEqual(events[-1].record.role_group, "emeritus")

    def test_academic_year_expansion_clips_to_initial_start_and_windows(self) -> None:
        rows = roster_history.expand_active_years(
            people={"abc1de": roster_history.PersonSummary("abc1de", "Ada Curie")},
            appointments={
                "abc1de": [
                    roster_history.AppointmentInterval(
                        start_date=date(2019, 1, 1),
                        end_date=None,
                        role_group="faculty",
                        position="Professor",
                        source="git-history",
                        confidence="commit-date",
                    )
                ]
            },
            initial_start_date=date(2021, 8, 1),
            as_of_date=date(2023, 7, 1),
        )

        self.assertEqual([row.academic_year for row in rows], ["2021-2022", "2022-2023"])
        self.assertEqual(rows[0].start_date, date(2021, 8, 1))
        self.assertEqual(rows[0].end_date, date(2022, 7, 31))
        self.assertEqual(rows[1].end_date, date(2023, 7, 31))

    def test_write_outputs_creates_json_csv_and_markdown(self) -> None:
        result = roster_history.HistoryResult(
            people={"abc1de": roster_history.PersonSummary("abc1de", "Ada Curie")},
            appointments={
                "abc1de": [
                    roster_history.AppointmentInterval(
                        start_date=date(2021, 8, 1),
                        end_date=None,
                        role_group="faculty",
                        position="Professor",
                        source="manual",
                        confidence="exact",
                    )
                ]
            },
            rows=[
                roster_history.ActiveYearRow(
                    person_id="abc1de",
                    display_name="Ada Curie",
                    academic_year="2021-2022",
                    start_date=date(2021, 8, 1),
                    end_date=date(2022, 7, 31),
                    role_group="faculty",
                    position="Professor",
                    source="manual",
                    confidence="exact",
                    current_active=True,
                )
            ],
            notices=[],
            initial_start_date=date(2021, 8, 1),
            as_of_date=date(2022, 1, 1),
            generated_at="2022-01-01T00:00:00Z",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            json_path = root / "cache" / "active_people_by_year.json"
            csv_path = root / "reports" / "active.csv"
            md_path = root / "reports" / "active.md"

            roster_history.write_outputs(result, json_path, csv_path, md_path)

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            with csv_path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            markdown = md_path.read_text(encoding="utf-8")

        self.assertEqual(payload["rows"][0]["person_id"], "abc1de")
        self.assertEqual(rows[0]["academic_year"], "2021-2022")
        self.assertIn("Counts by Academic Year and Role", markdown)

    def test_direct_dry_run_main_does_not_write_outputs(self) -> None:
        config = env.load_config(load_env_file=False)
        result = roster_history.HistoryResult(
            people={},
            appointments={},
            rows=[],
            notices=[],
            initial_start_date=date(2021, 8, 1),
            as_of_date=date(2026, 6, 2),
            generated_at="2026-06-02T00:00:00Z",
        )
        write_calls: list[tuple[object, ...]] = []

        def fake_write_outputs(*args: object) -> None:
            write_calls.append(args)

        with (
            mock.patch.object(roster_history.env, "load_config", return_value=config),
            mock.patch.object(roster_history, "build_from_repo", return_value=result),
            mock.patch.object(roster_history, "write_outputs", side_effect=fake_write_outputs),
            mock.patch.object(roster_history, "print_report"),
            mock.patch("sys.argv", ["roster_history.py", "--dry-run"]),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            exit_code = roster_history.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(write_calls, [])

    def test_committed_support_reports_match_fixed_as_of_generator(self) -> None:
        config = env.load_config(load_env_file=False)
        result = roster_history.build_from_repo(config, date(2026, 6, 2))
        csv_path = config.repo_root / "reports" / "uva-arxiv-active-people-by-year.csv"
        md_path = config.repo_root / "reports" / "uva-arxiv-active-people-by-year.md"

        with csv_path.open(encoding="utf-8", newline="") as handle:
            committed_rows = list(csv.DictReader(handle))
        expected_rows = [row.to_dict() for row in result.rows]
        markdown = md_path.read_text(encoding="utf-8")

        self.assertEqual(committed_rows, expected_rows)
        self.assertIn("As-of date: 2026-06-02", markdown)
        self.assertIn(f"Rows: {len(result.rows)}", markdown)
        counts = result.counts_by_year_role()
        for academic_year in sorted(counts):
            year_counts = counts[academic_year]
            expected_line = (
                "| "
                + " | ".join(
                    [
                        academic_year,
                        str(year_counts.get("faculty", 0)),
                        str(year_counts.get("postdoc", 0)),
                        str(year_counts.get("grad", 0)),
                        str(year_counts.get("agfm_other", 0)),
                        str(year_counts.get("emeritus", 0)),
                    ]
                )
                + " |"
            )
            self.assertIn(expected_line, markdown)


if __name__ == "__main__":
    unittest.main()

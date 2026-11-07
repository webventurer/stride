"""
Test the record of how long each stage of a card took.

These tests build small Claude Code session folders, with reviewer logs beside
them, and check that the recorder writes the right rows, that the report puts
the slowest stage first, and that a missing log never stops a merge.

They own the stage_times module checks; running the cards belongs to the
skill.
"""

import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from click.testing import CliRunner
from diskcache import Cache
from stage_times import (
    StageRow,
    ensure_excluded,
    logs_folder_name,
    main,
    merged_cards,
    record_card,
    report_text,
)

CARD = "WB-970"
ASK = "AskUserQuestion"
START = datetime(2026, 11, 7, 14, 0, 0, tzinfo=timezone.utc)
START_CHECK_BRIEF = (
    "Read `.claude/commands/linear/reference/card-start-review.md`"
)
CARD_CHECK_BRIEF = (
    "Read `.claude/commands/linear/reference/card-check-review.md`"
)
SIMPLIFY_BRIEF = "Read `.claude/commands/linear/reference/simplify-review.md`"
COMMIT_BRIEF = "Read `.claude/skills/commit/REVIEW.md`"
LENSES = ("Promise by promise", "Try to break it", "Prove it")
AUTHOR_CONFIG = ("-c", "user.name=Test", "-c", "user.email=test@example.com")


def stamp(seconds: float) -> str:
    return (START + timedelta(seconds=seconds)).isoformat()


def user_text(seconds: float, text: str) -> dict:
    return {
        "type": "user",
        "timestamp": stamp(seconds),
        "message": {"content": text},
    }


def tool_result(seconds: float, tool_use_id: str) -> dict:
    block = {"type": "tool_result", "tool_use_id": tool_use_id}
    return {
        "type": "user",
        "timestamp": stamp(seconds),
        "message": {"content": [block]},
    }


def tool_use(seconds: float, name: str, tool_use_id: str, **input_) -> dict:
    block = {"type": "tool_use", "id": tool_use_id, "name": name}
    block["input"] = input_
    return {
        "type": "assistant",
        "timestamp": stamp(seconds),
        "message": {"content": [block]},
    }


def assistant_text(seconds: float) -> dict:
    return {
        "type": "assistant",
        "timestamp": stamp(seconds),
        "message": {"content": [{"type": "text", "text": "Done."}]},
    }


def merge_branch(repo: Path, card: str):
    def git(*arguments: str):
        command = ["git", "-C", str(repo), *AUTHOR_CONFIG, *arguments]
        subprocess.run(command, capture_output=True, check=True)

    git("checkout", "-q", "-b", card)
    git("commit", "-q", "--allow-empty", "-m", f"work on {card}")
    git("checkout", "-q", "main")
    git(
        "merge",
        "-q",
        "--no-ff",
        "-m",
        f"Merge branch 'mikemindel/{card}'",
        card,
    )


def write_jsonl(path: Path, events: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(event) for event in events]
    path.write_text("\n".join(lines) + "\n")


def write_reviewer(
    folder: Path,
    session: str,
    agent: str,
    brief: str,
    lens: str,
    stamps: list[float],
    effort: str | None = "high",
):
    prompt = f"{brief} and follow it. Your lens is {lens}. The card is WB-970."
    events = [user_text(stamps[0], prompt if lens else brief)]
    events += [assistant_text(second) for second in stamps[1:]]
    agents = folder / session / "subagents"
    write_jsonl(agents / f"agent-{agent}.jsonl", events)
    meta = {"model": "sonnet"}
    if effort:
        meta["effort"] = effort
    (agents / f"agent-{agent}.meta.json").write_text(json.dumps(meta))


def write_card_session(folder: Path, session: str = "s1"):
    write_jsonl(
        folder / f"{session}.jsonl",
        [
            user_text(0, "Run /linear:start WB-970"),
            assistant_text(5),
            user_text(65, "yes"),
            tool_use(70, "Edit", "edit-1"),
            tool_result(71, "edit-1"),
            assistant_text(80),
            tool_use(200, "Bash", "merge-1", command="gh pr merge 5 --merge"),
            tool_result(212, "merge-1"),
            assistant_text(213),
        ],
    )


def write_start_check(folder: Path, session: str = "s1"):
    stops = ((10, 55), (10, 30), (10, 20))
    for number, (lens, stops_at) in enumerate(zip(LENSES, stops)):
        write_reviewer(
            folder,
            session,
            f"start{number}",
            START_CHECK_BRIEF,
            lens,
            list(stops_at),
        )


def write_card_check_twice(folder: Path, session: str = "s1"):
    for run, begins in enumerate((100, 150)):
        for number, lens in enumerate(LENSES):
            write_reviewer(
                folder,
                session,
                f"check{run}{number}",
                CARD_CHECK_BRIEF,
                lens,
                [begins, begins + 10, begins + 20 + number],
            )


class RecorderTest(unittest.TestCase):
    """Tests for turning session logs into one row per stage run."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name) / "logs"
        self.store = Cache(str(Path(self.temp.name) / "store"))

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def rows(self, stage: str) -> list[StageRow]:
        return [
            row
            for row in record_card(CARD, [self.folder], self.store)
            if row.stage == stage
        ]

    def test_start_check_has_one_row_per_reviewer_on_run_one(self):
        write_card_session(self.folder)
        write_start_check(self.folder)

        rows = self.rows("Start check")

        self.assertEqual(sorted(row.lens for row in rows), sorted(LENSES))
        self.assertEqual({row.run for row in rows}, {1})
        self.assertFalse(any(row.repeat for row in rows))

    def test_row_holds_time_silence_working_time_model_and_effort(self):
        write_card_session(self.folder)
        write_start_check(self.folder)

        row = next(
            r for r in self.rows("Start check") if r.lens == "Try to break it"
        )

        self.assertEqual(row.seconds, 20)
        self.assertEqual(row.longest_silence, 20)
        self.assertEqual(row.working_seconds, 0)
        self.assertEqual((row.model, row.effort), ("sonnet", "high"))
        self.assertEqual(row.card, CARD)

    def test_longest_silence_is_the_largest_gap_between_events(self):
        write_card_session(self.folder)
        write_reviewer(
            self.folder,
            "s1",
            "slow",
            START_CHECK_BRIEF,
            "Prove it",
            [10, 20, 30, 130, 140],
        )

        row = self.rows("Start check")[0]

        self.assertEqual(
            (row.seconds, row.longest_silence, row.working_seconds),
            (130, 100, 30),
        )

    def test_a_reviewer_with_no_effort_set_records_it_blank(self):
        write_card_session(self.folder)
        write_reviewer(
            self.folder,
            "s1",
            "commit",
            COMMIT_BRIEF,
            "",
            [150, 160],
            effort=None,
        )

        row = self.rows("Commit review")[0]

        self.assertEqual((row.model, row.effort, row.lens), ("sonnet", "", ""))

    def test_second_card_check_run_is_marked_as_a_repeat(self):
        write_card_session(self.folder)
        write_card_check_twice(self.folder)

        rows = self.rows("Card check")

        self.assertEqual(len(rows), 6)
        self.assertEqual(
            [row.run for row in rows],
            [1, 1, 1, 2, 2, 2],
        )
        self.assertEqual(
            [row.repeat for row in rows],
            [False] * 3 + [True] * 3,
        )

    def test_waiting_on_the_user_is_a_row_and_never_a_repeat(self):
        write_card_session(self.folder)

        waits = self.rows("Wait on the user")

        self.assertEqual([wait.seconds for wait in waits], [60])
        self.assertEqual(waits[0].run, 1)
        self.assertFalse(waits[0].repeat)

    def test_build_runs_from_first_edit_to_the_next_reviewer_spawn(self):
        write_card_session(self.folder)
        write_reviewer(
            self.folder,
            "s1",
            "simplify",
            SIMPLIFY_BRIEF,
            "",
            [110, 120],
        )

        build = self.rows("Build")

        self.assertEqual([row.seconds for row in build], [40])
        self.assertEqual(self.rows("Simplification review")[0].seconds, 10)

    def test_merge_runs_from_the_merge_call_to_its_result(self):
        write_card_session(self.folder)

        merge = self.rows("Merge")

        self.assertEqual([row.seconds for row in merge], [12])

    def test_a_command_that_only_mentions_the_merge_is_not_a_merge(self):
        write_jsonl(
            self.folder / "s1.jsonl",
            [
                user_text(0, "Run /linear:start WB-970"),
                tool_use(
                    5, "Bash", "grep-1", command="grep -n 'gh pr merge' f"
                ),
                tool_result(6, "grep-1"),
            ],
        )

        self.assertEqual(self.rows("Merge"), [])

    def test_a_merge_after_a_directory_change_is_still_a_merge(self):
        write_jsonl(
            self.folder / "s1.jsonl",
            [
                user_text(0, "Run /linear:finish WB-970"),
                tool_use(5, "Bash", "m-1", command="cd repo && gh pr merge 5"),
                tool_result(9, "m-1"),
            ],
        )

        self.assertEqual([r.seconds for r in self.rows("Merge")], [4])

    def merge_rows_for(self, command: str) -> list:
        write_jsonl(
            self.folder / "s1.jsonl",
            [
                user_text(0, "Run /linear:finish WB-970"),
                tool_use(5, "Bash", "m-1", command=command),
                tool_result(9, "m-1"),
            ],
        )
        return self.rows("Merge")

    def test_a_merge_run_with_a_quoted_directory_change_is_a_merge(self):
        rows = self.merge_rows_for('cd "/path with spaces" && gh pr merge 5')

        self.assertEqual([r.seconds for r in rows], [4])

    def test_a_merge_followed_by_a_pipe_and_a_command_is_still_a_merge(self):
        command = (
            'gh pr merge 268 --merge --subject "Merge branch \'x\'" --body ""'
            " 2>&1 | tail -3; gh pr view 268"
        )

        self.assertEqual([r.seconds for r in self.merge_rows_for(command)], [4])

    def test_a_merge_mentioned_on_a_later_line_is_not_a_merge(self):
        command = "cat <<'EOF'\nsome text\ngh pr merge 5\nEOF"

        self.assertEqual(self.merge_rows_for(command), [])

    def test_a_merge_mentioned_after_and_mid_line_is_not_a_merge(self):
        command = (
            "python - <<'EOF'\ncommand = \"cd repo && gh pr merge 5\"\nEOF"
        )

        self.assertEqual(self.merge_rows_for(command), [])

    def test_the_window_starts_at_linear_start_not_an_earlier_mention(self):
        write_jsonl(
            self.folder / "s1.jsonl",
            [
                user_text(0, "/linear:next-steps recommends WB-970"),
                assistant_text(10),
                user_text(100, "/linear:start WB-970"),
                assistant_text(110),
            ],
        )

        self.assertEqual(self.rows("Wait on the user"), [])

    def test_a_card_id_does_not_match_a_longer_card_id(self):
        write_jsonl(
            self.folder / "s1.jsonl",
            [
                user_text(0, "/linear:start WB-955"),
                assistant_text(10),
                user_text(70, "yes"),
            ],
        )

        self.assertEqual(record_card("WB-95", [self.folder], self.store), [])

    def test_a_question_to_the_user_is_a_wait(self):
        write_jsonl(
            self.folder / "s1.jsonl",
            [
                user_text(0, "/linear:start WB-970"),
                tool_use(10, ASK, "ask-1"),
                tool_result(45, "ask-1"),
                assistant_text(50),
            ],
        )

        self.assertEqual(
            [w.seconds for w in self.rows("Wait on the user")], [35]
        )

    def test_one_log_with_every_stage_gets_one_row_for_each(self):
        write_card_session(self.folder)
        write_reviewer(
            self.folder, "s1", "simplify", SIMPLIFY_BRIEF, "", [110, 120]
        )
        write_reviewer(
            self.folder, "s1", "commit", COMMIT_BRIEF, "", [150, 160]
        )

        stages = [r.stage for r in record_card(CARD, [self.folder], self.store)]

        self.assertEqual(
            sorted(stages),
            sorted(
                [
                    "Build",
                    "Simplification review",
                    "Commit review",
                    "Merge",
                    "Wait on the user",
                ]
            ),
        )

    def test_recording_again_drops_rows_the_new_log_no_longer_has(self):
        write_card_session(self.folder)
        write_start_check(self.folder)
        record_card(CARD, [self.folder], self.store)
        (self.folder / "s1" / "subagents" / "agent-start0.jsonl").unlink()

        record_card(CARD, [self.folder], self.store)

        lenses = {
            key[2] for key in self.store.iterkeys() if key[1] == "Start check"
        }
        self.assertEqual(lenses, {"Try to break it", "Prove it"})

    def test_a_card_split_across_a_resumed_file_has_rows_from_both(self):
        write_card_session(self.folder, "first")
        write_start_check(self.folder, "first")
        write_jsonl(
            self.folder / "resumed.jsonl",
            [
                user_text(300, "WB-970 resumed"),
                assistant_text(305),
                assistant_text(340),
            ],
        )
        write_reviewer(
            self.folder,
            "resumed",
            "late",
            COMMIT_BRIEF,
            "",
            [310, 330],
        )

        stages = {
            row.stage for row in record_card(CARD, [self.folder], self.store)
        }

        self.assertTrue({"Start check", "Commit review", "Merge"} <= stages)

    def test_recording_the_same_card_twice_leaves_the_same_rows(self):
        write_card_session(self.folder)
        write_start_check(self.folder)

        record_card(CARD, [self.folder], self.store)
        first = sorted(self.store.iterkeys())
        record_card(CARD, [self.folder], self.store)

        self.assertEqual(sorted(self.store.iterkeys()), first)

    def test_a_missing_log_records_nothing(self):
        rows = record_card(CARD, [self.folder / "absent"], self.store)

        self.assertEqual(rows, [])
        self.assertEqual(len(self.store), 0)

    def test_an_unreadable_log_records_nothing(self):
        self.folder.mkdir(parents=True)
        (self.folder / "broken.jsonl").write_bytes(b"\xff\xfe not json")

        self.assertEqual(record_card(CARD, [self.folder], self.store), [])

    def test_events_before_the_card_is_first_mentioned_are_left_out(self):
        write_jsonl(
            self.folder / "s1.jsonl",
            [
                user_text(0, "work on WB-111"),
                tool_use(5, "Edit", "early"),
                tool_result(6, "early"),
                user_text(100, "Run /linear:start WB-970"),
                assistant_text(110),
            ],
        )

        self.assertEqual(self.rows("Build"), [])
        self.assertEqual(self.rows("Wait on the user"), [])


class StoreTest(unittest.TestCase):
    """Tests for where the record lives and that git never shows it."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.git("init", "-q", "-b", "main")
        self.git(*AUTHOR_CONFIG, "commit", "-q", "--allow-empty", "-m", "start")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.repo), *arguments],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def test_git_shows_nothing_under_work_after_the_store_is_written(self):
        ensure_excluded(self.repo)
        Cache(str(self.repo / "work" / "stage-times")).close()

        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_excluding_work_twice_adds_one_line(self):
        ensure_excluded(self.repo)
        ensure_excluded(self.repo)

        exclude = (self.repo / ".git" / "info" / "exclude").read_text()
        self.assertEqual(exclude.splitlines().count("/work"), 1)

    def test_merged_cards_come_from_merge_commits_newest_first(self):
        for card in ("wb-1-first", "wb-2-second", "wb-3-third"):
            merge_branch(self.repo, card)

        self.assertEqual(merged_cards(self.repo, 2), ["WB-3", "WB-2"])


class ReportTest(unittest.TestCase):
    """Tests for the report that says where the time goes."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Cache(str(Path(self.temp.name) / "store"))

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def add(self, card: str, stage: str, seconds: float, run: int = 1):
        row = StageRow(
            card, stage, "", "", "", stamp(0), seconds, 0.0, seconds, run
        )
        self.store.set((card, stage, "", run, row.started_at), row.as_dict())

    def test_stage_with_the_slowest_time_comes_first_not_the_highest_median(
        self,
    ):
        for seconds in (50, 52, 54):
            self.add(CARD, "Steady", seconds)
        for seconds in (10, 12, 100):
            self.add(CARD, "Spiky", seconds)

        report = report_text(self.store, [CARD])

        self.assertLess(report.index("Spiky"), report.index("Steady"))

    def test_report_lists_median_slowest_and_repeats_per_stage(self):
        self.add("WB-1", "Card check", 40)
        self.add("WB-1", "Card check", 60, run=2)
        self.add("WB-2", "Card check", 80)

        line = next(
            line
            for line in report_text(self.store, ["WB-1", "WB-2"]).splitlines()
            if "Card check" in line
        )

        self.assertIn("60.0", line)
        self.assertIn("80.0", line)
        self.assertTrue(line.rstrip(" |").endswith("1"))

    def test_report_flags_only_a_stage_slower_than_90_seconds(self):
        self.add(CARD, "Slow", 91)
        self.add(CARD, "Quick", 90)

        report = report_text(self.store, [CARD])

        flagged = [
            line
            for line in report.splitlines()
            if line.startswith("Over 90 s:")
        ]
        self.assertEqual(flagged, ["Over 90 s: Slow"])

    def test_report_names_a_merged_card_that_has_no_rows(self):
        self.add("WB-1", "Merge", 10)
        self.add("WB-2", "Merge", 10)

        report = report_text(self.store, ["WB-1", "WB-2", "WB-3"])

        self.assertIn("No rows: WB-3", report)

    def test_report_ignores_rows_from_cards_outside_the_last_n(self):
        self.add("WB-1", "Old", 500)
        self.add("WB-2", "New", 5)

        report = report_text(self.store, ["WB-2"])

        self.assertNotIn("Old", report)


class CommandTest(unittest.TestCase):
    """Tests for the command a merge runs and its never-stop promise."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(
            ["git", "-C", str(self.repo), "init", "-q", "-b", "main"],
            check=True,
        )
        self.home = Path(self.temp.name) / "home"

    def tearDown(self):
        self.temp.cleanup()

    def test_a_missing_log_exits_cleanly_and_names_the_card(self):
        result = CliRunner().invoke(
            main,
            [
                "--checkout",
                str(self.repo),
                "record",
                CARD,
                "--logs-folder",
                str(self.home / "absent"),
            ],
        )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn(CARD, result.output)

    def test_record_then_report_shows_the_recorded_stage(self):
        folder = self.home / "logs"
        write_card_session(folder)
        arguments = ["--checkout", str(self.repo)]

        CliRunner().invoke(
            main, [*arguments, "record", CARD, "--logs-folder", str(folder)]
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                *AUTHOR_CONFIG,
                "commit",
                "-q",
                "--allow-empty",
                "-m",
                "start",
            ],
            check=True,
        )
        merge_branch(self.repo, "wb-970-x")
        result = CliRunner().invoke(main, [*arguments, "report"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Merge", result.output)

    def test_record_writes_the_store_in_the_main_checkout_out_of_gits_sight(
        self,
    ):
        folder = self.home / "logs"
        write_card_session(folder)

        CliRunner().invoke(
            main,
            [
                "--checkout",
                str(self.repo),
                "record",
                CARD,
                "--logs-folder",
                str(folder),
            ],
        )

        store = Cache(str(self.repo / "work" / "stage-times"))
        self.assertGreater(len(store), 0)
        store.close()
        status = subprocess.run(
            ["git", "-C", str(self.repo), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(status.stdout, "")

    def test_logs_folder_name_matches_how_claude_code_names_it(self):
        self.assertEqual(
            logs_folder_name(Path("/Users/me/stride/.claude/worktrees/wb-1")),
            "-Users-me-stride--claude-worktrees-wb-1",
        )


if __name__ == "__main__":
    unittest.main()

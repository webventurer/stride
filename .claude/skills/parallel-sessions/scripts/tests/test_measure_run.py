"""
Test how much of the plan a batch run used, as the run's logs record it.

These tests build small run folders of session logs and check that every
session is found wherever its log was saved, that each session is counted
once, and that the coordinator's first turn is reported as planning.

They own the measure_run module checks; running a batch belongs to the
skill.
"""

import json
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner
from measure_run import SessionLog, main, session_logs, use_report

SONNET = "claude-sonnet-5-5"
OPUS = "claude-opus-5-5"
FABLE = "claude-fable-5-1"


def usage(cost: float, output_tokens: int = 100) -> dict:
    return {
        "inputTokens": 10,
        "cacheCreationInputTokens": 20,
        "cacheReadInputTokens": 30,
        "outputTokens": output_tokens,
        "costUSD": cost,
    }


def write_log(path: Path, session_id: str, turns: list[dict], span: tuple):
    events = [
        {"type": "system", "subtype": "hook_started"},
        {"type": "system", "subtype": "init", "session_id": session_id},
        {"type": "assistant", "timestamp": span[0], "message": {"id": "m1"}},
        *[{"type": "result", "modelUsage": turn} for turn in turns],
        {"type": "assistant", "timestamp": span[1], "message": {"id": "m2"}},
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(event) for event in events))


class SessionLogsTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.folder.name)

    def tearDown(self):
        self.folder.cleanup()

    def test_session_logs_finds_a_log_in_any_folder(self):
        times = ("2026-11-06T10:00:00Z", "2026-11-06T10:01:00Z")
        write_log(self.run_dir / "repo/work/logs/A-one.jsonl", "a", [], times)
        write_log(self.run_dir / "repo/.claude/other/B-two.log", "b", [], times)

        found = {log.session_id for log in session_logs(self.run_dir)}

        self.assertEqual(found, {"a", "b"})

    def test_session_logs_skips_files_that_are_not_session_logs(self):
        (self.run_dir / "notes.jsonl").write_text('{"type": "note"}')
        times = ("2026-11-06T10:00:00Z", "2026-11-06T10:01:00Z")
        write_log(self.run_dir / ".git/logs/x.jsonl", "git", [], times)

        found = session_logs(self.run_dir)

        self.assertEqual(found, [])


class SessionLogTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name, "captain.log")
        self.times = ("2026-11-06T10:00:00Z", "2026-11-06T10:05:00Z")

    def tearDown(self):
        self.folder.cleanup()

    def test_usage_counts_each_turn_once(self):
        turns = [{OPUS: usage(1.0)}, {OPUS: usage(2.5)}]
        write_log(self.path, "c", turns, self.times)

        log = SessionLog.from_path(self.path)

        self.assertEqual(log.usage[OPUS]["costUSD"], 2.5)

    def test_usage_includes_the_advisor_model(self):
        turns = [{OPUS: usage(2.0), FABLE: usage(3.0)}]
        write_log(self.path, "c", turns, self.times)

        log = SessionLog.from_path(self.path)

        self.assertEqual(log.usage[FABLE]["costUSD"], 3.0)

    def test_first_turn_usage_is_the_planning_turn(self):
        turns = [{OPUS: usage(0.8)}, {OPUS: usage(2.0)}]
        write_log(self.path, "c", turns, self.times)

        log = SessionLog.from_path(self.path)

        self.assertEqual(log.first_turn_usage[OPUS]["costUSD"], 0.8)

    def test_seconds_taken_spans_the_first_and_last_entry(self):
        write_log(self.path, "c", [], self.times)

        log = SessionLog.from_path(self.path)

        self.assertEqual(log.seconds_taken, 300)


class UseReportTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.run_dir = Path(self.folder.name)
        self.logs_dir = self.run_dir / "repo/work/logs"

    def tearDown(self):
        self.folder.cleanup()

    def test_use_report_counts_a_resumed_session_once(self):
        first = ("2026-11-06T10:00:00Z", "2026-11-06T10:01:00Z")
        later = ("2026-11-06T10:02:00Z", "2026-11-06T10:03:00Z")
        write_log(
            self.logs_dir / "card-a.jsonl", "a", [{SONNET: usage(1.0)}], first
        )
        resumed = self.logs_dir / "card-a.resume-1.jsonl"
        write_log(resumed, "a", [{SONNET: usage(1.5)}], later)

        report = use_report(self.run_dir)

        self.assertEqual(report["soldiers"]["card-a"]["use"], 1.5)
        self.assertEqual(report["soldiers"]["card-a"]["resume_count"], 1)

    def test_use_report_splits_the_captain_into_planning_and_running(self):
        times = ("2026-11-06T10:00:00Z", "2026-11-06T10:09:00Z")
        turns = [{OPUS: usage(0.8)}, {OPUS: usage(2.0), FABLE: usage(1.0)}]
        write_log(self.run_dir / "captain.log", "c", turns, times)

        report = use_report(self.run_dir)

        self.assertEqual(report["captain"]["planning"], 0.8)
        self.assertEqual(report["captain"]["running"], 2.2)

    def test_use_report_keeps_soldiers_with_the_same_prefix_apart(self):
        times = ("2026-11-06T10:00:00Z", "2026-11-06T10:01:00Z")
        write_log(
            self.logs_dir / "card-a.jsonl", "a", [{SONNET: usage(1.0)}], times
        )
        write_log(
            self.logs_dir / "card-b.jsonl", "b", [{SONNET: usage(2.0)}], times
        )

        report = use_report(self.run_dir)

        self.assertEqual(set(report["soldiers"]), {"card-a", "card-b"})

    def test_use_report_totals_every_session(self):
        times = ("2026-11-06T10:00:00Z", "2026-11-06T10:01:00Z")
        write_log(
            self.run_dir / "captain.log", "c", [{OPUS: usage(2.0)}], times
        )
        write_log(
            self.logs_dir / "card-a.jsonl", "a", [{SONNET: usage(1.0)}], times
        )

        report = use_report(self.run_dir)

        self.assertEqual(report["total_use"], 3.0)


class MainTest(unittest.TestCase):
    def test_main_prints_the_report_as_json(self):
        with tempfile.TemporaryDirectory() as folder:
            times = ("2026-11-06T10:00:00Z", "2026-11-06T10:01:00Z")
            path = Path(folder, "captain.log")
            write_log(path, "c", [{OPUS: usage(2.0)}], times)

            result = CliRunner().invoke(main, [folder])

        self.assertEqual(json.loads(result.output)["total_use"], 2.0)


if __name__ == "__main__":
    unittest.main()

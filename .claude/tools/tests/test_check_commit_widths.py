"""Tests for the commit-message width guard (.claude/hooks/check_commit_widths.py).

The guard enforces the /commit skill's 50/72 rule. These exercise the pure
validation functions directly; the do_commit.sh wiring is covered by live use.
"""

import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent.parent.parent / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

from check_commit_widths import (  # noqa: E402
    commit_message,
    overlong_prose,
    width_violations,
)


def offending_lines(problems: list) -> list:
    return [p[0] for p in problems]


def test_width_violations_flags_subject_over_50():
    subject = "feat: " + "x" * 50

    problems = width_violations(subject)

    assert offending_lines(problems) == [1]


def test_width_violations_passes_subject_at_50():
    assert width_violations("x" * 50) == []


def test_width_violations_flags_body_line_over_72():
    message = "feat: ok\n\n" + "word " * 20

    problems = width_violations(message)

    assert 3 in offending_lines(problems)


def test_width_violations_passes_wrapped_body():
    message = "feat: ok\n\nUnder the limit comfortably.\nSo is this one."

    assert width_violations(message) == []


def test_overlong_prose_exempts_unwrappable_url():
    assert overlong_prose("https://example.com/" + "a" * 80) is False


def test_overlong_prose_flags_long_line_with_spaces():
    assert overlong_prose("a " + "b" * 80) is True


def test_commit_message_joins_multiple_m_values_with_blank_lines():
    args = ["--args", "--allow-empty", "-m", "feat: Subject", "-m", "Body text"]

    assert commit_message(args) == "feat: Subject\n\nBody text"


def test_commit_message_reads_file_for_dash_capital_f(tmp_path: Path):
    body = tmp_path / "msg.txt"
    body.write_text("feat: Subject\n\nBody from file")

    assert (
        commit_message(["--args", "-F", str(body)])
        == "feat: Subject\n\nBody from file"
    )


def test_commit_message_empty_when_args_carry_no_message():
    assert commit_message(["--args", "--amend", "--no-edit"]) == ""


def test_commit_message_empty_for_fixup_flag():
    assert commit_message(["--args", "--allow-empty", "--fixup=abc123"]) == ""


def test_commit_message_empty_for_missing_file():
    assert commit_message(["--args", "-F", "/nonexistent/msg.txt"]) == ""


def test_width_violations_exempts_git_generated_subjects():
    long_merge = "Merge branch 'mikemindel/wb-539-" + "x" * 40 + "'"

    assert width_violations(long_merge) == []
    assert width_violations("fixup! " + "y" * 60) == []

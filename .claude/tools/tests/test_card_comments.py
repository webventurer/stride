"""
Tests for card_comments — the comments file the end card check hands its reviewers (WB-1063).

Run with:
    python -m pytest .claude/tools/tests/test_card_comments.py
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from click.testing import CliRunner  # noqa: E402

import linear_cli  # noqa: E402
from card_comments import comments_text  # noqa: E402

SITE_LIST = {
    "body": "Same-name site components:\n\n* hero: intended\n* footer: renamed\n* banner: removed",
    "createdAt": "2026-11-13T17:40:00.000Z",
    "user": {"name": "Mike Mindel"},
}


def test_a_card_with_comments_gives_each_comments_text():
    other = {
        "body": "Card start check: nothing to raise",
        "createdAt": "2026-11-13T17:30:00.000Z",
        "user": {"name": "Stride"},
    }

    text = comments_text([other, SITE_LIST])

    assert SITE_LIST["body"] in text
    assert other["body"] in text
    assert text.index(other["body"]) < text.index(SITE_LIST["body"])


def test_each_comment_names_who_posted_it_and_when():
    text = comments_text([SITE_LIST])

    assert "Mike Mindel" in text
    assert "2026-11-13T17:40:00.000Z" in text


def test_a_card_with_no_comments_gives_an_empty_file():
    assert comments_text([]) == ""


def test_comments_come_oldest_first_whatever_order_they_arrive_in():
    older = {"body": "first", "createdAt": "2026-11-01T00:00:00.000Z", "user": {"name": "A"}}
    newer = {"body": "second", "createdAt": "2026-11-02T00:00:00.000Z", "user": {"name": "B"}}

    text = comments_text([newer, older])

    assert text.index("first") < text.index("second")


def test_comment_save_writes_the_file_the_reviewers_read(tmp_path, monkeypatch):
    monkeypatch.setattr(linear_cli, "bearer_token", lambda: "key")
    monkeypatch.setattr(linear_cli, "list_comments", lambda api, issue: [SITE_LIST])
    target = tmp_path / "WB-347" / "comments.md"

    result = CliRunner().invoke(
        linear_cli.cli, ["comment", "save", "WB-347", "--to", str(target)]
    )

    assert result.exit_code == 0, result.output
    assert SITE_LIST["body"] in target.read_text()


def test_comment_save_writes_an_empty_file_for_a_card_with_no_comments(tmp_path, monkeypatch):
    monkeypatch.setattr(linear_cli, "bearer_token", lambda: "key")
    monkeypatch.setattr(linear_cli, "list_comments", lambda api, issue: [])
    target = tmp_path / "comments.md"

    result = CliRunner().invoke(
        linear_cli.cli, ["comment", "save", "WB-1", "--to", str(target)]
    )

    assert result.exit_code == 0, result.output
    assert target.read_text() == ""

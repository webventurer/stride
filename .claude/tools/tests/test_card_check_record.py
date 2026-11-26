"""
Tests for card_check_record — what a card check leaves on its card, and what the next start check has left to look at.

Run with:
    python -m pytest .claude/tools/tests/test_card_check_record.py
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

import linear_cli  # noqa: E402
import pytest  # noqa: E402
from card_check_record import check_scope, record_body  # noqa: E402
from click.testing import CliRunner  # noqa: E402

READ_AT = "2026-11-26T15:00:00Z"
BEFORE = "2026-11-26T14:00:00.000Z"
AFTER = "2026-11-26T16:00:00.000Z"

CARD = {
    "identifier": "WB-9",
    "id": "uuid-9",
    "title": "Refuse an email with no @ sign",
    "description": "The form refuses it.",
    "parent": None,
}


def comment(body, created_at=AFTER):
    return {"body": body, "createdAt": created_at}


def record(card=CARD, read_at=READ_AT, findings="", created_at=BEFORE):
    return comment(record_body(card, read_at, findings), created_at)


def scope(comments, card=CARD, siblings=(), commits=()):
    return check_scope(
        card, comments, lambda: list(siblings), lambda since: list(commits)
    )


def test_a_card_with_no_check_record_gets_the_full_check():
    result = scope([comment("Looks good to me")])

    assert result == {"check": "full"}


@pytest.mark.parametrize("field", ["title", "description"])
def test_a_card_reworded_since_its_record_gets_the_full_check(field):
    reworded = {**CARD, field: "Something else"}

    result = scope([record()], card=reworded)

    assert result == {"check": "full"}


def test_nothing_changed_since_the_record_means_no_check():
    result = scope([record()])

    assert result == {"check": "none", "since": READ_AT}


def test_commits_on_main_are_read_from_the_time_main_was_read():
    asked = []

    def commits(since):
        asked.append(since)
        return ["abc123 fix", "def456 docs"]

    result = check_scope(CARD, [record()], lambda: [], commits)

    assert asked == [READ_AT]
    assert result == {"check": "changes", "since": READ_AT}


def test_a_comment_posted_on_the_card_since_the_record_is_a_change():
    result = scope([record(), comment("Use the other form")])

    assert result["check"] == "changes"


def test_a_comment_posted_before_main_was_read_is_not_a_change():
    result = scope([comment("Agreed", BEFORE), record()])

    assert result["check"] == "none"


def test_a_comment_posted_while_the_check_ran_is_a_change():
    during = comment("One more thing", "2026-11-26T15:00:30.000Z")

    result = scope([during, record(created_at=AFTER)])

    assert result["check"] == "changes"


def test_a_comment_on_a_sibling_card_since_the_record_is_a_change():
    result = scope([record()], siblings=[comment("We renamed the form")])

    assert result["check"] == "changes"


def test_check_records_never_count_as_changes():
    sibling_record = record(created_at=AFTER)

    result = scope(
        [record(), record(created_at=AFTER)], siblings=[sibling_record]
    )

    assert result["check"] == "none"


def test_the_newest_record_is_the_one_that_counts():
    old_wording = {**CARD, "description": "An older draft."}
    older = record(old_wording, "2026-11-25T09:00:00Z", created_at=BEFORE)
    newer = record(created_at=AFTER)

    result = scope([newer, older])

    assert result == {"check": "none", "since": READ_AT}


def test_a_record_carries_the_checks_findings_below_its_first_line():
    body = record_body(CARD, READ_AT, "- Reworded the example\n")

    first, rest = body.split("\n\n", 1)
    assert first.startswith(f"**Card checked** against `main` as of {READ_AT}.")
    assert rest.strip() == "- Reworded the example"


def test_a_record_refuses_a_time_it_could_not_read_back():
    with pytest.raises(ValueError):
        record_body(CARD, "yesterday")


def invoke(*args, comments=(), siblings=None):
    siblings = siblings or {}
    posted = []

    def list_comments(api_key, identifier):
        return siblings.get(identifier, list(comments))

    def create_comment(api_key, issue_uuid, body):
        posted.append((issue_uuid, body))
        return {"id": "comment-1"}

    card = CARD if not siblings else {**CARD, "parent": {"id": "epic-uuid"}}
    sibling_cards = [{"identifier": CARD["identifier"]}] + [
        {"identifier": identifier} for identifier in siblings
    ]
    with (
        patch("linear_cli.bearer_token", return_value="key"),
        patch("linear_cli.get_issue", return_value=card),
        patch("linear_cli.list_comments", list_comments),
        patch("linear_cli.create_comment", create_comment),
        patch("linear_cli.list_by_parent", return_value=sibling_cards),
        patch("linear_cli.main_commits_since", return_value=[]),
    ):
        result = CliRunner().invoke(linear_cli.cli, list(args))
    return result, posted


def snapshot(tmp_path, card=CARD):
    file = tmp_path / "checked.json"
    file.write_text(json.dumps(card))
    return f"@{file}"


def test_record_check_posts_the_record_with_the_findings_file(tmp_path):
    findings = tmp_path / "findings.md"
    findings.write_text("- One note")

    result, posted = invoke(
        "issue",
        "record-check",
        "WB-9",
        "--read-at",
        READ_AT,
        "--checked",
        snapshot(tmp_path),
        "--findings",
        f"@{findings}",
    )

    assert result.exit_code == 0, result.output
    assert posted == [("uuid-9", record_body(CARD, READ_AT, "- One note"))]
    assert json.loads(result.output) == {
        "identifier": "WB-9",
        "checked_at": READ_AT,
    }


def test_a_card_edited_during_its_check_gets_the_full_check_next_time(tmp_path):
    as_checked = {**CARD, "description": "The wording the reviewers read."}

    _, posted = invoke(
        "issue",
        "record-check",
        "WB-9",
        "--read-at",
        READ_AT,
        "--checked",
        snapshot(tmp_path, as_checked),
    )

    assert scope([comment(posted[0][1])]) == {"check": "full"}


def test_record_check_posts_nothing_for_a_time_it_could_not_read_back(
    tmp_path,
):
    result, posted = invoke(
        "issue",
        "record-check",
        "WB-9",
        "--read-at",
        "now",
        "--checked",
        snapshot(tmp_path),
    )

    assert result.exit_code != 0
    assert posted == []


def test_check_scope_prints_one_line_saying_how_much_to_check():
    result, _ = invoke("issue", "check-scope", "WB-9", comments=[record()])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {"check": "none", "since": READ_AT}


def test_check_scope_counts_comments_on_the_cards_sibling_cards():
    result, _ = invoke(
        "issue",
        "check-scope",
        "WB-9",
        comments=[record()],
        siblings={"WB-10": [comment("Renamed the form")]},
    )

    assert json.loads(result.output)["check"] == "changes"

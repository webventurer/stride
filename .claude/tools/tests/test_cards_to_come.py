"""Tests for cards_to_come — which cards can hear a merged card's lessons.

Run with:
    python -m pytest .claude/tools/tests/test_cards_to_come.py
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

import linear_cli  # noqa: E402
from cards_to_come import cards_to_come  # noqa: E402


def card(identifier: str, state: str) -> dict:
    return {
        "identifier": identifier,
        "title": f"Card {identifier}",
        "state": {"name": state},
    }


MIX = [
    card("MERGED", "Done"),
    card("BATCH-DOING", "Doing"),
    card("BATCH-REVIEW", "In Review"),
    card("BATCH-OUTSIDE-EPIC", "Doing"),
    card("BATCH-DONE", "Done"),
    card("BATCH-CANCELED", "Canceled"),
    card("EPIC-DOING", "Doing"),
    card("EPIC-REVIEW", "In Review"),
    card("EPIC-WAITING", "Waiting"),
    card("EPIC-DONE", "Done"),
    card("EPIC-BACKLOG", "Backlog"),
    card("EPIC-BACKBURNER", "Backburner"),
    card("TODO", "Todo"),
    card("OTHER-DOING", "Doing"),
    card("OTHER-BACKLOG", "Backlog"),
    card("OTHER-BACKBURNER", "Backburner"),
]
EPIC = {c["identifier"] for c in MIX if c["identifier"].startswith("EPIC-")} | {
    "MERGED",
    "BATCH-DOING",
}
BATCH = {
    c["identifier"] for c in MIX if c["identifier"].startswith("BATCH-")
} | {"MERGED"}


def heard(cards: list[dict]) -> list[str]:
    return [c["identifier"] for c in cards]


def test_cards_to_come_keeps_the_batch_todo_and_the_epics_backlog():
    cards = cards_to_come(MIX, EPIC, BATCH)

    assert heard(cards) == [
        "BATCH-DOING",
        "BATCH-REVIEW",
        "BATCH-OUTSIDE-EPIC",
        "EPIC-BACKLOG",
        "EPIC-BACKBURNER",
        "TODO",
    ]


def test_cards_to_come_leaves_out_an_epic_card_in_todo():
    epic = card("A", "Todo") | {"title": "Epic: migrate"}

    assert cards_to_come([epic], set(), set()) == []


def test_cards_to_come_names_each_cards_column():
    cards = cards_to_come([card("A", "In Review")], set(), {"A"})

    assert cards == [
        {"identifier": "A", "title": "Card A", "state": "In Review"}
    ]


def test_cards_to_come_lists_a_card_found_twice_once():
    todo = card("A", "Todo")

    assert heard(cards_to_come([todo, todo], {"A"}, {"A"})) == ["A"]


def issue(identifier: str, state: str, parent: dict | None = None) -> dict:
    return card(identifier, state) | {"parent": parent}


def run_cards_to_come(parent_title: str, *batch: str) -> list[str]:
    parent = {"id": "parent-uuid", "title": parent_title}
    issues = {
        "WB-1": issue("WB-1", "Done", parent),
        "WB-2": issue("WB-2", "In Review"),
    }
    with (
        patch("linear_cli.bearer_token", return_value="key"),
        patch(
            "linear_cli.get_issue",
            side_effect=lambda key, name: issues[name.upper()],
        ),
        patch(
            "linear_cli.list_by_project_state",
            return_value=[card("WB-3", "Todo")],
        ),
        patch(
            "linear_cli.list_by_parent",
            return_value=[card("WB-4", "Backlog")],
        ),
    ):
        args = ["cards-to-come", "WB-1", "--project", "Stride"]
        for name in batch:
            args += ["--batch", name]
        result = CliRunner().invoke(linear_cli.cli, args)

    assert result.exit_code == 0, result.output
    return heard(json.loads(result.output))


def test_the_command_reads_the_batch_todo_and_the_epic():
    assert run_cards_to_come("Epic: migrate", "wb-2") == [
        "WB-3",
        "WB-4",
        "WB-2",
    ]


def test_the_command_reads_no_backlog_without_an_epic():
    assert run_cards_to_come("A plain parent card") == ["WB-3"]

"""Tests for considered_cards — the rule that picks the Todo cards to run at once.

Run with:
    python -m pytest .claude/tools/tests/test_todo_batch.py
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from todo_batch import (  # noqa: E402
    card_files,
    cards_of_epic,
    considered_cards,
)
from todo_order import cards_in_work_order  # noqa: E402


def card(
    identifier: str,
    files: tuple[str, ...] = (),
    open_blockers: tuple[str, ...] = (),
) -> dict:
    named = ", ".join(f"`{name}`" for name in files)
    return {
        "identifier": identifier,
        "title": f"Card {identifier}",
        "description": f"### What we'll do\n\nChange {named}.\n",
        "open_blockers": list(open_blockers),
    }


def reasons(considered: list[dict]) -> dict:
    return {c["identifier"]: c["reason"] for c in considered}


def test_considered_cards_takes_unlinked_cards_naming_different_files():
    cards = [card("A", ("report.py",)), card("B", ("linear.py",))]

    assert reasons(considered_cards(cards, 3)) == {"A": None, "B": None}


def test_considered_cards_leaves_out_a_card_whose_blocker_is_open():
    cards = [card("A"), card("C", open_blockers=("A", "WB-9"))]

    assert reasons(considered_cards(cards, 3))["C"] == "blocked by A, WB-9"


def test_considered_cards_leaves_out_the_lower_card_sharing_a_file():
    cards = [card("B", ("report.py",)), card("D", ("src/report.py",))]

    assert reasons(considered_cards(cards, 3)) == {
        "B": None,
        "D": "shares `report.py` with B",
    }


def test_considered_cards_stops_when_the_batch_is_full():
    cards = [card("A"), card("B"), card("C")]

    assert [c["identifier"] for c in considered_cards(cards, 2)] == ["A", "B"]


def test_considered_cards_gives_the_worked_example():
    cards = [
        card("A", ("todo.py",)),
        card("B", ("report.py",)),
        card("C", open_blockers=("A",)),
        card("D", ("report.py",)),
        card("E", ("guide.md",)),
    ]

    assert reasons(considered_cards(cards, 3)) == {
        "A": None,
        "B": None,
        "C": "blocked by A",
        "D": "shares `report.py` with B",
        "E": None,
    }


def test_considered_cards_is_the_top_card_alone_when_the_rest_clash():
    cards = [
        card("A", ("report.py",)),
        card("B", ("report.py",)),
        card("C", open_blockers=("A",)),
    ]

    in_batch = [
        c["identifier"] for c in considered_cards(cards, 3) if not c["reason"]
    ]

    assert in_batch == ["A"]


def test_card_files_reads_only_the_what_we_will_do_section():
    description = (
        "### Where things stand\n\n`old.py` exists.\n\n"
        "### What we'll do\n\nEdit `next-steps.md` and `.stride.json`, "
        "run `/parallel-sessions` and `uv run x.py --flag`.\n\n"
        "### Expected outcome\n\n`later.py` works.\n"
    )

    assert card_files({"description": description}) == {
        "next-steps.md",
        ".stride.json",
    }


def test_card_files_reads_extensions_with_digits_but_not_numbers():
    description = (
        "### What we'll do\n\nSwap `logo.mp4` and `data.h5`; gap `0.01`.\n"
    )

    assert card_files({"description": description}) == {"logo.mp4", "data.h5"}


def test_card_files_is_empty_without_a_description():
    assert card_files({"description": None}) == set()


def epic_card(
    identifier: str,
    epic: str | None,
    sort_order: float,
    priority: int = 3,
    open_blockers: tuple[str, ...] = (),
) -> dict:
    return card(identifier, open_blockers=open_blockers) | {
        "parent": {"identifier": epic} if epic else None,
        "priority": priority,
        "sortOrder": sort_order,
        "blockers": list(open_blockers),
    }


def epic_batch(cards: list[dict], epic: str, size: int) -> list[dict]:
    ordered = cards_in_work_order(cards)
    return considered_cards(cards_of_epic(ordered, epic), size)


def test_cards_of_epic_keeps_only_that_epics_sub_issues():
    cards = [
        epic_card("A", "WB-1", 1),
        epic_card("B", "WB-2", 2),
        epic_card("C", None, 3),
    ]

    assert [c["identifier"] for c in cards_of_epic(cards, "WB-1")] == ["A"]


def test_epic_batch_fills_the_limit_from_the_epic_when_other_cards_sit_above():
    cards = [
        epic_card("X1", "WB-2", 1),
        epic_card("X2", "WB-2", 2),
        epic_card("A", "WB-1", 3),
        epic_card("B", "WB-1", 4),
        epic_card("C", "WB-1", 5),
    ]

    assert [c["identifier"] for c in epic_batch(cards, "WB-1", 2)] == [
        "A",
        "B",
    ]


def test_epic_batch_puts_a_higher_priority_card_first_whatever_its_board_place():
    cards = [
        epic_card("A", "WB-1", 1, priority=3),
        epic_card("B", "WB-1", 2, priority=1),
    ]

    assert [c["identifier"] for c in epic_batch(cards, "WB-1", 2)] == [
        "B",
        "A",
    ]


def test_epic_batch_leaves_out_a_card_blocked_by_a_card_of_another_epic():
    cards = [
        epic_card("A", "WB-1", 1, open_blockers=("WB-99",)),
        epic_card("B", "WB-1", 2),
    ]

    assert reasons(epic_batch(cards, "WB-1", 3)) == {
        "A": "blocked by WB-99",
        "B": None,
    }


def test_epic_batch_ignores_a_shared_file_with_a_card_of_another_epic():
    cards = [
        epic_card("X", "WB-2", 1) | card("X", ("report.py",)),
        epic_card("A", "WB-1", 2) | card("A", ("report.py",)),
    ]

    assert reasons(epic_batch(cards, "WB-1", 3)) == {"A": None}


def test_epic_batch_is_empty_when_the_epic_has_nothing_in_todo():
    cards = [epic_card("X", "WB-2", 1)]

    assert epic_batch(cards, "WB-1", 3) == []


def test_epic_batch_leaves_out_a_sub_issue_sharing_a_file_with_the_batch():
    cards = [
        epic_card("A", "WB-1", 1) | card("A", ("report.py",)),
        epic_card("B", "WB-1", 2) | card("B", ("report.py",)),
    ]

    assert reasons(epic_batch(cards, "WB-1", 3)) == {
        "A": None,
        "B": "shares `report.py` with A",
    }

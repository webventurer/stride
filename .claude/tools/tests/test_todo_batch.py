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
    waits_on_answer: bool = False,
) -> dict:
    named = ", ".join(f"`{name}`" for name in files)
    return {
        "identifier": identifier,
        "title": f"Card {identifier}",
        "description": f"### What we'll do\n\nChange {named}.\n",
        "open_blockers": list(open_blockers),
        "waits_on_answer": waits_on_answer,
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


def test_considered_cards_leaves_out_a_card_waiting_on_an_answer():
    cards = [card("A", waits_on_answer=True), card("B")]

    assert reasons(considered_cards(cards, 3)) == {
        "A": "waits for an answer to a lesson question",
        "B": None,
    }


def test_considered_cards_leaves_out_a_card_the_run_already_started():
    cards = [card("A"), card("B")]

    assert reasons(considered_cards(cards, 3, frozenset({"A"}))) == {
        "A": "started earlier in this run and stopped before reaching Doing",
        "B": None,
    }


def test_considered_cards_does_not_count_a_left_out_card_in_the_batch():
    cards = [card("A", waits_on_answer=True), card("B"), card("C")]

    in_batch = [
        c["identifier"] for c in considered_cards(cards, 2) if not c["reason"]
    ]

    assert in_batch == ["B", "C"]


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


def described(identifier: str, description: str) -> dict:
    return {
        "identifier": identifier,
        "title": f"Card {identifier}",
        "description": description,
        "open_blockers": [],
        "waits_on_answer": False,
    }


def test_card_files_reads_a_file_named_outside_what_we_will_do():
    description = (
        "### Where things stand\n\n`old.py` exists.\n\n"
        "### What we'll do\n\nEdit `next-steps.md` and `.stride.json`, "
        "run `uv run x.py --flag`.\n\n"
        "### Expected outcome\n\n`later.py` works.\n"
    )

    assert card_files({"description": description}) == {
        "old.py",
        "next-steps.md",
        ".stride.json",
        "later.py",
    }


def test_card_files_ignores_files_quoted_or_left_alone():
    description = (
        "### Why this matters\n\n*sets in* `.stride.json`\n\n"
        "### What we'll do\n\nEdit `a.py`.\n\n"
        "### What we won't do\n\nWon't touch `b.py`.\n\n"
        "### Live check\n\nRun against `c.py`.\n"
    )

    assert card_files({"description": description}) == {"a.py"}


def test_card_files_counts_a_file_name_followed_by_a_command():
    description = "### Where things stand\n\nRuns `linear_cli.py order-todo`.\n"

    assert card_files({"description": description}) == {"linear_cli.py"}


def test_card_files_maps_a_command_or_skill_named_in_what_we_will_do():
    description = (
        "### What we'll do\n\nChange `/linear:start`, `/parallel-sessions` "
        "and `/work`, not `/linear:nothing`.\n"
    )

    assert card_files({"description": description}) == {
        ".claude/commands/linear/start.md",
        ".claude/skills/parallel-sessions/SKILL.md",
    }


def test_card_files_ignores_a_command_named_outside_what_we_will_do():
    description = "### Where things stand\n\nRuns `/linear:start`.\n"

    assert card_files({"description": description}) == set()


def test_considered_cards_leaves_out_a_card_naming_the_file_in_where_things_stand():
    first = described("A", "### What we'll do\n\nEdit `src/report.py`.\n")
    second = described(
        "B",
        "### Where things stand\n\n`report.py` is slow.\n\n"
        "### What we'll do\n\nEdit `x.py`.\n",
    )

    assert reasons(considered_cards([first, second], 3)) == {
        "A": None,
        "B": "shares `report.py` with A",
    }


def test_considered_cards_keeps_two_skills_with_the_same_file_name_apart_from_clashing():
    first = described(
        "A", "### What we'll do\n\nEdit `.claude/skills/commit/SKILL.md`.\n"
    )
    second = described(
        "B",
        "### What we'll do\n\nEdit "
        "`.claude/skills/parallel-sessions/SKILL.md`.\n",
    )

    assert reasons(considered_cards([first, second], 3)) == {
        "A": None,
        "B": None,
    }


def test_considered_cards_keeps_a_card_quoting_the_same_file_as_another():
    quoting = "### Why this matters\n\n*sets in* `.stride.json`\n\n"
    first = described("A", quoting + "### What we'll do\n\nEdit `a.py`.\n")
    second = described(
        "B",
        quoting + "### What we'll do\n\nEdit `b.py`.\n\n"
        "### What we won't do\n\nWon't touch `a.py`.\n",
    )

    assert reasons(considered_cards([first, second], 3)) == {
        "A": None,
        "B": None,
    }


WB_970 = """### Where things stand

`.claude/skills/parallel-sessions/scripts/measure_run.py` reads session logs.

### What we'll do

* **Keep the record:** the recorder adds `/work` to the exclude file, as `/parallel-sessions` does.
"""

WB_971 = """### Where things stand

`.claude/skills/parallel-sessions/BRIEF.md` tells a job to keep its slot.

### What we'll do

* **A waiting job keeps its turn open:** `.claude/skills/parallel-sessions/BRIEF.md` says so.

### Expected outcome

* `.claude/skills/parallel-sessions/SKILL.md` says the coordinator releases the slot at once.
"""

WB_943 = """### What we'll do

In unattended mode, `/linear:start` with no card named works through Todo until no card in it can start.
"""

WB_973 = """### What we'll do

* **An epic runs in batches:** `.claude/commands/linear/start.md` says so, and `linear_cli.py start-choice` and `next-batch` take the epic.
"""

WB_957 = """### Where things stand

`/linear:next-steps` writes Todo's order with `linear_cli.py order-todo`. `.claude/tools/todo_order.py` leaves epics out.

### What we'll do

* **Work cards below the epics:** every work card sits below every `Epic: ` card in Todo.
"""


def test_considered_cards_keeps_the_three_clashing_pairs_apart():
    pairs = [
        (("WB-970", WB_970), ("WB-971", WB_971)),
        (("WB-943", WB_943), ("WB-973", WB_973)),
        (("WB-957", WB_957), ("WB-973", WB_973)),
    ]

    held_back = [
        considered_cards([described(*a), described(*b)], 3)[1]["reason"]
        for a, b in pairs
    ]

    assert held_back == [
        "shares `.claude/skills/parallel-sessions/SKILL.md` with WB-970",
        "shares `.claude/commands/linear/start.md` with WB-943",
        "shares `linear_cli.py` with WB-957",
    ]


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

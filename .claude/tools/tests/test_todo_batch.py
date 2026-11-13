"""Tests for considered_cards — the rule that picks the Todo cards to run at once.

Run with:
    python -m pytest .claude/tools/tests/test_todo_batch.py
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from todo_batch import cards_of_epic, considered_cards  # noqa: E402
from todo_order import cards_in_work_order  # noqa: E402


def card(
    identifier: str,
    files: tuple[str, ...] = (),
    open_blockers: tuple[str, ...] = (),
    waits_on_answer: bool = False,
) -> dict:
    named = ", ".join(f"`{name}`" for name in files)
    return described(identifier, f"### What we'll do\n\nChange {named}.\n") | {
        "open_blockers": list(open_blockers),
        "waits_on_answer": waits_on_answer,
    }


def described(identifier: str, description: str) -> dict:
    return {
        "identifier": identifier,
        "title": f"Card {identifier}",
        "description": description,
        "open_blockers": [],
        "waits_on_answer": False,
    }


def reasons(considered: list[dict]) -> dict:
    return {c["identifier"]: c["reason"] for c in considered}


def test_considered_cards_leaves_out_a_card_whose_blocker_is_open():
    cards = [card("A"), card("C", open_blockers=("A", "WB-9"))]

    assert reasons(considered_cards(cards, 3))["C"] == "blocked by A, WB-9"


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
        "D": None,
    }


WB_1040 = """### What we'll do

A `/import-site` skill takes a site whose code you have and rebuilds it in Lander, in this order:

2. Write `DESIGN.md` from the original's styles: its stylesheets, and where it has none, its inline styles, utility classes and the running page's computed styles.
3. Put the original's colours, fonts and sizes into the site's own `src/styles/_colors.scss` and `src/styles/_theme.scss` as variables.
5. Write the pages in MDX, replacing the demo `content/home.mdx`, rebuild the original's header and navigation in `src/layout.mdx`, as `AGENTS.md` places them.
"""

WB_1038 = """### Why this matters

*"`principles/`, `AGENTS.md` and `DESIGN.md` together let a fresh AI agent answer \"what is Lander for?\" without reading any source code."*

### What we'll do

Correct every row above in the file it names (AGENTS.md unless the row says otherwise), in every place the file repeats the claim. Add the three missing facts to AGENTS.md.

### Expected outcome

* The breakpoint table in `templates/init/DESIGN.md` has those three rows, headed as widths up to which the layout changes
"""


def test_considered_cards_takes_the_two_cards_that_both_name_design_md():
    cards = [described("WB-1040", WB_1040), described("WB-1038", WB_1038)]

    assert reasons(considered_cards(cards, 3)) == {
        "WB-1040": None,
        "WB-1038": None,
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


def test_considered_cards_takes_the_three_pairs_from_7_nov_2026_together():
    pairs = [
        (("WB-970", WB_970), ("WB-971", WB_971)),
        (("WB-943", WB_943), ("WB-973", WB_973)),
        (("WB-957", WB_957), ("WB-973", WB_973)),
    ]

    held_back = [
        considered_cards([described(*a), described(*b)], 3)[1]["reason"]
        for a, b in pairs
    ]

    assert held_back == [None, None, None]


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


def test_epic_batch_is_empty_when_the_epic_has_nothing_in_todo():
    cards = [epic_card("X", "WB-2", 1)]

    assert epic_batch(cards, "WB-1", 3) == []


def test_epic_batch_takes_two_sub_issues_naming_the_same_file():
    cards = [
        epic_card("A", "WB-1", 1) | card("A", ("report.py",)),
        epic_card("B", "WB-1", 2) | card("B", ("report.py",)),
    ]

    assert reasons(epic_batch(cards, "WB-1", 3)) == {"A": None, "B": None}

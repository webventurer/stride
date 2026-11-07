"""Tests for cards_in_work_order — the rule that puts Todo in the order stride works it.

Run with:
    python -m pytest .claude/tools/tests/test_todo_order.py
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from todo_order import (  # noqa: E402
    cards_in_work_order,
    epics_in,
    new_sort_orders,
)

URGENT, HIGH, MEDIUM, LOW, NO_PRIORITY = 1, 2, 3, 4, 0


def card(
    identifier: str,
    priority: int,
    sort_order: float,
    blockers: list[str] | None = None,
) -> dict:
    return {
        "identifier": identifier,
        "title": f"Card {identifier}",
        "priority": priority,
        "sortOrder": sort_order,
        "blockers": blockers or [],
    }


def identifiers(cards: list[dict]) -> list[str]:
    return [c["identifier"] for c in cards]


def test_todo_order_ranks_by_priority_with_no_priority_last():
    cards = [card("A", NO_PRIORITY, 1), card("B", LOW, 2), card("C", URGENT, 3)]

    assert identifiers(cards_in_work_order(cards)) == ["C", "B", "A"]


def test_todo_order_keeps_board_order_within_a_priority():
    cards = [card("A", MEDIUM, 3), card("B", MEDIUM, 1), card("C", MEDIUM, 2)]

    assert identifiers(cards_in_work_order(cards)) == ["B", "C", "A"]


def test_todo_order_puts_a_blocked_card_directly_below_its_blocker():
    cards = [
        card("A", HIGH, 1),
        card("B", MEDIUM, 2),
        card("C", HIGH, 3, ["B"]),
    ]

    assert identifiers(cards_in_work_order(cards)) == ["A", "B", "C"]


def test_todo_order_waits_for_the_last_of_several_blockers():
    cards = [
        card("A", URGENT, 1, ["B", "C"]),
        card("B", HIGH, 2),
        card("C", LOW, 3),
        card("D", MEDIUM, 4),
    ]

    assert identifiers(cards_in_work_order(cards)) == ["B", "D", "C", "A"]


def test_todo_order_never_moves_a_blocked_card_up():
    cards = [
        card("B", MEDIUM, 1),
        card("D", MEDIUM, 2),
        card("C", MEDIUM, 3, ["B"]),
    ]

    assert identifiers(cards_in_work_order(cards)) == ["B", "D", "C"]


def test_todo_order_ignores_a_blocker_outside_todo():
    cards = [card("A", HIGH, 1, ["WB-1"]), card("B", MEDIUM, 2)]

    assert identifiers(cards_in_work_order(cards)) == ["A", "B"]


def test_todo_order_leaves_epics_out():
    epic = card("E", NO_PRIORITY, 0) | {"title": "Epic: Something"}

    assert identifiers(cards_in_work_order([epic, card("A", HIGH, 1)])) == ["A"]


def test_todo_order_still_places_cards_that_block_each_other():
    cards = [card("A", HIGH, 1, ["B"]), card("B", HIGH, 2, ["A"])]

    assert sorted(identifiers(cards_in_work_order(cards))) == ["A", "B"]


def test_new_sort_orders_rise_in_the_new_order():
    ordered = [card("C", HIGH, 30), card("A", HIGH, 10), card("B", HIGH, 20)]

    assert new_sort_orders(ordered, []) == {"C": 10, "A": 20, "B": 30}


def test_new_sort_orders_rise_when_cards_share_a_sort_order():
    ordered = [card("A", HIGH, 5), card("B", HIGH, 5), card("C", HIGH, 5)]

    values = list(new_sort_orders(ordered, []).values())

    assert values == sorted(values) and len(set(values)) == 3


def epic(identifier: str, sort_order: float) -> dict:
    return card(identifier, NO_PRIORITY, sort_order) | {
        "title": f"Epic: {identifier}"
    }


def test_epics_in_picks_only_the_epic_cards():
    cards = [epic("E", 0), card("A", HIGH, 1)]

    assert identifiers(epics_in(cards)) == ["E"]


def test_new_sort_orders_put_a_card_above_an_epic_below_it():
    ordered = [card("A", HIGH, 1), card("B", MEDIUM, 20), card("C", LOW, 30)]

    orders = new_sort_orders(ordered, [epic("E", 10)])

    assert orders["A"] > 10
    assert orders["A"] < orders["B"] < orders["C"]


def test_new_sort_orders_keep_the_places_of_cards_already_below_an_epic():
    ordered = [card("A", HIGH, 20), card("B", MEDIUM, 30)]

    assert new_sort_orders(ordered, [epic("E", 10)]) == {"A": 20, "B": 30}


def test_new_sort_orders_put_every_card_below_the_highest_of_two_epics():
    ordered = [card("A", HIGH, 1), card("B", MEDIUM, 2)]

    orders = new_sort_orders(ordered, [epic("E1", 10), epic("E2", 50)])

    assert min(orders.values()) > 50


def test_new_sort_orders_put_a_card_sharing_an_epics_place_below_it():
    ordered = [card("A", HIGH, 10)]

    assert new_sort_orders(ordered, [epic("E", 10)])["A"] > 10


def test_new_sort_orders_keep_today_s_places_with_no_epic():
    ordered = [card("C", HIGH, 30), card("A", HIGH, 10), card("B", HIGH, 20)]

    assert new_sort_orders(ordered, []) == {"C": 10, "A": 20, "B": 30}


def test_new_sort_orders_never_give_an_epic_a_place():
    ordered = [card("A", HIGH, 1)]

    assert "E" not in new_sort_orders(ordered, [epic("E", 10)])

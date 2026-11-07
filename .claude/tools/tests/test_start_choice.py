"""Tests for start_choice — what /linear:start does when no card is named.

Run with:
    python -m pytest .claude/tools/tests/test_start_choice.py
"""

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from start_choice import (  # noqa: E402
    branch_card_id,
    branch_card_ids,
    start_choice,
)


def cards_with_reasons(*reasons: str | None) -> list[dict]:
    return [
        {"identifier": f"WB-{n}", "reason": reason}
        for n, reason in enumerate(reasons, start=1)
    ]


def test_branch_card_id_reads_a_lowercase_branch_name():
    branch = "mikemindel/wb-945-a-parallel-sessions-job"

    assert branch_card_id(branch) == "WB-945"


def test_branch_card_id_reads_a_capitalised_branch_name():
    assert branch_card_id("feature/PG-205-add-thing") == "PG-205"


def test_branch_card_id_reads_a_card_id_in_an_earlier_part():
    assert branch_card_id("WB-945/fix-thing") == "WB-945"


def test_branch_card_id_reads_a_card_id_in_a_middle_part():
    assert branch_card_id("feature/wb-945/x") == "WB-945"


def test_branch_card_id_reads_a_card_id_inside_a_part():
    assert branch_card_id("me/fix-wb-945") == "WB-945"


def test_branch_card_id_reads_a_card_id_before_an_underscore():
    assert branch_card_id("me/wb-945_x") == "WB-945"


def test_branch_card_ids_lists_every_candidate_in_order():
    assert branch_card_ids("me/utf-8-fix-wb-945") == ["UTF-8", "WB-945"]


def test_branch_card_id_is_none_without_a_card_id():
    assert branch_card_id("quick/tidy-readme") is None


def test_start_choice_resumes_the_card_a_branch_names():
    choice = start_choice(
        "mikemindel/wb-9-thing", cards_with_reasons(None, None)
    )

    assert choice == {"action": "resume", "card": "WB-9"}


def test_start_choice_asks_on_a_branch_with_no_card_id():
    assert start_choice("quick/tidy", cards_with_reasons(None)) == {
        "action": "ask"
    }


def test_start_choice_runs_a_batch_of_two_or_more():
    choice = start_choice(
        "main", cards_with_reasons(None, "blocked by WB-1", None)
    )

    assert choice == {"action": "batch", "cards": ["WB-1", "WB-3"]}


def test_start_choice_runs_a_batch_of_one_as_a_single_card():
    choice = start_choice("main", cards_with_reasons(None, "blocked by WB-1"))

    assert choice == {"action": "single", "card": "WB-1"}


def test_start_choice_shows_each_reason_when_no_card_can_start():
    choice = start_choice("main", cards_with_reasons("blocked by WB-7"))

    assert choice == {
        "action": "blocked",
        "reasons": {"WB-1": "blocked by WB-7"},
    }


def test_start_choice_says_todo_is_empty():
    assert start_choice("main", []) == {"action": "empty"}

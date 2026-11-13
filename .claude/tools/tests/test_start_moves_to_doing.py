"""
Guard that /linear:start moves a card to Doing before its card check (WB-1042).

A card the card check rewords or cancels used to reach the move only if the
session remembered a later step. The move now comes first, so nothing the card
check does can skip it.

Run with:
    python -m pytest .claude/tools/tests/test_start_moves_to_doing.py
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
START = REPO_ROOT / ".claude" / "commands" / "linear" / "start.md"
CARD_CHECK_HEADING = "### 3. Check the card"


def test_start_has_exactly_one_move_to_doing():
    assert START.read_text().count("--state Doing") == 1


def test_the_move_to_doing_comes_before_the_card_check():
    text = START.read_text()

    assert text.index("--state Doing") < text.index(CARD_CHECK_HEADING)


def test_the_old_card_rewrite_comes_after_the_move_to_doing_and_before_the_reviewers():
    text = START.read_text()

    rewrite = text.index("reference/rewrite-old-card.md")
    assert text.index("--state Doing") < rewrite
    assert rewrite < text.index("**Spawn three reviewers at once.**")

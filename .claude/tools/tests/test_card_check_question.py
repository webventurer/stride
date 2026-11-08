"""Guard the question a card-check stop asks for a card change (WB-947, WB-1021).

`card-check.md` must point at the question template, keep its rules about
asking, use no reviewer words in "How to ask", and neither that file nor the
convention page may say a card-change stop shows the reviewer's verdict.

Run with:
    python -m pytest .claude/tools/tests/test_card_check_question.py
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CARD_CHECK = REPO_ROOT / ".claude" / "commands" / "linear" / "reference" / "card-check.md"
CONVENTION = REPO_ROOT / "docs" / "conventions" / "check-the-card-at-the-start-and-the-end.md"

REVIEWER_WORDS = ("kept-unproven", "broken", "unclear", "verdict")
SHOWS_THE_VERDICT = re.compile(r"shows?\s+the\s+promise,?\s+(?:its|and\s+its)\s+verdict", re.IGNORECASE)


def how_to_ask_section() -> str:
    text = CARD_CHECK.read_text()
    heading = "### How to ask"
    start = text.index(heading) + len(heading)
    following = re.search(r"^#{1,3} ", text[start:], re.MULTILINE)
    end = start + following.start() if following else len(text)
    return text[start:end]


def test_points_at_the_template_and_keeps_its_rules():
    section = how_to_ask_section()
    assert "asking-the-user.md" in section
    assert "One finding per question" in section
    assert "The card's words" in section
    assert "The user answers no" in section


def test_how_to_ask_uses_no_reviewer_words():
    section = how_to_ask_section().lower()
    for word in REVIEWER_WORDS:
        assert word not in section


def test_no_page_says_a_card_change_stop_shows_the_verdict():
    for path in (CARD_CHECK, CONVENTION):
        assert not SHOWS_THE_VERDICT.search(path.read_text()), path.name

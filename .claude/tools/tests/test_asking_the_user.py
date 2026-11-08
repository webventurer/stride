"""Guard the one template every question stride asks the user follows (WB-1021).

`asking-the-user.md` names the four parts in order, holds the WB-1017
example and says what to leave out. Each of the six places that put a
question to the user points at it and says its questions carry the four
labelled parts in order.

Run with:
    python -m pytest .claude/tools/tests/test_asking_the_user.py
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
LINEAR_REFERENCE = REPO_ROOT / ".claude" / "commands" / "linear" / "reference"
TEMPLATE = LINEAR_REFERENCE / "asking-the-user.md"

SIX_PLACES = (
    LINEAR_REFERENCE / "card-check.md",
    REPO_ROOT / ".claude" / "commands" / "linear" / "start.md",
    LINEAR_REFERENCE / "carry-lessons.md",
    LINEAR_REFERENCE / "todo-run.md",
    REPO_ROOT / ".claude" / "skills" / "parallel-sessions" / "BRIEF.md",
    REPO_ROOT / ".claude" / "skills" / "parallel-sessions" / "SKILL.md",
)

FOUR_PARTS = ("**Context:**", "**The gap:**", "**The question:**", "**My answer:**")
FOUR_PARTS_PHRASE = "four labelled parts in order"


def test_template_names_the_four_parts_in_order():
    text = TEMPLATE.read_text()
    positions = [text.index(part) for part in FOUR_PARTS]
    assert positions == sorted(positions)


def test_template_holds_the_wb_1017_example_word_for_word():
    text = TEMPLATE.read_text()
    assert "> **Context:** stride runs a few jobs at once, and each job needs one of a limited number of slots, like tickets for a ride." in text
    assert "> **The gap:** that fix only covers a job's first run." in text
    assert "> **The question:** should WB-1017 also make restarted jobs wait for a free slot before they start, the same way first runs now do?" in text
    assert "> **My answer:** yes. Otherwise WB-1017 brings back the waiting WB-1018 just got rid of. It's a small addition to the same card." in text


def test_template_says_to_leave_out_file_names_and_class_names_and_explain_stride_terms():
    text = TEMPLATE.read_text().lower()
    assert "file names" in text
    assert "class names" in text
    assert "stride term" in text
    assert "same sentence" in text


@pytest.mark.parametrize("path", SIX_PLACES, ids=lambda path: path.name)
def test_each_place_points_at_the_template_and_names_the_four_parts(path):
    text = path.read_text()
    assert "asking-the-user.md" in text
    assert FOUR_PARTS_PHRASE in text

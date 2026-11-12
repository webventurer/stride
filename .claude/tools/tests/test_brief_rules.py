"""Guard the rules a parallel-sessions job brief carries (WB-1019).

A brief filled in for a shared checkout carries all four rules. A brief filled
in for a worktree keeps the sub-agent, refused-action and people rules and
drops the commit rule, which only a shared checkout needs.

Run with:
    python -m pytest .claude/tools/tests/test_brief_rules.py
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BRIEF = REPO_ROOT / ".claude" / "skills" / "parallel-sessions" / "BRIEF.md"

SHARED_CHECKOUT = "Shared checkout"
WORKTREE_MODES = ("One worktree per job", "A stride card, one worktree per job")

SUB_AGENT_RULE = ("Agent tool", "Task tool", "Workflow tool", "opted in")
COMMIT_RULE = ("Never rewrite a commit", "git reset", "--amend", "fixup", "autosquash", "misfiled")
REFUSED_ACTION_RULE = ("hook or guard refuses", "heredoc", "never get the same result another way")
PEOPLE_RULE = ("never assume a pronoun", "commit messages")


def section(text: str, heading: str) -> str:
    start = text.index(heading) + len(heading)
    following = re.search(r"^## ", text[start:], re.MULTILINE)
    end = start + following.start() if following else len(text)
    return text[start:end]


def route(mode: str) -> str:
    routes = section(BRIEF.read_text(), "## Commit routes")
    match = re.search(rf"^\*\*{re.escape(mode)}:\*\*.*?(?=^\*\*[^*\n]+:\*\*|\Z)", routes, re.MULTILINE | re.DOTALL)
    assert match, f"no commit route for {mode}"
    return match.group(0)


def filled_in_brief(mode: str) -> str:
    text = BRIEF.read_text()
    return text[: text.index("## Commit routes")] + route(mode)


def mentions(text: str, phrases: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return all(phrase.lower() in lowered for phrase in phrases)


ALL_MODES = (SHARED_CHECKOUT, *WORKTREE_MODES)


@pytest.mark.parametrize("mode", ALL_MODES)
def test_every_brief_carries_the_sub_agent_refused_action_and_people_rules(mode):
    brief = filled_in_brief(mode)
    assert mentions(brief, SUB_AGENT_RULE)
    assert mentions(brief, REFUSED_ACTION_RULE)
    assert mentions(brief, PEOPLE_RULE)


def test_shared_checkout_brief_carries_the_commit_rule():
    assert mentions(filled_in_brief(SHARED_CHECKOUT), COMMIT_RULE)


@pytest.mark.parametrize("mode", WORKTREE_MODES)
def test_worktree_brief_drops_the_commit_rule(mode):
    brief = filled_in_brief(mode)
    assert "Never rewrite a commit" not in brief
    assert "misfiled" not in brief


@pytest.mark.parametrize("mode", ALL_MODES)
def test_keep_in_touch_list_names_where_to_send_a_refused_action(mode):
    keep_in_touch = section(filled_in_brief(mode), "## Keep in touch with the coordinator")
    assert re.search(r"refused an action", keep_in_touch, re.IGNORECASE)


def test_commit_rule_tells_the_job_to_report_the_verdict_to_the_coordinator():
    rule = route(SHARED_CHECKOUT)
    assert re.search(r"report .*coordinator", rule, re.IGNORECASE | re.DOTALL)


SKILL = REPO_ROOT / ".claude" / "skills" / "parallel-sessions" / "SKILL.md"


def screenshot_rule(brief: str) -> str:
    rules = section(brief, "## Rules")
    match = re.search(r"^- \*\*Screenshots\.\*\*.*$", rules, re.MULTILINE)
    assert match, "no screenshot rule in the brief's Rules"
    return match.group(0)


@pytest.mark.parametrize("mode", ALL_MODES)
def test_every_brief_carries_the_optional_screenshot_rule(mode):
    rule = screenshot_rule(filled_in_brief(mode))
    assert mentions(rule, ("screenshot", "time limit", "message the coordinator", "any other tool"))
    assert mentions(rule, ("screenshot-tool", "delete"))


@pytest.mark.parametrize("mode", ALL_MODES)
def test_a_brief_filled_in_with_a_tool_names_it(mode):
    rule = screenshot_rule(filled_in_brief(mode))
    filled = rule.replace("<the repo's screenshot tool>", "agentshot")
    assert filled.count("agentshot") == 2
    assert "<the repo's screenshot tool>" not in filled


@pytest.mark.parametrize("mode", ALL_MODES)
def test_a_brief_with_the_rule_deleted_never_mentions_screenshots(mode):
    brief = filled_in_brief(mode)
    without = brief.replace(screenshot_rule(brief) + "\n", "")
    assert without != brief
    assert "screenshot" not in without.lower()


def test_screenshot_rule_sits_on_one_line_so_deleting_it_leaves_the_rest_unchanged():
    brief = BRIEF.read_text()
    rule = screenshot_rule(brief)
    assert brief.count(rule) == 1


def test_filling_in_the_brief_is_told_to_read_the_screenshot_tool_setting():
    step = section(SKILL.read_text(), "### 3. Write one brief per job")
    assert mentions(step, ("screenshot-tool", "linear_cli.py screenshot-tool", "delete"))

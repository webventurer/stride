"""Picks the next batch of Todo cards that can run at the same time.

It works down Todo in the order `todo_order` gives, adding each card that
passes two rules, until the batch holds `parallel-sessions` cards or Todo
runs out. A card is out while any card blocking it is not Done, out while a
lesson question on it has no answer, out when a run has already started it and
it is still in Todo, and out when it shares a file with a card already in the
batch.

With an epic named, only that epic's sub-issues are looked at, so the batch
fills from them however many other cards sit above them in Todo.

A card's files are the backticked names ending in a file extension anywhere
in its description, a command after the name in the same backticks allowed,
except in "Why this matters", "What we won't do" and "Live check", plus the
file behind each `/command` or `/skill` named in "What we'll do". Two files are
the same file when one path ends with the other on a folder boundary. The
batch is a best guess: two cards can still clash in a file neither mentions.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WHAT_WE_WILL_DO_RE = re.compile(
    r"### What we[’']ll do\n(.*?)(?=\n### |\Z)", re.S
)
ASIDE_SECTIONS_RE = re.compile(
    r"^### (?:Why this matters|What we won[’']t do|Live check)\n.*?(?=^### |\Z)",
    re.M | re.S,
)
FILE_NAME_RE = re.compile(r"`([^`\s]*\.[A-Za-z][A-Za-z0-9]*)(?:\s[^`]*)?`")
SLASH_NAME_RE = re.compile(r"`/([\w-]+)(?::([\w-]+))?(?:\s[^`]*)?`")


def cards_of_epic(ordered_cards: list[dict], epic: str) -> list[dict]:
    return [
        c
        for c in ordered_cards
        if (c["parent"] or {}).get("identifier") == epic
    ]


def considered_cards(
    ordered_cards: list[dict], size: int, started: frozenset[str] = frozenset()
) -> list[dict]:
    considered: list[dict] = []
    for card in ordered_cards:
        batch = [c for c in considered if not c["reason"]]
        if len(batch) == size:
            break
        reason = reason_left_out(card, batch, started)
        considered.append(card | {"reason": reason})
    return considered


def reason_left_out(
    card: dict, batch: list[dict], started: frozenset[str]
) -> str | None:
    if card["open_blockers"]:
        return "blocked by " + ", ".join(card["open_blockers"])
    if card["waits_on_answer"]:
        return "waits for an answer to a lesson question"
    if card["identifier"] in started:
        return "started earlier in this run and stopped before reaching Doing"
    return shared_file_reason(card, batch)


def shared_file_reason(card: dict, batch: list[dict]) -> str | None:
    files = card_files(card)
    for other in batch:
        shared = shared_files(files, card_files(other))
        if shared:
            names = ", ".join(f"`{name}`" for name in shared)
            return f"shares {names} with {other['identifier']}"
    return None


def shared_files(files: set[str], other_files: set[str]) -> list[str]:
    return sorted(
        {
            min(file, other, key=len)
            for file in files
            for other in other_files
            if same_file(file, other)
        }
    )


def same_file(a: str, b: str) -> bool:
    return a == b or a.endswith("/" + b) or b.endswith("/" + a)


def card_files(card: dict) -> set[str]:
    description = card["description"] or ""
    named = FILE_NAME_RE.findall(ASIDE_SECTIONS_RE.sub("", description))
    section = WHAT_WE_WILL_DO_RE.search(description)
    commands = SLASH_NAME_RE.findall(section.group(1)) if section else []
    mapped = (command_file(*command) for command in commands)
    return set(named) | {path for path in mapped if path}


def command_file(first: str, second: str) -> str | None:
    path = (
        f".claude/commands/{first}/{second}.md"
        if second
        else f".claude/skills/{first}/SKILL.md"
    )
    return path if (REPO_ROOT / path).is_file() else None

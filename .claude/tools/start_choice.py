"""Decides what /linear:start does when it is run with no card named.

On a branch whose name holds a card ID, in either case, it resumes that
card; on any other branch but main, it asks. On main it
reads the batch `next-batch` picks: two or more cards run as a batch, one runs
alone, and a Todo with no card able to start, or no card at all, says so.

The choice is a rule, so a test covers every case, and `linear_cli.py
start-choice` prints it for the command to follow.
"""

import re

MAIN_BRANCH = "main"
CARD_ID_RE = re.compile(r"(?<![a-z0-9])([a-z]+-\d+)(?![0-9])", re.IGNORECASE)


def start_choice(branch: str, considered_cards: list[dict]) -> dict:
    if branch != MAIN_BRANCH:
        card = branch_card_id(branch)
        return {"action": "resume", "card": card} if card else {"action": "ask"}
    return todo_choice(considered_cards)


def branch_card_id(branch: str) -> str | None:
    return next(iter(branch_card_ids(branch)), None)


def branch_card_ids(branch: str) -> list[str]:
    return [found.upper() for found in CARD_ID_RE.findall(branch)]


def todo_choice(considered_cards: list[dict]) -> dict:
    batch = [c["identifier"] for c in considered_cards if not c["reason"]]
    if len(batch) > 1:
        return {"action": "batch", "cards": batch}
    if batch:
        return {"action": "single", "card": batch[0]}
    if considered_cards:
        reasons = {c["identifier"]: c["reason"] for c in considered_cards}
        return {"action": "blocked", "reasons": reasons}
    return {"action": "empty"}

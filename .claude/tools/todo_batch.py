"""Picks the next batch of Todo cards that can run at the same time.

It works down Todo in the order `todo_order` gives, adding each card that
passes two rules, until the batch holds `parallel-sessions` cards or Todo
runs out. A card is out while any card blocking it is not Done, and out when
it shares a file with a card already in the batch.

With an epic named, only that epic's sub-issues are looked at, so the batch
fills from them however many other cards sit above them in Todo.

A card's files are the backticked names ending in a file extension in its
"What we'll do" section, compared by file name. The batch is a best guess:
two cards can still clash in a file neither names.
"""

import re

WHAT_WE_WILL_DO_RE = re.compile(
    r"### What we[’']ll do\n(.*?)(?=\n### |\Z)", re.S
)
FILE_NAME_RE = re.compile(r"`([^`\s]*\.[A-Za-z][A-Za-z0-9]*)`")


def cards_of_epic(ordered_cards: list[dict], epic: str) -> list[dict]:
    return [
        c
        for c in ordered_cards
        if (c["parent"] or {}).get("identifier") == epic
    ]


def considered_cards(ordered_cards: list[dict], size: int) -> list[dict]:
    considered: list[dict] = []
    for card in ordered_cards:
        batch = [c for c in considered if not c["reason"]]
        if len(batch) == size:
            break
        considered.append(card | {"reason": reason_left_out(card, batch)})
    return considered


def reason_left_out(card: dict, batch: list[dict]) -> str | None:
    if card["open_blockers"]:
        return "blocked by " + ", ".join(card["open_blockers"])
    return shared_file_reason(card, batch)


def shared_file_reason(card: dict, batch: list[dict]) -> str | None:
    files = card_files(card)
    clash = next((c for c in batch if files & card_files(c)), None)
    if not clash:
        return None
    shared = ", ".join(
        f"`{name}`" for name in sorted(files & card_files(clash))
    )
    return f"shares {shared} with {clash['identifier']}"


def card_files(card: dict) -> set[str]:
    section = WHAT_WE_WILL_DO_RE.search(card["description"] or "")
    names = FILE_NAME_RE.findall(section.group(1)) if section else []
    return {name.rsplit("/", 1)[-1] for name in names}

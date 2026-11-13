"""Picks the next batch of Todo cards that can run at the same time.

It works down Todo in the order `todo_order` gives, adding each card that
passes the rules, until the batch holds `parallel-sessions` cards or Todo
runs out. A card is out while any card blocking it is not Done, out while a
lesson question on it has no answer, and out when a run has already started it
and it is still in Todo. A file name that two cards share never holds one out:
each card runs in its own worktree and the merge, one card at a time, sorts out
a shared file.

With an epic named, only that epic's sub-issues are looked at, so the batch
fills from them however many other cards sit above them in Todo.
"""


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
        if sum(1 for c in considered if not c["reason"]) == size:
            break
        considered.append(card | {"reason": reason_left_out(card, started)})
    return considered


def reason_left_out(card: dict, started: frozenset[str]) -> str | None:
    if card["open_blockers"]:
        return "blocked by " + ", ".join(card["open_blockers"])
    if card["waits_on_answer"]:
        return "waits for an answer to a lesson question"
    if card["identifier"] in started:
        return "started earlier in this run and stopped before reaching Doing"
    return None

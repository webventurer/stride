"""Picks the cards still to come that can hear a merged card's lessons.

A card can hear one when it is in the merged card's batch and not yet merged,
in Doing or In Review; when it is in Todo; or when it waits in Backlog or
Backburner under the merged card's epic. Whether a lesson applies to a card is
the judgement `/linear:finish` makes from this list.
"""

from todo_order import is_epic

BEING_BUILT = ("Doing", "In Review")
WAITING_IN_EPIC = ("Backlog", "Backburner")


def epic_id(card: dict) -> str | None:
    parent = card["parent"]
    return parent["id"] if parent and is_epic(parent) else None


def cards_to_come(
    cards: list[dict], epic_members: set[str], batch: set[str]
) -> list[dict]:
    found = {
        card["identifier"]: {
            "identifier": card["identifier"],
            "title": card["title"],
            "state": card["state"]["name"],
        }
        for card in cards
        if can_hear(card, epic_members, batch)
    }
    return list(found.values())


def can_hear(card: dict, epic_members: set[str], batch: set[str]) -> bool:
    if is_epic(card):
        return False
    state = card["state"]["name"]
    if state in BEING_BUILT:
        return card["identifier"] in batch
    if state in WAITING_IN_EPIC:
        return card["identifier"] in epic_members
    return state == "Todo"

"""Puts a project's Todo cards in the order stride will work them.

Cards run by priority, Urgent first and No priority last, and keep their
current board order within a priority. A card never sits above the Todo card
it's waiting on, and a blocker outside Todo changes nothing. Epic cards are
left out of the order, so they keep their place, and every work card is given
a place below the highest epic.

The order comes from a rule, not judgement, so two runs over the same board
give the same order. `linear_cli.py order-todo` reads the board and writes it.
"""

NO_PRIORITY_RANK = 5
EPIC_PREFIX = "Epic: "
SORT_ORDER_GAP = 0.01


def is_epic(card: dict) -> bool:
    return card["title"].startswith(EPIC_PREFIX)


def epic_cards(cards: list[dict]) -> list[dict]:
    return [c for c in cards if is_epic(c)]


def cards_in_work_order(cards: list[dict]) -> list[dict]:
    work = [c for c in cards if not is_epic(c)]
    on_board = sorted(work, key=lambda c: c["sortOrder"])
    return cards_below_their_blockers(sorted(on_board, key=priority_rank))


def priority_rank(card: dict) -> int:
    return card["priority"] or NO_PRIORITY_RANK


def cards_below_their_blockers(ranked: list[dict]) -> list[dict]:
    in_todo = {c["identifier"] for c in ranked}
    blockers_in_todo = {
        c["identifier"]: set(c["blockers"]) & in_todo for c in ranked
    }
    placed: list[dict] = []
    held: list[dict] = []
    for card in ranked:
        held.append(card)
        place_unblocked_cards(held, blockers_in_todo, placed)
    return placed + held


def place_unblocked_cards(
    held: list[dict], blockers_in_todo: dict, placed: list[dict]
):
    free = next(
        (c for c in held if is_unblocked(c, blockers_in_todo, placed)), None
    )
    while free:
        held.remove(free)
        placed.append(free)
        free = next(
            (c for c in held if is_unblocked(c, blockers_in_todo, placed)), None
        )


def is_unblocked(
    card: dict, blockers_in_todo: dict, placed: list[dict]
) -> bool:
    return not blockers_in_todo[card["identifier"]] - {
        c["identifier"] for c in placed
    }


def new_sort_orders(ordered: list[dict], epics: list[dict]) -> dict[str, float]:
    slots = rising(sorted(c["sortOrder"] for c in ordered), below_epics(epics))
    return {c["identifier"]: slot for c, slot in zip(ordered, slots)}


def below_epics(epics: list[dict]) -> float:
    return max((e["sortOrder"] for e in epics), default=float("-inf"))


def rising(slots: list[float], above: float) -> list[float]:
    previous = above
    for i, slot in enumerate(slots):
        slots[i] = previous = max(slot, previous + SORT_ORDER_GAP)
    return slots

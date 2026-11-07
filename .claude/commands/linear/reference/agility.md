# Agility

> **What this is**: why a card's start check reads what has changed since the card was written, before any work on the card begins. [`/linear:start`](../start.md) step 3 runs that check, and [card start review](card-start-review.md) is the reviewer's brief.

<mark>**A plan is a map, not a contract.** When the ground changes, update the map before you walk on.</mark>

A card is written before the work around it happens. Cards in an epic are often drafted together, before any of them has shipped, and then they wait. While a card waits, the ground moves: a sibling card ships, a pattern doc lands on `main`, a comment on an open card settles a question the card guessed at. A builder who follows the card as written follows the old plan, and the end check then judges the change against promises nobody wants any more.

So every card start begins with the agile loop:

1. **Find out where you are.** Read what changed since the card's description last changed: commits that reached `main`, and comments on the epic's open sibling cards.
2. **Adjust your understanding.** Any promise the change has overtaken is a `stale` finding, naming the change and proposing new wording.
3. **Take the small step.** Build the card as it now reads.
4. **Repeat.** The next card starts the same way, with this one's work as part of the ground it reads.

## An example

In codefu's epic WB-922, story WB-924 said the coordinator writes Test 2's hidden tests. While a sibling card was open, a pattern doc landed on `main` that has a fresh writer session write them instead, so the coordinator never reads the hidden tests. A start check that reads only finished siblings can't see that doc. One that reads what reached `main` since the card's description last changed finds it, and the card is reworded before anyone builds the old plan.

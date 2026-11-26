# Favour speed of implementation over exhaustive testing

> Build quickly, prove each step with quick checks, and test by eye and with spot tests at the end.

While a piece of work is being built, give each card enough checking to prove what it changed, and save the thorough check for the end: do it once, when the whole piece of work is done rather than at the end of each card, by going through the result by eye and spot testing it, which means trying a few cases picked by hand. Every card keeps its unit tests written first, before-and-after screenshots where the change can be seen, the build and test run, and every review a stride command runs, including the card check at the start and the end, the simplification review and the commit review. What goes is the extra layers a builder is tempted to add on top: a scripted end-to-end comparison of old and new, the same live run repeated, a check run again after a change that leaves behaviour as it was. Every check and re-run a stride command asks for still happens. `/linear:finish` asks for no new end card check after a [behaviour-neutral change](../../../commands/linear/reference/card-check.md#a-behaviour-neutral-change-needs-no-fresh-check): only unpromised docs or card wording changed, and neither a promise nor behaviour did. Without this, a card can spend most of its time proving the same thing several ways. It is like calling an inspector back after every brick instead of once the wall is up.

## The test

Before adding a check of your own to a card, ask: **would this find something that the checks already running would miss and that can't wait until the end?** If yes, add it. If no, leave it out: either it adds nothing, or the thorough check at the end can cover it.

## Worked example: moving four pages to a new framework

An app has four pages to move to a new framework, one card per page, and each new page has to behave like the old one. The careful choice is to prove that on every card.

| | What was done | What it cost |
|:--|:--------------|:-------------|
| **Before** | Each card ports its page with unit tests, then writes a script that serves the old and new pages side by side, repeats the same steps on both in a browser and compares the results | A new comparison written, debugged and rerun for each of four pages, then thrown away. It confirms what the unit tests and the end card check already show |
| **After** | Each card ports its page with unit tests written first and takes screenshots before and after. When all four are done, the person who asked for the move uses every page by hand and spot tests the cases that matter most | The tests and screenshots on each card, and one sitting with the finished pages at the end |

Each page still has its unit tests, its screenshots and every stride review, so a card that breaks something they cover is still caught on that card. What goes is the second proof of the same behaviour. The price is that a difference only a person would notice may wait until the end to be found, and is then fixed there, with a test so it stays fixed. When a fifth page arrives, it gets the same tests, screenshots and reviews, and one check by hand when that piece of work is done.

## Where it stops

<mark>This principle doesn't cover work that can't be undone or that spends money.</mark> Deleting a person's files, starting a paid video render and taking a payment are checked before they run, because a check at the end arrives after the loss. [Be agile](be-agile.md) takes over there: when a step can't be backed out of, find out where you are before you take it.

## Related

- [Be agile](be-agile.md): the quick check after each step is how the step teaches you something before the next one.
- [Do the simplest thing that works](simplest-thing-that-works.md): the same restraint applied to what gets built, where this applies it to how the building is checked.
- [Don't build it until you need it](yagni.md): a comparison script that finds nothing new is code nobody needed.

## Source

No longer source exists; written fresh for the pack.

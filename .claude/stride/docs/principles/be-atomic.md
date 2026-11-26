# Give each commit, pull request and card one purpose (be atomic)

> One commit, one purpose. One pull request, one deliverable. One card, one outcome.

A unit of work is atomic when it is one complete, indivisible thing: everything inside it serves one purpose, and nothing inside it could be removed without breaking that purpose. The word comes from the Greek *atomos*, uncuttable. Atomic is about purpose, not size: renaming a function across 30 files is one purpose, and a single file holding a bug fix and an unrelated refactoring is two. Without it, reverting a commit undoes two unrelated things, a reviewer has to untangle changes that have nothing to do with each other, and a card can't be called done because half of it still isn't.

## The test

Before you commit, open a pull request or write a card, apply any of these:

- **The description test.** Can you describe it in one sentence without "and" joining unrelated ideas? "Fix the null check in payment validation" is atomic; "Fix the null check in payment validation and update the README" is not, unless the README change documents the fix.
- **The removal test.** For each part, ask: if I removed this, would the rest still be a coherent, complete change? If yes, the part serves a different purpose and goes in its own unit. If removing it leaves a hole, it belongs.
- **The revert test.** If you undid the whole unit, would exactly one logical thing disappear? If several unrelated things would, it isn't atomic.

Three reasons for combining changes feel natural at the time and don't pass these tests:

- **Proximity.** Changes made in the same session, in the same file or for the same task feel like they belong together. None of those is a reason to combine them.
- **"While I was in there".** A fix you notice while working on something else is a separate unit of work. Do it separately.
- **Convenience.** Shipping things together because it's easier now makes them harder to revert, review and understand later.

## Worked example: a fix and a rename in the same session

An author fixes a bug where invoice totals round the wrong way. While in the file, they notice the variable `amt` is used for the amount throughout the invoice module, and rename it to `amount` in all 12 files that use it. Both changes are finished, tested and sitting in the same working copy.

| | What was done | What it cost |
|:--|:--------------|:-------------|
| **Before** | One commit, "Fix invoice rounding and rename amt", holding the one-line rounding fix and the rename across 12 files | The reviewer has to find one changed line among dozens of renamed ones. When the fix later turns out to be wrong for credit notes, reverting it also reverts the rename, and every file that used `amount` since breaks |
| **After** | Two commits: "Fix rounding of invoice totals" with the one line and its test, and "Rename amt to amount in the invoice module" across 12 files | The fix reads as one line and can be reverted on its own. The rename is large but is one purpose, so it reviews as a single pattern repeated |

Splitting cost one extra commit message. Each commit now passes the revert test: undoing either removes exactly one thing. The size of the rename never mattered; the 12 files serve one purpose, so they stay together.

The same holds for pull requests and cards. A pull request that ships the fix and the rename together is harder to review and riskier to merge, and a card that asks for both can't be closed until both are done, even when one was finished on day one.

## Where it stops

<mark>A unit that serves one purpose should not be cut further, because dividing it breaks the change.</mark> A rename split into one commit per file, or a fix committed apart from the test that proves it, leaves each piece incomplete on its own. The removal test cuts both ways: a part whose removal leaves a hole belongs inside.

Atomicity applies to the work you hand over, not to how you work while the shape is still unclear. [Earn the split](avoid-premature-organisation.md) sets out where one gives way to the other.

## Related

- [Give each piece of code one reason to change](single-responsibility-principle.md): the same idea for code. Single responsibility is about structure; atomicity is about action. Both ask whether this is one thing or several pretending to be one.
- [Earn the split](avoid-premature-organisation.md): owns the boundary between working as one blob and handing over one purpose at a time.
- Skill: `/commit` applies this principle, grouping changes into one commit per purpose.

## Source

Distilled from codefu's `.claude/docs/concepts/atomicity.md`, which stride carries unchanged as `.claude/stride/docs/concepts/atomicity.md`, and which also covers functions, classes, database transactions and deployments. The worked example is written for this page.

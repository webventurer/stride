# Check the card at the start and the end

> The card is the agreement. Check it is a good one before the work starts, and check the work keeps it before it merges.

## The check

Before a change merges, ask:

1. **Has someone who never saw the reasoning compared the change with the card?** The author reads their intent into the code; a stranger reads only what is there
2. **Does every promise on the card have a verdict?** "Looks done" is not a verdict on any one promise
3. **If the code and the card disagree, who decided which one changes?** Never the agent alone

<mark>Passing every other review does not mean the change does what the card said. Only a check against the card asks that question.</mark>

## Problem

A card is the agreement about what a piece of work will do: its expected outcome, its edge cases, its constraints, how to test it. The reviews that run before merge each ask something else. Is the code as simple as it can be? Is each commit one change? Does the work fit the Vision? None of them reads the card's promises against the finished change, so a change can pass all of them and still break a promise.

That is what happened in the premium-alerts story MM-961. The only comparison of the finished work with its card ran after the merge. It found two ways the code reports a signal's history as complete when the card says it must not, and the simplification, atomicity and naming reviews had all passed it. With unattended mode on, there is no human approval step either, so nothing stood between the broken promise and `main`.

The tempting repair is the dangerous one. When code and card disagree, rewriting the card to match the code makes the check pass and the agreement worthless.

## The convention

### At the start

<!-- The start-of-work check of the card itself (WB-760) fills this section. -->

*To be written — the check that a card's promises are clear and checkable before work begins.*

### At the end

- **When it runs.** `/linear:start` runs the check after validation and the simplification review, before it opens the pull request. `/linear:finish` runs it again before merging whenever the branch's content or the card's wording has changed since the last passing check, so a fix pushed or a promise reworded after the check is checked too
- **Who checks.** A fresh reviewer that sees only the card and the change — never the author's reasoning, the plan or the conversation
- **What it returns.** Every promise on the card — each expected outcome, edge case, constraint and test scenario — with one verdict
- **Where the result lives.** The pull request carries the verdict table, one row per promise, with fingerprints of the exact content and card wording that were checked

| Verdict | Meaning | What happens |
|:--------|:--------|:-------------|
| **Kept** | The change does it, and a named test or line proves it | Nothing |
| **Kept, unproven** | The change appears to do it, but nothing proves it | The author adds the proof, then the check runs again |
| **Broken** | A concrete scenario shows the change does not do it | The author fixes the code, then the check runs again |
| **Unclear** | The card's wording cannot be checked, or contradicts itself | Stop and ask the user |

A change merges only when every promise is kept. Fixes and re-checks run without asking, in unattended mode too, for up to three rounds; then the run stops and the user decides. A card that makes no checkable promise stops the run rather than passing silently.

### Never quietly rewrite the card

- The agent never edits a card to make a verdict pass
- When the card itself looks wrong, the run stops and shows the promise and its verdict. The user decides whether to fix the code or change the card, in interactive and unattended mode alike
- A changed card gets a comment on the card saying what changed, why, and that the user signed off. The check then runs again against the new wording

## Example

Verdicts from the post-merge review of MM-961, the kind this check now gives before merge.

### Before

```text
# ❌ Every review passes; no one reads the card
simplification review: nothing to remove
commit atomicity: all atomic
Vision trace: verified
→ merged
```

### After

```text
# ✅ Each promise gets a verdict before merge
"The API reads while cron writes; a reader never sees a half-written file"
  → kept: the history is written to a temporary file and swapped in
"Concurrent reads"
  → kept, unproven: correct, but no test exercises it
"A per-signal page without [the plan-added row] proves nothing, however short"
  → broken: a 1-row signal page with no plan-added row, fetched after a gap,
    turns the signal complete: true
→ merge refused until the broken promise is fixed and the proof added
```

## Why this is useful

- What merges is what was agreed, not what the author believes was agreed
- A broken promise surfaces as a concrete scenario while it is still cheap to fix, not as a follow-up after merge
- Unattended runs keep a real check in place of the human approval they skip
- The card stays trustworthy, because it never bends to match the code without the user saying so
- A reader of the pull request sees, promise by promise, what the change keeps

## When to avoid

- `/linear:quick` work, which has no card until after it merges
- Discovery spikes whose purpose is to learn what the result should be — there is nothing to keep yet
- As a substitute for a good card. A vague card gets unclear verdicts; fix the card, not the check

## Related conventions

- **[Specify the result, not the edit](specify-the-result-not-the-edit.md)** — a card written as results is a card whose promises can be checked
- **[Derive the plan when work starts](derive-the-plan-when-work-starts.md)** — the plan may change; the card's promises stay fixed, and this check holds the work to them
- **[Ask for the disproof](ask-for-the-disproof.md)** — a broken verdict must name the scenario that breaks the promise, not just doubt it

---

_The card is the agreement. Check the work keeps it, and never bend the card to fit the work._

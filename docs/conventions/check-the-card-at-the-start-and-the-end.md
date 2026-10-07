# Check the card at the start and the end

> The card is the agreement. Check it is a good one before the work starts, and check the work keeps it before it merges.

## The check

Before work starts on a card, and again before the change merges, ask:

1. **Can every promise on the card be shown kept or broken?** A vague promise passes every check, because nothing can fail it
2. **Has someone who never saw the reasoning compared the change with the card?** The author reads their intent into the code; a stranger reads only what is there
3. **Does every promise on the card have a verdict?** "Looks done" is not a verdict on any one promise
4. **If the code and the card disagree, who decided which one changes?** Never the agent alone

<mark>Passing every other review does not mean the change does what the card said. Only a check against the card asks that question.</mark>

## Problem

A card is the agreement about what a piece of work will do: its expected outcome, its edge cases, its constraints, how to test it. The reviews that run before merge each ask something else. Is the code as simple as it can be? Is each commit one change? Does the work fit the Vision? None of them reads the card's promises against the finished change, so a change can pass all of them and still break a promise.

That is what happened in the premium-alerts story MM-961. The only comparison of the finished work with its card ran after the merge. It found two ways the code reports a signal's history as complete when the card says it must not, and the simplification, atomicity and naming reviews had all passed it. With unattended mode on, there is no human approval step either, so nothing stood between the broken promise and `main`.

The end check can only be as good as the promises it reads. A promise like "the history is reliable" can never be shown kept or broken, so it passes whatever the code does. Cards in an epic are usually drafted together at planning time, before any of them has shipped, so a promise can also go stale while it waits: an earlier card changes the code, and the later card still promises something that no longer fits.

The tempting repair is the dangerous one. When code and card disagree, rewriting the card to match the code makes the check pass and the agreement worthless.

## The convention

### At the start

- **When it runs.** `/linear:start` runs it right after the Vision check, before a branch exists or any code is written — for each card as it is started, never for a whole epic at once, so a later card is checked against what the earlier ones actually shipped
- **Who checks.** A fresh reviewer that reads the card, `VISION.md`, the current code and, for a card in an epic, what its finished sibling cards shipped — never the conversation that planned it
- **What it reports.** Only problems, each naming the card's line and proposing new wording

| Finding | Meaning | Stops the run when |
|:--------|:--------|:-------------------|
| **Uncheckable** | A promise has no observable result — "works well", "is robust" | Always |
| **Contradictory** | Two promises cannot both hold, or the current code already makes one impossible | Always |
| **Missing** | The current code plainly has an edge case on the card's path that the card does not mention | How the edge case is handled decides whether a stated promise is kept |
| **Stale** | A promise or its Vision trace no longer fits, given what a sibling card shipped | A promise no longer fits. A Vision trace alone is a note, because `/linear:finish` checks the trace again |
| **Mechanism** | A promise is met by making an edit, whether or not the result it serves holds — "move the retry logic into its own file" | The edit is the card's only statement of that result. A card created before 6 October 2026, when card language began asking for behaviour, gets a note |

Each finding is a **stop** or a **note**. A stop is a promise the builder would have to guess at, or that the end check couldn't judge; anything that doesn't stop the run is a note.

- **No findings:** work starts without a prompt
- **Notes only:** they're posted as one comment on the card and work starts, in both modes
- **Any stop:** the run pauses before a branch exists. In interactive mode the user accepts, rewords or rejects each stop and the run continues; in unattended mode the run ends and leaves them for the user, because a card changes only with sign-off. Notes are shown alongside, and any not acted on go into the one comment

The start check feeds the end check. Every promise that survives it can be shown kept or broken, so the verdicts at the end mean something: a kept promise was really tested, and a broken one has a real scenario.

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

- The agent never edits a card to make a finding or a verdict go away
- When the card itself looks wrong, the run stops and shows the promise and its verdict. The user decides whether to fix the code or change the card, in interactive and unattended mode alike
- A changed card gets a comment on the card saying what changed, why, and that the user signed off. The check then runs again against the new wording

## Example

The end verdicts come from the post-merge review of MM-961; the start finding is illustrative.

### Before

```text
# ❌ No one reads the card, at either end
"The history is reliable" rides along from planning, untested
simplification review: nothing to remove
commit atomicity: all atomic
Vision trace: verified
→ merged
```

### After

```text
# ✅ At the start: every promise must be checkable
"The history is reliable"
  → uncheckable: nothing in the finished work could show it false
    proposed: "complete is true only when every row since the
    plan-added row is held"
"covered_until is the newest report time on the latest page in an
 unbroken run, never the time a page was fetched"
  → no finding: it can be shown kept or broken

# ✅ At the end: each promise gets a verdict before merge
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
- A vague or stale promise is fixed before code is written against it, while it is still cheap to change
- A broken promise surfaces as a concrete scenario while it is still cheap to fix, not as a follow-up after merge
- Unattended runs keep a real check in place of the human approval they skip
- The card stays trustworthy, because it never bends to match the code without the user saying so
- A reader of the pull request sees, promise by promise, what the change keeps

## When to avoid

- `/linear:quick` work, which has no card until after it merges
- Discovery spikes whose purpose is to learn what the result should be — there is nothing to keep yet
- As a substitute for writing a good card. The start check flags weak promises and proposes wording; deciding what the card should promise stays with the user

## Related conventions

- **[Specify the result, not the edit](specify-the-result-not-the-edit.md)** — a card written as results is a card whose promises can be checked
- **[Derive the plan when work starts](derive-the-plan-when-work-starts.md)** — the plan may change; the card's promises stay fixed, and this check holds the work to them
- **[Ask for the disproof](ask-for-the-disproof.md)** — a broken verdict must name the scenario that breaks the promise, not just doubt it

---

_The card is the agreement. Make it checkable before the work, check the work keeps it before the merge, and never bend the card to fit the work._

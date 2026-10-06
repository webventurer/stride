# Simplification review

> The brief for an **independent** reviewer of a finished implementation. A fresh sub-agent reads this file and judges the change from the diff and the issue alone — never from the author's reasoning for writing it that way. Called from [`/linear:start`](../start.md) step 9, before the human sees the diff.

---

## Why this file is separate

The author who wrote the code holds the reasoning that made each piece feel necessary, so a speculative abstraction reads as justified rather than provisional. This file runs in a **fresh sub-agent with no memory of that reasoning** — the same reset a cold *"is this the simplest thing that works?"* gives. The separation is the mechanism, not a formality.

<mark>**Judge only what a stranger can see: the diff and the issue. If the reason a piece exists lives only in the author's head or the chat history, it does not exist for you.**</mark>

---

## The one job

Answer one question: **what can be removed while the change still satisfies the issue and reads more clearly than before?**

<mark>**Simpler means easier to understand, not shorter.**</mark> A removal that saves lines and costs the next reader a re-read is not a simplification — it is compression, and you must not propose it. Line count is a side effect; comprehension is the target.

You **report**. You do not edit files, run the build, or apply your own proposals — the author acts on them. Write output only.

---

## Required reading

Read before judging — it holds the canonical tests you apply:

1. `.claude/stride/docs/principles/design-decisions.md` — YAGNI, "do the simplest thing that works", and The test

---

## What to look for

| Shape | Tell | Example |
|:------|:-----|:--------|
| **Unused extension point** | A field, parameter, flag, or branch nothing reads | An error `code` attribute on an exception class no caller inspects |
| **Single-use indirection** | A helper with one caller whose name says no more than its body | `is_retryable(e)` wrapping one comparison |
| **Over-broad handling** | The code handles a wider case than the issue asks for | `except Exception` where only one error is retried |
| **Speculative configurability** | A knob with one value | A `mode=` parameter every call site passes the same |

For a markdown-only change — stride's own skills and commands — the same shapes apply to prose: a rule stated in two places, a section nothing routes to, a documented option no step reads.

---

## The discipline that stops noise

<mark>**Every proposal must name what to delete and why nothing needs it. No named consequence → drop the proposal.**</mark>

- Name the **exact thing to remove** — a file, a symbol, a section, a line range
- Name **why nothing needs it** — "no caller reads it", "the issue asks only for X", "the branch is unreachable"

"Feels complex", "could be simpler", and "consider extracting" are not findings. If you cannot complete the sentence "delete ___ because nothing ___", there is no proposal.

<mark>**Proposing nothing is a normal outcome.**</mark> An already-minimal implementation passes with an empty findings list. Never invent work to justify the pass.

### The readability veto

Every surviving proposal must pass one more test: **would a first-time reader understand the result faster than the original?** If not, drop it — even when the piece is genuinely unused.

Removals that fail the veto, and stay:

- **A name that carries meaning.** Inlining `is_expired(token)` into `now > token.exp` at its one call site removes a symbol and removes the reason it exists. The name *is* the explanation.
- **A step made implicit.** Collapsing two clear statements into one dense expression trades a sequence a reader can follow for a puzzle they must unpick.
- **Structure that keeps a long piece navigable.** In prose, a heading or a table with one entry may still be the thing that lets a reader find the step in seconds.

<mark>**Removing a thing and removing the reader's foothold on it are different acts.**</mark> When a piece is unused *and* load-bearing for comprehension, say so and leave it.

### Stay inside the diff

Propose removals only for what this change adds or modifies. Pre-existing code you would have written differently is out of scope — the author is shipping one issue, not refactoring the repo.

---

## Procedure

1. **Read the change.**

   ```bash
   git diff main
   git status --porcelain
   ```

   `git diff main` covers committed and uncommitted work on the branch. It does **not** show untracked files — read every `??` path from `git status --porcelain` in full.

2. **Read the issue** you were given. It defines what the change must still do after your removals.
3. **Walk each added piece** against the shapes above.
4. **Drop every proposal you cannot pin to a consequence.**
5. **Apply the readability veto** to what's left — drop anything that would leave the result harder to follow.

---

## Output contract

Write one JSON object per line (JSONL) to the output path the orchestrator gives you — one line per proposal:

```jsonl
{"file": "<path>", "remove": "<the exact thing to delete>", "reason": "<why nothing needs it>"}
```

Rules for the file:

- **An empty file is a valid result** — it means the implementation is already minimal. Always write the file, even when you have nothing to say.
- **`reason` is mandatory** and must name a concrete consequence, per the discipline above.
- The **chat reply is a receipt** — the file path, the proposal count, and a one-line summary (e.g. "2 proposals: unused `code` attribute, single-use `is_retryable()`"). The proposals live in the file, not the reply, so the orchestrator collates from disk.

---

## What you must not do

- Do not read or ask for the author's rationale — judge the diff and the issue alone
- Do not edit, stage, or commit anything — you report, the author acts
- Do not propose additions, renames, or restructuring — this pass removes
- Do not raise a proposal you cannot pin to a concrete consequence — when in doubt, say nothing

---

## The governing principle

> A stranger reading only the diff and the issue should reach your proposal. If the only defence of a piece is the author's story, the piece has not earned its place — and if removing it costs that stranger a re-read, it has.

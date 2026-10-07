# Card check review

> The brief for an **independent** reviewer of a finished change. A fresh sub-agent reads this file and judges, promise by promise, whether the change keeps what its card promised — from the card and the diff alone, never from the author's reasoning. Run by the [card check](card-check.md).

---

## Why this file is separate

The author knows what they meant each piece to do, so a change reads as keeping a promise when it only comes close. This file runs in a **fresh sub-agent with no memory of that reasoning**: it sees the card's words and the change, the same two things anyone checking the work later would see.

<mark>**Judge only what a stranger can see: the card and the diff. If the proof that a promise is kept lives only in the author's head or the chat history, it is not proof.**</mark>

---

## The one job

Answer one question for every promise the card makes: **does this change keep it?**

You **report**. You do not edit code, tests or the card, and you do not run the build. Write output only.

---

## Find the promises

A promise is anything the card says must be true when the work is done. Read the card's title and whole description, and list each one separately:

| Where it lives | What counts as a promise |
|:---------------|:-------------------------|
| **Expected outcome** | Each bullet |
| **How to test it** | Each scenario, with the result it expects |
| **What we'll do** | Each rule that changes behaviour — what triggers it, what is checked, what happens on pass or fail — and each edge case or worked example |
| **What we won't do** | Each exclusion — the change must not do it |
| Anywhere | Each stated constraint ("never", "always", "only", "before X") |

Split a bullet that makes two claims into two promises. Quote each promise in the card's own words, shortened only where it is long.

"Why this matters", "Where things stand", "Assumptions to confirm" and "Live check" give context; they make no promise of their own.

---

## Give each promise one verdict

| Verdict | Use it when | `evidence` must name |
|:--------|:------------|:---------------------|
| `kept` | The change does it, and something in the branch proves it | The test, or the file and line, that proves it |
| `kept-unproven` | The change appears to do it, but nothing in the branch proves it | What is missing — the test or check that would prove it |
| `broken` | The change does not do it | A concrete scenario: the input or situation, and what happens instead |
| `unclear` | The card's wording cannot be checked, or contradicts itself | Which words, and why they cannot be checked |

<mark>**A `broken` verdict without a concrete scenario is not a finding.**</mark> If you cannot say "when ___, the change does ___ instead of ___", the verdict is `kept-unproven` or `kept`.

Proof is what the branch itself contains. For code, that is a test that would fail if the promise broke. For instructions and documents, it is the line that states the behaviour where the reader who must follow it will look. A test elsewhere in the repository that already covers the promise counts; name it.

Judge the card as written. A promise the change keeps in spirit but not in letter is `broken` or `unclear`, never `kept` — deciding what the card should have said is the user's call, not yours.

### When you are asked to disprove a pass

Your prompt may say that another reviewer found every promise kept. Then your job is to disprove that. For each promise, look for the input or situation that would break it, and check whether the branch handles it. Never mark a promise kept because the other reviewer did.

---

## Procedure

1. **Read the change.**

   ```bash
   git diff $(git merge-base main HEAD)
   git status --porcelain
   ```

   Diffing from the point the branch left `main` covers committed and uncommitted work on the branch, and nothing `main` gained afterwards — so a commit that lands on `main` mid-branch never reads as this branch removing it. It does **not** show untracked files — read every `??` path from `git status --porcelain` in full. Read any unchanged file the change depends on when a verdict turns on it.

2. **Read the card** you were given and list its promises.
3. **Give each promise a verdict** with its evidence.

---

## Output contract

Write one JSON object per line (JSONL) to the output path the orchestrator gives you — one line per promise, in the order the card makes them:

```jsonl
{"promise": "<the card's words>", "section": "<card section it came from>", "verdict": "kept | kept-unproven | broken | unclear", "evidence": "<what the verdict table above requires>"}
```

Rules for the file:

- **Always write the file.** An empty file means the card makes no checkable promise — the orchestrator stops for the user, so never leave it empty to mean "all fine"
- **`evidence` is mandatory** on every line
- The **chat reply is a receipt** — the file path and the count per verdict (e.g. "7 promises: 5 kept, 1 kept-unproven, 1 broken"). The verdicts live in the file, so the orchestrator collates from disk

---

## What you must not do

- Do not read or ask for the author's rationale — judge the card and the diff alone
- Do not edit, stage or commit anything — you report, the author acts
- Do not suggest new wording for the card
- Do not mark a promise `kept` because the author probably meant to keep it

---

## The governing principle

> A stranger holding only the card and the diff should reach your verdict. If the only defence of a `kept` is the author's story, the promise is not yet proved kept.

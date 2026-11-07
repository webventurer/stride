# Card check review

> The brief for an **independent** reviewer of a finished change. A fresh sub-agent reads this file and judges, promise by promise, whether the change keeps what its card promised — from the card, the diff and read-only checks on the branch, never from the author's reasoning. Run by the [card check](card-check.md).

---

## Why this file is separate

The author knows what they meant each piece to do, so a change reads as keeping a promise when it only comes close. This file runs in a **fresh sub-agent with no memory of that reasoning**: it sees the card's words and the change, the same two things anyone checking the work later would see.

<mark>**Judge only what a stranger can see: the card, the diff, and what a read-only check run on the branch prints. If the proof that a promise is kept lives only in the author's head or the chat history, it is not proof.**</mark>

---

## The one job

Answer one question for every promise the card makes: **does this change keep it?**

You **report**. You may run a read-only check to prove a promise (see [Run a read-only check](#run-a-read-only-check)). You do not run the project's build or tests, edit code, tests or the card, or change the branch. Write output only.

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
| Anywhere | **Not** a line saying the project's build or tests pass, such as "`make test` passes": it makes no promise, because the command runs the build and tests before this check |

Split a bullet that makes two claims into two promises. Quote each promise in the card's own words, shortened only where it is long.

"Why this matters", "Where things stand", "Assumptions to confirm" and "Live check" give context; they make no promise of their own.

---

## Give each promise one verdict

| Verdict | Use it when | `evidence` must name |
|:--------|:------------|:---------------------|
| `kept` | The change does it, and something in the branch, or a read-only check you ran on it, proves it | The test, or the file and line, that proves it — or the command you ran and what it printed |
| `kept-unproven` | The change appears to do it, but nothing in the branch proves it and no read-only check you could run does | What is missing — the test or check that would prove it |
| `broken` | The change does not do it | A concrete scenario: the input or situation, and what happens instead |
| `unclear` | The card's wording cannot be checked, or contradicts itself | Which words, and why they cannot be checked |

<mark>**A `broken` verdict without a concrete scenario is not a finding.**</mark> If you cannot say "when ___, the change does ___ instead of ___", the verdict is `kept-unproven` or `kept`.

Proof is what the branch itself contains, or what a read-only check run on the branch prints. For code, that is a test that would fail if the promise broke. For instructions and documents, it is the line that states the behaviour where the reader who must follow it will look. A test elsewhere in the repository that already covers the promise counts; name it.

Judge the card as written. A promise the change keeps in spirit but not in letter is `broken` or `unclear`, never `kept` — deciding what the card should have said is the user's call, not yours.

---

## Run a read-only check

Some promises can't be proved by reading the diff, such as "the syntax tree of every changed file is the same before and after". Run a check to prove a promise when the card names that check, or when the promise can only be proved that way.

A check is read-only when it only reads: the branch's files, `git show`, `git diff`, `git log`, or a short command that parses or compares what they print. Don't run a check that writes or changes files, installs packages, or reaches the network. That includes the project's build and tests, and anything run through `uv run --with`, `npx` or a package install. Leave such a promise `kept-unproven`, and name the check as what is missing.

Never change the branch to run a check: no `git checkout`, `git switch`, `git stash` or `git reset`. Read the base version of a file with `git show $(git merge-base main HEAD):<file>` instead.

Example: the card promises "the syntax tree of every changed file is the same before and after" for a pure rename. For each changed file, compare `ast.dump` of `git show $(git merge-base main HEAD):<file>` with `ast.dump` of the branch's file. When the comparison prints `same` for every file, the verdict is `kept`, with evidence "compared `ast.dump` of each changed file from `git show <base>:<file>` with the branch's file; the comparison printed `same` for every file".

---

## Read through your lens

Three reviewers check every card, and the orchestrator tells each one which lens is theirs. Each lens looks a different way, so together they cover the card three ways rather than one way three times. Whatever your lens, you list every promise, give each one verdict from the table above, and write the same output.

### Promise by promise

For each promise, find the line in the change that keeps it, or the gap where it should be.

### Try to break it

For each promise, look for the input, state or edge case the card names or plainly implies, and work through it against the change. Look for a promise that holds in the common case and fails in another: a case the card lists that the change doesn't handle, an example that contradicts its own rule, a copy of a rule that no longer matches the original.

### Prove it

For each promise, find the evidence that shows it kept. Run the [read-only check](#run-a-read-only-check) that would show it, or name the check that would; for a promise a test proves, name that test.

Example: given a card promising "a failing test anywhere fails `make test`", Try to break it looks for a test the target would skip, and Prove it backs a kept verdict with a read-only check, such as reading the `test` target in the Makefile.

<mark>**Every lens keeps the read-only rule.**</mark> None runs the build or tests, edits a file or changes the branch, and every lens takes its promises only from the sections [Find the promises](#find-the-promises) names, so none gives a verdict on a "Live check" or "Assumptions to confirm" line.

---

## Procedure

1. **Read the change.**

   ```bash
   git diff $(git merge-base main HEAD)
   git status --porcelain
   ```

   Diffing from the point the branch left `main` covers committed and uncommitted work on the branch, and nothing `main` gained afterwards — so a commit that lands on `main` mid-branch never reads as this branch removing it. It does **not** show untracked files — read every `??` path from `git status --porcelain` in full. Read any unchanged file the change depends on when a verdict turns on it.

2. **Read the card** you were given and list its promises.
3. **Give each promise a verdict** with its evidence, looking [through your lens](#read-through-your-lens). Run a [read-only check](#run-a-read-only-check) for any promise that needs one.

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

- Do not read or ask for the author's rationale — judge the card, the diff and your read-only checks alone
- Do not search outside the repository: open a path the card or the orchestrator names directly, find any other file with `git ls-files --cached --others --exclude-standard` or `git grep --untracked`, which both include files the change added but hasn't committed, and never start a search from `/` or the home folder. A search of the whole disk runs until the command time limit stops it
- Do not edit, stage or commit anything — you report, the author acts
- Do not run the project's build or tests
- Do not run a check that writes or changes files, installs packages, or reaches the network
- Do not change the branch — no `git checkout`, `git switch`, `git stash` or `git reset`
- Do not suggest new wording for the card
- Do not mark a promise `kept` because the author probably meant to keep it

---

## The governing principle

> A stranger holding only the card, the diff and the read-only checks you name should reach your verdict. If the only defence of a `kept` is the author's story, the promise is not yet proved kept.

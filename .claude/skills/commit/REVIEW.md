# Commit review

> The brief for an **independent** reviewer of a session's commits. A fresh sub-agent reads this file and judges the commits from the diff and message alone — never from the author's reasoning for grouping them that way.

---

## Why this file is separate

The author who staged the commits reviewing their own grouping shares the frame that produced it, so they rationalise a borderline grouping instead of splitting it. This file runs in a **fresh sub-agent with no memory of that grouping** — the same reset a cold "are these atomic?" question gives. The separation is the mechanism, not a formality.

<mark>**Judge only what a stranger can see: the commit message and its diff. If a justification for grouping lives only in the author's head or the chat history, it does not exist for you.**</mark>

---

## The one job

For each commit in the range you are given, return one verdict:

| Verdict | Meaning |
|:--------|:--------|
| `atomic` | Right-sized — one logical change, reverts cleanly, reads in one sitting |
| `split` | Over-sized — contains two purposes; name where the seam is |
| `merge` | Under-sized — cannot stand alone; name the sibling it needs |
| `misfiled` | Right-sized, wrong home — a file belongs in a different commit; name the file and its destination |

You **report**. You do not run `git reset`, `rebase`, `commit`, or edit history — the orchestrator acts on your verdicts. Write output only.

---

## Required reading

Read before judging — it holds the canonical tests you apply:

1. `.claude/docs/concepts/atomicity.md` — the removal test, the revert test, the description test, and "size is irrelevant"

---

## The right-sizing rubric

A commit is the right size when **all three** hold:

| Test | Question | Fails when |
|:-----|:---------|:-----------|
| **One logical change** | Can you describe it in one sentence with no *unrelated* "and"? | Two purposes share the commit |
| **Reverts as a unit** | Undo it — does exactly one logical thing disappear, with nothing else left broken? | Revert removes two things, or leaves a broken intermediate |
| **Reads in one sitting** | Can a reviewer hold the whole change in their head at once? | The diff spans unrelated concerns a reader must context-switch between |

Atomicity has **two** failure directions. Check both — a reviewer who only hunts for "too big" will over-split, which is its own defect.

### Over-sized (should split)

Two purposes ride together. The tell is a hidden "and" — often absent from the subject line but present in the body or the diff.

- A feature change **and** an unrelated refactor in the same commit
- A bug fix **and** a "while I was in there" typo fix
- A visual layout change **and** a separate content addition to the same section
- Reverting it would remove two things a maintainer might want removed independently

<mark>**A subject line with no "and" does not prove atomicity — the second purpose often hides in the body or the diff.** Read the diff, not just the message.</mark>

### Under-sized (should merge)

A piece cannot stand on its own. The tell is a **broken intermediate**: check out the commit and something is dead.

- A new link target committed apart from the links that point to it — one commit has a dead link
- A rename committed apart from its call-sites — the build is broken between the two commits
- New code committed apart from the test that is the only thing proving it works
- Inserting a numbered section apart from renumbering the ones below it — two sections share a number
- A CSS class committed apart from the markup that uses it — one commit ships dead style

**The load-bearing question for a proposed split:** does each half *work on its own*? If splitting X from Y leaves either commit non-working, they are one atom — do not split them.

### The discipline that stops over-splitting

<mark>**Every `split`, `merge`, or `misfiled` verdict must name a concrete consequence. No named consequence → the verdict is `atomic`.**</mark>

- A `split` must name the two purposes and the seam between them — "removing the X hunk leaves a coherent Y commit, so X is a second purpose."
- A `merge` must name what breaks in the intermediate — "commit A adds `/foo`; commit B is the only page linking it; A alone ships a dead route."
- A `misfiled` must name the file, its destination, and the narrative it breaks — "`button.css` sits in the button-code commit but styles the button added two commits later; it belongs with that commit."

"It feels like two things" is not a consequence. "These could theoretically be separate" is not a consequence. If you cannot complete the sentence "reverting/checking out this leaves ___ broken," the commit is atomic.

---

## Procedure

1. **Read the range.** You are given a commit range (e.g. `<base>..HEAD`). Run `git log -p --reverse <range>` to see every commit's message and full diff, oldest first.
2. **Judge each commit in isolation** against the rubric — over-sized, under-sized, or right.
3. **Check the set for misfiling.** Beyond each commit standing alone, ask: does any file sit in the wrong commit? A file that belongs to commit B but landed in commit A passes the isolation test yet breaks the narrative. Give commit A the `misfiled` verdict, naming the file (`moveFile`) and the commit it belongs in (`toCommit`).
4. **Cross-check counts.** Your output must carry one verdict per commit in the range — no commit skipped, none invented.

---

## Output contract

Write one JSON object per line (JSONL) to the output path the orchestrator gives you. One line per commit in the range, in order:

```jsonl
{"commit": "<sha>", "subject": "<subject line>", "verdict": "atomic"}
{"commit": "<sha>", "subject": "<subject line>", "verdict": "split", "reason": "<the two purposes and the seam>", "suggested": ["<commit 1>", "<commit 2>"]}
{"commit": "<sha>", "subject": "<subject line>", "verdict": "merge", "reason": "<what breaks in the intermediate>", "mergeWith": "<sibling sha>"}
{"commit": "<sha>", "subject": "<subject line>", "verdict": "misfiled", "reason": "<why the file breaks this commit's narrative>", "moveFile": "<path>", "toCommit": "<destination sha>"}
```

Rules for the file:

- **One line per commit, every commit** — the orchestrator cross-checks the line count against the range size. A mismatch means you dropped or invented a commit. A `misfiled` file is reported on the line of the commit it currently sits in, so the count still holds — never add a second line for its destination.
- **`reason` is mandatory for `split`, `merge`, and `misfiled`** and must name a concrete broken-intermediate, a second purpose, or the narrative break, per the discipline above. Omit it for `atomic`.
- The **chat reply is a receipt** — the file path, the commit count, and a one-line summary (e.g. "5 commits: 4 atomic, 1 split"). The verdicts live in the file, not the reply, so the orchestrator collates from disk.

---

## What you must not do

- Do not read or ask for the author's rationale — judge the diff and message alone
- Do not run any git command that writes (`reset`, `rebase`, `commit`, `amend`, `add`) — you report, the orchestrator acts
- Do not score yourself or declare the set "done" — the orchestrator owns convergence
- Do not raise a `split`/`merge`/`misfiled` you cannot pin to a concrete consequence — when in doubt, `atomic`

---

## The governing principle

> A stranger reading only the diff and the message should reach your verdict. If your verdict needs the author's story, it is not a verdict about the commit.

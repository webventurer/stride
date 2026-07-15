---
name: commit
description: Create atomic git commits using a multi-pass methodology — content, standards, final review, post-commit verification, and an independent review of the set. Use when committing code or documentation changes. Triggers on "commit", "git commit", or when the user asks to commit changes.
---

# Commit

> Create atomic git commits using a multi-pass methodology that separates content decisions from formatting standards.

## Skill documents

| File | Purpose |
|:-----|:--------|
| [SKILL.md](SKILL.md) | Overview, commit format reference, atomicity rules |
| [WORKFLOW.md](WORKFLOW.md) | Five-pass execution sequence |
| [REVIEW.md](REVIEW.md) | The independent reviewer's brief — over-split, under-split, and misfiled rubric, run by a fresh sub-agent in Pass 5 for 2+ commits |
| [references/chris-beams-commit-style.md](references/chris-beams-commit-style.md) | The 7 rules our format is built on |

---

## When to use

- User asks to commit staged or unstaged changes
- User runs `/commit`
- Changes are ready and the user explicitly requests a commit

## When NOT to use

- User is exploring changes or running `git diff`
- No changes exist to commit
- User has not explicitly asked for a commit

---

## Quick reference

<mark>**One logical change per commit. Separate concerns across passes: content, standards, final review, post-commit verification, and an independent review of the set.**</mark>

---

## Required reading

Read before executing:

1. `.claude/docs/patterns/git/atomic-git-commits.md` — the full atomic commit methodology and Conventional Commits standard

---

## Key principles

| Principle | What it means |
|:----------|:-------------|
| Atomic | One complete logical change per commit — not by size, by coherence |
| Imperative mood | "Add feature" not "Added feature" — completes "If applied, this commit will..." |
| WHY not what | Body explains the reasoning, not just a list of files |
| Working state | All tests pass after the commit |
| Selective staging | Stage files per logical change, not everything at once |

### Test-driven commits

Every commit should pass all tests:

1. Write failing tests for new functionality
2. Implement the feature
3. Ensure all tests pass
4. Commit the complete change

This ensures each commit represents a working state of the codebase.

---

## The coherence test

> If you removed any file from this commit, would the remaining files still represent the same complete logical change?

- If removing a file leaves a hole → it belongs
- If removing a file leaves a perfectly coherent commit → it does not belong

### The "and" test

<mark>**If your commit message contains "and", you probably have two commits.**</mark> "Add login validation **and** fix header styling" is two changes wearing a trench coat. If you can't describe the commit without "and", split it.

---

## The atomicity balance

Atomicity has two failure modes, not one. Find the sweet spot between them:

**Over-atomising** (too many commits):
- Splitting a one-line CSS fix and a related prop addition into separate commits
- Committing a function rename separately from updating its callers
- One commit per file when all files serve the same change

**Under-atomising** (too few commits):
- Lumping a bug fix, a new feature, and a formatting cleanup into one commit
- Committing everything changed in a session as a single commit
- Mixing unrelated changes that happened to touch the same area

**The sweet spot**: all changes share a common purpose that you can explain in one sentence. If removing any change leaves a hole, it belongs. If adding another change would require a second explanation, it doesn't.

**The test**: look in both directions. Ask "am I grouping unrelated things?" (under-atomising) AND "am I splitting apart things that need each other?" (over-atomising). When neither question raises a flag, you've found the right granularity.

For a session of 2+ commits, this two-directional test is operationalised in [WORKFLOW.md](WORKFLOW.md#pass-5-independent-atomicity-review-2-commits) Pass 5: a fresh sub-agent applies the [REVIEW.md](REVIEW.md) rubric to the finished set with no knowledge of how you grouped it — the independence that catches what your own review talks itself past.

### Forward and backward: prevent, then detect

The skill solves atomicity from both directions — once as each commit is formed, once after the set exists.

- **[Group by purpose](#group-by-purpose-not-by-origin) is the forward pass.** As each of the 1+ commits is formed, you draw its boundary by *purpose*, so every commit goes in atomic. Prevention, at authoring time.
- **The [independent Pass 5 review](WORKFLOW.md#pass-5-independent-atomicity-review-2-commits) is the backward pass.** Once the set exists, a fresh reviewer retrospectively checks the groupings hold — no hidden "and", no misfiled file. Detection, after the fact.

You need both because the forward pass runs in *your* head: you share the frame that produced the grouping, so you rationalise a borderline call. The backward pass runs in *clean* context — that is what catches what the forward pass talked itself past. Prevention narrows the errors; independent detection catches the residue.

---

## Group by purpose, not by origin

<mark>**Group changes by what they're *for*, not by where they came from.**</mark> A commit's boundary is its purpose — the one thing it accomplishes — never the circumstances that produced it. *When* the changes were made, *who* asked for them, *which tool* emitted them, *which directory* they touched: all of that is origin, and origin is irrelevant to atomicity. Ask "what is this change *for*?" and let the answer draw the line.

This is the move that catches the most common AI mistake: lumping a whole session into one commit because it was one conversation. A session is an origin; it spans as many purposes as it spans, and each gets its own commit.

**Worked example — a multi-day session, split by purpose.** One sitting cleaned up three days of notes: a 20 June daily, a behavioural lesson lifted from a 22 June exchange, and a 23 June opportunity thread (an inbound, its call-prep, the board update). "All one session" would have been a single dump. By *purpose*, it was eleven commits — each daily its own record, the lesson its own change, the pitch materials their own, the board state its own. Same keystrokes, eleven purposes, eleven gifts to your future self.

The corollary: the list below catalogues the *origins* that masquerade as purposes. Each is a way of grouping by where the change came from — reject all of them.

## Common AI atomicity mistakes

<mark>**These are not valid reasons for combining changes into one commit — each is an *origin*, not a purpose:**</mark>

- **Modified in the same session** — files changed during one conversation are not automatically one atomic commit
- **Sharing a prefix** — using `docs:` on two unrelated documentation changes does not make them atomic
- **Requested as one task** — "update the docs and fix the bug" is two tasks and two commits
- **Touching the same area** — editing three files in `src/auth/` for different reasons is three commits
- **"While I was in there" changes** — noticing a typo while fixing a bug does not make the typo part of the bug fix
- **Produced by the same tool** — a test survey flags 3 files that need tests. Each test suite is its own commit. They share a prefix (`test:`) and came from the same analysis, but removing one leaves the others perfectly coherent
- **Same change in different places** — applying the same refactor to two independent directories is two commits, not one. Each stands alone — either could be reverted without breaking the other
- **Tests for pre-existing code** — <mark>**did the production code exist before this session?**</mark> If yes, tests are a separate `test:` commit. If no (new class + its test file), they belong together

**Example of mixed changes that should be separated**:

```bash
# BAD: Two different logical changes in one commit
git add TODO.md docs/research/ai-coding/what-is-a-frame.md
# This mixes: project management (TODO) + documentation (frame concept)

# GOOD: Separate atomic commits
git add TODO.md
.claude/hooks/do_commit.sh -m "build: Add TODO.md with AI frame loading system entry"

git add docs/research/ai-coding/what-is-a-frame.md
.claude/hooks/do_commit.sh -m "docs: Create comprehensive frame concept documentation"
```

---

## Patterns that DO belong together

Some pairings look like two commits but are genuinely one atomic change. Splitting them ships a broken intermediate state.

- **Tests with new code** — if the production code is new in this commit (not pre-existing), the test file belongs with it. Splitting would ship an intermediate commit where the class exists but is unverified. (The inverse rule — tests for pre-existing code are separate — is in the "Common AI atomicity mistakes" list above.)

- **New link target with the links to it** — when you add a new definition, reference page, or glossary entry AND repoint existing mentions to it, keep both in one commit. Splitting would leave an intermediate commit where the target exists but nothing links to it — or where links point at the old target which has been removed but the new one isn't yet in place. The atomic state is: target exists AND is used.

- **Deletion with its cleanup** — removing a concept means deleting its definition AND retargeting anything that pointed at it. Splitting would leave dead links for the duration of one commit.

- **Rename with all its callers** — renaming a function and updating every call-site is one commit. Splitting would leave compile/runtime errors between the two commits.

**The shared pattern**: if splitting would make any intermediate commit non-working (dead links, unverified code, broken builds, orphaned definitions), the pieces are one atomic change. The [coherence test](#the-coherence-test) catches this — *"would removing a file leave a hole?"* — because each piece *is* load-bearing for the others.

---

## Intent before diff

<mark>**"What is the user trying to accomplish?"** — ask this before looking at the diff.</mark>

The diff tells you *what changed*. The user's intent tells you *why*. AI consistently writes commit messages that describe the mechanics of the diff ("fix image paths", "rename directory") rather than the purpose ("add PDF export with embedded images"). The commit log should read like a story of what was accomplished, not a changelog of file operations.

## Describe what is, not what was

<mark>**Commit messages describe the destination, not the journey.** Don't narrate the previous state — describe what the current state does.</mark>

The diff already shows what changed. Narrating the previous version inside the message ("the previous intro claimed X — that's wrong, now it says Y") doubles the reader's work without adding information. Worse, the retrospective framing rots — six months later the "previous" state is gone from anyone's mind, and the message reads as confusing context-free criticism.

| Avoid | Prefer |
|:------|:-------|
| "The previous intro claimed X. That's wrong: ..." | Describe what the intro now says |
| "Removed the old behaviour and replaced it with..." | Describe the new behaviour |
| "Before, the function did Y. Now it does Z." | "The function does Z" |
| "Fixed the typo where..." | Describe the corrected text |
| "No longer does X" | Describe what it does instead |

This is the same principle as the auto-squash rule in `/linear:start` — *describe where you ended up, not how you got there.* The git log should read as if the work was right the first time. If the only context the reader has is the commit message and the diff, the message should make sense from that alone.

## Content focus blindness

Both people and AI consistently miss formatting standards while focused on content logic. The multi-pass approach solves this by making standards verification a dedicated step (Pass 2) separate from content decisions (Pass 1).

---

## Commit message format

```text
<type>: <Subject line — 50 chars max>

<Body explaining WHY — wrap at 72 chars>

- Bullet points for specific changes
```

### Standard prefixes

| Prefix | Use for |
|:-------|:--------|
| `feat:` | New features or functionality |
| `fix:` | Bug fixes and corrections |
| `docs:` | Documentation only changes |
| `refactor:` | Code restructuring without changing behaviour |
| `style:` | Formatting, white-space changes |
| `test:` | Adding or updating tests |
| `build:` | Build system or dependency changes |
| `chore:` | Maintenance tasks |
| `perf:` | Performance improvements |
| `ci:` | CI configuration changes |

### Subject line rules

- Standard prefix, lowercase (e.g. `feat:`, `fix:`)
- Capitalize first word after colon ("Add" not "add")
- Imperative mood ("Add" not "Added")
- No period at end
- Under 50 characters total

### Body rules

- Blank line after subject
- Wrap at 72 characters
- Explain WHY, not just what
- Start with explanatory paragraph before bullets
- Add warmth — show care for users and future developers

### Example

```text
fix: Fix null pointer in payment validation

When users had incomplete billing data, validation would crash
instead of showing helpful errors. This adds proper null checks
and returns meaningful validation messages.

- Add null checks for all required fields
- Return validation errors instead of exceptions
- Include tests for edge cases with missing data
```

---

## The pre-commit atomicity trap

Pre-commit hooks can accidentally cause you to commit multiple unrelated files together:

1. You stage one file: `git add file1.js`
2. You run `git commit` and hooks fix OTHER files
3. You run `git add -A` to include the fixes
4. **Result**: your commit now includes unrelated files

**Prevention**: Keep formatting off the commit path entirely. `/commit` runs no formatter (see [WORKFLOW.md](WORKFLOW.md) Pass 0), so there's no whole-repo reformatting to drag unrelated files in. Format via your editor, or run `pnpm fix` on its own and land the result as a separate `style:` commit. If a consumer's git hook reformats files mid-commit, stage only the files for *this* change — never `git add -A` the hook's other fixes.

---

## How to fold

To fold a change into an existing commit — a typo fix, a missed edge case, a wording correction that belongs to work already in flight — collapse it into the target so the rewritten history reads as if the work was right the first time. Only the target's SHA changes; commits unrelated to the fold keep their identity.

### Pattern A — Fixup sits on top of its target (common case)

When the change being folded is the most recent thing on the branch and the target is `HEAD~1`, use **soft-reset + amend**. The agent can complete the fold end-to-end; no user step required.

```bash
# 1. Record the fold intent as a fixup commit (optional but recommended —
#    creates a reflog entry the agent or user can recover from)
git add <files>
.claude/hooks/do_commit.sh --fixup=<sha>     # writes "fixup! <original subject>"

# 2. Collapse the fixup into its target
git reset --soft HEAD~1                       # undoes the fixup, keeps changes staged
.claude/hooks/do_commit.sh --amend --no-edit  # folds staged changes into the target

# 3. If the branch was already pushed, update the remote
git push --force-with-lease
```

`--no-edit` keeps the target's original commit message — the journey-shaped fixup commit message disappears, and the log reads as a single coherent commit. `--force-with-lease` only overwrites the remote if its tip matches what the agent last fetched, so it can't silently clobber someone else's work.

If there's no fixup commit yet (the change is still in the working tree) and the target is HEAD, skip step 1 and step 2's reset — just `git add` then `do_commit.sh --amend --no-edit`.

### Pattern B — Target is older, with unrelated commits between (uncommon)

The soft-reset trick collapses everything between target and HEAD into the target — wrong when there are unrelated commits in between. Use autosquash with a no-op sequence editor instead:

```bash
git add <files>
.claude/hooks/do_commit.sh --fixup=<sha>
GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash <sha>~1
```

`--autosquash` only takes effect with `-i`, but `-i` doesn't have to mean "human in the loop" — `GIT_SEQUENCE_EDITOR=:` makes the "edit the todo list" step a no-op, so git accepts the autosquash arrangement as-is. The base of the rebase is the commit *before* the target, so the target is replayed and the fixup folds into it; unrelated commits above ride on top with their messages preserved (new SHAs because their parent changed).

If the branch was already pushed, update the remote with `git push --force-with-lease`.

### Agent capability summary

| Action | Agent can do? |
|:--|:--|
| Write a `--fixup` commit | ✅ via `do_commit.sh --fixup=<sha>` |
| Soft-reset + amend (Pattern A) | ✅ when fixup is on top of target |
| Force-push-with-lease after fold | ✅ when the user has authorised it for this work |
| `git rebase -i --autosquash` | ✅ with `GIT_SEQUENCE_EDITOR=:` to accept the autosquash arrangement non-interactively |
| Bare `git commit --amend` | ❌ pre-tool-use hook blocks it; use `do_commit.sh --amend` |

### When to fold vs. new commit

| Situation | Use |
|:--|:--|
| Original commit on a local branch, work-in-progress | Fold (Pattern A or B) |
| Original commit is HEAD | `do_commit.sh --amend --no-edit` directly (skip the fixup step) |
| Original commit on `main` and pushed widely | New commit — don't rewrite shipped history without strong reason |

### What not to do

- ❌ `git reset --hard HEAD~N` + cherry-pick replay — clean but creates new SHAs across commits that didn't change
- ❌ `git reset --soft <base>` + recommit chain spanning multiple commits — error-prone manual content reconstruction (the single-step soft-reset in Pattern A is fine because there's no chain to reconstruct; `--no-edit` preserves the target's message)
- ❌ Bare `git commit --amend` — blocked by the pre-tool-use hook
- ❌ Bare `git rebase -i` — opens an editor the agent can't drive; pass `GIT_SEQUENCE_EDITOR=:` to make it non-interactive

---

## Execution

<mark>**Read and follow every step in [WORKFLOW.md](WORKFLOW.md).**</mark>

---

## What atomic commits afford

> Not what a commit *is* — what it makes possible.

Atomic commits aren't just a discipline. They're a position that creates possibilities that don't exist when changes are lumped together:

| Affordance | What becomes possible |
|:-----------|:----------------------|
| **Automatic changelog** | Typed prefixes + clear subjects let tooling generate changelogs mechanically — no human curation required |
| **Narrative arc** | The commit log reads like a story of the journey — what was built, why, in what order. Future developers inherit *context*, not just code |
| **Independent revertibility** | Any commit can be undone without collateral damage — you remove one idea, not a tangle of ideas |
| **Bisectability** | `git bisect` works because every commit is a working state — the bug hides in exactly one commit, not somewhere across a session dump |
| **Review in logical steps** | Reviewers follow the author's reasoning one thought at a time, instead of reverse-engineering intent from a wall of diffs |
| **Cherry-picking** | Individual changes move cleanly between branches — a fix doesn't drag an unrelated feature along for the ride |
| **Blame that explains** | `git blame` points to a commit that says *why*, not a grab-bag that says "various changes" |

<mark>Before atomic commits, these possibilities don't exist. After, they're available whether you use them or not — that's what makes them affordances, not features.</mark>

---

## The governing principle

> Make each commit a gift to your future self — one complete idea, clearly explained, independently revertible.

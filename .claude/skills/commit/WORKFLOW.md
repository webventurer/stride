# Commit workflow

<mark>**Follow these steps in order. Do not skip any step.**</mark>

---

## Execution sequence

| Pass | Action | Goal |
|:-----|:-------|:-----|
| 0 | **Pre-flight** | Identify atomic changes |
| 1 | **Content** | Stage selectively, verify one logical change |
| 2 | **Standards** | Verify message format against checklists |
| 3 | **Final review** | Sanity check before committing |
| 4 | **Post-commit** | Verify atomicity after committing |
| 5 | **Independent review** | For 2+ commits: a fresh sub-agent verifies the set ([REVIEW.md](REVIEW.md)) |

---

## Before you start

Read [SKILL.md](SKILL.md) first — it contains the coherence test, AI atomicity mistakes, commit format reference, and the pre-commit atomicity trap.

For a run that produces 2+ commits, [Pass 5](#pass-5-independent-atomicity-review-2-commits) hands the finished set to an independent reviewer defined by [REVIEW.md](REVIEW.md). Read that file too — it is the reviewer's brief and defines the over-split, under-split, and misfiled rubric the whole skill is calibrated against.

---

## Pass 0: Pre-flight

**Goal**: Understand the changes and plan the atomic commits before staging.

> <mark>**`/commit` does not run a formatter.**</mark> Formatting is a separate concern from deciding what belongs in a commit — running a whole-repo formatter here reformats unrelated files and pollutes the atomic commit. Keep the tree formatted on its own axis: your editor, or a manual `pnpm fix` landed as its own `style:` commit.

### Step 1: See what changed

Run `git status` to see all changed files and `git diff` to understand the changes.

**Record the session base** — before creating any commit, capture the current tip so [Pass 5](#pass-5-independent-atomicity-review-2-commits) can review exactly the commits this session adds, no more:

```bash
BASE=$(git rev-parse HEAD)   # the commit range this session reviews is $BASE..HEAD
```

This is exact where `git log --since=today` is not — it never sweeps in a commit from earlier work.

### Step 2: Per-file independence gate

<mark>**If 2+ files are changed, STOP. Write one sentence per file before doing anything else:**</mark>

```text
[file] → [what it does independently]
[file] → [what it does independently]
```

**Show these sentences in your output.** Then read them back: if a sentence is incomplete without another file, they belong together. If every sentence stands alone, each is a separate commit. **Do not proceed to Pass 1 until the sentences are written and the grouping decision follows from them — not from session context, not from shared topic, not from "they were changed together".**

For large changesets (10+ files), group by directory or purpose first, then apply the per-file check within each group. The point is to evaluate independence before grouping — not to write 100 sentences.

**Files that belong together** — the test is incomplete without the implementation:

```text
login.ts       → Adds JWT validation to the login flow
login.test.ts  → Tests the new JWT validation
```

**Files that don't** — each sentence stands alone:

```text
meta-cognitive-framework.md  → Fixes link paths to use .claude/docs/ prefix
check_markdown_links.py      → Excludes hooks directories from link checking
```

This prevents concept-level grouping ("they're both about X") from overriding file-level independence. Write the sentences first, then let the sentences decide.

### Step 2b: Shared-file bleed check

<mark>**If a file appears in multiple commit groups, it contains two concerns. Do not commit the whole file with either group.**</mark>

After grouping, scan for files that serve more than one commit. Common examples:

- `pyproject.toml` with two new entry points for two different features
- A shared utility file with additions for different features (e.g. sync `send` for one commit, async `send_async` for another)
- A config file touched by both a feature and an unrelated fix

**When you find a shared file**, use one of these strategies:

| Strategy | When to use |
|:---------|:------------|
| **Temporary edit** | Remove the lines for the later commit, stage, commit, then restore them for the next commit |
| **`git add -p`** | When changes are in separate hunks that git can split cleanly |

**Example**: a `notifier.py` has both `send` (sync commit) and `send_async` (parallelisation commit). Temporarily remove `send_async`, commit the sync version, then add it back for the parallelisation commit.

**The test**: after staging, does `git diff --cached` show only changes for *this* commit's concern? If it shows changes for another commit's concern, you have bleed.

When no file appears in multiple commit groups, report **"No shared-file bleed"** and move on.

### Step 3: Count the commits

Ask: could any subset of these changes be reverted independently and still make sense?

| Signal | Action |
|:-------|:-------|
| All changes serve one purpose | Proceed as one commit |
| Changes serve different purposes | Separate into multiple commits |
| Bug fix + unrelated feature | Two commits |
| Code change + unrelated formatting | Two commits |

Check the [common AI atomicity mistakes](SKILL.md#common-ai-atomicity-mistakes) — do not group changes just because they were made in the same session, share a prefix, or touch the same area.

**Common multi-change scenarios**:

- Bug fix + unrelated feature improvement
- Documentation updates + code changes
- Refactoring + new functionality
- Multiple unrelated bug fixes
- New file creation + existing file modifications for different purposes

---

## Pass 1: Content

**Goal**: Stage the right files for one atomic change.

1. **Stage selectively** — `git add` specific files, not `git add -A`
2. **Review staged changes** — `git diff --cached`
3. **Verify completeness** — are all files needed for this change staged?
4. **Apply the [coherence test](SKILL.md#the-coherence-test)** — does removing any file leave a hole?

### Staging techniques

**Stage specific files**:

```bash
git add file1.js file2.js
```

**Stage partial file changes** (when one file contains changes for multiple commits):

```bash
git add -p filename.js
# Select which hunks belong to each atomic change
```

---

## Pass 2: Standards

**Goal**: Draft the commit message and verify formatting against [SKILL.md](SKILL.md#commit-message-format).

This is a dedicated pass because of [content focus blindness](SKILL.md#content-focus-blindness) — both people and AI miss formatting rules while focused on content logic.

### Intent before diff

<mark>**Before looking at the diff, ask: "What is the user trying to accomplish?"**</mark>

The diff tells you *what changed*. The user's intent tells you *why*. The commit message should reflect the purpose, not the mechanics.

| Trap | Example | Fix |
|:-----|:--------|:----|
| Describing the diff | "Fix image paths" | The purpose was "Add PDF export" — the path fix was just a means |
| Describing the last step | "Rename directory to hyphens" | The purpose was "Embed images in PDF" — the rename enabled it |
| Describing the tool | "Run md2pdf script" | The purpose was "Generate shareable PDF of event notes" |

**The test:** if someone reads only the commit log six months from now, will they understand what was accomplished — or just what files moved?

### Subject line checklist (50 chars max)

- [ ] **No "and" in the subject** — if present, split into separate commits ([the "and" test](SKILL.md#the-and-test)) — **AI frequently misses this**
- [ ] **Standard prefix used** (feat:, docs:, fix:, refactor:, style:, test:, build:, etc.) — **AI frequently misses this**
- [ ] **Subject capitalized after colon** ("feat: Add feature" not "feat: add feature")
- [ ] **Imperative mood** ("Add" not "Added" or "Adds")
- [ ] **Under 50 characters** total length
- [ ] **No period at end** of subject line
- [ ] **Completes**: "If applied, this commit will [your subject]"

### Body and content checklist (72 chars per line)

- [ ] **Blank line after subject** line
- [ ] **Wrap at 72 characters** maximum per line
- [ ] **Explains WHY** not just what changed
- [ ] **Describes what is, not what was** — no "previously this did X, now it does Y" narration ([describe what is, not what was](SKILL.md#describe-what-is-not-what-was)) — **AI frequently misses this**
- [ ] **Start with explanatory paragraph** before bullet points
- [ ] **Use bullet points for lists** of changes
- [ ] **One atomic change** (can be reverted independently)
- [ ] **Add warmth** — show care for users and future developers

### Commit execution

<mark>**Never use `git commit` directly — it is blocked by a PreToolUse hook.** Use the wrapper script instead.</mark>

Use multiple `-m` flags to avoid heredoc issues with special characters:

```bash
.claude/hooks/do_commit.sh -m "type: Subject line here" -m "Explanatory paragraph about
why this change was needed. Keep lines under
72 characters.

- Specific change one
- Specific change two"
```

### Pre-commit hook failures

If the commit fails because hooks fix files:

1. Review what the hooks changed
2. Stage the hook-fixed files **only if they belong to this atomic change**
3. If hooks fixed unrelated files, commit your atomic change first, then handle hook fixes separately (see [the pre-commit atomicity trap](SKILL.md#the-pre-commit-atomicity-trap))
4. Re-run the commit

---

## Pass 3: Final review

**Goal**: Last sanity check before the commit lands.

- [ ] Does this commit represent one complete idea?
- [ ] Do all tests pass?
- [ ] Re-read the commit message — does it tell a complete story?
- [ ] Check the diff one more time — are all changes intentional?
- [ ] Can this be reverted independently?
- [ ] Is anything missing?
- [ ] Would this make sense to someone reviewing it in 6 months?

This is the crucial last moment to catch anything that slipped through while focused on content (Pass 1) and formatting (Pass 2).

If any check fails, go back to Pass 1 or Pass 2 as needed.

---

## Pass 4: Post-commit verification

**Goal**: Verify the commit is truly atomic after it lands.

```bash
git diff --stat HEAD~1 HEAD
git log -1
```

- [ ] All files serve the single purpose described in the commit message
- [ ] No hitchhikers — could any file be removed and still leave a coherent change?
- [ ] No stowaways — are there files that serve a different purpose?
- [ ] Clean revert — if reverted, would it remove exactly one logical improvement?

### If verification fails

```bash
# Undo the commit but keep all changes staged
git reset --soft HEAD~1

# Unstage everything
git reset HEAD .

# Now re-stage and commit each logical change separately
git add <files-for-change-1>
.claude/hooks/do_commit.sh -m "prefix: First logical change"

git add <files-for-change-2>
.claude/hooks/do_commit.sh -m "prefix: Second logical change"
```

### Folding mistakes

If a commit has a small error (typo, missed file) that belongs to the same logical change:

```bash
git add .
.claude/hooks/do_commit.sh --amend --no-edit
```

Only use `--amend` for unpushed commits.

---

## Pass 5: Independent atomicity review (2+ commits)

<mark>**If this session produced 2+ commits, do not sign off on your own grouping. Hand the finished set to a fresh sub-agent that never saw why you grouped it that way.**</mark>

A single commit skips this pass — [Pass 4](#pass-4-post-commit-verification) already checked it in isolation, and with one commit there is no misfiling between commits. Two or more is where hidden "and"s and wrong-commit files cluster, and where reviewing your own work fails: you share the frame that made the grouping, so you rationalise a borderline call instead of splitting it. The fix is not another self-check — it is a reviewer with clean context. See [REVIEW.md](REVIEW.md) for why the separation is the mechanism.

The atomicity "and" test runs in the reviewer's clean context via [REVIEW.md](REVIEW.md), not as a self-check you run first — the Pass 2 subject-line "and" check is drafting hygiene, but re-judging your own grouping here only adds a rationalisation you might anchor on.

### The loop

1. **Spawn the reviewer.** Use the Task tool (`general-purpose`, model `opus` — the verdict is judgement-dense). Give it **only** the range and the output path — never your reasoning for the grouping:

   > Read `.claude/skills/commit/REVIEW.md` and follow it. Review the commits in `$BASE..HEAD`. Write one JSONL verdict per commit to `<output-path>`. Judge from the diff and message alone.

   Do not paste the diffs, your commit plan, or this conversation into the prompt. The reviewer runs `git log -p` itself. Its blindness to your grouping is the point.

2. **Collate from disk.** Read the JSONL file — not the sub-agent's chat reply. Cross-check: the line count must equal the number of commits in `$BASE..HEAD`. A mismatch means a commit was dropped or invented — re-run before trusting the verdicts.

3. **Act on the verdicts.** If every line is `atomic`, the gate is passed — stop. Otherwise, regroup:

   ```bash
   # Undo this session's commits; every change stays unstaged in the working tree
   git reset "$BASE"          # default --mixed: moves HEAD to $BASE and unstages all

   # Re-stage and commit each corrected group (Pass 1 + Pass 2)
   git add <files-for-group-1>
   .claude/hooks/do_commit.sh -m "prefix: First logical change"

   git add <files-for-group-2>
   .claude/hooks/do_commit.sh -m "prefix: Second logical change"
   ```

   Read each verdict's fields as you re-stage: a `split` becomes two groups at the named seam, a `merge` folds the named siblings into one, a `misfiled` moves the named `moveFile` into its `toCommit` group. Resetting to `$BASE` (not `HEAD~1`) is safe because everything above `$BASE` is this session's own unpushed work. For a one-line `merge` of adjacent tip commits, [fold](SKILL.md#how-to-fold) instead of a full reset.

4. **Re-review after acting.** Regrouping rewrites SHAs, so spawn a **new** fresh reviewer over the new `$BASE..HEAD`. Never reuse the previous reviewer or your own judgement of the fix — a fresh pass is the only trustworthy signal.

5. **Converge or escalate.** Loop until a full pass returns all `atomic`. Cap at **3 iterations**. Stop early and surface the verdicts to the user if:
   - the reviewer flip-flops (flags a commit you split, then flags the merged version) — a sign it is thrashing, not converging, and the call is genuinely yours, or
   - iteration 3 still returns a non-`atomic` verdict.

### Guarding against over-splitting

The reviewer earns a `split`/`merge`/`misfiled` only by naming a concrete consequence (a second purpose, a broken intermediate, or the narrative a misplaced file breaks). A verdict with no named consequence is noise — treat it as `atomic`. Do **not** regroup on "it feels like two things." REVIEW.md holds the reviewer to this; you hold it too when you act on the file.

**What this catches that Pass 4 doesn't:** Pass 4 checks one commit in isolation. Pass 5 checks the *set* — whether files landed in the right commit and whether the log tells one story per step. A file that belongs to commit B but ended up in commit A passes Pass 4 (both commits are internally coherent) but fails Pass 5 (the narrative is wrong). Independence catches what a self-review talks itself past.

---

## Output

After a successful commit, display the result:

```bash
git log -1 --format="%h %s%n%n%b"
```

<mark>**Always show the FULL commit message — subject AND body.** Do not truncate to just the subject line. The body contains the reasoning (the WHY) which is the most valuable part of the commit.</mark>

Format:

```text
Committed:

<hash> <subject-line>

<full-commit-body including the explanatory paragraph and bullet points>
```

**Bad** — truncating to subject only:
```text
Committed:

995f948 feat: Add create-website skill
```

**Good** — full message:
```text
Committed:

995f948 feat: Add create-website skill

Structured skill for scaffolding Next.js landing pages from
reference designs — CSS Modules + SCSS, Color Hunt palettes,
component-per-directory architecture, zero Tailwind.

- SKILL.md with full technology decisions and patterns
- Colour scheme workflow with Color Hunt integration
```

---

## Verification gate

<mark>**Every pass must complete before the commit is final.**</mark>

- [ ] Pre-flight: atomic changes identified
- [ ] Content: files staged selectively, coherence test passed
- [ ] Standards: message format verified against checklists
- [ ] Final review: sanity check passed
- [ ] Post-commit: atomicity verified, output displayed
- [ ] Independent review: if 2+ commits this session, a fresh sub-agent ([REVIEW.md](REVIEW.md)) returned an all-`atomic` pass (or the user signed off on a flagged verdict)

---
description: Merge an approved PR, clean up branches, and mark the Linear issue Done.
---

# Finish issue

Merge an approved PR, clean up branches, and mark the issue Done.

Accepts a Linear issue ID as argument: `/linear:finish PG-205`

If no argument is given, infer the issue ID from the current branch name (extract the `[A-Z]+-\d+` pattern, e.g. `PG-205`). If neither works, ask the user. The resolved value is `<issue-id>` — every Linear call below uses it, not the raw `$ARGUMENTS` token (which is empty on the no-argument path).

Workflow: `/linear:plan-work` → `/linear:start` (includes terminal review) → `/linear:fix` (if GitHub review feedback) → **`/linear:finish`**

Read [unattended mode](reference/unattended.md) before the first optional
prompt. Interactive mode keeps the choices below; unattended mode applies only
the deterministic branches named by this command.

## Rules

- Never merge if tests fail
- Never merge a branch whose own change has no passing card check against the card's current wording, unless all that changed since a passing check is [behaviour-neutral](reference/card-check.md#a-behaviour-neutral-change-needs-no-fresh-check): it touches no promise on the card and changes no behaviour ([favour speed of implementation over exhaustive testing](../../stride/docs/principles/favour-speed-of-implementation-over-exhaustive-testing.md))
- The merge commit message should read as if the work was done right the first time — no mention of rejections, fix cycles, or iterations
- Use `--merge` (not `--squash`) to preserve atomic commits in the branch
- Never force-delete branches

---

## Steps

### 1. Read the Linear issue

Fetch the issue via `linear_cli.py` *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
uv run .claude/tools/linear_cli.py issue get <issue-id>
```

Extract from the JSON: identifier, title, `gitBranchName`, current state, project milestone (if any), parent issue.

Stop if the issue cannot be found.

### 2. Precondition: the branch has commits and an open PR

`/linear:finish` only merges an existing PR — it never commits, pushes, or opens one (that's `/linear:start`'s job). Confirm both preconditions up front, so an early invocation refuses clearly instead of appearing to start the finish flow.

**No commits ahead of `main`?** Nothing has been committed yet, so there's nothing a PR could contain:

```bash
git log main..<gitBranchName> --oneline
```

If empty, stop:

> *"Nothing committed on this branch yet — `/linear:finish` only merges an existing PR. Run `/linear:start <issue-id>` to implement, commit, push, and open the PR first."*

**No open PR?** The work is committed but not yet up for merge:

```bash
gh pr list --head <gitBranchName> --json number,url,title,reviewDecision,mergeable
```

If the list is empty, stop:

> *"No open PR for this branch — `/linear:finish` has nothing to merge. Run `/linear:start <issue-id>` to push and open the PR first."*

Capture the PR `number`, `url`, and `mergeable` for the merge in step 9. This gate is the single PR precondition — later steps assume the PR exists and never re-stop on it.

**Write down late lessons.** A lesson learnt after the pull request opened, such as while merging `main` or fixing review feedback, goes under `## Lessons for later cards` in the pull request body before the merge, as [`/linear:start`](start.md) step 17 sets out: read the body with `gh pr view <number> --json body -q .body`, edit it in a file, and save it with `gh pr edit <number> --body-file <file>`.

### 3. Check repo state

Run `git status -sb`.

If there are uncommitted changes, warn and stop — suggest `/commit`.

### 4. Validate

Run the project's required checks, build command (e.g. `pnpm build`) and tests locally. Reuse a passing run from this task when the relevant files have not changed. Follow the [local validation merge rule](reference/unattended.md#merge-after-local-validation): CI runs in the background and is not a Stride waiting gate.

If anything fails, stop — do not merge. Show what failed.

### 5. Check for pending fixup commits

Before the merge, scan the branch for `fixup!` commits. These are journey-shaped commits meant to fold into an earlier target via `git rebase --autosquash` — if they land on `main` verbatim, the log fills with `fixup! feat: ...` subjects whose bodies don't explain why each change exists. That breaks the Vision criterion: *"Every commit on a stride-managed branch does one job, with no monolithic commits, and its message explains why."*

Count them:

```bash
pending=$(git log main..HEAD --format=%s | grep -c '^fixup!')
```

If `pending` is zero, skip silently and continue to step 6.

In unattended mode, autosquash the fixups with the commands below and
force-push with `--force-with-lease`. Rebase conflicts or a refused lease are
hard stops. Continue to step 6 after a successful push.

The remaining choices in this step are the interactive path.

Otherwise, surface the fixups and offer three paths:

```
N fixup commit(s) pending on this branch:
  - <fixup subject 1>
  - <fixup subject 2>
  - ...

Autosquash them now before merging? (y / n / abort)
```

- **y** → run the autosquash and force-push:

  ```bash
  base=$(git merge-base main HEAD)
  GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash "$base"
  git push --force-with-lease
  ```

  `--force-with-lease` refuses if the remote tip has moved since the last fetch, so it can't silently overwrite someone else's push. Continue to step 6 with the rewritten history.

- **n** → continue to step 6 as-is. The user has explicitly chosen to merge the fixups verbatim. The drift is named on the issue (via the prompt the user just saw), not silently shipped.

- **abort** → exit cleanly. Tell the user:

  > *"Autosquash the fixups manually (`GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash main && git push --force-with-lease`), then re-run `/linear:finish`."*

  Do not merge.

<mark>**Why interactive mode prompts.**</mark> Rewriting published history normally needs explicit user authorisation. Unattended mode supplies that authorisation through machine-local project config while `--force-with-lease` protects a moved remote.

<mark>**Why fixup-specific, not all journey commits.**</mark> `fixup!` commits have an unambiguous target encoded in their subject (per `--fixup=<sha>`), so autosquash collapses them deterministically. Other journey-shaped commits ("WIP", "address feedback") are a `/linear:start` step 14 concern — caught at push time, not merge time.

**Failure modes**:

- Rebase conflicts → abort the rebase (`git rebase --abort`), surface the conflict, tell the user to resolve manually and re-run.
- `--force-with-lease` refused → the remote moved between fetch and push. Fetch, re-run.

### 6. Check every commit belongs to this card

Follow [branch scope](reference/branch-scope.md): judge each commit in `git log origin/main..HEAD` against the card's purpose from step 1, and move any commit that serves something else to `main` or its own branch before merging. Continue to step 7 once every remaining commit belongs.

### 7. Confirm Vision outcome (before merge)

<mark>**This step fires *before* the merge.**</mark> When trace drift is caught here, the catch is still actionable — the criterion can ride alongside its originating feature on the same branch, instead of needing a follow-up `VISION.md` PR.

If the issue has no "Why this matters" section (legacy soft path from `/linear:start`), skip silently and continue to step 8.

Otherwise, before drafting any Linear comment in this step, read [Linear card
language](reference/card-language.md).

Run a **silent trace check** *before* deciding whether to prompt the user. Inputs (already in context from step 1 and the steps above):

- The criterion the issue's *Why this matters* section claims to advance.
- The branch's commit subjects: `git log main..HEAD --oneline`.
- The full `VISION.md` Success criteria list.

Read the commit subjects against the Success criteria and apply the [*revise, don't stretch*](https://github.com/webventurer/stride/blob/main/docs/patterns/revise-dont-stretch.md) strain test to the issue's stated trace. <mark>**Don't ask the user whether the trace fits — judge it yourself, then decide whether to interrupt.**</mark> Three outcomes follow.

#### Match — silent confirmation

The issue's stated trace matches the agent's best-fit criterion *and* the fit is unambiguous. Surface a single line and continue to step 8:

```
Trace verified against "<criterion>" — proceeding to the card check.
```

No y/n prompt. The common path runs without interruption (Vision criterion #3).

#### Different clean fit — surface the difference

The agent finds a different criterion that plainly fits, without tripping a
strain signal. Surface both candidates with the commit reminder. Interactive
mode stops so the user can decide:

```
Branch ready to merge:
  - <commit 1>
  - <commit 2>
  - ...

Issue's stated trace:
  "<stated criterion>"

Agent's best-fit reading:
  "<alternative criterion>"

Which plainly fits the work? (stated / alternative / neither)
```

The commit subjects are authored to be informative (atomic-commits discipline) — they're the canonical summary of what shipped. Single-commit branches still get the block.

<mark>**Explain the drift in plain English.**</mark> Describe what the doc or feature actually does in concrete terms, what the criterion actually says, and why the connection lands — following the [`/clear-speak` skill](../../skills/clear-speak/SKILL.md), stride's standard for plain language. The reader may know nothing about stride's meta-cognitive framework, so keep stride-internal vocabulary (`Distinction`, `operationalises`, `gate`, `judgement-worthy`, `trace` as a noun) out of user-facing copy.

A worked before/after:

> **Abstract first attempt:** *"The friction Distinction is the test maintainers reach for to decide whether friction is judgement-worthy. It operationalises criterion #3 — every 'is this gate firing on the right thing?' question runs through this Distinction."*
>
> **Plain-English follow-up:** *"What the doc does: it helps stride's maintainers decide what to do when a user complains that something in stride is annoying. Two possibilities — either the user is doing the wrong kind of work (stride is right to push back), or the gate is firing on a use case nobody designed for (stride should be calibrated). Criterion #3 says stride shouldn't interrupt unless the interruption is worth the user's attention. The doc is the test for which interruptions earn their place."*

Same content, ten times the readability.

- **stated**: the agent was overconfident; user override stands. Continue to step 8.
- **alternative**: post a one-line Linear comment via `uv run .claude/tools/linear_cli.py comment create <issue-id> --body "..."` naming the agent's drift catch and the user-picked criterion. Continue to step 8. The drift is named on the issue; the body isn't auto-rewritten.
- **neither**: drop into the no-exact-fit path below.

In unattended mode, post the same one-line comment naming the clean alternative
and continue without asking. No Vision edit is needed because an existing
criterion already plainly fits.

#### No exact fit — evolve the Vision

Use this path when the stated trace is strained and a re-read finds no other
criterion that plainly fits. Surface the commits, the closest criterion, and a
plain-English explanation of why the fit is thin.

Then tend the Vision with [`/vision-evolve`](../../skills/vision-evolve/SKILL.md),
in interactive and unattended mode alike. It changes `VISION.md` itself and
needs no sign-off. Post a one-line comment on the issue naming the gap, then
continue once the trace plainly fits the changed Vision.

#### When in doubt, ask

If the agent is genuinely uncertain whether any criterion plainly fits, fall
back to **No exact fit** rather than auto-confirming. <mark>**A false silent
confirmation is worse than a Vision update:** the silent match path's whole
value is *trustworthy* verification.</mark>

This step turns the "Why this matters" line from a write-once token into a
verified reference. A missing criterion rides alongside its originating feature
instead of needing a separate PR.

### 8. Check the change against its card

<mark>**This step runs last before the merge**</mark>, after every step that can change the branch, so it judges the card's change exactly as it merges.

Follow [card check](reference/card-check.md), starting from [Before merge: is the record current?](reference/card-check.md#before-merge-is-the-record-current). When every recorded verdict is Kept, Fixed or Not acted on, and the pull request's recorded check matches the card's own change and the card's current wording, continue to step 9. When every recorded verdict passes in that way and all that changed since the check is [behaviour-neutral](reference/card-check.md#a-behaviour-neutral-change-needs-no-fresh-check), note it in the pull request's record as that section sets out, then continue to step 9. Otherwise run the check once, fix what it finds, re-run validation (step 4) and record the new verdicts in the pull request before merging.

### 9. Merge (preserve commits)

Merge with `--merge` to preserve the atomic commits from the branch. The merge commit gets the default subject only — no body. The individual commits on the branch already explain what was built and why; duplicating that in the merge commit just creates drift between the two messages.

```bash
gh pr merge <number> --merge --subject "Merge branch '<gitBranchName>'" --body ""
```

Pass `--body ""` explicitly so `gh` does not fall back to the PR description.

### 10. Clean up branches, remove worktree, close the worktree tab

Detect the main repo path. Run `git worktree list` — the first entry is the main repo:

```bash
git worktree list
```

**All git commands must use `git -C <main-repo-path>`** to avoid depending on the worktree directory.

**Step 10a — Update the main checkout, only when nothing of the user's is in it:**

The main checkout is where the user may be mid-commit or on another branch. A finish that switched it would pull the card's work into their commit. Ask the script first; it fetches, changes nothing and prints one line:

```bash
.claude/tools/main_checkout_update.sh <main-repo-path> <gitBranchName>
```

When it prints `updated`, the checkout is on `main` or on this card's own branch with nothing uncommitted, staged or untracked and nothing unpushed. Fast-forward it:

```bash
git -C <main-repo-path> checkout main && git -C <main-repo-path> pull --ff-only
```

`--ff-only` moves `main` to GitHub's or changes nothing. Never rebase or merge the main checkout here: a rebase replays any stray local commit unasked, and a clash would leave the shared checkout half-way through a rebase for every job behind it.

When it prints `left: <reason>`, run neither the checkout nor the pull. The pull request merges on GitHub whatever the main checkout holds, so carry on with the remaining steps and say at the top of step 17's summary that the main checkout was left alone, the reason, and the steps that bring the card's work in:

| Printed | Steps for the user |
| --- | --- |
| `left: uncommitted changes` | commit or stash them, then run `git pull --rebase` on `main` |
| `left: unpushed commits` | run `git pull --rebase` on `main` |
| `left: on branch <name>` or `left: detached HEAD` | switch to `main`, then run `git pull --rebase` |
| `left: the fetch failed` | nothing was checked; say the fetch failed |

As a `/parallel-sessions` job, include the reason in the message to the coordinator that the card has merged.

When the checkout or the pull refuses, the pull request has already merged, so the refusal doesn't undo it or stop the finish: leave the main checkout as it is, carry on with the remaining steps, and report the refusal at the top of step 17's summary. Quote git's own error line and the output of:

```bash
git -C <main-repo-path> log origin/main..main
```

An empty log means no local commits are in the way, so the cause is something else, such as a failed checkout or no network; git's error line says which. The user or the coordinator decides what to do with the main checkout. As a `/parallel-sessions` job, include the refusal in the message to the coordinator that the card has merged.

**Step 10b — Tear down the worktree (if one was used):**

As a `/parallel-sessions` job, skip this step: the session is still running in the worktree, and the coordinator removes it once the session exits.

Otherwise, follow [worktree teardown](reference/worktree.md#teardown) — it removes the worktree and guides the user to close its tab in the current VS Code window. Do this **before** deleting the branch (git won't delete a branch a worktree has checked out). For an inline run with no worktree, it skips silently.

**Step 10c — Delete branches:**

Now that any worktree is gone, the branch can be deleted. As a `/parallel-sessions` job, the worktree is still there with the local branch checked out, so delete the local branch with the script below instead of the **Local** bullet, then delete the remote branch with the **Remote** bullet. The coordinator removes only the worktree folder.

```bash
.claude/tools/delete_job_branch.sh <gitBranchName>
```

It fetches, deletes the branch only when its work is on `origin/main`, detaches the worktree at the branch's own commit first, and prints `deleted` or `kept: <reason>`. It doesn't depend on step 10a: a main checkout left alone makes no difference. When it prints `kept: <reason>`, name the branch and the reason in step 17's summary and in the message to the coordinator, and carry on. Nothing force-deletes a branch.

- **Local**, for a run that isn't a `/parallel-sessions` job: `git -C <main-repo-path> branch -d <gitBranchName>` — use lowercase `-d` since the merge commit makes the branch fully merged. If already deleted, skip silently. When step 10a's pull was refused or the main checkout was left alone, it lacks the merge commit and `-d` can say the branch isn't fully merged: skip the local deletion, say so in the summary, and carry on
- **Remote**: `git -C <main-repo-path> push origin --delete <gitBranchName>` — if already deleted (GitHub may auto-delete), skip silently

### 11. Update Linear → done

Move the issue to **Done**:

```bash
uv run .claude/tools/linear_cli.py issue update <issue-id> --state Done
```

Only set Done status. Skip if already Done. Never set any other status.

### 12. Carry the lessons to the cards still to come

Before the next card starts, carry what this card taught to every card still to come. Follow [carry lessons](reference/carry-lessons.md). Carry the one-line result into the summary in step 17. As a `/parallel-sessions` job, also send that line to the coordinator at once, before step 13, because a card still being built may be about to open its pull request.

### 13. Check milestone completion

Skip this step if the issue had no milestone.

Otherwise, fetch issues attached to the milestone in non-Done states via `linear_cli.py`:

```bash
uv run .claude/tools/linear_cli.py milestone-open-issues <milestone-UUID>
```

If any nodes come back, the milestone has remaining work — skip silently.

If the nodes list is empty, all stories in the milestone are now Done. In
unattended mode, append the completion note without prompting; the empty
open-issue list makes this deterministic. In interactive mode, prompt:

```
All stories in *[Milestone name]* are complete — mark the milestone done?
```

If the user confirms, append a completion note to the milestone description via `uv run .claude/tools/linear_cli.py update-milestone-description <milestone-UUID> --description "..."` (Linear has no milestone "completed" state, so a description note is the durable signal). Format:

```
Completed: <YYYY-MM-DD> — all stories Done.
```

If the user declines, leave the milestone untouched.

### 14. Check parent-issue epic completion

Skip this step if the issue had no `parentId`, or if the parent's title doesn't start with `Epic: ` (the parent is a regular sub-issue parent, not a stride epic).

Otherwise, fetch the parent epic's open sub-issues (`<parent-id>` is the parent UUID, `parent.id` from the `uv run .claude/tools/linear_cli.py issue get` at step 1):

```bash
uv run .claude/tools/linear_cli.py list-by-parent <parent-id> | jq '[.[] | select(.state.type as $t | ["backlog","unstarted","started"] | index($t))]'
```

If any items come back, the epic has remaining sub-issues — skip silently.

If the result is empty, all sub-issues of the epic are now Done. In unattended
mode, move the parent epic to Done without prompting; the empty open-sub-issue
list makes this deterministic. In interactive mode, prompt:

```
All sub-issues of *[Epic title]* are complete — mark the epic Done?
```

If the user confirms, move the parent issue to Done:

```bash
uv run .claude/tools/linear_cli.py issue update <parent-id> --state Done
```

`linear_cli.py` accepts state names directly — no separate ID lookup needed. Unlike milestones, parent-issue epics have a real status, so closing them is a normal status transition — no description note needed.

If the user declines, leave the epic untouched.

### 15. Sync Vision if it changed

Detect whether the merged PR's diff included `VISION.md`:

```bash
git -C <main-repo-path> fetch origin main
merge_commit=$(git -C <main-repo-path> log origin/main --first-parent --grep="^Merge branch '<gitBranchName>'" -1 --format=%H)
git -C <main-repo-path> diff <merge_commit>^..<merge_commit> --name-only
```

If `VISION.md` is **not** in the file list, skip this entire step silently — no prompt, no noise. The common case (a PR that didn't touch Vision) sees no extra friction.

If `VISION.md` **is** in the file list, run `/linear:update-vision`'s flow
inline. Interactive mode surfaces:

```
This PR changed VISION.md — sync to Linear?
```

Unattended mode surfaces *"This PR changed VISION.md — syncing to Linear"*.
Treat the one-way command contract as approval, show what differs, write the
differing fields, and continue without prompting.

Then:

1. Read `VISION.md` as the merge left it, not from the main checkout, whose copy is older when step 10a left it alone: `mkdir -p /tmp/<identifier> && git -C <main-repo-path> show <merge_commit>:VISION.md > /tmp/<identifier>/VISION.md`.
2. Resolve the Linear project from `.stride.json`. Get its id, URL, and current subtitle (`description`) from the project list by name — `uv run .claude/tools/linear_cli.py project get` takes an ID, not a name: `uv run .claude/tools/linear_cli.py project list | jq -r --arg name "<project-name>" '.[] | select(.name == $name) | {id, url, description}'`.
3. Fetch the current project `content` via `linear_cli.py` (the Vision lives in `content`, not the length-limited `description`). The subtitle is VISION.md's opening blockquote — the `>` line under the H1 (read it from the file saved in sub-step 1):
   ```bash
   uv run .claude/tools/linear_cli.py get-project-content <project-id>
   ```
4. Compare both fields against `VISION.md` (after trimming surrounding whitespace). Linear normalises markdown on save (e.g. `-` list markers become `*`), so treat normalisation-only differences as in sync. The subtitle is the tagline vs the current `description`; skip the subtitle if VISION.md has no opening blockquote (never blank an existing one).
   - **Both match**: report *"Linear already matches VISION.md (content + subtitle) — no update needed"* and continue to step 17.
   - **Either differs**: show what will change (content diff and/or old→new subtitle). In unattended mode continue to the writes; in interactive mode ask:

     ```
     Replace the Linear content and/or subtitle with VISION.md? (y/n)
     ```

5. On `y`, write whichever differs (`--content @/tmp/<identifier>/VISION.md` reads the file directly — no shell quoting in the path ([why](reference/workflow.md#how-skills-talk-to-linear)); the subtitle is a short single-line field, so it stays inline):
   ```bash
   uv run .claude/tools/linear_cli.py update-project-content <project-id> --content @/tmp/<identifier>/VISION.md
   uv run .claude/tools/linear_cli.py project update <project-id> --description "<tagline-from-step-3>"
   ```
   On `n`: skip the writes and continue to step 17.

If any step in the sync flow fails (`.stride.json` missing, project not found, `update-project-content` / `project update` errors), surface the failure clearly and continue to step 17. The issue is already Done from step 11 — sync failure is non-fatal and recoverable via the standalone `/linear:update-vision` command later.

Track the outcome for the summary in step 17:

| State | When |
|:------|:-----|
| `applied` | Diff existed and `update-project-content` succeeded |
| `declined` | Diff existed and user picked `n` |
| `already in sync` | No diff, identical-check short-circuited |
| `failed: <reason>` | Sync attempted but errored |
| *(omitted)* | `VISION.md` was not in the merged diff |

### 16. Record the card's stage times

Record how long each stage of the card took, from the session logs Claude Code already saved. Run it from the main repo, and give it the directory this session started in, not the current one, which step 10 may have removed:

```bash
uv run <main-repo-path>/.claude/skills/parallel-sessions/scripts/stage_times.py --checkout <main-repo-path> record <issue-id> --working-dir <directory this session started in>
```

The card is already merged and Done, so nothing here stops the finish. A card whose logs are missing or can't be read records nothing, and the command says so in one line. Whatever it prints or fails with, carry on to step 17.

### 17. Summary

Read the output focus and apply this command's format from [reference/output-focus.md](reference/output-focus.md).

---

## Error handling

- Issue ID unresolvable → stop, ask the user
- Issue not found in Linear → stop
- No commits ahead of `main` → stop; nothing committed yet, run `/linear:start` to implement and open the PR
- No open PR for the branch → stop; run `/linear:start` to push and open the PR
- Uncommitted changes → stop, suggest `/commit`
- Tests fail → stop, do not merge
- Recording the stage times fails or finds no log → carry on; the card has already merged
- Main checkout left alone in step 10a → run neither the checkout nor the pull, finish the remaining steps, report the reason and the steps that bring the work in at the top of the summary
- `pull --ff-only` refuses in step 10a → leave the main checkout as it is, finish the remaining steps, report the refusal and `git log origin/main..main` in the summary
- Card check finds an unclear promise or nothing checkable → stop, do not merge
- Fixup commits present + user picks "abort" → exit cleanly, do not merge (autosquash + force-push manually, then re-run)
- Fixup rebase conflicts → abort rebase, surface conflict, do not merge
- Vision has no exact fit → tend the Vision with [`/vision-evolve`](../../skills/vision-evolve/SKILL.md), re-check, then continue
- A lesson would change the purpose of a card still to come → post the question on that card; interactive mode asks the user there and then, unattended mode finishes the remaining steps and reports the question; a card started by name stops there before the next card starts, and a run through Todo leaves only that card out of its later batches
- Branch not fully merged → stop, warn (never force-delete)
- Local branch already deleted → skip silently
- Remote branch already deleted → skip silently

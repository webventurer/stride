# Finish issue

Merge an approved PR, clean up branches, and mark the issue Done.

Accepts a Linear issue ID as argument: `/finish PG-205`

If no argument is given, infer the issue ID from the current branch name (extract `PG-\d+` pattern). If neither works, ask the user.

Workflow: `/plan-work` → `/start` (includes terminal review) → `/fix` (if GitHub review feedback) → **`/finish`**

## Rules

- Never merge if tests fail
- The merge commit message should read as if the work was done right the first time — no mention of rejections, fix cycles, or iterations
- Use `--merge` (not `--squash`) to preserve atomic commits in the branch
- Never force-delete branches

---

## Steps

### 1. Read the Linear issue

Fetch the issue via linctl *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl issue get $ARGUMENTS --json
```

Extract from the JSON: identifier, title, `gitBranchName`, current state, project milestone (if any), parent issue.

Stop if the issue cannot be found.

### 2. Find the PR

Run `gh pr list --head <gitBranchName> --json number,url,title,reviewDecision,mergeable`.

If no PR exists, stop — nothing to merge.

### 3. Check repo state

Run `git status -sb`.

If there are uncommitted changes, warn and stop — suggest `/commit`.

### 4. Validate

Run the project's build command (e.g. `pnpm build`). If the project has tests, run them too.

If anything fails, stop — do not merge. Show what failed.

### 5. Confirm Vision outcome (before merge)

<mark>**This step fires *before* the merge.**</mark> When trace drift is caught here, the catch is still actionable — the criterion can ride alongside its originating feature on the same branch, instead of needing a follow-up `VISION.md` PR.

If the issue has no "Why this matters" section (legacy soft path from `/linear:start`), skip silently and continue to step 6.

Otherwise, run a **silent trace check** *before* deciding whether to prompt the user. Inputs (already in context from step 1 and the steps above):

- The criterion the issue's *Why this matters* section claims to advance.
- The branch's commit subjects: `git log main..HEAD --oneline`.
- The full `VISION.md` Success criteria list.

Read the commit subjects against the Success criteria and apply the [*revise, don't stretch*](https://github.com/webventurer/stride/blob/main/docs/patterns/revise-dont-stretch.md) strain test to the issue's stated trace. <mark>**Don't ask the user whether the trace fits — judge it yourself, then decide whether to interrupt.**</mark> Three outcomes follow.

#### Match — silent confirmation

The issue's stated trace matches the agent's best-fit criterion *and* the fit is unambiguous. Surface a single line and continue to step 6:

```
Trace verified against "<criterion>" — proceeding to merge.
```

No y/n prompt. The common path runs without interruption (Vision criterion #3).

#### Drift — surface the difference, let the user pick

The agent's best-fit differs from the issue's stated trace, *or* the stated trace is strained (one of the strain signals trips). Surface both candidates with the commit reminder so the user can decide:

```
Branch ready to merge:
  - <commit 1>
  - <commit 2>
  - ...

Issue's stated trace:
  "<stated criterion>"

Agent's best-fit reading:
  "<alternative criterion>"

Which fits the work? (stated / alternative / something else)
```

The commit subjects are authored to be informative (atomic-commits discipline) — they're the canonical summary of what shipped. Single-commit branches still get the block.

<mark>**Explain the drift in plain English.**</mark> Describe what the doc or feature actually does in concrete terms, what the criterion actually says, and why the connection lands. Avoid stride-internal vocabulary (`Distinction`, `operationalises`, `gate`, `judgement-worthy`, `trace` as a noun) in user-facing copy — the reader may know nothing about stride's meta-cognitive framework. If a 12-year-old wouldn't understand it, rewrite.

A worked before/after, from the WB-297 dogfood that made this rule explicit:

> **Abstract first attempt:** *"The friction Distinction is the test maintainers reach for to decide whether friction is judgement-worthy. It operationalises criterion #3 — every 'is this gate firing on the right thing?' question runs through this Distinction."*
>
> **Plain-English follow-up:** *"What the doc does: it helps stride's maintainers decide what to do when a user complains that something in stride is annoying. Two possibilities — either the user is doing the wrong kind of work (stride is right to push back), or the gate is firing on a use case nobody designed for (stride should be calibrated). Criterion #3 says stride shouldn't interrupt unless the interruption is worth the user's attention. The doc is the test for which interruptions earn their place."*

Same content, ten times the readability.

- **stated**: the agent was overconfident; user override stands. Continue to step 6 (Merge).
- **alternative**: post a one-line Linear comment via `linctl comment create <issue-id> --body "..."` naming the agent's drift catch and the user-picked criterion. Continue to step 6. The drift is named on the issue; the body isn't auto-rewritten.
- **something else**: drop into the missing-criterion path below.

#### Something else — missing criterion path

Ask one follow-up — *"In one line, what shifted?"* — and post the user's answer as a Linear comment on the issue via `linctl comment create <issue-id> --body "..."`. Then ask:

```
Stop and add the criterion to VISION.md before merging? (y/n)
```

- **Yes**: pause the flow. Tell the user:

  > *"Add the criterion to `VISION.md`, run `/commit` to add it as a separate atomic commit on this branch, then re-run `/linear:finish`."*

  Exit cleanly. Do not merge. Re-running `/linear:finish` re-runs validation (step 4) and re-runs the trace check — which should now match against the just-added criterion.

- **No**: continue to step 6 (Merge). The drift is named in the comment but not amended; the user can file a follow-up `VISION.md` PR if they want.

#### When in doubt, ask

If the agent is genuinely uncertain whether the trace matches — neither obviously clean nor obviously drifted — fall back to the **drift** branch and surface both candidates rather than auto-confirming. <mark>**A false silent confirmation is worse than a borderline prompt:** the silent path's whole value is *trustworthy* trace verification, not speed at the cost of accuracy.</mark>

This step turns the "Why this matters" line from a write-once token into a verified reference — and (with the *Yes, stop* branch) makes the catch *amendable*: a missing criterion rides alongside its originating feature instead of needing a separate PR.

### 6. Merge (preserve commits)

Merge with `--merge` to preserve the atomic commits from the branch. The merge commit gets the default subject only — no body. The individual commits on the branch already explain what was built and why; duplicating that in the merge commit just creates drift between the two messages.

```bash
gh pr merge <number> --merge --subject "Merge branch '<gitBranchName>'" --body ""
```

Pass `--body ""` explicitly so `gh` does not fall back to the PR description.

### 7. Clean up branches, remove worktree, close VS Code

Detect the main repo path. Run `git worktree list` — the first entry is the main repo:

```bash
git worktree list
```

**All git commands must use `git -C <main-repo-path>`** to avoid depending on the worktree directory.

Derive the worktree path from the repo name and issue ID:

```
../<repo-dirname>-<issue-id-lowercase>
```

**Step 7a — Switch to main and pull:**

```bash
git -C <main-repo-path> checkout main && git -C <main-repo-path> pull
```

**Step 7b — Remove worktree:**

Remove the worktree first — git refuses to delete a branch that a worktree is checked out on.

```bash
git -C <main-repo-path> worktree remove <worktree-path>
```

If the worktree directory does not exist, skip silently. If `git worktree remove` fails due to untracked files, use `--force`.

**Step 7c — Delete branches:**

Now that the worktree is gone, the branch can be deleted:

- **Local**: `git -C <main-repo-path> branch -d <gitBranchName>` — use lowercase `-d` since the merge commit makes the branch fully merged. If already deleted, skip silently
- **Remote**: `git -C <main-repo-path> push origin --delete <gitBranchName>` — if already deleted (GitHub may auto-delete), skip silently

**Step 7d — Ask user to close VS Code:**

```
Please close the VS Code window for <worktree-dirname>.
```

VS Code does not support programmatic window closing. The worktree directory is already gone, so VS Code will show an error state — the user just needs to close the window.

### 8. Update Linear → done

Move the issue to **Done**:

```bash
LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl issue update $ARGUMENTS --state Done
```

Only set Done status. Skip if already Done. Never set any other status.

### 8b. Check milestone completion

Skip this step if the issue had no milestone.

Otherwise, fetch issues attached to the milestone in non-Done states (linctl has no typed milestone command, so `linear_cli.py` provides it):

```bash
LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY uv run .claude/tools/linear_cli.py milestone-open-issues <milestone-UUID>
```

If any nodes come back, the milestone has remaining work — skip silently.

If the nodes list is empty, all stories in the milestone are now Done. Prompt:

```
All stories in *[Milestone name]* are complete — mark the milestone done?
```

If the user confirms, append a completion note to the milestone description via `LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY uv run .claude/tools/linear_cli.py update-milestone-description <milestone-UUID> --description "..."` (Linear has no milestone "completed" state, so a description note is the durable signal). Format:

```
Completed: <YYYY-MM-DD> — all stories Done.
```

If the user declines, leave the milestone untouched.

### 8c. Check parent-issue epic completion

Skip this step if the issue had no `parentId`, or if the parent's title doesn't start with `Epic: ` (the parent is a regular sub-issue parent, not a stride epic).

Otherwise, fetch the parent epic's open sub-issues (`<parent-id>` is the parent UUID, `parent.id` from the `linctl issue get` at step 1):

```bash
LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY uv run .claude/tools/linear_cli.py list-by-parent <parent-id> | jq '[.[] | select(.state.type as $t | ["backlog","unstarted","started"] | index($t))]'
```

If any items come back, the epic has remaining sub-issues — skip silently.

If the result is empty, all sub-issues of the epic are now Done. Prompt:

```
All sub-issues of *[Epic title]* are complete — mark the epic Done?
```

If the user confirms, move the parent issue to Done:

```bash
LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl issue update <parent-id> --state Done
```

linctl accepts state names directly — no separate ID lookup needed. Unlike milestones, parent-issue epics have a real status, so closing them is a normal status transition — no description note needed.

If the user declines, leave the epic untouched.

### 8d. Sync Vision if it changed

Detect whether the merged PR's diff included `VISION.md`:

```bash
merge_commit=$(git -C <main-repo-path> log -1 --format=%H)
git -C <main-repo-path> diff <merge_commit>^..<merge_commit> --name-only
```

If `VISION.md` is **not** in the file list, skip this entire step silently — no prompt, no noise. The common case (a PR that didn't touch Vision) sees no extra friction.

If `VISION.md` **is** in the file list, surface a one-line note and run `/linear:update-vision`'s flow inline:

```
This PR changed VISION.md — sync to Linear?
```

Then:

1. Read `VISION.md` from the repo root.
2. Resolve the Linear project from `.linear_project`.
3. Fetch the current Linear description:
   ```bash
   LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl project get "<project-name>" --json
   ```
4. Compare against `VISION.md` (after trimming surrounding whitespace).
   - **Identical**: report *"Linear project description already matches VISION.md — no update needed"* and continue to step 9.
   - **Different**: show the diff and ask:

     ```
     Replace the Linear project description with VISION.md? (y/n)
     ```

5. On `y`:
   ```bash
   LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl project update <project-id> --description "$(cat VISION.md)"
   ```
   On `n`: skip the write and continue to step 9.

If any step in the sync flow fails (`.linear_project` missing, project not found, `linctl project update` errors), surface the failure clearly and continue to step 9. The issue is already Done from step 8 — sync failure is non-fatal and recoverable via the standalone `/linear:update-vision` command later.

Track the outcome for the summary in step 9:

| State | When |
|:------|:-----|
| `applied` | Diff existed and `linctl project update` succeeded |
| `declined` | Diff existed and user picked `n` |
| `already in sync` | No diff, identical-check short-circuited |
| `failed: <reason>` | Sync attempted but errored |
| *(omitted)* | `VISION.md` was not in the merged diff |

### 9. Summary

Display:

- Issue ID and title
- PR: merged
- Build: passed
- Local branch: deleted / already gone
- Remote branch: deleted / already gone
- Worktree: removed / not found
- Linear status: Done
- Milestone (if applicable): name + completion status (`complete` if 8b marked it complete, `<n> stories remaining` otherwise)
- Epic (if applicable): name + completion status (`Done` if 8c moved the parent to Done, `<n> sub-issues remaining` otherwise)
- Vision sync (if `VISION.md` was in the merged diff): `applied` / `declined` / `already in sync` / `failed: <reason>` (per step 8d). Omit the row if VISION.md wasn't touched.

---

## Error handling

- Issue ID unresolvable → stop, ask the user
- Issue not found in Linear → stop
- No PR found → stop, nothing to merge
- Uncommitted changes → stop, suggest `/commit`
- Tests fail → stop, do not merge
- Vision-confirm answered "no" + user picks "stop and add criterion" → exit cleanly, do not merge (re-run after adding the criterion commit)
- Branch not fully merged → stop, warn (never force-delete)
- Local branch already deleted → skip silently
- Remote branch already deleted → skip silently

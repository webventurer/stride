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

Fetch the issue via MCP:

- `get_issue` with `$ARGUMENTS`

Extract: issue ID, title, `gitBranchName`, current status, milestone, `parentId`.

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

Read the issue's "Why this matters" section (loaded in step 1). If it names a Vision outcome, **first run `git log main..HEAD --oneline`** to capture the branch's commit subjects — they're the user's reminder of what just shipped. Then surface the commits and the trace-back question in one block:

```
Branch ready to merge:
  - <commit 1>
  - <commit 2>
  - ...

This issue claimed to advance the Vision outcome:
  "<outcome line from VISION.md>"

Did the work actually advance that outcome? (y/n)
```

The commit subjects are already authored to be informative (atomic-commits discipline) — they're the canonical summary of what shipped. Showing them right above the question lets the user answer in seconds instead of scrolling back to recall the work. Single-commit branches still get the block (one entry) — consistent shape, no special-case logic.

- **Yes**: continue to step 6 (Merge).
- **No**: ask one follow-up — *"In one line, what shifted?"* — and post the user's answer as a Linear comment on the issue via `save_comment`. Then ask:

  ```
  Stop and add the criterion to VISION.md before merging? (y/n)
  ```

  - **Yes**: pause the flow. Tell the user:

    > *"Add the criterion to `VISION.md`, run `/commit` to add it as a separate atomic commit on this branch, then re-run `/linear:finish`."*

    Exit cleanly. Do not merge. Re-running `/linear:finish` re-runs validation (step 4) on the new commit, then re-asks the Vision-confirm — which should now answer *yes* against the just-added criterion.

  - **No**: continue to step 6 (Merge). The drift is named in the comment but not amended; the user can file a follow-up `VISION.md` PR if they want.

If the issue had no "Why this matters" section (legacy soft path from `/linear:start`), skip silently and continue to step 6.

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

Move the issue to **Done** via `save_issue`.

Only set Done status. Skip if already Done. Never set any other status.

### 8b. Check milestone completion

Skip this step if the issue had no milestone.

Otherwise, call `list_issues` filtered by the milestone with non-Done states (`backlog`, `unstarted`, `started`). If any results come back, the milestone has remaining work — skip silently.

If the result is empty, all stories in the milestone are now Done. Prompt:

```
All stories in *[Milestone name]* are complete — mark the milestone done?
```

If the user confirms, append a completion note to the milestone description via `save_milestone` (Linear has no milestone "completed" state, so a description note is the durable signal). Format:

```
Completed: <YYYY-MM-DD> — all stories Done.
```

If the user declines, leave the milestone untouched.

### 8c. Check parent-issue epic completion

Skip this step if the issue had no `parentId`, or if the parent's title doesn't start with `Epic: ` (the parent is a regular sub-issue parent, not a stride epic).

Otherwise, call `list_issues` filtered by `parentId` with non-Done states (`backlog`, `unstarted`, `started`). If any results come back, the epic has remaining sub-issues — skip silently.

If the result is empty, all sub-issues of the epic are now Done. Prompt:

```
All sub-issues of *[Epic title]* are complete — mark the epic Done?
```

If the user confirms, move the parent issue to Done via `save_issue` with `state` set to the Done status ID (resolve via `list_issue_statuses`). Unlike milestones, parent-issue epics have a real status, so closing them is a normal status transition — no description note needed.

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
3. Call `get_project` to fetch the current Linear description.
4. Compare against `VISION.md` (after trimming surrounding whitespace).
   - **Identical**: report *"Linear project description already matches VISION.md — no update needed"* and continue to step 9.
   - **Different**: show the diff and ask:

     ```
     Replace the Linear project description with VISION.md? (y/n)
     ```

5. On `y`: call `save_project` with the full `VISION.md` contents as `description`. On `n`: skip the write and continue to step 9.

If any step in the sync flow fails (`.linear_project` missing, project not found via `list_projects`, `save_project` errors), surface the failure clearly and continue to step 9. The issue is already Done from step 8 — sync failure is non-fatal and recoverable via the standalone `/linear:update-vision` command later.

Track the outcome for the summary in step 9:

| State | When |
|:------|:-----|
| `applied` | Diff existed and `save_project` succeeded |
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

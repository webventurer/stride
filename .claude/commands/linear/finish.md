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

### 5. Merge (preserve commits)

Merge with `--merge` to preserve the atomic commits from the branch. The merge commit gets the default subject only — no body. The individual commits on the branch already explain what was built and why; duplicating that in the merge commit just creates drift between the two messages.

```bash
gh pr merge <number> --merge --subject "Merge branch '<gitBranchName>'" --body ""
```

Pass `--body ""` explicitly so `gh` does not fall back to the PR description.

### 6. Clean up branches, remove worktree, close VS Code

Detect the main repo path. Run `git worktree list` — the first entry is the main repo:

```bash
git worktree list
```

**All git commands must use `git -C <main-repo-path>`** to avoid depending on the worktree directory.

Derive the worktree path from the repo name and issue ID:

```
../<repo-dirname>-<issue-id-lowercase>
```

**Step 6a — Switch to main and pull:**

```bash
git -C <main-repo-path> checkout main && git -C <main-repo-path> pull
```

**Step 6b — Remove worktree:**

Remove the worktree first — git refuses to delete a branch that a worktree is checked out on.

```bash
git -C <main-repo-path> worktree remove <worktree-path>
```

If the worktree directory does not exist, skip silently. If `git worktree remove` fails due to untracked files, use `--force`.

**Step 6c — Delete branches:**

Now that the worktree is gone, the branch can be deleted:

- **Local**: `git -C <main-repo-path> branch -d <gitBranchName>` — use lowercase `-d` since the merge commit makes the branch fully merged. If already deleted, skip silently
- **Remote**: `git -C <main-repo-path> push origin --delete <gitBranchName>` — if already deleted (GitHub may auto-delete), skip silently

**Step 6d — Ask user to close VS Code:**

```
Please close the VS Code window for <worktree-dirname>.
```

VS Code does not support programmatic window closing. The worktree directory is already gone, so VS Code will show an error state — the user just needs to close the window.

### 7. Confirm Vision outcome

Read the issue's "Why this matters" section (loaded in step 1). If it names a Vision outcome, surface it and ask the user one yes/no question:

```
This issue claimed to advance the Vision outcome:
  "<outcome line from VISION.md>"

Did the merged work actually advance that outcome? (y/n)
```

- **Yes**: continue to step 8.
- **No**: ask one follow-up — *"In one line, what shifted?"* — and post the user's answer as a Linear comment on the issue via `save_comment`. Then continue. The comment closes the loop: the trace-back claimed at draft time has now been verified or amended at finish time.

If the issue had no "Why this matters" section (legacy soft path from `/linear:start`), skip silently.

This step turns the "Why this matters" line from a write-once token into a verified reference. It's near-zero cost — one yes/no most of the time — and the rare *no* surfaces drift before it compounds.

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

---

## Error handling

- Issue ID unresolvable → stop, ask the user
- Issue not found in Linear → stop
- No PR found → stop, nothing to merge
- Uncommitted changes → stop, suggest `/commit`
- Tests fail → stop, do not merge
- Branch not fully merged → stop, warn (never force-delete)
- Local branch already deleted → skip silently
- Remote branch already deleted → skip silently

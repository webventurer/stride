# Provision Linear workflow states

Create the workflow states stride needs ([`linear_statuses.json`](linear_statuses.json)) in a Linear workspace, and order them to match — so `/linear:start` / `/linear:finish` transitions land instead of silently no-opping on a missing or misnamed column.

<mark>**Non-destructive.** This only *creates* missing states and *reorders* canonical ones. It never deletes or renames a state, so no in-progress work is ever orphaned.</mark> Idempotent: a workspace that already has every canonical state in order is left untouched.

## Steps

### 1. Pick the workspace to provision

List the configured workspaces (these come from `~/.env`):

```bash
env | grep -oE '^LINEAR_[A-Z_]+_API_KEY' | sort -u
```

If none are found, point the user at [reference/setup.md](reference/setup.md) to add a `LINEAR_<TEAM>_API_KEY`. If exactly one is set, use it. If several, ask which workspace to provision — this writes to a live board, so target one deliberately.

### 2. Preview what's missing

Run the read-only drift check first so the user sees what will be created *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
LINCTL_API_KEY="$LINEAR_<TEAM>_API_KEY" uv run .claude/tools/linear_cli.py state-drift
```

Each `{name, type}` in the list is a canonical state the board lacks and `/linear:setup` will create. An empty list (`[]`) means nothing is missing — setup will at most reorder, and is likely a no-op.

### 3. Confirm, then provision

Show the missing states (from step 2) and confirm before writing:

```
Provision these states into <workspace> and order them to match stride's sequence?
This only adds and reorders columns — it never deletes or renames. (y/n)
```

On **n**, stop without writing. On **y**, provision:

```bash
LINCTL_API_KEY="$LINEAR_<TEAM>_API_KEY" uv run .claude/tools/linear_cli.py provision-states
```

It returns `{created, reordered, in_sync}` — the states it created, the ones it repositioned, and whether the board was already in sync.

### 4. Summary

Report per workspace:

| Workspace | Created | Reordered | Result |
|:----------|:--------|:----------|:-------|
| Webventurer | — | — | already in sync |
| FreshOrg | Doing, In Review, Waiting | — | 3 states created |

If `in_sync` is `true` and nothing was created or reordered, say so plainly: "Already in sync — no changes." Re-running is always safe.

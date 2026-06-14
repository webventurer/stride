# Worktree setup

> The mechanics `/linear:start` follows when `--worktree` is passed. The decision — inline by default, isolated worktree when the flag is present — stays in `start.md` (step 6); this file holds the execution detail so the command stays scannable. Step numbers below refer to `/linear:start`'s steps.

> **Same-window model.** Stride does not open an editor or a terminal. It creates the worktree and prints a handoff; the user opens a new terminal tab in their **current** VS Code window, `cd`s in, and launches `claude`. A new terminal tab is a fresh shell, so nothing relocates the running session — and multiple cards become side-by-side tabs in one window, no alt-tabbing.

---

## W1. Guard the state

`--worktree` means "set up a workspace to **start** this issue in." If the issue is already `In Review` or `Done`, that's fix-or-finish territory, not start — stop and tell the user:

```
WB-123 is already <state>. --worktree sets up a fresh workspace to start an
issue; for an issue in review or done, work in its existing checkout instead.
```

## W2. Create the worktree

The branch is created **by the worktree**, not inline — so step 5's inline `git checkout -b` is skipped when `--worktree` is passed (see start.md step 5).

Resolve the path from the repo name and issue ID:

```
../<repo-dirname>-<issue-id-lowercase>
```

For example, repo `lander` + issue `PG-210` → `../lander-pg-210`.

Create the worktree on the issue's branch (from Linear's `gitBranchName`):

```bash
git worktree add ../<repo-dirname>-<issue-id-lowercase> -b <gitBranchName>
```

If the branch already exists (a remote branch, or one created earlier), drop the `-b`:

```bash
git worktree add ../<repo-dirname>-<issue-id-lowercase> <gitBranchName>
```

## W3. Print the handoff and exit

Stride opens nothing — the user drives the editor. Print this, then **exit before step 7 (Implement)**; the fresh `claude` session takes over from there:

```
Worktree ready: <worktree-path>

Open a new terminal tab (Ctrl/Cmd+Shift+`) and run:

  cd <worktree-path> && claude

Then in that session:  /linear:start <issue-id>
  (no --worktree this time — it picks up the branch and does the work)

Optional, from that tab:
  code --add .    show this worktree's files in the VS Code explorer
  /diffity-diff   open a visual diff of this stream's changes
```

The second, flag-less `/linear:start` is the real work; the first invocation is setup-and-exit. The handoff names that explicitly so the double-invocation isn't a surprise.

## W4. Resuming in the worktree

When the user runs `/linear:start <issue-id>` (no flag) from the worktree's terminal, step 5's branch resolution finds it already on the correct branch and skips to step 6 — the flow continues from the Vision check onward exactly as an inline run would.

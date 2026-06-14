# Worktree

> The worktree lifecycle stride manages: **Setup** when `/linear:start` is given `--worktree` (step 6), **Teardown** when `/linear:finish` cleans up (step 8). The decision — inline by default, isolated worktree when the flag is present — stays in the command files; this file holds the execution detail so they stay scannable.

> **Same-window model.** Stride does not open or close an editor or a terminal. On setup it creates the worktree and prints a handoff; the user opens a new terminal tab in their **current** VS Code window, `cd`s in, and launches `claude`. A new terminal tab is a fresh shell, so nothing relocates the running session — and multiple cards become side-by-side tabs in one window, no alt-tabbing. On teardown the worktree directory is removed and the user closes that tab.

---

## Setup

The mechanics `/linear:start` follows when `--worktree` is passed. Step numbers refer to `/linear:start`'s steps.

### Guard the state

`--worktree` means "set up a workspace to **start** this issue in." If the issue is already `In Review` or `Done`, that's fix-or-finish territory, not start — stop and tell the user:

```
WB-123 is already <state>. --worktree sets up a fresh workspace to start an
issue; for an issue in review or done, work in its existing checkout instead.
```

### Create the worktree

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

### Symlink the venv (Python projects)

A fresh worktree has no `.venv`, so `cd`-ing in and running anything Python fails with `command not found`. If the parent repo root has a virtualenv, link it in so the stream can run immediately.

After `git worktree add` succeeds:

1. Look for a venv at the parent repo root — check `.venv` first, then `venv`.
2. If one is found and the worktree has no matching directory or symlink, link it:

   ```bash
   ln -s <parent-repo>/.venv <worktree>/.venv
   ```

3. If none is found, **skip silently** — no message, no action. This is the path for Node, Rails, Go, and any non-Python project.
4. When a symlink is created, print one line so the user knows: *"Shared venv from `<parent>/.venv` linked into the worktree."*

Scope: the common `.venv` / `venv` layout only. Skip Poetry / Pipenv / Conda (their envs live outside the repo) and bespoke names — those users link manually. No Windows symlink support yet. The linked venv's `VIRTUAL_ENV` resolves to the parent path (cosmetic — binaries and packages still work), and a worktree always shares the parent's interpreter, so it never runs a different Python than its parent.

### Print the handoff and exit

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

### Resuming in the worktree

When the user runs `/linear:start <issue-id>` (no flag) from the worktree's terminal, step 5's branch resolution finds it already on the correct branch and skips to step 6 — the flow continues from the Vision check onward exactly as an inline run would.

---

## Teardown

The mechanics `/linear:finish` follows (step 8) when the issue was worked in a worktree. Run from the **main repo**, not the worktree that's about to vanish — `git worktree list`'s first entry is the main repo; use `git -C <main-repo-path>` for every command. Skip this whole section silently for an inline run (no worktree on disk).

### Remove the worktree

Remove the worktree **before** deleting its branch — git refuses to delete a branch a worktree has checked out. The path is the same one Setup derived: `../<repo-dirname>-<issue-id-lowercase>`.

```bash
git -C <main-repo-path> worktree remove <worktree-path>
```

If the worktree directory does not exist, skip silently. If `git worktree remove` fails due to untracked files, use `--force`.

### Close the worktree's tab

There is no separate window to close — the worktree was a terminal tab in the current window. Print:

```
The worktree is gone. In your VS Code window:
- Close the terminal tab that was running in <worktree-dirname>.
- If you added the worktree as a folder (code --add), remove it:
  code --remove <worktree-path>, or right-click it in the Explorer
  → Remove Folder from Workspace.
```

VS Code can't close a tab or remove a folder root programmatically, so this is a manual step. The wording holds whether or not the folder was ever added.

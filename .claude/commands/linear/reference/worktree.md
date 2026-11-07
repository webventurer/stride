# Worktree

> The worktree lifecycle stride manages: **Setup** when `/linear:start` is given `--worktree` (step 7), **Teardown** when `/linear:finish` cleans up (step 10). The decision — inline by default, isolated worktree when the flag is present — stays in the command files; this file holds the execution detail so they stay scannable.

> **Same-window model.** Stride does not open or close an editor or a terminal. On setup it creates the worktree and prints a handoff; the user opens a new terminal tab in their **current** VS Code window, `cd`s in, and launches `claude`. A new terminal tab is a fresh shell, so nothing relocates the running session — and multiple cards become side-by-side tabs in one window, no alt-tabbing. On teardown the worktree directory is removed and the user closes that tab.

---

## Setup

The mechanics `/linear:start` follows when `--worktree` is passed. Step numbers refer to `/linear:start`'s steps.

> **Resolve every path here to an absolute path.** The handoff's `cd` runs in a fresh terminal tab whose working directory you don't control, and the venv symlink's target must resolve from inside the worktree — relative paths break both. Compute the worktree path once as absolute (e.g. `/Users/you/projects/lander/.claude/worktrees/pg-210`) and use that everywhere below.

### Guard the state

`--worktree` means "set up a workspace to **start** this issue in." If the issue is already `In Review` or `Done`, that's fix-or-finish territory, not start — stop and tell the user:

```
WB-123 is already <state>. --worktree sets up a fresh workspace to start an
issue; for an issue in review or done, work in its existing checkout instead.
```

### Create the worktree

The branch is created **by the worktree**, not inline — so step 6's inline `git switch -c` is skipped when `--worktree` is passed (see start.md step 6).

Every worktree goes in the main checkout's `.claude/worktrees/` folder, named by the lowercase issue ID. Repo `lander` and issue `PG-210` give `lander/.claude/worktrees/pg-210`. The Claude Code app keeps its session worktrees in the same folder, so there is one place to look for unmerged work.

Resolve `main_repo` from the first worktree in `git worktree list --porcelain`, then get the path:

```bash
"$main_repo/.claude/tools/card_worktree_path.sh" "$main_repo" <issue-id>
```

It prints the absolute worktree path. It first checks that git ignores `.claude/worktrees/` in the main checkout, from `.gitignore` or `.git/info/exclude`, so the worktree never shows in the main checkout's `git status` or its linters. When the folder isn't ignored, it exits non-zero and names the line to add to `.gitignore`. Stop and show that message: create nothing. Installing stride adds the line when its `.gitignore` prompt is answered yes.

Create the worktree at that path on the issue's branch (from Linear's `gitBranchName`):

```bash
git worktree add <worktree-path> -b <gitBranchName> origin/main
```

If the branch already exists (a remote branch, or one created earlier), drop the `-b`:

```bash
git worktree add <worktree-path> <gitBranchName>
```

### Share Stride settings

Worktrees of the same repository share the user's settings. After creating
the worktree, link `.stride.json` before printing the handoff. A link keeps
project, authentication selection, focus and unattended mode in sync; editing
settings through either checkout changes the shared file.

Use `main_repo` from the step above, not the current directory, which may
itself be a linked worktree. Set `worktree` to the new worktree's absolute path.
Quote both paths.

Before linking, apply the [machine-local check](unattended.md#read-the-mode)
to the source, including any symlink targets. Confirm its fields are valid
for the existing project settings; do not fill missing values from memory.
If the source is missing, unreadable, invalid or tracked, stop before the
handoff and report the reason. Use `/linear:setup` for missing configuration
or repair the existing file; never invent unattended approval.

Run the settings script only after those checks pass:

```bash
"$main_repo/.claude/tools/share_stride_settings.sh" "$main_repo" "$worktree"
```

It exits zero once `.stride.json` in the worktree is a link to the main checkout's copy, whether it made the link or the link was already there. For a tracked file it prints "Tracked .stride.json in <path>", and for a taken path "Existing .stride.json in <path>". On a non-zero exit, stop before the handoff.

If either path is not ignored, add `.stride.json` to the appropriate local
Git exclude file before retrying. If a different file, directory or link
already occupies the destination, preserve it and report the conflict; this
includes dangling links. Do not force replacement or announce readiness on
failure. Re-running with the correct link leaves it unchanged.

After success, print: *"Shared Stride settings from `<main-repo>/.stride.json`
linked into the worktree."* The new session reads its local `.stride.json`
normally. On each read, `unattended: true` and `false` reflect the shared
file's current value; the usual validation and merge checks still apply.

### Link what stride installed

Stride's install is gitignored, so a fresh worktree has none of it: no `/linear:*` commands, no `linear_cli.py`, no `/commit` skill, no hooks. Without them the handoff's `/linear:start` doesn't resolve. Link each missing path in from the parent instead, so the worktree runs the same stride the parent does.

The paths linked are:

- **Every path in the stride section of the parent's `.gitignore`**, between the `# >>> stride` and `# <<< stride <<<` markers. This includes stride's Codex files, such as `.codex/skills/` and `.codex/hooks.json`.
- **`.claude/settings.local.json`**, where stride's hooks are configured.
- **The parent's venv**, `.venv` or `venv`, so Python runs straight away in the worktree.

A path is linked only when the parent has it and the worktree doesn't. A path the branch tracks, or one linked earlier, is left alone. `.claude/worktrees` is never linked, even though stride's section lists it: the worktree sits inside that folder, so a link would point back at itself and its siblings. Each link is added to the repository's shared `info/exclude` without a trailing slash, because git matches a trailing-slash ignore line such as `.claude/tools/` only against a real folder, never against a link. Without that line every linked folder would show in `git status` as untracked.

After the settings are shared, run the linking script with the two absolute paths from above, and show its output to the user:

```bash
"$main_repo/.claude/tools/link_stride_install.sh" "$main_repo" "$worktree"
```

It prints one line naming what it linked. When nothing was linked, it prints nothing. That's the case for a repo with no stride section and no venv.

<mark>**A linked file is the parent's file.**</mark> Editing a linked skill, command or tool inside the worktree edits the parent's copy, and the change shows in every worktree at once. Those paths aren't the branch's to change. To change stride itself, edit it in the parent or reinstall.

Scope: the venv link covers the common `.venv` / `venv` layout only. Poetry, Pipenv and Conda keep their environments outside the repo. No Windows symlink support yet. A linked venv's `VIRTUAL_ENV` points at the parent path, which is cosmetic, and the worktree always runs the parent's Python.

### Print the handoff and exit

Stride opens nothing — the user drives the editor. Print this, then **exit before step 8 (Implement)**; the fresh `claude` session takes over from there:

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

When the user runs `/linear:start <issue-id>` (no flag) from the worktree's terminal, step 6's branch resolution finds it already on the correct branch and skips to step 7 — the flow continues from the Vision check onward exactly as an inline run would, except that the card check is skipped because the first run already made it.

---

## Teardown

The mechanics `/linear:finish` follows (step 10) when the issue was worked in a worktree. Run from the **main repo**, not the worktree that's about to vanish — `git worktree list`'s first entry is the main repo; use `git -C <main-repo-path>` for every command. Skip this whole section silently for an inline run (no worktree on disk).

### Remove the worktree

Remove the worktree **before** deleting its branch — git refuses to delete a branch a worktree has checked out. Find it by the branch it has checked out, not by rebuilding a path, so a worktree made beside the repo as `../<repo>-<issue-id>` by an older stride is removed too:

```bash
"<main-repo-path>/.claude/tools/remove_card_worktree.sh" "<main-repo-path>" <gitBranchName>
```

It prints the path it removed, which names the tab to close below. It forces the removal. When the worktree's folder was deleted by hand, it prunes git's record instead, so the branch can still be deleted. When no worktree has the branch, it prints nothing: skip the tab step.

Removing a worktree removes its `.stride.json` link, not the shared source.
Never follow the link to delete the main checkout's settings.

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

# Clean start

> **What this is**: the check `/linear:start` and `/linear:quick` run before creating a branch, so a new branch starts from `main` on the remote and carries nothing left over from earlier work.

<mark>**A branch starts clean: nothing uncommitted and no unpushed commits beneath it, unless they are the work this run was asked to do.**</mark> Leftovers settle on `main` first. Otherwise they ride into the new branch and merge inside a pull request they have nothing to do with.

[Branch scope](branch-scope.md) checks the same thing at merge time. This check comes first, while moving a leftover is still a commit and a push rather than a rebase of a published branch.

## Find the leftovers

```bash
git fetch
git status --short
git log origin/main..main --oneline
```

Two kinds count as leftovers:

| Kind | Shows up as |
|:--|:--|
| **Uncommitted** | Modified or untracked files in `git status --short` |
| **Unpushed** | Commits on local `main` that `origin/main` does not have |

When both are empty, report nothing and continue.

## Judge each one

A leftover belongs to this run only when it *is* the requested work: the change `/linear:quick` was asked to ship, or work the card for `/linear:start` describes. Sharing a directory with the work, or being made in the same session, does not make it belong.

`/linear:quick` run with no description means "ship what I already did", so its uncommitted changes belong. Unpushed commits on `main` still get judged.

## Settle the ones that don't belong

The destination follows [PR vs direct commit](pr-vs-direct-commit.md):

- **Uncommitted, documentation or configuration with obvious intent** — commit on `main` with [`/commit`](../../../skills/commit/SKILL.md), then `git push`
- **Unpushed commit, documentation or configuration with obvious intent** — `git push` from `main`
- **Anything else** — code or structure needs its own branch and pull request: stop, ship it with its own `/linear:quick` (or `/linear:plan-work` if it is bigger than one scroll), then re-run this command

Then confirm both `git status --short` and `git log origin/main..main` are empty before branching.

## Branch from the remote

Create the new branch from `origin/main`, not local `main`:

```bash
git switch -c <branch> origin/main
```

Uncommitted changes that belong to this run come with the switch.

When an unpushed commit on `main` *is* this run's work (you committed the change first, then ran `/linear:quick`), branch from local `main` so it comes along, then move local `main` back to the remote:

```bash
git switch -c <branch>
git branch -f main origin/main
```

If unpushed commits that belong sit among ones that don't, stop and ask: pushing `main` would publish them all.

## Modes

Read [unattended mode](unattended.md). Interactive mode lists the leftovers with the destination each would take and asks `settle / keep / abort`. **keep** leaves them where they are and continues: unpushed commits stay on local `main` and out of the branch, while uncommitted files come along and meet [branch scope](branch-scope.md) at merge. **abort** stops before any branch exists.

Unattended mode settles a leftover only when it is plainly documentation or configuration that does not belong to this run. Anything else is the unrelated-changes stop in [unattended mode](unattended.md#always-stop).

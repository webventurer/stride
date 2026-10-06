# Branch scope

> **What this is**: the check `/linear:finish` and `/linear:quick` run before merging, so a branch merges only the commits that serve its purpose.

<mark>**A branch merges only the commits that serve its purpose.**</mark> A commit that serves something else leaves the branch before the merge, even when it touches the same files or was made in the same session.

## The purpose

| Command | The branch's purpose comes from |
|:--|:--|
| `/linear:finish` | The card's title and its *What we'll do* section |
| `/linear:quick` | The change description and the PR's summary |

## Judge each commit

List the commits the branch adds:

```bash
git log main..HEAD --format='%h %s'
```

Read each commit's subject and diff (`git show <sha>`). A commit belongs when removing it would leave the purpose incomplete. That is the [coherence test](../../../skills/commit/SKILL.md#the-coherence-test) applied to the branch instead of the commit.

These do not make a commit belong: sharing a file or directory with the work, being made in the same session, or fixing something noticed while doing the work. A `VISION.md` commit made by the command's own Vision trace step does belong; that step puts it on the branch deliberately.

**Example.** A branch whose purpose is "list the skill's sources in one file and reconcile the Activity Log" carries `docs: Run Premium Alerts in its own environment`. Removing it leaves the sources list and the reconciliation complete, so it does not belong.

When every commit belongs, report nothing and continue.

## Move a stray commit

The destination follows [PR vs direct commit](pr-vs-direct-commit.md): documentation or configuration whose intent is obvious from the diff goes straight to `main`; anything else gets its own branch and PR.

1. Copy it to its destination:

   ```bash
   git switch main && git pull --ff-only
   git cherry-pick <sha> && git push              # straight to main
   # or: git switch -c <type>/<slug> && git cherry-pick <sha> && git push -u origin <type>/<slug>
   git switch <branch>
   ```

2. Drop it from the branch, without an editor:

   ```bash
   GIT_SEQUENCE_EDITOR="sed -i.bak '/^pick <short-sha> /d'" git rebase -i "$(git merge-base main HEAD)"
   git push --force-with-lease
   ```

3. Confirm `git log main..HEAD` now lists only commits that serve the purpose.

A rebase conflict or a refused lease is a hard stop: abort the rebase (`git rebase --abort`), report it and do not merge.

## Modes

Read [unattended mode](unattended.md). Interactive mode lists the stray commits with the destination each would take and asks `move / keep / abort`. **keep** merges them as they are; **abort** stops without merging.

Unattended mode moves a commit only when it plainly serves a different purpose. When it is unclear whether a commit belongs, stop and ask; that is the ambiguous-scope stop in [unattended mode](unattended.md#always-stop).

## What this does not catch

This check moves whole commits. A single commit that carries two purposes is split by [`/commit`](../../../skills/commit/SKILL.md) before it reaches the branch.

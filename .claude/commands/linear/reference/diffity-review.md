# Open a PR diff in diffity

The shared launch procedure for surfacing a diff in diffity — a localhost diff viewer, independent of the editor's PR panel, so the visual diff always renders. The diff is usually a PR (`diffity --new <pr-url>`), but the same mechanics surface the working tree vs `main` (`diffity --new main`). Called at the review steps of [`/linear:start`](../start.md) — working tree before commit, and the PR after — and [`/linear:quick`](../quick.md); each command decides *when* in its flow to invoke this and keeps its own framing around it.

<mark>**diffity is not a dependency.**</mark> If it's missing, skip the visual diff and let the PR on GitHub stand as the diff surface. Never fall back to a terminal `git diff` — no install, no prompt, no error.

## Launch

Check, then background-launch, then print the URL:

```bash
which diffity || echo "diffity not installed — skipping visual diff"
```

If diffity is present:

1. Launch with the PR URL, forcing a fresh instance with `--new`. Run it via the Bash tool with `run_in_background: true` — let the tool handle backgrounding, no `&` and no `--quiet`:

   ```bash
   diffity --new <pr-url>
   ```

   `--new` matters: diffity reuses any instance already running for the repo and **ignores a new ref**, so without it a stale viewer masks the just-created PR. `--new` is repo-scoped — instances for other repos are left alone.

2. Wait 2 seconds, then read the port and print only the short URL — no session IDs or hashes:

   ```bash
   diffity list --json
   ```

   > Diffity is showing the PR diff at http://localhost:5391

If diffity errors at any point, note it in one line and carry on — a broken viewer never blocks the review.

## Refresh after changes

If the user requests changes and you push an update to the same PR, re-launch with `--new` to point the viewer at the updated diff.

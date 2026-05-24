# Check Linear connections

Verify linctl can authenticate against every configured Linear workspace, then confirm the board's workflow states match the names stride uses.

## Steps

### 1. Find configured workspaces

Look for `LINEAR_*_API_KEY` env vars currently set in the shell (these come from `~/.env`):

```bash
env | grep -oE '^LINEAR_[A-Z_]+_API_KEY' | sort -u
```

If none are found, tell the user to add at least one `LINEAR_<TEAM>_API_KEY` to `~/.env` — see [reference/setup.md](reference/setup.md).

### 2. Test each workspace

For each env var found, run linctl's identity check to confirm the key works *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
LINCTL_API_KEY="$LINEAR_<TEAM>_API_KEY" linctl whoami --json
```

Report the result as a table:

| Workspace | Env var | Status | User |
|:----------|:--------|:-------|:-----|
| Org1 | `LINEAR_ORG1_API_KEY` | Connected | you@example.com |
| Org2 | `LINEAR_ORG2_API_KEY` | Connected | you@example.com |

If a workspace fails, show the error and suggest checking:

- The API key is set in `~/.env` and the shell has loaded it (`source ~/.env` or restart the shell)
- The key value matches an active personal API key in Linear's *Settings → API*
- `which linctl` returns a path — if not, `brew install dorkitude/linctl/linctl`

### 3. Verify the board matches stride's states

The state names stride uses (`Doing`, `In Review`, `Done`, `Backlog`, …) live in one place: [`linear_statuses.json`](linear_statuses.json). A name that doesn't exist on the board silently no-ops — the trap WB-401 hit with `In Progress`. This step confirms every state stride declares actually exists on the live board.

For each connected workspace, run the drift check *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
LINCTL_API_KEY="$LINEAR_<TEAM>_API_KEY" uv run .claude/tools/linear_cli.py state-drift
```

It returns a JSON list of `{name, type}` pairs stride declares but the board lacks — drift that will cause silent no-ops. An empty list (`[]`) means the board carries every state stride uses (extra board states are fine — the JSON records what stride *uses*, not everything that exists).

Report per workspace:

| Workspace | Board match | Drift |
|:----------|:------------|:------|
| Webventurer | ✅ in sync | — |
| Org2 | ⚠️ drift | `In Review` (started) missing |

If a workspace drifts, the fix is a human one: rename the board state to match `linear_statuses.json`, or edit the JSON to match the board. stride doesn't auto-reconcile — the board is the source of truth for what *exists*, the JSON for what stride *uses*. When the drift is *missing* states (not a rename), suggest running [`/linear:setup`](setup.md) to provision them — but only as a suggestion; never run it automatically from `/linear:check`.

### 4. Summary

End with a one-line summary: "N of M Linear workspaces connected via linctl; boards in sync / N drifted."

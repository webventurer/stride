# Check Linear connections

Verify linctl can authenticate against every configured Linear workspace, then confirm each team's board carries the workflow states stride uses.

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

### 3. Verify each team's board matches stride's states

The state names stride uses (`Doing`, `In Review`, `Done`, `Backlog`, …) live in one place: [`linear_statuses.json`](linear_statuses.json). A name that doesn't exist on the board silently no-ops — e.g. a board state named `In Progress` when stride uses `Doing`. This step confirms every state stride declares actually exists on the live board.

**Boards are per-team, not per-workspace** — a workspace can hold several teams, each with its own board, so check every team rather than assuming the first. For each connected workspace, list its teams *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
LINCTL_API_KEY="$LINEAR_<TEAM>_API_KEY" linctl team list --json
```

Then run the drift check **once per team**, passing the team key. Without `--team` the tool checks only the workspace's first team, so a multi-team workspace would silently skip the rest:

```bash
LINCTL_API_KEY="$LINEAR_<TEAM>_API_KEY" uv run .claude/tools/linear_cli.py state-drift --team <TEAM-KEY>
```

It returns a JSON list of `{name, type}` pairs stride declares but the board lacks — drift that will cause silent no-ops. An empty list (`[]`) means that team's board carries every state stride uses (extra board states are fine — the JSON records what stride *uses*, not everything that exists). `state-drift` is read-only — it never writes to the board.

Report one row per team:

| Workspace | Team | Board match | Drift |
|:----------|:-----|:------------|:------|
| Org1 | ENG | ✅ in sync | — |
| Org1 | OPS | ⚠️ drift | `In Review` (started) missing |

If a team drifts, point the user at [`/linear:setup`](setup.md) for that team — on an empty board it provisions the states to match; on a populated board it reports the target order for the human to apply (rename the board state to match `linear_statuses.json`, or edit the JSON to match the board). stride never auto-reconciles — the board is the source of truth for what *exists*, the JSON for what stride *uses*. Only ever suggest `/linear:setup`; never run it automatically from `/linear:check`.

### 4. Summary

End with a one-line summary: "N of M Linear workspaces connected via linctl; K of L team boards in sync, N drifted." If any board drifted, name `/linear:setup` as the next step.

# Check Linear connections

Verify stride can authenticate against every configured Linear workspace, then confirm each team's board carries the workflow states stride uses.

## Steps

### 1. Find configured workspaces

Discover the configured workspaces — see [Workspaces and teams → Find configured workspaces](reference/workspaces-and-teams.md#find-configured-workspaces). `check` tests **every** workspace found (where `/linear:setup` targets one).

### 2. Test each workspace

For each env var found, run the identity check to confirm the key works — workspace-iterating, so the per-workspace `LINEAR_API_KEY=` wrap is explicit (it overrides `.linear_project`'s single key):

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py whoami
```

Report the result as a table:

| Workspace | Env var | Status | User |
|:----------|:--------|:-------|:-----|
| Org1 | `LINEAR_ORG1_API_KEY` | Connected | you@example.com |
| Org2 | `LINEAR_ORG2_API_KEY` | Connected | you@example.com |

If a workspace fails, show the error and suggest checking:

- The API key is set in `~/.env` and the shell has loaded it (`source ~/.env` or restart the shell)
- The key value matches an active personal API key in Linear's *Settings → API*
- `uv` and `jq` are on the PATH (run `bin/prereqs.mjs` or `pnpm install` if not)

### 3. Verify each team's board matches stride's states

The state names stride uses (`Doing`, `In Review`, `Done`, `Backlog`, …) live in one place: [`linear_statuses.json`](linear_statuses.json). A name that doesn't exist on the board silently no-ops — e.g. a board state named `In Progress` when stride uses `Doing`. This step confirms every state stride declares actually exists on the live board.

For each connected workspace, list its teams — see [Workspaces and teams → List a workspace's teams](reference/workspaces-and-teams.md#list-a-workspaces-teams). Check **every** team, not just the first.

Then run the drift check **once per team**, passing the team key. Without `--team` the tool checks only the workspace's first team, so a multi-team workspace would silently skip the rest:

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py state-drift --team <TEAM-KEY>
```

It returns a JSON list of `{name, type}` pairs stride declares but the board lacks — drift that will cause silent no-ops. An empty list (`[]`) means that team's board carries every state stride uses (extra board states are fine — the JSON records what stride *uses*, not everything that exists). `state-drift` is read-only — it never writes to the board.

Report one row per team:

| Workspace | Team | Board match | Drift |
|:----------|:-----|:------------|:------|
| Org1 | ENG | ✅ in sync | — |
| Org1 | OPS | ⚠️ drift | `In Review` (started) missing |

If a team drifts, point the user at [`/linear:setup`](setup.md) for that team — on an empty board it provisions the states to match; on a populated board it reports the target order for the human to apply (rename the board state to match `linear_statuses.json`, or edit the JSON to match the board). stride never auto-reconciles — the board is the source of truth for what *exists*, the JSON for what stride *uses*. Only ever suggest `/linear:setup`; never run it automatically from `/linear:check`.

### 4. Verify the repo is pinned to a project

`/linear:setup` pins a repo to a Linear project by writing `.linear_project` (its [create-project step](reference/create-project.md)). This confirms that pin still resolves — the read-only mirror of what setup writes.

Read `.linear_project` at the repo root:

- **Absent** → the repo isn't pinned. Not a failure — a repo that only runs workspace-level commands doesn't need one, and `/linear:setup` or `/linear:plan-work` writes it on first use. Report "not pinned" and move on.
- **Present** → read its `project = <name>` and confirm the project resolves (auth comes from the file's `api_key_env`, no wrap needed):

  ```bash
  uv run .claude/tools/linear_cli.py project get "<name>"
  ```

  A match confirms the binding is live. No match → the name in `.linear_project` doesn't resolve — the project was renamed or deleted, or `api_key_env` points at the wrong workspace. Point the user at `/linear:setup` to re-pin, or at `.linear_project` to fix the name.

### 5. Remind about board ordering

Linear only honours a manually pinned `sortOrder` — like an epic placed at the top of its project — when the board view is sorted by **Manual**. Under Created / Priority / Updated ordering the pin is ignored and the epic won't visibly move, even though the API write succeeded.

stride already sets Manual ordering on a *project's* board when it pins an epic there — automatically, via `set-project-view-manual` on the epic path (see [reference/epic-flow.md](reference/epic-flow.md)). What stays a manual UI step is the **team / work board view** you sequence day-to-day work in: Linear's API neither sets nor reports that view's sort mode, so `check` can't verify it and reminds instead:

> *"Can't read board sort order — if you sequence work by hand on a board view, confirm it's set to Manual, or stride's ordering looks scrambled. (Project boards pinned via the epic path are already Manual.)"*

A health-check reminder, not a failure — it always prints, since the mode is unreadable.

### 6. Summary

End with a one-line summary: "N of M Linear workspaces connected; K of L team boards in sync, N drifted; project binding ok / unresolved / not pinned." If any board drifted or the project binding didn't resolve, name `/linear:setup` as the next step.

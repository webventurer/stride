# Workspaces and teams

> **What this is**: the shared mechanics for discovering Linear workspaces and listing a team's board — used by [`/linear:check`](../check.md) and [`/linear:setup`](../setup.md). Both walk this ground (check verifies *every* workspace and team; setup targets *one*), so the commands live here once. Each caller keeps its own all-vs-one framing and links here for the mechanics.

## Find configured workspaces

Workspaces come from `LINEAR_*_API_KEY` env vars in `~/.env`:

```bash
env | grep -oE '^LINEAR_[A-Z_]+_API_KEY' | sort -u
```

If none are found, add at least one `LINEAR_<WORKSPACE>_API_KEY` — see [reference/setup.md](setup.md).

## List a workspace's teams

Boards are **per-team, not per-workspace** — a workspace can hold several teams, each with its own board. List them, wrapping the call in the workspace's key (the explicit per-workspace wrap, since these commands iterate workspaces rather than reading the single `.linear_project` key — see [How skills talk to Linear](workflow.md#how-skills-talk-to-linear)):

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py team list
```

Capture each team's **key** (e.g. `WB`) — it's the `--team` argument the state commands (`state-drift`, `provision-states`) need.

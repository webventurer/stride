# Linear setup

> **AI Assistant Note**: Reference this document when setting up Linear integration for a new project.

This guide covers how to connect Claude Code to Linear via linctl, using a per-workspace API key in `~/.env`.

## Quick reference

**Prerequisites**: A Linear workspace, `linctl` installed, and a `LINEAR_<TEAM>_API_KEY` in `~/.env` (see the [install guide](/install)).

**Utility commands:**

| Command | What it does |
|:--------|:-------------|
| `/linear:check` | Verify linctl auth — confirm each `LINEAR_<TEAM>_API_KEY` resolves, and the board matches `linear_statuses.json` |
| `/linear:setup` | Provision the workspace's workflow states from `linear_statuses.json` — creates missing columns, reorders to sequence, never deletes |
| `/linear:list-projects` | List all projects across connected Linear workspaces |
| `/linear:next-steps` | Review priorities, surface PRs needing fix, recommend what to work on next |

**Workflow commands:**

| Command | What it does |
|:--------|:-------------|
| `/linear:plan-work` | Draft and create a Linear issue with optional `--research` and `--craft` flags |
| `/linear:quick` | Ship a small change first, then file the card after merge (born Done) — for work too small to plan up front |
| `/linear:start` | Branch, implement, validate, open PR, and review the diff in the terminal |
| `/linear:fix` | Address GitHub PR review feedback, validate, push, and comment on the PR |
| `/linear:finish` | Squash merge an approved PR, delete branches, mark issue Done |

See [workflow.md](workflow.md) for detailed command docs and typical flow.

## Connecting to Linear

### 1. Add your API key

stride's `/linear:*` skills reach Linear through [linctl](https://github.com/dorkitude/linctl) using a per-workspace API key — no `.mcp.json`, no OAuth. Add one key per workspace to `~/.env`:

```
LINEAR_<TEAM>_API_KEY=lin_api_...
```

Get a key at [linear.app/settings/api](https://linear.app/settings/api). See the [install guide](/install) for the full prerequisite list.

### 2. Verify the connection

Run `/linear:check` to confirm linctl can authenticate against each `LINEAR_<TEAM>_API_KEY` set in `~/.env`. It runs `linctl whoami` per key and reports which workspace each one resolves to.

### 3. Install the Linear GitHub integration

Linear's [GitHub integration](https://linear.app/settings/integrations/github) connects PRs to issues automatically. Without it, `/linear:start` creates PRs that Linear doesn't know about — you lose status sync, auto-transitions, and the PR link on the issue.

**Install the GitHub App:**

1. Go to **Linear Settings** → **Integrations** → **GitHub**
2. Click **Connect** and authorize the GitHub App for your organisation
3. Select which repositories Linear can access

**What it enables:**

| Feature | Without integration | With integration |
|:--------|:-------------------|:-----------------|
| PR linked on issue | Manual | Automatic (via branch name) |
| Issue status on PR merge | Manual | Auto-transitions to Done |
| PR status visible in Linear | No | Yes (open, merged, closed) |
| Branch name linking | No | `username/pg-123-feature` links to PG-123 |

The `/linear:start` command already names branches in the format Linear expects (e.g. `mike/pg-205-add-dark-mode`). Once the integration is installed, Linear picks up the link automatically.

## Adapting for your project

The commands resolve the Linear project from a `.linear_project` file in the repo root. If this file does not exist, `/next-steps` and `/plan-work` will ask which project to use and save the selection.

- **Team**: resolved from `.linear_project` (or ask the user on first run)
- **Project**: read from `.linear_project`

---

*Setup once, then let the commands handle the Linear ceremony.*

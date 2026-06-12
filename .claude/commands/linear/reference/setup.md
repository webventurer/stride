# Linear setup

> **AI Assistant Note**: Reference this document when setting up Linear integration for a new project.

This guide covers how to connect Claude Code to Linear using a per-workspace API key in `~/.env`. The `/linear:*` commands talk to Linear's GraphQL API via stride's vendored `linear_cli.py` — no external CLI to install.

## Quick reference

**Prerequisites**: A Linear workspace and a `LINEAR_<WORKSPACE>_API_KEY` in `~/.env` (see the [install guide](/install)).

**Utility commands:**

| Command | What it does |
|:--------|:-------------|
| `/linear:check` | Verify auth — confirm each `LINEAR_<WORKSPACE>_API_KEY` resolves, and the board matches `linear_statuses.json` |
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

stride's `/linear:*` skills reach Linear via the vendored `linear_cli.py` (in `.claude/tools/`) using a per-workspace API key — no `.mcp.json`, no OAuth, no external CLI install. Add one key per workspace to `~/.env`:

```
LINEAR_<WORKSPACE>_API_KEY=lin_api_...
```

Get a key at [linear.app/settings/api](https://linear.app/settings/api). See the [install guide](/install) for the full prerequisite list.

**How Linear API keys are scoped:** Linear API keys are per workspace (per user, scoped to the workspace), not per team.

- An API key is created by a user under Settings → API → Personal API keys, and inherits that user's permissions across the entire workspace — every team they have access to.
- There is no concept of a team-scoped API key. To restrict scope to one team, you'd either use a dedicated service-account user that's only added to that team, or filter by `teamId` in your queries.
- OAuth apps work the same way at the workspace level; scopes are workspace-wide, not team-wide.

One key per workspace is the model — substitute the workspace identifier for `<WORKSPACE>` (e.g. `LINEAR_ACME_API_KEY` for an Acme workspace).

### 2. Verify the connection

Run `/linear:check` to confirm stride can authenticate against each `LINEAR_<WORKSPACE>_API_KEY` set in `~/.env`. It runs `linear_cli.py whoami` per key and reports which workspace each one resolves to.

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

The commands resolve the Linear project from a `.stride.json` file in the repo root. If this file does not exist, `/next-steps` and `/plan-work` will ask which project to use and save the selection.

- **Team**: resolved from `.stride.json` (or ask the user on first run)
- **Project**: read from `.stride.json`

### `.stride.json` format

```json
{
  "project": "Stride >>>",
  "api_key_env": "LINEAR_WEBVENTURER_API_KEY"
}
```

- `project` — the Linear project name.
- `api_key_env` — names the env var in `~/.env` that holds the workspace API key. When set, `linear_cli.py` reads the bearer token from that env var automatically, so per-call `LINEAR_API_KEY=$LINEAR_<X>_API_KEY` wraps aren't needed. Workspace-iterating commands (`/linear:check`, `/linear:setup`, `/linear:list-projects`) still use the explicit wrap since they target multiple workspaces.

Override the resolved token per-call with `LINEAR_API_KEY=<token>`.

---

*Setup once, then let the commands handle the Linear ceremony.*

# .claude/tools/

Small, vendored Python utilities that live alongside the repo. Each
file stands on its own — no package, no install, no dependency graph
beyond `requests` / `click`.

## Linear: `linear.py` (library) + `linear_cli.py` (CLI)

Stride's Linear client is split across two files:

- **`linear.py`** — the library. Talks Linear's GraphQL API directly via `requests`. All typed helpers, custom queries, and resolvers live here. Import-only.
- **`linear_cli.py`** — the CLI front-end. Click commands that wrap the library, used by every `/linear:*` slash command.

### Requirements

- **Python 3.10+**, **`click`**, **`requests`** — auto-installed by `uv run` via the PEP 723 header; no `pip install`.
- **`LINEAR_API_KEY`** in the environment (canonical), or **`LINCTL_API_KEY`** (legacy alias, still read for backward compat).

### What `linear.py` provides

**Issue queries** (return a list of node dicts: `identifier`, `title`, `state`):

- `search_by_project(project, text)` — text search within a project.
- `list_by_project_state(project, state, since=None)` — issues in a project in one state; `since` is an ISO8601 duration/datetime (e.g. `-P1W`) filtering on `createdAt`.
- `list_by_parent(parent_id)` — sub-issues of a parent (`parent_id` is the parent UUID).

**Milestones**:

- `list_milestones(project_id)` — returns `{id, name}` per milestone.
- `milestone_open_issues(milestone_id)` — non-Done (`backlog`/`unstarted`/`started`) issues in a milestone.
- `create_milestone(project_id, name, target_date=None)` — returns `{id, name}`; `target_date` is a `TimelessDate` (`YYYY-MM-DD`).
- `update_milestone_description(milestone_id, description)` — returns the success bool.

**Board order**:

- `min_backlog_sort_order(project_id)` — lowest Backlog `sortOrder`, or `None` if empty. Lower = higher on the board.
- `set_sort_order(issue_id, sort_order)` — returns the success bool.

**Workflow states** (`/linear:check`, `/linear:setup`):

- `state_drift(team_key=None)` — names declared in `linear_statuses.json` but missing from the team's board.
- `provision_states(team_key=None)` — on an empty team, creates/orders/archives states to match the JSON; on a populated team, returns an advisory report.

**Read helpers**:

- `get_issue(api_key, identifier)`, `get_project(api_key, identifier)`, `whoami(api_key)`.
- `list_teams(api_key)`, `get_team(api_key, key)`, `list_team_states(api_key, team_key)`.
- `list_comments(api_key, issue_id)`.

**Write helpers**: `create_issue` (returns the full issue object, accepts `parent_id`, `priority`, `project_milestone_id`, etc.), `update_issue` (accepts `parent_id`), `create_comment`, `create_attachment`, `create_project`, `update_project`.

**Resolvers** (name → UUID lookups used by the CLI):

- `resolve_project_id(api_key, name_or_id)` — round-trips UUIDs unchanged; resolves names via one query.
- `resolve_state_for_issue(api_key, identifier, state_name)` — returns `(issue_uuid, state_id)` in a single round-trip.
- `resolve_labels_for_team(api_key, team_id, names)` — translates label names → UUIDs scoped to a team.

`LinearError` is raised on HTTP, network, or GraphQL errors. `LinctlError` remains as a legacy alias.

### `linear_cli.py` subcommands

Every command outputs JSON. Slash commands parse JSON; ad-hoc terminal use pipes through `| jq`.

| Subcommand | Maps to |
|:-----------|:--------|
| `whoami` | `linctl whoami` |
| `issue get <id>` | `linctl issue get` |
| `issue create -t <team> --title ... [--project <name>] [--state <name>] [--priority N] [--labels a,b] [--parent <id>]` | `linctl issue create` |
| `issue update <id> [--state <name>] [--parent <id>] [--title] [--description] [--labels] [--priority]` | `linctl issue update` |
| `issue attach <id> --url <url> [--title <t>]` | `linctl issue attach` |
| `comment list <id>` | `linctl comment list` |
| `comment create <id> --body <text>` | `linctl comment create` |
| `team list` | `linctl team list` |
| `team state -t <team>` | `linctl team state` |
| `project list` | `linctl project list` |
| `project create -t <team> --name <name> [--description <subtitle>] [--content <body>]` | `linctl project create` |
| `project get <name-or-id>` | `linctl project get` (also accepts names; linctl is UUID-only here) |
| `project update <id> --description "..."` | `linctl project update` |
| `label list -t <team>` | `linctl label list` |

Plus the stride-specific flat commands: `search-by-project`, `list-by-project-state`, `list-by-project-state-type`, `list-by-parent`, `list-milestones`, `milestone-open-issues`, `create-milestone`, `update-milestone-description`, `get-project-content`, `update-project-content`, `min-backlog-sort-order`, `set-sort-order`, `state-drift`, `provision-states`.

### Usage

```bash
LINEAR_API_KEY=$LINEAR_ACME_API_KEY \
  uv run .claude/tools/linear_cli.py search-by-project --project "Stride >>>" --text "linctl"
LINEAR_API_KEY=$LINEAR_ACME_API_KEY \
  uv run .claude/tools/linear_cli.py issue get WB-453
LINEAR_API_KEY=$LINEAR_ACME_API_KEY \
  uv run .claude/tools/linear_cli.py project get "Stride >>>"
LINEAR_API_KEY=$LINEAR_ACME_API_KEY \
  uv run .claude/tools/linear_cli.py list-milestones <project-uuid>
LINEAR_API_KEY=$LINEAR_ACME_API_KEY \
  uv run .claude/tools/linear_cli.py min-backlog-sort-order <project-uuid>
LINEAR_API_KEY=$LINEAR_ACME_API_KEY \
  uv run .claude/tools/linear_cli.py set-sort-order <issue-uuid> --sort-order -120550
```

The `LINCTL_API_KEY=` wrap (still used by some slash commands while
they call `linctl` for the fat-CLI surface) keeps working — it falls
through to the same bearer-token resolver.

### Tests

All tests are pure-function or `requests.post`-mocked — they run
without network access:

```bash
python -m pytest .claude/tools/tests/test_linear.py
```

## `openrouter_cli.py`

Tiny OpenRouter CLI used by the `chorus` / plan-work feedback loops.
Not part of the Linear client — just shares the same `.claude/tools/` home.

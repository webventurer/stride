# .claude/tools/

Small, vendored Python utilities that live alongside the repo. Each
file stands on its own — no package, no install, no dependency graph
beyond `requests` / `click`.

## `linear_cli.py`

A Linear GraphQL client + the operations the `/linear:*` skills need:
project/parent-scoped issue queries, project milestones, board
`sortOrder`, workflow-state drift and provisioning. Talks Linear's
GraphQL API directly via `requests` — no external CLI dependency.

### Requirements

- **Python 3.10+**, **`click`**, **`requests`** — auto-installed by `uv run` via the PEP 723 header; no `pip install`.
- **`LINEAR_API_KEY`** in the environment (canonical), or **`LINCTL_API_KEY`** (legacy alias, still read for backward compat).

### What it provides

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

**CRUD helpers** (`create_issue`, `update_issue`, `list_issues`, `create_attachment`, `create_project`, `update_project`, `create_label`, `list_labels`, `resolve_by_name`, …) — vendored direct-GraphQL helpers, each taking an `api_key` argument. Not currently called by any slash command; available for future skills.

`LinearError` is raised on HTTP, network, or GraphQL errors. `LinctlError` remains as a legacy alias.

### Usage

```bash
# issue queries
LINEAR_API_KEY=$LINEAR_ACME_API_KEY \
  uv run .claude/tools/linear_cli.py search-by-project --project "Stride >>>" --text "linctl"
LINEAR_API_KEY=$LINEAR_ACME_API_KEY \
  uv run .claude/tools/linear_cli.py list-by-project-state --project "Stride >>>" --state Done --since -P1W
LINEAR_API_KEY=$LINEAR_ACME_API_KEY \
  uv run .claude/tools/linear_cli.py list-by-parent <parent-uuid>

# milestones
LINEAR_API_KEY=$LINEAR_ACME_API_KEY \
  uv run .claude/tools/linear_cli.py list-milestones <project-uuid>
LINEAR_API_KEY=$LINEAR_ACME_API_KEY \
  uv run .claude/tools/linear_cli.py create-milestone --project <project-uuid> --name "Phase 1" --target-date 2026-12-31

# board order
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
python -m pytest .claude/tools/tests/test_linear_cli.py
```

## `openrouter_cli.py`

Tiny OpenRouter CLI used by the `chorus` / plan-work feedback loops.
Not part of the Linear client — just shares the same `.claude/tools/` home.

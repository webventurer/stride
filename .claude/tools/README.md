# .claude/tools/

Small, vendored Python utilities that live alongside the repo. Each
file stands on its own — no package, no install, no dependency graph
beyond `httpx` / `click`.

## `linear_client.py` — archived

Moved to [`archive/linear_client.py`](../../archive/linear_client.py): a
Linear GraphQL API client (talks to the API directly via `requests`) built to
power the `*-to-linear` migration skills. Nothing on `main` imports it, and
the linctl-first direction means new work reaches for `linear_cli.py` (below)
instead. Kept in-tree but out of the installed footprint — restore it here if
a skill needs it again.

## `linear_cli.py`

A CLI for the Linear operations the `/linear:*` skills need that linctl's
typed commands can't express: project/parent-scoped issue queries, project
milestones, and board `sortOrder`. Each builds a GraphQL query and runs it
through `linctl graphql`, so it inherits linctl's auth (`LINCTL_API_KEY`) —
no second auth path, no `requests`. It is the single home for every
linctl-gap operation, so the skill markdown never inlines raw GraphQL.

Built for the linctl migration: linctl's `issue list` / `issue
search` filter by team and state but not by project or parent (and no
Linear CLI in the ecosystem exposes a parent filter — it's graphql-only),
linctl has no typed milestone command, and `issue update` has no
`--sort-order` flag. This wrapper fills exactly those gaps.

### Requirements

- **Python 3.10+** and **`click`** — auto-installed by `uv run` via the PEP 723 header; no `pip install`.
- **`linctl` on PATH** and **`LINCTL_API_KEY`** set to the target workspace key.

### What it provides

**Issue queries** (return a list of node dicts: `identifier`, `title`, `state`):

- `search_by_project(project, text)` — text search within a project.
- `list_by_project_state(project, state, since=None)` — issues in a project in one state; `since` is an ISO8601 duration/datetime (e.g. `-P1W`) filtering on `createdAt`.
- `list_by_parent(parent_id)` — sub-issues of a parent (`parent_id` is the parent UUID).

**Milestones** (linctl has no typed milestone command):

- `list_milestones(project_id)` — returns `{id, name}` per milestone.
- `milestone_open_issues(milestone_id)` — non-Done (`backlog`/`unstarted`/`started`) issues in a milestone.
- `create_milestone(project_id, name, target_date=None)` — returns `{id, name}`; `target_date` is a `TimelessDate` (`YYYY-MM-DD`).
- `update_milestone_description(milestone_id, description)` — returns the success bool.

**Board order** (`issue update` has no `--sort-order` flag):

- `min_backlog_sort_order(project_id)` — lowest Backlog `sortOrder`, or `None` if empty. Lower = higher on the board.
- `set_sort_order(issue_id, sort_order)` — returns the success bool.

`LinctlError` is raised on subprocess failure or a GraphQL `errors` payload.

### Usage

```bash
# issue queries
LINCTL_API_KEY=$LINEAR_WEBVENTURER_API_KEY \
  uv run .claude/tools/linear_cli.py search-by-project --project "Stride >>>" --text "linctl"
LINCTL_API_KEY=$LINEAR_WEBVENTURER_API_KEY \
  uv run .claude/tools/linear_cli.py list-by-project-state --project "Stride >>>" --state Done --since -P1W
LINCTL_API_KEY=$LINEAR_WEBVENTURER_API_KEY \
  uv run .claude/tools/linear_cli.py list-by-parent <parent-uuid>

# milestones
LINCTL_API_KEY=$LINEAR_WEBVENTURER_API_KEY \
  uv run .claude/tools/linear_cli.py list-milestones <project-uuid>
LINCTL_API_KEY=$LINEAR_WEBVENTURER_API_KEY \
  uv run .claude/tools/linear_cli.py create-milestone --project <project-uuid> --name "Phase 1" --target-date 2026-12-31

# board order
LINCTL_API_KEY=$LINEAR_WEBVENTURER_API_KEY \
  uv run .claude/tools/linear_cli.py min-backlog-sort-order <project-uuid>
LINCTL_API_KEY=$LINEAR_WEBVENTURER_API_KEY \
  uv run .claude/tools/linear_cli.py set-sort-order <issue-uuid> --sort-order -120550
```

### Tests

All tests are pure-function or subprocess-mocked — they run without
network, linctl, or `LINEAR_E2E`:

```bash
python -m pytest .claude/tools/tests/test_linear_cli.py
```

## `openrouter_cli.py`

Tiny OpenRouter CLI used by the `chorus` / plan-work feedback loops.
Not part of the Linear client — just shares the same `.claude/tools/` home.

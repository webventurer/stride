# .claude/tools/

Small, vendored Python utilities that live alongside the repo. Each
file stands on its own — no package, no install, no dependency graph
beyond `requests` / `httpx` / `click`.

## `linear_client.py`

A small Python client for the Linear GraphQL API. Built to power the
`linear-to-linear` and `trello-to-linear` migration skills in this
repo, but reusable in any Python script that needs to create issues,
projects, labels, or attachments in Linear straight through the
GraphQL API.

### Vendor contract

<mark>**Copy the file, no support, no versioning, no PyPI.** If you copy `linear_client.py` into your project, you own your copy. It is not a published package. There are no releases, no changelog, no semver guarantees. When Linear's API changes, we update `linear_client.py` in this repo — it is your job to pull the update into your vendored copy (or fix it yourself).</mark>

This is a deliberate choice. The alternative — a published SDK with a
support contract — costs more in ceremony than it would save in
convenience for the small number of scripts that will ever use this.

### Requirements

- **Python 3.10+** — the module uses PEP 604 union syntax (`dict | None`). On 3.9 you will get a `TypeError` at import time.
- **`requests`** — the only external dependency. `pip install requests` and you're done.

### What it provides

- `graphql(api_key, query, variables)` — raw client with retries and
  proper error handling (`LinearError` on HTTP or GraphQL errors).
- `resolve_by_name(api_key, entity, name)` — convenience for turning
  names into IDs.
- `resolve_states(api_key, team_id)` — workflow states by team.
- `require_env(name)` — env var helper.
- `normalize_quotes(text)` — fold smart quotes to straight quotes.
- `LinearError` — the exception raised on any failure.

#### Mutations (all return the created/updated node id as a string)

- `create_issue(api_key, team_id, project_id, state_id, title, description, label_ids=None)`
- `update_issue(api_key, issue_id, title=None, description=None, state_id=None, label_ids=None)`
- `create_attachment(api_key, issue_id, title, url, subtitle=None, metadata=None)`
- `create_project(api_key, team_id, name, description=None, content=None)`
- `update_project(api_key, project_id, description=None, content=None)`
- `create_project_update(api_key, project_id, body, health)`
- `create_project_link(api_key, project_id, url, label)`
- `create_label(api_key, name, color=None, team_id=None)`
- `delete_issue(api_key, issue_id)`
- `delete_project(api_key, project_id)`
- `delete_label(api_key, label_id)`

#### Queries

- `list_issues(api_key, team_id=None, project_id=None)` — auto-paginates. Returns list of dicts: `id`, `identifier`, `title`, `description`.
- `list_projects(api_key, team_id=None)` — auto-paginates. Returns list of dicts: `id`, `name`, `teams`. Filter by team client-side if `team_id` is passed.
- `list_labels(api_key, team_id=None)` — auto-paginates. Returns list of dicts: `id`, `name`, `color`, `team`. Filter by team client-side if `team_id` is passed.

### API contract

- **IDs only.** Mutation helpers accept entity IDs, not names. Use
  `resolve_by_name()` first if you start from a name.
- **Returns an ID string.** Every create/update helper returns the
  created or updated node's id.
- **Raises `LinearError` on failure.** Connection errors (after
  retries), HTTP errors, and 200 responses with a GraphQL `errors`
  payload all raise `LinearError` with the operation name and error
  messages. Never logs API keys.
- **Retries only connection errors and timeouts.** GraphQL errors are
  raised, not retried.

### What's deliberately missing

The current surface stops at the CRUD that our own in-repo skills needed. If you're integrating this into a new project, you may reach for helpers that aren't here:

- `get_issue(issue_id)` — single-issue read. Use `list_issues(project_id=...)` and filter client-side, or call `graphql()` directly.
- `list_comments(issue_id)` / `create_comment(issue_id, body)` — comment CRUD.
- `list_milestones(project_id)` / `create_milestone(...)` — project milestones.
- User, team, and cycle queries beyond `resolve_by_name()`.
- Pagination cursors exposed to the caller (list helpers paginate internally and return the full list).

These aren't broken or hidden — they're just outside the line we drew around "things our skills call". The vendor contract is explicit: copy the file and add what you need in your own vendored copy. The `graphql()` helper gives you the full Linear GraphQL API directly; the typed helpers are just a convenience layer over the dozen or so operations we happened to need first.

### Usage

```python
from linear_client import create_issue, resolve_by_name, require_env

api_key = require_env("LINEAR_API_KEY")
team_id = resolve_by_name(api_key, "teams", "Engineering")
project_id = resolve_by_name(api_key, "projects", "my-project")
state_id = resolve_by_name(api_key, "workflowStates", "Backlog")

issue_id = create_issue(
    api_key,
    team_id=team_id,
    project_id=project_id,
    state_id=state_id,
    title="Investigate flaky test",
    description="The auth test fails 1 in 50 runs.",
)
print(f"Created {issue_id}")
```

### Tests

Live tests are gated by `LINEAR_E2E=1` so they only run when a real
API key is available. The mocked error-handling test runs
unconditionally.

```bash
python -m pytest .claude/tools/tests/              # unit only
LINEAR_E2E=1 python -m pytest .claude/tools/tests/ # live + unit
```

Set `LINEAR_TEST_API_KEY_ENV` and `LINEAR_TEST_TEAM` if you want to
target a workspace other than the default `LINEAR_PLAYGROUND_API_KEY`
/ `Playground`.

### Skill-specific loaders

`load_source_cards` and `load_target_issues_file` live in
`.claude/skills/linear-to-linear/scripts/skill_io.py`. They know the
shape of the export/match JSON files that `linear-to-linear`
produces and are not part of the reusable client.

### How the in-repo skills import it

Skill scripts live in `.claude/skills/<skill>/scripts/` and are run
directly with `python scripts/foo.py`. Each script does:

```python
import _bootstrap  # noqa: F401
from linear_client import ...
```

The `_bootstrap.py` module sits next to the scripts and adds
`<repo-root>/.claude/tools` to `sys.path` so the `linear_client`
import resolves to this directory.

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

### Why it's separate from `linear_client.py`

| | `linear_client.py` | `linear_cli.py` |
|:--|:--|:--|
| Talks to | Linear API directly (`requests`) | `linctl graphql` (subprocess) |
| Auth | `LINEAR_<TEAM>_API_KEY` via `require_env` | `LINCTL_API_KEY` (linctl's own) |
| Used by | migration skills (`*-to-linear`) | `/linear:*` workflow skills |

Keeping them apart preserves one auth model per skill family.

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

## `openrouter-chat.py`

Tiny OpenRouter CLI used by the `chorus` / plan-work feedback loops.
Not part of the Linear client — just shares the same `.claude/tools/` home.

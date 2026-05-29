# Linear workflow

> **AI Assistant Note**: Reference this document when explaining what the Linear commands do or how the workflow fits together.

## Typical workflow

**Utility:**

```
/linear:check               → verify Linear auth + board matches statuses JSON
/linear:setup               → provision workflow states (non-destructive)
/linear:list-projects       → list all projects across workspaces
/linear:next-steps          → see what needs doing
```

**Workflow:**

```
/linear:plan-work           → create a new issue (if needed)
/linear:start PG-X          → branch, implement, PR, terminal review
  ... you review the diff in the terminal ...
  ... someone reviews on GitHub ...
/linear:fix PG-X            → address GitHub review feedback (if any)
/linear:finish PG-X         → squash merge, clean up, Done
```

For a change too small to plan up front, skip the card-first cycle:

```
/linear:quick "small fix"   → implement, review, then say a ship phrase
  ... you review the diff in the terminal, then say "ship it" ...
                            → merge + file the card retroactively in Done
```

## What's an "issue"?

It's the universal term for a **tracked item** — something that needs attention. The word comes from bug tracking ("there's an issue with X"), but it got stretched to cover everything: features, bugs, tasks, research, chores.

A new feature is an "issue" in Linear/GitHub/Jira. It's not that the feature *is* an issue — it's that the **tracking artifact** for the feature is called an issue. The word describes the container, not the content.

It's like how every email is called a "message" whether it's a question, an announcement, or a complaint. "Message" is the container; the content varies.

## How skills talk to Linear

Stride's `/linear:*` skills call `linear_cli.py` (in `.claude/tools/`) — a vendored Python client that talks Linear's GraphQL API directly via `requests`. No external CLI install.

Project-scoped commands read the bearer token from `.linear_project`'s `api_key_env` field automatically — no per-call wrap. Workspace-iterating commands (`/linear:check`, `/linear:setup`, `/linear:list-projects`) wrap each call explicitly with the workspace's env var:

```bash
LINEAR_API_KEY=$LINEAR_<WORKSPACE>_API_KEY uv run .claude/tools/linear_cli.py <verb> ...
```

Substitute `<WORKSPACE>` with the workspace name you're driving against (e.g. `LINEAR_ORG1_API_KEY`). The per-workspace variables live in `~/.env` per [setup.md](setup.md). One stride install can drive multiple Linear workspaces — the env-var-per-workspace pattern is how you switch between them per invocation.

**JSON for agents:** `linear_cli.py` always outputs JSON, so the agent can parse with `jq` without a flag.

**Why a vendored client, not MCP:** MCP loads ~60k tokens of schema before the agent reasons; the vendored client loads zero. Plus stride owns the auth path end-to-end — no second protocol to configure.

## Workflow states

The state names the `/linear:*` commands move issues through — `Backlog` on create, `Doing` on start, `In Review` after the PR, `Done` on finish — are defined once in [`linear_statuses.json`](../linear_statuses.json), grouped by Linear's state type and mapped to each workflow transition. That file is the source of truth for the names stride uses and for the type groups `/linear:next-steps` filters on.

The call sites keep readable literals (`linear_cli.py issue update <id> --state Doing`) for scannability — but the canonical list is the JSON. `/linear:check` diffs it against the live board (via `linear_cli.py state-drift`) and flags any state stride expects that the board doesn't have, catching the silent-no-op trap a name mismatch causes (e.g. `In Progress` matching nothing). Adapting stride to a workspace whose states are named differently starts here: edit the JSON, then run `/linear:check` to confirm the board matches.

## Reviewing PRs in VS Code

To review pull requests directly in VS Code, install the [GitHub Pull Requests](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-pull-request-github) extension. It lets you browse, review, and comment on PRs with in-editor line comments — no need to switch to the browser.

## Board ordering — set the view to Manual sort

stride sequences your work by setting each issue's position on the board — `/linear:plan-work` places new issues, and you arrange the backlog into the order you'll tackle it. **That order only shows if your Linear board (or the view you use for stride work) is sorted by "Manual".**

If the view is sorted by **Priority**, **Created**, or **Updated** instead, Linear ignores the manual positions entirely, and stride's execution order looks scrambled — cards group by priority or date rather than the sequence you set. The fix is one setting: open the view's sort menu and choose **Manual**.

Board sort is a per-view setting in Linear's UI, so stride can't set it for you — hence this note rather than an automated step.

## Commands

### `/linear:next-steps`

**Review priorities and recommend next work.** Shows current work, open PRs, recently completed issues, and backlog — then recommends 1–3 concrete next actions.

Priority ordering: build failure > PRs needing fix > in-progress work > PRs needing review > approved PRs to merge > backlog.

For each open PR, checks GitHub for `CHANGES_REQUESTED` reviews and unresolved comments. PRs needing fix are surfaced above new backlog work.

**Usage**: `/linear:next-steps`

### `/linear:plan-work`

**Plan work and create a Linear issue.** Checks for duplicates, optionally refines the description with CRAFT, drafts title and description, and waits for your approval before creating.

In `--research` mode, explores the codebase and Linear first, then adds code examples (showing how similar patterns are already implemented) and acceptance criteria (observable outcomes, not implementation steps).

Also assesses whether tests make sense for the change. If they do, the issue notes that tests should be written first — not strict TDD, but having them in place catches regressions later.

**Usage**:

- `/linear:plan-work "add dark mode toggle"` — quick mode
- `/linear:plan-work --research "add PostHog integration"` — research mode with code examples and acceptance criteria
- `/linear:plan-work --craft "add dark mode toggle"` — auto-run CRAFT prompt refinement
- `/linear:plan-work --research --craft "add PostHog integration"` — research + CRAFT combined

### `/linear:start`

**Start work on a Linear issue.** One headless flow: create or switch to the feature branch, move the issue to Doing, implement the changes, validate (build + tests), commit, push, open a PR, move to In Review, then show the full diff for terminal review.

Trusts the issue — the plan was agreed during `/plan-work`. No approval gate mid-flow.

Ends by asking: "Does this look right, or do you want changes?" If you request changes, it fixes, re-validates, and shows the updated diff. Repeat until satisfied.

**Usage**:

- `/linear:start PG-205` — explicit issue
- `/linear:start` — infers from branch

### `/linear:fix`

**Address GitHub PR review feedback.** Reads review comments from GitHub (review body, line comments, past reviews), implements all requested changes in one pass, validates, pushes, and posts a summary comment on the PR.

Reviewer feedback takes priority over the original issue — plans evolve through review.

**Usage**:

- `/linear:fix PG-205` — explicit issue
- `/linear:fix` — infers from branch

### `/linear:finish`

**Finish the issue.** Runs build + tests (stops if they fail), squash merges the PR with a clean commit message, switches to main, deletes local and remote branches, and marks the issue Done in Linear.

The squash commit message reads as if the work was done right the first time — no mention of rejections, fix cycles, or iterations.

**Usage**:

- `/linear:finish PG-205` — explicit issue
- `/linear:finish` — infers from branch

---
description: Recommend what to work on next, ranked against the project Vision.
---

# Review priorities and recommend next work

Review what's happening and recommend what to work on next.

Read [unattended mode](reference/unattended.md) before the first optional
prompt. Unattended mode ranks all work and writes Todo's order; it changes
nothing else.

## Decision rules

- **Priority ordering**: build failure > PRs needing fix > in-progress work > PRs needing review > approved PRs to merge > backlog
- If there are started issues assigned to the current user, treat these as the primary tasks
- Do not recommend new work unless current tasks are blocked or completed
- Sort backlog candidates by priority: Urgent > High > Medium > Low
- **Within each tier, refine ordering by Vision alignment** — see [reference/align-to-vision.md](reference/align-to-vision.md). Items advancing least-progressed Success criteria sit higher within the tier
- Prefer quick wins when priorities and alignment are equal (small, self-contained issues)
- Treat issues with dependencies, blocker labels, or blocked status as blocked
- Flag blocked issues but do not recommend them
- Recommend 1–3 concrete next actions, not a full backlog dump

## Steps

### 0. Resolve project

Check for a `.stride.json` file in the repository root.

- If **found**: read the project name from it (`project` field in JSON)
- If **not found**: list available projects (`uv run .claude/tools/linear_cli.py project list` — auth per [reference/workflow.md](reference/workflow.md)), ask the user to choose, then ask which `LINEAR_*_API_KEY` env var in `~/.env` authenticates that workspace. Save all five fields as `.stride.json`:

  ```json
  {
    "project": "<chosen-project-name>",
    "api_key_env": "LINEAR_<WORKSPACE>_API_KEY",
    "focus": "outcome",
    "unattended": false,
    "parallel-sessions": 3
  }
  ```

  Then check the repo's `.gitignore` — if `.stride.json` isn't listed, append it. The `focus` field sets the default output abstraction — `"outcome"` is the default; see [reference/output-focus.md](reference/output-focus.md) for the accepted values. The `unattended` field defaults to `false`; see [reference/unattended.md](reference/unattended.md). The `parallel-sessions` field defaults to `3`: the most cards stride runs at once; see [recovery/backfill-parallel-sessions-field.md](recovery/backfill-parallel-sessions-field.md).

  Then set the chosen project's board to Manual ordering, so stride's `sortOrder` pins show from the first card (the call is idempotent):

  ```bash
  uv run .claude/tools/linear_cli.py project get "<chosen-project-name>"
  uv run .claude/tools/linear_cli.py set-project-view-manual <project-id>
  ```

Use the resolved project name for all Linear API calls in this command.

### 1. Vision check

Vision is the guiding light for ranking — without it, recommendations drift from the project's stated purpose. Before fetching candidates, check that one exists.

Read `VISION.md` from the repo root.

- **If missing**: stop and tell the user:

  ```
  No VISION.md found at the repo root.

  /linear:next-steps needs a Vision to rank candidates against
  — without one, recommendations drift from the project's
  stated purpose.

  Run /vision first, then re-run /linear:next-steps.
  ```

  Do not rank candidates against a project with no anchor.

- **If present**: read the full file and load its Success criteria as context for step 6 (Recommend next actions).

### 2. Fetch data (all calls in parallel)

All `linear_cli.py` calls below read the bearer token from `.stride.json`'s `api_key_env` field automatically — no per-call wrap needed.

| Call | Purpose |
|:-----|:--------|
| `uv run .claude/tools/linear_cli.py whoami` | Authenticated user |
| `uv run .claude/tools/linear_cli.py list-by-project-state-type --project "<project>" --type started` | Started issues (spans all started-type states, e.g. Doing / In Review / Waiting) |
| `uv run .claude/tools/linear_cli.py list-by-project-state --project "<project>" --state Todo` | Unstarted issues |
| `uv run .claude/tools/linear_cli.py list-by-project-state --project "<project>" --state Backlog` | Backlog issues |
| `uv run .claude/tools/linear_cli.py list-by-project-state --project "<project>" --state Done --since -P1W` | Recently completed |
| `uv run .claude/tools/linear_cli.py list-milestones <project-UUID>` | Milestones |
| `uv run .claude/tools/linear_cli.py search-by-project --project "<project>" --text "Epic: "` | Parent-issue epics (matched by title prefix) |
| `gh pr list --state open number,title,headRefName,author,reviewDecision,reviews,url` | Open PRs |

### 3. Show current work

If there are started issues, show them first — they provide context for what's already happening.

| ID | Title | Assignee | Priority |
|:---|:------|:---------|:---------|

If none: "Nothing currently in progress."

### 4. Open pull requests

If there are open PRs, show them:

| PR | Title | Branch | Review | Action |
|:---|:------|:-------|:-------|:-------|

For each PR, check for unaddressed review feedback:

```bash
gh api repos/{owner}/{repo}/pulls/<number>/reviews --jq '[.[] | select(.state == "CHANGES_REQUESTED")] | length'
gh api repos/{owner}/{repo}/pulls/<number>/comments --jq 'length'
```

Classify each PR:

- **Needs fix** — has `CHANGES_REQUESTED` or unresolved review comments → recommend `/fix <issue-id>`
- **Needs review** — `reviewDecision` is not `APPROVED` and no feedback yet → waiting on reviewers
- **Approved** — ready to merge → recommend `/finish <issue-id>`

PRs needing fix take priority over all new backlog work.

If none: "No open pull requests."

### 5. Recently completed (last 7 days)

| ID | Title | Completed |
|:---|:------|:----------|

If none: "No issues completed recently."

This context should influence recommendations — prefer follow-up issues or related tasks where appropriate. The completed list also informs Vision-alignment ranking in step 7: criteria with several recent completions are *more* progressed; criteria with none are *less* progressed.

### 6. Build candidate list

Combine `unstarted` and `backlog` issues into a single candidate list. Exclude issues already in `started`. Exclude issues identified as blocked. Sort by priority (Urgent first).

If milestones or parent-issue epics exist for the project, unattended mode uses
all work and groups the list by epic and milestone. Interactive mode asks:
**"Show next steps for a specific epic, or all work?"** Combine both signals
when offering choices — list parent-issue epics (titles starting with `Epic: `)
and milestones together as filter options, with the source labelled. If the
user picks a parent-issue epic, filter the candidate list to issues whose
`parentId` equals that epic's ID. If they pick a milestone, filter by
`milestone`. If they pick all work, group the candidate list by epic and by
milestone, with one group for issues that have neither.

Show as a table per epic/milestone (or one combined table when no epics or milestones exist):

| ID | Title | Priority | Labels | Status |
|:---|:------|:---------|:-------|:-------|

If the list is empty: "Backlog is empty — nothing to recommend."

#### Put Todo in the order stride will work it

Todo's order on the board is the order work happens, so next-steps writes it, by rule rather than judgement: priority first, Urgent to Low and then No priority; equal priorities keep their current order; a card never sits above the Todo card it's waiting on, read from Linear's "blocked by" links; `Epic: ` cards keep their place. Show the order first:

```bash
uv run .claude/tools/linear_cli.py order-todo --project "<project>" --dry-run
```

Interactive mode shows that order and asks once: **"Write this order to Todo on the board? (y/n)"**. Unattended mode writes it. To write it, run the same command without `--dry-run`: it sets the project's board view to Manual, so the order shows, then rewrites only the Todo cards whose place changed. It changes nothing else on the board. Vision alignment still shapes the recommendations below; it doesn't decide board order.

#### Pick the next batch

Cards that don't depend on each other can run side by side, so next-steps names the next batch. It works down Todo in the order above, adding each card that passes two rules, until the batch holds the `parallel-sessions` number from `.stride.json` or Todo runs out:

- **Blockers:** a card is out while any card blocking it is not Done, wherever that blocker sits. A blocker that is Done doesn't count.
- **Files:** a card is out when it shares a file with a card already in the batch. A card's files are the backticked names ending in a file extension, such as `next-steps.md`, in its "What we'll do" section.

```bash
uv run .claude/tools/linear_cli.py next-batch --project "<project>"
```

Show each card it considered, in or out, with the reason it gives, such as "blocked by WB-12" or "shares `report.py` with WB-14". Call the batch a best guess: two cards can still clash in a file neither names. When the command stops with the `parallel-sessions` setting's message instead, show that message in place of a batch. Next-steps doesn't run the batch.

### 7. Recommend next actions

Apply the priority ordering: build failure > PRs needing fix > in-progress > PRs needing review > approved PRs to merge > backlog.

**Within the backlog tier, apply [reference/align-to-vision.md](reference/align-to-vision.md)** to refine ordering — items advancing least-progressed Vision Success criteria sit higher within the tier. Use the recently-completed list from step 5 plus the started/in-flight context as signals for which criteria are progressed.

Pick 1–3 items. For each recommendation, explain briefly why it's the right next move using factors such as: priority, quick win potential, follow-up to recently completed work, unblocking other work, PR needing review, alignment with current work in progress. **Name the Vision outcome the item serves** so the user sees why the agent picked it.

Read the output focus and apply this command's format from [reference/output-focus.md](reference/output-focus.md).

If a candidate doesn't cleanly trace to any Success criterion, surface that honestly rather than inventing a tie-in (see [reference/align-to-vision.md](reference/align-to-vision.md) for the surfacing format).

### 8. Offer to start

Interactive mode asks: "Want me to start one of these? I can run `/start <ID>`
for you." Unattended mode ends after the recommendations; next-steps never starts
work automatically.

When `/linear:start` runs next-steps because no card was named, skip this step: `/linear:start` acts on the batch next-steps named.

# Plan work and create a Linear issue

Accepts a description and optional flags: `/plan-work --research --craft --worktree --epic "add error handling to API calls"`. With `--worktree`, the command also sets up an isolated git worktree for the new issue after creation. With `--epic`, it skips size-sensing and goes straight to the parent-issue flow.

## Modes

- **Quick mode** (default): `/plan-work "description"` — draft, review, create
- **Research mode**: `/plan-work --research "description"` — explore codebase and Linear first, then draft with richer context

## Flags

- `--research` — explore codebase and Linear before drafting (adds implementation notes, code examples, related code and issues)
- `--craft` — auto-run CRAFT prompt refinement without asking (skips the interactive prompt in step 4)
- `--worktree` — after issue creation, set up an isolated git worktree at `../<repo-dirname>-<issue-id-lowercase>` and hand off to a new Claude Code session (see step 12). `/linear:start` runs inline by default; pass this flag at planning time if the work needs an isolated workspace.
- `--epic` — skip size-sensing and go straight to the epic-sized parent-issue flow (see step 4b). Pass this when you already know the description is a named initiative with multiple stories.

## Decision rules

- **Vision is the anchor**: every issue must trace back to a Vision outcome. The draft's "Why this matters" section must reference which Vision outcome the issue serves. If it can't, ask the user to choose: **add a new criterion to `VISION.md` (re-run `/vision` to evolve it), or drop the issue as out of scope**. Don't draft past this prompt — repeated trace-back failures are a signal the Vision needs updating, not that the gate should be loosened. Without `VISION.md` at the repo root, the command stops and suggests `/vision` (see step 1).
- **Story is the default; epic when warranted**: most descriptions are story-sized (one deliverable, ships as one PR), and stride defaults to that without asking. Epic-sized work (a named initiative with multiple stories) is reached two ways — the `--epic` flag, or size-sensing surfacing a soft prompt when epic-shape signals fire (see step 4b). Epic-sized work becomes a parent issue with sub-issues for each story; story-sized work becomes an issue, optionally linked to an existing epic via `parentId`.
- **Epic title prefix**: epic-sized parent issues use `Epic: <stakeholder outcome>` as their title — the prefix makes the scope visible at a glance on the kanban board, and the post-colon part still follows the stakeholder-outcome rule. Example: `Epic: Bulk/Batch Blog Processing (parallel article pipeline)`.
- One issue = one deliverable. If the description contains "and" connecting unrelated outcomes, split.
- Default to the smallest issue that moves something forward. If the user's description is broad, propose a focused first issue plus follow-ups.
- **When proposing multiple follow-ups, order them by Vision alignment** — see [reference/align-to-vision.md](reference/align-to-vision.md). The follow-up advancing the least-progressed Success criterion sits first.
- Titles are imperative and start with a verb (Add, Fix, Replace, Remove…). Avoid "Investigate" unless the outcome genuinely is a report, not a code change.
- Titles describe the outcome a stakeholder would recognise — what changes from their perspective — not the implementation. *"Background jobs run reliably after the first one"*, not *"Reset Tortoise globals between RQ jobs"*. Infrastructure exception: when there's no user-visible outcome, name the *system behaviour* that changes (e.g. "Linter accepts 100-char lines"), not the file that changes. See `docs/reference/issue-template.md` for the canonical rule and examples.
- Never assign the issue unless the user explicitly asks.
- Labels are optional — suggest at most 3, only when clearly relevant. Prefer no labels over speculative ones.
- Priority defaults to Medium. Only upgrade if the user says it's urgent or the description implies user-facing impact (breakage, a time-sensitive launch, etc.).
- Research mode exists to improve the draft, not to produce an audit. Cap file exploration at 2–5 relevant files; summarise patterns, don't catalogue the repo.
- Duplicate handling is two-tier: exact/near-exact → warn strongly and ask; similar/related → mention briefly and continue.
- The user always gets final approval before creation. Never auto-create.

## Steps

### 0. Resolve project

Check for a `.linear_project` file in the repository root.

- If **found**: read the project name from it
- If **not found**: list available projects via `list_projects`, ask the user to choose, and save their selection to `.linear_project`. Then check the repo's `.gitignore` — if `.linear_project` isn't listed, append it.

Use the resolved project name for all Linear API calls in this command.

### 1. Vision check

Vision is the guiding light — every issue drafted by stride must trace back to a Vision outcome. Before sizing or drafting, check that one exists.

Read `VISION.md` from the repo root.

- **If missing**: stop and tell the user:

  ```
  No VISION.md found at the repo root.

  /linear:plan-work needs a Vision to anchor issues to — without
  one, every issue is drafted in a vacuum and nothing measures
  whether the work belongs in this project.

  Run /vision first, then re-run /linear:plan-work.
  ```

  Do not draft an issue against a project with no anchor.

- **If present**: read the full file and load it as context for the rest of the flow. The Success criteria section in particular tells you what outcomes the project is committed to — the draft's "Why this matters" should connect the proposed work to one of them.

<mark>**This is a hard gate, not a warning.**</mark> Stop-and-suggest, don't draft-with-warning. Vision-less drafting produces issues that look fine in isolation but accumulate as drift.

### 2. Parse arguments

Extract the description and flags from `$ARGUMENTS`. Determine if `--research`, `--craft`, `--worktree`, and/or `--epic` are present.

### 3. Duplicate check (all modes)

Search Linear for potentially related issues:

```
list_issues with a query matching key terms from the description
```

Handle results in two tiers:

- **Exact or near-exact duplicates** (same problem, same scope): warn strongly, show them, and ask whether to proceed or stop.
- **Similar or related issues** (overlapping area but different scope/angle): show briefly, continue drafting, and reference them in the draft's "Related issues" section.

### 4. CRAFT prompt refinement (all modes)

<mark>**When `--craft` is present, always run CRAFT before research. Never skip this step.**</mark> The user passes `--craft` to sharpen their description into a clearer prompt — skipping it means research works from a vaguer input than intended.

If `--craft` flag is present, run CRAFT automatically. Otherwise, ask the user: "Would you like me to run `/craft` on your description first to sharpen the issue before drafting?"

- If **yes** (or `--craft`): read [reference/ISSUE-TEMPLATE.md](reference/ISSUE-TEMPLATE.md) for story-sized work, or [reference/EPIC-TEMPLATE.md](reference/EPIC-TEMPLATE.md) when drafting the parent issue on the epic-sized path. Substitute `[user's description]` with what the user provided **and** `[VISION]` with the full contents of the `VISION.md` loaded in step 1, run `/craft` with the populated prompt, then use the refined output as the description for all subsequent steps. Substituting the entire Vision into the prompt is what lets the agent — or any model the prompt is sent to — anchor the draft on real criteria, real constraints, and real non-goals rather than guessing.
- If **no**: continue with the original description

### 4b. Size — story by default, epic when warranted

Story is the default. Most descriptions are story-sized — one deliverable that ships as one PR — and asking every invocation imposes epic-shaped overhead on the common case. Skip this step and continue to step 5 unless one of the following triggers fires.

**Trigger 1 — `--epic` flag.** If `--epic` was parsed in step 2, skip size-sensing entirely and follow the **epic-sized path** below.

**Trigger 2 — size-sensing detects epic shape.** Read the description (the `--craft`-refined version from step 4 if `--craft` was used; otherwise the raw input). Look for **epic-shape signals**:

- Multiple `and`-joined outcomes that don't share a single purpose
- References to *"phases"*, *"stages"*, *"milestones"*, *"Q2"*, *"by launch"*, *"rollout"*, etc.
- A description that resists a single stakeholder-readable PR title without joining unrelated ideas with `and`
- Length and structure that suggest a roadmap rather than a deliverable (5+ paragraphs of *"first we'll, then we'll, then we'll"*)

If any signals fire, surface a **soft prompt** — not a forced gate:

> *"This sounds epic-sized — I'm seeing [name the signals: multiple phases / unrelated outcomes / a rollout shape]. Want to break it into stories under an epic, narrow this to one story-sized deliverable, or proceed as one story?"*

Three paths:

- **Break into epic** → follow the **epic-sized path** below.
- **Narrow to story** → ask which slice to file as the first story; defer the rest. Continue to step 5 with the narrowed description as story-sized.
- **No, it's one story** → continue to step 5 as story-sized.

If no signals fire, skip silently and continue to step 5 as story-sized. The common path stays frictionless.

<mark>**Size-sensing offers, doesn't force.**</mark> When signals are detected, the agent asks; the user always has final say. Auto-flipping silently would be a worse failure mode than the old forced ask.

**Story-sized path** (default / "no, it's one story" / "narrow to story") — continue to step 5 as normal. At step 10 (create issue), also call `list_issues` filtered for parent-issue epics in the project (titles starting with `Epic: `): if any exist, ask "Link this story to an existing epic?" and if yes, set the `parentId` field on `save_issue` to the chosen epic's ID. Legacy milestones — boards may still have them from before WB-279; if `list_milestones` returns any, offer them as a secondary option and use the `milestone` field instead.

**Epic-sized path** (`--epic` / "break into epic") — follow the parent-issue path:

1. Call `list_issues` filtered for existing parent-issue epics in the project (titles starting with `Epic: `) and show any matches.
2. Ask: "Create a new epic, or link these stories to an existing one?"
3. If creating: run duplicate check (step 3), CRAFT if requested (step 4), then steps 5 onwards (research, test consideration, draft, approval, create) for the **parent issue** — skip step 4b on the recursion since size has already been decided. Use [reference/EPIC-TEMPLATE.md](reference/EPIC-TEMPLATE.md) instead of ISSUE-TEMPLATE.md and prefix the title with `Epic: `. Save the parent issue first via `save_issue` (in Backlog) and capture the returned ID.
4. Confirm the parent issue with the user before drafting sub-issues.
5. Ask: "What are the first 1–3 stories for this epic?" — each answer becomes a separate issue draft.
6. For each story: run duplicate check (step 3), CRAFT if requested (step 4), then steps 5 onwards with `parentId` set to the parent issue's ID on `save_issue` — again skip step 4b. Story drafts use ISSUE-TEMPLATE.md as normal — they're stories that happen to have a parent.
7. After all stories are created, summarise: list the parent epic and all sub-issues created underneath it.

<mark>**Do not bundle all stories into one issue.** Each story is its own sub-issue with `parentId` set.</mark>

**Legacy milestone path**: if the user explicitly wants a date-bound milestone instead of a parent-issue epic (e.g. "ship by Q2", "before launch"), use `save_milestone` and link stories via `milestone`. This stays available for date/scope-bound tracking but is no longer the default — parent-issue epics carry the narrative; milestones are time markers.

### 5. Research (only with `--research`)

- Search the codebase for 2–5 relevant files using Grep/Glob — summarise patterns or constraints, avoid exhaustive repository analysis
- Check Linear for similar issues via `list_issues` (broader search than step 3)
- Read relevant project documentation if necessary (see [reference/project-docs.md](reference/project-docs.md) for standard paths)
- Fetch available labels via `list_issue_labels` for the resolved team
- Summarise findings for use in the draft

### 6. Test consideration

Assess whether tests make sense for this change. Not every issue needs them — pure documentation, config changes, or exploratory spikes typically don't.

If tests do make sense, note in the issue that **tests should be written first, then the implementation to match**. Claude writes both at once so it's not strict TDD, but having tests in place makes sure future changes don't break the tool.

Add a `### How to test it` section to the draft when applicable:

```markdown
### How to test it
Write tests first. [Brief description of what to test — expected
behaviour, edge cases, error conditions.]
```

Omit the section entirely when tests don't apply.

### 7. Draft the issue

**Quick mode (story-sized)** — use the full issue structure from [ISSUE-TEMPLATE.md](reference/ISSUE-TEMPLATE.md) (Title, Description with Why this matters, Where things stand, What we'll do, What we won't do, Expected outcome, How to test it, Assumptions to confirm).

**Quick mode (epic-sized parent issue)** — use [EPIC-TEMPLATE.md](reference/EPIC-TEMPLATE.md) instead (Title with `Epic: ` prefix, Description with Why this matters, Goal, Phases, Decision, Out of scope). Sub-issue drafts under the parent still use ISSUE-TEMPLATE.md — they're stories that happen to have a parent.

**Research mode** — also include the research mode additions from [ISSUE-TEMPLATE.md](reference/ISSUE-TEMPLATE.md) (Implementation notes, Code examples, Related code, Related issues). Research mode applies to story drafts; epic parent-issue drafts stay strategic and don't accumulate research-mode sections — the implementation detail belongs on the sub-issues.

**Ground the draft in the Vision** loaded at step 1. The "Why this matters" section must explicitly reference which Vision outcome the issue serves — quote the relevant Success criteria line or constraint, and explain how this work moves toward it. If the user's description doesn't trace cleanly to any Vision outcome:

> "I can't trace this work back to a Vision outcome. The Vision says: [list relevant outcomes]. Two paths:
>
> 1. **Add a new criterion to `VISION.md`** — re-run `/vision` to evolve the Vision, then come back. Repeated trace-back failures are a signal the Vision needs updating.
> 2. **Drop the issue as out of scope** — the work doesn't belong in this project right now.
>
> Which one?"

Don't draft past the user's answer. The Vision is the project's stated purpose; an issue that doesn't serve it is either out of scope or a sign the Vision needs updating.

Apply the priority, labels, and scope guidance from the decision rules above.

### 8. Cross-model feedback loop (optional)

After drafting the issue:

1. **Claude presents the draft** with its own assessment — what's strong, what could be better, any concerns about scope or feasibility
2. Ask: **"Want to send this to ChatGPT for feedback before creating?"**

If **yes**, run the three-voice feedback loop (Claude → ChatGPT → Claude → User):

**Round N:**

1. **Send to ChatGPT** — send the current draft (including Claude's assessment) to ChatGPT:

```bash
uv run .claude/tools/openrouter-chat.py "<full draft text + Claude assessment>" -m openai/gpt-5.4-pro -s "You are reviewing a Linear issue draft and a first review from Claude. Give specific, actionable feedback on why this matters, where things stand, what we'll do, and expected outcome. Point out gaps, assumptions, or scope creep. Agree or disagree with the first review. Be direct."
```

2. **Show ChatGPT's feedback** — display the full ChatGPT response as text output so the user can read it. Do not summarise or collapse it — the user needs to see the raw feedback before Claude responds. Use a heading like "**ChatGPT's feedback (round N):**" followed by the complete response text.

3. **Claude responds** — after the user has seen ChatGPT's feedback, review it against the draft. Incorporate points that strengthen the issue, push back on points that don't fit or expand scope unnecessarily. Explain your reasoning for each decision. Present the updated draft.

4. **User decides** — ask: **"Send to ChatGPT again or save the issue on Linear?"**
   - If **again** — repeat from step 1 with the revised draft
   - If **save** — continue to step 9

Each round has three voices: Claude proposes and synthesises, ChatGPT challenges, the user steers. The loop sharpens the issue through cross-model perspectives — like a design review but for issue planning.

### 9. Present for approval

Show the full draft to the user. Ask for explicit approval before creating.

- If the user requests changes, revise and re-present
- If the user declines, stop — do not create the issue

### 10. Create the issue

Only after explicit approval:

First, resolve the Backlog status ID — call `list_issue_statuses` for the team and find the status with `name: "Backlog"` (not "Backburner" or other backlog-type statuses). Use the ID, not the name, when creating the issue.

```
save_issue with:
  - team: resolved team
  - project: resolved project
  - state: <Backlog status ID from list_issue_statuses>
  - title, description, priority, and labels from the draft
```

Do not assign the issue unless the user explicitly requested it.

### 11. Confirm creation

Display:
- Linear issue identifier (e.g., PG-184)
- URL to the issue
- Branch name from Linear's `gitBranchName` field

### 12. Set up worktree (only with `--worktree`)

Skip if `--worktree` was not passed in step 2. Otherwise, set up an isolated worktree for the new issue.

Resolve the worktree path from the repo name and issue ID:

```
../<repo-dirname>-<issue-id-lowercase>
```

For example, if the repo is `lander` and the issue is `PG-210`, the worktree path is `../lander-pg-210`.

Create the worktree using the branch name from Linear's `gitBranchName`:

```bash
git worktree add ../<repo-dirname>-<issue-id-lowercase> -b <gitBranchName>
```

Open VS Code in the worktree:

```bash
code <worktree-path>
```

If `code` is not found, warn the user:

```
⚠ `code` command not found. VS Code must be open in the worktree for the workflow to work.

Fix: open VS Code, press Cmd+Shift+P, run "Shell Command: Install 'code' command in PATH".

For VS Code Insiders, add to ~/.bash_profile or ~/.zprofile:
export PATH="$PATH:/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin"
```

Then display the worktree summary and end the command — the user continues in a new Claude Code session:

```
The worktree is ready:

- Path: <absolute-worktree-path>
- Branch: <branch-name>
- Linear: <issue-id> — <status>

Open a Claude Code session there with:

cd <absolute-worktree-path>
claude

Then run /linear:start <issue-id> — it will pick up the branch and continue from the Vision check onwards.
```

## Error handling

- If `$ARGUMENTS` is empty or missing a description, ask the user for one
- If issue creation fails, show the error and stop

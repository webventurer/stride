# Plan work and create a Linear issue (optional --research mode)

Accepts a description and optional flags: `/plan-work --research --craft "add error handling to API calls"`

## Modes

- **Quick mode** (default): `/plan-work "description"` — draft, review, create
- **Research mode**: `/plan-work --research "description"` — explore codebase and Linear first, then draft with richer context

## Flags

- `--research` — explore codebase and Linear before drafting (adds implementation notes, code examples, related code and issues)
- `--craft` — auto-run CRAFT prompt refinement without asking (skips the interactive prompt in step 4)

## Decision rules

- **Vision is the anchor**: every issue must trace back to a Vision outcome. The draft's "Why this matters" section must reference which Vision outcome the issue serves. If it can't, ask the user to choose: **add a new criterion to `VISION.md` (re-run `/vision` to evolve it), or drop the issue as out of scope**. Don't draft past this prompt — repeated trace-back failures are a signal the Vision needs updating, not that the gate should be loosened. Without `VISION.md` at the repo root, the command stops and suggests `/vision` (see step 1).
- **Sizing first**: before drafting, determine whether the description is story-sized (one deliverable, ships as one PR) or epic-sized (a named initiative with multiple stories). Epic-sized work becomes a Milestone; story-sized work becomes an Issue linked to a Milestone if one exists.
- One issue = one deliverable. If the description contains "and" connecting unrelated outcomes, split.
- Default to the smallest issue that moves something forward. If the user's description is broad, propose a focused first issue plus follow-ups.
- **When proposing multiple follow-ups, order them by Vision alignment** — see [reference/align-to-vision.md](reference/align-to-vision.md). The follow-up advancing the least-progressed Success Criterion sits first.
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

- **If present**: read the full file and load it as context for the rest of the flow. The Success Criteria section in particular tells you what outcomes the project is committed to — the draft's "Why this matters" should connect the proposed work to one of them.

<mark>**This is a hard gate, not a warning.**</mark> Stop-and-suggest, don't draft-with-warning. Vision-less drafting produces issues that look fine in isolation but accumulate as drift.

### 2. Parse arguments

Extract the description and flags from `$ARGUMENTS`. Determine if `--research` and/or `--craft` are present.

### 2b. Sizing gate

Ask the user: **"Is this story-sized (one deliverable, ships as one PR) or epic-sized (a named initiative with multiple stories)?"**

**If story-sized** — continue to step 3 as normal. At step 10 (create issue), also call `list_milestones` for the project: if any milestones exist, ask "Link this story to an existing epic?" and if yes, set the `milestone` field on `save_issue`.

**If epic-sized** — follow the epic path:

1. Call `list_milestones` for the project and show any existing milestones
2. Ask: "Create a new epic (milestone), or link the stories to an existing one?"
3. If creating: ask for a name and one-line description, then call `save_milestone` with `name`, `description`, and `project`
4. Confirm the milestone with the user before proceeding
5. Ask: "What are the first 1–3 stories for this epic?" — each answer becomes a separate issue draft
6. For each story: run the full flow from step 3 onwards (duplicate check, CRAFT if requested, draft, approval, create) with `milestone` set to the new or chosen milestone
7. After all stories are created, summarise: list the milestone and all created issues

<mark>**Do not bundle all stories into one issue.** Each story is its own issue linked to the milestone.</mark>

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

- If **yes** (or `--craft`): read [reference/ISSUE-TEMPLATE.md](reference/ISSUE-TEMPLATE.md), substitute `[user's description]` with what the user provided **and** `[VISION]` with the full contents of the `VISION.md` loaded in step 1, run `/craft` with the populated prompt, then use the refined output as the description for all subsequent steps. Substituting the entire Vision into the prompt is what lets the agent — or any model the prompt is sent to — anchor the draft on real criteria, real constraints, and real non-goals rather than guessing.
- If **no**: continue with the original description

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

**Quick mode** — use the full issue structure from [ISSUE-TEMPLATE.md](reference/ISSUE-TEMPLATE.md) (Title, Description with Why this matters, Where things stand, What we'll do, What we won't do, Expected outcome, How to test it, Assumptions to confirm).

**Research mode** — also include the research mode additions from [ISSUE-TEMPLATE.md](reference/ISSUE-TEMPLATE.md) (Implementation notes, Code examples, Related code, Related issues).

**Ground the draft in the Vision** loaded at step 1. The "Why this matters" section must explicitly reference which Vision outcome the issue serves — quote the relevant Success Criteria line or constraint, and explain how this work moves toward it. If the user's description doesn't trace cleanly to any Vision outcome:

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

## Error handling

- If `$ARGUMENTS` is empty or missing a description, ask the user for one
- If issue creation fails, show the error and stop

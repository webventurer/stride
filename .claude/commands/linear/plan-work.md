---
description: Draft a Linear story, epic, or bug anchored to a Vision outcome, before any code.
---

# Plan work and create a Linear issue

Accepts a description and optional flags: `/plan-work --research --craft --epic --bug --project <name> "add error handling to API calls"`. With `--epic`, it skips size-sensing and goes straight to the parent-issue flow. With `--bug`, it skips shape-sensing and drafts straight to the bug template. With `--project`, it files the issue against a different Linear project and skips the Vision check (for quick adds when the target repo isn't cloned locally).

Read [unattended mode](reference/unattended.md) after resolving `.stride.json`.
Unattended mode skips optional refinement and approval prompts, but never drafts
past duplicate, scope, project, or Vision ambiguity.

## Modes

- **Quick mode** (default): `/plan-work "description"` — check the code, draft, create
- **Research mode**: `/plan-work --research "description"` — also explore Linear and the project's documents, then draft with richer context

## Flags

- `--research` — go beyond the code check every run makes, exploring Linear and the project's documents before drafting (adds implementation notes, code examples, related code and issues)
- `--craft` — auto-run CRAFT prompt refinement without asking (skips the interactive prompt in step 4)
- `--epic` — skip size-sensing and go straight to the epic-sized parent-issue flow (see step 5). Pass this when you already know the description is a named initiative with multiple stories.
- `--bug` — skip shape-sensing and draft straight to the bug template (see step 6). Pass this when you already know the description is a bug report (symptoms + repro + gap), not a feature request.
- `--project <name>` — file the issue against the named Linear project instead of the current repo's `.stride.json`. Skips the Vision check entirely (the current repo's Vision doesn't apply to another project's work). Use this for quick cross-project adds when the target project's repo isn't cloned locally. The target project must exist in Linear; mistyped names fail fast at step 0.

## Decision rules

### Anchoring

- **Vision is the anchor** (within-project mode): every issue must trace back to a Vision outcome. The draft's "Why this matters" section must reference which Vision outcome the issue serves. If it can't, ask the user to choose: **grow the Vision, or drop the issue as out of scope**. Growing the Vision is [`/vision-evolve`](../../skills/vision-evolve/SKILL.md)'s job. Before either path, see [*revise, don't stretch*](https://github.com/webventurer/stride/blob/main/docs/patterns/revise-dont-stretch.md) — a strained trace is itself a signal that often resolves with a revision rather than a Vision evolution. Don't draft past this prompt. Without `VISION.md` at the repo root, the command stops and suggests `/vision` (see step 1). **Cross-project mode** (`--project` flag) skips this rule entirely — the current repo's Vision doesn't apply to another project's work; full Vision anchoring happens later when the target project's `/linear:start` picks up the issue.
- One issue = one deliverable. If the description contains "and" connecting unrelated outcomes, split. When new work surfaces during an in-flight issue, see [*new issue, not new scope*](https://github.com/webventurer/stride/blob/main/docs/patterns/new-issue-not-new-scope.md) — file the new work separately rather than expanding the current issue's scope.
- Default to the smallest issue that moves something forward. If the user's description is broad, propose a focused first issue plus follow-ups.
- **When proposing multiple follow-ups, order them by Vision alignment** — see [reference/align-to-vision.md](reference/align-to-vision.md). The follow-up advancing the least-progressed Success criterion sits first.

### Defaults & modes

- **Story is the default; epic when warranted**: most descriptions are story-sized (one deliverable, ships as one PR), and stride defaults to that without asking. Epic-sized work (a named initiative with multiple stories) is reached two ways — the `--epic` flag, or size-sensing surfacing a soft prompt when epic-shape signals fire (see step 5). Epic-sized work becomes a parent issue with sub-issues for each story; story-sized work becomes an issue, optionally linked to an existing epic via `parentId`.
- **Epic title prefix**: epic-sized parent issues use `Epic: <stakeholder outcome>` as their title — the prefix makes the scope visible at a glance on the kanban board, and the post-colon part still follows the stakeholder-outcome rule. Example: `Epic: Bulk/Batch Blog Processing (parallel article pipeline)`.
- **Feature is the default; bug when warranted**: most descriptions are feature-shaped (*"add / build / ship X"*) and use the story template — that's the default without asking. Bug-shaped work (*"X is broken / fails / silently no-ops"*) is reached two ways — the `--bug` flag, or shape-sensing surfacing a soft prompt when bug-shape signals fire (see step 6). Bug-shaped work uses [bug.md](reference/templates/bug.md) — symptoms / repro / expected vs actual / suspected causes as first-class sections, instead of burying diagnosis under *"Where things stand"*. Shape and size are independent: a feature can be story- or epic-sized, and so can a bug.

### Drafting style

- Titles are imperative and start with a verb (Add, Fix, Replace, Remove…). Avoid "Investigate" unless the outcome genuinely is a report, not a code change.
- Titles describe the outcome a stakeholder would recognise — what changes from their perspective — not the implementation. *"Background jobs run reliably after the first one"*, not *"Reset Tortoise globals between RQ jobs"*. Infrastructure exception: when there's no user-visible outcome, name the *system behaviour* that changes (e.g. "Linter accepts 100-char lines"), not the file that changes. See `docs/reference/issue-template.md` for the canonical rule and examples.
- Card bodies describe the behaviour the user or caller sees, not the internal mechanism — see [Linear card language](reference/card-language.md#explain-the-solution-before-the-implementation). Implementation detail appears only where a constraint forces it.
- Titles use plain language — no bare jargon or stride-internal vocabulary. The [`/clear-speak` skill](../../skills/clear-speak/SKILL.md) is stride's canonical standard for what counts as jargon and how to replace it.
- Labels are optional — suggest at most 3, only when clearly relevant. Prefer no labels over speculative ones.
- Priority defaults to Medium. Only upgrade if the user says it's urgent or the description implies user-facing impact (breakage, a time-sensitive launch, etc.).
- The code check and research mode exist to improve the draft, not to produce an audit. Cap file exploration at 2–5 relevant files per card; summarise patterns, don't catalogue the repo.

### Process

- Duplicate handling is two-tier: exact/near-exact → interactive mode warns and asks; unattended mode stops. Similar/related → mention briefly and continue.
- A story or bug card is created as soon as every check passes, without showing the draft. When something only the user can decide is open, interactive mode shows the draft and asks for approval before creating, and unattended mode stops at its hard stops. The epic-sized path keeps its draft and approval.
- Never assign the issue unless the user explicitly asks.

## Steps

### 0. Resolve project

First, check `$ARGUMENTS` for the `--project <name>` flag.

- **If `--project <name>` is present** (cross-project mode): use the flag's value as the project name. **Mark the run as cross-project mode** — step 1 (Vision check) is skipped and step 9 swaps the Vision-grounding requirement for a cross-project note.
- **Otherwise** (within-project mode), check for a `.stride.json` file in the repository root.
  - If **found**: read the project name from it (`project` field in JSON).
  - If **not found**: list available projects *(auth per [reference/workflow.md](reference/workflow.md))* and ask the user to choose. Then ask which `LINEAR_*_API_KEY` env var in `~/.env` authenticates that workspace. Save all five fields as `.stride.json`:

    ```json
    {
      "project": "<chosen-project-name>",
      "api_key_env": "LINEAR_<WORKSPACE>_API_KEY",
      "focus": "outcome",
      "unattended": false,
      "parallel-sessions": 3
    }
    ```

    Then check the repo's `.gitignore` — if `.stride.json` isn't listed, append it. The `api_key_env` field lets `linear_cli.py` read the bearer token without a per-call `LINEAR_API_KEY=` wrap. The `focus` field sets the default output abstraction for the `/linear:*` commands — `"outcome"` is the default; see [reference/output-focus.md](reference/output-focus.md) for the accepted values. The `unattended` field defaults to `false`; see [reference/unattended.md](reference/unattended.md). The `parallel-sessions` field defaults to `3`: the most cards stride runs at once; see [recovery/backfill-parallel-sessions-field.md](recovery/backfill-parallel-sessions-field.md).

    ```bash
    uv run .claude/tools/linear_cli.py project list
    ```

    Then set the chosen project's board to Manual ordering, so stride's `sortOrder` pins show from the first card (the call is idempotent):

    ```bash
    uv run .claude/tools/linear_cli.py project get "<chosen-project-name>"
    uv run .claude/tools/linear_cli.py set-project-view-manual <project-id>
    ```

**Resolve the project name** (both modes). `linear_cli.py issue create --project "<name>"` resolves the name internally on `uv run .claude/tools/linear_cli.py issue create --project "<name>"` — no UUID lookup needed. Run `uv run .claude/tools/linear_cli.py project get "<name>"` once to confirm the name resolves and capture the project UUID for any later `linear_cli.py` calls (`list-milestones`, `min-backlog-sort-order`, `create-milestone` all take it).

- **Zero matches**: stop and tell the user the name doesn't resolve. Ask them to verify the spelling. Do not proceed to drafting on a typo.
- **One match**: store the name. Use it as the `--project "<name>"` argument on every `uv run .claude/tools/linear_cli.py issue create` call (step 12 and any nested calls in step 5's epic-sized path).
- **Multiple matches**: show the candidates and ask the user to disambiguate.

### 1. Vision check

**Skip this step entirely if cross-project mode is active** (the `--project` flag was passed in step 0). Surface a one-line note and continue to step 2:

> *"Cross-project mode: filing into <project name>. Vision check skipped. Run `/linear:plan-work` from inside <project name>'s repo for full Vision-anchored planning."*

Otherwise (within-project mode), run the Vision check below.

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

Extract the description and flags from `$ARGUMENTS`. Determine if `--research`, `--craft`, `--epic`, and/or `--bug` are present. (`--project` is parsed earlier in step 0 because project resolution and the Vision-check skip both depend on it.)

If `--worktree` is passed, it's no longer valid here — error and stop: *"`--worktree` is now part of `/linear:start`. File the issue first, then `/linear:start <id> --worktree` from the new session."*

### 3. Duplicate check (all modes)

Search Linear for potentially related issues:

```
uv run .claude/tools/linear_cli.py search-by-project --project "<project>" --text "<key terms>"
```

Handle results in two tiers:

- **Exact or near-exact duplicates** (same problem, same scope): show them and
  stop in unattended mode. Interactive mode warns strongly and asks whether to
  proceed.
- **Similar or related issues** (overlapping area but different scope/angle): show briefly, continue drafting, and reference them in the draft's "Related issues" section.

### 4. CRAFT prompt refinement (all modes)

<mark>**When `--craft` is present, always run CRAFT before research. Never skip this step.**</mark> The user passes `--craft` to sharpen their description into a clearer prompt — skipping it means research works from a vaguer input than intended.

If `--craft` flag is present, run CRAFT automatically. Without the flag,
unattended mode skips CRAFT and interactive mode asks: "Would you like me to
run `/craft` on your description first to sharpen the issue before drafting?"

- If **yes** (or `--craft`): read [reference/templates/story.md](reference/templates/story.md) for story-sized work, or [reference/templates/epic.md](reference/templates/epic.md) when drafting the parent issue on the epic-sized path. Substitute `[user's description]` with what the user provided **and** `[VISION]` with the full contents of the `VISION.md` loaded in step 1, run `/craft` with the populated prompt, then use the refined output as the description for all subsequent steps. Substituting the entire Vision into the prompt is what lets the agent — or any model the prompt is sent to — anchor the draft on real criteria, real constraints, and real non-goals rather than guessing.
- If **no**: continue with the original description

### 5. Size — story by default, epic when warranted

Story is the default. Most descriptions are story-sized — one deliverable that ships as one PR — and asking every invocation imposes epic-shaped overhead on the common case. Skip this step and continue to step 7 unless one of the following triggers fires.

**Trigger 1 — `--epic` flag.** If `--epic` was parsed in step 2, skip size-sensing entirely and follow the **epic-sized path** below.

**Trigger 2 — size-sensing detects epic shape.** Read the description (the `--craft`-refined version from step 4 if `--craft` was used; otherwise the raw input). Look for **epic-shape signals**:

- Multiple `and`-joined outcomes that don't share a single purpose
- References to *"phases"*, *"stages"*, *"milestones"*, *"Q2"*, *"by launch"*, *"rollout"*, etc.
- A description that resists a single stakeholder-readable PR title without joining unrelated ideas with `and`
- Length and structure that suggest a roadmap rather than a deliverable (5+ paragraphs of *"first we'll, then we'll, then we'll"*)

If any signals fire, surface a **soft prompt** — not a forced gate:

In unattended mode, stop and name the signals. Ask the user to re-run with
`--epic` or a narrower story description; scope shape is not safe to guess.

> *"This sounds epic-sized — I'm seeing [name the signals: multiple phases / unrelated outcomes / a rollout shape]. Want to break it into stories under an epic, narrow this to one story-sized deliverable, or proceed as one story?"*

Three paths:

- **Break into epic** → follow the **epic-sized path** below.
- **Narrow to story** → ask which slice to file as the first story; defer the rest. Continue to step 7 with the narrowed description as story-sized.
- **No, it's one story** → continue to step 7 as story-sized.

If no signals fire, skip silently and continue to step 7 as story-sized. The common path stays frictionless.

<mark>**Size-sensing offers, doesn't force.**</mark> When signals are detected, the agent asks; the user always has final say. Auto-flipping silently would be a worse failure mode than the old forced ask.

**Story-sized path** (default / "no, it's one story" / "narrow to story") — continue to step 7 as normal. At step 12 (create issue), also search for parent-issue epics in the project (`uv run .claude/tools/linear_cli.py search-by-project --project "<project>" --text "Epic: "`): if any exist, ask "Link this story to an existing epic?" and if yes, set the parent after creation via `uv run .claude/tools/linear_cli.py issue update <new-id> --parent <epic-id>`. Legacy milestones — boards may still have them from before stride moved to parent-issue epics; if `uv run .claude/tools/linear_cli.py list-milestones <project-UUID>` returns any, offer them as a secondary option and use the `--project-milestone "<name>"` flag on `uv run .claude/tools/linear_cli.py issue create` instead.

In unattended mode, create the story without a parent or legacy milestone.
Linkage requires an explicit ID or a later deliberate update; never infer it
from a fuzzy search result.

**Epic-sized path** (`--epic` / "break into epic") — follow [reference/epic-flow.md](reference/epic-flow.md): search for or create a parent issue, draft 1–3 sub-issues with `parentId` set, and position them on the backlog. <mark>Don't bundle all stories into one issue</mark> — each is its own sub-issue. (That reference also covers the legacy date-bound *milestone* alternative.)

### 6. Shape — feature by default, bug when warranted

Feature is the default. Most descriptions are feature-shaped — *"add / build / ship / replace X"* — and asking every invocation imposes bug-shaped overhead on the common case. Skip this step and continue to step 7 unless one of the following triggers fires.

**Trigger 1 — `--bug` flag.** If `--bug` was parsed in step 2, skip shape-sensing entirely and mark the draft as bug-shaped — step 9 will route to [bug.md](reference/templates/bug.md).

**Trigger 2 — shape-sensing detects bug shape.** Read the description (the `--craft`-refined version from step 4 if `--craft` was used; otherwise the raw input). Look for **bug-shape signals**:

- Failure-mode keywords: *broken, fails, silently, no-op, regression, throws, crashes, errors out, doesn't work, stuck*
- Verb is *fix*, not *add / build / ship / replace*
- The description names a symptom and a missing behaviour, not a desired capability

If any signals fire, surface a **soft prompt** — not a forced gate:

In unattended mode, stop and name the signals. Ask the user to re-run with
`--bug` or confirm a feature description; issue shape is not safe to guess.

> *"This sounds bug-shaped — I'm seeing [name the signals: e.g. 'silently' / 'fails to' / verb is 'fix']. Use the bug template (symptoms / repro / expected vs actual / suspected causes), or treat as a feature?"*

Two paths:

- **Use bug template** → mark the draft as bug-shaped; step 9 routes to bug.md.
- **Treat as feature** → continue to step 7 with the description treated as feature-shaped.

If no signals fire, skip silently and continue to step 7 — feature-shaped is the default.

<mark>**Shape-sensing offers, doesn't force.**</mark> Same pattern as size-sensing — the agent asks when signals fire; the user always has final say. Auto-flipping silently would be a worse failure mode than the old forced ask.

**Shape and size are independent.** A feature can be story- or epic-sized, and so can a bug. When both the epic-sized path (step 5) and bug-shaped marker are active, the parent issue uses epic.md and sub-issues use bug.md. No `epic-bug` template exists — bug at epic scale is rare enough that the two-template composition handles it.

### 7. Check the code (all modes)

<mark>**A card's account of the problem and its proposed fix are guesses until they are read against the code.**</mark> Find the 2–5 files the card would touch using Grep/Glob, and read them. In cross-project mode, read them in the target project's repo when it is on this machine. On the epic-sized path, check each story rather than the parent.

Before drafting, confirm:

- **The account is true:** what the card will say about how things stand today matches the code
- **The fix can work:** what the card will promise is possible given how the code behaves, and the code doesn't already have something that does the job
- **The evidence says what the card says:** when the description cites a specific run, recording or results file, open that data too

When the check contradicts the description, correct the draft and tell the user what changed. When the requested fix can't work, interactive mode asks how to proceed, and unattended mode stops and names the file that rules it out. When the code can't be reached, or the check leaves a point open, say so under *Assumptions to confirm*; step 11 treats that point as open for a story. A bug draft's *Suspected causes* are guesses by design and are not open.

**With `--research`**, also:

- Check Linear for similar issues via `uv run .claude/tools/linear_cli.py search-by-project --project "<project>" --text "<keywords>"` (broader search than step 3)
- Read relevant project documentation if necessary (see [reference/project-docs.md](reference/project-docs.md) for standard paths)
- Fetch available labels via `uv run .claude/tools/linear_cli.py label list` (workspace-scoped)
- Summarise patterns, constraints and findings for use in the draft

#### Will it move the needle?

Every card is a claim on the attention of the person running stride, so a card is drafted only when there is evidence it will matter. Read [moves the needle](reference/moves-the-needle.md), then answer three questions from what the code check and any recording or results file showed: how often has this happened, what does it cost, and what happens if nothing is done? The check also runs in cross-project mode, and on the epic-sized path it runs for the parent epic and for each story.

- **When the case is made:** continue to step 8. The answers go in the draft's "Why this matters" (step 9).
- **When the case is thin:** say so, with the reason, and recommend not filing. In interactive mode the person can overrule the recommendation, and the draft then records that they did. In unattended mode, file nothing and report the reason.
- **An explicit request is the case:** when the person's own words ask for this specific piece of work, that counts as the case, and the draft records that they asked. A follow-up an agent found while doing other work is not an explicit request, even when the person told the agent to file follow-ups.
- **Several follow-ups in one run** (a focused first issue plus its follow-ups, or an epic's stories): judge each one. File the ones that make the case and print one line above step 13's receipt that names each one left out, with its reason. Follow-ups filed by separate runs are each judged by their own run.

### 8. Test consideration

Assess whether tests make sense for this change. Not every issue needs them — pure documentation, config changes, or exploratory spikes typically don't.

If tests do make sense, note in the issue that **tests should be written first, then the implementation to match**. Claude writes both at once so it's not strict TDD, but having tests in place makes sure future changes don't break the tool.

Add a `### How to test it` section to the draft when applicable:

```markdown
### How to test it
Write tests first. [Brief description of what to test — expected
behaviour, edge cases, error conditions.]
```

Omit the section entirely when tests don't apply.

### 9. Draft the issue

Before drafting a card title or description in this step, read [Linear card
language](reference/card-language.md). It applies to story, bug, epic, and
sub-issue drafts.

<mark>**Read the linked template before drafting** — its sections are the source of truth, not this step's summary. Don't draft from memory or from the prose around the link; open the file and follow it.</mark>

**Story drafts** (feature-shaped, story-sized — the default path) — use the full issue structure from [story.md](reference/templates/story.md). With `--research`, also append the research-mode additions described in that template.

**Bug drafts** (bug-shaped, story-sized — `--bug` flag or the bug-shape branch of step 6) — use [bug.md](reference/templates/bug.md) instead. Symptoms / repro / expected vs actual / suspected causes are first-class sections, in place of *"Where things stand"* and *"What we'll do"*. With `--research`, append the research-mode additions described in that template.

**Epic parent-issue drafts** — use [epic.md](reference/templates/epic.md) instead. Sub-issues under the parent default to story.md — they're stories that happen to have a parent. When the epic is also bug-shaped (`--epic --bug`), sub-issues use bug.md instead. Research mode never applies to the epic itself; that detail belongs on each sub-issue.

**Ground the draft in the Vision** loaded at step 1 — *within-project mode only*. The "Why this matters" section must explicitly reference which Vision outcome the issue serves — quote the relevant Success criteria line or constraint, and explain how this work moves toward it. If the user's description doesn't trace cleanly to any Vision outcome:

> "I can't trace this work back to a Vision outcome. The Vision says: [list relevant outcomes]. Two paths:
>
> 1. **Grow the Vision** — I'll tend it with [`/vision-evolve`](../../skills/vision-evolve/SKILL.md), then draft the issue against the changed Vision.
> 2. **Drop the issue as out of scope** — the work doesn't belong in this project right now.
>
> Which one?"

Don't draft past the user's answer. The Vision is the project's stated purpose; an issue that doesn't serve it is either out of scope or a sign the Vision needs updating.

**Cross-project mode** (`--project` flag was passed): the current repo's Vision doesn't apply. Replace the *"Why this matters → Vision criterion"* requirement with a single line:

> *"Cross-project draft — Vision anchoring deferred. Re-anchor via `/linear:start` from within the target project's repo when the work is picked up."*

**State the case for filing** in "Why this matters", in both modes, in plain words: how often it happened, what it costs, and what happens if nothing is done, from the check in step 7. In cross-project mode they sit beside the cross-project line.

Everything else in the draft (sizing, *Where things stand*, *What we'll do*, *What we won't do*, *Expected outcome*, *How to test it*, *Assumptions to confirm*) is filled as normal from the user's description, optionally CRAFT-sharpened, and from step 7's check of the code.

Apply the priority, labels, and scope guidance from the decision rules above.

### 10. Cross-model feedback loop (optional)

Skip this step in both modes unless the user explicitly requested
cross-model feedback in the same invocation.

After drafting the issue, **Claude presents the draft** with its own assessment — what's strong, what could be better, any concerns about scope or feasibility. Then run the three-voice feedback loop (Claude → ChatGPT → Claude → User):

**Round N:**

1. **Send to ChatGPT** — send the current draft (including Claude's assessment) to ChatGPT. The helper's default reviewer model is OpenRouter's `~openai/gpt-latest` alias, which auto-refreshes server-side as OpenAI ships new top-tier models. Override with `-m <other-model>` only when a different reviewer voice is wanted.

```bash
uv run .claude/tools/openrouter_cli.py "<full draft text + Claude assessment>" -s "You are reviewing a Linear issue draft and a first review from Claude. Give specific, actionable feedback on why this matters, where things stand, what we'll do, and expected outcome. Point out gaps, assumptions, or scope creep. Agree or disagree with the first review. Be direct."
```

2. **Show ChatGPT's feedback** — display the full ChatGPT response as text output so the user can read it. Do not summarise or collapse it — the user needs to see the raw feedback before Claude responds. Use a heading like "**ChatGPT's feedback (round N):**" followed by the complete response text.

3. **Claude responds** — after the user has seen ChatGPT's feedback, review it against the draft. Incorporate points that strengthen the issue, push back on points that don't fit or expand scope unnecessarily. Explain your reasoning for each decision. Present the updated draft.

4. **User decides** — ask: **"Send to ChatGPT again or save the issue on Linear?"**
   - If **again** — repeat from step 1 with the revised draft
   - If **save** — on the epic-sized path, continue to step 11 for its approval. On the story and bug path the user has seen the draft, so saving counts as the approval; continue to step 12

Each round has three voices: Claude proposes and synthesises, ChatGPT challenges, the user steers. The loop sharpens the issue through cross-model perspectives — like a design review but for issue planning.

### 11. Show the draft only when something is open

On the epic-sized path, show the full draft and ask for explicit approval before creating, as the [epic flow](reference/epic-flow.md) sets out. In unattended mode, show it for the record and continue directly to step 12.

On the story and bug path, the draft is not shown. Something is **open** when only the user can decide it:

- a near-duplicate, a Vision ambiguity, or an epic-shaped or bug-shaped description that step 5 or 6 raised as a question (an explicit `--epic` or `--bug` flag skips that question, so it isn't open) (steps 1, 3, 5, 6, 9)
- a case that doesn't move the needle (step 7)
- a requested fix the code check rules out (step 7)
- a project name that doesn't match exactly one project, which step 0 stops on before any draft exists, so it asks about the name rather than showing a draft
- a point the code check or the Vision trace could not settle, which a story draft would file under *Assumptions to confirm* (an entry that only restates a known default doesn't count)

When nothing is open, continue directly to step 12 in both modes. The config setting is the persistent approval for routine issue creation; duplicate, scope, project, and Vision ambiguity remain hard stops in unattended mode, and a point the code check could not settle goes into the card's *Assumptions to confirm*.

When something is open in interactive mode, show the full draft to the user and ask for explicit approval before creating.

<mark>**Present the draft as the final text output of the turn, and ask for approval in plain prose.**</mark> Never pair the draft with a tool-based approval dialog in the same turn — the dialog can suppress the text above it, and the user ends up approving a card they never saw. End the turn on the draft + prose question; the user's reply is the gate.

- If the user requests changes, revise and re-present
- If the user declines, stop — do not create the issue

### 12. Create the issue

Only after every check passes with nothing open, after interactive approval, on the epic-sized path after its approval, or in unattended mode after every hard check passes.
Write the drafted description to a file first and pass it with `--description
@<file>` — the body is multi-line markdown, so it goes through a file, never an
inline string ([why](reference/workflow.md#how-skills-talk-to-linear)).
`linear_cli.py` accepts state names directly — no separate ID lookup — and
accepts the project's name on `--project`:

**Type label.** Every stride card carries exactly one type label ([`linear_labels.json`](linear_labels.json)) so its shape shows on the board: `Bug` for a bug-shaped draft (the bug-shape branch of step 6), `Story` for a standard story. The label is always first in `--labels`; any optional suggested labels follow it.

```bash
uv run .claude/tools/linear_cli.py issue create \
  -t <TEAM-KEY> \
  --project "<project-name from .stride.json>" \
  --state Backlog \
  --title "<from draft>" \
  --description @<draft-file> \
  --priority <0–4> \
  --labels "<Bug|Issue>[,suggested,labels]" \
 
```

Capture the issue identifier (e.g. `PG-184`) from the JSON output. If the draft is a sub-issue of an existing epic, follow up with `uv run .claude/tools/linear_cli.py issue update <new-id> --parent <epic-id>`. If sortOrder positioning is required, follow the ordering recipe in [reference/epic-flow.md](reference/epic-flow.md) (step 7).

Do not assign the issue unless the user explicitly requested it.

### 13. Confirm creation

Never print the draft. On the epic-sized path, display the identifier, URL and branch name after the summary in [epic flow](reference/epic-flow.md), as before; the rest of this step is for story and bug cards. First print only the lines other steps require, when they apply: what the code check corrected in the description (step 7), similar issues found (step 3), the cross-project note (step 1), and the one line naming each follow-up left out (step 7).

Then end the run with the receipt as one line:

```
PG-184 Add a video section — <issue URL> — branch <gitBranchName from Linear>
```

## Error handling

- If `$ARGUMENTS` is empty or missing a description, ask the user for one
- If issue creation fails, show the error and stop

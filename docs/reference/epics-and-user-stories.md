# Epics and stories

Stride breaks work into three layers — **epic, story, task** — and maps them onto Linear's primitives. This page is the reference for what each layer is, where it lives, and how the `/linear` commands use them.

Above all three sits **Vision** — `VISION.md` at the repo root, written via [/vision](/skills/vision). Epics and stories carve up the work; the Vision is what they're carving up *toward*. When `/linear:plan-work` asks whether a description is epic-sized or story-sized, the answer should trace back to a Vision outcome.

## The mapping

| Layer | Linear primitive | Where it lives |
|:------|:-----------------|:---------------|
| **Product** | Project | `Stride >>>` — the whole-product container |
| **Epic** (named initiative) | **Parent issue** with sub-issues | Created by `/linear:plan-work` when the description is epic-sized; title prefixed `Epic: ` |
| **Story** (slice of value) | Issue, optionally a sub-issue of an epic | Created by `/linear:plan-work`; ships as one PR |
| **Task** (unit of work) | Atomic commit | Created during `/linear:start` as the branch accumulates commits |

Milestones remain available as a Linear primitive — use them for genuinely date-bound or multi-phase tracking inside a project ("ship by Q2", "post-launch hardening"). They're no longer the default for an epic because milestones have no body, no status, and don't appear on the kanban board. Parent-issue epics carry the narrative and flow through Backlog → Doing → Done like any other card.

## What each layer is

**Epic.** A named initiative made of multiple stories. Too big to ship as one PR. Has a stakeholder-recognisable name like a feature or theme. Lives as a parent issue with sub-issues for each story. Title carries the `Epic: ` prefix so the umbrella is visible at a glance on the kanban board.

**Story.** One deliverable. Ships as one PR. Reverts cleanly. Sits as a sub-issue under an epic when one exists; otherwise sits directly in the project.

**Task.** One atomic commit. Stride's task layer lives in git history, not Linear's sub-issue feature. Each commit is one task-sized idea, and the PR ships them together as a coherent story.

**When in doubt about epic vs. story, ask: can this ship as one PR?** If yes, it's a story. If no, it's an epic. <mark>**Premature epics are clutter; missing epics are confusion.**</mark>

## Plan a few, ship, replan

When `/linear:plan-work` creates an epic (parent issue), it asks for **the first 1–3 stories** — not all of them. After the first lands, run `/linear:next-steps` against the epic and plan the next 1–3 — same loop, fresh context.

| Why plan 1–3 (agile) | What planning all of them at once (waterfall) costs |
|:---------------------|:----------------------------------------------------|
| You only know enough to plan a few stories well — beyond that you're guessing | Locks in design decisions before requirements force them |
| Each shipped story changes the context — story 4 might look different after 1–3 land | The backlog goes stale before you reach it |
| 1–3 fits in working memory; the user can review them as a coherent set | Bulk creation bypasses real review and bloats the board |
| Leaves the epic open to *act, then adjust* — feedback from a shipped story shapes the next plan | Pretends the future is knowable; closes doors before you need to |

## How the `/linear` commands map to layers

| Command | Layer it operates on |
|:--------|:---------------------|
| `/linear:plan-work` | Epic and story creation. Asks the sizing question; routes epic-sized work through parent-issue creation, story-sized through issue creation (optionally as a sub-issue of an existing epic) |
| `/linear:start` | Story → atomic commits. Surfaces the parent milestone if any; opens a branch and PR for the story |
| `/linear:fix` | Story (after PR review) — applies reviewer feedback as new commits |
| `/linear:finish` | Story closure. Marks the story Done; if it was the last open story in its milestone, prompts to mark the milestone done |
| `/linear:next-steps` | Story selection within a project or milestone. Offers an epic filter when milestones exist |

## Two axes: decomposition and flow

Epic → story → task is **decomposition** — how big a unit of work is. That's orthogonal to **flow** — where a unit sits on the kanban board (Backburner → Backlog → Todo → Doing → In Review → Done).

| Axis | Question it answers | Reference |
|:-----|:--------------------|:----------|
| **Decomposition** | *What is this work, and how big?* | This doc |
| **Flow** | *Where is this work right now?* | [Kanban process](/reference/kanban) |

A story sits somewhere on the kanban lanes. So does its parent epic. So do the child tasks once work begins. Parent-issue epics group sub-issues by decomposition *and* flow through the lanes themselves — the umbrella card moves Backlog → Doing → Done alongside its sub-issues. Milestones, when used for date-bound tracking, group by decomposition only; they don't move through flow.

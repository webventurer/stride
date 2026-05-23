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

## Why parent issues, not milestones?

Linear's own [Parent and sub-issues docs](https://linear.app/docs/parent-and-sub-issues) frame the choice cleanly:

> "Consider creating sub-issues when a set of work is too large to be a single issue but too small to be a project."

That's stride's epic. A milestone is a date-bound chunking marker inside a project — it has no body, no status, no place on the board. A parent issue is a real card with all of those, so the umbrella *moves* through the lanes alongside its sub-issues, the narrative *lives* on the card, and a non-engineer scanning the board sees the epic as an actual unit of work. Milestones still have a place — they're the right answer when the chunking is "ship before X date" rather than "this is a multi-story body of work" — but for stride's epic concept, parent issues fit better.

## What each layer is

**Epic.** A named initiative made of multiple stories. Too big to ship as one PR. Has a stakeholder-recognisable name like a feature or theme. Lives as a parent issue with sub-issues for each story. Title carries the `Epic: ` prefix so the umbrella is visible at a glance on the kanban board.

**Story.** One deliverable. Ships as one PR. Reverts cleanly. Sits as a sub-issue under an epic when one exists; otherwise sits directly in the project.

**Task.** One atomic commit. Stride's task layer lives in git history, not Linear's sub-issue feature. Each commit is one task-sized idea, and the PR ships them together as a coherent story.

**When in doubt about epic vs. story, ask: can this ship as one PR?** If yes, it's a story. If no, it's an epic. <mark>**Premature epics are clutter; missing epics are confusion.**</mark>

## How epics work

When `/linear:plan-work` recognises an epic-sized description, it does three things in order:

1. **Drafts the parent issue** using [EPIC-TEMPLATE.md](https://github.com/webventurer/stride/blob/main/.claude/commands/linear/reference/EPIC-TEMPLATE.md). The body has four sections — *Why this matters / What success looks like / What we agreed / What we won't touch* — strategic only, no implementation detail. The title is prefixed `Epic: ` so the umbrella is visible at a glance on the board.
2. **Saves the parent first** so its ID is available for the sub-issues that follow.
3. **Drafts each story as a sub-issue** with `parentId` set to the parent. Stories use the regular [issue template](/reference/issue-template) — they're stories that happen to have a parent.

After the work starts, the parent moves through the lanes like any other card (`/linear:start` opens a story, `/linear:finish` closes it; when the last sub-issue ships, `/linear:finish` prompts to mark the parent Done too).

For a visual mock-up of the parent and the sub-issues panel as Linear renders them, see [Example: Epic card](/reference/example-epic-card). For one of those sub-issues fully written out against the [issue template](/reference/issue-template), see [Example: Story card](/reference/example-story-card).

**The strategic frame lives on the epic; AI-implementable detail lives on each sub-issue.** That split is deliberate — an epic body that tries to enumerate all the implementation steps becomes a place where the same scope conversation happens twice (once on the epic, once on each sub-issue), and the sub-issue is the one a developer actually reads when they pick up work.

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
| `/linear:start` | Story → atomic commits. Surfaces the parent epic (parent issue) or milestone if any; opens a branch and PR for the story |
| `/linear:fix` | Story (after PR review) — applies reviewer feedback as new commits |
| `/linear:finish` | Story closure. Marks the story Done; if it was the last open sub-issue in its parent epic (or last open story in its milestone), prompts to mark the epic/milestone done |
| `/linear:next-steps` | Story selection within a project, parent-issue epic, or milestone. Offers an epic filter listing both parent-issue epics and milestones when either exists |

## Two axes: decomposition and flow

Epic → story → task is **decomposition** — how big a unit of work is. That's orthogonal to **flow** — where a unit sits on the kanban board (Backburner → Backlog → Todo → Doing → In Review → Done).

| Axis | Question it answers | Reference |
|:-----|:--------------------|:----------|
| **Decomposition** | *What is this work, and how big?* | This doc |
| **Flow** | *Where is this work right now?* | [Kanban process](/reference/kanban) |

A story sits somewhere on the kanban lanes. So does its parent epic. So do the child tasks once work begins. Parent-issue epics group sub-issues by decomposition *and* flow through the lanes themselves — the umbrella card moves Backlog → Doing → Done alongside its sub-issues. Milestones, when used for date-bound tracking, group by decomposition only; they don't move through flow.

# Issue template

Every Linear issue created by [`/linear:plan-work`](/skills/linear#linear-plan-work) follows the same seven-section structure. Each heading answers a natural question so the reader can scan quickly and know exactly what the issue is about.

## Title

The title is the first thing a stakeholder reads. Two rules:

1. **Imperative form** — start with a verb (Add, Fix, Replace, Remove…). Avoid "Investigate" unless the outcome genuinely is a report.
2. **Outcome, not implementation** — say *what changes for the reader, not what the implementation does*. The body explains *how*; the title says *what* changes for the reader.

### Outcome vs. implementation

| Implementation-level (avoid) | Outcome-level (prefer) |
|:-----------------------------|:-----------------------|
| Reset Tortoise globals between RQ jobs to prevent stale-loop pool | Background jobs run reliably after the first one |
| Add `null` check to `validateUser()` | Sign-up no longer crashes when the email is missing |
| Migrate from Webpack 4 to 5 | Builds finish in under 30 seconds |

### The infrastructure exception

Some work has no user-visible outcome — package upgrades, internal refactors, build changes. For these, name the **system behaviour** that changes, not the file that changes:

| Avoid | Prefer |
|:------|:-------|
| Update `pyproject.toml` ruff config | Linter accepts both 88- and 100-char lines |
| Move `linear_client.py` to `tools/` | `linear_client` is reusable across migration scripts |

If even the system behaviour is invisible (a pure rename, for instance), say what it is plainly: "Rename …", "Upgrade …". Don't contort the title into pretending there's a stakeholder when there isn't.

## Sections

| # | Section | Question it answers |
|:--|:--------|:--------------------|
| 1 | Why this matters | Should I care? |
| 2 | Where things stand | What's the current state? |
| 3 | What we'll do | What's the plan? |
| 4 | What we won't do | Where's the boundary? |
| 5 | Expected outcome | How do we know it's done? |
| 6 | How to test it | How do we verify? |
| 7 | Assumptions to confirm | What's still uncertain? |

Sections 4, 6, and 7 are optional — omit them when they don't add value.

### Why this matters: trace back to Vision

This section names the **Vision outcome** the issue serves — quote the relevant Success criterion line from [`VISION.md`](/) and explain how the work moves toward it. [`/linear:plan-work`](/skills/linear#linear-plan-work) enforces this: every draft must reference a Success criterion, and the agent pushes back if the user's request can't be tied to one. Either the work is out of scope, or the Vision needs a new outcome.

No Vision-tracing = no issue. Issues drafted in a vacuum drift from the project's purpose; the rule lives here so the doc matches the behaviour the command already enforces.

## Example

**Verify new issue template format renders correctly**

### Why this matters

Every issue we create uses this template. If the format is broken, every card in the backlog is harder to read.

### Where things stand

The issue template has new conversational headings but no one has checked whether they render correctly in Linear's markdown.

### What we'll do

- Create a single placeholder issue using the new template format
- Visual check that all sections render as expected

### What we won't do

No changes to the template based on this card — just validation.

### Expected outcome

- Issue appears in Linear with all sections visible and correctly formatted
- "Why this matters" section appears first, before "Where things stand"
- All headings render as distinct sections with no overlap

### How to test it

Visual inspection in Linear — open the issue and confirm each heading renders as a separate section with correct hierarchy.

### Assumptions to confirm

- Linear renders h3 markdown headings consistently across views (board, detail, sidebar)

## Design principles

The headings are deliberately conversational — they work equally well for bugs, features, and improvements. "Where things stand" is neutral: it can describe a broken API, a missing feature, or an opportunity for something new.

## Companion: epic structure

The seven-section template above is for **stories** — issues that ship as one PR. Epics (parent issues with sub-issues) use a shorter, strategic template instead:

| # | Section | Question it answers |
|:--|:--------|:--------------------|
| 1 | Why this matters | Should I care, and which Vision outcome does this serve? |
| 2 | What success looks like | What does this epic deliver as an outcome? |
| 3 | What we agreed | What's already been decided before opening sub-issues? |
| 4 | What we won't touch | What does this epic deliberately leave out? |

The epic body deliberately has **no** "What we'll do", "How to test it", or "Assumptions to confirm" sections. Those live on each sub-issue. Putting them on the epic creates two places where the same scope conversation happens — and the sub-issue is the one a developer reads when they pick up work. The epic carries the strategic frame; the sub-issues carry the tactical detail.

Epic titles are prefixed `Epic: <stakeholder outcome>` so the umbrella is visible at a glance on the kanban board. The post-colon part still follows the same outcome-not-implementation rule as story titles.

For the canonical worked example and the full mechanism, see [Epics and stories](/reference/epics-and-user-stories#how-epics-work). The CRAFT prompt that draws the body out of a description lives in [`EPIC-TEMPLATE.md`](https://github.com/webventurer/stride/blob/main/.claude/commands/linear/reference/EPIC-TEMPLATE.md), the parallel of the [`ISSUE-TEMPLATE.md`](https://github.com/webventurer/stride/blob/main/.claude/commands/linear/reference/ISSUE-TEMPLATE.md) used for stories.

The template avoids overlap between sections. Earlier versions had separate Goal, Acceptance criteria, and Success metric sections that all answered "how do we know it's done?" — these were merged into a single Expected outcome.

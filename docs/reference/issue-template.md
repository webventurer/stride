# Issue template

Every Linear issue created by [`/linear:plan-work`](/skills/linear#linear-plan-work) follows the same two-part structure: a plain-English part for the reader, then a part for the builder. Each heading answers a natural question so the reader can scan quickly and know exactly what the issue is about.

## Issue vs card

The two words name different aspects of the same artefact, so stride uses them deliberately:

| Term | Means | Used when |
|:-----|:------|:----------|
| **issue** | The content unit Linear's API and `/linear:*` commands operate on | Talking about planning, content, the thing with a description and status |
| **card** | The visual artefact on a kanban board | Talking about board rendering, kanban methodology, visual flow |

Throughout this template, "issue" is the right word — it's the content unit you're drafting. "Card" is correct in the [Kanban process](/reference/kanban) doc and in the worked-example mock-ups ([Epic card](/reference/example-epic-card), [Story card](/reference/example-story-card)), where the topic is board rendering.

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
| | **For the reader** | Written for the person who decides what goes in Todo, under the `### Why this matters` heading |
| 1 | Serves | Which Vision success criterion is this for? |
| 2 | Today | What happens now? |
| 3 | The problem | Should I care? |
| 4 | The change | What will be different? |
| 5 | Example | What does it look like? |
| | *a horizontal rule, then* **For the builder** | Written for the AI that builds it |
| 6 | What we'll do | What's the plan? |
| 7 | What we won't do | Where's the boundary? |
| 8 | Expected outcome | How do we know it's done? |
| 9 | How to test it | How do we verify? |
| 10 | Assumptions to confirm | What's still uncertain? |

Sections 7, 9, and 10 are optional — omit them when they don't add value.

### The reader's half

The five lines are one or two sentences each (**Serves:** is as long as the Vision line is), written in plain words for a reader of about 16: no file names and no commands in backticks outside the **Serves:** quote, and any stride term explained in the same sentence. The reader's half promises nothing the builder's half doesn't also promise, and whoever rewords one half rewords the other in the same edit. There is no "Where things stand" section: what happens now goes in **Today:**. A card already on the board without the reader's half is left as it is.

A bug card keeps the same reader's half, and its builder's half holds its symptoms, repro, expected vs actual, suspected causes, what we won't do, acceptance and regression test instead of the four story sections.

### Serves: trace back to Vision

The **Serves:** line names the **Vision outcome** the issue serves — the relevant Success criterion line from [`VISION.md`](/), quoted word for word. **The change:** explains how the work moves toward it. [`/linear:plan-work`](/skills/linear#linear-plan-work) enforces this: every draft must reference a Success criterion, and the agent pushes back if the user's request can't be tied to one. Either the work is out of scope, or the Vision needs a new outcome.

No Vision-tracing = no issue. Issues drafted in a vacuum drift from the project's purpose; the rule lives here so the doc matches the behaviour the command already enforces.

## Example

**Verify new issue template format renders correctly**

**For the reader**

### Why this matters

**Serves:** "Anyone who doesn't know stride's commands or code can understand every Linear card: an outcome in its title, everyday words in its description and updates"

**Today:** the issue template has a new two-part layout, but no one has checked how Linear draws it, like printing a poster without looking at the proof.

**The problem:** every issue we create uses this template. If the layout is broken, every issue in the backlog is harder to read.

**The change:** one placeholder issue is created in the new layout and looked at in Linear.

**Example:** the placeholder shows "For the reader" and "For the builder" as two clearly separate parts, with the rule between them.

---

**For the builder**

### What we'll do

- Create a single placeholder issue using the new template format
- Visual check that all sections render as expected

### What we won't do

No changes to the template based on this issue — just validation.

### Expected outcome

- Issue appears in Linear with all sections visible and correctly formatted
- The reader's half appears first, above a horizontal rule and "For the builder"
- All headings render as distinct sections with no overlap

### How to test it

Visual inspection in Linear — open the issue and confirm each heading renders as a separate section with correct hierarchy.

### Assumptions to confirm

- Linear renders h3 markdown headings consistently across views (board, detail, sidebar)

## Design principles

The headings are deliberately conversational — they work equally well for bugs, features, and improvements. "Today:" is neutral: it can describe a broken API, a missing feature, or an opportunity for something new.

## Companion: epic structure

The two-part template above is for **stories** — issues that ship as one PR. Epics (parent issues with sub-issues) use a shorter, strategic template instead:

| # | Section | Question it answers |
|:--|:--------|:--------------------|
| | **For the reader** | The same five lines as a story (Serves, Today, The problem, The change, Example), under `### Why this matters` |
| | *a horizontal rule, then* **For the builder** | |
| 6 | What success looks like | What does this epic deliver as an outcome? |
| 7 | What we agreed | What's already been decided before opening sub-issues? |
| 8 | What we won't touch | What does this epic deliberately leave out? |

The epic's builder half deliberately has **no** "What we'll do", "Expected outcome", "How to test it", or "Assumptions to confirm" sections. Those live on each sub-issue. Putting them on the epic creates two places where the same scope conversation happens — and the sub-issue is the one a developer reads when they pick up work. The epic carries the strategic frame; the sub-issues carry the tactical detail.

Epic titles are prefixed `Epic: <stakeholder outcome>` so the umbrella is visible at a glance on the kanban board. The post-colon part still follows the same outcome-not-implementation rule as story titles.

For the canonical worked example and the full mechanism, see [Epics and stories](/reference/epics-and-user-stories#how-epics-work). The [epic structure](#companion-epic-structure) is the shorter counterpart to the [two-part story template](#sections).

The template avoids overlap between sections. Earlier versions had separate Goal, Acceptance criteria, and Success metric sections that all answered "how do we know it's done?" — these were merged into a single Expected outcome.

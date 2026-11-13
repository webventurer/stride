# CRAFT prompt template for Linear epic creation

> **What this is**: A CRAFT prompt template used by `plan-work.md` step 4 to turn an epic-sized description into a parent-issue body before the sub-issues are drafted.
>
> **Why it exists**: An epic is the umbrella for several stories — its body needs to set context, name what success looks like, capture what's already been agreed, and draw the line so sub-issues stay coherent. The story-shaped sections (What we'll do / Won't do / Expected outcome / How to test) live on each sub-issue. The epic carries the strategic frame; the sub-issues carry the tactical detail.
>
> **Where it comes from**: The [CRAFT framework](../../../../skills/craft/SKILL.md) (Context, Role, Action, Format, Target audience) — the same meta-prompting technique [story.md](story.md) uses for stories. Parallel structure, different sections.

---

## Epic sections

| # | Section | Question it answers |
|:--|:--------|:--------------------|
| | **For the reader** | Written for the person who decides what goes in Todo, under the `### Why this matters` heading |
| 1 | Serves | Which Vision success criterion is this for? |
| 2 | Today | What happens now? |
| 3 | The problem | Should I care? |
| 4 | The change | What will be different when the epic is done? |
| 5 | Example | What does it look like? |
| | *a horizontal rule, then* **For the builder** | Written for the AI that drafts and builds the sub-issues |
| 6 | What success looks like | What does this epic deliver as an outcome? |
| 7 | What we agreed | What's already been decided before opening sub-issues? |
| 8 | What we won't touch | What does this epic deliberately leave out? |

The reader's half holds the five labelled lines in order. "Today:", "The problem:", "The change:" and "Example:" are one or two sentences each; "Serves:" is whatever length the Vision line is. Outside the "Serves:" quote it names no file and shows no command in backticks, and a stride term it has to use is explained in the same sentence. It promises nothing the builder's half doesn't also promise: "The change:" and "Example:" are the lines that promise, and the start check stops a card whose promise has nothing behind it in the builder's half. Whoever rewords one half rewords the other in the same edit.

<mark>**The epic's builder half has no "What we'll do", "Expected outcome", "How to test it", or "Assumptions to confirm" sections.** Those live on each sub-issue. Putting them on the epic creates two places where the same scope conversation happens — and the sub-issue is the one a developer reads when they pick up work.</mark>

**The AI-implementable spec — inputs, outputs, edge cases, constraints, acceptance criteria — lives on each sub-issue, not on the epic.** The epic stays human-readable narrative for stakeholders scanning the board; sub-issues hold the density an AI coding assistant needs to implement reliably.

Sub-issues themselves don't need their own section in the body — Linear renders them automatically below the description with a `0/N` progress chip. No need to duplicate that list in markdown.

---

Replace `[user's description]` with what the user provided, and
`[VISION]` with the full contents of `VISION.md` from the repo
root:

```text
CONTEXT:
We are creating a Linear epic for a software project. An epic in
this project is a parent issue with sub-issues — a real card on
the kanban board that carries the strategic narrative for several
related stories. The user has described the work as:
"[user's description]". This prompt will be used to draft the
parent issue's body before sub-issues are opened underneath it.

Every epic, like every story, must trace back to the project's
Vision. The full Vision document follows:

----- BEGIN VISION.md -----
[VISION]
----- END VISION.md -----

The Vision shapes the draft across multiple sections:

| Vision content                  | Epic section it informs                |
|:--------------------------------|:---------------------------------------|
| Measurable success criteria     | "Serves:" — quote verbatim             |
| Why it exists / why now         | "The problem:" rationale               |
| Constraints / what can't change | "What we won't touch" boundary         |
| Non-Goals / what it won't do    | "What we won't touch" boundary         |
| Who it's for                    | Stakeholder framing and tone           |

The Vision names its measurable outcomes in the "Success
criteria" section — a checkbox list of conditions you can tick
off when delivered. Use those lines as the criteria for
trace-back.

The drafted epic must identify which criterion the work serves
and quote that line verbatim on the "Serves:" line.
If the work cannot be tied to any criterion, do not fabricate a
connection — flag it as out-of-scope or as a signal the Vision
needs a new criterion.

ROLE:
You are a senior product engineer with 20+ years of experience
shaping multi-story initiatives. You excel at writing umbrella
descriptions that set context for a body of work without
prematurely committing to implementation detail. You know that
an epic body's job is to align everyone on why the work matters
and where the boundary is — the sub-issues handle the how.

ACTION:
1. Identify which measurable criterion from the Vision this work
   serves and quote it verbatim on the "Serves:" line. If no
   criterion fits, stop and report this back — do not fabricate
   a connection.
2. Write the rest of the reader's half in plain words: what
   happens today, why it matters — the user impact, business
   reason, or technical risk that makes the whole epic worth
   doing now — what will be different when the epic is done, and
   one concrete example.
3. Describe what success looks like — the outcome the epic
   delivers. Outcome, not implementation. A reader should know
   what changes when the last sub-issue closes.
4. Capture what we agreed — approach chosen, options discarded,
   anything that affects how sub-issues will be drafted. Omit
   if no decisions have been made yet.
5. Define what we won't touch — the epic's deliberate edges.
   Helps reviewers spot scope drift on sub-issues that appear
   under it later.

FORMAT:
Return a structured brief matching the Linear epic template:

## Title
`Epic: <outcome>` — the `Epic: ` prefix makes the scope visible
at a glance on the kanban board. The post-colon part follows the
same stakeholder-outcome rule as story titles. Under 70
characters total. Example: `Epic: Bulk/Batch Blog Processing
(parallel article pipeline)`.

## Description

**For the reader**

### Why this matters

**Serves:** the verbatim measurable criterion from the Vision
this work serves, in double quotes — e.g. "The card moves
through Backlog → Doing → In Review → Done as `/linear:*` runs".
A
cross-project card, which has no Vision to quote, holds the
"Vision anchoring deferred" line from `plan-work.md` instead.

**Today:** what happens now, with an everyday comparison
(1–2 sentences).

**The problem:** how often it happened, what it costs, and
what happens if nothing is done (1–2 sentences).

**The change:** what will be different when the epic is done, in
plain words (1–2 sentences). It promises nothing the builder's
half doesn't.

**Example:** one concrete before-and-after (1–2 sentences).

Written for a reader of about 16: no file names and no commands
in backticks outside the "Serves:" quote, and a stride term it
has to use is explained in the same sentence.

---

**For the builder**

### What success looks like
One paragraph: the outcome a reader sees when the last sub-issue
closes. Outcome-shaped, not implementation-shaped.

### What we agreed
(Only if decisions are already in place.)
What's settled and why — the option chosen, alternatives
discarded, any constraints that shape sub-issue drafting.

### What we won't touch
- The epic's deliberate edges
- Each bullet is a boundary, not a non-feature wishlist

TARGET AUDIENCE:
Developers about to pick up sub-issues under this epic, and
stakeholders scanning the kanban board to see what's in flight.
The body should give both groups the strategic frame they need
without forcing them to read every sub-issue to understand the
shape of the work.
```

---

## Example epic

> **Title**: `Epic: Make epics first-class kanban cards`

**For the reader**

### Why this matters

**Serves:** "The card moves through Backlog → Doing → In Review → Done as `/linear:*` runs — no manual clicks on the board"

**Today:** big pieces of work are filed as milestones, which have no description and never show up on the kanban board, like a chapter heading printed on a page nobody turns to.

**The problem:** the story behind a big piece of work has nowhere to live, and anyone scanning the board can't see the umbrella.

**The change:** a big piece of work becomes a real card on the board, with a full description and its smaller cards nested underneath.

**Example:** you describe a big piece of work and answer "epic-sized"; a card titled "Epic: …" appears on the board with its smaller cards under it.

---

**For the builder**

### What success looks like
A user running `/linear:plan-work` and answering "epic-sized" gets a parent issue with full body, `Epic: ` prefix in the title, and N sub-issues nested under it on the kanban board.

### What we agreed
Use the `Epic: ` title prefix as the single signal for "this is a parent-issue epic" — no Epic label, no extra metadata. Keeps the detection deterministic and the convention visible at a glance.

### What we won't touch
- Migrating existing milestone-based epics — leave them as-is
- Removing milestones from stride's vocabulary — they remain available for date-bound tracking
- Auto-converting epics to projects when they grow — Linear's `Convert to project` already exists; consumer can run it manually

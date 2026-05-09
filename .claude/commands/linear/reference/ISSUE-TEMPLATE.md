# CRAFT prompt template for Linear issue creation

> **What this is**: A CRAFT prompt template used by `plan-work.md` step 3 to turn a vague user description into a precise brief before research and drafting.
>
> **Why it exists**: Users often describe work loosely — "add error handling" or "fix the dashboard". Running this through CRAFT produces a structured brief (why it matters, where things stand, what we'll do, expected outcome) that gives the research step (4) precise targets and the drafting step (6) concrete material to work with.
>
> **Where it comes from**: The [CRAFT framework](../../../skills/craft/SKILL.md) (Context, Role, Action, Format, Target audience) — a meta-prompting technique for generating structured, high-quality LLM outputs.

---

## Issue sections

| # | Section | Question it answers |
|:--|:--------|:--------------------|
| 1 | Summary | What's the shape of this in 30 seconds? |
| 2 | Why this matters | Should I care? |
| 3 | Where things stand | What's the current state? |
| 4 | What we'll do | What's the plan? |
| 5 | What we won't do | Where's the boundary? |
| 6 | Expected outcome | How do we know it's done? |
| 7 | How to test it | How do we verify? |
| 8 | Assumptions to confirm | What's still uncertain? |

<mark>**Summary leads. Plain language, no jargon, no Vision references yet** — Vision-grounding lives in *Why this matters* immediately after.</mark> The Summary's job is to make the issue's purpose scannable in 30 seconds, so the reader (and `/linear:finish`'s Vision-confirm) doesn't have to re-read the dense detail to remember what shipped.

---

Replace `[user's description]` with what the user provided, and
`[VISION]` with the full contents of `VISION.md` from the repo
root:

```text
CONTEXT:
We are creating a Linear issue for a software project. The user
has described the work as: "[user's description]". This prompt
will be used to guide codebase research and issue drafting — it
needs to surface why this matters, where things stand, what
we'll do, and the expected outcome so the resulting issue is
immediately actionable by a developer.

Every issue in this project must trace back to the project's
Vision. The full Vision document follows:

----- BEGIN VISION.md -----
[VISION]
----- END VISION.md -----

The Vision shapes the draft across multiple sections, not just
the trace-back. Use it as follows:

| Vision content                  | Issue section it informs            |
|:--------------------------------|:------------------------------------|
| (none — kept Vision-free)       | "Summary" — plain language only     |
| Measurable success criteria     | "Why this matters" — quote verbatim |
| Non-Goals / what it won't do    | "What we won't do" boundary         |
| Constraints / what can't change | "Where things stand", "How to test" |
| Who it's for                    | Stakeholder framing and tone        |
| Why it exists / why now         | "Why this matters" rationale        |

The Summary deliberately avoids Vision references — it leads
with what the work *is* in plain language, so the trace-back in
"Why this matters" lands against an already-articulated purpose.

The Vision names its measurable outcomes in the "Success
criteria" section — a checkbox list of conditions you can tick
off when delivered. Use those lines as the criteria for
trace-back.

The drafted issue must identify which criterion the work serves
and quote that line verbatim in the Why-this-matters section.
If the work cannot be tied to any criterion, do not fabricate a
connection — flag it as out-of-scope or as a signal the Vision
needs a new criterion.

ROLE:
You are a senior product engineer with 20+ years of experience
breaking down ambiguous feature requests into precise, atomic
engineering tasks. You excel at identifying the core need
behind a request, separating must-haves from nice-to-haves,
and writing issue descriptions that a developer can start
working on without asking clarifying questions.

ACTION:
1. Write a plain-language Summary first — three short paragraphs:
   the problem (what's broken / missing), the fix (what the change
   does, often a small before/after table), and optionally what
   stays the same. No jargon, no Vision references, no implementation
   detail. The Summary is what someone scans in 30 seconds to know
   the shape of the work.
2. Identify which measurable criterion from the Vision this work
   serves and quote it verbatim, then explain why this matters —
   the user impact, business reason, or technical risk that makes
   this worth doing now. Let the Vision's Why / Why-now framing
   inform the rationale. If no criterion fits, stop and report
   this back — do not fabricate a connection. Either the work is
   out of scope or the Vision needs a new criterion.
3. Describe where things stand — the current state, whether
   that's a bug, a gap, or an opportunity for something new
4. Define what we'll do — the deliverable and scope boundary
5. Define what we won't do — scope exclusions, only if
   genuinely useful
6. Define the expected outcome — observable results that prove
   it's done, plus measurable metrics if applicable
7. Describe how to test it — expected behaviour, edge cases,
   error conditions (omit for docs, config, or exploratory work)
8. Flag any ambiguities or assumptions that need confirming

FORMAT:
Return a structured brief matching the Linear issue template:

## Title
Concise, imperative, starting with a verb (e.g., "Add dark mode
toggle to dashboard header"). Under 70 characters.

## Summary

**The problem.** Plain-language statement of what's broken,
missing, or causing friction. No jargon, no Vision references.
2–4 sentences.

**The fix.** What the change does. Often a small before/after
table when the diff is structural. 2–4 sentences or a table.

**What stays the same.** (Optional — include when behaviour is
being added rather than replaced.) What's preserved by the change.

### Why this matters
First line: the verbatim measurable criterion from the Vision
this work serves, in italic markdown — e.g. *"Every multi-step
stride interaction discloses its scope upfront"*. Then 1–2
sentences on user impact, business reason, or technical risk
that makes this worth doing now.

### Where things stand
Current state — the bug, gap, or opportunity (1–2 sentences)

### What we'll do
One-sentence deliverable, then bullet list of scope details

### What we won't do
(Only if genuinely useful — omit if nothing meaningful)

### Expected outcome
Observable results that prove it's done (2–3 bullets). These
are not implementation steps — they describe what a reviewer
should see, not how to code it. Include measurable metrics
when applicable.

### How to test it
(Optional — omit for docs, config, or exploratory work)
Write tests first. What to test: expected behaviour, edge cases,
error conditions.

### Assumptions to confirm
- Bullet list of ambiguities that need resolving

TARGET AUDIENCE:
A developer who will implement this issue. They need clarity,
not context they already have from the codebase. Prefer
concrete over abstract — "the API returns 500 when X is null"
beats "improve error handling".
```

---

## Research mode additions

When running in `--research` mode, append these sections to the
issue after the base template above:

### Implementation notes
Findings from codebase exploration

### Code examples
Actual snippets from the codebase showing how similar patterns are
already implemented — component structure, styling, registration,
utility usage. The goal: the implementing agent should never need
to ask "how do we do X in this codebase?" because examples of X
are right there in the issue.

### Related code
- Files, components, or areas discovered during research

### Related issues
- Links/identifiers of similar Linear issues found

---

## Example issue

> **Verify new issue template format renders correctly**

## Summary

**The problem.** The issue template just got new conversational
headings, but no one has rendered an issue from it in Linear yet
— so we don't know whether the markdown displays cleanly across
Linear's board, detail, and sidebar views.

**The fix.** Create one placeholder issue using the new template
and visually inspect each section in Linear. No template changes
ship from this work — pure validation.

### Why this matters
*Sets the stakes — why this work is worth doing now.*

*"Issue titles read as stakeholder outcomes, not implementation
steps"*

Every issue we create uses this template. If the format is
broken, every issue in the backlog is harder to read — and the
stakeholder-readable shape we're committing to in the Vision
gets undermined at the first hop.

### Where things stand
*Current state — the gap, limitation, or opportunity.*

The issue template has new conversational headings but
no one has checked whether they render correctly in
Linear's markdown.

### What we'll do
*Concrete deliverables — what ships when this closes.*

Confirm the new issue template renders correctly in Linear.
- Create a single placeholder issue using the new template
  format
- Visual check that all sections render as expected

### What we won't do
*Draws the line so scope doesn't creep.*

No changes to the template based on this issue — just
validation.

### Expected outcome
*Observable proof it's done — what a reviewer should see.*
- Issue appears in Linear with all sections visible and
  correctly formatted
- "Why this matters" section appears first, before
  "Where things stand"
- All headings render as distinct sections with no overlap

### How to test it
*How to verify the outcome is real.*

Visual inspection in Linear — open the issue and confirm each
heading renders as a separate section with correct hierarchy.

### Assumptions to confirm
*Unknowns that could change the plan.*
- Linear renders h3 markdown headings consistently across
  views (board, detail, sidebar)

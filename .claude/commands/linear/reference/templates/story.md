# CRAFT prompt template for Linear issue creation

> **What this is**: A CRAFT prompt template used by `plan-work.md` step 4 to turn a vague user description into a precise brief before research and drafting.
>
> **Why it exists**: Users often describe work loosely — "add error handling" or "fix the dashboard". Running this through CRAFT produces a structured brief (why it matters, where things stand, what we'll do, expected outcome) that gives the research step (4) precise targets and the drafting step (6) concrete material to work with.
>
> **Where it comes from**: The [CRAFT framework](../../../skills/craft/SKILL.md) (Context, Role, Action, Format, Target audience) — a meta-prompting technique for generating structured, high-quality LLM outputs.

---

## Issue sections

| # | Section | Question it answers |
|:--|:--------|:--------------------|
| 1 | Why this matters | Should I care? |
| 2 | Where things stand | What's the current state? |
| 3 | What we'll do | What's the plan? |
| 4 | What we won't do | Where's the boundary? |
| 5 | Expected outcome | How do we know it's done? |
| 6 | How to test it | How do we verify? |
| 7 | Assumptions to confirm | What's still uncertain? |

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
| Measurable success criteria     | "Why this matters" — quote verbatim |
| Non-Goals / what it won't do    | "What we won't do" boundary         |
| Constraints / what can't change | "Where things stand", "How to test" |
| Who it's for                    | Stakeholder framing and tone        |
| Why it exists / why now         | "Why this matters" rationale        |

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
1. Identify which measurable criterion from the Vision this work
   serves and quote it verbatim, then explain why this matters —
   the user impact, business reason, or technical risk that makes
   this worth doing now. Let the Vision's Why / Why-now framing
   inform the rationale. If no criterion fits, stop and report
   this back — do not fabricate a connection. Either the work is
   out of scope or the Vision needs a new criterion.
2. Describe where things stand — the current state, whether
   that's a bug, a gap, or an opportunity for something new
3. Explain what we'll do — the concrete solution, then the
   deliverable and scope boundary. When a relevant principle
   exists, apply it to the context to derive concrete, testable
   requirements. Explain the connection and identify choices
   the principle does not settle. Describe the trigger, rule
   and action, with worked examples before implementation details.
4. Define what we won't do — scope exclusions, only if
   genuinely useful
5. Define the expected outcome — observable results that prove
   it's done, plus measurable metrics if applicable. Every line
   the end check counts as a promise, here and in steps 3, 4
   and 6, passes two tests: someone holding the finished change
   can answer it yes or no, and the answer is no if the change
   was made but doesn't work. Rewrite or move a line that fails,
   following the table in `reference/card-language.md`
6. Describe how to test it — expected behaviour, edge cases,
   error conditions (omit for docs, config, or exploratory work)
7. Flag any ambiguities or assumptions that need confirming

FORMAT:
Return a structured brief matching the Linear issue template:

## Title
Concise, imperative, starting with a verb (e.g., "Add dark mode
toggle to dashboard header"). Under 70 characters.

## Description

### Why this matters
First line: the verbatim measurable criterion from the Vision
this work serves, in italic markdown — e.g. *"Linear board state
matches branch state automatically as /linear:* runs"*. Then 1–2
sentences on user impact, business reason, or technical risk
that makes this worth doing now.

### Where things stand
Current state — the bug, gap, or opportunity (1–2 sentences)

### What we'll do
State the solution in one sentence, then explain how it works
in plain language. When a relevant principle exists, apply it
to this context to derive concrete, testable requirements.
Explain the connection and identify choices it does not settle.
Describe what triggers the behaviour, what is checked, what
happens when it passes or fails, and any material exception.
Use concrete worked examples for distinct behaviour-changing
rules. Mark example values as illustrative unless agreed.
Describe the behaviour the caller sees, not the internal
mechanism. Follow with implementation details only where a
constraint forces them, then scope; a list of settings or
files is not an explanation of the solution.

### What we won't do
(Only if genuinely useful — omit if nothing meaningful)

### Expected outcome
Observable results that prove it's done (2–3 bullets). These
are not implementation steps — they describe what a reviewer
should see, not how to code it. Include measurable metrics
when applicable.

### How to test it
(Optional — omit for docs, config, or exploratory work)
What the finished change must show: the tests that prove the
expected behaviour, edge cases and error conditions. A run done by
hand, such as a live test on a throwaway card, goes under "Live
check" instead; its result is posted on the card as a comment. A
claim only that run can prove, such as matching the real board,
belongs under "Live check" too, not in What we'll do.

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

> **Refuse a sign-up email that has no @ sign**

### Why this matters
*Sets the stakes — why this work is worth doing now.*

*"New users finish sign-up on their first try"*

A typo in the email address today creates an account nobody
can log in to, and the user only finds out when the welcome
email never arrives.

### Where things stand
*Current state — the gap, limitation, or opportunity.*

The sign-up form accepts any text in the email field and
creates the account straight away.

### What we'll do
*Concrete deliverables — what ships when this closes.*

When the email field has no @ sign, the form refuses to submit
and shows "Enter an email address with an @ sign" under the
field. Example: "ana.example.com" is refused; "ana@example.com"
creates the account.

### What we won't do
*Draws the line so scope doesn't creep.*

- Won't check that the email address exists or can receive mail

### Expected outcome
*Observable proof it's done — what a reviewer should see.*
- Submitting "ana.example.com" creates no account and shows
  "Enter an email address with an @ sign" under the field
- Submitting "ana@example.com" creates the account

### How to test it
*How to verify the outcome is real.*

A form test submits each of the two addresses above and checks
the account count and the message shown.

### Assumptions to confirm
*Unknowns that could change the plan.*
- An @ sign is enough of a check to catch most typos

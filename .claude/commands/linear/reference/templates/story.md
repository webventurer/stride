# CRAFT prompt template for Linear issue creation

> **What this is**: A CRAFT prompt template used by `plan-work.md` step 4 to turn a vague user description into a precise brief before research and drafting.
>
> **Why it exists**: Users often describe work loosely — "add error handling" or "fix the dashboard". Running this through CRAFT produces a structured brief (a plain-English part for the reader, then what we'll do and the expected outcome for the builder) that gives the research step (4) precise targets and the drafting step (6) concrete material to work with.
>
> **Where it comes from**: The [CRAFT framework](../../../skills/craft/SKILL.md) (Context, Role, Action, Format, Target audience) — a meta-prompting technique for generating structured, high-quality LLM outputs.

---

## Issue sections

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

The reader's half holds the five labelled lines in order. "Today:", "The problem:", "The change:" and "Example:" are one or two sentences each; "Serves:" is whatever length the Vision line is. Outside the "Serves:" quote it names no file and shows no command in backticks, and a stride term it has to use is explained in the same sentence. It promises nothing the builder's half doesn't also promise: "The change:" and "Example:" are the lines that promise, and the start check stops a card whose promise has nothing behind it in the builder's half. Whoever rewords one half rewords the other in the same edit.

---

Replace `[user's description]` with what the user provided, and
`[VISION]` with the full contents of `VISION.md` from the repo
root:

```text
CONTEXT:
We are creating a Linear issue for a software project. The user
has described the work as: "[user's description]". This prompt
will be used to guide codebase research and issue drafting — it
needs to surface a plain-English part for the reader (what it
serves, today, the problem, the change, an example), then what
we'll do and the expected outcome for the builder, so the
resulting issue is immediately actionable by a developer.

Every issue in this project must trace back to the project's
Vision. The full Vision document follows:

----- BEGIN VISION.md -----
[VISION]
----- END VISION.md -----

The Vision shapes the draft across multiple sections, not just
the trace-back. Use it as follows:

| Vision content                  | Issue section it informs            |
|:--------------------------------|:------------------------------------|
| Measurable success criteria     | "Serves:" — quote verbatim          |
| Non-Goals / what it won't do    | "What we won't do" boundary         |
| Constraints / what can't change | "Today:", "How to test it"          |
| Who it's for                    | Stakeholder framing and tone        |
| Why it exists / why now         | "The problem:" rationale            |

The Vision names its measurable outcomes in the "Success
criteria" section — a checkbox list of conditions you can tick
off when delivered. Use those lines as the criteria for
trace-back.

The drafted issue must identify which criterion the work serves
and quote that line verbatim on the "Serves:" line.
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
   serves and quote it verbatim on the "Serves:" line. If no
   criterion fits, stop and report this back — do not fabricate
   a connection. Either the work is out of scope or the Vision
   needs a new criterion.
2. Write the rest of the reader's half in plain words: what
   happens today (a bug, a gap, or an opportunity for something
   new), why it matters — the user impact, business reason, or
   technical risk that makes this worth doing now, letting the
   Vision's Why / Why-now framing inform the rationale — what
   will change, and one concrete example.
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

**For the reader**

### Why this matters

**Serves:** the verbatim measurable criterion from the Vision
this work serves, in double quotes — e.g. "The card moves
through Backlog → Doing → In Review → Done as `/linear:*` runs".
A
cross-project card, which has no Vision to quote, holds the
"Vision anchoring deferred" line from `plan-work.md` instead.

**Today:** what happens now, with an everyday comparison
(1–2 sentences). It includes any fact the builder can't find in
the code, such as something seen in another project.

**The problem:** the case for filing: how often it happened,
what it costs, and what happens if nothing is done (1–2
sentences).

**The change:** what will be different, in plain words (1–2
sentences). It promises nothing the builder's half doesn't.

**Example:** one concrete before-and-after (1–2 sentences).

Written for a reader of about 16: no file names and no commands
in backticks outside the "Serves:" quote, and a stride term it
has to use is explained in the same sentence.

---

**For the builder**

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

**For the reader**

### Why this matters

**Serves:** "New users finish sign-up on their first try"

**Today:** the sign-up form accepts any text in the email field
and creates the account straight away, like a post office that
takes a parcel with no street on the address.

**The problem:** a typo in the email address creates an account
nobody can log in to. The user only finds out when the welcome
email never arrives.

**The change:** the form refuses an email address that has no @
sign and says why.

**Example:** "ana.example.com" is refused with a message under
the field; "ana@example.com" creates the account.

---

**For the builder**

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

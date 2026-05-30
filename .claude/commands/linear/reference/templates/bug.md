# CRAFT prompt template for Linear bug creation

> **What this is**: A CRAFT prompt template used by `plan-work.md` step 4 to turn a bug report into a precise diagnosis-shaped brief before drafting.
>
> **Why it exists**: Bugs answer a different shape of question than features — symptoms, repro, expected vs actual, suspected causes. Running bug-shaped work through the story template buries the rigour under *"Where things stand"* and invites premature commitment to a specific fix before diagnosis is done. This template surfaces the bug-shaped sections as first-class, so the draft reads as a diagnosis brief rather than a feature spec wearing a bug label.
>
> **Where it comes from**: The [CRAFT framework](../../../../skills/craft/SKILL.md) (Context, Role, Action, Format, Target audience) — the same meta-prompting technique [issue.md](issue.md) uses for features. Parallel structure, different sections.

---

## Bug sections

| # | Section | Question it answers |
|:--|:--------|:--------------------|
| 1 | Why this matters | Should I care? |
| 2 | Symptoms | What does a user observe? |
| 3 | Repro | How do I trigger it? |
| 4 | Expected vs actual | What's the gap? |
| 5 | Suspected causes | What might be wrong? |
| 6 | What we won't do | Where's the boundary? |
| 7 | Acceptance | How do we know it's fixed? |
| 8 | Regression test | What would have caught this? |

<mark>**The bug template drops "What we'll do" and "Assumptions to confirm".**</mark> The deliverable is implicit — *fix the bug* — and committing to a specific fix before diagnosis is done is premature. Each suspected cause is itself an assumption to test, so a separate Assumptions section duplicates the work.

---

Replace `[user's description]` with what the user provided, and
`[VISION]` with the full contents of `VISION.md` from the repo
root:

```text
CONTEXT:
We are creating a Linear bug report for a software project. The
user has described the bug as: "[user's description]". This
prompt will guide diagnosis-shaped drafting — it needs to
surface symptoms (what a user sees), repro (how to trigger it),
the expected/actual gap, and suspected causes ordered by
likelihood. The resulting card is a diagnosis brief, not a
commitment to a specific fix.

Every bug in this project must trace back to the project's
Vision — usually because it breaks a Success criterion the
project is committed to. The full Vision document follows:

----- BEGIN VISION.md -----
[VISION]
----- END VISION.md -----

The Vision shapes the bug draft across multiple sections:

| Vision content                  | Bug section it informs              |
|:--------------------------------|:------------------------------------|
| Measurable success criteria     | "Why this matters" — quote verbatim |
| Constraints / what can't change | "What we won't do" boundary         |
| Who it's for                    | Stakeholder framing and tone        |

The Vision names its measurable outcomes in the "Success
criteria" section — a checkbox list of conditions you can tick
off when delivered. A bug usually surfaces because one of those
criteria is being violated. Identify which criterion is at
stake and quote it verbatim in the Why-this-matters section.
If the bug doesn't trace to any criterion, do not fabricate a
connection — flag it as out-of-scope or as a signal the Vision
needs a new criterion.

ROLE:
You are a senior product engineer with 20+ years of experience
diagnosing production bugs. You excel at separating symptoms
from causes, writing repro steps minimal enough to run in a
clean environment, and listing suspected causes in order of
likelihood without locking in on the first guess. You know that
a good bug report leaves the fix open until diagnosis is done.

ACTION:
1. Identify which measurable criterion from the Vision is at
   stake and quote it verbatim, then explain why this bug
   matters — the user impact, business reason, or technical
   risk that makes it worth fixing now. If no criterion fits,
   stop and report this back — do not fabricate a connection.
2. Describe the symptoms — what a user observes, in
   user-visible terms. Not the internal cause, not the fix —
   just what's wrong from outside.
3. Write the repro — numbered steps, exact commands, minimal
   setup. A developer with a clean checkout should be able to
   follow these and see the bug.
4. State the gap — expected behaviour vs actual behaviour, in
   two lines. No paragraphs.
5. List suspected causes in order of likelihood. Each cause is
   an assumption to test, not a commitment. The first one is
   the most likely; the last one is the long-shot worth
   keeping on the list.
6. Define what we won't do — scope exclusions, only if
   genuinely useful (e.g. "not refactoring the surrounding
   module while we're in there").
7. Define acceptance — the failure mode disappears AND the
   regression test passes. Both, not one.
8. Name the regression test — the test that would have caught
   this bug if it had existed. Where it lives, what it
   asserts.

FORMAT:
Return a structured brief matching the Linear bug template:

## Title
Concise, imperative, naming the failure mode from the user's
perspective (e.g., "Submit button does nothing on the contact
form"). Under 70 characters. Avoid implementation jargon — the
title is what shows up on the board.

## Description

### Why this matters
First line: the verbatim measurable criterion from the Vision
this bug violates, in italic markdown — e.g. *"Background jobs
run reliably after the first one"*. Then 1–2 sentences on user
impact: who hits this, how often, what they can't do because
of it.

### Symptoms
What a user observes. User-visible terms, not internals. 2–4
bullets — what they see, not what's happening underneath.

### Repro
Numbered steps. Exact commands where applicable. Minimal setup
— a developer with a clean checkout should be able to follow
these end-to-end.

```
1. ...
2. ...
3. ...
```

### Expected vs actual
Two lines. Format:

- **Expected**: <what should happen>
- **Actual**: <what happens instead>

No paragraphs — the gap is the point.

### Suspected causes
Ordered by likelihood. Each cause is an assumption to test,
not a commitment to a fix.

1. Most likely — <hypothesis>
2. Second — <hypothesis>
3. Long-shot — <hypothesis>

### What we won't do
(Only if genuinely useful — omit if nothing meaningful.)
Scope exclusions — e.g. "not refactoring the surrounding
module while we're in there".

### Acceptance
- [ ] Failure mode disappears under the repro steps above
- [ ] Regression test (below) passes

### Regression test
Write the test first — the test that would have caught this
bug if it had existed. Name the file, describe what it asserts,
and confirm it fails on the current code and passes after the
fix.

TARGET AUDIENCE:
A developer who will diagnose and fix this bug. They need the
symptoms, repro, and gap in concrete terms so they can reach a
diagnosis before touching code. Prefer specific over general —
"jobs after the first one return without running" beats "jobs
fail intermittently".
```

---

## Research mode additions

When running in `--research` mode, append these sections to the
bug after the base template above:

### Implementation notes
Findings from codebase exploration — what the relevant code
path looks like, what assumptions the existing code makes,
where the bug likely lives.

### Code examples
Actual snippets from the codebase showing the suspect call
sites, similar patterns that work correctly, or related fixes
applied elsewhere. The implementing agent should never need to
ask "where does this code live?" because pointers are right
there in the bug.

### Related code
- Files, components, or areas discovered during research

### Related issues
- Links/identifiers of similar Linear bugs or prior fixes

---

## Example bug

> **Submit button does nothing on the contact form**

### Why this matters
*Sets the stakes — why this work is worth doing now.*

*"Users can reach support without leaving the site"*

The contact form is the only path to support for users with
billing issues. Clicking Submit produces no visible response —
no success banner, no error, nothing. Anyone hitting a payment
problem is silently locked out of the channel that exists to
help them.

### Symptoms
*What the user observes.*

- Button visually depresses then springs back
- No success banner, no error message, no spinner
- Refreshing the page wipes the form — no draft preserved

### Repro
*How to trigger it.*

```
1. Open /contact in a fresh tab
2. Fill in the form with valid values
3. Click Submit
4. Observe: nothing changes on the page
```

### Expected vs actual
*The gap.*

- **Expected**: Form submits, success banner appears, message reaches support
- **Actual**: Nothing happens — no banner, no error, no email delivered

### Suspected causes
*Ordered by likelihood — assumptions to test, not commitments.*

1. The submit handler isn't bound to the button after a recent
   refactor moved it into a hook the button doesn't reference
2. Validation rejects the input silently — fails without
   surfacing the error to the UI
3. Long-shot: the form posts but the success handler swallows
   a 4xx response without showing it

### What we won't do
*Draws the line so scope doesn't creep.*

Not redesigning the form layout — fixing the submission path
only.

### Acceptance
*How we know it's fixed.*

- [ ] Submitting a valid form shows a success banner and
  delivers the message
- [ ] Submitting an invalid form shows the validation error
  inline
- [ ] Regression test (below) passes

### Regression test
*The test that would have caught this.*

`tests/contact-form.test.tsx::submits_and_shows_success` —
renders the form, fills valid input, clicks Submit, asserts
the success banner appears and the submit API was called.
Fails on the current code; passes after the fix.

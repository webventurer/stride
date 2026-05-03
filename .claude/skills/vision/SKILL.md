---
name: vision
description: Walk through writing a project Vision interactively. Asks seven questions one at a time (what it delivers / who it's for / why it exists / why now / how we know it's working / what can't change / what it won't do), drafts the file, shows it for approval, then writes VISION.md at the repo root. Triggers on "vision", "/vision", or when the user wants to bootstrap a new project's Vision document.
---

# /vision — author a project Vision

A Vision is the canonical "what is this project for" document. Written once, evolved sparingly. It frames everything downstream — every issue, every feature, every architectural decision should trace back to it.

This skill walks you through writing one. It interviews you on five questions, drafts the file, shows it for approval, then writes `VISION.md` at the repo root.

## When to use

- Starting a new project that doesn't yet have a Vision
- Bootstrapping a Vision for an existing project that grew up without one
- Any consumer repo where someone wants to capture product intent before writing more code

## When NOT to use

- The project already has a good `VISION.md` and the user just wants edits — go direct
- The user wants per-story scope — that's a Linear issue, not a Vision
- The user wants an implementation plan — that's `/linear:plan-work`, not this

---

## What goes in a Vision

Seven sections. Each answers one question. Keep it scannable — a Vision someone can't read in two minutes won't anchor anything.

| # | Section | Question it answers |
|:--|:--------|:--------------------|
| 1 | **What it delivers** | What does this project actually do? |
| 2 | **Who it's for** | Who specifically benefits? Who's it *not* for? |
| 3 | **Why it exists** | What's the motivation? |
| 4 | **Why now** | Why this moment? What changes if you wait? |
| 5 | **How we know it's working** | What can we tick off when delivered? |
| 6 | **What can't change** | Tech, platform, compliance — anything we have to respect |
| 7 | **What it won't do** | What's intentionally out of scope? |

---

## Steps

### 1. Check for existing VISION.md

If `VISION.md` already exists at the repo root, read it and show the user. Ask:

> "A `VISION.md` already exists. Replace it, edit it, or stop?"

- **Replace** — proceed with the interview, overwrite when done.
- **Edit** — switch to direct editing, skip the interview.
- **Stop** — exit cleanly.

### 2. Interview, one question at a time

<mark>**Don't dump all five questions at once.**</mark> Each answer informs the next prompt's nuance, and a single-shot questionnaire produces shallow answers.

#### Q1 — What it delivers

Ask:

> "**What** does this project deliver? One or two paragraphs. Aim for something a stakeholder who's never seen the code could understand."

Wait for the answer. Push back gently if it's vague or implementation-heavy ("a Python CLI" — that's *how*, not *what*).

#### Q2 — Who it's for

Ask:

> "**Who specifically benefits** when this lands? And just as important — who's it *not* for?"

Push back on "everyone" — that usually means "no-one in particular". A specific group with specific needs gives the project a real target; a generic audience gives planners no traction for trade-offs.

Asking this *before* Why is deliberate. A motivation only makes sense once you know whose motivation it is.

#### Q3 — Why it exists

Ask:

> "**Why** does this exist? What's the motivation — business, technical, personal? What changes when the project succeeds?"

The answer helps future planners make trade-offs. Push back if the answer is just "because we need it" — what would *not having it* cost?

#### Q4 — Why now

Ask:

> "**Why now?** What changes if you wait six months?"

If the answer is "nothing in particular", that's a signal to defer the project, not pretend it's urgent. A real *why now* names the trigger: a market shift, a deprecation, a window closing, a compounding cost.

#### Q5 — How we know it's working

Ask:

> "**How do we know it's working?** List 3–7 concrete, checkable criteria — things you could tick off when delivered. Examples: 'Sign-up completes in under 30 seconds end-to-end', 'Page loads in under 2 seconds on a 3G connection', 'CI runs in under 5 minutes'."

This is the most important section. Adjectives are the enemy of "done" — "fast", "good", "robust" never fail clearly, so they never trigger completion. Push back hard and ask for measurable conditions instead.

#### Q6 — What can't change

Ask:

> "**What can't change?** Tech stack, platform, compliance, deployment target — anything the project must respect."

Common: language choice, framework, runtime, hosted environment, regulatory rules, team expertise. An empty list is a valid answer if there genuinely are no hard constraints.

#### Q7 — What it won't do

Ask:

> "**What does this project explicitly *not* do?** This prevents scope creep down the line. What's intentionally out of bounds?"

Non-goals keep the project tight. Encourage at least 2–3.

### 3. Assemble the draft

Render all seven answers into this structure:

```markdown
# Vision: <project name>

## What it delivers

<answer to Q1>

## Who it's for

<answer to Q2>

## Why it exists

<answer to Q3>

## Why now

<answer to Q4>

## How we know it's working

- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>

## What can't change

- <constraint 1>
- <constraint 2>

## What it won't do

- <non-goal 1>
- <non-goal 2>
```

Show the assembled draft to the user.

### 4. Approval gate

Ask:

> "Does this look right? Approve to write `VISION.md`, or tell me what to change."

If the user requests changes, revise and re-show. Repeat until approved. Do not write the file before explicit approval.

### 5. Write the file

On approval, write `VISION.md` to the repo root.

If a file existed before and the user chose "replace", overwrite it. If creating fresh, write a new file.

Confirm:

> "Written `VISION.md` at the repo root.
>
> This is the project's anchor — every issue, every feature, every architectural decision should trace back here."

### 6. Final torch

Close with two reminders:

> <mark>**Adjectives are the enemy of done.**</mark> "Fast", "good", "easy" never fail clearly, so they never trigger completion — the project drifts past the point of value. Re-read the Success Criteria you just wrote — would you know how to verify each one?
>
> **The Vision is the only artefact downstream tooling carries forward.** Anything you didn't write here, future planners and agents have to invent. Be explicit about what matters.

---

## Behaviour notes

- **Don't draft from your own context.** The user's answers are the raw material. Synthesising "what the project probably wants" is the wrong job — the act of articulating is the value, and a Vision the user didn't write themselves won't anchor them.
- **Push back on vagueness.** Especially on Success Criteria. Better to spend two extra questions than ship a Vision that lets everything count as success.
- **Keep it short.** A 200-word Vision the user actually re-reads beats a 2000-word one they wrote once and forgot.
- **Outcome-shaped, not implementation-shaped.** The What section describes what changes for the user, not what's in the codebase. "Atomic commits without leaving Claude Code" beats "a CLI built in Node" — the latter is a constraint, not a what.
- **One overwrite confirmation per session.** If `VISION.md` already exists and the user chose Replace, don't ask again at write-time.

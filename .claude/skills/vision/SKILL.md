---
name: vision
description: Walk through writing a project Vision interactively. Two modes — short (one question, ~2 minutes, CRAFT-assembled) for small projects, or full (seven questions covering what it delivers / who it's for / why it exists / why now / how we know it's working / what can't change / what it won't do) for substantial products. Drafts the file, shows it for approval, then writes VISION.md at the repo root. Triggers on "vision", "/vision", or when the user wants to bootstrap a new project's Vision document.
---

# /vision — author a project Vision

A Vision is the canonical "what is this project for" document. Written once, evolved sparingly.

A good Vision is **load-bearing**: it anchors decisions, names the constraints, and refuses to drift into adjective soup. Iterations sharpen it; they don't bloat it. Future-you, a future agent, or a new contributor should be able to read it in 2–3 minutes and know what the project is, who it's for, and what it won't do.

Every issue, every feature, every architectural decision traces back to it.

This skill walks you through writing one. It offers two modes — **short** (one question, ~2 minutes, suitable for small projects or side-tools) and **full** (seven questions, ~15 minutes, the load-bearing path for substantial products). Either way it drafts the file, shows it for approval, then writes `VISION.md` at the repo root.

## When to use

- Starting a new project that doesn't yet have a Vision
- Bootstrapping a Vision for an existing project that grew up without one
- Any consumer repo where someone wants to capture product intent before writing more code

Pick **short mode** when the work is a small dashboard, a side-tool, or anything where the seven-question interview would feel disproportionate to what you're shipping. Pick **full mode** for substantial products where the act of articulating each section is itself the value.

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
| 5 | **Success criteria** | What can we tick off when delivered? |
| 6 | **What can't change** | Tech, platform, compliance — anything we have to respect |
| 7 | **What it won't do** | What's intentionally out of scope? |

Both modes produce the same seven sections. Short mode infers most of them from a single rich answer; full mode interviews you on each one.

---

## Steps

### 1. Check for existing VISION.md

If `VISION.md` already exists at the repo root, read it and show the user. Ask:

> "A `VISION.md` already exists. Replace it, edit it, or stop?"

- **Replace** — proceed with the interview, overwrite when done.
- **Edit** — switch to direct editing, skip the interview.
- **Stop** — exit cleanly.

### 2. Choose mode — short or full

<mark>**This is a forced gate, not a flag.**</mark> Before any question is asked, prompt the user:

> "Two modes:
>
> - **Short Vision** — one question, ~2 minutes, CRAFT-assembled. For small projects, side-tools, dashboards.
> - **Full Vision** — seven questions, ~15 minutes, one at a time. For substantial products where the act of articulating each section is the value.
>
> Which one?"

The choice is forced — there's no flag, no default-pick, no way to skip past it into the seven-question path by accident. Every user makes the size-of-work call deliberately.

**Why a forced gate, not a flag.** A flag (`--short`) lets users default-skip the choice — they'd run `/vision`, get the seven-question path by inertia, suffer through, and never discover short mode existed. The gate makes the decision *visible* at the moment it matters. Recurrence-reveals-reality: small-project friction recurs, so the gate that addresses it has to fire reliably, not behind an opt-in flag.

Carry the chosen mode as context into step 3a or 3b.

### 3a. Short mode — one question, CRAFT-assembled

*Run this step only if "short" was chosen in step 2. Otherwise skip to step 3b.*

Ask:

> "Tell me about this project: what does it deliver, who is it for, and how will you know it's working? A paragraph or two is enough."

Wait for the user's answer. Push back gently if it's a single line — short mode still needs enough substance to fill seven sections. *"A todo app for me"* isn't enough; *"A todo app I run from the terminal — it's for me, just as a way to learn Rust, and I'll know it's working when I'm using it daily for two weeks"* is.

With the answer in hand, **assemble the full Vision draft via CRAFT**:

- For each of the seven sections, lift content where the answer covers it. *What it delivers* and *Who it's for* are usually direct lifts; *Success criteria* extracts from the *"how will you know"* part.
- For sections the answer doesn't cover (*Why it exists*, *Why now*, *What can't change*, *What it won't do*), draft plausible content from the substance of the answer and mark each inferred section with a `<!-- inferred — adjust as needed -->` comment so the user knows what to verify at the approval gate.
- Keep adjectives out of *Success criteria* — render the criteria measurably even when the user gave a vague answer. If the answer doesn't yield measurable criteria, push back at the approval gate.

Hand the assembled draft to step 4. The user reviews and edits at the approval gate.

### 3b. Full mode — seven questions, one at a time

*Run this step only if "full" was chosen in step 2.*

Open with the upfront disclosure — count, time estimate, skip affordance:

> "I'll ask 7 questions about the project — should take ~5 minutes. Type `skip` on any question to leave it blank for later."

<mark>**Don't dump all seven questions at once.**</mark> Each answer informs the next prompt's nuance, and a single-shot questionnaire produces shallow answers.

**Skip handling.** When the user's answer to any question is the single word `skip` (case-insensitive), treat it as an explicit skip:

- Don't push back, don't re-prompt — move directly to the next question.
- Track the question number as skipped (for surfacing at the approval gate in step 5).
- In step 4's assembled draft, render that section's content as `_TBD — answer later via /vision_` instead of the missing answer.

#### Q1 — What it delivers

Ask:

> "(1/7) **What** does this project deliver? One or two paragraphs. Aim for something a stakeholder who's never seen the code could understand."

Wait for the answer. Push back gently if it's vague or implementation-heavy ("a Python CLI" — that's *how*, not *what*).

#### Q2 — Who it's for

Ask:

> "(2/7) **Who specifically benefits** when this lands? And just as important — who's it *not* for?"

Push back on "everyone" — that usually means "no-one in particular". A specific group with specific needs gives the project a real target; a generic audience gives planners no traction for trade-offs.

Asking this *before* Why is deliberate. A motivation only makes sense once you know whose motivation it is.

#### Q3 — Why it exists

Ask:

> "(3/7) **Why** does this exist? What's the motivation — business, technical, personal? What changes when the project succeeds?"

The answer helps future planners make trade-offs. Push back if the answer is just "because we need it" — what would *not having it* cost?

#### Q4 — Why now

Ask:

> "(4/7) **Why now?** What changes if you wait six months?"

If the answer is "nothing in particular", that's a signal to defer the project, not pretend it's urgent. A real *why now* names the trigger: a market shift, a deprecation, a window closing, a compounding cost.

#### Q5 — Success criteria

Ask:

> "(5/7) **How do we know it's working?** List 3–7 concrete, checkable criteria — things you could tick off when delivered. Examples: 'Sign-up completes in under 30 seconds end-to-end', 'Page loads in under 2 seconds on a 3G connection', 'CI runs in under 5 minutes'."

This is the most important section. Adjectives are the enemy of "done" — "fast", "good", "robust" never fail clearly, so they never trigger completion. Push back hard and ask for measurable conditions instead.

#### Q6 — What can't change

Ask:

> "(6/7) **What can't change?** Tech stack, platform, compliance, deployment target — anything the project must respect."

Common: language choice, framework, runtime, hosted environment, regulatory rules, team expertise. An empty list is a valid answer if there genuinely are no hard constraints.

#### Q7 — What it won't do

Ask:

> "(7/7) **What does this project explicitly *not* do?** This prevents scope creep down the line. What's intentionally out of bounds?"

Non-goals keep the project tight. Encourage at least 2–3.

### 4. Assemble the draft

Render the seven answers (full mode) or use the CRAFT-assembled draft (short mode) into this structure:

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

## Success criteria

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

### 5. Approval gate

Ask:

> "Does this look right? Approve to write `VISION.md`, or tell me what to change."

If the user requests changes, revise and re-show. Repeat until approved. Do not write the file before explicit approval.

For short-mode drafts, draw the user's attention to any sections marked `<!-- inferred — adjust as needed -->` — those are the highest-value review targets.

For full-mode drafts where the user skipped one or more questions, surface the skipped sections before asking for approval:

> "You skipped: Q3 (Why it exists), Q6 (What can't change). Continue and write `VISION.md` with `_TBD_` placeholders, or fill them in now?"

If the user picks *fill in now*, ask the skipped questions in order; otherwise continue to step 6 with the placeholders intact. Re-running `/vision` later in edit mode lets the user fill them in any time.

### 6. Write the file

On approval, write `VISION.md` to the repo root.

If a file existed before and the user chose "replace", overwrite it. If creating fresh, write a new file.

Confirm:

> "Written `VISION.md` at the repo root.
>
> This is the project's anchor — every issue, every feature, every architectural decision should trace back here."

### 7. Sync to Linear (gated)

Once `VISION.md` is on disk, ask:

> "Push this Vision to the Linear project description now? (y/n)"

- **Yes** → invoke [`/linear:update-vision`](../../commands/linear/update-vision.md). That command runs its own diff-and-confirm gate, so the user reviews the actual diff before anything writes to Linear. When `/linear:update-vision` finishes (whether it wrote, declined the diff, or short-circuited as identical), continue to step 8.
- **No** → skip Linear sync. Surface a one-line hint and continue to step 8:

  > *"Run `/linear:update-vision` whenever you're ready to push."*

**Failure handling.** If `/linear:update-vision` errors out (`.linear_project` missing, project not found, `save_project` fails), do not abort `/vision`. The file *was* written successfully — that's the primary deliverable. Surface the failure clearly, name the retry path, and continue to step 8:

> *"Vision was written to `VISION.md`. Linear sync failed: `<error>`. Run `/linear:update-vision` after fixing to retry."*

The two gates are different decisions: this step's gate asks *"engage with Linear sync at all?"*; `/linear:update-vision`'s internal gate asks *"here's the actual diff, confirm?"*. Both stay — one decides scope, the other reviews content.

### 8. Final torch

Close with two reminders:

> <mark>**Adjectives are the enemy of done.**</mark> "Fast", "good", "easy" never fail clearly, so they never trigger completion — the project drifts past the point of value. Re-read the Success criteria you just wrote — would you know how to verify each one?
>
> **The Vision is the only artefact downstream tooling carries forward.** Anything you didn't write here, future planners and agents have to invent. Be explicit about what matters.

If the project graduates from a small side-tool to something more substantial later, re-run `/vision` and pick **full** to deepen the Vision. The existing Replace/Edit/Stop prompt handles the upgrade.

---

## Behaviour notes

- **Don't draft from your own context.** The user's answers are the raw material. Synthesising "what the project probably wants" is the wrong job — the act of articulating is the value, and a Vision the user didn't write themselves won't anchor them. *(Short mode does fill in some sections from a single answer — that's the calibrated trade-off, not licence to invent content the user never gave.)*
- **Push back on vagueness.** Especially on Success criteria. Better to spend two extra questions than ship a Vision that lets everything count as success.
- **Keep it short.** A 200-word Vision the user actually re-reads beats a 2000-word one they wrote once and forgot.
- **Outcome-shaped, not implementation-shaped.** The What section describes what changes for the user, not what's in the codebase. "Atomic commits without leaving Claude Code" beats "a CLI built in Node" — the latter is a constraint, not a what.
- **One overwrite confirmation per session.** If `VISION.md` already exists and the user chose Replace, don't ask again at write-time.

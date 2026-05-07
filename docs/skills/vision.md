# /vision — Project vision

<div class="image-row">

<div>

A Vision is the canonical "what is this project for" document. Written once, evolved sparingly. It's the anchor every issue, every feature, and every architectural decision should trace back to.

`/vision` walks you through writing one. It interviews you on seven questions one at a time, drafts the file, shows it for approval, then writes `VISION.md` at the repo root.

*Vision sits above the loop — issues, features, and architectural decisions trace back to it.*

</div>

<div>

![Vision lightbulb](/lightbulb.svg)

</div>

</div>


## When to use

- Starting a new project that doesn't yet have a Vision
- Bootstrapping a Vision for an existing project that grew up without one
- Any consumer repo where someone wants to capture product intent before writing more code

## When NOT to use

- The project already has a good `VISION.md` and you just want edits — go direct
- You want per-story scope — that's a Linear issue, not a Vision
- You want an implementation plan — that's [`/linear:plan-work`](/skills/linear#linearplan-work), not this

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

Seven sections is heavier than the standard five-section product vision template (Pichler, Moore). The three additions — *Why now*, *What can't change*, *What it won't do* — exist so the Vision can do double duty as a planning anchor for `/linear:*`, not just a stakeholder pitch.

## How it works

`/vision` is an interactive interview, not a fill-in-the-blanks form. <mark>**Each answer informs the next prompt's nuance** — a single-shot questionnaire produces shallow answers.</mark>

1. Greets you and explains what a Vision is for
2. Asks the seven questions one at a time, pushing back on vagueness
3. Assembles the draft and shows it for review
4. Writes `VISION.md` at the repo root only after explicit approval
5. Closes with two reminders — the adjective trap, and the "downstream tooling carries this forward" point

If a `VISION.md` already exists, the skill asks before overwriting.

## Why the order matters

The seven questions aren't a list of fields — they're a sequence designed so each answer sharpens the next.

| Question | Why this position |
|:---------|:------------------|
| **What it delivers** *first* | Forces an outcome-shaped statement before anyone reaches for implementation language |
| **Who it's for** *before Why* | A motivation only makes sense once you know whose motivation it is |
| **Why it exists** *before Why now* | Establishes the standing reason before you ask about timing |
| **Why now** *as its own section* | Most templates skip this. Without it, "we should build this" reads as evergreen — which means it's never urgent |
| **Success criteria** *before constraints* | Forces measurable outcomes before talk of limits softens what "done" means |
| **What can't change** *near the end* | Constraints land more honestly once you've written the desired outcome |
| **What it won't do** *last* | Non-goals are the easiest to defer until you've named the actual goal |

## The hard part — measurable success criteria

The Success criteria section is where most Vision documents drift. <mark>**Adjectives are the enemy of done.**</mark> "Fast", "good", "easy", "robust" never fail clearly, so they never trigger completion — and the project drifts past the point of value.

| Vague (avoid) | Measurable (use) |
|:--------------|:-----------------|
| The site is fast | Page loads in under 2 seconds on a 3G connection |
| Sign-up is easy | Sign-up completes in under 30 seconds end-to-end |
| The build is reliable | CI runs in under 5 minutes, fails on first error |
| Tests catch regressions | `git bisect` finds a regression in fewer than 5 commits |

If you can't tell whether a criterion has been met, it can't trigger "done". Re-read your Success criteria — would you know how to verify each one?

## Where Vision sits in stride

Vision is the **guiding light**. Functionally, that makes it stride's upstream anchor — every skill below reads `VISION.md` before deciding anything, so the work flows from a single source of intent:

| Layer | What it does | What anchors it |
|:------|:-------------|:----------------|
| **Vision** | What this project is for | (the user's intent, captured once) |
| **/craft** | Sharpens a problem into a clear prompt | The Vision tells you what problems are in scope |
| **/linear** | Turns problems into tracked issues, branches, PRs | Issue titles trace back to Vision outcomes |
| **/commit** | Records each change as one atomic, revertible unit | The branch the commits live on traces back to a Vision-aligned issue |

Without a Vision, everything downstream has to reinvent "what is this project for" from thin context. With one, every issue title can be measured against it, every feature decision has an anchor, and future planners — human or AI — inherit your reasoning.

## What a good Vision looks like

stride's own `VISION.md` (at the repo root) is a worked example. Read it and notice:

- The **What it delivers** opens with a stakeholder-readable line ("Manage your own dev team on a Kanban board so everything's visible — except the team is AI"), then explains the mechanics
- **Who it's for** is sharp — "developers using Claude Code who care about codebases that survive past day 30" — and explicitly names who it's *not* for
- **Success criteria** has six measurable criteria, every one verifiable
- **What it won't do** lists five hard non-goals, each starting with "Not a..."

A Vision the user actually re-reads is worth more than a 2000-word one written once and forgotten. Aim for something that fits on a single screen.

## Under the hood

This page is the human-readable overview. The full agent specification — including the interview pacing rules, the push-back-on-vagueness behaviour, and the assemble-then-approve gate — lives in `.claude/skills/vision/SKILL.md` inside your project after [installation](/install). That file is what the agent actually follows when you run `/vision`.

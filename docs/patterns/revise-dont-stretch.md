# Revise, don't stretch

> When the Vision-trace feels strained at `/linear:plan-work` draft time, **revise the trace — don't stretch it.**

## The recognised situation

You're drafting an issue at `/linear:plan-work` time. The "Why this matters" section needs to name a Vision Success criterion the work serves. The candidate criterion fits — but only with bridging language. You're writing *"this serves [X] indirectly"* or *"also touches [Y]"* or *"this loosely advances [Z]"*. The trace works on paper; the strain is real.

## The move

Pause. Re-read [`VISION.md`](https://github.com/webventurer/stride/blob/main/VISION.md), Success criteria especially. Look for a criterion that fits *more directly*. Revise the candidate trace toward it.

Two outcomes:

| Outcome | What happens |
|:--|:--|
| **Revised trace lands cleanly** | Use it. Note in the draft *why* the better fit was missed first time — Vision evolved since you last absorbed it, earlier scan missed it, etc. |
| **Revision can't find a clean fit** | Surface the strain to the user honestly. Follow `/linear:plan-work`'s existing *can't-trace* path: add a new criterion to `VISION.md` (re-run `/vision`), or drop the issue as out of scope |

## Why this is the right move

Strained traces look like compliance but are **drift**. The Vision-anchor mechanic only works if the trace is honest — a fictional anchor on the board makes the gate ceremony, not signal.

Catching at draft time is cheap; revising one section beats shipping with a fictional anchor. `/linear:finish`'s Vision-confirm step is the backup catch, but it's rarer (post-merge), and in some flows the drift isn't caught at all.

The Vision evolves with the work — newer criteria sometimes fit better than ones you scanned first. The trace you reach for first may have been overtaken by a more direct one mid-stream.

## Worked example: WB-301

At `/linear:plan-work` draft time, the agent traced WB-301 to:

1. *"The card moves through Backlog → Doing → In Review → Done as `/linear:*` runs"*
2. *"Issue titles read as stakeholder outcomes, not implementation steps"*

Both fit, but only with bridging — neither directly named what the work was about.

At `/linear:finish` (with the Vision-confirm step live), the user named the actual shift: the work served the *newer* criterion *"The common path through every `/linear:*` command runs without prompts; interruptions appear only when stride detects friction worth the user's judgement"* — added to `VISION.md` mid-stream during the friction-calibration work.

The original trace was strained because **the Vision had evolved** between the draft and the finish. The agent's first-pass scan reached for criteria that were in scope when it last absorbed the Vision, not what fit best now.

Applied retroactively, the strain test trips on signal (a) — the trace was hedged across two criteria with no single direct fit. A re-read of `VISION.md` would have surfaced the newer criterion.

## The strain test

Three signals — quick read, not a checklist. If any one trips, pause and revise.

| Signal | What it looks like |
|:--|:--|
| **Hedge** | You wrote *"this serves [X] indirectly"*, *"also serves"*, *"this loosely advances"* — anything that softens the trace |
| **Length-disproportion** | The trace takes more sentences than *"What we'll do"* — you're explaining the connection harder than the work itself |
| **Force-fit scanning** | You're going line-by-line through the criteria looking for one that *could* be made to fit, instead of one that *does* fit |

## What this Pattern is *not*

- **Not licence to keep revising until perfect.** First-fit is good enough by default. Revision fires when the strain test trips, not as a routine extra pass.
- **Not a gate or auto-detector.** No prompt, no scoring, no auto re-scan trigger. The Pattern relies on the drafter noticing strain and reaching for this doc. The friction is yours to read; the doc names what to do once you've read it.
- **Not a replacement for** `/linear:finish`'s Vision-confirm step. Both catch drift — this catches at draft time (cheap), the confirm step catches at merge time (backup).

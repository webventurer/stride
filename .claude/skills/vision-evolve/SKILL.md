---
name: vision-evolve
description: Tend a Vision that already exists — add a line, reword one, or fold overlapping lines together — so VISION.md stays a true guide as the work grows. Use when work fits no Success criterion, when two criteria overlap, or when a line no longer says what the project delivers. Triggers on "vision-evolve", "/vision-evolve", "evolve the Vision", "update the Vision", "add a Success criterion".
---

# /vision-evolve — tend an existing Vision

A Vision only stays a true guide if it is tended as the work grows. `/vision` writes one for the first time; this skill looks after it from then on: adding a line, rewording one, or folding lines together. [Revise, don't stretch](https://github.com/webventurer/stride/blob/main/docs/patterns/revise-dont-stretch.md) and [the Vision evolves with the work](https://github.com/webventurer/stride/blob/main/docs/patterns/vision-evolves-with-the-work.md) hold the thinking behind it.

## The principle

**The Vision is a true account of what the project is for, kept true as the work grows.**

Anyone reading `VISION.md` should be able to trust two things: every line names something the project really delivers, and every piece of work traces honestly to one of them. When either stops being true, the Vision is no longer a guide, only a document. Everything below serves that one aim; read the Vision, judge what keeps it true, and keep the change small.

## How it plays out

These guidelines are what the principle usually asks for. When a case fits none of them, go back to the principle.

### A line says something true and useful about what the project delivers

A Success criterion is a promise the project can be checked against. It names an outcome someone could see, in words a reader who has never seen the code understands. A line that is vague, true of any project, or true only of the code's shape says nothing, so reword it or remove it.

### Work that fits no line means the Vision has grown

When the closest line only fits if you stretch what it says, the Vision is missing a line. Grow it honestly. Squeezing the work into a line that doesn't cover it leaves a record that says the work was verified when it wasn't, and the next reader trusts a trace that isn't true.

### Lines that overlap become one stronger line

Two lines that say nearly the same thing split the work between them, and nobody can say which one a card serves. Fold them into one line that keeps what each was for. If an addition would overlap an existing line, reword that line instead of adding a second.

### A line written only to justify one card isn't useful

A line that restates the card in hand will never apply to a second card. Name the lasting outcome the work reveals, the thing the project is now committed to, and write that. Ask whether a card next month that has nothing to do with this one could still be filed against the line.

### The agent owns this upkeep, and needs no sign-off

Tending the Vision is part of the work, in interactive and unattended mode alike. Change `VISION.md` yourself, then tell the user what you changed and why in one plain sentence, and carry on. Don't stop to ask whether the new line is wanted, and don't hand the edit back to the user.

## Where the change goes

- Edit `VISION.md` on the branch that revealed the gap, and commit the Vision change on its own with `/commit`, so the history shows when the Vision moved and why.
- Re-run the check that fired, such as the trace in `/linear:finish` or `/linear:quick`. It should now pass against the changed line, and the work carries on from there.

## Copy the change to Linear

Once `VISION.md` is saved, copy it to the Linear project page with [`/linear:update-vision`](../../commands/linear/update-vision.md). Don't ask the user to confirm the difference first: the Vision was changed by the work, and the copy simply follows it. When the repo has no `.stride.json`, or the Linear write fails, keep the saved `VISION.md` and say the Linear copy was skipped.

## When NOT to use

- The project has no `VISION.md` yet: use `/vision` to write the first one.
- The work doesn't belong in this project at all: drop the card as out of scope instead of growing the Vision to hold it.

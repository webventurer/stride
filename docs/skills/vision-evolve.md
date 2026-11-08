# /vision-evolve — Tend the Vision

A Vision only stays a true guide if it is tended as the work grows. [`/vision`](/skills/vision) writes one for the first time. `/vision-evolve` looks after it from then on: adding a line, rewording one, or folding lines together.

The agent runs it when work fits no Success criterion, in `/linear:finish`, `/linear:quick` and `/linear:plan-work`. You can also run it yourself whenever a line no longer says what the project delivers.

## The principles

It is written as principles, not steps. The agent applies them with judgement and keeps each change small.

- **A line says something true and useful about what the project delivers.** A Success criterion names an outcome someone could see, in words a reader who has never seen the code understands.
- **Work that fits no line means the Vision has grown.** Grow it honestly. Squeezing the work into a line that doesn't cover it leaves a trace that says the work was verified when it wasn't.
- **Lines that overlap become one stronger line.** Two lines that say nearly the same thing leave nobody sure which one a card serves.
- **A line written only to justify one card isn't useful.** It should name the lasting outcome the work reveals, so a later card with nothing to do with this one could still be filed against it.
- **The agent owns this upkeep, and needs no sign-off.** That holds in interactive and unattended mode alike. The agent changes `VISION.md`, tells you what it changed, and carries on.

## Where the change goes

The Vision change is committed on its own, on the branch that revealed the gap, so the history shows when the Vision moved and why. The check that fired is run again and now passes.

Once `VISION.md` is saved, the agent copies it to the Linear project page with [`/linear:update-vision`](/skills/linear#linearupdate-vision), without asking you to confirm the difference. When the repo has no `.stride.json`, or the Linear write fails, `VISION.md` stays saved and the agent says the Linear copy was skipped.

## When NOT to use

- The project has no `VISION.md` yet. Use [`/vision`](/skills/vision) to write the first one.
- The work doesn't belong in this project at all. Drop the card as out of scope instead of growing the Vision to hold it.

The thinking behind it lives in two patterns: [revise, don't stretch](/patterns/revise-dont-stretch) and [the Vision evolves with the work](/patterns/vision-evolves-with-the-work).

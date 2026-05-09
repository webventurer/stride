# New issue, not new scope

> When work appears mid-flight that wasn't in scope, draft it as its own issue via `/linear:plan-work`. **Don't expand the current one.**

## The recognised situation

You're working through issue X. Mid-implementation, mid-review, mid-PR — something else surfaces. A subtle bug spotted while writing tests. A doc that should be touched. A related improvement that *"would be small to add."*

The temptation: *"I'm already in here. Let me just expand the scope of issue X to cover it."*

That feels efficient. It isn't.

## The move

Open a fresh `/linear:plan-work` for the new work. Let it sit in Backlog. Continue with X.

The new issue waits its turn. The current issue ships clean. The git log stays narratable. The kanban board stays honest. Each piece earns its place — including the new piece, but as its own piece, not glued onto another.

## Why this is the right move

| Absorb (tempting) | Separate (right) |
|:--|:--|
| Issue X grows an extra purpose mid-flight | Issue X ships its one purpose; new work waits in Backlog |
| Commits join with `"and"` to cover both purposes | Commits stay atomic — one purpose per commit |
| PR review covers two threads at once | PR review covers one thread, cleanly |
| Title rewrites to *"Do X **and** Y"* | Title stays as the original outcome |
| Future `git bisect` finds two changes per commit | `git bisect` lands on the one change that broke things |

The downstream cost of scope creep compounds: atomic commits depend on atomic issues; narratable logs depend on atomic commits; reviewable PRs depend on narratable diffs; debuggability depends on reviewable PRs. One absorbed scope ripples through all four layers.

## Worked example: the WB-308 split

Mid-session, while running `/linear:finish` on WB-297 (the friction Distinction doc), the agent surfaced a Vision-trace drift in stride-internal jargon. The user pushed back: *"can you say in plain English."* The plain-English version landed cleanly — but it surfaced a wider problem: the drift output should always read in plain English, not just when prompted.

The temptation: expand WB-297 to also fix the drift output's readability. *"I'm already editing `finish.md` — one more change won't hurt."*

The move: file WB-308 *"/linear:finish drift output reads in plain English"* as its own card. WB-297 shipped its one purpose (the friction Distinction lives in docs); WB-308 became the next deliverable. Both git logs stayed atomic. Both PRs reviewed cleanly.

The cost of doing this *the other way* — absorbing WB-308 into WB-297 — would have been hidden but real: the merge commit subject would have to read *"Add friction Distinction **and** make drift output plain-English"*, the trace-back would have to span two unrelated criteria, and any future `git bisect` looking for a regression in either change would land on the same commit.

## The "and" test

If you can't describe the expanded scope without joining ideas with *"and"*, you're holding two purposes in one issue. Split before the description goes to Linear.

This is the same shape as `/commit`'s subject-line rule (*"if your commit message contains 'and', you probably have two commits"*) — applied one level up. Issues are the *upstream* of commits; the *"and"* test catches the same problem before it cascades.

## What this Pattern is *not*

- **Not "never combine related work."** Genuinely inseparable pieces — a rename plus every call site, a deletion plus its cleanup, tests for new code — are *one* atomic change. See [*Patterns that DO belong together*](https://github.com/webventurer/stride/blob/main/.claude/skills/commit/SKILL.md) in `/commit`'s docs for the exception. The test: would splitting the work leave any intermediate state non-working? If yes, it belongs together. If no, it splits.
- **Not a way to defer real planning.** The new issue still goes through `/linear:plan-work` properly — Vision trace, *Why this matters*, *What we'll do*, the lot. *"Park it as a card"* doesn't mean *"file a one-line stub."*
- **Not a license to file every passing thought.** The Pattern fires when work surfaces that you'd otherwise *do right now*. If the thought is *"someday it'd be nice if..."*, that's not scope creep — that's brainstorming. The Pattern is for the moment of temptation, not the moment of musing.

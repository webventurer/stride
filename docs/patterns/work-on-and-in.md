# Work on the project, in the project

> **Use stride to build stride.** The fastest way to find what stride should fix next is to *use* stride for real work — the friction you hit while working *in* the project is the highest-signal source of work *on* the project.

## The recognised situation

You're using stride for its intended job — running `/linear:list-projects`, shipping through `/linear:start` → `/linear:finish`, filing cards. Mid-flow, the tool itself does something wrong: a command prints a wall of blanks, a step references a file that doesn't exist, a re-install leaves duplicates.

The temptation is to treat that as an interruption — a distraction from "the real work". It's the opposite. **That friction is the real work, surfacing itself.** You didn't have to audit the tool in the abstract to find the gap; using it for something real handed you the gap, with a reproduction case already in hand.

## The two loops

| Loop | What you're doing | Example from a real session |
|:--|:--|:--|
| **In the project** | Using stride for actual work | Running `/linear:list-projects` to see the workspace |
| **On the project** | Improving stride itself | Fixing the query so the command fills its documented columns |

The loops feed each other. Working *in* the project surfaces what to fix *on* it; fixing it makes the next pass *in* smoother. Neither loop alone produces this — an abstract audit *on* the project guesses at problems; using it *in* the project without acting *on* the friction just tolerates the same papercut forever.

## The move

When using stride surfaces a flaw in stride:

1. **Don't push through the friction.** Name it — it's data, not noise ([friction is information](./friction-distinction)).
2. **File it as it stands.** A new issue, not absorbed into whatever you were doing ([new issue, not new scope](./new-issue-not-new-scope)).
3. **Fix it in the same working rhythm** — `/linear:quick` for an obvious one-scroll fix, `/linear:plan-work` when it crosses files or contracts.
4. **Let the Vision grow if the flaw reveals a missing outcome** — on the same branch as the fix ([Vision evolves with the work](./vision-evolves-with-the-work)).

The reproduction case is free: you just hit it. The motivation is concrete: it annoyed *you*, doing *real* work. That beats any speculative backlog.

## Why this composes the other patterns

This is the upstream frame the other three patterns hang off — it says *run the loop deliberately*, then hands off:

| Pattern | Where it fires in the loop |
|:--|:--|
| [Friction is information](./friction-distinction) | The instant you hit the flaw — is this signal, or a use-case mismatch? |
| [New issue, not new scope](./new-issue-not-new-scope) | Once it's signal — capture it without derailing the current work |
| [Vision evolves with the work](./vision-evolves-with-the-work) | If the flaw exposes an outcome the Vision never named |

Reading them in isolation, you might wait for friction to find you. This pattern says: **put yourself in the friction on purpose.** Dogfood the tool on real work, and the backlog writes itself from what actually broke.

## What this is *not*

- **Not licence to yak-shave.** Surfacing a flaw mid-flow doesn't mean fixing it mid-flow. File it; fix it in its own atomic unit. The *discovery* is opportunistic; the *fix* stays disciplined.
- **Not a substitute for the Vision.** The loop tells you what's broken *today*; the Vision says what the project is *for*. A flaw worth fixing still has to trace to an outcome — using the tool doesn't exempt the fix from the trace gate.
- **Not "every annoyance is a bug".** Some friction is the guardrail working as designed. The [friction Distinction](./friction-distinction) is the test for which is which — run it before you file.
- **Not unique to stride's maintainers.** Any consumer building *their* project with stride hits the same loop: real work surfaces what their setup, their Vision, or their board needs next.

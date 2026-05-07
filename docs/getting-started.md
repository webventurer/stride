# Getting started

<mark>**Vision sets the destination, Linear runs the trip, `/commit` records each step.**</mark>

> New here? Start with [Why Stride?](/why-stride) first — this page assumes you've decided.

## Vision — the guiding light

Before the loop, there's a question the loop can't answer: **what is this project for?**

[`/vision`](/skills/vision) walks you through writing a `VISION.md` — seven questions, one at a time, drafted and approved before it lands at the repo root. Without it, every planner — human or AI — has to reinvent "what's this project for" from thin context. With it, the rest of stride has something concrete to measure against.

Functionally, Vision is stride's *upstream anchor* — planning, ranking, and implementation all read it before deciding anything. You only run `/vision` once per project, then evolve it sparingly. The three loop skills below are how stride executes against the Vision.

## Linear integration

![Kanban board](/kanban-board.svg)
*Issues flow from Backlog through Doing to Done, driven entirely by `/linear` commands.*

The `/linear` commands connect your development workflow directly to [Linear](https://linear.app). This is an opinionated choice — Linear is keyboard-driven, git-integrated, and built for the way modern software teams actually work. No drag-and-drop boards, no workflow bloat.

Rather than context-switching between your editor and a browser, you can plan work, create issues, implement features, handle PR feedback, and close issues — all from within Claude Code. The five commands cover the **full development lifecycle**: from researching a problem and writing a well-structured issue, through to merging an approved pull request and marking it done.

This keeps the agent *grounded in real project priorities* rather than working in isolation.

### Stories and epics

Most issues are **stories** — one deliverable, ships as one PR. When several stories serve a common purpose (bigger than a PR, smaller than the Vision), `/linear:plan-work` groups them under a parent **epic** card with sub-issues nested below. The umbrella moves through the kanban lanes alongside its sub-issues, so a non-engineer scanning the board sees the whole shape. See [Epics and stories](/reference/epics-and-user-stories) for the mechanism.

## Atomic commits — the per-change discipline

Inside the Linear flow, every commit point calls `/commit`. That's where the per-change discipline lives — atomic commits that keep the git history readable, revertible, and bisectable.

Agents can produce large volumes of changes in a single session. Without discipline, those changes land as **monolithic commits** — impossible to review, difficult to revert, and dangerous to bisect. Atomic commits solve this by ensuring every commit contains *exactly one complete logical change*.

The `/commit` skill encodes a **four-pass methodology** that separates content decisions from formatting standards. It catches the specific atomicity mistakes that AI agents make — grouping by session, by shared prefix, or by proximity rather than by purpose. Each commit becomes independently revertible, clearly explained, and safe to ship.

## The loop

The three skills aren't independent — they're stages in the same loop, and each one makes the next one better.

1. **`/craft`** sharpens the problem — structured prompt generation that turns a vague idea into a clear description *before* the agent starts work
2. **`/linear`** turns that description into a tracked issue, then manages the full lifecycle — branching, implementation, PR, review, merge
3. **`/commit`** is called at every commit point within `/linear` to keep the git history atomic — one complete logical change per commit, independently revertible

Remove any piece and the loop still works, but the output gets worse. Without `/craft`, the agent works from whatever you typed. Without `/commit`, the agent dumps everything into monolithic commits. Without `/linear`, the agent works in isolation with no connection to project priorities.

> "When faced with two or more alternatives that deliver roughly the same value, **take the path that makes future change easier**." — David Thomas & Andrew Hunt, *The Pragmatic Programmer*

Vibe coding produces code. [Agentic engineering](/reference/agentic-engineering) produces **a traceable, reversible, purposeful history of decisions** — every change is atomic, every change is tied to an objective, and the agent operates with the discipline of a senior engineer rather than the enthusiasm of an intern with root access.

The approach is designed to compound: as AI models improve, the structured documentation gets more from them, not less.

## Next steps

- [How it works](/how-it-works) — see what gets installed and how the pieces connect
- [Install stride](/install) into your project
- Anchor the project with [/vision](/skills/vision)
- Learn about [atomic commits](/skills/commit)
- Set up the [Linear workflow](/skills/linear)
- Generate better prompts with [/craft](/skills/craft)

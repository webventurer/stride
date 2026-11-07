# CLAUDE.md

This file shapes behaviour on every turn. Discoverable details (commands, architecture, tech stack) live in `README.md` and `docs/` — only durable rules belong here.

## The principle

**Speed up whenever you can, but never at the cost of quality. Scheduling is stride's job, not yours. Every finished card teaches the next ones.**

In practice that means four things:

- **Fast:** cards that don't depend on each other run side by side, and a card waiting on another holds back until that card is done.
- **Quality:** a card in a batch gets every check it would get on its own.
- **No scheduling for you:** you decide what goes in Todo. Stride decides the order and how many run at once.
- **Agile:** take a small step, see what it taught you, and change the plan before the next step.

## The guiding light

[`VISION.md`](VISION.md) at the repo root is stride's guiding light. Every issue, every feature, every architectural decision traces back to it. If a request can't be tied to a Vision outcome, push back — either the work is out of scope, or the Vision needs a new outcome. *(Planning, ranking, and implementation all read `VISION.md` before deciding anything — that's the upstream-anchor role.)*

The Success criteria section names the outcomes the project is committed to — use them when ranking work, framing issues, or making implementation trade-offs.

## Critical rules

- **Use `/commit`, never bare `git commit`.** A pre-tool-use hook blocks bare commits. The `/commit` skill runs four atomic-commit passes; bypassing it produces commits that don't earn their place.
- **Atomic commits.** One purpose per commit. If the message needs "and" to join unrelated ideas, split.
- **Markdown only.** Stride installs as plain markdown into `.claude/`. The install footprint has no runtime, no build step, no compiled binaries.
- **Don't commit unless asked.** Wait for an explicit `/commit` or commit instruction.

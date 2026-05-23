# CLAUDE.md

This file shapes behaviour on every turn. Discoverable details (commands, architecture, tech stack) live in `README.md` and `docs/` — only durable rules belong here.

## The guiding light

[`VISION.md`](VISION.md) at the repo root is stride's guiding light. Every issue, every feature, every architectural decision traces back to it. If a request can't be tied to a Vision outcome, push back — either the work is out of scope, or the Vision needs a new outcome. *(Planning, ranking, and implementation all read `VISION.md` before deciding anything — that's the upstream-anchor role.)*

The Success criteria section names the outcomes the project is committed to — use them when ranking work, framing issues, or making implementation trade-offs.

## Critical rules

- **Use `/commit`, never bare `git commit`.** A pre-tool-use hook blocks bare commits. The `/commit` skill runs four atomic-commit passes; bypassing it produces commits that don't earn their place.
- **Atomic commits.** One purpose per commit. If the message needs "and" to join unrelated ideas, split.
- **Markdown only.** Stride installs as plain markdown into `.claude/`. The install footprint has no runtime, no build step, no compiled binaries.
- **Don't commit unless asked.** Wait for an explicit `/commit` or commit instruction.

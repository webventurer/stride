# codefu-core

<mark>Vibe coding builds on quicksand. The first few stories go up fast, but a few changes later the house is tipping over and you can't tell which wall is load-bearing.</mark>

Vibe coding is great on day one — you describe what you want, the agent builds it, and within minutes you have a running app. But by day ten you can't tell which change broke things. By day thirty you're afraid to touch anything. By day ninety you're rewriting from scratch.

codefu-core gives you a **solid foundation from the start** — three Claude Code skills that turn you from a vibe coder into an [agentic engineer](docs/reference/agentic-engineering.md). A [Linear](https://linear.app) workflow that structures *what the agent works on*, atomic commits that structure *how it records each change*, and prompt generation that structures *how it thinks before starting*. Linear is an opinionated choice — it's keyboard-driven, git-integrated, and built for the way modern software teams actually work. Everything installs as plain markdown into your `.claude/` directory. No runtime dependencies, no lock-in — read it, change it, make it yours.

![CODEFU!](designs/codefu-poster.jpg)

## What you get

This is what **agentic engineering** means — imposing structure on the agent at every stage. `/craft` structures *how the agent thinks* before starting. `/linear` structures *what it works on* and why. `/commit` structures *how it records* each change. They're not three independent tools — they're stages in the same loop, and each one makes the next one better.

`/craft` sharpens the problem before `/linear` turns it into a tracked issue. `/linear` manages the full lifecycle — branching, implementation, PR, merge — and calls `/commit` at every commit point to keep the git history atomic. Remove any piece and the loop still works, but the output gets worse.

**`/linear`** — Five commands covering the full development cycle. Plan work, create issues, implement on a branch, handle PR feedback, merge and close — all driven from Claude Code, all synced with Linear.

![Kanban board](docs/public/kanban-board.svg)
*Issues flow from Backlog through In Progress to Done — driven entirely by `/linear` commands.*

**`/commit`** — Four-pass atomic commits, called by `/linear` at every commit point. The agent stages selectively, checks coherence, verifies formatting, and writes commit messages that explain *why*, not just what. Every commit is one complete logical change, independently revertible.

![Commit pipeline](docs/public/commit-pipeline.svg)
*Four passes separate content decisions from formatting standards — catching the mistakes AI agents make.*

**`/craft`** — Structured prompt generation using the C.R.A.F.T. framework. Built into `/linear:plan-work --craft` to sharpen issue descriptions *before* the agent drafts them — better input in, better issues out.

## Install

```bash
npx github:webventurer/codefu-core
```

This copies skills, commands, hooks, and docs into your project. It merges hook config into your existing `.claude/settings.json` (or creates one). Nothing is installed globally.

## Quick start

```bash
# See what needs doing
/linear:next-steps

# Plan and create an issue
/linear:plan-work "add dark mode toggle"

# Implement it — branch, code, test, PR
/linear:start PG-123

# Commit your changes
/commit

# Address review feedback
/linear:fix PG-123

# Merge, clean up, done
/linear:finish PG-123
```

## Docs

Full documentation at the [docs site](https://webventurer.github.io/codefu-core) or run locally:

```bash
pnpm dev
```

## License

[MIT](LICENSE)

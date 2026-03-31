# Agentic engineering

![Vibe coding vs agentic engineering](/foundations.svg)

## Vibe coding

Vibe coding is the fastest way to get something working. You describe what you want, the AI agent builds it, and within minutes you have a running application. No boilerplate, no configuration ritual, no waiting. For prototypes, throwaway scripts, and "let me see if this idea works" — it's genuinely excellent.

### What's good about it

- **Instant momentum** — from idea to working code in minutes
- **Low barrier** — no setup, no process, no overhead
- **Great for exploration** — try ideas without committing to them
- **Accessible** — anyone can build software, regardless of engineering background

### Where it breaks down

The problems don't show up on day one. They show up on day ten, when you need to change something.

<mark>Vibe coding builds on quicksand. The first few stories go up fast, but a few changes later the house is tipping over and you can't tell which wall is load-bearing.</mark>

- **No history** — `git log` shows "initial commit" and "updates". When something breaks, you can't tell what changed or why
- **No reversibility** — everything is one monolithic commit. Revert one thing and you revert everything. Fix one bug and you might reintroduce another
- **No traceability** — the code works, but nobody knows *why* it was built this way. Was that workaround intentional? Was this feature requested? Who asked for this?
- **No structure to change** — every modification is a fresh conversation with the agent. There's no branch, no issue, no PR — just "change this" and hope nothing else breaks
- **Compounding debt** — each vibe-coded change makes the next one harder. The agent has no memory of previous decisions, no context about what's fragile, no awareness of what other changes are in flight

### The timeline

| | What it feels like |
|:--|:-------------------|
| **Day 1** | Running app, feels amazing — you built *that* in an hour? |
| **Day 10** | Something broke. Which change? No idea — `git log` says "updates" |
| **Day 30** | Afraid to touch anything. Every fix introduces two new bugs |
| **Day 90** | Rewriting from scratch. Faster than untangling what's there |

The cruel irony: vibe coding feels most productive at the start, when you need it least. By the time the problems are visible, the codebase is too tangled to retrofit structure without starting over.

## Agentic engineering

Agentic engineering is the practice of imposing structure on AI agents so they produce work that is traceable, reversible, and tied to real objectives. It costs more upfront — you're trading instant momentum for a solid foundation.

### What you get

- **Traceable history** — every commit explains *why*, not just what. `git log` reads like a project narrative
- **Safe reversibility** — any single change can be reverted independently without touching anything else
- **Connected to purpose** — every change links to an issue. The agent works on what was asked for, not what it felt like building
- **Structure for change** — branches, PRs, reviews, and a clear lifecycle mean changes are isolated and reviewable before they land
- **Compounding returns** — each well-structured change makes the next one easier. The agent has context, the history has meaning, and the codebase stays navigable

### The timeline

| | What it feels like |
|:--|:-------------------|
| **Day 1** | Still setting up — slower than vibe coding, no question |
| **Day 10** | Something broke. `git bisect` finds it in 30 seconds |
| **Day 30** | Confident refactoring — atomic reverts mean you can experiment safely |
| **Day 90** | Codebase still navigable, still growing. History tells the full story |

### What it costs

- **Slower start** — setup, install, configuration before you write any code
- **Process overhead** — issues, branches, commit passes, PR reviews add steps
- **Learning curve** — you need to understand the methodology, not just use it
- **Opinionated** — it prescribes Linear, prescribes commit format, prescribes workflow. If you disagree with the opinions, you're fighting the tool

### The trade-off

This is the core decision:

| | Vibe coding | Agentic engineering |
|:--|:------------|:--------------------|
| **Day 1** | Running app | Still setting up |
| **Day 10** | "Which change broke this?" | Clear git history, easy bisect |
| **Day 30** | "I'm afraid to touch anything" | Confident refactoring, atomic reverts |
| **Day 90** | Rewrite from scratch | Codebase still navigable, still changeable |

<mark>Vibe coding optimises for the first hour. Agentic engineering optimises for the next six months.</mark>

## How flowfu structures the agent

Agentic engineering imposes structure at three levels:

| Level | What it structures | Skill | Without it |
|:------|:-------------------|:------|:-----------|
| **Thinking** | How the agent understands the problem before starting | `/craft` | The agent works from whatever you typed — ambiguity in, ambiguity out |
| **Planning** | What the agent works on and why | `/linear` | The agent works in isolation, disconnected from project priorities |
| **Recording** | How the agent captures each change | `/commit` | Changes land as monolithic commits — impossible to review, dangerous to revert |

These aren't independent concerns. `/craft` feeds into `/linear:plan-work` to produce better issues. `/linear` calls `/commit` at every commit point to keep the history atomic. The structure compounds — better input at each stage means better output at the next.

## Why it compounds

<mark>As AI models improve, structured documentation gets *more* from them, not less.</mark>

A better model following vague instructions still produces vague output. A better model following the four-pass commit methodology produces *tighter* atomic commits. A better model working from a well-structured Linear issue produces *more precise* implementations.

The investment in structure pays increasing returns as the tools get better. Vibe coding doesn't scale with model improvements — the bottleneck was never the model's capability, it was the absence of structure around it.

## The governing principle

> "When faced with two or more alternatives that deliver roughly the same value, **take the path that makes future change easier**." — David Thomas & Andrew Hunt, *The Pragmatic Programmer*

Every decision in flowfu optimises for future change: atomic commits make reverting safe, Linear integration makes priorities visible, structured prompts make the agent's starting point explicit. The path that makes future change easier *is* the structured path.

# Why Stride?

<mark>Vibe coding builds on quicksand. The first few stories go up fast, but a few changes later the house is tipping over and you can't tell which wall is load-bearing.</mark> By day ten you can't tell which change broke things. By day thirty you're afraid to touch anything. By day ninety you're rewriting from scratch.

<div class="inline-image">

![Vibe coding vs agentic engineering](/foundations.svg)

</div>

## What stride gives you

stride gives you a **solid foundation from the start**. Three things turn you from a vibe coder into an **agentic engineer** — a [Linear](https://linear.app) workflow that structures *what the agent works on*, atomic commits that structure *how it records each change*, and prompt generation that structures *how it thinks before starting*. All without leaving the terminal.

[`/vision`](/skills/vision) sits *above* the loop — it captures what the project is for, so every issue, every feature, and every commit traces back to a single anchor. [`/clear-speak`](/skills/clear-speak) sits *beside* it — point it at any writing the agent produces and it swaps the jargon for words a non-engineer can follow.

Cards don't have to queue behind you. Cards that don't depend on each other build side by side, each in its own worktree (its own separate folder), while you keep making quick changes to your app in your own session. Quick changes go in your session one request and one `/commit` at a time; work that needs thought goes on a card. [Foreground loop, background structure](/patterns/foreground-loop-background-structure) sets out the two lanes, and [`/parallel-sessions`](/skills/parallel-sessions) runs the cards.

### Why it works

- It matches how attention works. Seeing a change land moments after you ask keeps you engaged, and that's exactly what a long background run loses.
- It's cheap. The foreground half is one rule (stride won't touch your folder while you're working in it), one refusal (the session running cards won't take app changes) and docs. No new machinery.
- It moves the [bottleneck](/concepts/attention-bottleneck) to the right place. The thing that limits you becomes what you decide to build, not waiting for stride.

## The principle

**Speed up whenever you can, but never at the cost of quality. Scheduling is stride's job, not yours. Every finished card teaches the next ones.**

In practice that means four things:

- **Fast:** cards that don't depend on each other run side by side, and a card waiting on another holds back until that card is done.
- **Quality:** a card in a batch gets every check it would get on its own.
- **No scheduling for you:** you decide what goes in Todo. Stride decides the order and how many run at once.
- **Agile:** take a small step, see what it taught you, and change the plan before the next step.

## Where to go next

Ready? Head to [Getting started](/getting-started) for how the pieces fit together, or [Install](/install) to drop stride into your project.

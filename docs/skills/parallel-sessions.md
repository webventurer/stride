# /parallel-sessions — Run independent cards at once

Give it several jobs that don't depend on each other, such as three Linear cards, and it runs each one in its own Claude Code session, a set number at a time. Each session commits only its own work, and you are asked only about the decisions that are yours to make.

## How a batch runs

1. **Settle the batch.** The coordinator, the session you talk to, works out what the batch is for, the job each session runs (such as `/linear:start` on one card), the items, how many run at once, and whether they share one checkout or get a worktree each. It asks only about what your message left out.
2. **Wait for "go".** It shows the batch, one line per item, and starts nothing until you say go.
3. **Start every session in one turn.** Each session gets a written brief naming the files it may change. A slot store caps how many run at once, so the rest wait their turn without you starting them.
4. **Check and merge.** When a session's work is ready, the coordinator checks the commit against the paths its brief named, and that nothing in those paths is left uncommitted. In worktree mode it checks each branch combined with `main` before merging it.

## Runs through Todo

In unattended mode, `/linear:start` with no card named carries on through Todo with no further "go" from you. Each time a card finishes, whether it merged, was cancelled, failed or stopped on a question, the next card that can start takes its place, never more at once than your limit. After a merge, that waits until the card's lessons have reached Todo. A card the coordinator keeps back is marked on the board as blocked by the card it waits for. The run stops when no card is running and none in Todo can start.

Cards that change the same files still run together. Each card is tested combined with `main` as it stands, one card at a time, before it merges, so a clash with another card, or with a commit you pushed meanwhile, is fixed before the merge.

While a batch runs, you can keep making quick changes to your app in your own session, one request and one commit at a time. [Foreground loop, background structure](/patterns/foreground-loop-background-structure) sets out the two lanes.

## Two modes

| Mode | Use it when | What happens |
|:-----|:------------|:-------------|
| **Shared checkout** | The jobs only create new files, such as transcripts or captures | Every session works in the main checkout |
| **One worktree per job** | The jobs change existing code, as Linear cards do | Each session works on its own branch in `.claude/worktrees/`, with stride's install linked in, and the coordinator merges each finished branch |

## Who decides what

The skill runs on a chain of command. Job sessions settle how to do the work, the coordinator settles what they can't, and only questions about what a card is for, or how far it goes, reach you. The decisions the coordinator settles for you aren't sent as they happen: the run's final report lists them, one line each, and you can overrule any of them. The skill's `reference/` folder sets out which model and effort each rank runs on, and what it costs.

## Needs

- `uv`, which runs the slot store without installing anything
- A Claude Code session that can start side sessions, or the `claude` command line, which the skill falls back to

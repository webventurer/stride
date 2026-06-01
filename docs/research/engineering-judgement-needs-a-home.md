# Engineering judgement needs a home

> The knowledge that tells you *which* tool, *how much* infrastructure, and *whether to build at all* — and where that knowledge should live so Stride and Claude reach for it before acting, not after the result disappoints.

## The question

Stride already injects two layers on every turn: **how to think** (the meta-cognitive framework) and **what to optimise for** (the six design principles). Both are domain-agnostic — they shape reasoning and values, not technical choices.

What they don't carry is the third layer: **what you need to know about the materials.** That a 90-char URL can't be wrapped. That data analysis belongs in pandas, not hand-rolled JavaScript loops. That a vector database solves a retrieval problem you may not have. That passing data as JSON between two Python functions is usually a worse in-memory dataframe.

This is *engineering judgement* — the accumulated sense of trade-offs that a senior engineer applies without thinking. The question this doc explores: **where should that judgement live, and in what shape, so an agent reaches for it before it acts rather than producing a plausible-but-wrong result?**

The honest framing up front: this is a problem statement, not a finished answer. We've started building pieces (the option-ladders); this doc names the whole and asks how to structure it.

## Why this matters: you can't just let it DO

<mark>**You can't let Claude and Stride go off and DO something, because the end result may not be what you wanted.**</mark>

An agent is fluent enough to produce *a* solution to almost any request. Fluency is not judgement. Asked to "analyse this data," it will happily write the analysis in JavaScript because the project is a web app — and the result works, passes, and is the wrong tool: no vectorised operations, no `groupby`, a reinvented half of pandas. The output looks like success. It isn't.

The failure mode is specific: **the agent optimises for producing output, not for choosing the approach a knowledgeable engineer would have chosen.** The gap between those two is exactly the judgement layer. Where the meta-cognitive *torch* says "consider what you're not seeing," this layer supplies the specific things worth seeing — the trade-offs that distinguish a defensible choice from a fluent guess.

This is why "act, read the signal, adjust" (feedback from action) is necessary but not sufficient. Feedback corrects you *after* you move. Judgement narrows the move *before* you make it. You want both.

## What this knowledge looks like

The category isn't one thing — it's a set of recurring decision points, each with a question it answers and a default that holds until a signal fires. A partial map:

| Judgement area | The question it answers | The failure without it |
|:---------------|:------------------------|:-----------------------|
| **Trade-offs** | What does this choice cost, and what door does it close? | Treating decisions as free; optimising one axis blind to the others |
| **YAGNI tool order** | What's the *leftmost* option that meets the requirement? | Reaching for "real" infrastructure (a DB, a pipeline) for data that fits in a spreadsheet |
| **Option ladders** | What are the realistic options, simplest-first, and what signal moves me right? | Picking the heavyweight option because it sounds like "real engineering" |
| **Right tool for the job** | Does the task fit the language/runtime, or am I forcing it? | Numerical analysis in JavaScript; shell parsing JSON; a SPA to show one chart |
| **Data interchange** | Should this data be in-memory, JSON, a flat file, or a database? | JSON files between two Python functions — a worse dataframe with a hand-rolled query layer |
| **RAG / vector databases** | Is this a semantic-retrieval-over-a-large-corpus problem — or a lookup `grep`/SQL already solves? | Standing up embeddings + a vector store for data that fit in the prompt |

### Worked examples of the failure

- **Python and DataFrames vs JavaScript.** Data analysis — joins, percentiles, grouping, time-series — is what pandas/polars exist for. Doing it in JavaScript because the surrounding app is JS optimises for "one language" and pays for it in reinvented primitives and missing ecosystem. The right tool is chosen by the *task*, not the repo. (Already explored in [`option-ladders/data-format.md`](../option-ladders/data-format.md).)

- **When to pass data as JSON.** JSON earns its place at a *boundary* — a non-Python consumer, a git-diffable schema review, a wire format between services. Inside one Python process it's usually dead weight between the source and the dataframe you load it into anyway. The signal is "something across the boundary needs it," not "I need to move data."

- **When to reach for RAG and vector databases.** They solve one problem: **semantic retrieval over a corpus too large or too unstructured to fit in context, where keyword search isn't enough.** That's it. If the data fits in the prompt, a query answers exactly, or `grep`/full-text search suffices, a vector store is infrastructure for a requirement you don't have — embeddings to maintain, a store to host, relevance to tune, all to answer something a `WHERE` clause would. The judgement is recognising the *shape* of problem they fit (fuzzy recall across volume) versus the shapes they don't (exact lookup, small data, structured filters).

### What else belongs here

The list above is a start, not a boundary. Other judgement areas that recur and would want a home:

- **Build vs buy vs borrow** — when a library, a hosted service, or 20 lines of your own is right
- **Abstraction timing** — three similar lines beat a premature abstraction; *when* does duplication earn an extraction
- **Sync vs async / batch vs stream** — does the work need concurrency, or is that complexity for a load that doesn't exist
- **Caching and indexing** — what they cost (staleness, invalidation, write overhead) against what they buy
- **Schema and migrations** — when structure must be decided up front vs deferred (postpone decisions)
- **State and idempotency** — can this be re-run safely; where does state actually need to live
- **Error handling vs the happy path** — which failures are worth code and which are worth a crash
- **Cost and latency** — the network round-trip, the token budget, the build step — trade-offs that don't show up in a passing test
- **Observability** — when logging/metrics earn their place versus noise

## The shape that's working: the option-ladder

The two existing docs aren't ad-hoc — they share a structure worth naming, because it's the reusable template for encoding judgement:

1. **Untangle the hidden concerns.** "Useable format" turned out to be three independent decisions (storage / access / working representation). Most tool debates are several debates mashed together; separating them surfaces the YAGNI answer.
2. **List the options simplest-first**, ordered by *how much new infrastructure each introduces*.
3. **Default to the leftmost option that meets the requirement.**
4. **Name the signals that move you right** — concrete triggers ("loaders take >1s," "a non-Python consumer needs the data"), not vibes.
5. **Add the torch** — what would shift the recommendation.

This template turns a fuzzy "it depends" into a navigable ladder with a default and exit conditions. It's the most promising unit we have for packaging judgement so an agent can apply it deterministically.

## Where should this knowledge live?

This is the open question. Several homes are possible, and they're not mutually exclusive — the right answer is probably a split by *layer type*.

| Candidate home | Fits knowledge that is… | Tension |
|:---------------|:------------------------|:--------|
| **`option-ladders/`** | A bounded decision with rankable options (data format, display, storage) | Only fits problems that *have* a clean ladder |
| **A `judgement/` or `playbooks/` dir** | Decision guides that don't reduce to a single ladder (build-vs-buy, abstraction timing) | A new top-level category to maintain |
| **`principles/`** | Stable, domain-agnostic rules ("postpone decisions") | Already exists; engineering specifics would dilute it |
| **`reference/`** | Look-up knowledge (what RAG is, what a vector DB costs) | Passive — read when sought, not when needed |

Cutting across the *where* is a sharper question — **how does the knowledge reach the agent at the moment it decides?**

- **Always in context (hook-injected),** like `design-decisions.md` and the meta-cognitive framework. Guarantees it fires every turn; costs context budget on every turn, and doesn't scale — you can't inject ten tool-choice ladders into every prompt.
- **Retrieved when relevant (skill / doc pulled on demand),** like the option-ladders' AI Assistant Notes ("when a user asks how to load data, reference this"). Cheap and scalable; risks *not firing* when the agent doesn't recognise it's at a decision point — and not recognising the decision point is the original failure.

That tension is the crux: the always-on layer is for the handful of universal moves (how to think, what to value); the retrieved layer is for the long tail of specific trade-offs. The hard part is the **trigger** — teaching the agent to notice "this is a tool-choice moment, go consult the ladder" reliably enough that the retrieved knowledge actually gets retrieved.

## Open questions to resolve next

- **Taxonomy.** Is "engineering judgement" one category, or does it split cleanly across the existing six layer types (concept / distinction / context / principle / pattern / rule)? A vector-DB explainer is a *concept*; "default to the leftmost option" is a *principle*; an option-ladder is a *pattern*. Maybe the home isn't one dir but a discipline for filing each piece by its layer.
- **The trigger problem.** What makes an agent reliably *notice* it's at a judgement point? A pre-action checklist? A hook that fires on certain task shapes? This is the highest-leverage unsolved piece.
- **Authoring cost.** Each ladder is ~200 lines of careful work. What's the minimum viable judgement doc, and which decision points are worth that investment first (ranked by how often the failure actually bites)?
- **Scope vs Vision.** Stride's Vision says it's *not* a project orchestrator and *not* a vibe-coding accelerator. Does a judgement layer serve "AI speed into maintainable codebases," or does it drift toward being a general engineering tutor? The line matters.

## The torch — what this framing might miss

- **This could become a second-guessing tax.** A judgement layer that fires on every action risks turning "ship a small change" into a seminar. The option-ladder default-to-leftmost discipline is partly a defence against this — most of the time the answer is "the simple thing," stated once. But a poorly-scoped judgement layer could reintroduce exactly the friction Stride's Vision works to remove. The goal is *guardrails, not walls*.
- **The trigger problem may be the whole problem.** Writing the knowledge is the easy 80%; getting it consulted at the right moment is the hard 20% — and if that's unsolved, every doc we author is a tree falling in an empty forest. It may be worth prototyping the *trigger* on a single existing ladder before authoring more content.

---

*The pieces exist (option-ladders, principles, the torch). What's missing is the category that names them and the trigger that fires them. This doc is the placeholder for that decision, not the decision itself.*

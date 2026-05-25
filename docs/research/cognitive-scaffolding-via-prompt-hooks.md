# Cognitive scaffolding via UserPromptSubmit hooks

> How stride re-injects behaviour-shaping framing on every turn — and why that produces a better class of agent–human interaction than a more capable model alone would.

## The question

stride installs `UserPromptSubmit` hooks that prepend the same framing to *every* user message. It's a small, almost invisible mechanism. The question this doc explores: **does re-injecting framing on every turn actually change how the agent thinks and decides — and if so, what kind of interaction does it create?**

The honest framing up front: we can't measure an agent's inner experience, and we don't claim one. What we *can* observe is the agent's **output** — the shape of its reasoning, the choices it offers, the things it catches. That output changes, observably, when the framing is in context. This doc is about that observable change.

## The mechanism

Three hooks fire on every `UserPromptSubmit`:

| Hook | Source | What it injects | Role |
|:-----|:-------|:----------------|:-----|
| `inject_design_principles.sh` | `settings.json` (committed) | `design-decisions.md` — the 6 principles + "the test" | **What to optimise for** |
| `inject_meta_cognitive.sh` | `settings.local.json` | the meta-cognitive framework — stance, layers, the torch | **How to think** |
| `faithful_content.sh` | `settings.local.json` | "Execute content exactly as given" | **A fidelity guardrail** |

Each is tiny (the design doc is ~580 words, table-led so it skims fast). The cost is near-free; the effect is not.

**Why every turn, not once?** The hook's own comment says it plainly: *"so they stay active even in long conversations where doc context may get compressed."* The model has no memory across a context compaction — anything not re-stated can silently fall out. These docs are *behaviour-shaping*, so if they evaporate mid-session, behaviour drifts back toward the model's defaults. Re-injection is cheap insurance against that drift. It is **not** a [YAGNI](https://github.com/webventurer/stride/blob/main/.claude/stride/docs/principles/design-decisions.md) violation: it serves a present, recurring need, not a speculative future one.

## What it changes

Left to its own momentum, a capable model produces *fluent* output — answers that "sound reasonable" and arrive fast. Fluency is the default, and the default has a failure mode: it commits to the first plausible framing and decorates it, rather than interrogating it.

The injected framing replaces fluency-by-default with **named cognitive moves the agent reaches for before committing**:

- **The principles** give it a checklist to run a design choice against — *is this atomic? is this YAGNI? does it close doors?* — so "sounds reasonable" has to survive contact with explicit tests.
- **The layers** (concept / distinction / context / principle / pattern / rule) give it a vocabulary for *what kind of move* a situation needs — recognising that two options have blurred together (a **distinction**) is different from not knowing what to do (a **principle**).
- **The torch** is the sharpest of the three: *before* presenting a recommendation, name the 1–2 things absent from your own framing. This fires while the conclusion is still editable, not as a retrospective caveat.

<mark>**The shift is from describing a decision to interrogating it — and doing the interrogation out loud, before the human has to.**</mark>

The agent's own account of the difference, given mid-session, was blunt about both the gain and its limit: it won't claim to *feel* the framing, but it can see that the framing visibly changes its output and not as decoration. With the torch in context it stops and looks for what's absent *before* committing, rather than bolting caveats on afterwards — and that genuinely changes the answer. Without the framing it would still be competent, but it would drift toward "sounds reasonable" faster and over-build more often. The named moves are handholds it reaches for; reaching for them is what produces the clear, correctable options. The honesty in that account matters as much as the claim: the structure only pays off **when the move catches something real**, and the human supplying live signal is doing as much of the work as the scaffolding.

## Evidence from practice

This isn't theory; the de-branding work in this project is a worked example of the scaffolding catching things the fluent default would have missed.

| Moment | What the fluent default would do | What the scaffolding caught |
|:-------|:---------------------------------|:----------------------------|
| Removing `WB-*` from the commands ([WB-439](https://linear.app/)) | Treat every `WB-NNN` as an example and bulk-generalise it | The torch surfaced that most were **real citations** (`WB-401 hit this trap`, `WB-256 enforces`) — provenance, not examples. Generalising them would have made the docs cite issues that don't exist. |
| The `PG-` placeholder ([WB-441](https://linear.app/)) | Swap `PG-` for something "cleaner" (`FOO`, `ABC`) and call it done | The human supplied the real signal — *"a two-letter prefix looks like a real issue ID; keep it"* — and the scaffolding's job was to make the steps legible enough that the correction landed cleanly, then narrow the card to the one genuine fix (the regex). |
| `/linear:check` being per-workspace | Ship the obvious per-team rework | Surfaced the gap *and* the YAGNI tension — multi-team workspaces were a test artifact, not the steady state — so the work shipped with its own scope honestly bounded. |
| `transitions` block sitting unwired; prefix→workspace auth resolution | Helpfully "complete" them | Named both as deliberate **postpone-decisions** calls, with the trigger that would later justify them — preventing a future agent from "fixing" a non-bug. |

In none of these did the agent arrive at the answer alone. The pattern was: **agent supplies structure, human supplies signal, structure makes the correction cheap.**

## The better class of interaction

What specifically improves when the framing is live:

1. **Legible reasoning.** The agent shows its working in a shape the human can audit — named principles, explicit trade-offs, a torch line. The human isn't reverse-engineering intent from a wall of confident prose.
2. **Correctable steps.** Because the reasoning is legible, the human can intervene *at the step that's wrong* rather than rejecting the whole answer. The `PG` reversal took one sentence from the human because the agent had already laid out the seam.
3. **A division of labour that plays to each side.** The agent is good at structure, breadth, and not getting tired; the human is good at real-world signal — *"it's not biting"*, *"that looks like real work"*. The framing makes the agent **wait for that signal rather than guess past it**, which is exactly what *postpone-decisions* and *friction-is-information* prescribe.
4. **Shared vocabulary.** "YAGNI", "atomic", "the torch", "distinction", "trace" become a compression layer. The human can say *"is that YAGNI?"* and the agent knows the whole move that invokes. Less is spelled out because more is shared.

## The tension we're iterating on

The real subject of this doc isn't the hooks — it's a **tension**, and the hooks are one knob on it. The tension is between **what the agent provides** and **what the human actually needs**, and it does not have a fixed setting.

| The agent can over-provide | The agent can under-provide |
|:---------------------------|:----------------------------|
| Too many structured choices; a torch line on a trivial call; options where an obvious default would do; caveats that perform thoroughness without adding it | Just *doing it* with no legible reasoning; guessing past a decision the human wanted to make; collapsing a real fork into a silent default |

Both ends are failures. Over-provision turns the agent into a tax — every well-formed options table is a small interruption, and a wall of them is its own kind of noise. Under-provision turns it into a fast guesser the human can't audit. <mark>**The quality of the interaction lives in the *calibration* between those ends — and the calibration is negotiated turn by turn, not set once.**</mark>

This is the Vision's own principle — *"guardrails, not walls… the common path runs without prompts; friction appears only where it carries signal worth your judgement"* — applied to the **agent's output volume**. Every structured choice the agent raises has to earn its place exactly like a gate does: surface it when the human's answer genuinely changes what happens next; pick the obvious default and move when it doesn't.

What makes it *work* is that the calibration is **driven by the human's signal, read live** ([feedback-from-action](https://github.com/webventurer/stride/blob/main/.claude/docs/patterns/context-speaks/act-then-adjust.md)):

- *"just do it"* / *"jfdi"* → provide less; act, don't ask
- *"wait, let me think"* / a clarifying question → provide more; slow down, lay out the seam
- *"it's not biting"* / *"keep it"* → the human has supplied the real-world signal the agent was missing; stop guessing and converge

The scaffolding doesn't *solve* the tension — it makes the level **adjustable and the adjustments cheap**. Legible reasoning is what lets the human nudge the level in one sentence instead of rejecting a whole answer. The torch is what stops the agent committing before the human has had the chance to nudge. The principles are what tell the agent which interruptions are worth raising at all.

"Seems to be working" is the honest status: this is not a solved setting we found, it's a level the two sides keep finding *together*, mid-conversation. The mechanism's contribution is that it makes finding it low-friction — and that's the whole claim.

## The deeper claim

stride's [Vision](https://github.com/webventurer/stride/blob/main/VISION.md) argues that *structured docs get **more** out of a capable model, not less* — and that the gap compounds as models improve. This mechanism is that thesis applied not to the codebase but to the **interaction layer**.

A weaker model needs the scaffolding to avoid failing. A stronger model doesn't fail without it — but *with* it, the strong model spends its capability on the right things: catching the citation-vs-example distinction, naming the deferred decision, surfacing the absent frame. The scaffolding doesn't constrain a capable agent; it **gives its capability somewhere to land**.

## Honest limits

The torch turned on this doc:

- **Performative structure is a real failure mode.** The framing can produce well-shaped-*looking* output — a torch line, a tidy options table — that adds nothing because the situation didn't need the distinction. Structure earns its place the same way everything in stride does: when removing it would leave a hole. When it's decoration, it's noise, and noise is worse than silence because it *looks* like signal.
- **The human's real-world signal is still load-bearing.** Every catch above had a human supplying something the agent couldn't derive — that a prefix looks real, that a problem isn't biting. The scaffolding makes the agent *receptive* to that signal and *legible* in response; it does not manufacture the signal. Remove the human and you get well-structured guesses.
- **Token cost is real but small here.** ~1,200–1,500 words re-sent per turn. Justified today by the drift-insurance; worth revisiting (a compact table + pointer, or conditional re-injection after compaction) only if a real signal appears — sessions getting expensive, or the framing crowding out useful context. Not before.

## Open questions

- Does the value **decay within a session** as the model has already absorbed the framing — i.e. is re-injection most valuable right after a compaction and near-redundant otherwise? If so, conditional injection beats unconditional.
- Which of the three hooks does the most work? The torch feels disproportionately load-bearing in the transcript evidence; the faithful-content one-liner rarely visibly fires. A subtractive experiment (drop one, observe) would tell us.
- Does the **shared vocabulary** transfer to the human, or only run one way? If the human starts thinking in *YAGNI / torch / distinction* too, the compression is mutual and the interaction improves further — but that's a claim we haven't tested.

---

*This doc is a record of stride dogfooding its own framing — written after a session where the scaffolding repeatedly caught things the fluent default would have shipped. It cites real issues (WB-439, WB-441) as provenance, which is appropriate for a research record even though those same citations were stripped from the installed commands.*

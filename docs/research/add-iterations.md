# Should stride add iterations?

> **Status**: Research stage. Exploring whether to port the **iteration** layer from telic into stride. Current recommendation: don't port speculatively — wait for evidence stride needs it. The strongest case is the *forced-replan moment*; everything else is partially handled by atomic commits. This doc captures the analysis so future-us can act on it (or not) when the data arrives.

## What an iteration is

**Iteration.** One pass of the agent's loop toward a story — plan, implement, review, refine. Stride-specific: doesn't surface on the kanban board, and isn't a Linear primitive. The story sits in *Doing*; the iterations happen underneath. A small story might ship in a single iteration; a larger one might take five or six.

*Not a Scrum sprint.* A sprint is a time-box across a whole team; an iteration here is one loop pass inside one story for one agent. They share the word *iterate* and nothing else.

Stride doesn't have this layer today. Its [reference doc](/reference/epics-and-user-stories) describes a 3-layer hierarchy — epic, story, task — and `/linear:start` runs a story through one continuous agent pass. This doc explores whether to add iteration as a fourth layer by porting from telic.

## How telic actually implements iterations

The original [epics-and-stories research doc](/research/epics-and-user-stories) said telic uses `sprints/sprint-N/.loop/` with named iterations (`iter 1–5`). **That's not how telic actually works** — review of the telic codebase showed:

| What we said | What telic actually has |
|:-------------|:------------------------|
| Per-iteration subdirectories (`iter-1/`, `iter-2/`…) | One `.loop_state.json` + boolean gates + an iteration *counter* (1–200) |
| Iterations as separate artifacts | Iterations as semantic phases (plan → review → implement → evaluate) cycling through state |
| `.loop/` holds iteration content | `.loop/` only holds verification scripts; state is in `.loop_state.json` |

**Telic's actual mechanism:**

- Entry: `telic-loop my-sprint`
- Loop: while iteration < max, deterministically pick next action from a P0–P9 priority queue (no LLM cost), dispatch to a role (Planner / Reviewer / Builder / Evaluator), commit atomically, save state, repeat
- Phases: plan → review → implement → evaluate, gated by booleans
- Exit: all tasks done + tests pass + a VRC (Value-Risk-Coherence) check passes
- Resume: rerun the same command — picks up from saved gate state

## What iterations would buy stride

| Real problem | How iterations help | How real is it for stride today? |
|:-------------|:--------------------|:---------------------------------|
| Stories that exceed one conversation's context | State persists between passes; resume cleanly | Real but rare — `/plan-work`'s "one PR = one deliverable" rule should keep stories small |
| Plan turns out wrong mid-implementation | Forces an explicit replan, freed from the original plan's bias | Real and common; today the agent course-corrects in the same conversation, often poorly because old plan stays in context |
| Verification reveals a deeper issue | Structured "verify failed → replan" event vs. ad-hoc patching | Real — `/linear:fix` partially handles this for *external* feedback, but not for self-discovered issues |
| Resumability across sessions | Saved state lets you pick up after a crash or break | Mild — atomic commits already give you decent resumability |
| Forced quality reflection | Review phase asks "did I do what I planned?" — distinct from "do tests pass?" | Real — stride doesn't enforce this today |

## What stride already has

| Iteration concern | Stride's existing answer |
|:------------------|:-------------------------|
| Externalised state between phases | Atomic commits — each one is a discrete checkpoint, revertable |
| Audit trail | Commit messages + PR + Linear comments |
| Discrete units of work | `/commit`'s atomicity rules + `/plan-work`'s one-issue-one-deliverable |
| Replanning trigger | `/linear:fix` for external review feedback (not self-discovered) |

The atomic commit *is* a lightweight iteration. So the question isn't "should stride have iterations?" — it's "what does an explicit iteration layer give that atomic commits don't already give?"

## The forced-replan moment — the strongest case

The strongest argument for porting iterations is **the forced-replan moment**. Today, when an agent's implementation contradicts its plan, the agent silently bends the plan rather than admitting "this plan was wrong." Iterations would surface that as a structured event: verify fails → exit gate fails → restart with a new plan.

That's a real quality win that atomic commits don't provide. Atomic commits enforce *purpose-per-unit* but not *plan-vs-reality reconciliation*.

The weaker cases (resumability, audit trail, structure) are partially handled by stride's existing primitives.

## Porting effort

What we'd be taking on if we ported:

| Tier | Lines | What you get |
|:-----|:------|:-------------|
| **Minimum** | ~400–600 | Plan + implement + verify + simple "tests pass + human approves" gate. No VRC, no rollback, single agent |
| **Solid first version** | ~2,000–3,000 | Full state machine + value checklist + decision engine. No multi-model dispatch yet |
| **Telic-parity** | ~9,600 | Don't aim here — most of telic is mission-specific |

**Translate, don't embed.** Stride doesn't need telic as a library — it needs telic's *architecture* expressed in stride idioms (`/linear:start` host, stride's `/commit` skill for atomicity, Linear MCP for state).

**Stride integration shape:**

- `/linear:start` becomes the host for iterations (no new top-level command)
- Internally: pull issue → branch → run iteration loop (plan/implement/verify/gate, multiple passes) → exit when gates pass or max iterations → push + open PR (existing stride flow)
- Other commands (`/plan-work`, `/fix`, `/finish`) untouched
- New `.loop_state.json` is `.gitignore`'d (transient, not shipped)

## Recommendation

**Don't port speculatively. Wait for evidence.**

Ship a few more stride epics under the *current* model (no iterations). When you hit one of these cases, the friction will be diagnostic — *which* of the five problems above is biting? That tells you what slice of telic to port.

Today the case is theoretical: telic shows the mechanism works, but stride hasn't shown it needs it.

## What would trigger porting

Concrete signals that would justify the work:

| Signal | What it would mean |
|:-------|:-------------------|
| PRs where the diff doesn't match the issue description | Agent is silently drifting — forced-replan would catch this |
| Stories regularly hitting context-window limits | Need state persistence between passes |
| Agents pushing tests-pass commits where tests pass but feature doesn't actually work | Need a value gate beyond "tests pass" |
| Multiple sessions abandoned mid-story with hard-to-resume state | Need explicit checkpoint state |

Until at least one of these recurs, atomic commits + `/linear:fix` are doing a respectable job, and the YAGNI principle says hold off.

## Open question

Is stride's user the experienced operator we've been talking to, or a less-experienced developer who'd benefit from forced verification structure?

If the latter, the case for iterations strengthens — iterations are partly a guard rail against agent over-confidence. The forced "review" phase asks *"did I do what I planned?"* before the agent can declare done. That discipline matters more for users who can't easily tell when an agent has drifted.

This is the most likely future requirement that would tip the decision. Worth re-examining once stride has external users.

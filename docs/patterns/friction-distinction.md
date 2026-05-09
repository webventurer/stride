# Friction is information. The question is which kind.

What this doc does: it helps stride's maintainers decide what to do when a user complains that something in stride is annoying. Two possibilities — either the user is doing the wrong kind of work (stride is right to push back), or the gate is firing on a use case nobody designed for (stride should be calibrated). The doc names the question and gives a way to tell them apart.

> Stride deliberately introduces friction — `/commit`, the trace-back gate, the Vision-confirm step. Each one fires for a reason. When a user *also* hits that friction, two readings are possible, and they produce opposite actions.

## The two readings

| Reading | When it's true | What to do |
|:--|:--|:--|
| **Friction-as-signal** | The gate is correctly placed; the user's work doesn't fit the project | Push back on the work — it's out of scope, or `VISION.md` needs to evolve to include it |
| **Friction-as-context-mismatch** | The gate fires on a context it wasn't designed for; the user's work is legitimate | Calibrate the gate — add a mode, scope a condition, build an off-ramp |

Both look the same from the user's seat: *"this isn't working, something's wrong."* The maintainer's job is to tell them apart before deciding whether to weaken the gate or push back on the work.

## How to tell them apart

The load-bearing question:

> *"Does this friction recur for users doing this kind of work, OR is this user doing the wrong kind of work?"*

Two heuristics:

- **Recurrence reveals reality** — if the same friction surfaces across multiple users on legitimate work, it's *context-mismatch*. Calibrate.
- **Singular drift is signal** — if one user is hitting friction because their work doesn't trace back to Vision, the work is the problem, not the gate. Push back.

<mark>**Default to *signal*. Earn *context-mismatch* with evidence.**</mark> The asymmetric default keeps anchors honest — it's much cheaper to revisit a calibration that didn't earn its place than to recover an anchor that quietly eroded.

## Worked example: the cross-project case

A user wanted to file an issue from repo `foo` into the Linear project for repo `bar`. `/linear:plan-work` ran its Vision check against `foo`'s `VISION.md` — the work didn't trace, the gate fired, and the user was told to *"add a criterion or drop as out of scope."*

The first read was **signal**: *"the gate is doing its job — your work doesn't fit `foo`."* Push the user through.

But the user's work was legitimate — it just belonged in `bar`'s project, not `foo`'s. The gate fired on a context it wasn't designed for: cross-project quick-add. `foo`'s Vision was correctly anchoring `foo`'s work; it just wasn't the right Vision to *check against* for an issue filed into `bar`.

The maintainer-side move:

1. **Test for recurrence** — would another user, doing legitimate cross-project work, hit the same friction? Yes — anyone with two stride-managed repos hits this on day one.
2. **Reading flips** — the friction was *context-mismatch*, not signal. The gate needed calibration, not the user.
3. **Calibration**, not removal — `/linear:plan-work --project <name>` now skips the Vision check explicitly when filing cross-project, surfaces a one-line note explaining why, and defers the Vision anchoring to `/linear:start` running inside the target repo. The discipline is preserved (the work *will* be Vision-anchored when picked up); the gate is just no longer firing on the wrong surface.

The work did fit — *into a different project*. The Distinction made the call land cleanly: not a position to defend, a question to answer.

## What this Distinction is *not*

- **Not licence to weaken every gate at the first sign of friction.** The default reading is *signal*. *Context-mismatch* requires evidence — recurrence + legitimate work — not just one user pushing back.
- **Not a way to skip the trace-back rule.** When friction-as-signal fires, the answer is still *"push back, or add a criterion via `/vision`"* — not *"call it context-mismatch and carve an exception."* If you can't show recurrence and legitimate work, it's signal.
- **Not a substitute for `VISION.md`.** The Distinction tells maintainers which Principle to reach for; it doesn't replace the anchor itself. The Vision is what *defines* legitimate work. Without it, neither reading is grounded.

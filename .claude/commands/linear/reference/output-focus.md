# Output focus

> **What this is**: the shared rules for how commands read the `focus` field from `.stride.json` and adjust their natural-language output accordingly. Linked from `/linear:start`, `/linear:finish`, `/linear:fix`, and `/linear:next-steps` — the commands that produce narrative summaries.
>
> **Why it exists**: command output previously operated at the implementation layer by default. The `focus` field lets teams choose the abstraction level that fits their workflow: `"outcome"` answers "what moved forward for the user, and why?"; `"technical"` answers "what decisions were made and how?"

---

## Reading the field

At the start of any output-generating step, read `focus` from `.stride.json`:

```bash
jq -r '.focus // "outcome"' .stride.json 2>/dev/null || echo outcome
```

- Missing file or missing field → `"outcome"` (the default)
- Invalid value → treat as `"outcome"` and carry on

---

## When technical detail surfaces in `outcome` mode

In `outcome` mode, technical detail appears **only when one of these five conditions applies**:

1. A human must choose between options
2. There is user-facing risk
3. There is migration or deployment risk
4. The implementation creates a constraint future work depends on
5. The agent is blocked or genuinely uncertain

When a condition applies, format it inline with the outcome summary:

```
Needs your call: <one sentence>
Why: <one sentence>
```

If none of the five conditions apply, omit technical detail entirely — the diffity diff and PR comments are the surfaces for implementation review.

**"Needs your call?" is where the torch lives.** The torch — things the user didn't know to ask about — still belongs in the output, but only when it meets one of the five conditions above. The five conditions are the filter. An observation that doesn't meet any of them goes to diffity, not to the outcome summary. The torch as a free-form section is gone; its function survives.

---

## Anti-hallucination rule

<mark>**Do not invent product impact.** If the work is internal with no UI change, say so plainly.</mark>

Acceptable forms:
- "No direct user-visible change"
- "Internal change supporting X"
- "Infrastructure work — no change visible to end users"

Never inflate implementation work into fake product impact to fill the Outcome or User-visible change fields.

**The same rule governs `Why it matters`.** Ground it in the issue's own `Why this matters` section and the Vision outcome the work serves — report the forward motion the work was committed to, not a manufactured significance. If the only honest why is "enables X later," say exactly that. The output's `Why it matters` closes the loop on the issue's opening `Why this matters`: the issue states why the work was taken on; the summary reports that why, delivered.

---

## The two modes at a glance

| | `outcome` (default) | `technical` |
|:--|:--|:--|
| **Answers** | What moved forward for the user, and why? | What decisions were made and how? |
| **`Why it matters` line** | Shown — grounded in the issue | Shown — folded into the narrative |
| **Technical detail** | Only under the five conditions above | Always |
| **Footprint-audit line** | Omitted | Shown |
| **Cleanup table** | Omitted | Shown |
| **Vision alignment prose** | Omitted | Shown |
| **Set via** | `.stride.json` `"focus": "outcome"` or absent | `.stride.json` `"focus": "technical"` |

---

## Command output shapes

> **Plain language throughout.** Every "plain-English sentence" in the templates below follows the [`/clear-speak` skill](../../../skills/clear-speak/SKILL.md) — stride's canonical standard for what counts as jargon and how to replace it. Write each summary so a non-engineer can scan it top-to-bottom.

### `/linear:start` step 15 and `/linear:fix` step 11 (review gate)

**Outcome mode:**

```
Outcome: <one plain-English sentence — what the product/feature does differently>
Why it matters: <one sentence — what this unlocks or how it moves the project forward>
User-visible change: <yes — [what a user sees] | no — internal change supporting [X]>
Needs your call? <none | specific decision or risk — one sentence>

WB-XXX — <title>
Branch: <name>
Build: passed
PR: <url>
Linear: In Review
[Squashed N commits into M — if step 10 grouped commits]

Does this look right?
```

**Technical mode** — same metadata, plus the footprint-audit line (`kept N helpers / dropped X / inlined Y`) and the full implementation narrative (What ships, Decisions worth flagging, The torch).

---

### `/linear:finish` step 13 (summary)

**Outcome mode:**

```
✓ WB-XXX — <title> — Done
Outcome: <one sentence — what the product/feature does differently>
Why it matters: <one sentence — what this unlocks or how it moves the project forward>
User-visible change: <yes — [what] | no — internal change supporting [X]>
PR: <url>
Build: passed
[Milestone: <name> — complete / <n> remaining — if applicable]
[Epic: <name> — Done / <n> sub-issues remaining — if applicable]
[Vision sync: applied / declined / already in sync — if VISION.md touched]
```

**Technical mode** — same, plus: local branch, remote branch, and worktree cleanup status.

---

### `/linear:next-steps` step 7 (recommendations)

**Outcome mode** — action and one-line reason only:

> **Recommended next**
>
> 1. **WB-XX — Title** — \<one-line reason tied to product/user outcome\>
> 2. **WB-YY — Title** — \<one-line reason\>

**Technical mode** — current format, naming the Vision outcome per recommendation:

> **Recommended next**
>
> 1. **PG-XX — Title** — reason. Serves Vision outcome: "\<criterion line from VISION.md\>".
> 2. **PG-YY — Title** — reason. Serves Vision outcome: "\<criterion line from VISION.md\>".

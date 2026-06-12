# Output focus

> **What this is**: the shared rules for how commands read the `focus` field from `.stride.json` and adjust their natural-language output accordingly. Linked from `/linear:start`, `/linear:finish`, `/linear:fix`, and `/linear:next-steps` — the commands that produce narrative summaries.
>
> **Why it exists**: command output previously operated at the implementation layer by default. The `focus` field lets teams choose the abstraction level that fits their workflow: `"outcome"` answers "what moved forward for the user?"; `"technical"` answers "what decisions were made and how?"

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

---

## The two modes at a glance

| | `outcome` (default) | `technical` |
|:--|:--|:--|
| **Answers** | What moved forward for the user? | What decisions were made and how? |
| **Technical detail** | Only under the five conditions above | Always |
| **Cleanup table** | Omitted | Shown |
| **Vision alignment prose** | Omitted | Shown |
| **Set via** | `.stride.json` `"focus": "outcome"` or absent | `.stride.json` `"focus": "technical"` |

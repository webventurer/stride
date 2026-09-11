# Linear card language

> **What this is**: the shared writing rule for titles, descriptions, and comments that stride adds to Linear cards.
>
> **Why it exists**: a card must be easy to understand without dropping the technical detail someone needs to complete the work correctly.

## Before writing card text

Follow [`clear-speak`](../../../skills/clear-speak/SKILL.md), stride's canonical plain-language standard. Its 16-year-old test applies to the wording, not the amount of detail: use familiar words, explain an unfamiliar term when it first appears, and keep the precise term when the work depends on it.

Within `clear-speak`, pay particular attention to [George Orwell's rules for writing](../../../skills/clear-speak/writing/george-orwell-rules-for-writing.md). Treat them as questions that expose vague or wasteful wording, not as commands that outrank accuracy: break a writing rule before making the card incomplete or wrong.

Keep every technical fact needed to do the work correctly, including:

- exact filenames and commands
- constraints and decisions already made
- edge cases and failure behaviour
- acceptance criteria and checks that prove the work is done

If clarity and precision seem to conflict, keep the precise detail and explain it plainly. Never replace a concrete fact with a broad summary that leaves the implementer guessing.

Preserve user-written text unless the user asks for a rewrite. When stride supplies the wording, describe the user, business, operational, or system outcome without inventing product impact that the work does not have.

## Explain the solution before the implementation

A card must answer "what will actually happen?" before listing settings, files or implementation tasks. Plain words alone are not enough: explain the decision they describe.

Follow [principles over rules](../../../stride/docs/principles/principles-over-rules.md): when a relevant principle exists, apply it to the context to derive concrete, testable requirements. Explain how each requirement serves the principle, and identify choices it does not settle. Keep that reasoning visible so readers can judge a new case. This explanation belongs in "What we'll do", after "Why this matters" and "Where things stand" in the [story template](templates/story.md).

- State the proposed solution in one sentence. Naming the goal again, such as "avoid stacking trades", is not a solution.
- Describe the trigger, the rule and the resulting action: "When X happens, check Y; if it fails, do Z." Include what happens when it passes and any material exception.
- Give a concrete worked example for each distinct behaviour-changing rule, showing an allowed and a refused case where applicable. Keep examples internally consistent with all the rules.
- Label illustrative numbers beside the example. Keep them separate from agreed defaults and unresolved policy choices; approval of an explanation does not approve its example values.
- Put configuration names, files, recovery behaviour and test details after the explanation. Preserve the technical facts needed to implement it correctly.
- When the user says a conversational explanation is clearer, make that explanation the card's main account of the solution rather than translating it back into abstract requirements.

Before saving, check: could a 16-year-old use this card to predict what happens in a new example? If they can only repeat the goal or list the settings, rewrite the explanation first.

## Where it applies

Apply this rule whenever a `/linear:*` command writes a card title, description, or comment, whether the card is new or already exists. It does not bulk-rewrite old cards, and it does not apply to state-only moves or attachment-only changes because those operations write no prose.

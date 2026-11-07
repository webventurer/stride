# Linear card language

> **What this is**: the shared writing rule for titles, descriptions, and comments that stride adds to Linear cards.
>
> **Why it exists**: a card must be easy to understand without dropping the technical detail someone needs to complete the work correctly.

## Before writing card text

Follow [`clear-speak`](../../../skills/clear-speak/SKILL.md), stride's canonical plain-language standard. Its 16-year-old test applies to the wording, not the amount of detail: use familiar words, explain an unfamiliar term when it first appears, and keep the precise term when the work depends on it.

Within `clear-speak`, pay particular attention to [George Orwell's rules for writing](../../../skills/clear-speak/writing/george-orwell-rules-for-writing.md). Treat them as questions that expose vague or wasteful wording, not as commands that outrank accuracy: break a writing rule before making the card incomplete or wrong.

Keep every technical fact needed to do the work correctly, including:

- exact file paths from the repository root, so a reviewer opens a file without searching for it, and exact commands
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
- Describe the behaviour the user or caller sees, not the internal mechanism. State inputs, outputs, edge cases, constraints and the tests that prove them; leave how the code achieves them to the builder. Name an implementation detail only where a constraint forces it, such as "runs after the save so a failure cannot stop it". A card that prescribes an algorithm fixes choices the builder should make against real data, and every review then finds holes in the algorithm instead of checking the promises.
- Put configuration names, files, recovery behaviour and test details after the explanation. Preserve the technical facts needed to implement it correctly.
- When the user says a conversational explanation is clearer, make that explanation the card's main account of the solution rather than translating it back into abstract requirements.

Before saving, check: could a 16-year-old use this card to predict what happens in a new example? If they can only repeat the goal or list the settings, rewrite the explanation first. Then check each paragraph: does it say what the caller observes, or how the code achieves it? Move or cut the how unless a constraint forces it.

## Every promise can be marked right or wrong

The end check judges every line it counts as a promise ([Find the promises](card-check-review.md#find-the-promises)). Each of those lines must pass two tests:

1. Someone holding the finished change can answer it yes or no.
2. The answer is no if the change was made but doesn't work.

A line that fails test 2 is an edit when it describes something the change does. It is not a promise at all when it is true or false whatever the change does, such as a fact about today, an opinion or a guess.

| The line | What to do with it | Example |
|:--|:--|:--|
| Passes both tests | Keep it | "A search for each old name finds nothing" |
| A vague quality, a process or a risk | Rewrite it as the result it stands for | "The work runs through `/script`" becomes the result `/script` protects, or goes when the card already promises it. "Risk: narrowing a catch can let an error through" becomes "each error the old catch handled is still handled" |
| An opinion or a guess | Move it to "Assumptions to confirm" | "A reviewer may prefer another name" |
| A fact about how things are today | Move it to "Where things stand" | "The brief says nothing about other checks" |
| An edit, which passes test 1 but not test 2 | Rewrite it as the result the edit is for | "Add a row to the table" becomes what a reader of the table now finds |

The [card start check](card-start-review.md) applies the same two tests before work starts.

## Where it applies

Apply this rule whenever a `/linear:*` command writes a card title, description, or comment, whether the card is new or already exists. It does not bulk-rewrite old cards, and it does not apply to state-only moves or attachment-only changes because those operations write no prose.

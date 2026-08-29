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

## Where it applies

Apply this rule whenever a `/linear:*` command writes a card title, description, or comment, whether the card is new or already exists. It does not bulk-rewrite old cards, and it does not apply to state-only moves or attachment-only changes because those operations write no prose.

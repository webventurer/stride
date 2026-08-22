# /clear-speak — Plain-language rewriting

Point it at any writing — a doc, a command file, an issue draft, a commit message, a README paragraph — and it replaces the jargon with words a non-engineer can follow on the first read.

`/clear-speak` is also stride's canonical standard for what counts as jargon. [`/linear:plan-work`](/skills/linear#linearplan-work) links to it for issue titles, and [`/linear:finish`](/skills/linear#linearfinish) links to it when explaining a Vision trace in plain English. As a rule it keeps *new* output plain; as a tool it fixes text that has already drifted.

## The test

**Can someone understand this without a dictionary or a degree?**

If not, find simpler words. The stricter version: if a 16-year-old wouldn't understand it, rewrite it.

## How it works

1. **Spot the jargon** — Latin and Greek roots, `-tion`/`-ment`/`-ism` nouns, abstract compounds, bare code identifiers dropped into prose, and any word you'd never say out loud
2. **Ask the replacement question** — "how would I explain this to a smart friend who doesn't know this field?" The answer is usually the rewrite
3. **Apply the transformation** — swap the fancy word for the plain one, and turn actions hiding inside nouns back into verbs

## Quick transformations

| Jargon | Clear speak |
|:-------|:------------|
| `migrate_from_legacy()` | The step that upgrades your old settings file |
| Dead code | Code nothing uses anymore |
| Parse-before-delete guard | Check the file before deleting it |
| Idempotent install | Safe to run twice |
| Deterministic ordering | Always comes out in the same order |
| Silent no-op | Quietly does nothing |
| Completeness audit | Gap check |
| Architectural analysis | Map the shape |
| Facilitate | Help with |

## When to use

- Cleaning up a doc, command file, or reference before it ships
- Naming a function, concept, or heading so it reads plainly
- Sharpening an issue title or description into a plain outcome
- Rewriting a commit body so a non-engineer can follow what changed
- Any time writing slips into fancy words

## What it doesn't do

<mark>**Keep the precise term, add the plain gloss — never strip the precise word.**</mark>

A technical term earns its place when it is genuinely precise, when the audience expects it, or when simplifying would lose meaning. For a load-bearing term like *atomic commit*, give it a one-line plain explanation the first time, then use it freely. Clear speak is not dumbing down — it is thinking the idea through until you can say it simply.

## Quality check

After a rewrite, four checks:

- **The 16-year-old test** — would a smart 16-year-old understand this?
- **The conversation test** — would you say this out loud to a friend?
- **The speed test** — can readers understand it on the first read?
- **The meaning test** — did you preserve what it actually said?

## Source

Built on George Orwell's six rules for writing, plus two supporting references shipped with the skill: writing clearly, simply, and with action; and plain headings with precise vocabulary inside.

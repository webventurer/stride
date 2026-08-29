# Plain-language Linear cards

## Context

We are planning one Linear story for stride. Stride creates card titles, descriptions, and comments through markdown command files. These can contain abstract language that makes the work harder to understand.

The requested outcome is:

- Add one shared `.claude/commands/linear/reference/card-language.md` rule for all Stride-written card text. It points to `.claude/skills/clear-speak/SKILL.md` as the canonical plain-language standard instead of copying those rules.
- Make card text plain enough for a 16-year-old to follow without removing the filenames, commands, constraints, edge cases, or acceptance criteria needed to complete the work correctly.
- Require every command that creates a card or adds generated text to a card to read the shared rule at the point where it writes that text.
- Keep state-only moves and attachment-only changes outside the rule because they do not write prose.
- Do not add a `.stride.json` field, backfill, recovery file, or `/linear:check` change: this is an always-on writing standard, not a user choice.

The story traces to this approved Vision criterion:

> Every Linear card can be understood by someone who does not know stride's commands or code — its title names a stakeholder outcome, while its description and updates use concrete, everyday words

## Role

You are a senior product engineer with 20 years of experience writing precise engineering work in everyday language. You simplify wording without simplifying away the technical details needed to do the job.

## Action

1. Draft one atomic story for the shared writing rule and every current card-text write point.
2. Keep `card-language.md` small: apply the canonical `clear-speak` standard to cards, then add only the card-specific requirement to keep every technical fact needed to do the work correctly.
3. Cover card titles, descriptions, and comments written by stride. Preserve user-written text and exclude state-only or attachment-only updates.
4. Require a test that checks `card-language.md` links to `clear-speak`, inventories the commands that write card text, and fails when one does not read the shared reference.
5. Do not add configuration, a readability score, an external service, a runtime abstraction, or a bulk rewrite of existing Linear cards.

## Format

Return one story with an imperative title under 70 characters and these sections:

- `### Why this matters`
- `### Where things stand`
- `### What we'll do`
- `### What we won't do`
- `### Expected outcome`
- `### How to test it`

Use Medium priority and the `Story` label. Do not assign it.

## Target audience

A developer or AI coding agent implementing the story. The draft itself must demonstrate the rule: clear to a 16-year-old reader and technically complete enough to implement without guessing.

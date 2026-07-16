---
name: clear-speak
description: Rewrite jargon into plain language a non-engineer can follow on the first read. Use on any docs, command files, issue drafts, commit messages, or README paragraphs. Triggers on "clear-speak", "clear speak", "simpler words", "plain language", "say this simply", or when writing slips into jargon.
---

# Clear speak

Rewrite academic and abstract language into words that land immediately.

## What this is for

`/clear-speak` is an **on-demand** plain-language tool. Point it at any chunk of writing — a doc, a command file, an issue draft, a commit message, a README paragraph — and it rewrites the jargon into something a non-engineer can follow top to bottom.

<mark>**Works on any prose. Tuned for the writing that ships in a repo** — docs, commands, issue/commit/README text — where jargon does the most damage.</mark>

> **The canonical home of the plain-language rule — and the on-demand tool.** Commands that generate output can link here for the always-on standard that keeps *new* output plain; as a tool, `/clear-speak` applies that same standard to *fix* text that has already drifted into jargon, anywhere in the repo.

## When to use

- Cleaning up a doc, command file, or reference before it ships
- Naming a function, concept, or heading so it reads plainly
- Sharpening an issue title or description into a plain outcome
- Rewriting a commit body so a non-engineer can follow what changed
- Any time writing slips into fancy words

## The test

**Can someone understand this without a dictionary or a degree?**

If not, find simpler words.

## Quick transformations

Drawn from real code and docs:

| Jargon | Clear speak |
|:-------|:------------|
| `migrate_from_legacy()` | The step that upgrades your old settings file |
| Dead code | Code nothing uses anymore |
| Parse-before-delete guard | Check the file before deleting it |
| Lazy migration trigger | The upgrade that fires on its own |
| Instantiate the client | Create the client |
| Idempotent install | Safe to run twice |
| Deterministic ordering | Always comes out in the same order |
| Silent no-op | Quietly does nothing |

And the everyday academic words that creep into any writing:

| Academic | Clear speak |
|:---------|:------------|
| Completeness audit | Gap check |
| Soundness audit | Logic check |
| Architectural analysis | Map the shape |
| Synthesize | Pull together |
| Articulate | Say clearly |
| Facilitate | Help with |

## The principle

<mark>**If a 16-year-old wouldn't understand it, rewrite it.**</mark>

Academic language creates distance. Clear speak creates connection.

## Background reading

The test, the quick transformations, and the principle above are enough for most rewrites. These docs flesh out the reasoning — open the relevant one on demand when you need the deeper detail, not on every rewrite:

1. `writing/george-orwell-rules-for-writing.md` — the six rules
2. `writing/write-clearly-simply-with-action.md` — clarity, simplicity, action
3. `writing/headings-guide-vocabulary-inside.md` — plain headings, precise terms inside

## Reference

| Resource | Path |
|:---------|:-----|
| Full workflow | `WORKFLOW.md` |

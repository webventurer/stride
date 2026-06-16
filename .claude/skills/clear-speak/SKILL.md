---
name: clear-speak
description: Rewrite jargon into plain language a non-engineer can follow on the first read. Use on stride's own writing — command files, issue drafts, commit messages, README paragraphs. Triggers on "clear-speak", "clear speak", "simpler words", "plain language", "say this simply", or when stride's output slips into jargon.
---

# Clear speak

Rewrite academic and abstract language into words that land immediately.

## What this is for

`/clear-speak` is stride's **on-demand** plain-language tool. Point it at a chunk of stride's own writing — a command file, an issue draft, a commit message, a README paragraph — and it rewrites the jargon into something a non-engineer can follow top to bottom.

<mark>**Scope: stride's own writing, not a general prose rewriter.**</mark> Command files, issue/commit/README text, and the things stride produces. Pointed at arbitrary prose it drifts toward "not stride's job" — stride's purpose is the Linear/commit workflow, not a general writing utility.

> **The canonical home of stride's plain-language rule — and the on-demand tool.** stride's commands point here for the always-on standard that keeps *new* output plain (`output-focus.md`, `/linear:finish`, `/linear:plan-work` all link to this skill); `/clear-speak` applies that same standard as a tool you invoke to *fix* text that has already drifted into jargon, anywhere in the repo.

## When to use

- Cleaning up a command file or reference doc before it ships
- Sharpening an issue title or description into a stakeholder outcome
- Rewriting a commit body so a non-engineer can follow what changed
- Any time you catch stride's output using fancy words

## The test

**Can someone understand this without a dictionary or a degree?**

If not, find simpler words.

## Quick transformations

Drawn from stride's own writing:

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

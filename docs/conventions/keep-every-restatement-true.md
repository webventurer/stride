# Keep every restatement true

> A rule stated in more than one place is a fact with copies. Change one copy and the others quietly start lying.

## The check

Before calling a change to a rule finished, ask:

1. **Where else is this claim stated?** The one-line summary, the index row, the checklist, the closing line, the worked example — each is a copy
2. **Does the example still pass the rule it demonstrates?** A rule can outgrow the example that was written to show it
3. **Could this restatement be a link instead?** A copy you did not make cannot drift

<mark>Restatements do not look like duplication. They look like prose, so nobody thinks to check them.</mark>

## Problem

A rule gets a qualifier. The document holding it is updated and reads correctly. But the index still summarises the old rule, the memorable one-liner still says the old thing, and the worked example now quietly violates the very check it was written to illustrate. Each of those was written as a sentence, not as a duplicate, so nothing signals that it needs to change with the rule. A reader who arrives through the index gets the old rule and never sees the correction.

## The convention

- After changing a rule, list every place that states it, and fix or delete each one
- Look in the fixed places first: title, one-line summary, `<mark>` insight, index row, checklist, closing line
- Re-read the worked example against the changed rule. An example that no longer passes is a defect, not decoration
- Prefer a link over a restatement. Restate only where the reader needs the claim without leaving the page
- When a restatement must exist, keep it short enough that its drift is obvious

## Example

### Before

```text
# ❌ The rule gained a qualifier; its copies did not
Rule doc:  The expected shape may name files; the outcome may not
Index:     Neither says how
Checklist: Can the outcome be stated without filenames?
Tagline:   If the card names a file, it is describing the edit
```

The rule is right. Three copies now contradict it, and two of them are what a reader meets first.

### After

```text
# ✅ Every copy carries the qualifier, or points at the rule
Rule doc:  The expected shape may name files; the outcome may not
Index:     Either may propose how — neither makes it a condition of being done
Checklist: Can the outcome be stated without filenames? An expected shape
           may name them; the outcome may not
Tagline:   The apples are the deliverable. The planting plan is a courtesy.
```

## Why this is useful

- The reader who arrives through the index gets the current rule, not the previous one
- An example checked against its own rule is the cheapest test a document has
- Deleting a restatement is usually better than maintaining it, and the sweep is where you notice
- A rule nobody contradicts is a rule people can quote

## When to avoid

- A document deliberately frozen as a record of what was true at the time — a decision log, a shipped card, a dated capture
- Restating a claim for a different audience in different words, where the paraphrase is the point. Cross-link the two so a later change finds both

## Related conventions

- **[Specify the result, not the edit](specify-the-result-not-the-edit.md)** — its checklist lives in the index as well as the document, so both move together
- **[Give each responsibility one visible home](give-each-responsibility-one-visible-home.md)** — one home means fewer copies to keep true
- **[Read the set as one document](read-the-set-as-one-document.md)** — the pass that finds drift; this convention is what you look for while making it

---

_The rule is not changed until everything that repeats it agrees._

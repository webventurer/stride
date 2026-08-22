# Read the set as one document

> When any document in a set changes, read the whole set in one pass. A contradiction between two files is a finding, not noise.

## The check

Before calling a documentation change finished, read the set end to end and ask:

1. **Does every term mean the same thing in every document?** A word that shifted meaning is a defect nobody can see from inside one file
2. **Does any document permit what another forbids?**
3. **Does each example still pass the rules of the set, not just the rules of its own page?**
4. **Does the index say what the documents now say?**
5. **Where two documents touch the same rule, is it clear which one owns it?**

<mark>A contradiction between two documents is information: either one of them is wrong, or you have found a distinction nobody has written down yet.</mark>

## Problem

Documents are edited one at a time and read one at a time, so the set is never seen whole. Every file ends up locally correct and the set ends up collectively incoherent — because the contradiction exists only in the space between two files, and no single reading covers that space. The author cannot see it, having just read one file closely. The new reader hits it immediately, arriving through the index and following links.

## The convention

- Change a document, then read the whole set in one pass before calling it done
- Read as a stranger arriving through the index, not as the author of the edit
- Record every contradiction before fixing any of them. Fixing as you read hides the pattern
- Sort each finding:
  - **Defect** — one side is wrong. Fix it
  - **Distinction** — both sides are right in different cases. Write the rule that separates them
- A set too large to read in one sitting is too large to keep consistent. Split it or shrink it

The distinctions are the point. Defects are worth fixing, but the rules worth keeping are usually found this way — in the gap between two statements that both seemed obvious until they were read next to each other.

## Example

### Before

```text
# ❌ Read one file at a time — each is locally correct
specify-the-result-not-the-edit.md   the expected shape may name files
index.md                             neither says how
give-each-responsibility-...md       one responsibility, one sentence, one directory
give-each-responsibility-...md       keep one-module responsibilities as modules
```

### After

```text
# ✅ Read the set in one pass — the findings live between the files
Defect       the index says "neither says how"; the rule now permits an
             expected shape, which is exactly saying how
Defect       the subtitle says "one directory"; rule two says a one-module
             responsibility stays a module
Distinction  "observable" was assumed to mean behaviour, but a boundary is
             proved by an import check
             -> new rule: a structural check counts as proof
```

Two defects fixed. One distinction that became part of the convention.

## Why this is useful

- The set read as one document is what a new reader actually experiences
- A contradiction marks where the thinking is unfinished — it points at the rule nobody has written yet
- Defects of this kind survive every other check, because each file passes on its own
- Cheap. A handful of short documents is one sitting

## When to avoid

- A single document with no siblings. There is no set yet
- Mid-draft, where inconsistency is expected and the pass is wasted. Do it before finishing, not throughout
- Documents deliberately holding different views for different audiences. Say so in both, or the next reader files it as a defect

## Related conventions

- **[Keep every restatement true](keep-every-restatement-true.md)** — the most common finding this pass produces, and the only one you can look for directly
- **[Specify the result, not the edit](specify-the-result-not-the-edit.md)** — its expected-shape rule came out of a set read, as a distinction rather than a defect
- **[Ask for the disproof](ask-for-the-disproof.md)** — the same move aimed at a hypothesis instead of a set of documents

---

_A contradiction between two files is a rule waiting to be written._

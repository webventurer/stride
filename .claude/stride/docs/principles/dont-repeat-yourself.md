# Write each fact once (don't repeat yourself)

> A value or rule that must be the same everywhere lives in one place, from the second copy on.

A value or rule that must be the same everywhere, such as a storage key, a limit or a rule in a document, is a fact. Written in two places, it becomes a fact with copies, and copies drift: change one and the others quietly start lying. So from the moment a second copy is needed, the fact lives in one file and every other place points at it. Code imports the value; a document links to the rule. Restatements in prose are the copies most often missed, because they don't look like duplication. They look like ordinary sentences, so nobody thinks to check them when the rule changes.

## The test

Before writing a value or rule a second time, ask: **must these two always say the same thing?** If they must, give the fact one home and point at it from the second place. When a rule changes, ask:

- **Where else is this claim stated?** The one-line summary, the index row, the checklist, the closing line and the worked example are each a copy. Look in those fixed places first.
- **Does the example still pass the rule it demonstrates?** A rule can outgrow the example written to show it, and an example that no longer passes is a defect, not decoration.
- **Could this restatement be a link instead?** A copy you did not make cannot drift.

Restate only where the reader needs the claim without leaving the page, and keep the restatement short enough that its drift is obvious.

## Worked example: a rule that gained a qualifier

A rule about cards says what each part of a card may contain. A card states its outcome, what will be true when the work is done, and may sketch an expected shape, a suggestion of how the builder might do it. The rule gains a qualifier: the expected shape may name files, and the outcome may not. The rule's own document is updated and reads correctly.

```text
# Before: the rule gained a qualifier; its copies did not
Rule doc:  The expected shape may name files; the outcome may not
Index:     Neither says how
Checklist: Can the outcome be stated without filenames?

# After: every copy carries the qualifier, or points at the rule
Rule doc:  The expected shape may name files; the outcome may not
Index:     Either may propose how; neither makes it a condition of being done
Checklist: Can the outcome be stated without filenames? An expected shape
           may name them; the outcome may not
```

In the before, the rule is right and both copies contradict it, and the copies are what a reader meets first. A reader who arrives through the index gets the old rule and never sees the correction. In the after, the reader gets the current rule wherever they arrive. The sweep that fixes the copies is also where a restatement that isn't needed gets noticed and deleted, which is usually better than keeping it true. The rule isn't changed until everything that repeats it agrees.

## Where it stops

<mark>Writing each fact once applies to facts that must stay the same, not to code that only looks alike.</mark> To tell them apart, ask: if one copy changed and the other didn't, would that be a bug? If it would, the two are one fact, and it is written once from its second copy. If it wouldn't, the two are code that happens to look alike today and may change for different reasons tomorrow. Sharing it early ties together things that will want to drift apart, so it stays apart until it has appeared three times, which [Share code only once it has appeared three times](recurrence-reveals-reality.md) covers.

Two kinds of copy are meant to stay as they are. A record deliberately frozen as what was true at the time, such as a decision log or a finished card, isn't updated when the rule changes. And a claim restated for a different audience in different words, where the paraphrase is the point, stays as its own text; link the two so a later change finds both.

## Related

- [Share code only once it has appeared three times](recurrence-reveals-reality.md): the rule for code that only looks alike, on the other side of the boundary above.
- [Keep each concern in one place](separation-of-concerns.md): one home for each concern means fewer copies to keep true.
- [Find the shared shape by removing the smallest difference first](flocking.md): how to find what is truly shared once code has repeated enough to share.

## Source

Distilled from stride's `docs/conventions/keep-every-restatement-true.md`, which holds the worked example. The example drops the source's tagline row, whose wording relies on context outside the example. The framing for values, such as a storage key that code imports, comes from the principle's line in the pack's list, and the boundary with sharing code, with its "would that be a bug?" test, is written for this page.

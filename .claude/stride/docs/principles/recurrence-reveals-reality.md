# Share code only once it has appeared three times (recurrence reveals reality)

> You can't design the right abstraction up front. Each time the same need comes back, it shows more of the shape, so wait until the shape is clear before you share the code.

The first time you see a piece of code, it's a fact. The second time, it's a coincidence: the same lines appearing again. The third time, it's a pattern, and now you can see what a shared function should own. Don't design the boundary; let recurrence reveal it. Code that only looks alike stays apart until then, because the boundary you would draw on the second copy is a guess, and a guessed abstraction doesn't fit the reality that emerges. Each new copy rules out some of the possible shapes until the right one becomes visible.

| Occurrence | What you know | Action |
|:-----------|:--------------|:-------|
| **First** | Existence: something is there | Observe |
| **Second** | Possibility: it might be real | Stay neutral |
| **Third** | Reliability: the shape is clear | Act |

## The test

Before sharing code between callers, ask:

- **How many times has this need come back?** If only once or twice, the shape may not be clear yet.
- **Can you name what the shared code would do?** Not how it works, but what it owns. If you can't name it, you can't shape it.
- **Is there enough alike to work with?** Is there duplication to remove and names to simplify? If not, wait for another copy.

Three is a heuristic, not a magic number. Sometimes two copies are enough and sometimes you need four. The third copy is usually where the shape becomes undeniable, but the shape, not the count, is what decides.

## Worked example: a sort that only looked shared

An invoice export writes a CSV file: it sorts the invoices by date, writes a header row and writes one row per invoice. A customer export is then written, and it does the same six lines: sort by date, header, rows. The author sees the second copy and considers sharing it.

| | What exists | What the third export needs |
|:--|:------------|:----------------------------|
| **Shared at the second copy** | `write_csv(path, header, rows)`, which sorts the rows by date because both callers did | The order export sorts by order number, so the function gains a `sort_key` option, and the first two callers now carry a sort setting they never chose |
| **Shared at the third copy** | `write_csv(path, header, rows)`, which writes the rows it is given; each export sorts its own rows first | Nothing extra: three short calls and a function with no options |

Waiting cost two copies of six lines for a while, which was cheap to read and cheap to change. With two copies, sorting by date looked like part of the shape. The third copy showed it was a coincidence, and that what all three exports share is writing a header and rows. The function drawn at three copies holds only that, and its name says what it does. When a fourth export arrives, it fits without an option.

## Where it stops

<mark>Waiting for the third copy applies to code that only looks alike, not to a fact that must stay the same everywhere.</mark> A storage key, a price rule or a file path that every caller must agree on is written once from its second copy, because two copies of a fact drift apart. [Write each fact once](dont-repeat-yourself.md) sets out where the line between the two falls.

Nor is waiting an excuse to stop looking. Once the third copy arrives, or the shape becomes clear sooner, the evidence is in, and leaving the duplication any longer only adds cost.

## Related

- [Write each fact once](dont-repeat-yourself.md): owns the boundary between a fact that must stay the same and code that only looks alike.
- [Find the shared shape by removing the smallest difference first](flocking.md): flocking is the mechanism for drawing the shape; recurrence is the timing that gives it enough copies to work with.
- [Don't build it until you need it](yagni.md): what has appeared once is not yet a pattern.
- [Decide only when a requirement forces you to](postpone-decisions.md): each new copy supplies the facts a postponed decision was waiting for.

## Source

Distilled from codefu's `.claude/docs/principles/recurrence-reveals-reality.md`, which holds the longer argument and its links to abstraction and meta-cognition. The worked example is written for this page. Codefu's `/earn-extraction` skill applies this principle.

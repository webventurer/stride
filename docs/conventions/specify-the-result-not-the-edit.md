# Specify the result, not the edit

> A card declares the state that must hold when the work is complete, not the changes that produce it.

## The check

Before writing the card, ask:

1. **Can the outcome be stated without filenames?** The expected shape may name files; the outcome may not
2. **Does the specification describe observable completion?** Use behaviour where behaviour changes; use a structural check — an import assertion or a directory's contents — where the result is a boundary. A result nobody can check is not a result
3. **Is there exactly one responsibility?** If the card joins unrelated outcomes, split it
4. **Is its boundary explicit?** Say what crosses it and what must stay outside it
5. **Are package and module choices proportional to the code that exists now?** Keep one-module responsibilities as modules
6. **Could another implementation satisfy the same specification?** If only one sequence of edits satisfies it, it is a plan, not a specification

<mark>A card written as edits is satisfied by making the edits, whether or not the result holds.</mark>

## Problem

A card that lists changes gets closed when the changes land. Nobody checks whether the intended state is true, because the card never said what that state was. Halfway through, a better implementation appears and the card is now wrong — so it gets followed anyway, or silently ignored.

## The convention

Every card should declare:

- What must be true when the work is complete
- Which responsibility owns that result
- What crosses the responsibility boundary
- What must no longer happen
- What proves the result — behaviour, or a structural check where the result is a boundary

Preferred form:

> Any implementation should remain valid if it produces the declared result.

The card defines done. When work begins, `/linear:start` inspects the current repository and derives the implementation checklist. See [Derive the plan when work starts](derive-the-plan-when-work-starts.md).

The responsibility a card names has to have a home. Module versus package, naming, and where the responsibility statement lives are in [Give each responsibility one visible home](give-each-responsibility-one-visible-home.md).

A card may also record the expected shape — proposed modules, names, sequence. Mark it non-binding. It is a head start for the implementer, not a condition of completion, and the design thinking behind a good name is worth keeping even when the split turns out differently.

Include it only when a layout was actually chosen. A card whose deliverable is a document, a test module, or a single behaviour change has no layout to propose, and an empty shape section invented to fill the template is worse than none.

**Apples and orchards.** The result is the apples — what has to be in the barn at harvest. The expected shape is where you thought to plant the trees. You are judged on the apples. If the north slope turns out to be clay, plant elsewhere and still bring the apples in. But the planting plan is worth writing down: someone walked the ground and thought about sun and drainage, and throwing it away makes the next person walk it again.

## Example

### Before

```text
# ❌ Describes the edit
Move the retry logic out of polling.py into a new retries.py.
Update the three call sites. Add a test for the new module.
```

### After

```text
# ✅ Describes the result
A failed poll retries on its own schedule, and polling no longer
decides when a retry happens.

Owner: strategy — it holds the polling claim.
Crosses the boundary: the poll outcome goes in; a retry decision comes out.
No longer happens: polling code reads retry settings.
Proven by: a poll that fails twice is attempted three times, and
polling's own tests need no retry fixtures.
```

### A card's "What we'll do"

The same move, one section down — results, with the layout riding alongside and labelled.

```markdown
Give the account responsibility one home.

- Live account and symbol settings are interpreted in one place
- Comparisons with configured intent are separate from the mutations that fix them
- Validation and correction are reached through the account package, not its internals
- No caller outside the package imports an internal account module

**Expected shape** — current best layout, not binding. A different split that
produces the result above is fine.

| Module | Holds |
|:--|:--|
| `account/current_settings.py` | interpretation of live account and symbol settings |
| `account/checks.py` | comparisons with configured intent |
| `account/setup.py` | validation and correction |
| `account/__init__.py` | the responsibility statement and the public operations |
```

Four bullets a reviewer can check. One table an implementer can start from. Neither pretending to be the other.

## Why this is useful

- The card can only be closed when the state it names is true
- A better implementation found mid-work does not invalidate the card
- The reviewer checks behaviour, not diff shape
- "What must no longer happen" catches the half-migration that leaves both paths alive
- Naming work survives without becoming an instruction the implementer cannot argue with

## When to avoid

- A mechanical change with no observable result — a rename, a formatting sweep. State the scope instead
- A spike whose purpose is to find out what the result should be
- A card with no layout decision in it. No shape section, rather than a section restating the one obvious file
- An expected shape you are not willing to have overridden. That is an orchard-layout card, not an apples card — declare the layout as the result and say why

## Related conventions

- **[Derive the plan when work starts](derive-the-plan-when-work-starts.md)** — turns the declared result into a visible route using current repository evidence
- **[Give each responsibility one visible home](give-each-responsibility-one-visible-home.md)** — the owner a card names has to exist somewhere
- **[Keep every restatement true](keep-every-restatement-true.md)** — this rule is restated in the index checklist; change one and check the other
- **[Read the set as one document](read-the-set-as-one-document.md)** — the expected-shape rule was found by reading this convention next to the others
- **[Ask for the disproof](ask-for-the-disproof.md)** — the result a card declares is what a disproof attempt aims at

---

_The apples are the deliverable. The planting plan is a courtesy._

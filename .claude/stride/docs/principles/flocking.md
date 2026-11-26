# Find the shared shape by removing the smallest difference first (flocking)

> When you can't see what messy code ought to look like, take the two most alike pieces and remove the smallest difference between them, one step at a time, until the shape appears.

You don't have to see the abstraction in advance. Birds flock without a leader because each one follows a few simple local rules, and good structure in code can emerge the same way: from small, behaviour-preserving changes applied one after another, not from a design drawn up front. Without this, you either stare at messy code waiting for the right design to occur to you, or you rewrite it in one leap to the shape you guess it should have, and when the tests fail you can't tell which part of the leap broke them.

## The test

When you face similar code and can't see the shared shape, apply the three flocking rules in order:

- **Select the most alike things.** Find the most similar cases: methods with the same shape, arguments with the same name, conditionals with a similar structure.
- **Find the smallest difference.** Between those cases, pinpoint the smallest difference, not the biggest.
- **Make the simplest change.** Remove that difference with the simplest possible change. Sometimes you first make the pieces more alike before you can make them identical.

Work in small steps: change one line at a time, run the tests after every change, and if they fail, undo and make a better change. As you gain experience you will take larger steps, but when a big step fails, revert it and take a smaller one. Small changes mean the error messages point at the one line that caused them.

## Worked example: a basket summary

A shop page prints a line about the basket. It was written one case at a time, and each branch reads plainly. A wish list now wants the same kind of line, and the author can't yet see what the branches share. A careful author might rewrite the function in one pass to the general shape they expect; flocking takes it one difference at a time instead.

```python
# Before: three branches written one case at a time; the shared shape is hidden
def basket_summary(count):
    if count == 0:
        return "Your basket is empty."
    if count == 1:
        return "Your basket has 1 item."
    return f"Your basket has {count} items."

# After: the two alike branches flocked into one, and the concept they hid has a name
def basket_summary(count):
    if count == 0:
        return "Your basket is empty."
    return f"Your basket has {count} {unit(count)}."

def unit(count):
    return "item" if count == 1 else "items"
```

The two most alike branches are the last two. Between them there are two differences: `1` against `{count}`, and `item` against `items`. The smallest is `1` against `{count}`, because when `count` is 1 the two print the same, so the first step changes `1` to `{count}` and the tests pass. The next difference, `item` against `items`, needs a concept that varies with the count, so the second step adds `unit(count)` and uses it in both branches. The tests pass, the branches are now identical, and the third step deletes one. The empty basket stays its own branch, because its sentence has a different shape and there is no small difference to remove. Every step left the tests passing, and `unit` is a name nobody planned: it came out of the difference. The wish list can now reuse `unit` without copying a branch.

## Where it stops

<mark>Flocking finds the shape; it doesn't tell you when there are enough copies to look for one.</mark> With one copy there is nothing to remove, and with two you can see similarity but not always the shape. [Share code only once it has appeared three times](recurrence-reveals-reality.md) sets that timing.

Nor does every refactoring step improve the code. A step can make things worse, which disproves an idea cheaply, because each step is as easy to revert as it was to make. That safety is what lets you explore the problem without a plan.

## Related

- [Share code only once it has appeared three times](recurrence-reveals-reality.md): recurrence is the timing; flocking is the mechanism that works on the copies.
- [Do the simplest thing that works](simplest-thing-that-works.md): each flocking step is the simplest change that removes one difference.
- [Name things for what they do](name-things-for-what-they-do.md): the concept a difference reveals needs a name that says what it does, such as `unit`.

## Source

Distilled from codefu's `.claude/docs/principles/flocking.md`, which holds the bird rules, the refactoring decision tree and questions for spotting patterns in code. The worked example is written for this page. Codefu's `/flock` skill applies this principle.

Further reading: **Sandi Metz**, *99 Bottles of OOP*: where the flocking rules for code come from, worked through a full refactoring.

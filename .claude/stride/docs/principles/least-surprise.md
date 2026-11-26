# Make code do what a reader expects (least surprise)

> Code behaves the way its name and the usual conventions lead a reader to expect.

A reader comes to code with expectations already formed: by the conventions they have met elsewhere, by what a thing is called, by where it appears, and by how similar things in the same code behaved. Least surprise asks the code to match those expectations. Each time it doesn't, the reader has to stop, work out what happened, and repair their picture of how the code works. That costs time, makes them trust their next guess less, and the mistakes they make in the meantime turn into bugs. Following the convention by default, and keeping similar operations alike, means what a reader learns in one place holds everywhere.

## The test

Before settling how something behaves, ask: **if a reader guessed what this does, would they be right?** If not, change the behaviour to match the guess, or change what sets the guess. Four checks find the mismatch:

- **Expectation:** if a reader expected X to happen, what actually happens?
- **Convention:** is this consistent with the patterns readers already know, such as a `get` method that changes nothing or an `is` prefix that returns true or false?
- **Name:** does the name describe the behaviour, or suggest something else?
- **Similarity:** do similar operations behave similarly? Inconsistency between similar things surprises most of all, because the reader had every reason to expect them to match.

## Worked example: two lookups that fail in different ways

A billing module has two lookups, written at different times. The invoice lookup returns nothing when the invoice is missing. The author of the customer lookup decides a missing customer is always a bug, so it should fail loudly where the bug is.

```python
# Before: two lookups that look alike handle a missing record differently
def find_invoice(invoice_id):
    return INVOICES.get(invoice_id)    # None when missing

def find_customer(customer_id):
    return CUSTOMERS[customer_id]      # raises KeyError when missing

# A caller who has used find_invoice writes the same check, and it never runs:
customer = find_customer(customer_id)
if customer is None:
    return "No such customer"


# After: both lookups follow one convention, and the failing case has its own name
def find_invoice(invoice_id):
    return INVOICES.get(invoice_id)

def find_customer(customer_id):
    return CUSTOMERS.get(customer_id)

def require_customer(customer_id):
    return CUSTOMERS[customer_id]
```

Each choice in the before was reasonable on its own, and the surprise came from the pair. Now a reader who learns how `find_invoice` behaves knows how every `find_` behaves, and the caller's check works. The case the author cared about, a missing customer that should stop the program, still exists, and its name tells the caller what they are getting. The next lookup someone adds has a convention to follow.

## Where it stops

<mark>Least surprise doesn't forbid surprise: a destructive action should sometimes be harder to do than a reader expects.</mark> Asking for an extra confirmation before deleting something for good, or putting a dangerous action where a hand won't land on it by habit, is surprise that prevents accidents. Speed can justify it too, such as an editor whose keys do different things in different modes, which surprises newcomers and repays those who learn it. A specialised field may also have conventions of its own that outweigh the general ones. Before breaking an expectation, ask:

1. **Is there a real need?** Not just wanting to be different.
2. **Does the benefit outweigh the cost?** Surprise has a real cost.
3. **Can the difference be made clear?** Surprise plus confusion is worse than surprise alone.
4. **Is there no other way?** The goal may be reachable without the surprise.

Where the surprise stays, say so beside the code, so the next reader meets it as a fact rather than a bug.

## Related

- [Name things for what they do](name-things-for-what-they-do.md): how to choose the name that sets the reader's expectation.
- [Do the simplest thing that works](simplest-thing-that-works.md): the obvious solution is usually the unsurprising one.

## Source

Distilled from codefu's `.claude/docs/principles/principle-of-least-surprise.md`, also known as the principle of least astonishment. The worked example is written for this page.

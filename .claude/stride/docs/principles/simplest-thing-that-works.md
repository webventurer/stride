# Do the simplest thing that works

> When stuck or facing complexity, ask what the simplest thing that could possibly work is, and build that.

Prefer the obvious solution over the clever one. When you try to handle error checking, future flexibility, performance and edge cases all at once, there is no room left to think about the problem itself, so solve the immediate need first. The question is also a way out of being stuck: get something concrete written that you can look at, because writing it organises your thinking. Complexity has to earn its place by solving a real problem. Without this, work stalls in analysis, and what does get built carries machinery nobody needed, which every later change has to work around.

## The test

Before building, ask:

- **Will this help me make rapid progress against the real problem?** If not, it is probably over-engineered or off target.
- **Does this capture the core 20% of the work that delivers 80% of the value?** Build the essential part users actually need, and defer edge cases and nice-to-haves until they prove necessary.
- **Can I hold the whole solution in my head while I work on it?** If you can't, or can't explain it clearly to a colleague, it isn't simple enough yet.
- **Am I solving today's problem or tomorrow's speculation?** Build for the requirement in front of you.

The usual moves follow from these: a linear search before a binary one until speed is shown to matter, a hard-coded value before a configuration system until the value actually varies, one case before many, and an `if` before a framework until several cases show the pattern. Push hard for simplicity until simplicity fights back, which is when removing anything more would stop the solution doing its job.

## Worked example: looking up a customer

An invoice screen shows the customer for each invoice, looked up by ID from a list of about forty customers loaded at start-up. The lookup runs for every invoice on the screen, so the author builds an index to keep it fast.

```python
# Before: an index kept alongside the list, which every change must update
class CustomerIndex:
    def __init__(self, customers):
        self.customers = customers
        self.by_id = {customer.id: customer for customer in customers}

    def add(self, customer):
        self.customers.append(customer)
        self.by_id[customer.id] = customer

    def remove(self, customer):
        self.customers.remove(customer)
        del self.by_id[customer.id]

    def find(self, customer_id):
        return self.by_id.get(customer_id)


# After: search the list, which is short enough that the search costs nothing
def find_customer(customers, customer_id):
    return next((customer for customer in customers if customer.id == customer_id), None)
```

The index keeps a second copy of the customers that has to stay in step with the list. Any code that changes the list directly, without going through `add` or `remove`, leaves the index wrong, and nothing warns that it has happened. The search through forty customers takes a few microseconds, and the screen behaves exactly as before. If the list grows and the lookup shows up as slow when measured, the index is built then, and the measurement says where it is needed.

## Where it stops

<mark>The simplest thing still has to work.</mark> It is not the most stupid thing, nor something that clearly can't work: make it as simple as possible, but not simpler. If the solution doesn't solve the problem, leaves out what users need to get their basic task done, or is so minimal it is unclear, it has gone too simple. Some problems are complex in themselves, and pushing for simplicity is how you find out where the complexity is genuinely needed; let it in there.

Nor does it excuse leaving out error handling that matters. Check for errors where real failures can happen, and leave out checks for errors that cannot occur, which only add noise. Where the question is what to leave unbuilt rather than what to build, [Don't build it until you need it](yagni.md) takes over.

## Related

- [Don't build it until you need it](yagni.md): where YAGNI says what to leave out, this says what to build.
- [Use what already exists before building something new](leverage-existing-mechanisms.md): the simplest thing is often already built.
- [Be agile](be-agile.md): the simple version is the small step, and what it teaches shapes the next one.

## Source

Distilled from codefu's `.claude/docs/principles/the-simplest-thing-that-could-possibly-work.md`, which holds the principle's origin story and answers to the common objections. codefu's `/strive-for-simplicity` skill applies this principle to code. The worked example is written for this page.

Further reading: **Ward Cunningham**, interviewed by Bill Venners, "The Simplest Thing that Could Possibly Work" (Artima): where the question comes from and why it breaks a deadlock. **Ron Jeffries**, "Do the Simplest Thing that Could Possibly Work": how the practice is applied in Extreme Programming, and the reminder that the simplest thing must still work.

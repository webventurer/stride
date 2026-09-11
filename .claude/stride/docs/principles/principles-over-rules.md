# Principles over rules

**Start with the principle when one is available. Let the guidance follow from what it means in this context.** Keep the reason visible so someone facing a different situation can make a good decision too.

A programming principle is a guiding belief that helps people create software others can understand, maintain and change. Following a rule is easy to check; deciding whether it serves its purpose takes judgement. This is the thinking behind stride's [Vision](../../../../VISION.md): apply guardrails that encourage discipline without obstructing flow.

## Why the distinction matters

In [Living by principles instead of by rules](https://sandradodd.com/rules), Deb Lewis distinguishes choosing an action because you believe in its value from complying because someone else demands it. People learn principles by seeing them lived and experiencing their benefits. A rule tells you what to follow or break; understanding the principle helps you choose in situations nobody wrote a rule for.

That distinction comes from a discussion about family life. Applied to software, it invites us to explain what our guidance protects, rather than treating compliance as proof of good design.

| Kind of guidance | What it provides | Example |
|:-----------------|:-----------------|:--------|
| Principle | A value or purpose to guide judgement | Make behaviour clear to a human reader. |
| Rule of thumb | A useful shortcut that can fail in some contexts | Prefer a small number of function arguments. |
| Rule | A specific requirement within a defined scope | Reject an entry that exceeds the agreed limit. |
| Dogma | A belief treated as beyond question | Every extra argument is bad, regardless of what it expresses. |

A principle and a heuristic are related, but not identical: the principle gives direction; the heuristic suggests a practical starting point. Calling something a principle does not prevent it becoming dogma if we refuse to examine whether it helps.

## Let the specifics follow from the purpose

For software behaviour, we still need precise decisions. **Principles guide the choice; concrete requirements make the chosen behaviour predictable and testable.**

**Principle → context → concrete requirements → observable checks.** Applying a principle should lead to a decision someone can implement and test: what happens, under which conditions, and how we know it works. Explain the connection. A principle alone may not determine a threshold or exception; identify those choices and the evidence or agreement needed to settle them.

Two useful starting principles are:

- Aim for correct code that expresses its behaviour as clearly and simply as possible to a human reader.
- When alternatives deliver roughly the same value, prefer the one that makes future change easier. See [design decisions](design-decisions.md#choose-the-path-that-makes-change-easier).

When a decision is unclear, return to what you are trying to achieve. Consider the actual readers, dependencies, risks and likely changes. Then explain why a particular choice serves that purpose here. If no established principle fits, describe the concrete requirement or evidence; inventing a grand principle adds nothing.

This gives rules a reason and a scope. It also gives you a way to weigh competing concerns: a little duplication might be clearer than an abstraction, while shared behaviour that repeatedly changes together might justify extraction. Neither a line count nor a slogan settles that choice.

## Examples of judgement

### Function arguments

“No more than four arguments” is a prompt to look closer. The concerns behind it might be confusing call sites, values that are easy to swap, hidden relationships, or several responsibilities mixed together.

A fifth argument can be the clearest expression of the operation. If several arguments describe one meaningful concept, grouping them may help. Hiding unrelated values in an options object merely to satisfy the count leaves the original problem in place.

### Naming a directory

Instead of choosing a universal winner among `folder`, `dir` and `directory`, ask what a reader needs to understand. `source_directory` and `destination_directory` can express distinct roles clearly. `folder` may fit a user-facing concept or an established local vocabulary.

In Python, `dir` is an abbreviation and the name of a built-in function; using it as a variable can obscure meaning and shadow that function. It is not a reserved keyword. The principle is clarity in context, rather than a ban on every abbreviation.

### Copying a folder

“Don't copy folders” hides the reason. A more useful concern is avoiding unnecessary maintenance debt: two copies of shared behaviour can drift and make every later fix cost twice.

Copying a template to create an independent starting point may be appropriate. Copying a maintained subsystem to avoid understanding its dependencies may be expensive. Ask who will own the copies and whether they should change together.

### Writing a Linear story

The principle is that a reader should understand why the work matters and predict what the proposed change will do. That explains the order in [story.md](../../../commands/linear/reference/templates/story.md): **Why this matters → Where things stand → What we'll do**.

Within “What we'll do”, name the relevant principle when one exists, then explain how the proposed behaviour follows from it. Concrete triggers, checks, exceptions and examples make that reasoning usable. Configuration names and file lists come after the explanation. The principle gives the reader a reason; the details let them implement and verify the decision.

## Familiar programming principles

KISS (keep it simple) encourages the simplest understandable design that meets the need. YAGNI (you ain't gonna need it) encourages postponing capabilities until they are needed; it does not mean neglecting the work that keeps today's code easy to change. These are compatible aims, rather than instructions to minimise every line. See [Fowler on YAGNI](https://martinfowler.com/bliki/Yagni.html).

SOLID offers principles for keeping object-oriented software understandable and changeable. Three relevant examples are:

- **Single responsibility:** group work that changes for the same reason; separate independent reasons to change. “Do one thing well” does not mean one method per class. See [single responsibility](single-responsibility-principle.md).
- **Open/closed:** arrange useful boundaries so new behaviour can be added without repeatedly disturbing stable code. It does not mean existing code must never be edited.
- **Dependency inversion:** keep high-level policy from depending directly on low-level details; let both depend on suitable abstractions, whose meaning is not dictated by those details. See [Robert C. Martin's design principles](https://objectmentor.com/resources/articles/Principles_and_Patterns.pdf).

Dependency injection is a technique, not a synonym for dependency inversion. Supplying a dependency through a constructor is one form of injection; it is not the only form, nor a reason to create an interface or framework without a need. See [Fowler on dependency injection](https://martinfowler.com/articles/injection.html).

## Build judgement through small experiments

Design is a craft: read the code, notice what feels difficult, try a change, and see whether it improves the result. Sometimes you need to write an alternative before you can judge it. The undo button is part of the process.

Prefer familiar idioms and simple concepts so future readers have less to learn. An additional concept can earn its place when it makes the behaviour significantly easier to understand. Try it, check correctness, and keep it only if the benefit pays for the added complexity.

Experience helps you recognise tensions, but a feeling is a starting signal, not proof. Explain what became clearer or easier to change. Treat inherited advice as suggestions to understand and test, rather than lore to repeat.

## Keep rules connected to their reasons

“When you have principles there's no need for rules” captures an aspiration towards understanding, but becomes another absolute if taken literally. Rules of thumb help people learn. Precise requirements help people coordinate and make automated behaviour predictable.

Principles do not silently override an agreed constraint. A configured limit still needs an exact boundary and defined behaviour when it is reached. The principle helps explain and evaluate that policy; changing the policy remains an explicit decision.

When writing guidance, preserve the purpose, the context in which it applies, and the consequence it is meant to avoid. Prefer “this helps because…” and “in this situation…” to unsupported “always” and “never”. The aim is to help someone make the next good decision, including when the next context is different.

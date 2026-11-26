# Name things for what they do

> A name says what the code achieves for its caller, and the code keeps that promise.

A name is a claim about what the code does, read at every place the code is used. It should say what the code achieves for its caller, not how it works, so it still holds when the way it works changes. The code must do everything the name promises and nothing the name hides. Each idea gets one name, used everywhere. And a comment that explains what a block of code does is a name waiting to happen: move the block into a function and let the comment become its name. Without this, a reader has to open every function to learn what it does, and a name that has stopped being true is a lie nothing will catch. When the code changes and the name stops being true, rename it: that repairs documentation that has gone wrong.

## The test

Before settling on a name, ask: **can a reader tell what this does from the line that uses it, without opening it, and does the body do exactly that?** Then check it against each of these:

- **Command or query:** could you call it twice, or not at all, and leave the system unchanged? Then it is a query, named for the fact it reports (`function_count(block)`, not `function_count_of(block)`, whose `_of` only says the two are related); otherwise it is a command and takes a verb (`save_order(order)`). A query that converts its input, such as `parse_headers(response)`, may keep its verb.
- **What, not how:** will the name still make sense if the way it works changes? `format_name()` survives a new algorithm; `split_and_join()` doesn't.
- **A class:** does the name say what it is (`TextFile`, with a `content()` method) rather than what it does (`FileLoader`)?
- **One idea, one name:** is this idea called the same thing everywhere, and is this word used for nothing else?
- **The comment:** does a comment explain what this block does? Move the block into a function named for it, and delete the comment.
- **The right size:** is the name neither too vague (`get_data()`) nor tied to a detail that will change (`get_pending_trades()` when callers rely on getting every open trade)?
- **Easy to work with:** can it be said aloud, found by a search, and read without knowing a joke or a project nickname (`yeet_old_records()` is `delete_expired_records()`)?

Reading a name aloud chooses between candidates that fit; it never decides whether a function takes a verb. What the function does to the world decides that.

## Worked example: a script that writes welcome letters

A script writes each new customer's welcome letter into its own folder. Each name below was chosen because it sounded right at the time.

```python
# Before: names say how, one hides an effect, one idea has two names, and a comment does a name's job
def cleaned_path_for(client):
    path = OUTPUT / client.id
    path.mkdir(exist_ok=True)
    return path

def split_and_join(name):
    return " ".join(name.split())

def write_letter(customer):
    path = cleaned_path_for(customer)
    # greet the customer by name, with stray spaces removed
    greeting = f"Dear {split_and_join(customer.name)},"
    (path / "letter.txt").write_text(greeting)


# After: each name says what it achieves, and each body keeps the promise
def prepare_output_dir(customer):
    path = OUTPUT / customer.id
    path.mkdir(exist_ok=True)
    return path

def format_name(name):
    return " ".join(name.split())

def letter_greeting(customer):
    return f"Dear {format_name(customer.name)},"

def write_letter(customer):
    (prepare_output_dir(customer) / "letter.txt").write_text(letter_greeting(customer))
```

`cleaned_path_for` read as a lookup, with a `_for` that named no fact, but created a folder, so a caller couldn't tell anything had changed on disk; `prepare_output_dir` takes a verb because it has an effect. `split_and_join` described how it worked, and `format_name` describes the service, so it stays true if the formatting later capitalises too. `client` and `customer` were one idea with two names, and a reader had to check they were the same. The comment became `letter_greeting`, which can now be tested on its own. The letters come out the same as before.

## Where it stops

<mark>Naming a thing for what it does doesn't mean spelling out every step: a name that repeats what its module already says is longer, not clearer.</mark> Domain terms that are already exact, such as `serialize()`, `commit()` and `rollback()`, need nothing added, nor do tiny utilities whose body is obvious, such as `min()`. A public name other code depends on, such as an external API, may have to stay as it is. A comment that records something the reader can't find in the code, such as how an outside system behaves, stays as a comment. Whether the code behaves the way its name and the usual conventions lead a reader to expect is [Make code do what a reader expects](least-surprise.md).

## Related

- [Make code do what a reader expects](least-surprise.md): the name sets an expectation, and that page is about the behaviour matching it.
- [Give each piece of code one reason to change](single-responsibility-principle.md): a name that needs "and" is usually two functions.
- [Write each fact once](dont-repeat-yourself.md): one name for each idea is the naming case of writing each fact once.

## Source

Distilled from codefu's `.claude/skills/namer/SKILL.md` and `docs/naming/principles/` (its README and the seven pages it lists: consistency, understandability, specificity, brevity, searchability, pronounceability and austerity), with the promise and comment points from `docs/naming/conventions/general/self-documenting-names.md` and `docs/patterns/python/readability/self-documenting-code.md`. The worked example recasts the namer skill's examples, with the client and customer pair from `consistency.md`, as one before and after. Codefu's `/namer` skill applies this principle.

Further reading: *Naming Things: The Hardest Problem in Software Engineering*, and **Tom Benner**'s article "The 7 principles of naming": the fuller explanations and trade-offs behind the naming principles.

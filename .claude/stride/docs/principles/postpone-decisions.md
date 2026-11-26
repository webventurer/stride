# Decide only when a requirement forces you to (postpone decisions)

> A decision made before a requirement forces it is a guess, so keep the ability to decide later.

Any design decision made ahead of a real requirement rests on a guess about what will be needed. Guesses are often wrong, and a wrong shape is harder to undo than a missing one, because other code has by then been written to fit it. The move is to leave the decision open, shape the code so that deciding later stays cheap, and let the requirement that forces the decision supply the facts.

## The test

Compare the cost of deciding now with the cost of deciding later. **When the future cost of waiting equals the cost of deciding now, wait.** Waiting costs nothing extra, and the requirement that arrives will say what the decision should be.

Decide now only when waiting would cost more: when other code is about to depend on the choice, or when changing it later would mean rewriting those callers. A piece of code with no dependencies, whose changes have no consequences, can stay imperfect, because nothing relies on its shape. When it acquires dependencies, those dependencies supply the information needed to decide its design well.

## Worked example: where to put date formatting

A weekly report prints dates as day, short month and year. The author sees that email will want dates too, and considers a shared `formatting` module with a locale option, a time zone option and a choice of long or short form.

| | What exists | What a reader must understand |
|:--|:------------|:------------------------------|
| **Decided now** | `formatting.format_date(date, locale, zone, style)` and a `formatting` module, with the report as its one caller | A module, three options and their defaults, none of which any caller needs |
| **Decision postponed** | A private `report_date(date)` in the report file | One function that does one thing |

The author postpones. The report keeps its private function, and nothing else depends on it.

A month later the email needs dates, and it needs the time zone shown, which the report never did. Now two callers exist, and the difference between them is known: one shows the zone and one doesn't. The shared function takes one option, `show_zone`, and the module is named for what it holds. The guessed version would have offered a locale option nobody uses and no way to show the zone nobody expected to need.

## Where it stops

<mark>Postponing a decision is not drifting.</mark> It applies to choices no requirement has forced yet. Once a requirement forces the choice, such as a second caller, a recurring change or a dependency that has arrived, the information is in and waiting further only adds cost.

It is also not the same as [don't build it until you need it](yagni.md), the principle it is most often confused with. YAGNI is about **not building** what nothing needs yet. Postponing a decision is about **not committing to a shape** until a requirement says what shape it should be. In the example, the shared module is a YAGNI failure, because nothing needs it yet. Its three options commit to a shape before a second caller shows what varies, which is the decision to postpone. The report's private function still gets built, because the report needs it today.

Nor does it excuse messy code. Postponing means keeping the code simple, named clearly and loosely coupled, which is what makes the later decision cheap to carry out. Design is more the art of preserving changeability than the act of achieving perfection.

## Related

- [Don't build it until you need it](yagni.md): the neighbouring principle about what to leave unbuilt.
- [Give each piece of code one reason to change](single-responsibility-principle.md): where postponing sits in the argument for keeping code small and changeable.
- [Do the simplest thing that works](simplest-thing-that-works.md): the positive instruction that keeps early code easy to reshape.
- [Share code only once it has appeared three times](recurrence-reveals-reality.md): what repeats supplies the facts a postponed decision was waiting for.
- [Earn the split](avoid-premature-organisation.md): the same patience applied to files, folders and sections.

## Source

Distilled from codefu's `.claude/docs/principles/postpone-decisions.md`, which holds the longer argument.

Further reading: **Sandi Metz**, *Practical Object-Oriented Design* (2012, 2nd edition 2018): the source of the rule that any decision made ahead of an explicit requirement is a guess.

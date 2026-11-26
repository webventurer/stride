# Be agile (agility)

- Agility
    - Find out where you are.
    - Take a small step towards your goal.
    - Adjust your understanding based on what you learned.
    - Repeat.
- When faced with **two or more alternatives** that deliver roughly the same value, **take the path that makes future change easier**.

Agility is not a process you follow but how you do the work: you never know enough at the start to plan the whole route, so you take a small step, look at what it taught you, and change the plan before the next one. The rule for choosing between alternatives is how to choose each step. A good design is easier to change than a bad one, and every other principle in this pack is a case of that: code not written, a decision left open, a concern kept in one place and a clear name are all easier to change than their opposites. Stride runs the loop at the start of every card, reading what has changed since the card was written before building it. Without agility, a plan made with the least information is carried out as written, and its mistakes surface late and large.

## The test

- Before the next step, ask: **what did the last step teach me, and does the plan still say the right thing?** If it doesn't, change the plan first, then take the step.
- When two options deliver roughly the same value, ask: **which one is easier to change if I turn out to be wrong?** Take that one, and avoid the one-way street that can't be backed out of.

## Worked example: moving to a shared total one page at a time

Twelve report pages each add up their own invoice lines. The plan is one shared `invoice_total()` that every page calls. Switching all twelve in one change looks tidy: one review, one release, and no stretch where some pages use the old code and some the new.

| | What was done | What it cost |
|:--|:--------------|:-------------|
| **Before** | Write `invoice_total()`, switch all twelve pages to it in one change, then run the reports | Two pages turn out to leave tax out of their totals. The difference shows up at the end, inside a change touching twelve pages, and finding which pages moved means checking all twelve |
| **After** | Read how each page totals today. Switch one page and compare its output with the old figures. The second page shows that some totals leave tax out, so `invoice_total()` gains an `include_tax` option before the other ten move. Repeat | Each surprise arrives while one page is in play, and the function is shaped by what the pages showed rather than by the first guess |

The steps cost a few more reviews, and every page ends up calling the same function as before. What changed is when the tax difference was learned: on page two, while it was cheap to absorb, rather than at the end. Moving one page at a time is also the path that makes change easier, because any single step can be undone without touching the other eleven.

## Where it stops

<mark>Agility doesn't mean working without a plan.</mark> The small step is a step towards a goal, and the plan is a map, not a contract: when the ground changes, update the map before you walk on. Small steps are not an excuse for careless ones either; the point is to make mistakes small and correctable, not to make more of them.

The rule for choosing between alternatives only breaks ties. When one option clearly delivers more value, take it even if it is harder to change. When a choice doesn't need making yet, [Decide only when a requirement forces you to](postpone-decisions.md) takes over.

## Related

- [Start from the principle, not the rule](principles-over-rules.md): how every principle in the pack, this one included, is applied.
- [Decide only when a requirement forces you to](postpone-decisions.md): keeping a choice open is the path that makes change easier when nothing forces it yet.
- [Do the simplest thing that works](simplest-thing-that-works.md): what the small step should be.
- [When a fix needs another fix, stop and find the cause](friction-is-information.md): what to do when a step teaches you the plan is wrong.

## Source

Distilled from codefu's `docs/research/agile/what-agile-really-means.md`, and from stride's `.claude/commands/linear/reference/agility.md` for how the loop runs at the start of every card. codefu's `/agility` skill applies this principle. The worked example is written for this page.

Further reading: **Dave Thomas**, "Agile is Dead" (GOTO 2015): where the four steps and the rule for choosing between alternatives come from. **Dave Thomas**, "Time to Kill Agile" (2014): the blog post behind the talk.

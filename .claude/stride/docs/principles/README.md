# Principles

Stride's principles, most important first. Each name links to its page.

## How to work

1. **[Start from the principle, not the rule](principles-over-rules.md)** (principles over rules). Apply each principle to the case in front of you and keep the reason visible.
2. **[Be agile](be-agile.md)** (agility). Find out where you are, take a small step, adjust, repeat; between equal options, take the path that makes future change easier.

## Build less

3. **[Don't build it until you need it](yagni.md)** (YAGNI). Code not written costs nothing to read, test or change.
4. **[Use what already exists before building something new](leverage-existing-mechanisms.md)** (leverage existing mechanisms).
5. **[Do the simplest thing that works](simplest-thing-that-works.md).** The obvious solution over the clever one.
6. **[Decide only when a requirement forces you to](postpone-decisions.md)** (postpone decisions). A decision made early is a guess.

## Give each thing one home

7. **[Give each piece of code one reason to change](single-responsibility-principle.md)** (single responsibility). If describing it needs "and", split it.
8. **[Earn the split](avoid-premature-organisation.md)** (avoid premature organisation). Work on a new thing as one blob until it is clear; split it only when you need to.
9. **[Keep each concern in one place](separation-of-concerns.md)** (separation of concerns). When one concern changes, one place is edited.
10. **[Put one thing in each file](one-thing-per-file.md).** A thing earns its own file once it has its own reason to change.
11. **[Keep structure apart from styling](keep-structure-apart-from-styling.md).** A component holds structure; its look comes from stylesheets.

## Make code read the way it behaves

12. **[Name things for what they do](name-things-for-what-they-do.md).** A name says what the code achieves, and the code does all it promises.
13. **[Make code do what a reader expects](least-surprise.md)** (least surprise). Behave the way the name and the usual conventions suggest.

## Share only what is truly shared

14. **[Write each fact once](dont-repeat-yourself.md)** (don't repeat yourself). A value that must match everywhere lives in one place from its second copy.
15. **[Share code only once it has appeared three times](recurrence-reveals-reality.md)** (recurrence reveals reality). Code that only looks alike stays apart.
16. **[Find the shared shape by removing the smallest difference first](flocking.md)** (flocking).

## Keep each change to one purpose

17. **[Give each commit, pull request and card one purpose](be-atomic.md)** (be atomic). Purpose, not size: a rename across 30 files is one purpose.
18. **[When a fix needs another fix, stop and find the cause](friction-is-information.md)** (friction is information).

## The test

Before committing to a design choice, ask:

1. **Does this close doors?** If yes, can we avoid closing them?
2. **Does this add complexity for a requirement that doesn't exist yet?** If yes, remove it.
3. **Would a developer seeing this for the first time understand why it's here?** If no, simplify.

*Design is more the art of preserving changeability than it is the act of achieving perfection.*

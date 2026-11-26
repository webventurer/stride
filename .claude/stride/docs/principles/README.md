# Principles

Stride's principles, most important first. Apply each one with judgement; none is a rule to follow to the letter. Every principle here is a case of being agile: choosing the path that makes future change easier. Open a principle's page when a decision turns on it, or when two principles pull against each other. The pages are in `.claude/stride/docs/principles/`.

## How to work

1. **[Start from the principle, not the rule](principles-over-rules.md)** (principles over rules). Apply each principle to the case in front of you and keep the reason visible. A rule tells you what to follow or break; understanding the principle helps you choose in situations nobody wrote a rule for.
2. **[Be agile](be-agile.md)** (agility). Find out where you are, take a small step, adjust, repeat; between equal options, take the path that makes future change easier. Without agility, a plan made with the least information is carried out as written, and its mistakes surface late and large.

## Build less

3. **[Don't build it until you need it](yagni.md)** (YAGNI). Build only what a present requirement needs. Code not written costs nothing to read, test or change.
4. **[Use what already exists before building something new](leverage-existing-mechanisms.md)** (leverage existing mechanisms). Check what the tools beneath you already do. Most of the time the capability is there, and the job is to find it and use it properly.
5. **[Do the simplest thing that works](simplest-thing-that-works.md).** The obvious solution over the clever one. Complexity has to earn its place by solving a real problem.
6. **[Favour speed of implementation over exhaustive testing](favour-speed-of-implementation-over-exhaustive-testing.md).** Prove each card with quick checks, and test the whole piece of work at the end, by eye and spot tests. Without this, a card can spend most of its time proving the same thing several ways.
7. **[Decide only when a requirement forces you to](postpone-decisions.md)** (postpone decisions). Keep the ability to decide later. Any design decision made ahead of a real requirement rests on a guess about what will be needed.

## Give each thing one home

8. **[Give each piece of code one reason to change](single-responsibility-principle.md)** (single responsibility). If describing it needs "and", split it. When you depend on a class that does too much, it may change for a reason unrelated to your use of it — and each time it changes, there's a possibility of breaking your code.
9. **[Earn the split](avoid-premature-organisation.md)** (avoid premature organisation). Work on a new thing as one blob until it is clear; split it only when you need to. Structure drawn before that clarity is a guess, and a wrong guess is harder to undo than a missing split.
10. **[Keep each concern in one place](separation-of-concerns.md)** (separation of concerns). When one concern changes, one place is edited. Three modules that each own a concern are simpler than thirty that share one.
11. **[Put one thing in each file](one-thing-per-file.md).** A thing earns its own file once it has its own reason to change. Its history and its diffs show changes to that thing alone.
12. **[Keep structure apart from styling](keep-structure-apart-from-styling.md).** A component holds structure; its look comes from stylesheets. When the two are mixed, every change of look means editing the component.

## Make code read the way it behaves

13. **[Name things for what they do](name-things-for-what-they-do.md).** A name says what the code achieves, and the code does all it promises. A name is a claim about what the code does, read at every place the code is used.
14. **[Make code do what a reader expects](least-surprise.md)** (least surprise). Behave the way the name and the usual conventions suggest. Following the convention by default, and keeping similar operations alike, means what a reader learns in one place holds everywhere.

## Share only what is truly shared

15. **[Write each fact once](dont-repeat-yourself.md)** (don't repeat yourself). A value that must match everywhere lives in one place from its second copy. Written in two places, it becomes a fact with copies, and copies drift: change one and the others quietly start lying.
16. **[Share code only once it has appeared three times](recurrence-reveals-reality.md)** (recurrence reveals reality). Code that only looks alike stays apart. Each new copy rules out some of the possible shapes until the right one becomes visible.
17. **[Find the shared shape by removing the smallest difference first](flocking.md)** (flocking). Make the two most alike pieces identical, one small change at a time. Small changes mean the error messages point at the one line that caused them.

## Keep each change to one purpose

18. **[Give each commit, pull request and card one purpose](be-atomic.md)** (be atomic). Purpose, not size: a rename across 30 files is one purpose. Shipping things together because it's easier now makes them harder to revert, review and understand later.
19. **[When a fix needs another fix, stop and find the cause](friction-is-information.md)** (friction is information). Look for the level the problem belongs at instead of adding another workaround. The workaround works today and creates three new problems tomorrow.

## The test

Before committing to a design choice, ask:

1. **Does this close doors?** If yes, can we avoid closing them?
2. **Does this add complexity for a requirement that doesn't exist yet?** If yes, remove it.
3. **Would a developer seeing this for the first time understand why it's here?** If no, simplify.

*Design is more the art of preserving changeability than it is the act of achieving perfection.*

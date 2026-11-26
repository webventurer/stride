# Earn the split (avoid premature organisation)

> Work on a new thing as one blob until you have clarity, and split it only when you need to: when the content itself starts telling you it needs its own space.

A new file, folder, module, layer, document section or card appears only when you can name the different reasons its parts change, not because they might one day. Structure drawn before that clarity is a guess, and a wrong guess is harder to undo than a missing split. It splits related ideas that belong together while they are still forming, leaves empty categories that never fill, and makes every new piece start with "where does this go?" instead of the work itself. The directory does not create the separation; it makes an earned boundary visible.

## The test

Before adding a file, folder, module, section or card, ask: **can I name the different reason each part changes, from content that exists today?** If you can, split along those reasons. If you are guessing about what will exist, keep it in one place and carry on building. Name a new group for what its content is, such as `css/`; a `misc/` or `new/` folder names no reason to change.

The content tells you it needs its own space when:

- **Items cluster.** Three or more related items sit together; one is no pattern yet and two could be coincidence.
- **References pile up.** The same pieces keep pointing at each other.
- **New pieces want to join.** Each new item naturally belongs with an existing group.
- **The current shape causes friction.** You keep searching for related items, or a file has become hard to find your way around.

## Worked example: a folder of CSS notes

A folder of best-practice notes is about to get its first note on CSS. The author expects many more, so they set up the structure now, choosing the categories a CSS course would use.

```text
# Before: three categories drawn up front, around one note
best-practice/
├── css/
│   ├── layout/
│   │   └── responsive-design.md
│   ├── colour/
│   └── typography/
└── other-best-practices.md

# After: the notes stay flat until six of them cluster, then move together
best-practice/
├── css/
│   ├── responsive-design.md
│   ├── grid-layouts.md
│   ├── flexbox-patterns.md
│   ├── colour-system.md
│   ├── typography-scale.md
│   └── component-styling.md
└── other-best-practices.md
```

The before has two empty folders, and every new note starts with a choice the categories can't answer: `flexbox-patterns.md` is layout, but `component-styling.md` touches layout, colour and type at once. The after kept every note in `best-practice/` while they were being written. When six CSS notes sat side by side and each new one wanted to join them, one request grouped them under `css/` and updated every link that pointed at them. The content showed one boundary, not three, so the earned split is one flat folder. This pack's own folder is flat for the same reason: its groups live in the list that indexes it, so a principle can change group without its file moving.

## Where it stops

<mark>Earning the split is not the same as never splitting.</mark> Once the signals above are clear, leaving the clutter in place costs more every day: related items are hard to find, and fixes to one get missed in the others. Splitting is then a response to evidence, and it is done properly, with every reference updated. Constant reshuffling over minor differences is the opposite failure: it breaks links and gives no one a stable place to look.

[Give each piece of code one reason to change](single-responsibility-principle.md) says what to split along; this says when. A reason to change that you can name from code that exists is a line to split on. One you can only imagine is a guess dressed as architecture, and it waits.

The blob is how you work while the shape is unclear, not how you hand the work over. By the time you commit, the purposes are known, and [give each commit, pull request and card one purpose](be-atomic.md) keeps each commit to one of them.

## Related

- [Give each piece of code one reason to change](single-responsibility-principle.md): what to split along, where this principle says when.
- [Give each commit, pull request and card one purpose](be-atomic.md): how the work is handed over once its purposes are known.
- [Keep each concern in one place](separation-of-concerns.md): which worry lives where, once the split is earned.
- [Put one thing in each file](one-thing-per-file.md): the file-level case of this principle.
- [Decide only when a requirement forces you to](postpone-decisions.md): the same patience applied to design decisions.
- [Share code only once it has appeared three times](recurrence-reveals-reality.md): the same count of three, applied to shared code.

## Source

Distilled from codefu's `docs/research/ai-coding/avoid-premature-organisation.md`, and from its `.claude/docs/principles/separation-of-concerns.md` for the line on earned boundaries. The worked example recasts the first source's CSS documentation example as a before and after.

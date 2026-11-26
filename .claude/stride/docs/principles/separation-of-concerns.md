# Keep each concern in one place (separation of concerns)

> One worry, one home: when one concern changes, one place is edited.

A concern is a reason the software might have to change, and each one should live in a single place you can point at. Edsger Dijkstra named the idea: study one aspect of a problem in isolation, for the sake of its own consistency, while knowing you are only holding one aspect at a time. The same holds for data and display: the facts a page shows and the way it shows them change for different reasons, so a new layout shouldn't touch how the figures are worked out, and a new figure shouldn't touch the layout. The failure this prevents is not too few files. It is one worry turning up in every file.

## The test

Ask: **when this worry changes, how many places do I edit?** One place means the concern is separated. Eight places means it is smeared, however many modules the codebase has. The count is the test, not the file layout or the directory names.

- **Sort by reason to change, not by layer.** Folders such as `controllers/`, `models/` and `services/` sort code by what kind of thing it is. David Parnas's point is to divide a system by what is likely to change, so that when a decision is revisited only one module notices.
- **Name what each piece is the only place for.** After a split, if you can't say what each piece is the only home of, the pieces are smaller but the system is not simpler.

## Worked example: an exchange that fails

A trading program has a small job: fetch signals, decide whether to trade, plan the trade, submit it to an exchange and supervise it. The exchange is unreliable. Orders get rejected, connections drop, and fills arrive late or twice. Each time a failure showed up somewhere, the code where it showed up gained a defence against it, which is the obvious local fix.

| | Where the exchange's unreliability is handled | What a reader must understand |
|:--|:----------------------------------------------|:------------------------------|
| **Before** | Retries, partial-failure branches and "what if the connection missed this" checks in signal handling, planning, connection events, replay, reconciliation, saving, logging and status reports: over 2,500 lines, with several paths updating the same trade | Every one of those paths, held in your head at once, to answer "what is this trade doing?" |
| **After** | One exchange module that retries, drops duplicate fills and hands back a settled answer; deciding, planning, reconciling and reporting each in their own place, joined by a thin loop | The exchange module for anything about the exchange, and one other module for anything else |

The volume was a symptom. The cause was that the exchange's unreliability had no home, so every part of the program grew its own defence. Once it had one, everything inward of the exchange module could assume it was talking to something reliable. That is where the strongest boundary belongs: around whatever is most likely to change or misbehave, which in an integration is almost always the far side you don't control. The joining loop is the part to watch; when it starts making decisions of its own, a concern has failed to land and has moved back into the middle.

## Where it stops

<mark>Splitting a system into many pieces is not the same as separating its concerns.</mark> Thirty small modules with retry logic in each are one concern smeared across thirty places, and a folder per technical layer or an interface for every class adds a boundary to understand while removing nothing. Three modules that each own a concern are simpler than thirty that share one. Move a reason to change, not a quantity of code: moving two hundred lines into a new file relocates the problem, and moving a concern removes it from everywhere else.

When to draw a new boundary is [earn the split](avoid-premature-organisation.md). You can also give every module [one reason to change](single-responsibility-principle.md) and still fail here, if the same worry is a reason to change in eight of them.

## Related

- [Give each piece of code one reason to change](single-responsibility-principle.md): the same idea checked one unit at a time.
- [Earn the split](avoid-premature-organisation.md): when a concern has shown itself clearly enough to get its own place.
- [Put one thing in each file](one-thing-per-file.md): the file-level case.
- [Keep structure apart from styling](keep-structure-apart-from-styling.md): one concern pair kept apart in front-end code.
- [When a fix needs another fix, stop and find the cause](friction-is-information.md): a defence repeated across the code is the signal that a concern has no home.

## Source

Distilled from codefu's `.claude/docs/principles/separation-of-concerns.md`, which holds the longer argument, the layer-versus-concern table and the guide to finding seams. The worked example recasts its "What bleeding through looks like" trading example as a before and after. The line on keeping data apart from display is written for this page.

Further reading: **Edsger Dijkstra**, *On the role of scientific thought* (1974): where the term comes from. **David Parnas**, *On the Criteria To Be Used in Decomposing Systems into Modules* (1972): divide a system by what is likely to change.

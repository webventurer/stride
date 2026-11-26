# Don't build it until you need it (YAGNI)

> Don't build something until a present requirement needs it.

YAGNI stands for "you aren't gonna need it". A feature, parameter, option or extension point that nothing uses today is a guess about the future. Guesses are usually wrong, and a wrong guess still has to be read, tested and worked around by everyone who comes after. Code not written costs nothing to read, test or change.

## The test

Before adding a piece, ask: **does this add complexity for a requirement that doesn't exist yet?** If it does, leave it out.

## Worked example: an unused extension point

A function sends the weekly report by email. Its author expects SMS one day, so they add a `channel` parameter, a `Channel` base class and a registry of channels. Email is the only channel, and no one has asked for another.

| | Call | What a reader must understand |
|:--|:-----|:------------------------------|
| **Before** | `send_report(report, channel=EmailChannel(), registry=CHANNELS)` | A channel parameter, a base class and a registry, for one channel |
| **After** | `send_email(report)` | One function that sends one email |

The removal deletes a base class, a registry and a parameter that every caller had to fill in. The one real requirement, sending email, reads the same as before. When SMS is asked for, the requirement says how the two channels differ, and the extension point that gets built then fits them. The guessed one would have fitted a guess.

## Where it stops

<mark>YAGNI rules out speculative code. It doesn't rule out code a recurring change has already asked for.</mark> When the same kind of change has arrived again and again, the requirement is real, and making room for it at that point is a response to evidence. See [Share code only once it has appeared three times](recurrence-reveals-reality.md) for how repetition becomes evidence.

Nor does YAGNI excuse making a change hard. It says what to leave unbuilt, and it says nothing against keeping the code simple and the names clear, which is what makes the later change cheap.

Leaving a piece unbuilt differs from leaving a shape undecided; [Decide only when a requirement forces you to](postpone-decisions.md) draws the line between them.

## Related

- [Do the simplest thing that works](simplest-thing-that-works.md): the positive instruction that goes with YAGNI. Where YAGNI says what to leave out, this says what to build.
- [Decide only when a requirement forces you to](postpone-decisions.md): the neighbouring principle about not committing to a shape early.
- [Share code only once it has appeared three times](recurrence-reveals-reality.md): what repeats is real, and what has appeared once is not yet a pattern.
- [Be agile](be-agile.md): code not written is the cheapest code to change.

## Source

Distilled from codefu's `.claude/docs/principles/yagni.md`.

Further reading: **Martin Fowler**, "Yagni" (2015): the costs of building a presumed feature early. **Kent Beck**, *Extreme Programming Explained* (1999): where the phrase comes from.

# When a fix needs another fix, stop and find the cause (friction is information)

> Something is fighting you. That's information about the approach, not a problem to push through.

When work gets hard in a particular way, with workarounds breeding workarounds, rules that are nothing but exceptions and tools fighting you instead of helping, the instinct is to push harder: find a better workaround, try a different rule, force the tool. Don't. Friction that comes from the shape of the problem resisting the shape of your solution, rather than from a typo or a missing import, is a sign that you are solving at the wrong level, asking the wrong question or missing an abstraction. Pushing through doesn't solve it; it buries it. The workaround works today and creates three new problems tomorrow.

## The test

When a fix needs another fix, stop and ask:

- **What exactly is resisting?** Name the friction rather than just feeling it.
- **Is this incidental or structural?** A typo is incidental: fix it and move on. A workaround breeding workarounds is structural: change the approach, not the effort.
- **What would make this problem disappear?** Not get easier, but disappear.

The signs that the friction is structural: workarounds that need more workarounds, every proposed rule having exceptions, solutions that create new kinds of problem, the feeling that this shouldn't be this hard, and two valid approaches with no way to choose between them.

Then make the move: notice the friction and name it, stop solving, ask what it's telling you, and change the level rather than the effort. The right level doesn't make the problem easier; it makes it the wrong problem to have. Often the way through is a dimension you aren't seeing: you are looking at a thing in isolation when it is a thing in context, such as a function name whose real problem is the module it sits in.

## Worked example: report times in the wrong time zone

An order report shows each order's time an hour out for customers in another country. The author adds an hour in the report's display code, and the report is right. The careful, plausible next step is to keep fixing each symptom where it appears.

| | What was done | What it cost |
|:--|:--------------|:-------------|
| **Before** | Fix one adds an hour in the report. When the clocks change, the times go wrong again, so fix two checks for daylight saving. The confirmation email shows the same orders an hour out, so fix three adds an hour there too, with its own daylight-saving check | Three fixes in two places, each correct on its own. The next screen to show an order time needs its own fix, and anyone changing one fix has to know about the other two |
| **After** | At fix two, the author stops and names what is resisting: every fix is about time zones, and each one lives in display code. The cause is upstream: order times are stored as local times with no zone. Times are stored with their zone, and each screen converts once, to the viewer's zone, when it displays them | The three fixes are deleted. The report, the email and the next screen each show the right time with one conversion and no knowledge of each other |

The second fix was the signal. A fix that needs another fix means the cause sits somewhere the fixes aren't, and here it sat in storage, a level below the code being patched. Changing the level made the display bugs the wrong problem to have.

## Where it stops

<mark>Not everything that's hard is friction.</mark> Difficulty is resistance that yields to effort: a complex algorithm or a new interface is hard, but more effort produces more progress, so keep going. Friction is resistance that grows with effort, where each fix creates more problems than it solves. Incidental friction, such as a missing import or a misconfigured tool, is a one-off with no cause behind it: fix it and move on. Stop and look for the cause only when the same kind of problem keeps coming back in new forms.

## Related

- [Start from the principle, not the rule](principles-over-rules.md): when every rule you try has exceptions, you are missing the principle that sits above them.
- [Name things for what they do](name-things-for-what-they-do.md): a name that feels forced often means the code sits in the wrong container, not that the name is wrong.
- [Be agile](be-agile.md): adjusting your understanding based on what you learned is what stopping at the second fix makes room for.

## Source

Distilled from codefu's `.claude/docs/principles/friction-is-information.md`, with the line between friction, difficulty and incidental bumps from codefu's `docs/distinctions/friction.md`. The worked example is written for this page.

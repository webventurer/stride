# Principle name, saying what it asks (familiar term)

<!-- Filename: kebab-case of the familiar term, such as yagni.md or postpone-decisions.md, so re-wording the title never renames the file. A principle with no familiar term takes the kebab-case of its title. -->

<!-- Copy this file to .claude/stride/docs/principles/ when adding a principle to the pack, add its line to that folder's README.md, and delete every comment like this one from the copy. Keep the section spine: opening → The test → Worked example → Where it stops → Related → Source. Don't invent new section names. -->

<!-- Draw every section from the source document named under Source. Carry its wording, its tests and its example across, trimmed to fit; don't write them fresh. The source has been refined over time and a fresh version loses that work. If the source has no before-and-after example, or there is no source, stop and raise it with the card's owner instead of inventing one, unless the card that adds the principle says to write it fresh. -->

<!-- When the file is written, run /nothing-lost against the source and carry back anything a reader would need to apply the principle. -->

<!-- Length: up to two full pages, about 1,000 words, counted with the comments removed. Use less when the idea needs less: codefu's yagni.md (435 words) and postpone-decisions.md (695 words) are complete well under the limit. A principle that won't fit goes to the card's owner rather than over the limit. -->

> One line that states the move: what to do, in words the reader already owns.

One paragraph that states the principle, what it asks you to do, and what goes wrong without it. A reader who stops here can apply the principle.

## The test

Before `<the moment the principle applies>`, ask: **the one question that tells you whether you are following it?** Say what to do with each answer.

<!-- When the source has several tests, such as single responsibility's "and" test and its "read the name aloud" test, keep each one as a bullet of one line rather than choosing between them. Add a closing paragraph only when the test has an exception, such as "decide now only when waiting would cost more". -->

## Worked example: what the example shows

<!-- Required. A before and an after, both shown in full. Use a table when the change is in what someone did or what exists; use a code pair when the change is in the code itself. Name the two columns for what differs in this example: "What exists" and "What a reader must understand" suit code, "What was done" and "What it cost" suit a way of working. The before must be a plausible choice a careful person would make, not a weak version set up to be knocked down. -->

The situation in two or three sentences: what someone is building or doing, and the choice in front of them.

| | What exists | What a reader must understand |
|:--|:------------|:------------------------------|
| **Before** | `the call, file or step as first done` | What it costs, and for what benefit |
| **After** | `the call, file or step with the principle applied` | What it costs now |

Or, when the change is in the code (use the source's language for the fence):

```text
# Before: what is wrong with it, in one comment
...

# After: what is better, in one comment
...
```

One paragraph on what the change bought: what was removed or made cheaper, what still works the same, and what happens when the next requirement arrives.

## Where it stops

<mark>One sentence on what the principle does not rule out, where a reader would naturally over-apply it.</mark> Then the case that marks the edge, and the neighbouring principle in the pack that takes over there.

<!-- Where two principles pull against each other, such as "write each fact once" and "share code only once it has appeared three times", the boundary is explained in the file of the principle more often over-applied, and the other file links to that section in one line. Explaining it twice gives two copies that drift. -->

<!-- Add a second paragraph only when the principle is commonly used as an excuse, such as "Nor does it excuse messy code". -->

## Related

- Neighbouring principle, as a link to its file in the pack: how the two differ or fit together, in one line.
- Skill: `/skill-name` applies this principle. <!-- Only for a skill stride ships. A codefu skill that applies the principle is named in plain text under Source, because stride doesn't install it. -->

<!-- Link only to files in the pack. Anything outside it is a dead link in an installed project. -->

## Source

Distilled from codefu's `path/to/source-essay.md`, which holds the longer argument and further examples. <!-- Plain text, not a link: codefu is not installed alongside stride. Name every source when there is more than one. A principle written fresh says "No longer source exists; written fresh for the pack." -->

Further reading: **Author**, *Title* (year): what it adds, in one line.

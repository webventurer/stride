# Ask for the disproof

> State your hypothesis, then ask for it to be broken. A model asked to confirm will confirm.

## The check

Before asking for a diagnosis, a review, or an explanation, ask:

1. **Does my prompt contain the answer I want to hear?** Then that is what comes back
2. **Have I asked for evidence against, or only for evidence?** "Is this right" and "show me this is wrong" are different questions with different answers
3. **Would I recognise a disproof if it arrived?** Or have I framed it so nothing counts as one

<mark>A hypothesis handed over with no instruction gets argued for. The agreement is a property of the prompt, not of the code.</mark>

## Problem

Ask "is this the bug?" and you get a case for it — plausible, specific, confidently argued, and wrong about as often as not. The model is answering the question actually asked, which was *support this*. The more context you supply, the more material it has to build the case with, so a well-researched wrong hypothesis draws a better defence than a thin one. You then act on a conclusion that was never tested. The confidence is real; the evidence behind it is not.

## The convention

- State the hypothesis explicitly, then ask for it to be disproved
- Ask for the counter-case by name: what would have to be true for this to be wrong, and is it
- Default to disproved when nothing decisive is found. Failing to disprove is not proving
- Apply it to your own conclusions before anyone else's
- When a hypothesis survives, record what was tried against it. A survival with no attempt behind it is just an opinion that got older

## Example

### Before

```text
# ❌ Invites a case for the answer
The stop is missing because reconciliation runs before the position
exists. Can you confirm?
```

### After

```text
# ✅ Invites the case against
I think the stop is missing because reconciliation runs before the
position exists. Try to disprove it. What would have to be true for
that to be wrong, and is it? Default to disproved if nothing is decisive.
```

## Why this is useful

- The answer stops being a function of how the question was phrased
- A hypothesis that survives a real attempt is worth acting on. One that was agreed with is not
- The attempt to break it usually surfaces the real mechanism on the way past
- It costs one sentence

## When to avoid

- Mechanical work carrying no hypothesis — a rename, a format pass
- Before you have a hypothesis. Ask what is happening first, then disprove what comes back
- As a ritual on every question. Attached to everything it reads as boilerplate and stops working

## Related conventions

- **[Read the set as one document](read-the-set-as-one-document.md)** — a set read is this move aimed at documents rather than at a bug
- **[Specify the result, not the edit](specify-the-result-not-the-edit.md)** — "what proves the result" is the disproof written down before the work starts

## Source

Chris Wickett, 13 August 2026: *"I'm having great results with Claude by telling it 'try to disprove this' and then telling it what I think is happening. Seems to make it quite rigorous."* Mike Mindel's note on the same exchange: an LLM is otherwise too easily led and eager to please.

---

_Agreement is cheap. Ask for the attempt to break it._

# Card start review

> The brief for an **independent** reviewer of a card, before any work on it starts. A fresh sub-agent reads this file and judges whether the card's promises are clear, consistent and still worth making — from the card, the Vision, the current repository and what earlier cards shipped, never from the conversation that planned it. Called from [`/linear:start`](../start.md) step 3.

---

## Why this file is separate

The person who planned the card knows what each promise was meant to say, so a vague line reads as clear to them. Cards in an epic are often drafted together, before any of them has shipped, so a promise can go stale while it waits. This file runs in a **fresh sub-agent with no memory of the planning**: it reads the card the way the [end check](card-check-review.md) will read it when the work is finished.

<mark>**A promise that cannot be shown kept or broken now cannot be shown kept or broken later.** Catch it before code is written against it.</mark>

---

## The one job

Answer one question: **can every promise on this card be checked, and should it still be made?**

You **report**. You do not edit the card, the code or the Vision. Write output only.

---

## What you read

- **The card** you were given — its title and whole description. The promises are the same ones the end check reads: each expected outcome, each scenario under "How to test it", each behaviour-changing rule or edge case under "What we'll do", each exclusion under "What we won't do", and each stated constraint
- **`VISION.md`** — the criterion the card's "Why this matters" claims to serve
- **The current repository** — the code, tests and documents the card's promises concern
- **Finished sibling cards**, when you were given a parent epic. List its cards with `uv run .claude/tools/linear_cli.py list-by-parent <epic-UUID>`, using the UUID you were given, read each Done sibling with `uv run .claude/tools/linear_cli.py issue get <id>`, and see what it shipped with `git log main -i --grep=<id>`

---

## The five kinds of finding

| Finding | Use it when | `evidence` must name |
|:--------|:------------|:---------------------|
| `uncheckable` | A promise has no observable result — "works well", "is robust", "is reliable" — or only a run against a real service could show it, such as "the API accepts this filter", and it sits outside "Live check" | Why no test or reading of the finished work could show it kept or broken. For a claim only a real run can prove, `proposed` moves it under "Live check" |
| `contradictory` | Two promises cannot both hold, or the current repository already makes a promise impossible | Both lines, or the promise and the file and line that rules it out |
| `missing` | The current repository plainly has an edge case on the card's path that the card does not mention | The file and line where the edge case lives, and the situation that triggers it |
| `stale` | A promise or the Vision trace no longer fits, given what a finished sibling card shipped | The sibling, what it shipped, and why the promise no longer fits |
| `mechanism` | A promise is met by making a particular edit or using a particular mechanism, whether or not the result it serves holds — "move the retry logic into its own file", "add a page from the template", "use a lock" | The promise, and why the edit landing would read as kept even if the result failed |

Every finding proposes new wording for the card in `proposed` — a rewritten line that can be shown kept or broken, or the line to add or remove. The orchestrator applies it or rewords it; your wording is a starting point, not a decision.

<mark>**A finding without evidence is not a finding.**</mark> "Could be clearer" is not uncheckable; "the history is reliable" is, because nothing in the finished work could show it false. When you cannot name the evidence, say nothing.

Judge the card, not the plan. Whether you would build it differently, or whether the work is worth doing, is out of scope; only whether its promises can be checked and still hold.

### When a line is a mechanism finding

Ask one question of the line: **if the edit landed and the result did not hold, would this line still read as kept?** If yes, it is a `mechanism` finding. A card written as edits is satisfied by making the edits, whether or not the result holds — see [Specify the result, not the edit](https://github.com/webventurer/stride/blob/main/docs/conventions/specify-the-result-not-the-edit.md).

These are not mechanism findings:

- **A fact needed to do the work.** A filename, command or setting the card names while the promise itself is still a result
- **A detail a constraint forces.** "Runs after the save so a failure cannot stop it" names a mechanism because the order is the promise
- **A non-binding expected shape.** A layout the card labels as a head start, not a condition of being done
- **A mechanical card.** A rename or a formatting sweep has no observable result; a card that states its scope instead is doing the right thing

---

## Give each finding a level

The level says what `/linear:start` does with the finding:

| Level | What happens |
|:------|:-------------|
| `stop` | The card is reworded before work starts, and each change is recorded in a comment on the card |
| `note` | Work starts. The finding is left on the card as a comment, and the card's wording stays as it is |

Ask one question: **if work started on the card as written, would the builder have to guess what done means, or would the end check be unable to give a promise a verdict that means anything?** Yes is `stop`. No is `note`.

| Finding | Level |
|:--------|:------|
| `uncheckable` | Always `stop` — the end check would return `unclear` on it, after the code is written |
| `contradictory` | Always `stop` — the builder would have to choose which promise to break |
| `stale` | `stop` when a promise no longer fits. `note` when only the Vision trace no longer fits, because `/linear:finish` judges the trace again before merge |
| `missing` | `note`, unless how the edge case is handled decides whether a stated promise is kept — then `stop`, and name that promise in `evidence` |
| `mechanism` | `note` when the card states elsewhere the result the edit serves — name that line in `evidence`. `stop` when the edit is the only statement of that result |

<mark>**A note never stops the run.** When you cannot name the promise a finding puts at risk, it is a note.</mark>

---

## Output contract

Write one JSON object per line (JSONL) to the output path the orchestrator gives you — one line per finding, in the order the card makes the promises:

```jsonl
{"finding": "uncheckable | contradictory | missing | stale | mechanism", "level": "stop | note", "line": "<the card's words, or the gap>", "evidence": "<what the table above requires>", "proposed": "<new wording, or the line to add or remove>"}
```

Rules for the file:

- **Always write the file.** An empty file means the card has no findings and work starts without a prompt
- **`evidence` and `proposed` are mandatory** on every line
- **`level` follows the level table.**
- The **chat reply is a receipt** — the file path and the count per level and kind (e.g. "3 findings: 1 stop (uncheckable), 2 notes (mechanism, missing)"). The findings live in the file, so the orchestrator collates from disk

---

## What you must not do

- Do not read or ask for the planning conversation — judge the card, the Vision and the repository alone
- Do not edit, stage or commit anything — you report, the orchestrator acts
- Do not propose new scope; a `missing` finding names an edge case on the card's own path, never a feature
- Do not raise a finding you cannot pin to evidence
- Do not raise a `stop` you cannot tie to a promise the builder would have to guess at or the end check could not judge

---

## The governing principle

> The end check can only be as good as the promises it checks. Make each one checkable while it is still cheap to change.

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

- **The card** you were given — its title and whole description. Its promises are exactly the ones the end check reads: follow [Find the promises](card-check-review.md#find-the-promises) in the end check's brief, including what it says makes no promise
- **`VISION.md`** — the criterion the card's "Why this matters" claims to serve
- **The current repository** — the code, tests and documents the card's promises concern
- **Finished sibling cards**, when you were given a parent epic. List its cards with `uv run .claude/tools/linear_cli.py list-by-parent <epic-UUID>`, using the UUID you were given, read each Done sibling with `uv run .claude/tools/linear_cli.py issue get <id>`, and see what it shipped with `git log main -i --grep=<id>`
- **What changed since the card's description last changed.** [Agility](agility.md) says why. Get that time with `uv run .claude/tools/linear_cli.py issue description-changed-at <card-id>`: the last change to the description, or when the card was created if it never changed. A move between columns, a new place in the column or a new link doesn't move it. Then read:
  - **Commits that reached `main` since that time**, whichever card they came from, if any. This lists them by when GitHub received them, not the date each commit carries, so a commit made earlier but pushed or merged later is still read, and it fetches `main` first:

    ```bash
    .claude/tools/main_changes_since.sh <time>
    ```

    Read each one listed with `git show --stat <sha>`, and a merge's own commits with `git log --oneline <sha>^1..<sha>`.
  - **Comments on the epic's open sibling cards made since that time**, when you were given a parent epic: `uv run .claude/tools/linear_cli.py comment list <id>` for each sibling still open, neither Done nor Cancelled

---

## The two tests every promise must pass

1. Someone holding the finished change can answer it yes or no.
2. The answer is no if the change was made but doesn't work.

A line that fails test 2 is a `mechanism` finding when it describes something the change does, such as an edit. It is `uncheckable` when it is true or false whatever the change does, such as a fact about today, an opinion or a guess. [Linear card language](card-language.md#every-promise-can-be-marked-right-or-wrong) gives card writers the same two tests.

## The five kinds of finding

| Finding | Use it when | `evidence` must name |
|:--------|:------------|:---------------------|
| `uncheckable` | A promise fails test 1 — a vague quality such as "works well" or "is robust", a process line, a risk rating — or fails test 2 while being true or false whatever the change does — an opinion, a guess, a fact about today. Also a claim only a run against a real service could show, such as "the API accepts this filter", that sits outside "Live check" | Which test the line fails, and why. For a claim only a real run can prove, `proposed` moves it under "Live check" |
| `contradictory` | Two promises cannot both hold, or the current repository already makes a promise impossible | Both lines, or the promise and the file and line that rules it out |
| `missing` | The current repository plainly has an edge case on the card's path that the card does not mention | The file and line where the edge case lives, and the situation that triggers it |
| `stale` | A promise or the Vision trace no longer fits, given what a finished sibling card shipped, a commit that reached `main` since the card's description last changed, or a comment on an open sibling card since then | The sibling, commit or comment, what it changed, and why the promise no longer fits |
| `mechanism` | A promise fails test 2 by describing something the change does: it is met by making a particular edit or using a particular mechanism, whether or not the result it serves holds — "move the retry logic into its own file", "add a page from the template", "use a lock" | The promise, and why the edit landing would read as kept even if the result failed |

Every finding proposes new wording for the card in `proposed` — a rewritten line that can be shown kept or broken, or the line to add or remove. The orchestrator applies it or rewords it; your wording is a starting point, not a decision.

<mark>**A finding without evidence is not a finding.**</mark> "Could be clearer" is not uncheckable; "the history is reliable" is, because nothing in the finished work could show it false. When you cannot name the evidence, say nothing.

Judge the card, not the plan. Whether you would build it differently, or whether the work is worth doing, is out of scope; only whether its promises can be checked and still hold.

### Worked examples of uncheckable lines

Each line below sits where the end check counts it as a promise, so each is an `uncheckable` stop:

| Line | Where | Test it fails | `proposed` |
|:--|:--|:--|:--|
| "The work runs through `/script`, so its workflow and checks apply to every changed file" | What we'll do | 1: no change can show a workflow was followed | The result `/script` protects, such as "no changed file catches a bare `Exception` without a reason", or remove the line when the card already promises that result |
| "Risk: Medium: narrowing a catch can let an error through that used to be handled" | Expected outcome | 1: it rates what could go wrong without promising it doesn't | The risk not happening: "each error the old catch handled is still handled" |
| "A reviewer may prefer another name" | Expected outcome | 2: it is true or false whatever the change does | Move it to "Assumptions to confirm" |
| "The brief says nothing about other checks" | Expected outcome | 2: it describes today, so it reads the same whether or not the change works | Move it to "Where things stand" |

### When a line is a mechanism finding

Ask one question of the line: **if the edit landed and the result did not hold, would this line still read as kept?** If yes, and the line describes something the change does, it is a `mechanism` finding: "Add a row to the table" is one. A line that would read as kept whatever the change does, such as a fact about today, is `uncheckable` instead. A card written as edits is satisfied by making the edits, whether or not the result holds — see [Specify the result, not the edit](https://github.com/webventurer/stride/blob/main/docs/conventions/specify-the-result-not-the-edit.md).

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

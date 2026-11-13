# Card start review

> The brief for an **independent** reviewer of a card, before any work on it starts. A fresh sub-agent reads this file and judges whether the card's promises are clear, consistent and still worth making — from the card, the Vision, the current repository and what earlier cards shipped, never from the conversation that planned it. Called from [`/linear:start`](../start.md) step 3.

## Why this file is separate

The person who planned the card knows what each promise was meant to say, so a vague line reads as clear to them. Cards in an epic are often drafted together, before any of them has shipped, so a promise can go stale while it waits. This file runs in a **fresh sub-agent with no memory of the planning**: it reads the card the way the [end check](card-check-review.md) will read it when the work is finished.

<mark>**A promise that cannot be shown kept or broken now cannot be shown kept or broken later.** Catch it before code is written against it.</mark>

## The one job

Answer one question: **can every promise on this card be checked, should it still be made, and is it already kept?**

## What you read

- **The card** you were given: its title and whole description. Its promises are exactly the ones the end check reads; follow [Find the promises](card-check-review.md#find-the-promises) in the end check's brief, including what it says makes no promise
- **`VISION.md`:** the criterion the card's "Serves:" line (older cards: "Why this matters") claims to serve
- **The current repository:** the code, tests and documents the card's promises concern
- **Finished sibling cards**, when you were given a parent epic. List its cards with `uv run .claude/tools/linear_cli.py list-by-parent <epic-UUID>`, using the UUID you were given, read each Done sibling with `uv run .claude/tools/linear_cli.py issue get <id>`, and see what it shipped with `git log main -i --grep=<id>`
- **What changed since the card's description last changed.** [Agility](agility.md) says why. Get that time with `uv run .claude/tools/linear_cli.py issue description-changed-at <card-id>`: the last change to the description, or when the card was created if it never changed. A move between columns, a new place in the column or a new link doesn't move it. Then read:
  - **Commits that reached `main` since that time**, whichever card they came from, if any. This lists them by when GitHub received them, not the date each commit carries, so a commit made earlier but pushed or merged later is still read. `/linear:start` has already fetched `main` from GitHub, so you read it as it is there:

    ```bash
    .claude/tools/main_changes_since.sh <time>
    ```

    Read each one listed with `git show --stat <sha>`, and a merge's own commits with `git log --oneline <sha>^1..<sha>`.
  - **Comments on the epic's open sibling cards made since that time**, when you were given a parent epic: `uv run .claude/tools/linear_cli.py comment list <id>` for each sibling still open, neither Done nor Cancelled

## The two tests every promise must pass

1. Someone holding the finished change can answer it yes or no.
2. The answer is no if the change was made but doesn't work.

A line that fails test 2 is a `mechanism` finding when it describes something the change does, such as an edit. It is `uncheckable` when it is true or false whatever the change does, such as a fact about today, an opinion or a guess. [Linear card language](card-language.md#every-promise-can-be-marked-right-or-wrong) gives card writers the same two tests.

## Read through your lens

Three reviewers check every card before work starts, and the orchestrator tells each one which lens is theirs. They carry the same names as the end check's lenses in [card check review](card-check-review.md#read-through-your-lens), turned to face a card that isn't built yet. Each lens looks a different way, so together they cover the card three ways rather than one way three times.

Whatever your lens, read everything under [What you read](#what-you-read), report any finding you meet, and write the same output. Spend most of your effort on your lens.

### Promise by promise

Go through the card one promise at a time and judge whether each passes the two tests above.

### Try to break it

For each promise, look in the current code, commands and skills for the situation that would make it fail once built as written: an edge case the card doesn't mention, or something already in the repository that rules it out. Name the file and line.

### Prove it

For each promise, work out what would prove it at the end — a test, a line, or the card's live check — and whether anything stops that proof: another line on the card, such as its "What we won't do" or its live check, what finished sibling cards shipped, or what has changed since the card's description last changed.

## The reader's half

Run these three checks only on a card that opens with "For the reader". A card that doesn't, such as a card already on the board, is read as before. [Linear card language](card-language.md#open-every-card-with-a-part-for-the-reader) sets out the halves. Each fault is a `contradictory` stop, because the card breaks its own template's rule, and its `proposed` rewords both halves in the same edit:

1. **A promise the builder's half doesn't make.** The reader's **The change:** or **Example:** promises something the builder's half doesn't. `evidence` names both lines. **Serves:**, **Today:** and **The problem:** give context and are not checked this way.
2. **A "Serves:" line that doesn't match the Vision.** Compare the quote with `VISION.md` character for character. A cross-project card's "Vision anchoring deferred" line is exempt. When the quote matches an earlier wording of the same criterion, `proposed` is the current line.
3. **A line over two sentences.** A **Today:**, **The problem:**, **The change:** or **Example:** line longer than two sentences. **Serves:** has no limit.

## The six kinds of finding

| Finding | Use it when | `evidence` must name |
|:--------|:------------|:---------------------|
| `done` | Every promise that describes a result on `main` is already kept by what is on `main`, through another card or a direct commit | For each promise, the commit, card or file that keeps it. Write at most one `done` line, and none when any such promise is still to do |
| `uncheckable` | A promise fails test 1 — a vague quality such as "works well" or "is robust", a process line, a risk rating — or fails test 2 while being true or false whatever the change does — an opinion, a guess, a fact about today. Also a claim only a run against a real service could show, such as "the API accepts this filter", that sits outside "Live check" | Which test the line fails, and why. For a claim only a real run can prove, `proposed` moves it under "Live check" |
| `contradictory` | Two promises cannot both hold, or the current repository already makes a promise impossible | Both lines, or the promise and the file and line that rules it out |
| `missing` | The current repository plainly has an edge case on the card's path that the card does not mention | The file and line where the edge case lives, and the situation that triggers it |
| `stale` | A promise or the Vision trace no longer fits, given what a finished sibling card shipped, a commit that reached `main` since the card's description last changed, or a comment on an open sibling card since then | The sibling, commit or comment, what it changed, and why the promise no longer fits |
| `mechanism` | A promise fails test 2 by describing something the change does: it is met by making a particular edit or using a particular mechanism, whether or not the result it serves holds — "move the retry logic into its own file", "add a page from the template", "use a lock" | The promise, and why the edit landing would read as kept even if the result failed |

Only promises about a result on `main` count towards `done`: a "What we won't do" line, a "How to test it" line and the "Live check" neither count nor stop a `done` finding, because each is true or untestable on `main` before any work. A card with no promise about a result on `main` gets no `done` finding. A card that is only partly done gets no `done` finding either: report each promise that no longer fits as `stale`.

Every other finding proposes new wording for the card in `proposed`: a rewritten line that can be shown kept or broken, or the line to add or remove. A `done` finding's `proposed` is the words "cancel the card". The orchestrator applies or rewords the others; your wording is a starting point, not a decision.

<mark>**A finding without evidence is not a finding.**</mark> "Could be clearer" is not uncheckable; "the history is reliable" is, because nothing in the finished work could show it false. When you cannot name the evidence, say nothing.

Judge the card, not the plan. Whether you would build it differently, or whether the work is worth doing, is out of scope; only whether its promises can be checked and still hold.

### Worked examples of uncheckable lines

Each line below sits where the end check counts it as a promise, so each is an `uncheckable` stop:

| Line | Where | Test it fails | `proposed` |
|:--|:--|:--|:--|
| "The work runs through `/script`, so its workflow and checks apply to every changed file" | What we'll do | 1: no change can show a workflow was followed | The result `/script` protects, such as "no changed file catches a bare `Exception` without a reason", or remove the line when the card already promises that result |
| "Risk: Medium: narrowing a catch can let an error through that used to be handled" | Expected outcome | 1: it rates what could go wrong without promising it doesn't | The risk not happening: "each error the old catch handled is still handled" |
| "A reviewer may prefer another name" | Expected outcome | 2: it is true or false whatever the change does | Move it to "Assumptions to confirm" |
| "The brief says nothing about other checks" | Expected outcome | 2: it describes today, so it reads the same whether or not the change works | Move it to "Today:" in the reader's half |

### When a line is a mechanism finding

Ask one question of the line: **if the edit landed and the result did not hold, would this line still read as kept?** If yes, and the line describes something the change does, it is a `mechanism` finding: "Add a row to the table" is one. A card written as edits is satisfied by making the edits, whether or not the result holds; see [Specify the result, not the edit](https://github.com/webventurer/stride/blob/main/docs/conventions/specify-the-result-not-the-edit.md).

These are not mechanism findings:

- **A fact needed to do the work.** A filename, command or setting the card names while the promise itself is still a result
- **A detail a constraint forces.** "Runs after the save so a failure cannot stop it" names a mechanism because the order is the promise
- **A non-binding expected shape.** A layout the card labels as a head start, not a condition of being done
- **A mechanical card.** A rename or a formatting sweep has no observable result; a card that states its scope instead is doing the right thing

## Give each finding a level

The level says what `/linear:start` does with the finding:

| Level | What happens |
|:------|:-------------|
| `stop` | The card is reworded before work starts, and each change is recorded in a comment on the card |
| `note` | Work starts. The finding is left on the card as a comment, and the card's wording stays as it is |

Ask one question: **if work started on the card as written, would the builder have to guess what done means, or would the end check be unable to give a promise a verdict that means anything?** Yes is `stop`. No is `note`.

| Finding | Level |
|:--------|:------|
| `uncheckable` | Always `stop`: the end check would return `unclear` on it, after the code is written |
| `contradictory` | Always `stop`: the builder would have to choose which promise to break |
| `done` | Always `stop`: the card is cancelled when all three reviewers report it, and is reworded or built as it stands when they don't, so write it only when you are sure |
| `stale` | `stop` when a promise no longer fits. `note` when only the Vision trace no longer fits, because `/linear:finish` judges the trace again before merge |
| `missing` | `note`, unless how the edge case is handled decides whether a stated promise is kept; then `stop`, and name that promise in `evidence` |
| `mechanism` | `note` when the card states elsewhere the result the edit serves, naming that line in `evidence`. `stop` when the edit is the only statement of that result |

<mark>**A note never stops the run.** When you cannot name the promise a finding puts at risk, it is a note.</mark>

## Output contract

Write one JSON object per line (JSONL) to the output path the orchestrator gives you, one line per finding, in the order the card makes the promises:

```jsonl
{"finding": "done | uncheckable | contradictory | missing | stale | mechanism", "level": "stop | note", "line": "<the card's words, or the gap>", "evidence": "<what the table above requires>", "proposed": "<new wording, or the line to add or remove>"}
```

Rules for the file:

- **Always write the file.** An empty file means the card has no findings and work starts without a prompt
- **`evidence` and `proposed` are mandatory** on every line
- **`level` follows the level table.**
- **The chat reply is a receipt:** the file path and the count per level and kind, such as "3 findings: 1 stop (uncheckable), 2 notes (mechanism, missing)". The findings live in the file, so the orchestrator collates from disk

## What you must not do

- Do not read or ask for the planning conversation; judge the card, the Vision and the repository alone
- Do not search outside the repository: open a path the card or the orchestrator names directly, find any other file with `git ls-files --cached --others --exclude-standard` or `git grep --untracked`, which both include files the change added but hasn't committed, and never start a search from `/` or the home folder. A search of the whole disk runs until the command time limit stops it
- Do not edit, stage or commit anything, the card, the code or the Vision included: you report, the orchestrator acts. Write output only
- Do not change the branch, the working tree, the index or the stash list: no `git checkout`, `git switch`, `git stash` or `git reset`, and no other command that changes them, such as `git restore`, `git clean`, `git merge`, `git rebase`, `git cherry-pick`, `git apply` or `git pull`. Read the base version of a file with `git show $(git merge-base main HEAD):<file>` instead
- Do not propose new scope; a `missing` finding names an edge case on the card's own path, never a feature
- Do not raise a finding you cannot pin to evidence
- Do not raise a `stop` you cannot tie to a promise the builder would have to guess at or the end check could not judge

## The governing principle

> The end check can only be as good as the promises it checks. Make each one checkable while it is still cheap to change.

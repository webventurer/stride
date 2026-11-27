# Card start review

> The brief for an **independent** reviewer of a card, before any work on it starts. A fresh sub-agent reads this file and judges whether the card's promises are clear, consistent and still worth making — from the card, the Vision, the current repository and what earlier cards shipped, never from the conversation that planned it. Called from [`/linear:plan-work`](../plan-work.md) step 12 on a draft before it is filed, and from [`/linear:start`](../start.md) step 3.

## Why this file is separate

The person who planned the card knows what each promise was meant to say, so a vague line reads as clear to them. Cards in an epic are often drafted together, before any of them has shipped, so a promise can go stale while it waits. This file runs in a **fresh sub-agent with no memory of the planning**: it reads the card the way the [end check](card-check-review.md) will read it when the work is finished.

<mark>**A promise that cannot be shown kept or broken now cannot be shown kept or broken later.** Catch it before code is written against it.</mark>

## The one job

Answer one question: **can every promise on this card be checked, should it still be made, and is it already kept?**

## What you read

- **The card** you were given: its title and whole description. **Today:** (older cards: "Where things stand") is where it says what it assumes about the code; check that assumption against the repository. Its promises are exactly the ones the end check reads; follow [Find the promises](card-check-review.md#find-the-promises) in the end check's brief, including what it says makes no promise
- **`VISION.md`:** the criterion the card's "Serves:" line (older cards: "Why this matters") claims to serve
- **The current repository:** the code, tests and documents the card's promises concern
- **The card's lesson comments:** every comment on the card headed **Lesson from** another card, whatever its time, in a full check as in a check of changes: `uv run .claude/tools/linear_cli.py comment list <card-id>`. A lesson that overtakes a promise is a `stale` finding, as a commit that overtakes one is
- **Finished sibling cards**, when you were given a parent epic. List its cards with `uv run .claude/tools/linear_cli.py list-by-parent <epic-UUID>`, using the UUID you were given, read each Done sibling with `uv run .claude/tools/linear_cli.py issue get <id>`, and see what it shipped with `git log main -i --grep=<id>`
- **What changed since the card's description last changed.** [Agility](agility.md) says why. Use the time you were given when the card was just rewritten into the new shape, because the rewrite reset the description's change time. Otherwise get that time with `uv run .claude/tools/linear_cli.py issue description-changed-at <card-id>`: the last change to the description, or when the card was created if it never changed. A move between columns, a new place in the column or a new link doesn't move it. Then read:
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

## Inside the repo

A card's job, its sub-agents included, works inside the repo it is built in, and is refused when it reaches outside.

**Inside the repo** means what a fresh worktree of the card's branch holds. That is the narrowest place a card can be built, so every card is judged against it, whether or not it is later started with `--worktree`. It holds:

- **What the card's branch tracks,** and files the repo's own tests make when they run, in the system's temporary folder too
- **What stride links in from the main checkout:** stride's install, `.stride.json`, `.claude/settings.local.json`, the project's `.venv` or `venv` and the `worktree-links` paths, as `.claude/commands/linear/reference/worktree.md` sets out. A Python environment kept outside the worktree, such as Poetry's, Pipenv's or Conda's, is not linked in, and is outside

**Allowed outside the repo,** because it is stride's plumbing rather than the card's work: the shared slot store; stride's scratch files, under `/tmp/<identifier>` for a card and `/tmp/plan-work.XXXXXX/` for a draft; the files an orchestrator hands a reviewer, and the reviewer's own output path; Linear; GitHub; and the tools the repo's own commands run, such as `uv`, `node` and `pnpm`, with the packages they install, such as `uv run --with`.

**Outside the repo and not allowed:** the person's other projects, the files and environments of installed programs, such as anything under `~/.local`, and the person's own files. A file in the main checkout that a fresh worktree doesn't have is outside too: one git ignores and stride doesn't link into the worktree, and one that is untracked or not yet committed.

Judge each check against what that worktree will hold, wherever you run from.

## Read through your lens

Three reviewers check every card before work starts, and the orchestrator tells each one which lens is theirs. They carry the same names as the end check's lenses in [card check review](card-check-review.md#read-through-your-lens), turned to face a card that isn't built yet. Each lens looks a different way, so together they cover the card three ways rather than one way three times.

Whatever your lens, read everything under [What you read](#what-you-read), report any finding you meet, and write the same output. Spend most of your effort on your lens.

### Promise by promise

Go through the card one promise at a time and judge whether each passes the two tests above.

### Try to break it

For each promise, look in the current code, commands and skills for the situation that would make it fail once built as written: an edge case the card doesn't mention, or something already in the repository that rules it out. Name the file and line.

### Prove it

For each promise, work out what would prove it at the end — a test, a line, or the card's live check — and whether anything stops that proof: another line on the card, such as its "What we won't do" or its live check, what finished sibling cards shipped, or what has changed since the card's description last changed.

Raise an `uncheckable` stop for each of these, judged against what is [inside the repo](#inside-the-repo):

- **A promise whose only proof needs a file from outside the repo.** `proposed` proves it with test files in the repo and moves the run on real files under "Live check" as the person's to run after the merge
- **A live check the job would run, or any other run the card asks of the job, that needs outside files,** though it makes no promise. `proposed` marks it as the person's to run after the merge

A "Live check" line already marked as the person's to run after the merge is what the rule asks for, so it is no finding.

## A draft not yet filed

When the orchestrator says the card is a draft not yet filed, read it as above, with these differences:

- **It has no card number,** so skip [What changed](#what-you-read) and the lesson comments, and run no Linear command for the card itself
- **Read the repository as it is on `main`,** which the orchestrator has just fetched: `git show origin/main:<path>` and `git grep <pattern> origin/main`, `VISION.md` included. When the orchestrator says the Vision has just changed, read `VISION.md` from the working tree instead
- **Write every `missing` finding's `proposed` as the line that puts the edge case on the card,** because each one is written into the draft, whatever its level
- **A draft for another project** is judged against that project's `origin/main` when the orchestrator gives its path (`git -C <path>`), with no check of its "Serves:" line or its Vision trace. What is [inside the repo](#inside-the-repo) then means inside that project's repo. When its code is not on this machine, judge only the wording: the two tests, and lines that contradict each other

## A check of changes only

When the orchestrator says to check only what changed since a time, the card as it reads now already passed a check then. Read the card, then what changed:

- **Commits that reached `main` since that time:** `.claude/tools/main_changes_since.sh <time>`
- **Comments posted since that time** on the card itself and on every sibling card: `uv run .claude/tools/linear_cli.py comment list <id>`. The siblings are the other cards under the card's parent, whatever its title: `issue get <card-id>` shows `parent.id`, and `list-by-parent <parent-id>` lists them. A comment that starts `**Card checked**` is a check's own record, not a change

A comment on this card or on any sibling card that overtakes a promise is a `stale` finding, as a commit that overtakes one is.

Then read whatever those changes touch. Raise only a finding one of those changes causes; one that would have held at the earlier check stays unraised. Name the commit or comment in `evidence`.

## The reader's half

Run these three checks only on a card that opens with "For the reader". A card that doesn't, such as a card already on the board, is read as before. [Linear card language](card-language.md#open-every-card-with-a-part-for-the-reader) sets out the halves. Each fault is a `contradictory` stop, because the card breaks its own template's rule, and its `proposed` rewords both halves in the same edit:

1. **A promise the builder's half doesn't make.** The reader's **The change:** or **Example:** promises something the builder's half doesn't. `evidence` names both lines. **Serves:**, **Today:** and **The problem:** give context and are not checked this way.
2. **A "Serves:" line that doesn't match the Vision.** Compare the quote with `VISION.md` character for character. A cross-project card's "Vision anchoring deferred" line is exempt. When the quote matches an earlier wording of the same criterion, `proposed` is the current line.
3. **A line over two sentences.** A **Today:**, **The problem:**, **The change:** or **Example:** line longer than two sentences. **Serves:** has no limit.

## The seven kinds of finding

| Finding | Use it when | `evidence` must name |
|:--------|:------------|:---------------------|
| `done` | Every promise that describes a result on `main` is already kept by what is on `main`, through another card or a direct commit | For each promise, the commit, card or file that keeps it. Write at most one `done` line, and none when any such promise is still to do |
| `uncheckable` | A promise fails test 1 — a vague quality such as "works well" or "is robust", a process line, a risk rating — or fails test 2 while being true or false whatever the change does — an opinion, a guess, a fact about today. Also a claim only a run against a real service could show, such as "the API accepts this filter", that sits outside "Live check". Also the two outside-the-repo cases under [Prove it](#prove-it) | Which test the line fails, and why. For a claim only a real run can prove, `proposed` moves it under "Live check". For a file from outside the repo, the file and the line that needs it |
| `contradictory` | Two promises cannot both hold, or the current repository already makes a promise impossible | Both lines, or the promise and the file and line that rules it out |
| `missing` | The current repository plainly has an edge case on the card's path that the card does not mention | The file and line where the edge case lives, and the situation that triggers it |
| `stale` | A promise or the Vision trace no longer fits, given what a finished sibling card shipped, a commit that reached `main` since the card's description last changed, or a comment on an open sibling card since then | The sibling, commit or comment, what it changed, and why the promise no longer fits |
| `mechanism` | A promise fails test 2 by describing something the change does: it is met by making a particular edit or using a particular mechanism, whether or not the result it serves holds — "move the retry logic into its own file", "add a page from the template", "use a lock" | The promise, and why the edit landing would read as kept even if the result failed |
| `long` | A story or bug description plainly runs past the 6,000-character aim its [story](templates/story.md) or [bug](templates/bug.md) template sets. Write at most one `long` line | What makes the card long, such as the lines that repeat each other |

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

Two cases are `stop` whatever the answer, because the job would be refused when it reached [outside the repo](#inside-the-repo): a promise whose only proof needs a file from outside it, and a run the card asks of the job that needs one, such as a live check, even though it makes no promise.

| Finding | Level |
|:--------|:------|
| `uncheckable` | Always `stop`: the end check would return `unclear` on it, after the code is written, or the job would be refused the outside file |
| `contradictory` | Always `stop`: the builder would have to choose which promise to break |
| `done` | Always `stop`: the card is cancelled when all three reviewers report it, and is reworded or built as it stands when they don't, so write it only when you are sure |
| `stale` | `stop` when a promise no longer fits. `note` when only the Vision trace no longer fits, because `/linear:finish` judges the trace again before merge |
| `missing` | `note`, unless how the edge case is handled decides whether a stated promise is kept; then `stop`, and name that promise in `evidence` |
| `mechanism` | `note` when the card states elsewhere the result the edit serves, naming that line in `evidence`. `stop` when the edit is the only statement of that result |
| `long` | Always `note`: length is an aim, and every decision and exclusion on the card comes before it |

<mark>**A note never stops the run.** When you cannot name the promise a finding puts at risk, it is a note, apart from those two cases.</mark>

## Output contract

Write one JSON object per line (JSONL) to the output path the orchestrator gives you, one line per finding, in the order the card makes the promises:

```jsonl
{"finding": "done | uncheckable | contradictory | missing | stale | mechanism | long", "level": "stop | note", "line": "<the card's words, or the gap>", "evidence": "<what the table above requires>", "proposed": "<new wording, or the line to add or remove>"}
```

Rules for the file:

- **Always write the file.** An empty file means the card has no findings and work starts without a prompt
- **`evidence` and `proposed` are mandatory** on every line
- **`level` follows the level table.**
- **The chat reply is a receipt:** the file path and the count per level and kind, such as "3 findings: 1 stop (uncheckable), 2 notes (mechanism, missing)". The findings live in the file, so the orchestrator collates from disk

## What you must not do

- Do not read or ask for the planning conversation; judge the card, the Vision and the repository alone
- Do not open a path outside the repository, even when the card names it. You may open: a path inside the repository, including what stride links into the worktree and every uncommitted and untracked file in the checkout you are told to review; the files the orchestrator hands you, such as the card and its comments under `/tmp/<identifier>`, or a draft under `/tmp/plan-work.XXXXXX/`; and your own output path. Don't open, copy or run anything else outside; judge an outside path from the card's own words. The one exception is a draft for another project, read with `git -C <path>` as [A draft not yet filed](#a-draft-not-yet-filed) sets out
- Do not search outside the repository: find a file you weren't given with `git ls-files --cached --others --exclude-standard` or `git grep --untracked`, which both include files the change added but hasn't committed, and never start a search from `/` or the home folder. A search of the whole disk runs until the command time limit stops it
- Do not edit, stage or commit anything, the card, the code or the Vision included: you report, the orchestrator acts. Write output only
- Do not change the branch, the working tree, the index or the stash list: no `git checkout`, `git switch`, `git stash` or `git reset`, and no other command that changes them, such as `git restore`, `git clean`, `git merge`, `git rebase`, `git cherry-pick`, `git apply` or `git pull`. Read the base version of a file with `git show $(git merge-base main HEAD):<file>` instead
- Do not propose new scope; a `missing` finding names an edge case on the card's own path, never a feature
- Do not raise a finding you cannot pin to evidence
- Do not raise a `stop` you cannot tie to a promise the builder would have to guess at or the end check could not judge, apart from a run the card asks of the job that needs a file from outside the repo

## The governing principle

> The end check can only be as good as the promises it checks. Make each one checkable while it is still cheap to change.

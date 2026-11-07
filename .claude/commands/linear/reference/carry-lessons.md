# Carry lessons

> **What this is**: how [`/linear:finish`](../finish.md) step 11 carries what a merged card's checks found to the cards still in Todo, before the next card starts. It is the "learn, apply, then take the next step" part of the agile loop that [agility](agility.md) describes.

<mark>**Every finished card teaches the cards still to come.**</mark> A card's checks find things the next cards need to know: a promise shape that keeps coming back unproven, a rule that clashed with the card, a test only a run can show. Once stride runs Todo by itself, nothing carries that lesson unless this step does.

## 1. Read what the merged card's checks found

Read the merged pull request's `## Card check` record, and the start check's comment on the card:

```bash
gh pr view <number> --json body -q .body
uv run .claude/tools/linear_cli.py comment list <issue-id>
```

The start check's comment is the one listing its stops and notes, posted before the card's branch existed. A card whose start check found nothing has no such comment; read it from its record alone. A pull request with no `## Card check` record, such as one merged through `/linear:quick`, has nothing to read: report "no lesson for Todo" and stop here.

## 2. Name each lesson

State each start-check stop or note, and each row of the record whose verdict is Fixed or Not acted on, as one rule about how a promise is worded or tested. For example, a finding that a promise naming two worktree locations was tested for one becomes "a promise naming two situations needs a test for each".

## 3. Apply it to the cards in Todo

List the cards in Todo, in the order stride will work them, then read each one:

```bash
uv run .claude/tools/linear_cli.py order-todo --project "<project>" --dry-run
uv run .claude/tools/linear_cli.py issue get <id>
```

For each card a lesson changes, reword only the lines it changes, save the card, and post one comment following [Linear card language](card-language.md):

```bash
uv run .claude/tools/linear_cli.py issue update <id> --description @<file>
uv run .claude/tools/linear_cli.py comment create <id> --body @<file>
```

The comment names the lesson, the merged card it came from, and each line it changed:

> Lesson from WB-622: a promise naming two situations needs a test for each. Old line: "works for a new repo and an existing one". New line: "works for a new repo" and "works for an existing repo".

**When a lesson would change what a card is for or how far it goes**, don't edit the card. Post the question as a comment on it, headed **Lesson question from <merged card>**, and leave the card as it is. In interactive mode, ask the user there and then. In unattended mode, finish the remaining steps of `/linear:finish` and report the question. The card waits for its answer. A card started by name stops there, before the next card starts. A run through Todo leaves only that card out of its later batches and carries on with the others, even when that card is the only one running. [`/linear:start`](../start.md) step 1 stops on a card started by name while a lesson question on it has no later comment starting `Answer:`. In interactive mode, post the user's reply as a comment starting `Answer:`.

This step only rewords card descriptions and posts comments. It never adds or removes a card, or moves one between columns.

## 4. Report what happened

End with one line for the summary: the cards reworded and the lesson each carried, the questions posted, or "no lesson for Todo" when the merged card's checks changed no Todo card and raised no question.

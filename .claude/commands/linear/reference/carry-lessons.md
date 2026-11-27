# Carry lessons

> **What this is**: how [`/linear:finish`](../finish.md) step 12 carries what a merged card taught to every card still to come, before the next card starts. It is the "learn, apply, then take the next step" part of the agile loop that [agility](agility.md) describes.

<mark>**Every finished card teaches the cards still to come.**</mark> A card learns things the next cards need to know: a promise shape that keeps coming back unproven, a rule that clashed with the card, a library default that behaved differently, a shared piece one card owns, an order two cards must merge in. Once stride runs Todo by itself, nothing carries that lesson unless this step does.

## 1. Read what the merged card taught

Read the merged pull request's `## Card check` and `## Lessons for later cards` sections, and the card's check records:

```bash
gh pr view <number> --json body -q .body
uv run .claude/tools/linear_cli.py comment list <issue-id>
```

A check record is a comment starting `**Card checked**`, posted when the card was filed and when its start check completed, listing that check's stops and notes. A record with nothing below its first line found nothing, and a card with no check record is read from the pull request alone. A pull request with neither section, such as one merged through `/linear:quick`, has nothing to read: report "no lesson for cards to come" and stop here.

Take the lessons from these records, never from memory of the build.

## 2. Name each lesson

State each start-check stop or note, and each row of the `## Card check` record whose verdict is Fixed or Not acted on, as one rule about how a promise is worded or tested. For example, a finding that a promise naming two worktree locations was tested for one becomes "a promise naming two situations needs a test for each". Each line of `## Lessons for later cards` is a lesson as it stands.

Then judge each lesson with [moves the needle](moves-the-needle.md). The judgement decides only whether a card in Todo is reworded or a card is asked a question. A lesson that has come back, which a comment on a card in Todo or the `## Card check` record of another recently merged pull request shows (read them when a lesson looks familiar), or that would cost a lot even once, can reword a card or raise a question. A lesson that only repeats a **Lesson from** comment on the merged card is that same sighting, so neither that comment nor its copies on other cards show it came back. A one-off that cost little is commented on each card it applies to, no card in Todo is reworded for it, and it is named in step 5's report.

## 3. Find the cards still to come

Ask stride which cards can hear a lesson, then read each one:

```bash
uv run .claude/tools/linear_cli.py cards-to-come <issue-id> --project "<project>" --batch <card> --batch <card>
uv run .claude/tools/linear_cli.py issue get <id>
```

Give one `--batch` for each card of the merged card's batch, as the coordinator's go names them, and none when the card ran outside a batch. The command lists the batch's cards in Doing or In Review, the cards in Todo, and the cards in Backlog or Backburner under the merged card's epic. No other card hears a lesson, and a listed card that no lesson applies to gets nothing.

## 4. Tell each card

A card in Todo is reworded first, when a lesson that passed moves the needle changes one of its lines. Reword only the lines it changes, in both halves of the card where a line appears in each, and save the card:

```bash
uv run .claude/tools/linear_cli.py issue update <id> --description @<file>
```

Then post one comment on each card a lesson applies to, headed **Lesson from <merged card>**, following [Linear card language](card-language.md). It names each lesson and why it applies to that card, and a reworded card's comment also lists each changed line:

```bash
uv run .claude/tools/linear_cli.py comment create <id> --body @<file>
```

A card in Doing, In Review, Backlog or Backburner gets the comment only, so a running build isn't changed under it. Its session reads the comment before its work merges, and its [start check](card-start-review.md) reads it when it starts.

> **Lesson from WB-622**
>
> A promise naming two situations needs a test for each. This card's promise names two. Old line: "works for a new repo and an existing one". New line: "works for a new repo" and "works for an existing repo".

**When a lesson would change what a card is for or how far it goes**, don't edit the card. Post the question as a comment on it, headed **Lesson question from <merged card>**, and leave the card as it is. The question carries the four labelled parts in order, as [asking the user](asking-the-user.md) sets out, under that heading. In interactive mode, ask the user there and then. In unattended mode, finish the remaining steps of `/linear:finish` and report the question. The card waits for its answer. A card started by name stops there, before the next card starts. A run through Todo leaves only that card out of its later batches and carries on with the others, even when that card is the only one running. A card being built in a batch doesn't merge: [`/parallel-sessions`](../../../skills/parallel-sessions/SKILL.md#5-watch-and-check) holds its go. [`/linear:start`](../start.md) step 1 stops on a card started by name while a lesson question on it has no later comment starting `Answer:`. In interactive mode, post the user's reply as a comment starting `Answer:`.

This step only rewords card descriptions and posts comments. It never adds or removes a card, or moves one between columns.

## 5. Report what happened

End with one line for the summary: each card that got a lesson comment or a lesson question, grouped by column, with the Todo cards reworded and the one-off lessons named and left. Report "no lesson for cards to come" only when no card step 3 listed needed a comment or a question, still naming any one-off lessons.

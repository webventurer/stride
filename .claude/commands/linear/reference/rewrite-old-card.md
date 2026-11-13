# Rewrite an old card

> **What this is**: how [`/linear:start`](../start.md) step 3 rewrites a card that was filed before the new shape into the new shape, before the card start check reads it.
>
> **Why it exists**: an old card is hardest to read at exactly the moment it is about to be built, and rewriting every old card at once would spend effort on cards that may never be worked. The rewrite happens only for a card `/linear:start` is starting.

## 1. Ask stride whether the card needs it

```bash
uv run .claude/tools/linear_cli.py issue rewrite-template <issue-id>
```

It prints `"story"`, `"bug"` or `"none"`. `none` means the card already opens with "For the reader", is an epic, is in Done or Canceled, or has no description: leave the card exactly as it is and go on to the card start check. Epics are never rewritten here; their sub-issues are rewritten when they are started. `story` or `bug` names the template to write the new card into.

A rewrite counts as a change that leaves behaviour as it is and keeps every ask, so it needs no sign-off, in interactive and unattended mode alike. If writing the new card would need to change what the card is for, stop and ask the user, in the four labelled parts [asking the user](asking-the-user.md) sets out. In unattended mode, post that question as a comment on the card and end the run.

## 2. Keep what the card start check needs from the old card

Read when the old description last changed, and save the old description. Saving the rewrite resets that time, so the three reviewers are given this one: they judge what has changed since the old card was written, not since the rewrite.

```bash
mkdir -p /tmp/<identifier> && uv run .claude/tools/linear_cli.py issue description-changed-at <issue-id> | jq -r . > /tmp/<identifier>/since.txt
uv run .claude/tools/linear_cli.py issue get <issue-id> | jq -r .description > /tmp/<identifier>/old-card.md
```

## 3. Write the new description

Write it into the [story](templates/story.md) or [bug](templates/bug.md) template, following [Linear card language](card-language.md).

- **Keep every promise.** Each expected outcome, constraint, edge case and test of the old card survives in the builder's half. Reword one only to fit the template's wording, never to change what it requires.
- **Today:** takes the facts about the current behaviour that the builder can't find in the code. A description of the code as it stands is dropped.
- **The problem:** takes the old card's case for filing, in one or two sentences. The rest of the backstory is dropped.
- **The change:** and **Example:** are written from the old card's own plan and expected outcome. They add no promise.
- **Serves:** quotes the Vision criterion the old card names, word for word. A card that names no Vision outcome gets no **Serves:** line, even when the project has a `VISION.md`, and the comment says so. For a card whose Vision link was put off when it was filed from another project, quote the criterion in this project's `VISION.md` that the card plainly serves. When no criterion fits without stretching, or the project has no `VISION.md`, leave out **Serves:** and say so in the comment.

Save it:

```bash
uv run .claude/tools/linear_cli.py issue update <issue-id> --description @<new-card-file>
```

## 4. Post one comment

Following [Linear card language](card-language.md), the comment says the card was rewritten into the new shape and lists:

- each expected outcome, constraint, edge case and test of the old card beside the line it became
- what was dropped
- the reason for any missing **Serves:** line
- `Old description last changed: <the time saved in step 2>` on a line of its own, so a later run of the card start check, after an interrupted run, still judges from that time
- the old description in full, inside a collapsed section, so nothing is lost

Open the collapsed section with `+++ Old description` on its own line and close it with `+++` on its own line.

```bash
uv run .claude/tools/linear_cli.py comment create <issue-id> --body @<comment-file>
```

Then carry on with the card start check, giving each reviewer the time saved in step 2. A run that finds the card already rewritten reads the time from that comment line.

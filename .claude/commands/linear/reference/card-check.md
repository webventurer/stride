# Card check

> Checks a finished change against its card, promise by promise, before it merges. Run by [`/linear:start`](../start.md) step 11 before the pull request opens, and by [`/linear:finish`](../finish.md) step 8 before the merge. Both modes follow it; [unattended mode](unattended.md) changes nothing here.

The card is the agreement about what the work will do. The simplification, atomicity and Vision reviews each ask a different question, so a change can pass them all and still miss a promise. This check asks the one they don't: **does the change do what the card said?**

<mark>**Never edit the card to make a verdict pass.** A card changes only on purpose, with the user's sign-off, recorded on the card.</mark>

---

## 1. Run the reviewers

Commit all work on the branch with `/commit` first, so the reviewers read exactly what will merge.

Spawn three fresh sub-agents at once with the Task tool (`general-purpose`, model `sonnet`, effort `high`), each with its own output path and its own lens from the brief's [Read through your lens](card-check-review.md#read-through-your-lens): the first "Promise by promise", the second "Try to break it", the third "Prove it". Give each **only** the card's title and file, its lens and its output path — never your reasoning, the plan checklist or this conversation.

Save the card to the file first, exactly as the card holds it now: the card may have been reworded since an earlier check, and `/linear:finish` runs this check in a session that never saved one. The file sits outside the worktree, so it never dirties the tree the reviewers read, and its path holds the card's identifier, so cards running side by side never share one:

```bash
mkdir -p /tmp/<identifier> && uv run .claude/tools/linear_cli.py issue get <issue-id> | jq -r .description > /tmp/<identifier>/card.md
```

Then give each reviewer:

> Read `.claude/commands/linear/reference/card-check-review.md` and follow it. Your lens is <Promise by promise | Try to break it | Prove it>. Review this branch's change since it left `main`. The card is: `<identifier> — <title>`. Read its exact description from `/tmp/<identifier>/card.md`. Write your verdicts as JSONL to `<output-path>`.

Sonnet at high effort is the setting [chain-of-command config](../../../skills/parallel-sessions/reference/chain-of-command-config.md#sonnet-at-high-effort-is-the-soldiers-sweet-spot) found as good as every higher setting while using fewer tokens than any of them. It was measured on implementation jobs, not on reviews.

Do not paste the diff. The reviewers run `git diff` themselves; their blindness to why the change looks the way it does is the point.

Read the verdicts from the three JSONL files, not the sub-agents' chat replies. Each promise takes the worst verdict any reviewer gave it, in this order: `unclear`, `broken`, `kept-unproven`, `kept`. A finding is any verdict other than `kept`.

## 2. Act on the verdicts

The check runs once. Check each finding against the branch, fix the ones that hold, and do not run the reviewers again.

| Verdict | What happens |
|:--------|:-------------|
| **Kept** | Nothing |
| **Kept, unproven** | When the proof the evidence names is missing, add it — a test, or the line that states the behaviour. When the branch already has it, record the finding as Not acted on, naming that proof |
| **Broken** | When the scenario in the evidence fails, fix the change so it works. When it doesn't fail, record the finding as Not acted on, with what you tried |
| **Unclear** | Stop and ask the user (see [When the card is the problem](#when-the-card-is-the-problem)) |
| **Empty file** | The card makes no checkable promise. Stop and ask the user (see [When the card is the problem](#when-the-card-is-the-problem)); never pass it silently |

An unclear verdict or an empty file from any reviewer stops for the user, whatever the other two found.

After the fixes, re-run the command's validation (build and tests) and commit them with `/commit`. In `/linear:finish`, also push them, so the pull request holds what will merge. The pull request records each fix next to its verdict, so the user's review is where a second look at a fix happens.

The check passes when every promise is kept, fixed, or recorded as Not acted on with its reason.

## When the card is the problem

An unclear verdict, an empty file, a promise the user would rather drop, or a broken verdict the user decides the code should not fix — each one means the card itself may be wrong. Stop in both modes and ask the user as "How to ask" below sets out, unless the fix leaves behaviour as it is today and keeps every ask.

### When the fix leaves behaviour as it is today

A rewording that leaves behaviour as it is today and keeps every ask doesn't stop, in both modes. Today means `main` before this card: the new wording describes what `main` already does, so it can't hide a promise the branch broke, and every change the card asks for is still promised. Reword both halves in the same edit, so "The change:" never describes the old behaviour. Apply it with `uv run .claude/tools/linear_cli.py issue update <issue-id> --description @<file>`, then note it on the card with `uv run .claude/tools/linear_cli.py comment create <issue-id> --body @<file>`: which promise changed, from what to what, and that it leaves behaviour as it is on `main` and keeps every ask. Write the comment following [Linear card language](card-language.md). Then run the check from step 1 against the new wording.

A fix that changes what the card is for, its purpose or scope, still stops for the user.

### How to ask

Ask in the four labelled parts in order and nothing more, as [asking the user](asking-the-user.md) sets out.

Around the shape:

- **One finding per question.** The question holds only the finding that needs the user's decision. A finding the check fixes itself stays out of it.
- **The card's words, not the reviewers' labels.** Quote the card's own words where the question needs them.
- **Several promises stop the check together:** ask about them one at a time, each in the four parts, and ask the next only after the first is answered, and before the check runs again.
- **The card makes no promise the check can judge:** Context says so, The gap lists what the card does say, and My answer quotes one promise to add.
- **The user answers no:** ask for their own wording in one line, with no four parts for that line, and use it. Don't offer a second fix.
- **The user wants the code fixed, not the card:** they can say so at any time. The question doesn't list it as a second option.

### What the answer does

- **Yes** — apply only the wording the user gives or approves, rewording both halves in the same edit so "The change:" never describes the old behaviour, with `uv run .claude/tools/linear_cli.py issue update <issue-id> --description @<file>`. Then record the change on the card with `uv run .claude/tools/linear_cli.py comment create <issue-id> --body @<file>`: which promise changed, from what to what, why, and that the user signed off. Write the comment following [Linear card language](card-language.md). Then run the check from step 1 against the new wording
- **Fix the code instead** — continue from step 2 with the user's direction

<mark>**A card change stops for the user, in unattended mode too, unless it leaves behaviour as it is today and keeps every ask.**</mark> Unattended mode fixes code without asking; it never decides what the card should promise.

## 3. Record the result in the pull request

The pull request body carries the latest verdicts, one row per promise, so a reader sees promise by promise what the change keeps, and `/linear:finish` can tell whether they still describe the branch:

```markdown
## Card check

Checked tree: `<the tree once the check's fixes are committed>`
Checked card: `<card fingerprint>`
Check cost: start <s> s (slowest of three), <n> stops, <n> notes · end <s> s (slowest of three), <n> findings: <n> fixed, <n> not acted on

| Promise | Verdict | Evidence |
|:--------|:--------|:---------|
| <the card's words> | Kept | <test or line> |
| <the card's words> | Fixed | <what the reviewer found, and the fix> |
| <the card's words> | Not acted on | <what the reviewer found, and why it does not hold> |
```

The tree hash names the exact content that was checked and fixed. Squashing or rewording commits keeps it; any change to the content gives a new one. Note the tree straight after committing the check's fixes, never when the record is written: a change made in between must not inherit a pass it never had.

The check cost line records what both checks took and what they found, so after a run of real cards the numbers show whether each check is worth its time. Take each time from the reviewer's completion notice; for the end check, the slowest of the three. A finding is counted once, even when several reviewers raised it. `/linear:finish` replaces the end part when it runs the check again.

The card fingerprint names the exact wording the change was checked against, so a promise added or reworded after the check is checked too. Compute it from the card's title and description:

```bash
uv run .claude/tools/linear_cli.py issue get <issue-id> | jq -r '.title + "\n\n" + .description' | git hash-object --stdin
```

Moving the card between board columns keeps it; any change to the title or description gives a new one.

- **`/linear:start`** writes this section into the body when it creates the pull request (step 17)
- **`/linear:finish`** replaces the section after a re-check: save the body with `gh pr view <number> --json body -q .body`, replace the `## Card check` section, and write it back with `gh pr edit <number> --body-file <file>`

## Before merge: is the record current?

`/linear:finish` merges only a branch whose current content has a passing check against the card's current wording. Read the pull request body and compare its `Checked tree:` value with `git rev-parse HEAD^{tree}`, and its `Checked card:` value with the card fingerprint computed now:

- **Same tree, same card, every verdict Kept, Fixed or Not acted on** — the check is current. Continue to the merge
- **Different tree, different card, no `## Card check` section, or any other verdict** — the content or the card changed since the check, or the change never passed it. Run the check once from step 1, then record the new result

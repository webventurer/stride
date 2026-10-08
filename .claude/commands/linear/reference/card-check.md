# Card check

> Checks a finished change against its card, promise by promise, before it merges. Run by [`/linear:start`](../start.md) step 11 before the pull request opens, and by [`/linear:finish`](../finish.md) step 7 before the merge. Both modes follow it; [unattended mode](unattended.md) changes nothing here.

The card is the agreement about what the work will do. The simplification, atomicity and Vision reviews each ask a different question, so a change can pass them all and still miss a promise. This check asks the one they don't: **does the change do what the card said?**

<mark>**Never edit the card to make a verdict pass.** A card changes only on purpose, with the user's sign-off, recorded on the card.</mark>

---

## 1. Run the reviewer

Commit all work on the branch with `/commit` first, so the reviewer reads exactly what will merge.

Spawn a fresh sub-agent with the Task tool (`general-purpose`, model `opus`). Give it **only** the card and an output path — never your reasoning, the plan checklist or this conversation:

> Read `.claude/commands/linear/reference/card-check-review.md` and follow it. Review this branch's change since it left `main`. The card is: `<identifier> — <title>`, described as: `<issue description>`. Write your verdicts as JSONL to `<output-path>`.

Do not paste the diff. The reviewer runs `git diff` itself; its blindness to why the change looks the way it does is the point.

Read the verdicts from the JSONL file, not the sub-agent's chat reply.

## 2. Act on the verdicts

The check runs once. Fix what it finds; do not run the reviewer again.

| Verdict | What happens |
|:--------|:-------------|
| **Kept** | Nothing |
| **Kept, unproven** | Add the proof the evidence names — a test, or the line that states the behaviour |
| **Broken** | Fix the change so the scenario in the evidence works |
| **Unclear** | Stop and ask the user (see [When the card is the problem](#when-the-card-is-the-problem)) |
| **Empty file** | The card makes no checkable promise. Stop and tell the user; never pass it silently |

After the fixes, re-run the command's validation (build and tests) and commit them with `/commit`. In `/linear:finish`, also push them, so the pull request holds what will merge. The pull request records each fix next to its verdict, so the user's review is where a second look at a fix happens.

The check passes when every verdict is kept, or was kept-unproven or broken and has been fixed.

## When the card is the problem

An unclear verdict, a promise the user would rather drop, or a broken verdict the user decides the code should not fix — each one means the card itself may be wrong. Stop in both modes and show the promise, its verdict and the evidence. The user decides:

- **Fix the code** — continue from step 2 with the user's direction
- **Change the card** — apply only wording the user gives or approves, with `uv run .claude/tools/linear_cli.py issue update <issue-id> --description @<file>`. Then record the change on the card with `uv run .claude/tools/linear_cli.py comment create <issue-id> --body @<file>`: which promise changed, from what to what, why, and that the user signed off. Write the comment following [Linear card language](card-language.md). Then run the check from step 1 against the new wording

<mark>**A card change always stops for the user, in unattended mode too.**</mark> Unattended mode fixes code without asking; it never decides what the card should promise.

## 3. Record the result in the pull request

The pull request body carries the latest verdicts, so a reader sees promise by promise what the change keeps, and `/linear:finish` can tell whether they still describe the branch:

```markdown
## Card check

Checked tree: `<the tree once the check's fixes are committed>`
Checked card: `<card fingerprint>`

| Promise | Verdict | Evidence |
|:--------|:--------|:---------|
| <the card's words> | Kept | <test or line> |
| <the card's words> | Fixed (was broken) | <what the reviewer found, and the fix> |
```

The tree hash names the exact content that was checked and fixed. Squashing or rewording commits keeps it; any change to the content gives a new one. Note the tree straight after committing the check's fixes, never when the record is written: a change made in between must not inherit a pass it never had.

The card fingerprint names the exact wording the change was checked against, so a promise added or reworded after the check is checked too. Compute it from the card's title and description:

```bash
uv run .claude/tools/linear_cli.py issue get <issue-id> | jq -r '.title + "\n\n" + .description' | git hash-object --stdin
```

Moving the card between board columns keeps it; any change to the title or description gives a new one.

- **`/linear:start`** writes this section into the body when it creates the pull request (step 17)
- **`/linear:finish`** replaces the section after a re-check: save the body with `gh pr view <number> --json body -q .body`, replace the `## Card check` section, and write it back with `gh pr edit <number> --body-file <file>`

## Before merge: is the record current?

`/linear:finish` merges only a branch whose current content has a passing check against the card's current wording. Read the pull request body and compare its `Checked tree:` value with `git rev-parse HEAD^{tree}`, and its `Checked card:` value with the card fingerprint computed now:

- **Same tree, same card, every verdict Kept or Fixed** — the check is current. Continue to the merge
- **Different tree, different card, no `## Card check` section, or any other verdict** — the content or the card changed since the check, or the change never passed it. Run the check once from step 1, then record the new result

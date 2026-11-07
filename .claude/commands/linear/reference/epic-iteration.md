# Epic iteration

> The path `/linear:start` follows when its argument is an epic rather than a story. The decision — single story by default, iterate when the argument is an epic — stays in `start.md` (step 1); this file holds the execution mechanics so the command stays scannable. Step numbers below refer to `/linear:start`'s steps.

> When the argument is an epic and the branch is `main`, `/linear:start` runs the epic's sub-issues in Todo as a batch ([below](#batch-on-main)); unattended mode runs on batch after batch until none of them can start. On any other branch it works them one at a time. Interactive mode pauses at every PR; [unattended mode](unattended.md) finishes a passing story and continues. An epic has no code of its own — its work lives in its stories.

---

## Batch on `main`

On `main`, ask stride what to do with the epic's cards, the way [`/linear:start`](../start.md) does with no card named, but only the epic's sub-issues in Todo:

```bash
uv run .claude/tools/linear_cli.py start-choice --project "<project>" --branch main --epic "<epic-identifier>"
```

Follow its answer:

- **`batch`** — run the cards through `/parallel-sessions`, settling its settings as `/linear:start` does for a batch on `main`. Interactive mode shows the batch and waits for the user's "go", then stops after the one batch, so the user runs `/linear:start <epic>` again for the next. Unattended mode gives the skill its "go" itself and runs on, as [below](#unattended-mode-runs-on-until-the-epics-cards-are-done) sets out
- **`single`** — interactive mode works that card as `/linear:start <card>` does, and the run ends when its pull request is merged. Unattended mode runs it as a batch of one, so a failure ends that card's job and not the run, and the run goes on
- **`blocked`** — show each sub-issue's reason and stop, starting nothing. Ending an unattended run, it opens the final report below
- **`empty`** — say no sub-issue of the epic is in Todo and stop. Ending an unattended run, it opens the final report below

`linear_cli.py next-batch --project "<project>" --epic "<epic-identifier>"` shows every sub-issue it looked at and why each one is out.

On `main`, E1 to E4 are not entered in either mode. On any other branch, work the sub-issues one at a time, as E1 to E4 say.

### Unattended mode runs on until the epic's cards are done

The run is the [Todo run](todo-run.md), with each round asking stride about the epic's cards only. The run keeps its list of started cards as the Todo run does, and each round asks:

```bash
uv run .claude/tools/linear_cli.py start-choice --project "<project>" --branch main --epic "<epic-identifier>" --started <card> --started <card>
```

After each batch's report, the run asks again. It ends on `blocked` or `empty`: no card of the epic left in Todo can start. A card outside the epic is never started, and a blocker outside the epic is never started either, so a card it blocks waits. Failed cards, held questions and lessons are handled as the Todo run sets them out.

The run's last message lists the epic's cards that were in Todo when it began:

- **Done:** each card that merged.
- **Failed:** each card that failed, with the check that failed or the decision it needs.
- **Waiting:** each card still in Todo that isn't listed as failed, with the reason `start-choice` gave.

The Todo run's lessons and questions follow, questions last.

## E1. Enumerate and disclose upfront

List the sub-issues before doing anything:

```bash
uv run .claude/tools/linear_cli.py list-by-parent <epic-UUID>
```

Order by `sortOrder` ascending (board order). When `sortOrder` is unset, fall back to identifier order. Then surface the plan — scope visible upfront, with an escape hatch:

```
Epic <ID>: <title>
N sub-issues, worked one at a time — interactive mode reviews and /finishes each PR; unattended mode continues after each passing finish:
  1. <SUB-1> — <title> [state]
  2. <SUB-2> — <title> [state]
  ...
Starting with the first unfinished one: <SUB-X>. Say stop to bail out.
```

**Set Manual ordering — once, here.** The disclosed order reflects `sortOrder`, but Linear only shows that order on the board when the project's view is on **Manual** ordering. Set it on the epic's project, so the board matches the disclosure:

```bash
uv run .claude/tools/linear_cli.py set-project-view-manual <project-UUID>
```

The call is idempotent. If it fails (older API, missing key), fall back to a one-line reminder: *"Switch the project's board view to Manual ordering — `sortOrder` is ignored otherwise, so the board won't match this order until you do."*

## E2. Work the next unfinished sub-issue

Pick the first sub-issue that isn't already `In Review` or `Done`. Run the full per-story flow — `/linear:start` steps 1–19 — for that sub-issue: branch, implement, validate, PR, status → In Review, terminal review. Sub-issues already In Review or Done are skipped (named in the disclosure, not re-worked).

## E3. Stop at the PR — every time

In interactive mode, after the sub-issue reaches its PR and terminal review
(step 19), **stop**. Do not merge or start the next sub-issue. Surface:

```
<SUB-X> is in review: <PR URL>
Review it, run /linear:finish when ready, then re-run /linear:start <epic-ID> to pick up the next sub-issue (<SUB-Y>).
```

<mark>**Interactive mode advances across invocations, each gated by your /finish + re-run.**</mark> This is the same per-PR approval `/linear:start`'s [Rules](../start.md#rules) demand; unattended mode is the explicit opt-in to auto-advance.

In unattended mode, `/linear:start` step 19 runs `/linear:finish` inline. After
it succeeds, refresh the sub-issues and continue to the next unfinished
sub-issue. Stop the loop immediately if finish hits a hard stop. When none
remain, continue to E4.

## E4. Epic complete

When every sub-issue is `Done`, report it. Interactive mode suggests moving the
epic itself to Done; unattended mode moves it to Done without prompting:

```
All N sub-issues of <epic-ID> are Done. Move the epic to Done? (it carries no code of its own)
```

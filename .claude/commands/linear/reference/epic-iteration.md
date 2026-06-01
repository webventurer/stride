# Epic iteration

> The path `/linear:start` follows when its argument is an epic rather than a story. The decision — single story by default, iterate when the argument is an epic — stays in `start.md` (step 1); this file holds the execution mechanics so the command stays scannable. Step numbers below refer to `/linear:start`'s steps.

> When the argument is an epic, `/linear:start` works its sub-issues one at a time, pausing at every PR. An epic has no code of its own — its work lives in its stories.

---

## E1. Enumerate and disclose upfront

List the sub-issues before doing anything:

```bash
uv run .claude/tools/linear_cli.py list-by-parent <epic-UUID>
```

Order by `sortOrder` ascending (board order). When `sortOrder` is unset, fall back to identifier order. Then surface the plan — scope visible upfront, with an escape hatch:

```
Epic <ID>: <title>
N sub-issues, worked one at a time — you review and /finish each PR before the next starts:
  1. <SUB-1> — <title> [state]
  2. <SUB-2> — <title> [state]
  ...
Starting with the first unfinished one: <SUB-X>. Say stop to bail out.
```

**Manual-ordering reminder — once, here.** The disclosed order reflects `sortOrder`, but Linear only shows that order on the board when the view is set to **Manual**. If the board order doesn't match the disclosure, surface once:

> *"Linear only honours manual position when the board view is set to Manual ordering — `sortOrder` is ignored otherwise. Switch the view to Manual so the epic's position shows?"*

## E2. Work the next unfinished sub-issue

Pick the first sub-issue that isn't already `In Review` or `Done`. Run the full per-story flow — `/linear:start` steps 1–15 — for that sub-issue: branch, implement, validate, PR, status → In Review, terminal review. Sub-issues already In Review or Done are skipped (named in the disclosure, not re-worked).

## E3. Stop at the PR — every time

After the sub-issue reaches its PR and terminal review (step 15), **stop**. Do not merge, do not start the next sub-issue. Surface:

```
<SUB-X> is in review: <PR URL>
Review it, run /linear:finish when ready, then re-run /linear:start <epic-ID> to pick up the next sub-issue (<SUB-Y>).
```

<mark>**The epic advances across invocations, each gated by your /finish + re-run — never an open-ended in-run loop, never an auto-advance.**</mark> This is the same per-PR approval `/linear:start`'s [Rules](../start.md#rules) demand; epic iteration just sequences it.

## E4. Epic complete

When every sub-issue is `Done`, report it and suggest moving the epic itself to Done:

```
All N sub-issues of <epic-ID> are Done. Move the epic to Done? (it carries no code of its own)
```

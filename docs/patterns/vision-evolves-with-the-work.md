# Vision evolves with the work

> When the trace-back to a Vision criterion can't be made honestly, **evolve the Vision on the same branch as the work that revealed the gap.** Don't push the evolution into a separate planning cycle.

## The recognised situation

You're at `/linear:plan-work` draft time, or at `/linear:finish` trace-confirm time. The trace-back to a Vision Success criterion doesn't fit. The candidates are close but none directly names what this work is in service of. The strain is real; revising the trace doesn't resolve it either — [*revise, don't stretch*](./revise-dont-stretch.md) catches the cases that *do* resolve via revision.

The Vision is genuinely missing a criterion. The work has surfaced an outcome the project is committed to but hasn't yet named.

## The move

Add the missing criterion to `VISION.md` **on the current branch**, as a separate atomic commit. Re-run the gate that fired — it now traces cleanly. Continue with the original work. When the PR merges, [`/linear:finish` step 8d](https://github.com/webventurer/stride/blob/main/.claude/commands/linear/finish.md) picks up the `VISION.md` change and syncs it to the Linear project description.

One branch. One PR. The Vision evolution rides alongside the feature that revealed the gap.

## The two enforcement points

The pattern fires at two distinct gates. Same move at either:

| Gate | When it fires | What it does |
|:--|:--|:--|
| **[`/linear:plan-work`](https://github.com/webventurer/stride/blob/main/.claude/commands/linear/plan-work.md) step 1 — Decision rules** | At draft time, the issue's *"Why this matters"* can't trace to any existing criterion | Prompt the user: add a new criterion to `VISION.md` (re-run `/vision` to evolve it), or drop the issue as out of scope |
| **[`/linear:finish`](https://github.com/webventurer/stride/blob/main/.claude/commands/linear/finish.md) step 5 — trace confirm** | At merge time, the agent flags drift in the *"Why this matters"* trace; the user picks *"something else — missing criterion"* | Post the user's one-line answer to the issue, prompt *stop and add the criterion to `VISION.md` before merging?* If yes, exit cleanly so the user can `/commit` the criterion on the same branch and re-run `/linear:finish` |

The upfront gate is the cheap catch. The merge-time gate is the backup — it fires when the strain wasn't visible until after the work was built. Both end in the same move: evolve the Vision on the branch.

## Why the catch is amendable

A trace gate that fired *only* after merge would force a follow-up PR — *"add the criterion the last PR needed"* — separated from the work that revealed it. Two PRs to review, two commits to navigate by `git bisect`, and a `git log` story where the criterion appears to land out of nowhere.

The amendable catch collapses that into one branch:

| Without amendable catch | With amendable catch |
|:--|:--|
| Trace drift caught after merge — file a follow-up issue | Trace drift caught before merge — pause, amend, resume |
| Follow-up PR adds the criterion in isolation | Same PR carries the criterion *and* the work that revealed it |
| `git log` shows the criterion arriving for no obvious reason | `git log` shows the criterion arriving on the same branch as its motivation |
| Linear sync to project description happens in a separate cycle | `/linear:finish` step 8d syncs `VISION.md` to Linear in the same flow |

The Vision changes only when the work pushes against it — and when it changes, the evidence is right there in the branch.

## Walking through the move

You finish a piece of work and run `/linear:finish`. At the trace-confirm step, the agent flags that the issue's *"Why this matters"* doesn't fit any existing Success criterion cleanly — the closest candidates need bridging language to make the connection hold.

You pick *"something else"*. The agent asks *in one line, what shifted?* — you answer by naming the outcome the project is actually committed to but hasn't yet written down. The agent posts your answer to the issue and prompts: *stop and add the criterion to `VISION.md` before merging?*

You say yes. On the same branch, you add the new criterion to `VISION.md` as a separate atomic commit, then re-run `/linear:finish`. The trace check now matches the just-added criterion. The merge goes through. Step 8d detects `VISION.md` in the merged diff and syncs the updated criteria list to the Linear project description.

End-to-end in one session: strain caught, criterion added, work merged, Linear synced. No follow-up issue, no second PR.

## What this Pattern is *not*

- **Not licence to add a criterion every time a trace feels off.** Read [*revise, don't stretch*](./revise-dont-stretch.md) first — most strain resolves with a revised trace toward an existing criterion. The Vision evolves only when revision can't find a clean fit.
- **Not a way to retroactively justify scope creep.** The new criterion has to describe an outcome the project is genuinely committed to — not just the work in front of you. If the criterion only exists to make this one issue trace cleanly, it's a fictional anchor in slower motion.
- **Not exclusive to** `/linear:finish`. The upfront gate at `/linear:plan-work` step 1 catches the same drift earlier — same move applies. The Pattern is the *evolution on the same branch*, not the gate that surfaces the need.
- **Not a substitute for** `/vision`. Adding a criterion mid-branch is the amendable catch — a one-line addition where the gap is obvious. Re-running `/vision` is for substantive rewrites (new audience, new scope, multiple new outcomes). When in doubt, the prompt at both gates offers `/vision` as the alternative path.

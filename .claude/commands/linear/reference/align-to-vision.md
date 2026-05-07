# Align to Vision

> Single source of truth for how stride ranks work against the project's Vision. Linked by every command that ranks Vision-using work — `/linear:next-steps`, `/linear:plan-work`, and any future Vision-using command. Don't restate the rule in command prompts; link this file instead.

---

## When to apply

Apply this rule when ranking work — choosing which item to surface first from a list of candidates. Examples:

- `/linear:next-steps` ordering backlog candidates
- `/linear:plan-work` ordering proposed follow-ups when a broad description splits into multiple issues
- Any future command that proposes "what to do next"

Do **not** apply this rule for execution commands (`/linear:start`, `/linear:fix`, `/linear:finish`). Those execute one chosen issue — there's nothing to rank.

## The rule

1. **Read `VISION.md`'s Success criteria.** That section names the outcomes the project is committed to.

2. **For each candidate item, infer which Success criterion it advances.** Use the issue body's "Why this matters" section — WB-256 enforces that newly drafted issues name the outcome they serve. For an issue without an explicit reference, reason from title and description about which criterion the work most plausibly advances. If the connection is genuinely unclear, treat the item as serving no specific criterion.

3. **Order by least-progressed first.** Among candidates, surface those advancing the **least-progressed** Success criteria higher. "Least-progressed" is a judgment based on what's visible in the project state:

   - Count of Done issues that referenced this criterion (fewer = less progressed)
   - Recent activity on the criterion (none in weeks = less progressed)
   - Whether the criterion has any in-flight or Backlog work at all (none = least progressed)

   The agent reasons from the available signals; there's no parser or scoring formula. Items advancing already-well-progressed criteria sink in the order; items advancing neglected criteria rise.

4. **Tiers stay intact. Alignment only orders items within a tier.**

   Each ranking command has its own priority chain. `/linear:next-steps` uses: build failure → PRs needing fix → in-progress → PRs needing review → approved PRs to merge → backlog. Each group in that chain is a **tier**, and the chain decides every comparison *between* tiers. Alignment never moves an item between tiers — it only orders items inside a single tier, where they'd otherwise be tied at the priority level.

   So a build failure always sits above a backlog item, no matter how Vision-aligned the backlog item is. Alignment never overrides priority; it just sorts the leftovers priority couldn't separate.

   **Where this matters most.** The backlog tier is where ties pile up — multiple Medium-priority issues sitting in Backlog with no other discriminator. That's where Vision alignment does its real work.

   **Concrete example.** `/linear:next-steps` sees:

   - 1 PR needing fix (PR #12)
   - 3 backlog issues at Medium priority: A, B, C

   Output:

   1. **PR #12** — PRs-needing-fix tier, sits above everything below
   2. **Issue B** — backlog tier; advances *"git log reads as a stakeholder narrative"* (no Done issues against this criterion yet — least progressed)
   3. **Issue A** — backlog tier; advances *"Linear board state matches branch state"* (already several Done issues — more progressed)
   4. **Issue C** — backlog tier; doesn't cleanly trace to any criterion — flagged for `/vision` review

   PR #12 stayed on top — alignment didn't move it down even though Issue B serves a less-progressed outcome. The priority ordering put PRs needing fix above the backlog tier, full stop. Within the backlog tier, alignment ordered B before A before C.

## What to surface to the user

When recommending an item, name the Vision outcome it serves. The user should see *why* the agent picked this one — not just that it was picked.

Format inside command output:

```
1. **WB-XX — Title** — reason. Serves Vision outcome: "<criterion line from VISION.md>".
```

If a candidate doesn't cleanly serve any Success criterion, surface that honestly:

```
2. **WB-YY — Title** — reason. Doesn't cleanly trace to a Vision outcome — flag as a candidate for /vision review.
```

An issue that can't trace to Vision is information: either the work is out of scope, or the Vision needs a new outcome.

## Without `VISION.md`

Commands using this rule treat missing `VISION.md` as a hard gate — same behaviour as `/linear:plan-work`. Stop and suggest `/vision`. Don't fall back to ranking without Vision; that defeats the rule's purpose.

## Why "least-progressed first"

YAGNI default. Alternatives — user-specified focus criterion, weighted-by-priority, criterion-of-the-week — are deferrable until usage shows the need. Least-progressed-first matches the natural project shape: outcomes neglected for weeks need attention more than outcomes that already have momentum.

When usage reveals a different default would help, swap the heuristic in this file. Every command that links here picks up the change.

## Why a separate reference doc

Each command that ranks against Vision needs the same heuristic. Restating it in every command prompt creates drift — one command's prompt evolves, the others don't, and "Vision is the guiding light" quietly fragments into "Vision is one of several lights, weighted differently per command." Linking a single file keeps the rule load-bearing and replaceable in one place.

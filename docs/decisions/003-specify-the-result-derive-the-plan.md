# 003 — Specify the result, derive the plan at start

**Date:** 2026-08-22
**Status:** Accepted
**Linear:** WB-654

## Context

A Linear card and the implementation it produces are written at different moments. The card is written before anyone has read the code that the work will touch; the implementation happens once that code is in front of you. When the card carries an edit list — these files, these functions, in this order — it freezes a route chosen without the ground in view. By the time work starts, the repository has usually moved: a helper already exists, a caller was renamed, the obvious seam is somewhere else.

Two bad outcomes follow. The agent either follows a stale route and produces edits that fit the card but not the codebase, or it silently departs from the card and nobody can tell whether the work is finished, because the card described edits rather than a result.

`/linear:start` made this worse by trusting the card wholesale — "the plan was agreed during `/plan-work`" — so nothing between the card and the diff was visible to the user.

## Decision

**A card declares the result; the implementation route is derived from the repository when work starts.**

Two conventions carry the two halves:

- [Specify the result, not the edit](https://github.com/webventurer/stride/blob/main/docs/conventions/specify-the-result-not-the-edit.md) — the card states the outcome, the boundary, what stays outside it, and how completion is proved. It may name the expected shape; it may not be satisfiable by only one sequence of edits.
- [Derive the plan when work starts](https://github.com/webventurer/stride/blob/main/docs/conventions/derive-the-plan-when-work-starts.md) — `/linear:start` reads the relevant code, tests, configuration, and callers first, then surfaces an ordered checklist before editing and marks items complete as it works.

The card is the contract. The checklist is the current route, and evidence found while implementing may change it — the destination stays fixed.

## Why

- **The route ages, the result doesn't.** An outcome written last week is still true today; an edit list often isn't. Deriving the route at start time means the plan is always as fresh as the repository.
- **Done becomes checkable.** A result names its own proof. An edit list only tells you the edits were made, which is not the same as the work being finished.
- **The checklist is visible without being a gate.** The user sees what the agent intends to do before it edits, and can stop it — but the common path continues without a prompt, so the disclosure costs nothing when the plan is obviously right.
- **Scope stays where the card put it.** Deriving a route is not licence to widen the work. A missing decision, a contradiction in the card, or genuine scope growth stops the flow and asks one question.

## Consequences

- `/linear:start` step 7 is "plan, then implement": inspect the repository, show an unchecked `- [ ]` checklist, then work through it visibly ([#192](https://github.com/webventurer/stride/pull/192))
- `/linear:plan-work` cards are written as outcomes with an explicit boundary and proof, not as edit lists
- The workflow reference and the docs site restate the same behaviour, so all three descriptions of `/linear:start` agree
- The conventions live in `docs/conventions/` ([#191](https://github.com/webventurer/stride/pull/191)), excluded from the published docs site while the set settles

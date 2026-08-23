# Derive the plan when work starts

> The card is the contract. The checklist is the current route.

## The check

Before implementation begins, ask:

1. **Does the card define done?** It should name the outcome, owner, boundary, exclusions, and proof without prescribing edits
2. **Does the checklist come from the repository as it exists now?** Read the relevant code, tests, configuration, documentation, and callers before choosing the route
3. **Can evidence change the route without changing the destination?** If not, the checklist has become a second specification

<mark>Keep the destination stable. Derive the route from the ground in front of you.</mark>

## Problem

An implementation plan written into a card starts ageing as soon as the card is filed. Files move, boundaries improve, tests appear, and assumptions become false. Following that stale route wastes current evidence. Ignoring it silently makes the card unreliable.

The opposite failure is a card so vague that implementation begins with no visible route. The agent explores and edits at the same time, so the user cannot see what it believes the work involves or where scope has started to drift.

## The convention

- `/linear:plan-work` writes the durable contract: the result, its owner and boundary, what is excluded, and what proves completion
- `/linear:start` reads the current repository before editing, then derives a short ordered checklist of the necessary changes and checks
- Show the checklist before editing and mark each item complete as the work progresses
- Revise the checklist when implementation evidence changes the route; keep the card's result, boundary, constraints, and proof fixed
- Pause when the repository exposes a missing product decision, a contradiction in the card, or scope that must expand
- Keep trivial work trivial. A one-step result gets a one-item checklist

The checklist is working context. It records the best route supported by current evidence. It does not earn permanence by being written down.

Write the contract when the work is agreed. Write the route when the work starts. The card stays current because it contains only durable facts. The checklist stays accurate because it comes from today's repository.

## Example

### Before

```text
# ❌ The card freezes an implementation route
Move signing from api.py to authentication.py.
Update BitunixClient to call build_headers().
Move the signing tests to test_authentication.py.
```

The work is judged by whether those edits happened, even if the repository now reveals a better boundary.

### After

```text
# ✅ The card defines done
Signed Bitunix request headers have one owner.

Owner: Bitunix API authentication.
Crosses the boundary: request details go in; signed headers come out.
No longer happens: endpoint operations construct signatures.
Proven by: the characterised requests keep the same headers and signatures.

# ✅ /linear:start derives the current route
- [ ] Trace every caller that creates signed headers
- [ ] Reuse the API package boundary already present
- [ ] Move signing behind that boundary without changing request bytes
- [ ] Run the authentication characterisation tests and the full API suite
```

The card remains true if file names or existing boundaries change. The checklist remains concrete because it was derived from the code that will actually be edited.

## Why this is useful

- Linear keeps a durable statement of done instead of a stale edit list
- The user sees a concrete route before code changes
- New evidence can improve the implementation without quietly rewriting the requirement
- Scope changes become visible because they cannot hide inside checklist edits
- Trivial cards stay light without needing a separate planning mode

## When to avoid

- Mechanical work small enough for `/linear:quick`
- A discovery spike whose purpose is to learn what the result should be
- A real change to the required result. Update or replace the card instead of disguising it as a checklist revision

## Related conventions

- **[Specify the result, not the edit](specify-the-result-not-the-edit.md)**: defines what belongs in the durable card
- **[Give each responsibility one visible home](give-each-responsibility-one-visible-home.md)**: gives the checklist an existing boundary to inspect and preserve
- **[Make future change easier](make-future-change-easier.md)**: lets current evidence choose the route that leaves the next change easier

---

_The card defines done. The repository decides how to get there._

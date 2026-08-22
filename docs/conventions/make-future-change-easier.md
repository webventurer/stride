# Make future change easier

> Meaningful simplification leaves the next change touching fewer concepts and fewer places.

## The check

Before choosing a design or calling something simpler, ask:

1. **What will the next known change have to understand and touch?** If every caller must know the implementation, the boundary has not helped
2. **Did this remove complexity from the system, or only move and rename it?** Fewer lines are not simpler when the same decisions remain scattered
3. **Can necessary detail live behind one small, complete handoff?** A caller should state its intent without coordinating the implementation
4. **Does an existing responsibility already own this?** Deepen that foundation before creating a parallel helper, path, or rule
5. **Has the boundary been earned by the code that exists?** Do not add extension points for changes that have not arrived

<mark>Complexity does not need to disappear. It needs one home and a simple handoff, so it can be understood and changed once.</mark>

## Problem

Simplification is often measured by the current diff: fewer lines, fewer files, or a shorter call. That can make the code smaller while leaving the real burden untouched. Callers still know the sequence, representation, policy, and failure rules, so the next change must rediscover and edit every copy.

The opposite mistake builds abstractions for predicted futures. An interface with no present responsibility adds a concept without absorbing any complexity. It makes today's change harder in exchange for flexibility that may never be used.

## The convention

- When two choices deliver roughly the same value, choose the one that leaves the next change easier
- Judge simplification by the knowledge and coordination a change requires, not by line count alone
- Put necessary detail with the responsibility that owns it and expose the smallest complete handoff
- Let callers name what they need; keep sequencing, representation, and policy behind the boundary
- Extend an existing owner before creating a parallel route to the same result
- Let new knowledge deepen the foundation so everything built on it benefits without learning the detail again
- Add a boundary only when present code reveals one; do not build speculative flexibility

A simple interface is not an interface class. It may be one function, one module entry point, one command, or one document that gives detailed implementation a stable home.

Meaningful simplification may add code inside the owner. It is still simpler when callers lose decisions, concepts, or coordination and the next change happens in one place.

## Example

### Before

```text
# ❌ Every caller owns the output policy
Image CLI: choose the root, build the dated path, write metadata
Video CLI: choose the root, build the dated path, write metadata
Skill: document the root and layout independently

Changing the output policy means finding and changing every copy.
```

### After

```text
# ✅ The output responsibility owns the policy
Callers ask for an image or video destination.
The output responsibility owns the root, dated layout and metadata paths.
Documentation describes that public result and links to its owning rule.

Changing the layout means changing its owner and the public claim; callers keep
stating the same intent.
```

The detailed layout still exists. The simplification is that it has one owner, while callers see a handoff expressed in their own language.

## Why this is useful

- A change to one responsibility has one place to land
- Callers remain readable because they express intent rather than mechanics
- Detailed implementations can improve without spreading their vocabulary outward
- Existing foundations compound in value: one improvement benefits every consumer
- Present requirements shape abstractions, so unused flexibility does not become permanent maintenance

## When to avoid

- One obvious use with no repeated policy or coordination — keep it inline until a boundary emerges
- A smaller interface that hides choices, failures, or effects the caller must understand
- Consumers that only look similar but own different policies; forcing them together raises the future cost of change
- A rewrite justified only by hypothetical future work. Wait for the requirement that reveals the right seam

## Related conventions

- **[Specify the result, not the edit](specify-the-result-not-the-edit.md)** — a result leaves implementation free to take the easiest path as reality becomes clearer
- **[Give each responsibility one visible home](give-each-responsibility-one-visible-home.md)** — the home that absorbs necessary detail and presents the simple handoff
- **[Keep every restatement true](keep-every-restatement-true.md)** — foundations compound only when consumers reference them instead of freezing copies
- **[Read the set as one document](read-the-set-as-one-document.md)** — a change is not easier when it leaves the surrounding claims contradictory

---

_Build on what already works. Leave the next change less to learn._

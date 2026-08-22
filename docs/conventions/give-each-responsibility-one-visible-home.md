# Give each responsibility one visible home

> One responsibility, one sentence, one place to look.

## The check

Before choosing a module or a package, ask:

1. **Can you describe it in one sentence without unrelated conjunctions?** An "and" joining unrelated ideas means two responsibilities
2. **Is the choice proportional to the code that exists now?** A package for one module is a folder pretending to be a boundary
3. **Does the name say the responsibility, or the mechanism?** Name what it owns, not how it works

<mark>A responsibility spread across directories cannot be read, reviewed, or replaced as one thing.</mark>

## Problem

Code accumulates by mechanism — a `handlers` module here, a `utils` module there — until no directory answers "what owns this?". Reviewing one responsibility means opening six files across four directories, and nobody can tell where it starts or stops. The opposite failure is as bad: a package created for a single module, promising a boundary that holds nothing.

## The convention

- Describe every responsibility in one sentence without unrelated conjunctions
- Keep one-module responsibilities as modules
- Use a package when a responsibility needs multiple modules
- Name the package after the responsibility
- Put its responsibility statement in `__init__.py`
- Expose one clear public handoff where the domain permits it
- Keep orchestration outside the responsibility it coordinates

A useful completion test:

> A developer can understand what this responsibility owns, what enters it, what leaves it, and when it finishes by opening one module or one directory.

## Example

### Before

```text
# ❌ Responsibility spread by mechanism
app/bitunix/
  exchange_client.py
  exchange_reconcile.py
  polling_helpers.py
  trade_utils.py
```

Four files, no directory that owns "keep the exchange matching the plan".

### After

```text
# ✅ One directory owns it
app/bitunix/trade_plan_execution/
  __init__.py        # the responsibility statement, and the public handoff
  exchange.py
  polling.py
  account_facts.py
  reconciliation/
```

```python
"""
Take an accepted TradePlan and keep Bitunix aligned with it until the plan ends.

The package reads exchange facts, places entries, reconciles live state,
applies corrections, and records terminal outcomes.

It owns exchange-side execution after plan acceptance; signal decisions, plan
construction, and operator reporting remain with Premium.
"""
```

The third paragraph is the load-bearing one — it says what the package does *not* own.

## Why this is useful

- One directory can be read, reviewed, and replaced as a unit
- The responsibility statement is where a reader already looks
- Naming what it does not own stops two packages quietly claiming the same thing
- The one-sentence test catches a split responsibility before the code grows around it

## When to avoid

- A responsibility that genuinely fits in one module — leave it a module
- Framework or tooling layout that prescribes the directory shape
- A boundary you cannot yet name. Wait for the second module; the name will be obvious then

## Related conventions

- **[Specify the result, not the edit](specify-the-result-not-the-edit.md)** — a card names the responsibility that owns its result
- **[Keep every restatement true](keep-every-restatement-true.md)** — a responsibility statement is a claim; it drifts when the code moves and nobody rereads it
- **[Read the set as one document](read-the-set-as-one-document.md)** — reading the set is what caught this document's subtitle contradicting its own second rule

---

_If you cannot point at it, it does not have a home._

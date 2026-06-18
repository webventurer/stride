# Recover: backfill the `focus` field into `.stride.json`

> **What this is**: the recovery runbook for a `.stride.json` written before stride added the `focus` field — the output-abstraction default the `/linear:*` commands read (`outcome` vs `technical`). `/linear:setup` runs this backfill automatically, so most installs never need this page — reach for it when materialising `focus` **outside** setup, or when the backfill reports the config is malformed.
>
> **Why it's safe to run any time**: `backfill-focus` is idempotent — a no-op when there's no `.stride.json`, and a no-op when the file already carries `focus` (an explicit `"technical"` is never clobbered). It never contacts Linear and only ever adds the one missing field.

## 1. Run the backfill

```bash
uv run .claude/tools/linear_cli.py backfill-focus
```

What it does, in order:

- Reads `.stride.json` — returns the config unchanged if the file is missing (nothing to backfill).
- If the config lacks `focus`, writes `"focus": "outcome"` into it. `outcome` is stride's default abstraction — recommendations lead with the action and one-line reason, not the implementation.
- If the config already has `focus`, leaves it untouched — an explicit `"technical"` is preserved, never overwritten.
- Returns the resulting config as JSON. An empty `{}` means there was no `.stride.json` — nothing to backfill.

This is the single place `focus` is materialised. The output-generating commands only ever *read* it (falling back to `outcome` when absent), so running them never rewrites the config as a side effect.

## 2. If the backfill reports invalid JSON

```
.stride.json contains invalid JSON — fix it or delete it and re-run /linear:setup.
```

The file couldn't be parsed, so the backfill **made no change** — nothing is lost. Recover either way:

- **Fix and retry** — repair the JSON (a trailing comma or unquoted key is the usual culprit), then re-run the backfill from step 1.
- **Start fresh** — delete `.stride.json` and run `/linear:setup`, which writes a new one from scratch with `focus` already set.

## 3. Verify

`.stride.json` now carries `focus`:

```bash
cat .stride.json
```

A `focus` key reading `"outcome"` (or your preserved `"technical"`) means the backfill is done.

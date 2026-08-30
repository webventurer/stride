# Recover: backfill the `unattended` field into `.stride.json`

> **What this is**: the recovery guide for a `.stride.json` written before Stride added the `unattended` field. `/linear:setup` runs this backfill automatically, so use this guide only when adding the field outside setup or recovering from an error.
>
> **Why it is safe to run**: `backfill-unattended` adds `false` only when the field is missing. It does nothing when `.stride.json` is absent and never replaces an existing `true` or `false`.

## 1. Run the backfill

```bash
uv run .claude/tools/linear_cli.py backfill-unattended
```

The command:

- Reads `.stride.json`. If the file is missing, it returns an empty `{}` and changes nothing.
- Adds `"unattended": false` when the field is missing. This keeps Stride in interactive mode.
- Preserves an existing `true` or `false` value.
- Returns the resulting config as JSON.

Delivery commands only read this field, falling back to `false` when it is missing. They never rewrite `.stride.json` as a side effect of shipping work.

## 2. If the config contains invalid JSON

The backfill stops without changing the file and reports:

```
.stride.json contains invalid JSON — fix it or delete it and re-run /linear:setup.
```

Recover in either of these ways:

- **Fix and retry** — repair the JSON, then run the backfill again.
- **Start fresh** — delete `.stride.json` and run `/linear:setup`, which writes a new file with `unattended` already set.

## 3. Verify the field

```bash
cat .stride.json
```

The backfill is complete when `unattended` is present and holds either `false` or your existing `true` value.

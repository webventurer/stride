# Recover: backfill the `parallel-sessions` field into `.stride.json`

> **What this is**: the recovery guide for a `.stride.json` written before Stride added the `parallel-sessions` field, the most cards Stride runs at once. `/linear:setup` runs this backfill automatically, so use this guide only when adding the field outside setup or recovering from an error.
>
> **Why it is safe to run**: `backfill-parallel-sessions` adds `3` only when the field is missing. It does nothing when `.stride.json` is absent and never replaces a value already there.

## 1. Run the backfill

```bash
uv run .claude/tools/linear_cli.py backfill-parallel-sessions
```

The command:

- Reads `.stride.json`. If the file is missing, it returns an empty `{}` and changes nothing.
- Adds `"parallel-sessions": 3` when the field is missing.
- Keeps any value already there, even one Stride would refuse.
- Returns the resulting config as JSON.

Commands that read the field fall back to `3` when it is missing. They never rewrite `.stride.json` as a side effect of shipping work.

## 2. If the value is refused

A whole number of 1 or more is valid; `1` means one card at a time. Any other value, such as `0`, `-2`, `"three"`, `2.5`, `true` or `null`, is refused when the field is read, with a message naming the field:

```
.stride.json "parallel-sessions" must be a whole number of 1 or more, not 0.
```

The backfill doesn't change a refused value. Edit `.stride.json` to a whole number of 1 or more, or delete the field and run the backfill again to get `3`.

## 3. If the config contains invalid JSON

The backfill stops without changing the file and reports:

```
.stride.json contains invalid JSON — fix it or delete it and re-run /linear:setup.
```

Repair the JSON and run the backfill again, or delete `.stride.json` and run `/linear:setup`, which writes a new file with `parallel-sessions` already set.

## 4. Verify the field

```bash
jq '."parallel-sessions"' .stride.json
```

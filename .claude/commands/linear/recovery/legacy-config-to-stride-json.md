# Recover: legacy `.linear_project` → `.stride.json`

> **What this is**: the recovery runbook for an older install pinned with a legacy `.linear_project` file (INI-style, from before stride moved its project pin to `.stride.json`). `/linear:setup` runs this migration automatically, so most installs never need this page — reach for it when recovering a pin **outside** setup, or when the migration reports the legacy file is malformed.
>
> **Why it's safe to run any time**: `migrate-legacy-config` is idempotent — a no-op when there's no `.linear_project`, and it only ever derives `.stride.json` from what the legacy file already says. It never contacts Linear and never touches a project.

## 1. Run the migration

```bash
uv run .claude/tools/linear_cli.py migrate-legacy-config
```

What it does, in order:

- Reads `.linear_project` — INI-style `key = value` lines (`#` comments ignored); a bare first line with no `=` is taken as the project name.
- Writes the same settings to `.stride.json`.
- Deletes `.linear_project`.
- Returns the migrated config as JSON. An empty `{}` means there was no legacy file — nothing to migrate.

## 2. Gitignore the new file

The legacy file may have been listed in `.gitignore`; the new one needs to be too. After a successful migration, append `.stride.json` to `.gitignore` if it isn't already listed.

## 3. If the migration reports a malformed file

```
.linear_project is malformed (no project found) — left in place.
Fix it or delete it and re-run /linear:setup.
```

No project name could be parsed, so the migration **left `.linear_project` untouched** — nothing is lost. Recover either way:

- **Fix and retry** — edit `.linear_project` so it names a project (a bare first line with the project name, or a `project = <name>` line), then re-run the migration from step 1.
- **Start fresh** — delete `.linear_project` and run `/linear:setup`, which writes a new `.stride.json` from scratch.

## 4. Verify

`.stride.json` now holds the project pin and the legacy file is gone:

```bash
cat .stride.json && test ! -e .linear_project && echo "legacy file removed"
```

A `.stride.json` carrying `project` and `api_key_env`, with no `.linear_project` left behind, means the migration is done.

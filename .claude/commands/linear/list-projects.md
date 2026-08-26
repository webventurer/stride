---
description: List all projects in the connected Linear workspace.
---

# List Linear projects

Show all projects in the connected Linear workspace.

Read [unattended mode](reference/unattended.md) before running. This command has
no routine approval gate, so both modes follow the same read-only steps.

## Steps

### 1. Fetch projects

Fetch all active projects via `linear_cli.py`. Workspace-iterating, so the per-workspace `LINEAR_API_KEY=` wrap is explicit:

```bash
LINEAR_API_KEY=$LINEAR_<WORKSPACE>_API_KEY uv run .claude/tools/linear_cli.py project list
```

### 2. Display

Present the results as a table:

| Project | Lead | Summary |
|:--------|:-----|:--------|
| Project Name | Jane Doe | One-line summary |

- If a project has no summary, show "—"
- If a project has no lead, show "—"
- Sort by most recently updated first

### 3. Summary

End with a one-line summary: "N projects found."

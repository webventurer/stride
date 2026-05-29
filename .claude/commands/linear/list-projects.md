# List Linear projects

Show all projects in the connected Linear workspace.

## Steps

### 1. Fetch projects

Fetch all active projects via linctl *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
LINCTL_API_KEY=$LINEAR_<WORKSPACE>_API_KEY linctl project list --json
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

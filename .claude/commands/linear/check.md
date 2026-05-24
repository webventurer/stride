# Check Linear connections

Verify linctl can authenticate against every configured Linear workspace.

## Steps

### 1. Find configured workspaces

Look for `LINEAR_*_API_KEY` env vars currently set in the shell (these come from `~/.env`):

```bash
env | grep -oE '^LINEAR_[A-Z_]+_API_KEY' | sort -u
```

If none are found, tell the user to add at least one `LINEAR_<TEAM>_API_KEY` to `~/.env` — see [reference/setup.md](reference/setup.md).

### 2. Test each workspace

For each env var found, run linctl's identity check to confirm the key works *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
LINCTL_API_KEY="$LINEAR_<TEAM>_API_KEY" linctl whoami --json
```

Report the result as a table:

| Workspace | Env var | Status | User |
|:----------|:--------|:-------|:-----|
| Org1 | `LINEAR_ORG1_API_KEY` | Connected | you@example.com |
| Org2 | `LINEAR_ORG2_API_KEY` | Connected | you@example.com |

If a workspace fails, show the error and suggest checking:

- The API key is set in `~/.env` and the shell has loaded it (`source ~/.env` or restart the shell)
- The key value matches an active personal API key in Linear's *Settings → API*
- `which linctl` returns a path — if not, `brew install dorkitude/linctl/linctl`

### 3. Summary

End with a one-line summary: "N of M Linear workspaces connected via linctl."

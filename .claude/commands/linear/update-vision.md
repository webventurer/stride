# Mirror VISION.md to the Linear project description

Push the contents of `VISION.md` into the Linear project's `description` field so the Linear project page reflects the canonical Vision.

Workflow: edit `VISION.md` → `/linear:update-vision` → confirm the diff → Linear updated.

## Rules

- `VISION.md` at the repo root is the source of truth — this command is one-way (repo → Linear)
- For existing projects: show the diff, require explicit confirmation before writing, and never touch metadata other than `description`
- For new projects (no `.linear_project`): the user supplies the name, `VISION.md` becomes the initial description, the team is resolved from `linctl team list` — no diff exists to confirm
- If `VISION.md` and the current Linear description already match, skip the write — report and stop
- The user's `.linear_project` selection drives which project is updated (or is written on first create)

---

## Steps

### 1. Vision check

Read `VISION.md` from the repo root.

- **If missing**: stop and tell the user:

  ```
  No VISION.md found at the repo root.

  /linear:update-vision needs VISION.md to push to Linear — it's the
  source of truth for the project's description.

  Run /vision first to author one, then re-run /linear:update-vision.
  ```

- **If present**: load the full file contents.

### 2. Resolve project

Check for a `.linear_project` file in the repository root.

- If **found**: read the project name from it and continue to step 3.
- If **not found**: list available projects *(auth per [reference/workflow.md](reference/workflow.md))*:

  ```bash
  LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl project list --json
  ```

  Offer two choices:

  1. **Pick an existing project** — choose from the list. Save the selection to `.linear_project`.
  2. **Create a new project** — follow [Create new project](#create-new-project) below.

  Once `.linear_project` exists, check the repo's `.gitignore` — if `.linear_project` isn't listed, append it. Then route: path 1 continues to step 3 (fetch the existing project's description), path 2 continues to step 6 (confirm — `linctl project create` already wrote the description, so the fetch / diff / write steps are no-ops).

#### Create new project

When the user picks *Create new project*:

1. Ask for the project name.
2. Resolve the Linear team:
   ```bash
   LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl team list --json
   ```
   - If exactly one team is returned, use its `key` (e.g. `WB`)
   - Otherwise, ask the user to choose
   - If no teams are returned, stop — the user has no team to create projects on
3. Create the project, passing `VISION.md`'s contents as the description via shell substitution so newlines survive:

   ```bash
   LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl project create \
     -t <TEAM-KEY> \
     --name "<project-name>" \
     --description "$(cat VISION.md)" \
     --json
   ```

   If the create fails (for example the user lacks permission to create projects on the team), surface the error and stop — do not retry silently.

4. Save the new project name to `.linear_project`. Capture the project URL from the JSON response — step 6 will display it.

### 3. Get the current project state

Fetch the existing project:

```bash
LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl project get "<project-name-from-.linear_project>" --json
```

Capture:

- Project ID (needed for the update in step 5)
- Current `description`
- Project URL

If the project cannot be found, stop and tell the user the name in `.linear_project` doesn't match any project they have access to.

### 4. Compare and decide

Compare the contents of `VISION.md` against the current Linear `description` (after trimming surrounding whitespace).

- **Identical**: report and stop:

  ```
  Linear project description already matches VISION.md — no update needed.
  ```

- **Different**: show the user what will change. Display the unified diff or a clear before/after — the agent picks the form that reads best. Then ask:

  ```
  Replace the Linear project description with VISION.md? (y/n)
  ```

  If the user declines, stop without writing.

### 5. Write

Only after explicit yes:

```bash
LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl project update <project-id-from-step-3> \
  --description "$(cat VISION.md)"
```

The `$(cat VISION.md)` substitution preserves markdown newlines and special characters.

### 6. Confirm

Display:

- Linear project description: Updated
- Project URL

End the command — no further status changes, no follow-up commits.

---

## Error handling

- `VISION.md` missing → stop, suggest `/vision`
- `.linear_project` missing → resolve interactively per step 2 (pick existing or create new)
- Project not found in Linear → stop, ask the user to verify `.linear_project`
- `linctl team list` returns no teams (create-new path) → stop, ask the user to verify Linear access
- User declines the diff → stop without writing
- `linctl project update` / `linctl project create` fails → show the error and stop; do not retry silently

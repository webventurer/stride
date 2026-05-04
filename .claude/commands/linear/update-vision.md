# Mirror VISION.md to the Linear project description

Push the contents of `VISION.md` into the Linear project's `description` field so the Linear project page reflects the canonical Vision.

Workflow: edit `VISION.md` → `/linear:update-vision` → confirm the diff → Linear updated.

## Rules

- `VISION.md` at the repo root is the source of truth — this command is one-way (repo → Linear)
- Always show the user what will change and require explicit confirmation before writing
- If `VISION.md` and the current Linear description already match, skip the write — report and stop
- Never touch other project metadata (target date, state, priority, summary, teams)
- The user's `.linear_project` selection drives which project is updated

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

- If **found**: read the project name from it
- If **not found**: list available projects via `list_projects`, ask the user to choose, and save their selection to `.linear_project`. Then check the repo's `.gitignore` — if `.linear_project` isn't listed, append it.

### 3. Get the current project state

Call `get_project` with the resolved name. Capture:

- Project ID (needed for `save_project`)
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

Only after explicit yes, call `save_project`:

- `id`: the project ID from step 3
- `description`: the full contents of `VISION.md`

Pass the markdown directly — do not escape newlines or other characters.

### 6. Confirm

Display:

- Linear project description: Updated
- Project URL

End the command — no further status changes, no follow-up commits.

---

## Error handling

- `VISION.md` missing → stop, suggest `/vision`
- `.linear_project` missing → resolve interactively per step 2
- Project not found in Linear → stop, ask the user to verify `.linear_project`
- User declines the diff → stop without writing
- `save_project` fails → show the error and stop; do not retry silently

# Mirror VISION.md to the Linear project

Push the contents of `VISION.md` into the Linear project's `content` field — the long-form project document — so the Linear project page reflects the canonical Vision.

Workflow: edit `VISION.md` → `/linear:update-vision` → confirm the diff → Linear updated.

> **Why `content`, not `description`, and why `linear_cli.py`:** a project's `description` is a short, length-limited summary — writing a full Vision to it fails with a GraphQL `Argument Validation Error`. The Vision belongs in `content` (the document body). `linctl` has no typed command for `content` (its `project get`/`project update` only touch `description`), so this command reads and writes `content` through `.claude/tools/linear_cli.py`, which uses `linctl graphql` under the hood.

## Rules

- `VISION.md` at the repo root is the source of truth — this command is one-way (repo → Linear)
- For existing projects: show the diff, require explicit confirmation before writing, and never touch metadata other than `content`
- For new projects (no `.linear_project`): the user supplies the name, `VISION.md` becomes the initial `content`, the team is resolved from `linctl team list` — no diff exists to confirm
- If `VISION.md` and the current Linear `content` already match, skip the write — report and stop
- The user's `.linear_project` selection drives which project is updated (or is written on first create)

---

## Steps

### 1. Vision check

Read `VISION.md` from the repo root.

- **If missing**: stop and tell the user:

  ```
  No VISION.md found at the repo root.

  /linear:update-vision needs VISION.md to push to Linear — it's the
  source of truth for the project's content.

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

  Once `.linear_project` exists, check the repo's `.gitignore` — if `.linear_project` isn't listed, append it. Then route: path 1 continues to step 3 (fetch the existing project's `content`), path 2 continues to step 6 (confirm — the create-new flow already wrote `content`, so the fetch / diff / write steps are no-ops).

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
3. Create the project (name + team only — the Vision goes into `content` next, not the length-limited `description`):

   ```bash
   LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl project create \
     -t <TEAM-KEY> \
     --name "<project-name>" \
     --json
   ```

   Capture the project `id` and URL from the JSON response. If the create fails (for example the user lacks permission to create projects on the team), surface the error and stop — do not retry silently.

4. Write `VISION.md` into the new project's `content`:

   ```bash
   LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY uv run .claude/tools/linear_cli.py \
     update-project-content <project-id> --content "$(cat VISION.md)"
   ```

   The `$(cat VISION.md)` substitution preserves markdown newlines and special characters.

5. Save the new project name to `.linear_project`. Step 6 will display the URL.

### 3. Get the current project state

`linctl project get` takes a project **ID**, not a name — so resolve the id (and URL) from the project list by name, then fetch the current `content` via `linear_cli.py` (linctl can't read `content`):

```bash
LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl project list --json \
  | jq -r --arg name "<project-name-from-.linear_project>" '.[] | select(.name == $name) | {id, url}'
LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY uv run .claude/tools/linear_cli.py get-project-content <project-id>
```

Capture:

- Project ID (needed for the update in step 5) and URL — from the `project list` filter
- Current `content` — from `get-project-content` (raw markdown)

If no project matches the name, stop and tell the user the name in `.linear_project` doesn't match any project they have access to.

### 4. Compare and decide

Compare the contents of `VISION.md` against the current Linear `content` (after trimming surrounding whitespace). Linear normalises markdown on save — notably it rewrites `-` list markers to `*` — so a byte-exact match is unattainable even straight after a sync; compare on substance, and treat a difference that is *only* list-marker style as already in sync.

- **Identical**: report and stop:

  ```
  Linear project content already matches VISION.md — no update needed.
  ```

- **Different**: show the user what will change. Display the unified diff or a clear before/after — the agent picks the form that reads best. Then ask:

  ```
  Replace the Linear project content with VISION.md? (y/n)
  ```

  If the user declines, stop without writing.

### 5. Write

Only after explicit yes:

```bash
LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY uv run .claude/tools/linear_cli.py \
  update-project-content <project-id-from-step-3> --content "$(cat VISION.md)"
```

The `$(cat VISION.md)` substitution preserves markdown newlines and special characters. The helper returns `true` on success.

### 6. Confirm

Display:

- Linear project content: Updated
- Project URL

End the command — no further status changes, no follow-up commits.

---

## Error handling

- `VISION.md` missing → stop, suggest `/vision`
- `.linear_project` missing → resolve interactively per step 2 (pick existing or create new)
- Project not found in Linear → stop, ask the user to verify `.linear_project`
- `linctl team list` returns no teams (create-new path) → stop, ask the user to verify Linear access
- User declines the diff → stop without writing
- `update-project-content` / `linctl project create` fails → show the error and stop; do not retry silently

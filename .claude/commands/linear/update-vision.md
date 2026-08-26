---
description: Mirror VISION.md into the connected Linear project page.
---

# Mirror VISION.md to the Linear project

Push `VISION.md` into the Linear project so the project page reflects the canonical Vision: the full document into the `content` field, and the opening tagline into the `description` field — the **subtitle** shown under the project name.

Workflow: edit `VISION.md` → `/linear:update-vision` → show the diff → Linear updated. Interactive mode confirms before the write.

Read [unattended mode](reference/unattended.md) before the write gate.
Unattended mode still shows the diff, then applies the one-way sync without an
approval prompt.

> **The two fields:** a project's `description` is a short, length-limited summary (the subtitle); its `content` is the long-form document body (the Vision). Writing a full Vision to `description` fails with a GraphQL `Argument Validation Error`, so the Vision goes in `content`. This command writes `content` via `linear_cli.py update-project-content` and the short subtitle via `linear_cli.py project update --description`.

## Rules

- `VISION.md` at the repo root is the source of truth — this command is one-way (repo → Linear)
- Two fields are mirrored: `content` (the full document) and `description` (the subtitle, from VISION.md's opening blockquote tagline). Touch no other metadata
- For existing projects: show what will change; interactive mode requires explicit confirmation, while unattended mode applies the one-way sync
- For new projects (no `.stride.json`): the user supplies the name, `VISION.md` becomes the initial `content` and its tagline the subtitle, the team is resolved from `uv run .claude/tools/linear_cli.py team list` — no diff exists to confirm
- If both `content` and subtitle already match `VISION.md`, skip the write — report and stop
- If `VISION.md` has no opening blockquote, leave the subtitle untouched — never blank an existing one
- The user's `.stride.json` selection drives which project is updated (or is written on first create)

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

Check for a `.stride.json` file in the repository root.

- If **found**: read the project name from it and continue to step 3.
- If **not found**: list available projects *(auth per [reference/workflow.md](reference/workflow.md))*:

  ```bash
  uv run .claude/tools/linear_cli.py project list
  ```

  Offer two choices:

  1. **Pick an existing project** — choose from the list. Save the selection to `.stride.json`.
  2. **Create a new project** — follow [Create a Linear project](reference/create-project.md).

  Once `.stride.json` exists, check the repo's `.gitignore` — if `.stride.json` isn't listed, append it. Then route: path 1 continues to step 3 (fetch the existing project's `content`), path 2 continues to step 6 (confirm — the create-new flow already wrote `content`, so the fetch / diff / write steps are no-ops).

### 3. Get the current project state

`uv run .claude/tools/linear_cli.py project get` accepts either a name or UUID — fetch the id, URL, and current subtitle (`description`) from the project list by name, then fetch the long-form `content` via `get-project-content`:

```bash
uv run .claude/tools/linear_cli.py project list \
  | jq -r --arg name "<project-name-from-.stride.json>" '.[] | select(.name == $name) | {id, url, description}'
uv run .claude/tools/linear_cli.py get-project-content <project-id>
```

The **subtitle** is VISION.md's opening blockquote — the `>` tagline directly under the H1 (already in front of you from step 1's read; take the line without its `> ` marker). If VISION.md has no opening blockquote, there's no subtitle to sync this run.

Capture:

- Project ID (for the writes in step 5) and URL — from the `project list` filter
- Current `content` — from `get-project-content` (raw markdown)
- Current subtitle — the `description` from the `project list` filter
- VISION.md tagline — the extracted blockquote (empty if VISION.md has none)

If no project matches the name, stop and tell the user the name in `.stride.json` doesn't match any project they have access to.

### 4. Compare and decide

`/linear:update-vision` mirrors two fields: the full document (`content`) and the subtitle (`description`). Compare each:

- **Content** — `VISION.md` vs the current Linear `content` (after trimming surrounding whitespace). Linear normalises markdown on save — notably `-` list markers become `*`, and it wraps link URLs in `<>` — so a byte-exact match is unattainable; compare on substance and treat normalisation-only differences as in sync.
- **Subtitle** — the extracted tagline vs the current `description`. If VISION.md has no opening blockquote (empty tagline), the subtitle is **out of scope** for this run — never blank an existing subtitle.

Then:

- **Both already match**: report and stop:

  ```
  Linear already matches VISION.md (content + subtitle) — no update needed.
  ```

- **Either differs**: show what will change (the content diff and/or the old→new subtitle). Unattended mode continues to step 5. Interactive mode asks:

  ```
  Replace the Linear content and/or subtitle with VISION.md? (y/n)
  ```

  If the user declines, stop without writing.

### 5. Write

After interactive approval, or immediately in unattended mode, write whichever
field differs:

- **Content** (if it differs) — via `linear_cli.py` (the Vision is long; `uv run .claude/tools/linear_cli.py project update --description` can't carry it):

  ```bash
  uv run .claude/tools/linear_cli.py \
    update-project-content <project-id-from-step-3> --content @VISION.md
  ```

- **Subtitle** (if it differs and the tagline is non-empty) — directly via `linear_cli.py`, since `description` is the short field `--description` is meant for:

  ```bash
  uv run .claude/tools/linear_cli.py project update <project-id-from-step-3> \
    --description "<tagline-from-step-3>"
  ```

`--content @VISION.md` reads the file directly, so markdown newlines and special characters never touch the shell ([why](reference/workflow.md#how-skills-talk-to-linear)). The subtitle is a short single-line field, so it stays inline.

### 6. Confirm

Display:

- Linear project content: Updated / unchanged
- Linear project subtitle: Updated / unchanged / skipped (no tagline)
- Project URL

End the command — no further status changes, no follow-up commits.

---

## Error handling

- `VISION.md` missing → stop, suggest `/vision`
- `.stride.json` missing → resolve interactively per step 2 (pick existing or create new)
- Project not found in Linear → stop, ask the user to verify `.stride.json`
- `uv run .claude/tools/linear_cli.py team list` returns no teams (create-new path) → stop, ask the user to verify Linear access
- User declines the diff in interactive mode → stop without writing
- `update-project-content` / `uv run .claude/tools/linear_cli.py project create` fails → show the error and stop; do not retry silently

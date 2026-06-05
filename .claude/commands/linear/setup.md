# Provision Linear workflow states

Make a Linear team's board match the workflow states stride needs ([`linear_statuses.json`](linear_statuses.json)) — so `/linear:start` / `/linear:finish` transitions land instead of silently no-opping on a missing or misnamed column. When the repo isn't yet pinned to a Linear project, setup also offers to create one and write `.linear_project` (step 6) — so a fresh repo reaches a working board in a single command.

<mark>**Card-aware, and that's the safety model.** An *empty* team (no issues) is set up authoritatively — create the canonical states, archive non-canonical ones, order them to match. A team that *already holds issues* is **never touched**; setup only reports what the board should be and asks the human to adjust it.</mark> A live board is the human's to change, not a script's.

Two Linear constraints worth knowing:

- **Reserved states** (`duplicate`, `triage` types) can't be created or repositioned via the API — Linear pins them. Setup leaves them where they are; everything else is ordered around them.
- **Board state is per-team**, not per-workspace — a workspace can hold several teams, so setup always targets one team deliberately (step 2).

## Steps

### 1. Pick the workspace

List the configured workspaces (these come from `~/.env`):

```bash
env | grep -oE '^LINEAR_[A-Z_]+_API_KEY' | sort -u
```

If none are found, point the user at [reference/setup.md](reference/setup.md) to add a `LINEAR_<WORKSPACE>_API_KEY`. If exactly one is set, use it. If several, ask which workspace to use.

### 2. Pick the team

A workspace can hold several teams; provisioning writes to one team's board. List them — workspace-targeted, so the per-workspace `LINEAR_API_KEY=` wrap is explicit (it overrides `.linear_project`'s single key):

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py team list
```

If exactly one team exists, use its key. If several, <mark>**ask which team to target — never assume the first.**</mark> Capture the chosen team **key** (e.g. `WB`) for the `--team` flag below.

### 3. Provision (card-aware)

Run *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py provision-states --team <TEAM-KEY>
```

The tool checks whether the team holds any issues and branches:

- **Empty team → `{"mode": "provisioned", "created", "deleted", "reordered", "in_sync"}`.** It created any missing canonical states, archived non-canonical ones, and ordered them to the JSON sequence. Safe — no in-progress work to orphan. (Reserved states like `Duplicate` stay where Linear pins them.)
- **Team with cards → `{"mode": "advise", "canonical_order", "board_order", "missing", "extra", "ordered"}`.** <mark>**Nothing was changed.**</mark> Show the user the canonical order vs the board's current order and any missing/extra columns, then ask them to adjust the board in Linear's UI — the API won't reorder a team that holds work.

### 4. Seed a sample card (empty teams only)

A freshly provisioned board has no issues, so Linear renders a blank screen. **If `mode` was `provisioned`**, create one sample card so the columns are visible:

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py issue create -t <TEAM-KEY> --state Backlog \
  --title "Sample card — so the board shows its columns" \
  --description "Placeholder so the board renders. Safe to delete."
```

Skip this when `mode` was `advise` — that team already has cards.

### 5. Tell the user the board-view toggles (UI only)

Applies to either path. These *team* board-view toggles aren't on the team API (`TeamUpdateInput` has no field for them), so the user sets them **once in Linear's UI**:

- **Default the team to the Board view** — otherwise it opens as a list.
- **Enable "Show empty groups"** in the board's display settings — otherwise columns with no cards stay hidden, so a freshly provisioned board still looks half-empty until each column has an issue.

Surface this as a closing note; setup can't do it for them.

*Project* board ordering is a separate, settable concern: Manual ordering on a project's board (so a pinned epic shows on top) is set automatically on the epic path via `set-project-view-manual` — see [reference/epic-flow.md](reference/epic-flow.md). That's project-scoped, not a team toggle.

### 6. Pin the repo to a Linear project

Provisioning readies a *team's* board; a repo also needs to know *which project* its `/linear:*` issues belong to — that binding is `.linear_project` at the repo root. Setup offers to create it when missing, so a fresh repo reaches a working board in one command.

Check for `.linear_project` at the repo root.

- **Present** → the repo is already pinned; skip silently. Re-running setup never re-creates a project.
- **Missing** → ask whether to create a Linear project for this repo now. If the user declines, skip. If they accept, run [`/linear:update-vision`'s *Create new project* flow](update-vision.md#create-new-project) on the team from step 2 — it asks for a name, creates the project, seeds `VISION.md` into the project `content` (when the file exists), writes `.linear_project`, and adds it to `.gitignore`. Reuse that path rather than restating it.

  **One addition specific to setup:** because step 1 already resolved the workspace, write `.linear_project` with *both* fields, not just the project name —

  ```
  project = <project-name>
  api_key_env = LINEAR_<WORKSPACE>_API_KEY
  ```

  If project creation fails (e.g. no permission to create projects on the team), surface the error and stop — don't pin `.linear_project` to a project that wasn't created.

### 7. Summary

- **provisioned**: report created / archived / reordered, plus that a sample card was seeded. If `in_sync` was already `true` and nothing changed, say "Already in sync — no changes."

  | Team | Created | Archived | Reordered |
  |:-----|:--------|:---------|:----------|
  | ENG (Engineering) | — | In Progress | 8 states ordered |

- **advise**: state plainly that nothing was changed (the team has cards), then show the target order and what to fix:

  ```
  OPS (Operations) has issues — left untouched.
  Canonical order: Backburner, Backlog, Todo, Doing, In Review, Waiting, Done, Canceled, Duplicate
  Board order:     Backburner, Backlog, Todo, Doing, Done, Canceled, Duplicate, In Review, Waiting
  Fix: drag "In Review" and "Waiting" before "Done" in Linear's board settings.
  ```

- **project**: if a project was created, report its name and URL, and that `.linear_project` was pinned (and added to `.gitignore` when it wasn't already listed). If `.linear_project` was already present, say nothing — the repo was already pinned.

Re-running is always safe: an empty team converges to in-sync; a populated team is only ever reported on; an already-pinned repo skips project creation.

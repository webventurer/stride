# Provision Linear workflow states

Make a Linear team's board match the workflow states stride needs ([`linear_statuses.json`](linear_statuses.json)) — so `/linear:start` / `/linear:finish` transitions land instead of silently no-opping on a missing or misnamed column. It also provisions the type labels stride tags cards with ([`linear_labels.json`](linear_labels.json)), so a card's shape shows on the board. When the repo isn't yet pinned to a Linear project, setup also offers to create one and write `.stride.json` (step 7) — so a fresh repo reaches a working board in a single command.

<mark>**Card-aware, and that's the safety model.** An *empty* team (no issues) is set up authoritatively — create the canonical states, archive non-canonical ones, order them to match. A team that *already holds issues* is **never touched**; setup only reports what the board should be and asks the human to adjust it.</mark> A live board is the human's to change, not a script's.

Two Linear constraints worth knowing:

- **Reserved states** (`duplicate`, `triage` types) can't be created or repositioned via the API — Linear pins them. Setup leaves them where they are; everything else is ordered around them.
- **Board state is per-team**, not per-workspace — a workspace can hold several teams, so setup always targets one team deliberately (step 2).

## Steps

### 1. Pick the workspace

Discover the configured workspaces — see [Workspaces and teams → Find configured workspaces](reference/workspaces-and-teams.md#find-configured-workspaces). Provisioning targets **one**: if exactly one is set, use it; if several, ask which workspace to use.

### 2. Pick the team

Provisioning writes to **one** team's board. List the workspace's teams — see [Workspaces and teams → List a workspace's teams](reference/workspaces-and-teams.md#list-a-workspaces-teams). If exactly one team exists, use its key. If several, <mark>**ask which team to target — never assume the first.**</mark> Capture the chosen team **key** (e.g. `WB`) for the `--team` flag below.

### 3. Provision (card-aware)

Run *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py provision-states --team <TEAM-KEY>
```

The tool checks whether the team holds any issues and branches:

- **Empty team → `{"mode": "provisioned", "created", "deleted", "reordered", "in_sync"}`.** It created any missing canonical states, archived non-canonical ones, and ordered them to the JSON sequence. Safe — no in-progress work to orphan. (Reserved states like `Duplicate` stay where Linear pins them.)
- **Team with cards → `{"mode": "advise", "canonical_order", "board_order", "missing", "extra", "ordered"}`.** <mark>**Nothing was changed.**</mark> Show the user the canonical order vs the board's current order and any missing/extra columns, then ask them to adjust the board in Linear's UI — the API won't reorder a team that holds work.

### 4. Provision type labels

Run *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py provision-labels --team <TEAM-KEY>
```

Unlike states, creating a label is non-destructive — it adds a tag, never reorders or archives existing work — so this runs the same way whether or not the team holds cards: it creates any declared type label ([`linear_labels.json`](linear_labels.json) — Bug, Epic, Issue) the team is missing and leaves the rest untouched. There's no advise mode.

- **`{"created": [...], "in_sync": false}`** — created the listed labels.
- **`{"created": [], "in_sync": true}`** — every declared label already exists; nothing changed.

These are the labels stride applies at card creation (`/linear:plan-work`, `/linear:quick`, the epic flow) so a card's type is visible on the board.

### 5. Seed a sample card (empty teams only)

A freshly provisioned board has no issues, so Linear renders a blank screen. **If `mode` was `provisioned`**, create one sample card so the columns are visible:

```bash
LINEAR_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py issue create -t <TEAM-KEY> --state Backlog \
  --title "Sample card — so the board shows its columns" \
  --description "Placeholder so the board renders. Safe to delete."
```

Skip this when `mode` was `advise` — that team already has cards.

### 6. Tell the user the board-view toggles (UI only)

Applies to either path. These *team* board-view toggles aren't on the team API (`TeamUpdateInput` has no field for them), so the user sets them **once in Linear's UI**:

- **Default the team to the Board view** — otherwise it opens as a list.
- **Enable "Show empty groups"** in the board's display settings — otherwise columns with no cards stay hidden, so a freshly provisioned board still looks half-empty until each column has an issue.

Surface this as a closing note; setup can't do it for them.

*Project* board ordering is a separate, settable concern: Manual ordering on a project's board (so a pinned epic shows on top) is set automatically on the epic path via `set-project-view-manual` — see [reference/epic-flow.md](reference/epic-flow.md). That's project-scoped, not a team toggle.

### 7. Pin the repo to a Linear project

Provisioning readies a *team's* board; a repo also needs to know *which project* its `/linear:*` issues belong to — that binding is `.stride.json` at the repo root. Setup offers to create it when missing, so a fresh repo reaches a working board in one command.

First, migrate any legacy `.linear_project` pin (INI-style, from before stride moved to `.stride.json`). This is a no-op when there's no legacy file, so it's always safe to run before the check:

```bash
uv run .claude/tools/linear_cli.py migrate-legacy-config
```

A legacy file is rewritten as `.stride.json` and deleted, so a previously legacy-pinned repo now reads as **already pinned** in the check below — that's what stops setup from creating a duplicate project. If the migration wrote `.stride.json`, append it to `.gitignore` when it isn't already listed.

Then materialise the `focus` default into an existing config that predates the field. This writes `"focus": "outcome"` into a `.stride.json` that lacks it, and is a no-op when the file is missing or already has `focus` (an explicit `"technical"` is never clobbered):

```bash
uv run .claude/tools/linear_cli.py backfill-focus
```

Setup is the single place `focus` is materialised — the output-generating commands only ever *read* it (falling back to `outcome` when absent), so running them never rewrites the config as a side effect.

Then check for `.stride.json` at the repo root:

- **Present** → the repo is pinned (already, or just migrated), and `focus` is now materialised; skip silently. Re-running setup never re-creates a project.
- **Missing** → the repo is genuinely unpinned. Ask whether to create a Linear project for this repo now. If the user declines, skip. If they accept, follow [Create a Linear project](reference/create-project.md), using the chosen team from step 2 — it creates the project, seeds `VISION.md` when present, writes `.stride.json` (`project`, `api_key_env`, and `focus`), and updates `.gitignore`.

### 8. Summary

- **provisioned**: report created / archived / reordered, plus that a sample card was seeded. If `in_sync` was already `true` and nothing changed, say "Already in sync — no changes."

  | Team | Created | Archived | Reordered |
  |:-----|:--------|:---------|:----------|
  | ENG (Engineering) | — | In Progress | 8 states ordered |

- **labels**: report which type labels were created, or that they were already in sync.

  | Team | Labels created |
  |:-----|:---------------|
  | ENG (Engineering) | Bug, Epic, Issue |

- **advise**: state plainly that nothing was changed (the team has cards), then show the target order and what to fix:

  ```
  OPS (Operations) has issues — left untouched.
  Canonical order: Backburner, Backlog, Todo, Doing, In Review, Waiting, Done, Canceled, Duplicate
  Board order:     Backburner, Backlog, Todo, Doing, Done, Canceled, Duplicate, In Review, Waiting
  Fix: drag "In Review" and "Waiting" before "Done" in Linear's board settings.
  ```

- **project**: if a project was created, report its name and URL, and that `.stride.json` was pinned (and added to `.gitignore` when it wasn't already listed). If a legacy `.linear_project` was **migrated**, report the existing project it reused and that `.linear_project` was replaced by `.stride.json` — no new project created. If `.stride.json` was already present, say nothing — the repo was already pinned.

Re-running is always safe: an empty team converges to in-sync; a populated team is only ever reported on; an already-pinned (or legacy-pinned) repo skips project creation.

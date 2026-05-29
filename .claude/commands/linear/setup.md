# Provision Linear workflow states

Make a Linear team's board match the workflow states stride needs ([`linear_statuses.json`](linear_statuses.json)) — so `/linear:start` / `/linear:finish` transitions land instead of silently no-opping on a missing or misnamed column.

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

A workspace can hold several teams; provisioning writes to one team's board. List them:

```bash
LINCTL_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" linctl team list
```

If exactly one team exists, use its key. If several, <mark>**ask which team to target — never assume the first.**</mark> Capture the chosen team **key** (e.g. `WB`) for the `--team` flag below.

### 3. Provision (card-aware)

Run *(auth per [reference/workflow.md](reference/workflow.md))*:

```bash
LINCTL_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" uv run .claude/tools/linear_cli.py provision-states --team <TEAM-KEY>
```

The tool checks whether the team holds any issues and branches:

- **Empty team → `{"mode": "provisioned", "created", "deleted", "reordered", "in_sync"}`.** It created any missing canonical states, archived non-canonical ones, and ordered them to the JSON sequence. Safe — no in-progress work to orphan. (Reserved states like `Duplicate` stay where Linear pins them.)
- **Team with cards → `{"mode": "advise", "canonical_order", "board_order", "missing", "extra", "ordered"}`.** <mark>**Nothing was changed.**</mark> Show the user the canonical order vs the board's current order and any missing/extra columns, then ask them to adjust the board in Linear's UI — the API won't reorder a team that holds work.

### 4. Seed a sample card (empty teams only)

A freshly provisioned board has no issues, so Linear renders a blank screen. **If `mode` was `provisioned`**, create one sample card so the columns are visible:

```bash
LINCTL_API_KEY="$LINEAR_<WORKSPACE>_API_KEY" linctl issue create -t <TEAM-KEY> --state Backlog \
  --title "Sample card — so the board shows its columns" \
  --description "Placeholder so the board renders. Safe to delete."
```

Skip this when `mode` was `advise` — that team already has cards.

### 5. Tell the user the board-view toggles (UI only)

Applies to either path. Linear's board-view preferences aren't on the team API — `TeamUpdateInput` has no field for them, and the `viewPreferences` mutations are per-user, per-view — so the user sets these **once in Linear's UI**:

- **Default the team to the Board view** — otherwise it opens as a list.
- **Enable "Show empty groups"** in the board's display settings — otherwise columns with no cards stay hidden, so a freshly provisioned board still looks half-empty until each column has an issue.

Surface this as a closing note; setup can't do it for them.

### 6. Summary

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

Re-running is always safe: an empty team converges to in-sync; a populated team is only ever reported on.

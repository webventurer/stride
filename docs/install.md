# Install

```bash
npx github:webventurer/stride
```

This copies skills, commands, hooks, and tools into your project's `.claude/` directory and merges hook config into your `.claude/settings.local.json` (gitignored, machine-local).

That command installs stride itself, not the CLIs the workflow relies on — see **What you need to install first** below, before your first `/linear:*` command.

## What you need to install first

stride needs [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plus four CLIs on your PATH — `gh`, `uv`, `linctl`, `jq` (used across the `/linear:*` skills, the commit hook, and the Python tools). On macOS:

```bash
npm install -g @anthropic-ai/claude-code
brew tap dorkitude/linctl
brew install gh uv linctl jq
```

### Linux

`gh`, `uv`, and `jq` install from your package manager; `linctl` uses the same brew tap as above, or `nix profile install github:dorkitude/linctl`.

### Windows

**WSL is the supported Windows path.** stride's commit hooks need a bash/zsh shell — the [Vision](https://github.com/webventurer/stride/blob/main/VISION.md) states plainly that *"Bash/zsh required for hooks (Windows requires WSL)."* Install [WSL](https://learn.microsoft.com/windows/wsl/install), then follow the macOS steps above inside it (`brew tap dorkitude/linctl && brew install gh uv linctl jq`).

`gh`, `uv`, and `jq` do have native Windows installers (winget / scoop / MSI) if you only need those — but `linctl` has none, so a native install still leaves you building it from source with Go (`go install`), and the hooks won't run without WSL anyway. Pick WSL up front.

### Connect Linear

stride's `/linear:*` skills reach Linear through **linctl**, authenticated by a per-workspace API key in `~/.env` — no `.mcp.json`, no OAuth. Add one key per workspace:

```
LINEAR_<TEAM>_API_KEY=lin_api_...
```

Get a key at [linear.app/settings/api](https://linear.app/settings/api) (one per workspace). Every `/linear:*` call is implicitly prefixed `LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl …` — see [the workflow reference](https://github.com/webventurer/stride/blob/main/.claude/commands/linear/reference/workflow.md). Verify the connection with `/linear:check`.

### Provision your Linear board

stride drives work through Linear's workflow columns, so a team's board needs the exact states stride expects — `Backburner`, `Backlog`, `Todo`, `Doing`, `In Review`, `Waiting`, `Done`, `Canceled`, `Duplicate`. `/linear:setup` makes the board match, so `/linear:start` and `/linear:finish` transitions land instead of silently no-opping on a missing or misnamed column:

```
/linear:setup
```

It's **card-aware**. A team with **no issues** is set up automatically — it creates the missing columns, archives non-canonical ones, orders them to match, and seeds a sample card so the board renders. A team that **already holds issues** is never modified; it only reports the target order for you to fix in Linear's UI — a live board is yours to change, not a script's. Run it once per team before your first `/linear:start`.

Two board-view preferences can't be set through the API, so toggle them once in Linear's UI: default the team to **Board** view, and enable **"Show empty groups"** so every column shows even before it holds a card.

### Set the Linear board to Manual sort

stride sequences your work by each issue's position on the board (`/linear:plan-work` places new issues; you arrange the backlog into the order you'll tackle it). **Set your Linear board — or whichever view you use for stride work — to "Manual" sort.** Under a Priority, Created, or Updated sort, Linear ignores those positions and stride's execution order looks scrambled. Board sort is a per-view UI setting, so stride can't set it for you.

### Authenticate GitHub and OpenRouter

- **GitHub** — run `gh auth login`.
- **OpenRouter** — only needed for `/linear:plan-work`'s cross-model feedback (it sends drafts to ChatGPT via [OpenRouter](https://openrouter.ai/)). Add `OPEN_ROUTER_API_KEY=sk-or-...` to `~/.env` — [get a key](https://openrouter.ai/keys).

## Next: anchor your project with `/vision`

Once stride is installed, run `/vision` before anything else:

```
/vision
```

It walks you through seven questions and writes `VISION.md` at the repo root — what the project delivers, why it exists, what success looks like. Vision is the project's guiding light. Functionally that makes it stride's upstream anchor — every `/linear:*` command reads it before deciding anything: `/linear:plan-work` won't draft an issue without it, and `/linear:start` / `/linear:fix` use it to ground implementation decisions.

Skipping this step means your first `/linear:plan-work` call stops with a hard-gate error. See [the `/vision` skill](/skills/vision) for the full walkthrough.

## Uninstall

```bash
npx -p github:webventurer/stride stride-uninstall
```

This removes all copied directories, the example file, and strips the stride hook from `.claude/settings.local.json`.

## What gets installed

```text
.claude/
├── skills/commit/       # skill + workflow + reference docs
├── skills/craft/        # CRAFT prompt skill
├── commands/linear/     # 9 commands + reference docs
├── hooks/               # commit wrapper + bare-commit blocker
├── tools/               # cross-model feedback script
└── stride/docs/         # supporting patterns and concepts
```

The installer only writes under `.claude/` — it never touches other directories in your repo. Hook config goes into `.claude/settings.local.json` (gitignored) — your committed `settings.json` is never modified. Claude Code concatenates hooks from both files, so repo hooks and stride hooks run together.

The installer also offers to add stride's paths to your root `.gitignore` in a marker-delimited section (`# >>> stride ... # <<< stride`). Accept the prompt to keep `git status` clean; decline to commit stride's content into your repo instead. Uninstall removes the section cleanly.

## App starters

Opinionated project scaffolds for starting a new app from zero. They're not part of stride — pick one for the stack you want, then run `npx github:webventurer/stride` inside it to add the engineering workflow on top.

### [app-starter](https://github.com/webventurer/app-starter)

A modern full-stack web app starter — React + TypeScript + Vite on the frontend, Hono + Neon + Clerk + Drizzle on the backend. Every layer is independently replaceable — swap one piece without rewiring the rest. Includes shadcn/ui for components, Biome for formatting, and reference docs that explain every technology choice.

```bash
gh repo clone webventurer/app-starter
./app-starter/scripts/create.sh my-app
```

### [python-template](https://github.com/webventurer/python-template)

A Python project starter with development tooling already wired up — direnv for environment management, pip-tools for dependencies, Pyright for type checking, pre-commit hooks, and pytest for tests. A Makefile, setup script, and GitHub Actions come in the box so you start from a working project on day one.

```bash
gh repo clone webventurer/python-template
cd python-template
direnv allow
./scripts/setup.sh
```

## Migration skills

Two skills for migrating issues between workspaces live on the [`migrate` branch](/reference/migration-skills). They require Python and are kept separate to keep the main install lightweight.

```bash
git checkout migrate
python -m venv .venv && source .venv/bin/activate
make install
```

This gives you `/linear-to-linear` (copy between Linear workspaces) and `/trello-to-linear` (migrate from Trello). See the [migration skills reference](/reference/migration-skills) for full details.

Switch back when done: `git checkout main`

## Known limitations

### No versioning

There's no version number, changelog, or upgrade path. When you install, you get the current state of the repo. If you install again later, files are overwritten with whatever's current — no diff, no migration notes.

**What this means:** you won't know what changed between installs. If the repo goes private or gets renamed, your project still works (the files are local), but updates stop with no warning.

**Workaround:** pin to a specific commit if stability matters:

```bash
npx github:webventurer/stride#<commit-sha>
```

### Hook scripts require bash

The commit safety hook (`block_bare_git_commit.sh`) is a shell script. If it fails — wrong shell, missing permissions, Windows without WSL — the enforcement disappears silently. The agent will happily use bare `git commit` without the four-pass methodology.

**Check it's working:** if you can run `.claude/hooks/do_commit.sh --help` without errors, you're fine. If not, check that the scripts are executable (`chmod +x .claude/hooks/*.sh`).

### Settings merge strategy

Hook config is written to `.claude/settings.local.json` (gitignored), not `settings.json`. This keeps your committed settings untouched — see [decision 001](decisions/001-hooks-in-settings-local.md) for rationale.

The merge uses a deep strategy on `settings.local.json`:

- **Objects** are merged recursively — your keys are preserved, stride's keys are added alongside
- **Arrays** (like hook lists) are appended with deduplication — if a hook already exists, it's skipped
- **Scalar values** — stride's value wins if both sides set the same key

Claude Code concatenates hook arrays from both `settings.json` and `settings.local.json`, so your repo's committed hooks and stride's installed hooks all run together.

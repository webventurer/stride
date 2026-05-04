# Install

```bash
npx github:webventurer/stride
```

This copies skills, commands, hooks, and tools into your project's `.claude/` directory and merges hook config into your `.claude/settings.local.json` (gitignored, machine-local).

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

This removes all copied directories, the example file, and strips the stride hook from `.claude/settings.local.json`. Your `.mcp.json` is left untouched — remove Linear servers manually if needed.

## Requirements

### Claude Code

Install the [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI:

```bash
npm install -g @anthropic-ai/claude-code
```

### Linear MCP server

The `/linear` commands need Linear's [official MCP server](https://linear.app/docs/mcp). There are two ways to connect — **OAuth** (simplest) or **API key** (needed for multiple orgs).

Create `.mcp.json` in your repo root using one of the snippets below:

#### OAuth (single org)

Uses browser-based login — no keys to manage:

```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/mcp"]
    }
  }
}
```

On first use, a browser window opens to authenticate. The token is cached locally.

#### API key (multiple orgs)

When you need separate connections to different Linear orgs — add one entry per org with its own API key:

```json
{
  "mcpServers": {
    "linear-org1": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.linear.app/mcp",
        "--header",
        "Authorization:Bearer ${LINEAR_ORG1_API_KEY}"
      ],
      "env": {
        "LINEAR_ORG1_API_KEY": "${LINEAR_ORG1_API_KEY}"
      }
    },
    "linear-org2": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.linear.app/mcp",
        "--header",
        "Authorization:Bearer ${LINEAR_ORG2_API_KEY}"
      ],
      "env": {
        "LINEAR_ORG2_API_KEY": "${LINEAR_ORG2_API_KEY}"
      }
    }
  }
}
```

Each entry points to the same `mcp.linear.app/mcp` endpoint but authenticates with a different key. Add the keys to your `~/.env`:

```
LINEAR_ORG1_API_KEY=lin_api_...
LINEAR_ORG2_API_KEY=lin_api_...
```

Get your API keys at [linear.app/settings/api](https://linear.app/settings/api) — one per org. Replace `org1`/`org2` with meaningful names (e.g. `LINEAR_ACME_API_KEY`).

#### Verify the connection

```
/linear:check
```

This confirms that each configured Linear server responds and shows which workspace it's connected to.

### GitHub CLI

Install the [GitHub CLI](https://cli.github.com/) (`gh`) for PR operations:

```bash
brew install gh                # macOS
# or: https://cli.github.com/ for other platforms
```

Then authenticate:

```bash
gh auth login
```

## Python tools

The cross-model feedback loop in `/linear:plan-work` uses a Python script to send drafts to ChatGPT via [OpenRouter](https://openrouter.ai/). Dependencies are managed inline with [uv](https://docs.astral.sh/uv/) — no venv or `pip install` needed.

```bash
brew install uv                # macOS
# or: curl -LsSf https://astral.sh/uv/install.sh | sh
```

Add your OpenRouter API key to `~/.env`:

```
OPEN_ROUTER_API_KEY=sk-or-...
```

Get your key at [openrouter.ai/keys](https://openrouter.ai/keys).

## What gets installed

```bash
.claude/
├── skills/commit/       # skill + workflow + reference docs
├── skills/craft/        # CRAFT prompt skill
├── commands/linear/     # 5 commands + reference docs
├── hooks/               # commit wrapper + bare-commit blocker
├── tools/               # cross-model feedback script
└── stride/docs/         # supporting patterns and concepts
```

The installer only writes under `.claude/` — it never touches other directories in your repo. Hook config goes into `.claude/settings.local.json` (gitignored) — your committed `settings.json` is never modified. Claude Code concatenates hooks from both files, so repo hooks and stride hooks run together.

The installer also offers to add stride's paths to your root `.gitignore` in a marker-delimited section (`# >>> stride ... # <<< stride`). Accept the prompt to keep `git status` clean; decline to commit stride's content into your repo instead. Uninstall removes the section cleanly.

## App starters

stride gives you the engineering workflow. App starters give you the project scaffold. Each starter is an opinionated template that gets you from zero to a working app in one command — with stride's skills already wired in.

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

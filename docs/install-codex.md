# Install for Codex

Codex support builds on top of Stride's shared `.claude/` installation. Stride first installs its skills, commands and hooks there, then creates the extra `.codex/` files that let Codex use them.

This means installing Stride for Codex also leaves the project ready for Claude Code. It does not install either CLI itself — install Claude Code or Codex separately before using it.

Follow the [Install](/install) page for the shared prerequisites, Linear connection and Vision step. This page covers only what Codex adds.

## Install with the Codex target

```bash
npx github:webventurer/stride --agent codex
```

Without `--agent`, Stride sets up Claude Code. With `--agent codex`, it keeps those shared, Claude-ready files and also writes the `.codex/` files. They are built from `.claude/`, ignored by git and replaced on each install — never edit them by hand.

## Trust the hooks, or they will not run

<mark>**Codex quarantines every hook until you approve it.**</mark> Open Codex in the project and run `/hooks` to review and trust stride's two hooks.

Codex records that approval against each hook's exact content. A stride update changes the content, which changes the hash, which quarantines the hooks again — so re-approve after every install. Skip this and the bare-commit block silently stops firing, with nothing in the output to say so.

## Check the board before you start

The Linear steps on the [Install](/install#connect-linear) page still apply. Codex reaches stride's commands as skills rather than slash commands, so they carry a `$` and a hyphen — [Running the commands](#running-the-commands) covers the form in full:

```text
$linear-check
$linear-setup
```

`$linear-check` confirms each API key authenticates. `$linear-setup` provisions the board with the exact states stride drives work through, then run `$linear-check` once more to confirm the columns landed. Do this first: without the right columns, the state transitions silently no-op and the card never moves.

## Running the commands

Codex has no namespaced slash commands, so `/linear:start` is reachable as a skill instead:

```text
$linear-start WB-123
```

Each command becomes a skill named `linear-<command>`, and the four shipped skills — `commit`, `craft`, `vision`, `clear-speak` — keep their names. Type `$` in Codex to see them, or `/skills` to browse.

The generated skill points at the command file under `.claude/commands/linear/` rather than copying it, so there is one place a command is authored and the two tools cannot drift.

## Skip the approval prompts

Codex asks before it runs commands and edits files. To turn those prompts off, edit `~/.codex/config.toml`:

```toml
default_permissions = ":danger-full-access"
approval_policy = "never"
```

<mark>**This is Codex's equivalent of `--dangerously-skip-permissions`, and it is machine-wide.**</mark> `~/.codex/config.toml` is your user config, not the project's, so the setting applies to every repository you open in Codex — including ones you did not install stride into. The agent will run commands and write files without asking, so only set it on a machine where you are happy with that.

Stride never writes this file. Nothing in the install footprint lives outside your repo, and a setting that widens what an agent may do is yours to make deliberately.

## What gets installed

```text
.codex/
├── skills/              # stride's skills + one skill per Linear command
└── hooks.json           # registers the same hook scripts with Codex
```

Both hooks are the same scripts under `.claude/hooks/` — `hooks.json` only wires them up.

## Known limitations

### An administrator can switch the guardrails off

Codex honours `allow_managed_hooks_only = true` in a managed `requirements.toml`. When that is set, Codex ignores user, project and session hook config entirely — including stride's `.codex/hooks.json`.

**What this means:** in a managed environment the bare-commit block may never run, with no error and nothing in the output to say so. If commits are landing without the multi-pass workflow, check that setting before assuming the hook is broken.

### The Linear MCP block is Claude-only

Stride blocks the `mcp__claude_ai_Linear__*` tools so Linear writes go through `linear_cli.py`, which is the path every command is written against. That block is a Claude Code permission, and Codex has no matching primitive.

**What this means:** under Codex nothing stops an agent reaching Linear through an MCP server instead of the CLI. The commands still call `linear_cli.py`, so the common path is unaffected — but the guardrail is documentation rather than enforcement there.

## Uninstall

The [uninstall command](/install#uninstall) removes the Codex footprint along with everything else — `.codex/skills/`, `.codex/hooks.json`, and the gitignore entries that cover them.

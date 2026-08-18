# Install for Codex

Stride runs under Codex CLI as well as Claude Code — the same commands, the same guardrails, generated from the same source.

Follow the [Install](/install) page first. Everything there applies: the prerequisites, the Linear connection, the Vision step. `.claude/` is installed whichever CLI you use, because it holds the skills, commands and docs every tool reads, and the Codex skills point back into it.

This page is only what differs.

## Install with the Codex target

```bash
npx github:webventurer/stride --agent codex
```

`--agent` chooses which CLIs to set up: `claude` (the default), `codex`, both as `claude,codex`, or `all`.

Selecting `codex` additionally writes `.codex/skills/` — stride's skills, plus one skill per Linear command — and `.codex/hooks.json`. Both are generated from `.claude/`, so they are gitignored as build artifacts and rewritten on each install.

## Trust the hooks, or they will not run

<mark>**Codex quarantines every hook until you approve it.**</mark> Open Codex in the project and run `/hooks` to review and trust stride's two hooks.

Codex records that approval against each hook's exact content. A stride update changes the content, which changes the hash, which quarantines the hooks again — so re-approve after every install. Skip this and the bare-commit block silently stops firing, with nothing in the output to say so.

## Running the commands

Codex has no namespaced slash commands, so `/linear:start` is reachable as a skill instead:

```text
$linear-start WB-123
```

Each command becomes a skill named `linear-<command>`, and the four shipped skills — `commit`, `craft`, `vision`, `clear-speak` — keep their names. Type `$` in Codex to see them, or `/skills` to browse.

The generated skill points at the command file under `.claude/commands/linear/` rather than copying it, so there is one place a command is authored and the two tools cannot drift.

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

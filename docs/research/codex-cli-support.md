# What stride needs to run under Codex CLI

> **The ground moved twice under this question.** When the card was filed, Codex CLI meant `AGENTS.md` plus deprecated home-dir prompts and no hooks. By 0.139.0 (June 2026) it had Claude-style lifecycle hooks and first-class skills on the same open standard. By 0.147.0 (August 2026) it ships a **built-in Claude Code migrator** that converts commands into skills in-product. The gap that looked hard is now specified by OpenAI's own code — but the migrator imports none of stride's commands as they stand.

Spike findings for WB-531. Verified against Codex CLI **0.147.0** (released 2026-08-07, confirmed installed locally as `codex-cli 0.147.0`) and stride `main` as of 2026-08-16.

## Verification basis

Claims below were checked against three sources, in descending order of authority:

1. **`openai/codex` Rust source at HEAD** — `codex-rs/ext/skills/src/host_roots.rs` (skill scan paths), `codex-rs/core-plugins/src/command_migration.rs` (command→skill rules), `codex-rs/external-agent-migration/` (Claude import), `codex-rs/docs/config.md`.
2. **Current docs site** — `learn.chatgpt.com/docs`. The old `developers.openai.com/codex` paths now 308-redirect; every link in the first draft of this doc was stale.
3. **Local install** — `codex-cli 0.147.0`, with a populated `~/.codex/` and `~/.agents/skills/`.

Nothing here has been smoke-tested by running stride's hooks under Codex. That test is named in the scoping notes.

## Quick reference

| Stride piece | Codex CLI home | Port difficulty |
|:-------------|:---------------|:----------------|
| Skills (`commit`, `craft`, `vision`, `clear-speak`) | `.codex/skills/` or `.agents/skills/` — same SKILL.md standard | **Trivial** — cross-compatible as-is |
| Commands (`/linear:*`) | No equivalent — becomes a skill per command (`$linear-start`) | **Moderate** — rules now specified by Codex's own migrator |
| PreToolUse hook (`block_bare_git_commit.sh`) | `.codex/hooks.json` | **None** — payload is field-identical, runs unmodified |
| UserPromptSubmit hook (`inject_design_principles.sh`) | `.codex/hooks.json` | **Easy** — wrap stdout in JSON, resolve path from `cwd` |
| `permissions.deny` (`mcp__claude_ai_Linear__*`) | No equivalent | **Unported** — a guardrail that does not translate |
| `do_commit.sh` + width check | Nothing needed — plain bash + python, tool-agnostic | **None** — already portable |
| MCP (`.mcp.json` → context7) | `[mcp_servers]` in `.codex/config.toml` — no `.mcp.json` compat | **Easy** — one-time TOML translation |
| Python tools (`linear_cli.py`, PEP 723 via `uv run`) | Unchanged — CLI-agnostic | **None** |
| `CLAUDE.md` ambient rules | `AGENTS.md` (repo root down to cwd, 32 KiB combined cap) | **Easy** — plus `@AGENTS.md` shim keeps Claude in sync |

## What stride actually ships (the surface to port)

From `bin/install.mjs` (`DIRS`/`HOOKS`/`STRIDE_SETTINGS`):

- **Four skills** — `commit`, `craft`, `vision`, `clear-speak` — SKILL.md with `name`/`description` frontmatter plus supporting files (`WORKFLOW.md`, references).
- **One command namespace** — `.claude/commands/linear/*.md`, invoked by path-derived names (`linear/start.md` → `/linear:start`) with `$ARGUMENTS` substitution. 29 markdown files including the `reference/` and `recovery/` subdirectories.
- **Two wired hooks** — `UserPromptSubmit` → `inject_design_principles.sh` (writes a doc to stdout for context injection); `PreToolUse` matcher `Bash` → `block_bare_git_commit.sh` (greps `.tool_input.command` for bare `git commit`, exit 2 blocks). Merged into `settings.local.json`, not `settings.json` (decision 001).
- **One permission rule** — `STRIDE_SETTINGS.permissions.deny: ["mcp__claude_ai_Linear__*"]`, which forces Linear writes through `linear_cli.py` rather than the MCP server.
- **Commit plumbing** — `do_commit.sh` forwarding to `git commit` after `check_commit_widths.py` validates `-m`/`-F` text. Pure bash + python3; nothing Claude-specific.
- **Tools** — `linear_cli.py`/`linear.py`/`openrouter_cli.py`, PEP 723 headers run via `uv`; auth from `LINEAR_<WORKSPACE>_API_KEY` in `~/.env` via `.linear_project`.
- **Docs** — `.claude/stride/docs/{patterns/git,concepts,principles}` referenced by skills and hooks.
- **Install guard** — `assertUnderClaudeDir` refuses any write outside `.claude/`; prereqs are `gh`, `uv`, `jq`.

Claude-specific assumptions: hook paths use `$CLAUDE_PROJECT_DIR`; command namespacing comes from Claude's directory convention; MCP config lives in `.mcp.json`; the permission-deny rule has no counterpart in any other CLI.

## What Codex CLI offers today (August 2026)

1. **Skills are first-class and cross-compatible** — the same SKILL.md format Claude Code uses, requiring `name` and `description` frontmatter. Explicit invocation is `$skill-name` or the `/skills` browser; implicit invocation matches on the description. Enabled skills also surface in the slash-command list.
2. **Hooks exist and are default-on** — 11 lifecycle events: `SessionStart`, `SessionEnd`, `SubagentStart`, `SubagentStop`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `Stop`. Configured in `~/.codex/hooks.json` or a trusted repo's `.codex/hooks.json`. Same JSON-on-stdin, exit-code-2-blocks contract as Claude Code.
3. **Project-level config shipped.** A trusted repo's `.codex/` dir carries `config.toml`, `hooks.json`, and experimental Starlark `rules/`. MCP servers go in `[mcp_servers]` TOML — Codex does not read `.mcp.json`.
4. **Codex ships a Claude Code migrator.** `/import` in the TUI, backed by `codex-rs/external-agent-migration`, pulls in skills, hooks, MCP servers, `CLAUDE.md` memory, subagents, plugins, marketplaces, and 30 days of session history. It converts Claude commands into skills automatically.
5. **`AGENTS.md` is the ambient-context file** — global `AGENTS.override.md`/`AGENTS.md` first, then project files concatenated root-down, stopping at `project_doc_max_bytes` (32 KiB default). Codex does not read `CLAUDE.md`; the bridge is a `CLAUDE.md` containing `@AGENTS.md`.
6. **Plugins** bundle skills, connectors, MCP servers, browser extensions, hooks, and scheduled-task templates into one installable unit with a marketplace.

## Skill scan paths — the precise picture

From `host_roots.rs`, in the order roots are assembled:

| Scope | Path | Status |
|:------|:-----|:-------|
| Repo | `<project>/.codex/skills` | Supported (Project config layer) |
| Repo | `<dir>/.agents/skills` — cwd, ancestors, and repo root | Supported |
| User | `~/.codex/skills` (`$CODEX_HOME/skills`) | **Deprecated** — "kept for backward compatibility" |
| User | `~/.agents/skills` | Canonical |
| Admin | System config folder `/skills` | Supported |
| Plugin | Plugin-provided roots | Supported |

Either repo-scope path works, and Codex's own repository uses `.codex/skills/`. **Stride should use `.codex/skills/`** — it already needs `.codex/hooks.json` and `.codex/config.toml`, so one directory holds the entire Codex footprint instead of two, and codefu already writes skills there.

At user scope the picture is different: `~/.codex/skills` still loads but is explicitly marked deprecated in source, with `~/.agents/skills` as the canonical replacement. Anything writing to the user-scope `~/.codex/skills` today is on a clock. This does not affect stride, which installs at repo scope.

## The gaps, ranked

### 1. Commands become skills — and the rules are now written down

`/linear:start WB-531` has no Codex equivalent, and this remains the only piece of the port with real design judgement in it. What changed is that OpenAI shipped a reference implementation. `core-plugins/src/command_migration.rs` defines exactly what a command-derived skill looks like:

- Skill name is `slugify("source-command-" + <path components joined by ->)`, capped at 64 characters. `.claude/commands/linear/start.md` becomes `source-command-linear-start`.
- The body is wrapped: `# {name}` / "Use this skill when the user asks to run the migrated source command `{source_name}`" / `## Command Template` / the original body.
- Frontmatter `description` is copied from the source command.

Stride's own renderer should follow these semantics and drop the `source-command-` prefix, yielding `$linear-start`. Two costs survive:

- **No `$ARGUMENTS` templating.** Skills receive the mention's surrounding text as free text. Stride's command bodies already treat the argument loosely ("extract the `[A-Z]+-\d+` pattern"), so this mostly survives, but every `WB-531`-style substitution site needs rereading as "the issue ID the user mentioned".
- **Naming flattens.** `/linear:start` → `$linear-start`. Muscle memory and docs diverge per tool. Skill descriptions become load-bearing for implicit invocation — they need writing for Codex's matcher, not just for humans.

### 2. `/import` imports zero of stride's commands

The built-in migrator is not a shipping path for stride, and the reasons are mechanical:

| Filter in `command_migration.rs` | Stride today |
|:---------------------------------|:-------------|
| `CommandDescriptionMode::RequireFrontmatter` — no frontmatter `description` means skipped | **0 of 29 command files have frontmatter at all** |
| `has_unsupported_command_template_features` rejects `$ARGUMENTS` | 4 files |
| ...rejects `` !` `` command substitution | 1 file |
| ...rejects any `@token` file mention | 6 files |
| ...rejects `{{...}}` and `$<digit>` placeholders | 0 files |
| `README.md` stems skipped | — |
| Recurses subdirectories | `reference/` and `recovery/` would become skills too |
| Duplicate slugs dropped silently | — |

Adding a frontmatter `description` to each `.claude/commands/linear/*.md` is a prerequisite for any Codex path, improves Claude's own skill matching, and can be done today independent of the renderer.

### 3. Hook parity is closer than the first draft claimed

**`block_bare_git_commit.sh` runs unmodified.** Codex's PreToolUse payload is `{session_id, transcript_path, cwd, hook_event_name, model, permission_mode, turn_id, tool_name, tool_use_id, tool_input}`, with `tool_input.command` as a string for Bash. The hook reads `.tool_input.command`, exits 2, writes the reason to stderr. Every field matches. Only the config location changes.

**`inject_design_principles.sh` needs two edits**, neither of which forks the file:

- Wrap stdout in `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"..."}}`.
- Resolve the doc path from the payload's `cwd` instead of `$CLAUDE_PROJECT_DIR`.

Claude Code accepts the same `hookSpecificOutput.additionalContext` shape for `UserPromptSubmit`, so **one hook file serves both tools**. No hook renderer is needed at all — only a `hooks.json` writer.

Three frictions remain:

- **Per-hash trust.** Every non-managed hook must be approved via `/hooks` before it runs, and re-approved when its content changes. Stride's "guardrails on by default" posture becomes "guardrails after the user approves them", and every stride update re-quarantines the hooks.
- **Admin kill switch.** `allow_managed_hooks_only = true` in `requirements.toml` makes Codex ignore all user, project, and session hook configs. An administrator can silently disable stride's guardrails with no Claude equivalent and no signal to the user.
- **`permissions.deny` has nowhere to go.** Stride's block on `mcp__claude_ai_Linear__*` keeps Linear writes on `linear_cli.py`. Codex has no matching permission primitive, so under Codex this rule is documentation, not enforcement.

### 4. Everything else is translation, not redesign

MCP is a one-time `.mcp.json` → `[mcp_servers]` TOML rendering; the docs' own example is literally `[mcp_servers.context7]`, stride's only server. `AGENTS.md` replaces or augments `CLAUDE.md` (and the `@AGENTS.md` shim keeps a single source), with the caveat that a global `~/.codex/AGENTS.md` may already exist and must be merged rather than overwritten — the same class of problem decision 001 solved for `settings.local.json`. The commit plumbing and Python tools run unchanged — they're shell and `uv`, not Claude features. Prereqs gain nothing new.

## Directory strategy — recommendation

**Generate per-tool output from the Claude-native source at install time. Do not symlink. Do not hand-maintain a second tree.**

| Option | Verdict | Why |
|:-------|:--------|:----|
| Cross-linked skills (symlinks) | **No** | Symlinks die in npm tarballs (resolved at pack time), on Windows (`core.symlinks=false` default), and Gemini CLI has a cluster of open symlink bugs. Codex follows them, but the distribution channel doesn't. |
| Copy to `~/.codex/` home dir | **No** | Not versioned, not team-shared, drifts per machine — and `~/.codex/skills` is now the deprecated user path. |
| Rely on Codex's `/import` | **No** | Imports zero stride commands as they stand, produces `source-command-*` names, and is a one-shot user action rather than an install. Useful as a specification, not as a mechanism. |
| Hand-maintained per-tool forks | **No** | The SuperClaude anti-pattern: parallel frameworks to keep in sync by hand. |
| **Install-time generation: `.claude/` stays canonical; `npx … --codex` writes `.codex/`** | **Yes** | The pattern every surviving multi-CLI framework converged on (ruler, GSD, dot-ai). Skills copy verbatim into `.codex/skills/` (same standard); commands render to one-skill-per-command; hooks are shared files registered in `.codex/hooks.json`; MCP renders to `.codex/config.toml`. Generated outputs are gitignored as build artifacts, exactly like stride's existing gitignore section management. |

Stride's installer guard (`assertUnderClaudeDir`) loosens to "under `.claude/` or `.codex/` only" — still a bounded, refusable footprint, and decision 002's namespace logic carries over unchanged.

## Plugins versus raw `.codex/` — settled

The first draft left this open. It closes against plugins:

- **Plugins do not bypass hook trust.** The docs say plainly: "Review and trust plugin hooks before you enable them." The friction that made plugins attractive is still there.
- **Plugins are account- or workspace-scoped, not repo-scoped.** Stride installs into a repository. A plugin cannot express "these guardrails apply to this project".

Ship raw `.codex/` files. Revisit only if plugin scoping changes.

## Minimum fresh-install path to a first successful command

1. `npx github:webventurer/stride --codex` (new flag) — generates `.codex/skills/` (4 skills + N command-skills), `.codex/hooks.json`, `.codex/config.toml` (context7 MCP), an `AGENTS.md` section, and a gitignore section.
2. User trusts the project in Codex (`.codex/` layers are skipped untrusted).
3. User approves the two hooks via `/hooks` (per-hash trust).
4. `LINEAR_<WORKSPACE>_API_KEY` in `~/.env`, `gh`/`uv`/`jq` present — unchanged from the Claude path.
5. `$linear-start WB-123` in Codex → the skill drives the same `linear_cli.py` flow.

Steps 2–3 are Codex-imposed friction with no Claude equivalent; the install doc must name them or the guardrails silently don't run.

## Does this warrant a Vision update?

Yes, when the implementation ticket is scoped — but not the wording the constraint anticipated. The Vision says: *"Currently Claude Code is the only supported AI agent — AgentSDK integration would unlock others."* The spike shows the unlock is **not** AgentSDK: it's the ecosystem converging on open standards stride can target directly — Agent Skills for skills, `AGENTS.md` for ambient context, Claude-shaped lifecycle hooks. A truthful evolved constraint would read along the lines of: *"Claude Code is the primary agent; other CLIs are supported where they implement the open standards stride targets (Agent Skills, AGENTS.md, lifecycle hooks) — via install-time generation from the Claude-native source."* Run `/vision` to evolve it alongside the implementation ticket, per [vision-evolves-with-the-work](../patterns/vision-evolves-with-the-work.md).

## Scoping notes for the implementation ticket

- **Smoke-test before building.** Codex 0.147.0 is installed locally. Hand-write a `.codex/hooks.json` against the unmodified `block_bare_git_commit.sh`, trust it, and try a bare `git commit`; then render one skill and one command-skill by hand. Everything above rests on reading docs and source, not on a run.
- **Add frontmatter descriptions to all 29 command files.** A prerequisite for any Codex path, and it sharpens Claude's own matching. Separable and shippable now.
- The build is otherwise installer work: a `--codex` target in `bin/install.mjs` plus renderers (SKILL.md passthrough, command→skill wrapper, `hooks.json` writer, TOML writer). No runtime code changes.
- Command-skill rendering is the only piece with design judgement in it — how much of each `/linear:*` body survives verbatim versus needs Codex-flavoured framing (argument handling, no `/commit` skill chaining).
- `AGENTS.md` generation must merge into any existing file, global or project, rather than overwrite.
- Decide what to do about `permissions.deny` under Codex — document the gap, or find another mechanism.
- Codex moves fast: 0.139.0 to 0.147.0 in two months, with the docs site relocating. Pin the verified version in whatever the ticket asserts, and re-verify before starting.
- Out of scope here, per the card: Gemini CLI (separate ticket — note its symlink bugs and TOML command format make it a genuinely different renderer), AgentRouter.

---

*Sources: Codex CLI docs at [learn.chatgpt.com/docs](https://learn.chatgpt.com/docs) ([build skills](https://learn.chatgpt.com/docs/build-skills), [hooks](https://learn.chatgpt.com/docs/hooks), [plugins](https://learn.chatgpt.com/docs/plugins), [MCP](https://learn.chatgpt.com/codex/extend/mcp), [AGENTS.md](https://learn.chatgpt.com/codex/guides/agents-md), [slash commands](https://learn.chatgpt.com/codex/reference/slash-commands)); [agents.md](https://agents.md/); [agentskills.io](https://agentskills.io); `openai/codex` source at HEAD (`ext/skills/src/host_roots.rs`, `core-plugins/src/command_migration.rs`, `external-agent-migration/`, `docs/config.md`); prior art ([ruler](https://github.com/intellectronica/ruler), [GSD](https://github.com/open-gsd/gsd-core), [dot-ai](https://github.com/luisrudge/dot-ai), [litestar-skills](https://github.com/litestar-org/litestar-skills)); and stride's `bin/install.mjs`, `bin/uninstall.mjs`, `bin/prereqs.mjs`, `docs/decisions/001`, `docs/decisions/002`. Researched 2026-06-11 against 0.139.0; re-verified 2026-08-16 against 0.147.0.*

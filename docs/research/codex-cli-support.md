# What stride needs to run under Codex CLI

> **The ground moved under this question.** When the card was filed, Codex CLI meant `AGENTS.md` plus deprecated home-dir prompts and no hooks. As of Codex CLI 0.139.0 (June 2026), Codex has Claude-style lifecycle hooks, first-class skills on the same open standard Claude Code uses, and a trusted project-level `.codex/` directory. Most of stride ports; the hard gap is namespaced slash commands.

Spike findings for WB-531. Verified against Codex CLI 0.139.0 (released 2026-06-09) and stride `main` as of 2026-06-11.

## Quick reference

| Stride piece | Codex CLI home | Port difficulty |
|:-------------|:---------------|:----------------|
| Skills (`commit`, `craft`, `vision`) | `.agents/skills/` — same SKILL.md standard ([agentskills.io](https://agentskills.io)) | **Trivial** — cross-compatible as-is |
| Commands (`/linear:*`) | No equivalent — becomes a skill per command (`$linear-start`) | **Hard** — namespacing and `$ARGUMENTS` lost |
| PreToolUse hook (`block_bare_git_commit.sh`) | `.codex/hooks.json`, PreToolUse `permissionDecision: "deny"` | **Easy** — same JSON-on-stdin, exit-2 contract |
| UserPromptSubmit hook (`inject_design_principles.sh`) | `.codex/hooks.json`, UserPromptSubmit `additionalContext` | **Easy** — injection supported at this event |
| `do_commit.sh` + width check | Nothing needed — plain bash + python, tool-agnostic | **None** — already portable |
| MCP (`.mcp.json` → context7) | `[mcp_servers]` in `.codex/config.toml` — no `.mcp.json` compat | **Easy** — one-time TOML translation |
| Python tools (`linear_cli.py`, PEP 723 via `uv run`) | Unchanged — CLI-agnostic | **None** |
| `CLAUDE.md` ambient rules | `AGENTS.md` (repo root, 32 KiB combined cap) | **Easy** — plus `@AGENTS.md` shim keeps Claude in sync |

## What stride actually ships (the surface to port)

From `bin/install.mjs` (`DIRS`/`FILES`/`HOOK_CONFIG`, `bin/install.mjs:29-111`):

- **Three skills** — `commit`, `craft`, `vision` — SKILL.md with `name`/`description` frontmatter plus supporting files (`WORKFLOW.md`, references).
- **One command namespace** — `.claude/commands/linear/*.md`, invoked by path-derived names (`linear/start.md` → `/linear:start`) with `$ARGUMENTS` substitution.
- **Two wired hooks** — `UserPromptSubmit` → `inject_design_principles.sh` (writes a doc to stdout for context injection); `PreToolUse` matcher `Bash` → `block_bare_git_commit.sh` (greps the command for bare `git commit`, exit 2 blocks). Merged into `settings.local.json`, not `settings.json` (decision 001).
- **Commit plumbing** — `do_commit.sh` forwarding to `git commit` after `check_commit_widths.py` validates `-m`/`-F` text. Pure bash + python3; nothing Claude-specific.
- **Tools** — `linear_cli.py`/`linear.py`/`openrouter_cli.py`, PEP 723 headers run via `uv`; auth from `LINEAR_<WORKSPACE>_API_KEY` in `~/.env` via `.linear_project`.
- **Docs** — `.claude/stride/docs/{patterns/git,concepts,principles}` referenced by skills and hooks.
- **Install guard** — `assertUnderClaudeDir` refuses any write outside `.claude/` (`bin/install.mjs:113-120`); prereqs are `gh`, `uv`, `jq`.

Claude-specific assumptions: hook paths use `$CLAUDE_PROJECT_DIR`; command namespacing comes from Claude's directory convention; MCP config lives in `.mcp.json`.

## What Codex CLI offers today (June 2026)

Facts verified against [developers.openai.com/codex](https://developers.openai.com/codex/) docs and the `openai/codex` repo at 0.139.0:

1. **Skills are first-class and cross-compatible.** Codex skills build on the open Agent Skills standard — the same SKILL.md format Claude Code uses. Repo scope is `.agents/skills/` (scanned cwd up to repo root), user scope `~/.agents/skills`. Invocation is implicit (description match) or explicit `$skill-name`. ([docs](https://developers.openai.com/codex/skills), loader paths verified in `codex-rs/core-skills/src/loader.rs`)
2. **Hooks exist and are default-on** — 10 lifecycle events including PreToolUse (deny + command rewrite) and UserPromptSubmit (block + `additionalContext` injection). Configured in `~/.codex/hooks.json` or a trusted repo's `.codex/hooks.json`. Same JSON-on-stdin, exit-code-2-blocks contract as Claude Code. ([docs](https://developers.openai.com/codex/hooks))
3. **Project-level config shipped.** A trusted repo's `.codex/` dir carries `config.toml`, `hooks.json`, and experimental Starlark `rules/`. MCP servers go in `[mcp_servers]` TOML — Codex does not read `.mcp.json`. ([config](https://developers.openai.com/codex/config-reference), [MCP](https://developers.openai.com/codex/mcp))
4. **Custom prompts are deprecated** and were never repo-local: `~/.codex/prompts/*.md` only, `/prompts:` prefix only, no subdirectory scanning. Repo-local prompts were [closed as not-planned](https://github.com/openai/codex/issues/9848). Skills are the official replacement.
5. **`AGENTS.md` is the ambient-context file** — `~/.codex/AGENTS.md` plus repo root down to cwd, concatenated under a 32 KiB default cap. Stewarded by the Linux Foundation's Agentic AI Foundation; read by ~24 tools. Claude Code is the notable holdout (bridge: a `CLAUDE.md` containing `@AGENTS.md`). ([agents.md](https://agents.md/))
6. **Plugins** bundle skills + MCP + hooks into one installable unit with a marketplace — the closest thing to "stride as one artifact". ([docs](https://developers.openai.com/codex/plugins))

## The gaps, ranked

### 1. Namespaced slash commands don't exist (the hard gap)

`/linear:start WB-531` has no Codex equivalent. Built-in slash commands are fixed; custom prompts get only the `/prompts:` prefix and are deprecated, home-dir-only. The viable mapping is **one skill per command**: `linear-start/SKILL.md` invoked as `$linear-start WB-531` (or implicitly). Costs:

- No `$ARGUMENTS` templating — skills receive the mention's surrounding text as free text. Stride's command bodies already treat the argument loosely ("extract the `[A-Z]+-\d+` pattern"), so this mostly survives, but every `WB-531`-style substitution site needs rereading as "the issue ID the user mentioned".
- Naming flattens: `/linear:start` → `$linear-start`. Muscle memory and docs diverge per tool.
- Skill descriptions become load-bearing for implicit invocation — they need writing for Codex's matcher, not just for humans.

### 2. Hook parity is close but gated by trust

Both shipped hooks translate directly — `block_bare_git_commit.sh` reads the same JSON shape and its exit-2 contract matches; `inject_design_principles.sh`'s stdout maps to UserPromptSubmit `additionalContext`, which Codex supports *at that event* (PreToolUse injection is rejected — [#19385](https://github.com/openai/codex/issues/19385) — but stride doesn't need it). Two real frictions:

- **Per-hash trust:** every non-managed hook must be approved via `/hooks` before it runs, and re-approved when its content changes. Stride's "guardrails on by default" posture becomes "guardrails after the user approves them", and every stride update re-quarantines the hooks.
- `$CLAUDE_PROJECT_DIR` must become cwd-relative paths (Codex hooks receive `cwd` in their input JSON).

### 3. Everything else is translation, not redesign

MCP is a one-time `.mcp.json` → `[mcp_servers]` TOML rendering. `AGENTS.md` replaces/augments `CLAUDE.md` (and the `@AGENTS.md` shim keeps a single source). The commit plumbing and Python tools run unchanged — they're shell and `uv`, not Claude features. Prereqs gain nothing new.

## Directory strategy — recommendation

**Generate per-tool output from the Claude-native source at install time. Do not symlink. Do not hand-maintain a second tree.**

| Option | Verdict | Why |
|:-------|:--------|:----|
| `.agents/` cross-linked (symlinks) | **No** | Symlinks die in npm tarballs (resolved at pack time), on Windows (`core.symlinks=false` default), and Gemini CLI has a cluster of open symlink bugs. Codex follows them, but the distribution channel doesn't. |
| Copy to `~/.codex/` home dir | **No** | Not versioned, not team-shared, drifts per machine — and the home-prompts mechanism it targeted is deprecated anyway. |
| Hand-maintained per-tool forks | **No** | The SuperClaude anti-pattern: three parallel frameworks to keep in sync by hand. |
| **Install-time generation: `.claude/` stays canonical; `npx … --codex` writes `.agents/skills/` + `.codex/`** | **Yes** | The pattern every surviving multi-CLI framework converged on (ruler, GSD, dot-ai). Skills copy near-verbatim (same standard); commands render to one-skill-per-command; hooks render to `.codex/hooks.json`; MCP renders to `.codex/config.toml`. Generated outputs are gitignored as build artifacts, exactly like stride's existing gitignore section management. |

`.agents/` is no longer just "a working name" — it's the actual repo-scope path Codex scans for skills and where its plugin marketplace lives, with ~16 tools adopting the same convention. Stride's installer guard (`assertUnderClaudeDir`) loosens to "under `.claude/`, `.agents/`, or `.codex/` only" — still a bounded, refusable footprint, and decision 002's namespace logic carries over unchanged.

## Minimum fresh-install path to a first successful command

1. `npx github:webventurer/stride --codex` (new flag) — generates `.agents/skills/` (3 skills + N command-skills), `.codex/hooks.json`, `.codex/config.toml` (context7 MCP), `AGENTS.md` section, gitignore section.
2. User trusts the project in Codex (`.codex/` layers are skipped untrusted).
3. User approves the two hooks via `/hooks` (per-hash trust).
4. `LINEAR_<WORKSPACE>_API_KEY` in `~/.env`, `gh`/`uv`/`jq` present — unchanged from the Claude path.
5. `$linear-start WB-123` in Codex → the skill drives the same `linear_cli.py` flow.

Steps 2–3 are Codex-imposed friction with no Claude equivalent; the install doc must name them or the guardrails silently don't run.

## Does this warrant a Vision update?

Yes, when the implementation ticket is scoped — but not the wording the constraint anticipated. The Vision says: *"Currently Claude Code is the only supported AI agent — AgentSDK integration would unlock others."* The spike shows the unlock is **not** AgentSDK: it's the ecosystem converging on open standards stride can target directly — Agent Skills for skills, `AGENTS.md` for ambient context, Claude-shaped lifecycle hooks. A truthful evolved constraint would read along the lines of: *"Claude Code is the primary agent; other CLIs are supported where they implement the open standards stride targets (Agent Skills, AGENTS.md, lifecycle hooks) — via install-time generation from the Claude-native source."* Run `/vision` to evolve it alongside the implementation ticket, per [vision-evolves-with-the-work](../patterns/vision-evolves-with-the-work.md).

## Scoping notes for the implementation ticket

- The build is mostly installer work: a `--codex` target in `bin/install.mjs` plus renderers (SKILL.md passthrough, command→skill wrapper, hooks.json writer, TOML writer). No runtime code changes.
- Command-skill rendering is the only piece with design judgement in it — how much of each `/linear:*` body survives verbatim vs needs Codex-flavoured framing (argument handling, no `/commit` skill chaining).
- Hook trust UX needs a documented walkthrough; consider whether Codex **plugins** (skills + hooks + MCP in one trusted unit) beat raw `.codex/` files — the litestar-skills repo ships both and is the working example to study.
- Out of scope here, per the card: Gemini CLI (separate ticket — note its symlink bugs and TOML command format make it a genuinely different renderer), AgentRouter.

---

*Sources: Codex CLI docs ([skills](https://developers.openai.com/codex/skills), [hooks](https://developers.openai.com/codex/hooks), [config](https://developers.openai.com/codex/config-reference), [MCP](https://developers.openai.com/codex/mcp), [custom prompts](https://developers.openai.com/codex/custom-prompts), [plugins](https://developers.openai.com/codex/plugins)), [agents.md](https://agents.md/), [agentskills.io](https://agentskills.io), `openai/codex` source (`core-skills/loader.rs`, issues [#9848](https://github.com/openai/codex/issues/9848), [#19385](https://github.com/openai/codex/issues/19385)), prior art ([ruler](https://github.com/intellectronica/ruler), [GSD](https://github.com/open-gsd/gsd-core), [dot-ai](https://github.com/luisrudge/dot-ai), [litestar-skills](https://github.com/litestar-org/litestar-skills)), and stride's `bin/install.mjs`, `bin/uninstall.mjs`, `bin/prereqs.mjs`, `docs/decisions/001`, `docs/decisions/002`. Researched 2026-06-11 against Codex CLI 0.139.0.*

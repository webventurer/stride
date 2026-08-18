# What stride needs to run under Gemini CLI

> **Gemini fits stride's commands better than Codex does.** It has namespaced slash commands with argument substitution — so `/linear:start WB-123` maps across unchanged, where Codex had to flatten it to `$linear-start`. It reads the same `.agents/skills/` directory Codex does, and its hooks honour the same exit-2 contract. The divergence is narrower than the card assumed: one command renderer, not a redesign.

Spike findings for WB-532. Verified against Gemini CLI **v0.55.1** (released 2026-08-11), tested against **0.50.0** installed locally, and stride `main` as of 2026-08-18.

## The short version

| Stride piece | Gemini home | Port difficulty |
|:-------------|:------------|:----------------|
| Skills (`commit`, `craft`, `vision`, `clear-speak`) | `.agents/skills/` — the same path Codex reads | **None** — one directory serves both tools |
| Commands (`/linear:*`) | `.gemini/commands/linear/<name>.toml` → `/linear:start` | **Moderate** — a TOML renderer, but the name and arguments survive |
| `block_bare_git_commit.sh` | `BeforeTool`, matcher `run_shell_command` | **None** — same payload field, same exit-2 contract |
| `inject_design_principles.sh` | `BeforeAgent`, `additionalContext` | **None** — the JSON stride already emits |
| Hook registration | `.gemini/settings.json` under `hooks` | **Easy** — a writer, like `.codex/hooks.json` |
| MCP | `.gemini/settings.json` under `mcpServers` | **Easy** — one-time translation |
| `permissions.deny` | Policy engine (`toolName`, `commandPrefix`, `commandRegex`) | **Possible** — unlike Codex, Gemini has a primitive for this |
| Python tools, commit plumbing | Unchanged — shell and `uv` | **None** |

## What generalises across the three CLIs

This is the part WB-635 needs.

**Shared — write once, register three times:**

| Contract | Claude | Codex | Gemini |
|:---------|:-------|:------|:-------|
| Hook input | JSON on `stdin` | same | same |
| Payload carries `cwd` | yes | yes | yes |
| Shell command path | `tool_input.command` | `tool_input.command` | `tool_input.command` |
| Block a tool | exit 2, `stderr` is the reason | same | same |
| Inject prompt context | `hookSpecificOutput.additionalContext` | same | same |
| Skill format | `SKILL.md`, `name` + `description` frontmatter | same | same |

Stride's two hook scripts and four skills are already in the shared column. **They need no per-tool variant at all** — only registration differs.

**Per-tool — the part an agent module owns:**

| Concern | Claude | Codex | Gemini |
|:--------|:-------|:------|:-------|
| Skills directory | `.claude/skills/` | `.codex/skills/` or `.agents/skills/` | `.gemini/skills/` or `.agents/skills/` |
| Commands | `.claude/commands/linear/*.md`, `$ARGUMENTS` | none — render each to a skill, arguments lost | `.gemini/commands/linear/*.toml`, <code v-pre>{{args}}</code> |
| Pre-tool event | `PreToolUse`, matcher `Bash` | `PreToolUse`, matcher `^Bash$` | `BeforeTool`, matcher `run_shell_command` |
| Prompt event | `UserPromptSubmit` | `UserPromptSubmit` | `BeforeAgent` |
| Hook registration | `.claude/settings.local.json` | `.codex/hooks.json` | `.gemini/settings.json` |
| Ambient context file | `CLAUDE.md` | `AGENTS.md` | `GEMINI.md` |
| MCP | `.mcp.json` | `.codex/config.toml` `[mcp_servers]` | `.gemini/settings.json` `mcpServers` |

<mark>**The seam is registration, not behaviour.**</mark> An agent module needs to answer four questions: which directory do my skills go in, how do commands render, which event names do I register under, and where does that registration live. Nothing else varies.

## Commands are where Gemini and Codex genuinely differ

Codex has no namespaced slash commands, so WB-631 rendered each command to a skill invoked as `$linear-start`, losing both the `linear:` namespace and argument substitution. Gemini needs none of that:

- `.gemini/commands/linear/start.toml` becomes `/linear:start` — subdirectories create the namespace, exactly as Claude's directories do.
- <code v-pre>{{args}}</code> in the `prompt` field receives whatever followed the command, the direct equivalent of Claude's `$ARGUMENTS`.

Verified live. A probe command at `.gemini/commands/linear/probe.toml` containing `prompt = "Report the argument you were given: &#123;&#123;args&#125;&#125;"`, invoked as `/linear:probe WB-123`, answered *"The argument you provided is: WB-123"*.

The TOML file itself is two fields — `description` and `prompt` — so the renderer's real work is deciding what the `prompt` says. The cheapest version points at the canonical command file the way the Codex skills do, keeping `.claude/commands/linear/` the only place a body is authored.

## Skills need no work at all

`.agents/skills/` is read by both Codex and Gemini. Gemini also accepts `.gemini/skills/`, and its user-scope paths are `~/.gemini/skills/` and `~/.agents/skills/`.

Verified live: a `SKILL.md` placed in `.agents/skills/probe-skill/` was discovered by Gemini 0.50.0, which reported the skill and quoted a marker string from its body — so the file is read, not merely listed.

This is the strongest argument for revisiting WB-533's choice of `.codex/skills/`. That decision was taken for footprint tidiness when Codex was the only target; with a second tool reading the same standard path, `.agents/skills/` would let one generated tree serve both. The counter-argument is ownership: a shared directory makes "remove exactly what was installed" harder, since two agents' uninstalls would target the same tree.

## Hooks are a registration change, nothing more

Both of stride's scripts already satisfy Gemini's contract:

- `block_bare_git_commit.sh` reads `.tool_input.command` and exits 2 with the reason on `stderr`. Gemini's `run_shell_command` takes a `command` string argument, and `BeforeTool` documents *"Exit Code 2 (Block Tool): Prevents execution. Uses `stderr` as the `reason` sent to the agent."* The script runs unmodified; only the matcher changes from `^Bash$` to `run_shell_command`.
- `inject_design_principles.sh` already emits `hookSpecificOutput.additionalContext` and resolves its doc from the payload's `cwd`. `BeforeAgent` reads exactly that field. The only change is the event name it registers under.

Registration goes in `.gemini/settings.json` under `hooks`, with the same `matcher` + `hooks[]` + `{type, command}` shape Claude and Codex use.

Two frictions to document, both mirroring Codex:

- **Trusted folders.** Gemini refuses to run in an untrusted directory at all — headless runs need `--skip-trust` or `GEMINI_CLI_TRUST_WORKSPACE=true`. This is broader than Codex's per-hash hook trust: it gates the whole session, not just the hooks.
- **`hooksConfig.enabled: false`** switches the hook system off wholesale, the counterpart to Codex's `allow_managed_hooks_only`.

## The one guardrail that gets *better*

Stride's `permissions.deny` on `mcp__claude_ai_Linear__*` has no Codex equivalent, and WB-633 documented that gap rather than faking it. Gemini has a policy engine with `toolName`, `commandPrefix` and `commandRegex` rules — so the Linear-MCP block may be expressible there. Worth confirming during the build; it would make Gemini the only non-Claude tool where that guardrail is enforced rather than documented.

## Directory strategy — recommendation

**Same as Codex: generate at install time from the `.claude/` source, into `.gemini/`.**

Symlinks stay ruled out — Gemini has a cluster of open symlink issues, and the npm tarball resolves them at pack time regardless. A home-directory copy stays ruled out for the same reasons as before: unversioned, not team-shared, drifts per machine.

The live question is whether skills go to `.gemini/skills/` (tidy, self-owned, mirrors the Codex decision) or `.agents/skills/` (one tree for both tools, no duplication). That is a WB-635 decision now that it has two cases to weigh, not a WB-532 one.

## Minimum fresh-install path

1. `npx github:webventurer/stride --agent gemini` — generates `.gemini/skills/` (or `.agents/skills/`), `.gemini/commands/linear/*.toml`, and a `hooks` block merged into `.gemini/settings.json`.
2. Trust the folder in Gemini, or the session will not start.
3. `LINEAR_<WORKSPACE>_API_KEY` in `~/.env`, `gh`/`uv`/`jq` present — unchanged.
4. `/linear:start WB-123` in Gemini drives the same flow it drives under Claude.

Step 2 is Gemini-imposed and has no Claude equivalent; the install docs must name it, as they now do for Codex's hook trust.

## Does this warrant a Vision update?

No. The Vision was already opened to standards-based CLIs during the Codex work, and its constraint — *"A CLI is supported only where it already implements the open standards stride targets — Agent Skills, `AGENTS.md`, lifecycle hooks"* — describes Gemini accurately. Gemini reads Agent Skills, has lifecycle hooks, and uses `GEMINI.md` rather than `AGENTS.md`, which the constraint's spirit covers. Nothing here strains it.

## Scoping notes for the implementation ticket

- **Settings merge, not file write.** Gemini's hooks and MCP config share `.gemini/settings.json` with the user's own settings, so the installer must merge the way it does for `.claude/settings.local.json` — never overwrite. This is a real difference from Codex, where `hooks.json` is stride's file alone.
- The command renderer is the only substantive new code: read `.claude/commands/linear/*.md`, write `.gemini/commands/linear/<stem>.toml` with a `description` from the frontmatter and a `prompt` that points at the canonical file.
- Skills need a copy, not a render — the same as Codex.
- Confirm whether the policy engine can express the Linear-MCP deny before assuming it can.
- **Do WB-635 first, or at least alongside.** This spike exists to give that card a second case; building a third set of bespoke glue before extracting the shape would waste the information.
- Gemini ships nightly builds and moved from 0.50 to 0.55 within weeks. Pin the verified version in whatever the ticket asserts, and re-verify before starting.

---

*Sources: `google-gemini/gemini-cli` docs at HEAD ([hooks reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md), [agent skills](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/using-agent-skills.md), [custom commands](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/custom-commands.md), [configuration](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/configuration.md), [shell tool](https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/shell.md)); live probes against Gemini CLI 0.50.0; and stride's `bin/install.mjs`, `install/agents/codex/skills.mjs`, `install/agents/codex/hooks.mjs`, [`docs/research/codex-cli-support.md`](codex-cli-support.md). Researched 2026-08-18 against v0.55.1.*

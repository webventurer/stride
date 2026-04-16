# 002 — Namespace the install footprint under .claude/stride/

**Date:** 2026-04-16
**Status:** Rejected
**Linear:** WB-231

## Context

Stride's installer scatters files across the consumer's `.claude/` tree — `.claude/hooks/`, `.claude/commands/linear/`, `.claude/skills/commit/`, `.claude/skills/craft/`, `.claude/docs/`. These mingle with files the consumer owns. The boundary between "stride's" and "mine" is invisible to `.gitignore` except by enumerating every path.

Every time stride adds a new tool, the consumer has to hand-patch their root `.gitignore` to hide it. Lander did this twice in two weeks — third time is guaranteed. This is recurrence revealing a structural problem, not a one-off inconvenience.

## Attempted decision

**All installed artefacts live under `.claude/stride/`.** The consumer's root `.gitignore` needs exactly one line — `.claude/stride/` — forever.

## Why this was rejected

Claude Code discovers skills and commands from **fixed filesystem locations**: `.claude/skills/` and `.claude/commands/`. There is no `commandsPath` or `skillsPath` setting. Moving content under `.claude/stride/skills/` and `.claude/stride/commands/` makes `/commit`, `/craft`, and `/linear:*` invisible to Claude Code — they simply disappear from the slash command list.

We found this out by implementing the change (PR #11), reverting hooks-only would have worked, but the main payload (skills and commands) cannot live outside the canonical paths without loss of functionality.

The decision was made without verifying Claude Code's discovery mechanism — that's the friction signal we should have read earlier.

## What we learned

Codefu also faces this problem. Its `.claude/.gitignore` enumerates every symlinked skill individually. The "one gitignore line" promise was architecturally incompatible with Claude Code's discovery model from the start.

Three paths forward that actually work:

| Option | Approach | Trade-off |
|:-------|:---------|:----------|
| Plugin | Package stride as a Claude Code plugin; `plugin.json` declares custom skill and command paths | Bigger architectural change; different install/distribution model |
| Symlinks | Physical files under `.claude/stride/`; symlinks at canonical paths | Consumer gitignores the symlinks too — defeats the "one line" promise |
| Partial namespace | Hooks, docs, tools under `.claude/stride/`; skills and commands at canonical paths | Consumer `.gitignore` still grows when stride adds new skill groups |

## Recommendation

**Follow up with a plugin-based approach.**

Claude Code plugins declare their own skill and command paths via `.claude-plugin/plugin.json`:

```json
{
  "name": "stride",
  "skills": "./skills/",
  "commands": ["./commands/"]
}
```

This means:

- All stride content lives inside a single directory (plugin root)
- Claude Code discovers skills and commands through the plugin mechanism, not filesystem convention
- Consumers install stride as a plugin — no `.gitignore` churn at all
- Distribution uses Claude Code's native plugin model instead of `npx` copying

This should be a new Linear issue, scoped separately from WB-231. The work involves:

1. Restructuring the stride source repo to match plugin layout
2. Adding `.claude-plugin/plugin.json` manifest
3. Replacing `npx github:webventurer/stride` install with a plugin install flow
4. Updating `docs/install.md`, `README.md`, and consumer-facing content

## Consequences of this rejection

- PR #11 closed without merging
- Feature branch deleted
- `.claude/stride/` namespace pattern is not adopted
- The original consumer pain (`.gitignore` growing every release) remains until the plugin follow-up is done

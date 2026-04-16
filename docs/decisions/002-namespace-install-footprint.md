# 002 — Namespace the install footprint under .claude/stride/

**Date:** 2026-04-16
**Status:** Accepted
**Linear:** WB-231

## Context

Stride's installer scatters files across the consumer's `.claude/` tree — `.claude/hooks/`, `.claude/commands/linear/`, `.claude/skills/commit/`, `.claude/skills/craft/`, `.claude/docs/`. These mingle with files the consumer owns. The boundary between "stride's" and "mine" is invisible to `.gitignore` except by enumerating every path.

Every time stride adds a new tool, the consumer has to hand-patch their root `.gitignore` to hide it. Lander did this twice in two weeks — third time is guaranteed. This is recurrence revealing a structural problem, not a one-off inconvenience.

## Decision

**All installed artefacts live under `.claude/stride/`.** The consumer's root `.gitignore` needs exactly one line — `.claude/stride/` — forever.

The internal structure mirrors the current layout:

```
.claude/stride/
├── skills/commit/
├── skills/craft/
├── commands/linear/
├── hooks/
├── docs/
└── tools/
```

Hook wiring stays in `settings.local.json` (already gitignored per [decision 001](001-hooks-in-settings-local.md)). Hook `command` paths point at `.claude/stride/hooks/...` instead of `.claude/hooks/...`. Claude Code does not auto-discover hooks from `.claude/hooks/` — the `command` field is a plain shell command that works with any path.

## Why

- **One line, forever** — `.claude/stride/` in `.gitignore` covers every future tool stride adds
- **Clear ownership boundary** — everything inside `.claude/stride/` is stride's; everything outside is the consumer's
- **One reason to change** — adding a stride tool means adding files under `.claude/stride/`, not touching `.gitignore`
- **Clean uninstall** — `rm -rf .claude/stride/` removes everything; no scattered files left behind

## Consequences

- The install script copies to `.claude/stride/<category>/` instead of `.claude/<category>/`
- `settings.local.json` hook paths use `$CLAUDE_PROJECT_DIR/.claude/stride/hooks/...`
- The uninstall script removes `.claude/stride/` instead of enumerating individual directories
- Existing consumers do a one-time cleanup: delete scattered paths, replace the multi-line `.gitignore` block with `.claude/stride/`
- Stride's source tree also uses `.claude/stride/` — the installer copies from `.claude/stride/` to `.claude/stride/` (same path, no mapping needed). This keeps `copyDir` simple and the source layout mirrors what consumers see

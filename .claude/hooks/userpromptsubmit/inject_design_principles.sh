#!/bin/bash
# UserPromptSubmit hook: inject design decision principles. Emits the JSON
# both Claude Code and Codex read, resolving the doc from the payload's cwd so
# neither tool needs an environment variable the other does not set.

ROOT=$(jq -r '.cwd // empty')
DOC="$ROOT/.claude/stride/docs/principles/design-decisions.md"

[ -f "$DOC" ] || exit 0

jq -n --rawfile context "$DOC" \
  '{hookSpecificOutput: {hookEventName: "UserPromptSubmit", additionalContext: $context}}'

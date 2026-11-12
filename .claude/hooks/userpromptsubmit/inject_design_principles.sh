#!/bin/bash
# UserPromptSubmit hook: inject design decision principles. Emits the JSON
# both Claude Code and Codex read, finding the doc from this script's own
# location so it works from any folder the shell sits in, and neither tool
# needs an environment variable the other does not set.

ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
DOC="$ROOT/.claude/stride/docs/principles/design-decisions.md"

[ -f "$DOC" ] || exit 0

jq -n --rawfile context "$DOC" \
  '{hookSpecificOutput: {hookEventName: "UserPromptSubmit", additionalContext: $context}}'

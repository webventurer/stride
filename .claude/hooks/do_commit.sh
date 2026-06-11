#!/bin/bash
# Wrapper for git commit — used exclusively by the /commit skill.
#
# The PreToolUse hook blocks all bare "git commit" commands.
# This script is the only sanctioned path to commit. Because the
# hook inspects the top-level Bash command (not subprocesses),
# calling this script bypasses the block cleanly.
#
# Before forwarding, the message passed via -m/-F is checked against
# the /commit skill's 50/72 width rule. Flags that carry no new
# message (--amend --no-edit, --fixup, editor commits) pass through
# unchecked — fail open, never block.
#
# Usage: .claude/hooks/do_commit.sh -m "feat: Subject" -m "Body..."
# All arguments are forwarded to git commit unchanged.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK="$DIR/check_commit_widths.py"

if [ -f "$CHECK" ] && command -v python3 >/dev/null; then
  python3 "$CHECK" --args "$@" || exit 1
fi

git commit "$@"

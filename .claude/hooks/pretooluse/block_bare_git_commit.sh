#!/bin/bash
# PreToolUse hook: block bare git commit commands that land in this project.
#
# All commits into the project must go through the /commit skill, which uses
# .claude/hooks/do_commit.sh instead of git commit directly. The hook only
# sees the top-level Bash command, so the wrapper script's internal git
# commit is invisible to it. A commit in a repository outside the project,
# such as a scratch repository a test builds, is allowed.
#
# Receives JSON on stdin with tool_input.command and cwd. Exits 0 to allow,
# exits 2 to block with a message. The decision is made by
# block_bare_git_commit.py; if that crashes the command is blocked. Without
# python3 it falls back to blocking any command that contains the words.

INPUT=$(cat)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null; then
  grep -qE 'git.*commit' <<<"$INPUT" || exit 0
  echo 'BLOCKED: bare "git commit" is not allowed (python3 is not installed, so the guard cannot tell where it lands).' >&2
  exit 2
fi

python3 "$DIR/block_bare_git_commit.py" <<<"$INPUT" || exit 2

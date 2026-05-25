#!/bin/bash
# Wrapper for git commit — used exclusively by the /commit skill.
#
# The PreToolUse hook blocks all bare "git commit" commands.
# This script is the only sanctioned path to commit. Because the
# hook inspects the top-level Bash command (not subprocesses),
# calling this script bypasses the block cleanly.
#
# Before committing it formats the *staged* files — and only those —
# when the project opts in with a "fix:staged" package.json script, so
# format drift never lands and unrelated files are never touched. A repo
# without that script commits unchanged. (Partially-staged files get
# fully staged after formatting; split such commits with `git add -p`
# and format manually if that matters.)
#
# Usage: .claude/hooks/do_commit.sh -m "feat: Subject" -m "Body..."
# All arguments are forwarded to git commit.

run_staged_formatter() {
  if [ -f pnpm-lock.yaml ]; then pnpm run --silent fix:staged
  elif [ -f yarn.lock ]; then yarn --silent fix:staged
  else npm run --silent fix:staged
  fi
}

format_staged() {
  [ -f package.json ] || return 0
  grep -q '"fix:staged"' package.json || return 0

  local staged
  staged=$(mktemp)
  git diff --cached --name-only -z --diff-filter=ACM >"$staged"
  if [ -s "$staged" ]; then
    run_staged_formatter
    xargs -0 git add -- <"$staged"
  fi
  rm -f "$staged"
}

format_staged
git commit "$@"

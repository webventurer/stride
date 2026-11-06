#!/bin/bash
set -euo pipefail
# Removes the worktree that has a card's branch checked out, wherever it
# sits, so worktrees made beside the repo are cleaned up as well as those in
# .claude/worktrees. Prints the removed path; prints nothing when no
# worktree has the branch.
# Usage: .claude/tools/remove_card_worktree.sh <main-repo> <branch>

# --- Guards ---

die() { echo "Error: $*" >&2; exit 1; }

require_args() {
  [ "$#" -eq 2 ] || die "Usage: remove_card_worktree.sh <main-repo> <branch>"
  [ -d "$1" ] || die "Main repo not found: $1"
}

# --- Functions ---

branch_worktree() {
  git -C "$MAIN_REPO" worktree list --porcelain |
    awk -v ref="branch refs/heads/$BRANCH" '/^worktree /{path=substr($0, 10)} $0==ref{print path}'
}

remove_or_prune() {
  if [ -d "$WORKTREE" ]; then
    git -C "$MAIN_REPO" worktree remove --force "$WORKTREE"
  else
    git -C "$MAIN_REPO" worktree prune
  fi
  echo "$WORKTREE"
}

# --- Execution ---

require_args "$@"
MAIN_REPO="$1"
BRANCH="$2"
WORKTREE="$(branch_worktree)"
[ -n "$WORKTREE" ] || exit 0
remove_or_prune

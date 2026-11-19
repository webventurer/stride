#!/bin/bash
set -euo pipefail
# Deletes a merged card's local branch from inside the job's own worktree, so
# the coordinator has only the worktree folder left to remove. Fetches origin's
# main, and deletes the branch only when its work is on origin/main: it detaches
# this worktree at the branch's own commit first (git won't delete a branch a
# worktree has checked out), then deletes the branch with a plain `branch -d`.
# Prints "deleted" (also when the branch was already gone), or
# "kept: <reason>" and changes nothing. Run it from the job's worktree.
# Usage: .claude/tools/delete_job_branch.sh <card-branch>

# --- Guards ---

die() { echo "Error: $*" >&2; exit 1; }

require_args() {
  [ "$#" -eq 1 ] || die "Usage: delete_job_branch.sh <card-branch>"
}

# --- Functions ---

keep() {
  echo "kept: $1"
  exit 0
}

branch_exists() {
  git rev-parse --verify --quiet "refs/heads/$BRANCH" >/dev/null
}

# --- Execution ---

require_args "$@"
BRANCH="$1"

branch_exists || { echo "deleted"; exit 0; }
git fetch --quiet origin main >/dev/null 2>&1 || keep "the fetch failed"
git merge-base --is-ancestor "$BRANCH" origin/main || keep "its work is not on origin/main"

if [ "$(git branch --show-current)" = "$BRANCH" ]; then
  git switch --quiet --detach
fi
git branch -d "$BRANCH" >/dev/null 2>&1 || keep "git refused to delete it"
echo "deleted"

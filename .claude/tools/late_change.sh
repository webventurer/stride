#!/bin/bash
set -euo pipefail
# Says whether the files changed since a card's end check need a fresh one.
# Compares the checked tree with the branch's current one and prints
# "no fresh check: <files>" or "fresh check: <reason>". Only VISION.md,
# README.md and Markdown pages under docs/ can skip it, never an agent's
# instruction file, and none that a card promise names or depends on: pass
# those paths, or their folders, after the tree. A change it can't place gets a
# fresh check. Run it in the branch.
# Usage: .claude/tools/late_change.sh <checked-tree> [promised-path ...]

# --- Guards ---

die() { echo "Error: $*" >&2; exit 1; }

require_args() {
  [ "$#" -ge 1 ] || die "Usage: late_change.sh <checked-tree> [promised-path ...]"
}

# --- Functions ---

fresh() {
  echo "fresh check: $1"
  exit 0
}

changed_files() {
  git -c core.quotePath=false diff-tree -r --name-only "$TREE^{tree}" "HEAD^{tree}"
}

can_skip() {
  case "$1" in
    */CLAUDE.md | */AGENTS.md | */.claude/*) return 1 ;;
    VISION.md | README.md | docs/*.md) return 0 ;;
    *) return 1 ;;
  esac
}

is_promised() {
  local file="$1" path
  shift
  for path in "$@"; do
    path="${path#./}"
    path="${path%/}"
    case "$file" in
      "$path" | "$path"/*) return 0 ;;
    esac
  done
  return 1
}

# --- Execution ---

require_args "$@"
TREE="$1"
shift

git cat-file -e "$TREE^{tree}" 2>/dev/null || fresh "the checked tree can't be read"
FILES="$(changed_files)" || fresh "the comparison failed"

SKIPPED=""
while IFS= read -r file; do
  [ -n "$file" ] || continue
  can_skip "$file" || fresh "$file is not a file that can skip it"
  ! is_promised "$file" "$@" || fresh "$file is named by a promise"
  SKIPPED="${SKIPPED:+$SKIPPED, }$file"
done <<<"$FILES"

echo "no fresh check: ${SKIPPED:-no file changed}"

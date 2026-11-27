#!/bin/bash
set -euo pipefail
# Says whether what moved since a card's end check needs a fresh one, and prints
# "no fresh check: <what moved>" or "fresh check: <reason>". Given the checked
# change as <base>..<tree>, it replays that change through each merge of main
# into the branch, up to the point where the branch now leaves origin/main, and
# compares the result with the branch, so work that only main brought in never
# counts. The replay needs git 2.38 or later; an untouched branch needs none.
# Given only a tree, as older records hold, it compares that tree with the
# branch's. Only VISION.md, README.md and Markdown pages under docs/ can skip a
# check, never an agent's instruction file, and none that a card promise names
# or depends on: pass those paths, or their folders, after the checked value. A
# change it can't place gets a fresh check. Run it in the branch.
# Usage: .claude/tools/late_change.sh <checked-change|checked-tree> [promised-path ...]

# --- Guards ---

die() { echo "Error: $*" >&2; exit 1; }

require_args() {
  [ "$#" -ge 1 ] || die "Usage: late_change.sh <checked-change|checked-tree> [promised-path ...]"
}

# --- Functions ---

fresh() {
  echo "fresh check: $1"
  exit 0
}

scratch_commit() {
  git -c user.name=stride -c user.email=stride@localhost \
    commit-tree -m "checked change" "$@"
}

main_merges() {
  git log --reverse --first-parent --merges --format=%P origin/main..HEAD |
    cut -d' ' -f2
}

replayed_tree() {
  local base="$1" tree="$2" now checked onto
  now="$(git merge-base origin/main HEAD)" || return 1
  if [ "$now" = "$base" ] && [ "$(git rev-parse "HEAD^{tree}")" = "$tree" ]; then
    echo "$tree"
    return
  fi
  checked="$(scratch_commit "$tree" -p "$base")" || return 1
  for onto in $(main_merges) "$now"; do
    git merge-base --is-ancestor "$onto" origin/main || continue
    tree="$(git merge-tree --write-tree "$checked" "$onto")" || return 1
    checked="$(scratch_commit "$tree" -p "$checked" -p "$onto")" || return 1
  done
  echo "$tree"
}

changed_files() {
  git -c core.quotePath=false diff-tree -r --name-only "$1^{tree}" "HEAD^{tree}"
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
CHECKED="$1"
shift

case "$CHECKED" in
  *..*)
    BASE="${CHECKED%%..*}"
    TREE="${CHECKED##*..}"
    git cat-file -e "$BASE^{commit}" 2>/dev/null &&
      git cat-file -e "$TREE^{tree}" 2>/dev/null ||
      fresh "the checked change can't be read"
    EXPECTED="$(replayed_tree "$BASE" "$TREE" 2>/dev/null)" ||
      fresh "the checked change doesn't replay cleanly on main"
    UNMOVED="the card's own change is as checked"
    ;;
  *)
    git cat-file -e "$CHECKED^{tree}" 2>/dev/null || fresh "the checked tree can't be read"
    EXPECTED="$CHECKED"
    UNMOVED="no file changed"
    ;;
esac

FILES="$(changed_files "$EXPECTED")" || fresh "the comparison failed"

SKIPPED=""
while IFS= read -r file; do
  [ -n "$file" ] || continue
  can_skip "$file" || fresh "$file is not a file that can skip it"
  ! is_promised "$file" "$@" || fresh "$file is named by a promise"
  SKIPPED="${SKIPPED:+$SKIPPED, }$file"
done <<<"$FILES"

echo "no fresh check: ${SKIPPED:-$UNMOVED}"

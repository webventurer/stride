#!/bin/bash
set -euo pipefail
# Links what stride installed in the main checkout into a fresh worktree.
# Stride's install is gitignored, so a new worktree lacks it; each missing
# path is linked from the main checkout and hidden from git status.
# Usage: .claude/tools/link_stride_install.sh <main-repo> <worktree>

# --- Guards ---

die() { echo "Error: $*" >&2; exit 1; }

require_args() {
  [ "$#" -eq 2 ] || die "Usage: link_stride_install.sh <main-repo> <worktree>"
  [ -d "$1" ] || die "Main repo not found: $1"
  [ -d "$2" ] || die "Worktree not found: $2"
}

# --- Constants ---

EXTRA_PATHS=(.claude/settings.local.json .venv venv)

# --- Functions ---

stride_section_paths() {
  sed -n '/^# >>> stride/,/^# <<< stride <<</{/^#/d;p;}' "$MAIN_REPO/.gitignore" 2>/dev/null || true
}

is_missing_from_worktree() {
  local path="$1"
  [ -e "$MAIN_REPO/$path" ] && [ ! -e "$WORKTREE/$path" ] && [ ! -L "$WORKTREE/$path" ]
}

hide_from_git() {
  local path="$1"
  grep -qxF "/$path" "$EXCLUDE" 2>/dev/null || printf '/%s\n' "$path" >>"$EXCLUDE"
}

link_path() {
  local path="$1"
  mkdir -p "$(dirname "$WORKTREE/$path")"
  ln -s "$MAIN_REPO/$path" "$WORKTREE/$path"
  hide_from_git "$path"
  LINKED+=("$path")
}

link_missing_paths() {
  local path
  for path in $(stride_section_paths) "${EXTRA_PATHS[@]}"; do
    path="${path%/}"
    if is_missing_from_worktree "$path"; then link_path "$path"; fi
  done
}

report_links() {
  [ "${#LINKED[@]}" -gt 0 ] || return 0
  echo "Linked from $MAIN_REPO into the worktree: ${LINKED[*]}"
}

# --- Execution ---

require_args "$@"
MAIN_REPO="$1"
WORKTREE="$2"
EXCLUDE="$(git -C "$WORKTREE" rev-parse --path-format=absolute --git-common-dir)/info/exclude"
LINKED=()
mkdir -p "$(dirname "$EXCLUDE")"
link_missing_paths
report_links

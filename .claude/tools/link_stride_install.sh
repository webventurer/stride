#!/bin/bash
set -euo pipefail
# Links what stride installed in the main checkout into a fresh worktree.
# Stride's install is gitignored, so a new worktree lacks it; each missing
# path is linked from the main checkout and hidden from git status.
# Also links each git-ignored path the main checkout's .stride.json names
# in its "worktree-links" list, so the repo's own commit hooks find them.
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
WORKTREES_DIR=.claude/worktrees

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
    [ "$path" = "$WORKTREES_DIR" ] && continue
    if is_missing_from_worktree "$path"; then link_path "$path"; fi
  done
}

named_paths() {
  [ -f "$SETTINGS" ] && grep -q '"worktree-links"' "$SETTINGS" || return 0
  if ! jq -e '(.["worktree-links"] // []) | type == "array" and all(type == "string")' "$SETTINGS" >/dev/null; then
    echo '.stride.json "worktree-links" must be a list of paths; none linked.' >&2
    return 0
  fi
  jq -r '(.["worktree-links"] // [])[]' "$SETTINGS"
}

is_plain_path() {
  case "$1" in
    "" | /* | *[[:space:]]* | *[*?[]* | .. | ../* | */.. | */../*) return 1 ;;
  esac
}

link_named_paths() {
  local path
  while IFS= read -r path; do
    if ! is_plain_path "$path"; then
      echo "Refused worktree-links name: $path" >&2
      continue
    fi
    path="${path%/}"
    if is_missing_from_worktree "$path"; then
      link_path "$path"
    elif [ ! -e "$MAIN_REPO/$path" ] && [ ! -e "$WORKTREE/$path" ]; then
      ABSENT+=("$path")
    fi
  done < <(named_paths)
}

report_links() {
  [ "${#LINKED[@]}" -gt 0 ] && echo "Linked from $MAIN_REPO into the worktree: ${LINKED[*]}"
  [ "${#ABSENT[@]}" -gt 0 ] && echo "Not linked, missing from the main checkout: ${ABSENT[*]}"
  return 0
}

# --- Execution ---

require_args "$@"
MAIN_REPO="$1"
WORKTREE="$2"
EXCLUDE="$(git -C "$WORKTREE" rev-parse --path-format=absolute --git-common-dir)/info/exclude"
SETTINGS="$MAIN_REPO/.stride.json"
LINKED=()
ABSENT=()
mkdir -p "$(dirname "$EXCLUDE")"
link_missing_paths
link_named_paths
report_links

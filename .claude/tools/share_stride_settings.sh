#!/bin/bash
set -euo pipefail
# Links the main checkout's .stride.json into a worktree, so every
# worktree of the repo reads the same machine-local settings.
# Exits non-zero, leaving the worktree untouched, when the settings are
# missing, not a JSON object, tracked, not ignored, or already taken.
# Usage: .claude/tools/share_stride_settings.sh <main-repo> <worktree>

# --- Guards ---

require_args() {
  [ "$#" -eq 2 ] || { echo "Usage: share_stride_settings.sh <main-repo> <worktree>" >&2; exit 2; }
}

require_settings_object() {
  jq -e 'type == "object"' "$MAIN_REPO/.stride.json" >/dev/null || exit 1
}

require_untracked_and_ignored() {
  local repo
  for repo in "$MAIN_REPO" "$WORKTREE"; do
    if git -C "$repo" ls-files --error-unmatch .stride.json >/dev/null 2>&1; then
      printf 'Tracked .stride.json in %s; stop and remove it from version control.\n' "$repo" >&2
      exit 1
    fi
    git -C "$repo" check-ignore -q .stride.json || exit 1
  done
}

# --- Functions ---

is_shared_link() {
  [ -L "$TARGET" ] && [ "$TARGET" -ef "$SOURCE" ]
}

is_taken() {
  [ -e "$TARGET" ] || [ -L "$TARGET" ]
}

link_settings() {
  if is_shared_link; then
    return 0
  elif is_taken; then
    printf 'Existing .stride.json in %s; preserve it and resolve the conflict.\n' "$WORKTREE" >&2
    exit 1
  fi
  ln -s "$SOURCE" "$TARGET"
}

require_readable_link() {
  test -r "$TARGET" && test "$TARGET" -ef "$SOURCE"
}

# --- Execution ---

require_args "$@"
MAIN_REPO="$1"
WORKTREE="$2"
SOURCE="$MAIN_REPO/.stride.json"
TARGET="$WORKTREE/.stride.json"
require_settings_object
require_untracked_and_ignored
link_settings
require_readable_link

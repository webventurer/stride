#!/bin/bash
set -euo pipefail
# Prints where a card's worktree goes: .claude/worktrees/<issue-id> in the
# main checkout. Refuses when git doesn't ignore that folder, so a worktree
# never shows up in the main checkout's git status or its linters.
# Usage: .claude/tools/card_worktree_path.sh <main-repo> <issue-id>

# --- Guards ---

die() { echo "Error: $*" >&2; exit 1; }

require_args() {
  [ "$#" -eq 2 ] || die "Usage: card_worktree_path.sh <main-repo> <issue-id>"
  [ -d "$1" ] || die "Main repo not found: $1"
}

# --- Constants ---

WORKTREES_DIR=.claude/worktrees

# --- Functions ---

require_ignored() {
  git -C "$MAIN_REPO" check-ignore -q "$WORKTREES_DIR/$ISSUE_DIR" ||
    die "$WORKTREES_DIR/ isn't ignored in $MAIN_REPO. Add this line to its .gitignore: $WORKTREES_DIR/"
}

# --- Execution ---

require_args "$@"
MAIN_REPO="$(cd "$1" && pwd -P)"
ISSUE_DIR="$(printf '%s' "$2" | tr '[:upper:]' '[:lower:]')"
require_ignored
printf '%s/%s/%s\n' "$MAIN_REPO" "$WORKTREES_DIR" "$ISSUE_DIR"

#!/bin/bash
set -euo pipefail
# Decides whether a finishing card may update the main checkout, and changes
# nothing in it. Prints one line: "updated" when the checkout is on main (or on
# the finishing card's own branch), has no uncommitted, staged or untracked
# changes and has no local main commits that origin lacks; otherwise
# "left: <reason>". It fetches origin's main first, and a failed fetch is a
# reason to leave the checkout alone.
# Usage: .claude/tools/main_checkout_update.sh <main-repo-path> <card-branch>

# --- Guards ---

die() { echo "Error: $*" >&2; exit 1; }

require_args() {
  [ "$#" -eq 2 ] || die "Usage: main_checkout_update.sh <main-repo-path> <card-branch>"
}

# --- Functions ---

leave() {
  echo "left: $1"
  exit 0
}

# --- Execution ---

require_args "$@"
MAIN_REPO="$1"
CARD_BRANCH="$2"

git -C "$MAIN_REPO" fetch --quiet origin main >/dev/null 2>&1 || leave "the fetch failed"

BRANCH="$(git -C "$MAIN_REPO" branch --show-current)"
[ -n "$BRANCH" ] || leave "detached HEAD"
[ "$BRANCH" = "main" ] || [ "$BRANCH" = "$CARD_BRANCH" ] || leave "on branch $BRANCH"
[ -z "$(git -C "$MAIN_REPO" status --porcelain)" ] || leave "uncommitted changes"
[ -z "$(git -C "$MAIN_REPO" log origin/main..main --format=%h)" ] || leave "unpushed commits"

echo "updated"

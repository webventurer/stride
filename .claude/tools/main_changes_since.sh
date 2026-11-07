#!/bin/bash
set -euo pipefail
# Lists the commits that reached main on GitHub since a time, counted by when
# GitHub received them rather than the date each commit carries, so a commit
# made before the time but pushed or merged after it is still listed.
# Usage: .claude/tools/main_changes_since.sh <ISO 8601 time>

# --- Guards ---

die() { echo "Error: $*" >&2; exit 1; }

require_args() {
  [ "$#" -eq 1 ] || die "Usage: main_changes_since.sh <ISO 8601 time>"
}

# --- Constants ---

MAIN_ACTIVITY="repos/{owner}/{repo}/activity?ref=refs/heads/main&per_page=100"

# --- Functions ---

whole_seconds() {
  local trimmed="${1%.*}"
  [ "$trimmed" = "$1" ] && printf '%s' "$1" || printf '%sZ' "$trimmed"
}

main_tip_before() {
  gh api --paginate "$MAIN_ACTIVITY" | jq -r --arg since "$SINCE" \
    '.[] | select((.timestamp | fromdateiso8601) > ($since | fromdateiso8601)) | .before' |
    tail -1
}

# --- Execution ---

require_args "$@"
SINCE="$(whole_seconds "$1")"
git fetch -q origin main
TIP_BEFORE="$(main_tip_before)"
[ -n "$TIP_BEFORE" ] || exit 0
git log --first-parent --format='%h %ci %s' "$TIP_BEFORE..origin/main"

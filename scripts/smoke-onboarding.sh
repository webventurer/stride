#!/usr/bin/env bash
# Measure stride's onboarding wall-clock against the 90-second Vision budget.
#
# Times the path from `node bin/install.mjs` (what `npx github:webventurer/stride`
# runs underneath) to first successful `linear_cli.py whoami`. That's what a
# fresh user does before they can run their first `/linear:start`.
#
# Run locally:
#   LINEAR_API_KEY=lin_api_... ./scripts/smoke-onboarding.sh
#
# Tighten the budget for CI / regression hunting:
#   STRIDE_SMOKE_BUDGET_SECONDS=75 LINEAR_API_KEY=... ./scripts/smoke-onboarding.sh
#
# Exits 0 if under budget, 1 if over, 2 on setup error (missing prereq, missing
# token, install failed). The 90-second target comes from the VISION.md
# criterion: "Setup gets a fresh user from `npx` to their first successful
# `/linear:start` in under 90 seconds on any supported OS."

set -euo pipefail

BUDGET="${STRIDE_SMOKE_BUDGET_SECONDS:-90}"
WORKDIR=""
trap 'cleanup' EXIT

cleanup() {
    [[ -n "$WORKDIR" && -d "$WORKDIR" ]] && rm -rf "$WORKDIR"
}

require_env() {
    [[ -n "${LINEAR_API_KEY:-}" ]] || die "LINEAR_API_KEY must be set (see docs/install.md)"
}

require_tools() {
    for tool in node uv jq; do
        command -v "$tool" >/dev/null \
            || die "missing prereq: $tool — see docs/install.md"
    done
}

die() {
    echo "error: $*" >&2
    exit 2
}

repo_root() {
    cd "$(dirname "$0")/.." && pwd
}

run_install() {
    # install.mjs prompts for gitignore + hook config. Auto-accept defaults so
    # the smoke run is non-interactive. printf exits cleanly (unlike `yes`,
    # which trips pipefail when install closes its stdin).
    printf 'y\n%.0s' {1..10} | node "$1/bin/install.mjs" 2>&1 | tail -5
}

verify_auth() {
    uv run --with click --with requests .claude/tools/linear_cli.py whoami \
        | jq -e '.authenticated == true' >/dev/null
}

report() {
    local elapsed="$1" budget="$2"
    echo
    if (( elapsed > budget )); then
        echo "FAIL: onboarding took ${elapsed}s, budget ${budget}s"
        echo "      Vision criterion: setup under ${budget}s on any supported OS"
        return 1
    fi
    echo "PASS: ${elapsed}s (budget ${budget}s)"
}

main() {
    require_env
    require_tools

    local root start end
    root="$(repo_root)"
    WORKDIR="$(mktemp -d)"

    cd "$WORKDIR"
    echo "Smoke-test in $WORKDIR against budget=${BUDGET}s..."

    start=$(date +%s)
    run_install "$root"
    verify_auth
    end=$(date +%s)

    report $((end - start)) "$BUDGET"
}

main "$@"
exit $?

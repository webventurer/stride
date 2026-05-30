#!/usr/bin/env bash
# Measure stride's onboarding wall-clock against the 90-second Vision budget.
#
# Two modes:
#   STRIDE_SMOKE_MODE=docker (default) — runs container.sh inside a clean
#       ubuntu:24.04 container. Exercises the Linux/WSL2 install path (WSL2
#       *is* a Linux environment, so the Ubuntu container covers it).
#   STRIDE_SMOKE_MODE=host — runs the timed portion on whatever OS invoked the
#       script. Use this for macOS coverage (Docker can't run macOS containers),
#       or when Docker isn't available.
#
# Docker mode (default — exercises the Linux/WSL2 install path):
#   LINEAR_API_KEY=lin_api_... ./onboarding/smoke-test.sh
#
# Host mode (skips Docker — for macOS coverage, or when Docker isn't available):
#   STRIDE_SMOKE_MODE=host LINEAR_API_KEY=lin_api_... ./onboarding/smoke-test.sh
#
# Use a different base image (docker mode only, default ubuntu:24.04):
#   STRIDE_SMOKE_IMAGE=ubuntu:22.04 LINEAR_API_KEY=... ./onboarding/smoke-test.sh
#
# Exits 0 if under budget, 1 if over, 2 on setup error. Anchors on the Vision
# criterion: "Setup gets a fresh user from `npx` to their first successful
# `/linear:start` in under 90 seconds on any supported OS."

set -euo pipefail

MODE="${STRIDE_SMOKE_MODE:-docker}"
BUDGET="${STRIDE_SMOKE_BUDGET_SECONDS:-90}"
IMAGE="${STRIDE_SMOKE_IMAGE:-ubuntu:24.04}"
REF="${STRIDE_SMOKE_REF:-github:webventurer/stride}"
HERE="$(cd "$(dirname "$0")" && pwd)"

die() {
    echo "error: $*" >&2
    exit 2
}

require_env() {
    [[ -n "${LINEAR_API_KEY:-}" ]] || die "LINEAR_API_KEY must be set"
}

require_docker() {
    command -v docker >/dev/null \
        || die "docker not found — install Docker or set STRIDE_SMOKE_MODE=host"
}

require_host_tools() {
    for tool in node npx jq uv; do
        command -v "$tool" >/dev/null \
            || die "missing prereq for host mode: $tool (see docs/install.md)"
    done
}

run_docker() {
    require_docker
    echo "Smoke-test in $IMAGE (ref=$REF) against budget=${BUDGET}s..."
    echo "Pulling image..."
    docker pull --quiet "$IMAGE" >/dev/null
    docker run --rm -i \
        -e LINEAR_API_KEY="$LINEAR_API_KEY" \
        -e STRIDE_SMOKE_REF="$REF" \
        "$IMAGE" \
        bash -s < "$HERE/container.sh"
}

run_host() {
    require_host_tools
    echo "Smoke-test on host (ref=$REF) against budget=${BUDGET}s..."
    local workdir status=0
    workdir="$(mktemp -d)"
    ( cd "$workdir" && time_onboarding && assert_config_file_auth ) || status=$?
    rm -rf "$workdir"
    return "$status"
}

time_onboarding() {
    local start end
    start=$(date +%s)
    printf 'y\n%.0s' $(seq 1 10) | npx --yes "$REF" >/dev/null 2>&1
    [[ -f .claude/commands/linear/start.md && -x .claude/hooks/do_commit.sh ]] \
        || { echo "install incomplete: missing skill or hook" >&2; exit 1; }
    uv run --with click --with requests .claude/tools/linear_cli.py whoami \
        | jq -e '.authenticated == true' >/dev/null
    end=$(date +%s)
    echo "STRIDE_ELAPSED=$((end - start))"
}

# Untimed: unset LINEAR_API_KEY so auth must resolve via .linear_project.
assert_config_file_auth() {
    printf 'project = Smoke\napi_key_env = STRIDE_SMOKE_CONFIG_KEY\n' > .linear_project
    env -u LINEAR_API_KEY STRIDE_SMOKE_CONFIG_KEY="$LINEAR_API_KEY" \
        uv run --with click --with requests .claude/tools/linear_cli.py whoami \
        | jq -e '.authenticated == true' >/dev/null \
        || { echo "config-file auth path failed: .linear_project -> api_key_env" >&2; exit 1; }
}

extract_elapsed() {
    local out="$1" elapsed
    elapsed=$(echo "$out" | grep -o 'STRIDE_ELAPSED=[0-9]*' | tail -1 | cut -d= -f2)
    [[ -n "$elapsed" ]] || { echo "$out" >&2; die "no elapsed reading"; }
    echo "$elapsed"
}

report() {
    local elapsed="$1"
    echo
    if (( elapsed > BUDGET )); then
        echo "FAIL: onboarding took ${elapsed}s, budget ${BUDGET}s"
        echo "      Vision criterion: setup under ${BUDGET}s on any supported OS"
        exit 1
    fi
    echo "PASS: ${elapsed}s (budget ${BUDGET}s)"
}

main() {
    require_env
    local out
    case "$MODE" in
        docker) out=$(run_docker) ;;
        host) out=$(run_host) ;;
        *) die "unknown STRIDE_SMOKE_MODE: $MODE (use docker or host)" ;;
    esac
    report "$(extract_elapsed "$out")"
}

main "$@"
exit $?

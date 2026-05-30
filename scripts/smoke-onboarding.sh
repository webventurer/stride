#!/usr/bin/env bash
# Measure stride's onboarding wall-clock against the 90-second Vision budget,
# inside a clean Ubuntu LTS container — the path a real user follows.
#
# Times `npx github:webventurer/stride` plus the first successful
# `linear_cli.py whoami`. Prereq install (gh, uv, jq, node) runs first and is
# *outside* the budget — it represents the one-time machine setup a fresh user
# does before reaching for stride.
#
# Run locally:
#   LINEAR_API_KEY=lin_api_... ./scripts/smoke-onboarding.sh
#
# Tighten the budget (e.g. for CI regression hunting):
#   STRIDE_SMOKE_BUDGET_SECONDS=75 LINEAR_API_KEY=... ./scripts/smoke-onboarding.sh
#
# Test a specific branch instead of `main`:
#   STRIDE_SMOKE_REF=github:webventurer/stride#wb-457-foo LINEAR_API_KEY=... ./scripts/smoke-onboarding.sh
#
# Use a different base image (default ubuntu:24.04):
#   STRIDE_SMOKE_IMAGE=ubuntu:22.04 LINEAR_API_KEY=... ./scripts/smoke-onboarding.sh
#
# Exits 0 if under budget, 1 if over, 2 on setup error. Anchors on the Vision
# criterion: "Setup gets a fresh user from `npx` to their first successful
# `/linear:start` in under 90 seconds on any supported OS."

set -euo pipefail

BUDGET="${STRIDE_SMOKE_BUDGET_SECONDS:-90}"
IMAGE="${STRIDE_SMOKE_IMAGE:-ubuntu:24.04}"
REF="${STRIDE_SMOKE_REF:-github:webventurer/stride}"

die() {
    echo "error: $*" >&2
    exit 2
}

require_env() {
    [[ -n "${LINEAR_API_KEY:-}" ]] || die "LINEAR_API_KEY must be set"
}

require_tools() {
    command -v docker >/dev/null \
        || die "docker not found — install Docker to run the smoke test"
}

# The script that runs *inside* the container. Self-contained: installs
# prereqs, then times only the stride-onboarding portion.
container_script() {
    cat <<'BODY'
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

# ---- prereq install (outside stride's 90s budget) ----

apt-get update -qq
apt-get install -qq -y --no-install-recommends curl ca-certificates gnupg jq >/dev/null

# Node (for npx) — NodeSource repo, current LTS
curl -fsSL https://deb.nodesource.com/setup_22.x | bash - >/dev/null 2>&1
apt-get install -qq -y nodejs >/dev/null

# uv (for the Python tools)
curl -LsSf https://astral.sh/uv/install.sh 2>/dev/null | sh >/dev/null
export PATH="$HOME/.local/bin:$PATH"

# gh (GitHub CLI) — official apt repo
mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null
chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | tee /etc/apt/sources.list.d/github-cli.list >/dev/null
apt-get update -qq
apt-get install -qq -y gh >/dev/null

# ---- stride install + auth (timed) ----

mkdir -p /tmp/test-project
cd /tmp/test-project

START=$(date +%s)

# install.mjs prompts for gitignore + hook config. printf exits cleanly so
# pipefail doesn't trip the way `yes` does on SIGPIPE.
printf 'y\n%.0s' $(seq 1 10) | npx --yes REF_PLACEHOLDER >/dev/null 2>&1

uv run --with click --with requests .claude/tools/linear_cli.py whoami \
    | jq -e '.authenticated == true' >/dev/null

END=$(date +%s)
ELAPSED=$((END - START))

# Outer script greps this line
echo "STRIDE_ELAPSED=$ELAPSED"
BODY
}

main() {
    require_env
    require_tools

    echo "Smoke-test in $IMAGE (ref=$REF) against budget=${BUDGET}s..."
    echo "Pulling image..."
    docker pull --quiet "$IMAGE" >/dev/null

    local script
    script="$(container_script | sed "s|REF_PLACEHOLDER|$REF|")"

    local out
    out=$(docker run --rm -i \
        -e LINEAR_API_KEY="$LINEAR_API_KEY" \
        "$IMAGE" \
        bash -c "$script" 2>&1) || {
            echo "$out" >&2
            die "container run failed"
        }

    local elapsed
    elapsed=$(echo "$out" | grep -o 'STRIDE_ELAPSED=[0-9]*' | cut -d= -f2)
    [[ -n "$elapsed" ]] || { echo "$out" >&2; die "no elapsed reading from container"; }

    echo
    if (( elapsed > BUDGET )); then
        echo "FAIL: onboarding took ${elapsed}s, budget ${BUDGET}s"
        echo "      Vision criterion: setup under ${BUDGET}s on any supported OS"
        exit 1
    fi
    echo "PASS: ${elapsed}s (budget ${BUDGET}s)"
}

main "$@"
exit $?

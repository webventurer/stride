#!/usr/bin/env bash
# Run *inside* a clean Ubuntu LTS container by `smoke-test.sh` (docker mode).
# Installs the documented prereqs (outside the 90-second budget), then times
# the stride onboarding — `npx <ref>` plus the first `linear_cli.py whoami`.
#
# Reads `STRIDE_SMOKE_REF` for the install ref (default `github:webventurer/
# stride`). Caller must pass `LINEAR_API_KEY` as an env var. Output line
# `STRIDE_ELAPSED=<seconds>` is what the host script parses.

set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
export DEBCONF_NOWARNINGS=yes

REF="${STRIDE_SMOKE_REF:-github:webventurer/stride}"

# ---- prereq install (outside the budget — represents the user's one-time setup) ----

apt-get update -qq
apt-get install -qq -y --no-install-recommends curl ca-certificates gnupg jq >/dev/null

curl -fsSL https://deb.nodesource.com/setup_22.x | bash - >/dev/null 2>&1
apt-get install -qq -y nodejs >/dev/null

curl -LsSf https://astral.sh/uv/install.sh 2>/dev/null | sh >/dev/null
export PATH="$HOME/.local/bin:$PATH"

mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null
chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | tee /etc/apt/sources.list.d/github-cli.list >/dev/null
apt-get update -qq
apt-get install -qq -y gh >/dev/null

# ---- stride install + auth (timed) ----

mkdir -p /tmp/test-project && cd /tmp/test-project

START=$(date +%s)
printf 'y\n%.0s' $(seq 1 10) | npx --yes "$REF" >/dev/null 2>&1
[[ -f .claude/commands/linear/start.md && -x .claude/hooks/do_commit.sh ]] \
    || { echo "install incomplete: missing skill or hook" >&2; exit 1; }
uv run --with click --with requests .claude/tools/linear_cli.py whoami \
    | jq -e '.authenticated == true' >/dev/null
END=$(date +%s)

echo "STRIDE_ELAPSED=$((END - START))"

# ---- config-file auth probe (untimed — correctness, not the 90s budget) ----
# The env-var path above bypasses .linear_project resolution. Most real users
# instead name a per-workspace key in .linear_project and let bearer_token()
# resolve it from the environment. Exercise that path with LINEAR_API_KEY unset.
printf 'project = Smoke\napi_key_env = STRIDE_SMOKE_CONFIG_KEY\n' > .linear_project
env -u LINEAR_API_KEY STRIDE_SMOKE_CONFIG_KEY="$LINEAR_API_KEY" \
    uv run --with click --with requests .claude/tools/linear_cli.py whoami \
    | jq -e '.authenticated == true' >/dev/null \
    || { echo "config-file auth path failed: .linear_project -> api_key_env" >&2; exit 1; }
rm -f .linear_project

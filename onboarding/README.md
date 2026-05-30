# Onboarding smoke test

> **AI Assistant Note**: This directory holds the wall-clock smoke test that anchors stride's 90-second onboarding criterion. When asked about onboarding measurement, OS coverage, the install gate, or what the smoke test does and doesn't verify, read this file first. Update it when the scripts here change.

stride's [`VISION.md`](../VISION.md) commits to a measurable onboarding budget: a fresh user must go from `npx` to their first successful `/linear:start` in under 90 seconds on any supported OS. This directory holds the script that measures it, so a regression past the budget becomes a release-blocking failure instead of a quiet drift.

## 🚨 Quick reference

**Run it**:

```bash
# Docker mode (default — exercises the Linux/WSL2 install path):
LINEAR_API_KEY=lin_api_... ./onboarding/smoke-test.sh

# Host mode (skips Docker — for macOS coverage, or when Docker isn't available):
STRIDE_SMOKE_MODE=host LINEAR_API_KEY=lin_api_... ./onboarding/smoke-test.sh
```

**Exit codes**: `0` under budget, `1` over budget, `2` setup error (missing prereq, missing `LINEAR_API_KEY`).

**Today's numbers**: 4–6 seconds end-to-end on a clean Ubuntu 24.04 container or macOS Apple Silicon host. 15× headroom over the 90-second budget.

## The two scripts

| File | Where it runs | What it does |
|:-----|:--------------|:-------------|
| `smoke-test.sh` | Caller's shell | Dispatcher. Reads `STRIDE_SMOKE_MODE`, picks docker or host path, parses the elapsed reading, compares against the budget, exits PASS/FAIL. |
| `container.sh` | *Inside* the Ubuntu container (docker mode only) | Installs the documented prereqs (`curl`, `node`, `uv`, `gh`, `jq`) *outside* the timed window, then runs `npx <ref>` plus an auth probe *inside* it. Emits `STRIDE_ELAPSED=<seconds>` for the dispatcher. |

## Supported-OS coverage

stride's Vision criterion names three target OSes — macOS, Ubuntu LTS, and Windows-via-WSL2. The smoke test reaches all three through two modes:

| OS | Mode | Path |
|:---|:-----|:-----|
| **Linux** (Ubuntu LTS) | docker | Pulls `ubuntu:24.04`, runs `container.sh` inside it. Fresh OS, no host contamination. |
| **Windows-via-WSL2** | docker | WSL2 *is* a Linux environment. The Ubuntu container path is the same install path a WSL2 user would hit, so docker mode covers WSL2 by transitivity (proper, distinct on-Windows runs are a follow-up). |
| **macOS** | host | Runs the timed portion on whatever OS invoked the script. Docker can't run macOS containers, so on macOS the test executes against the developer's actual host shell. |

On macOS specifically, **both modes work** — Docker Desktop runs Linux containers on Apple Silicon. Host mode is the *macOS-coverage* path; docker mode on macOS just re-exercises the Linux path from a Mac.

## What this smoke test does test

The end-to-end install → first-real-command path:

- **Documented prereq install on a fresh OS** — apt + NodeSource + `uv` install script + GitHub's `gh` apt repo. If any of these stop working (broken URL, missing key, removed package), docker mode catches it.
- **`npx <ref>` runs to completion** — the install procedure consumers actually invoke. `bin/install.mjs` executes against a fresh tempdir with no prior stride footprint.
- **Skill markdown landed** — checks `.claude/commands/linear/start.md` exists. Catches partial installs where the install crashed midway.
- **Hook landed and is executable** — checks `.claude/hooks/do_commit.sh` is in place. Without it `/commit` is broken.
- **Python tool chain works end-to-end** — `uv run` resolves the PEP 723 deps (`click`, `requests`), `linear.py` imports cleanly, `bearer_token()` resolves an API key, the GraphQL endpoint responds, auth succeeds.
- **Both auth entry points** — the timed probe authenticates via `LINEAR_API_KEY` in the environment; a second untimed probe writes a `.linear_project` naming an `api_key_env`, unsets `LINEAR_API_KEY`, and confirms `token_from_project_config()` resolves the key from the named var. That's the config-file path most real users hit, now exercised on the install path rather than only in unit tests.
- **90-second wall-clock budget** — the criterion this whole script exists to measure. `STRIDE_SMOKE_BUDGET_SECONDS=-1` forces a FAIL for testing the failure path itself.

## What this smoke test does not test

Honest gaps. Some are out of scope, some are follow-ups, all are worth knowing:

- **Silent prompt drift in `install.mjs`** — we pipe `printf 'y\n' x 10` blindly to accept defaults. If a new interactive prompt is added to `install.mjs` and the printf count isn't updated, the install still completes but skips the new prompt's intended choice. No alarm fires here.
- **Re-install / orphan prune** — runs against a fresh tempdir every time. The on-re-install file pruning behaviour (introduced in WB-447) is not on the smoke path. A regression that broke prune-on-re-install would pass here.
- **Claude Code itself doesn't run** — we prove the bytes for `/linear:start` are on disk; we don't prove Claude Code finds and invokes them. Closing that gap needs a Claude Code integration harness, not a shell smoke test.
- **OAuth path** — explicit Epic B scope (WB-458). The smoke test exercises only the PAT path until OAuth lands.
- **Native Windows runs** — covered transitively via WSL2, not natively. If a real on-Windows-without-WSL2 user surfaces a path-separator or CRLF bug, the smoke test won't catch it.

## Environment variables

| Variable | Default | Purpose |
|:---------|:--------|:--------|
| `LINEAR_API_KEY` | *(required)* | PAT for the test workspace. The script refuses to run without it. |
| `STRIDE_SMOKE_MODE` | `docker` | `docker` runs container.sh in `ubuntu:24.04`; `host` runs the timed portion on the caller's OS. |
| `STRIDE_SMOKE_BUDGET_SECONDS` | `90` | Tighten for CI regression hunting (e.g. push the bar to 75 next quarter). Set to `-1` to force a FAIL for testing the failure path. |
| `STRIDE_SMOKE_REF` | `github:webventurer/stride` | What `npx --yes` installs. Override with `github:webventurer/stride#branch-name` to smoke-test a branch before merge. |
| `STRIDE_SMOKE_IMAGE` | `ubuntu:24.04` | Base image for docker mode. Override to test under a different LTS (e.g. `ubuntu:22.04`). Ignored in host mode. |

## When this fires

Today: **locally only**. Run it before merging a change that touches install plumbing (`bin/install.mjs`, prereq lists, the Python tool bootstrap, the auth chain) or before cutting a release.

Deferred: a `.github/workflows/onboarding-smoke.yml` that runs this on every release in CI. Requires a `LINEAR_TEST_API_KEY` GitHub secret and a Linear test workspace — both out-of-scope for the issue that introduced the script.

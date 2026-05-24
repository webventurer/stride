# Linear MCP vs Linear CLI

## CLI vs MCP

CLIs are eating MCPs. The industry is converging on the very same idea. MCPs for all their merit can be token hungry, slow, and unreliable for complex tool chaining. However, coding agents have become incredibly good at working with CLIs, and in fact they are far more comfortable working with CLI tools than MCP.

## The bigger pattern across r/Linear

The strongest recurring theme isn't "which CLI" — it's "move off Linear MCP because of context bloat." One representative quote: *"GitHub, Linear, Playwright MCPs can consume 60,000 tokens before the conversation even begins. This seriously degrades LLM's ability to reason."* Several people describe a pattern of "start with MCP enabled so the agent can see the connections, ask it to build a custom CLI, then remove the MCP." That's the meta-recommendation right now.

Worth flagging since you've already got `linear-webventurer` MCP wired into `.mcp.json` — the people writing this advice are running into exactly your setup.

## Research from Reddit

### Recommendation by use case

| Your situation | Pick |
|:---|:---|
| Driving Linear from Claude Code / agent workflows (your case in this repo) | **dorkitude/linctl** — explicitly built for this; most mentions; consistently recommended over MCP for context efficiency |
| Mature, terminal-focused human use (jump to issue, create PR with Linear context) | **schpet/linear-cli** — the elder, most often cited as "robust" |
| JSON-out CLI that an agent calls as a skill, with GraphQL fallback | **czottmann/linearis** |
| Maximum token efficiency in agent context | **joa23/linear-cli** |

## Bottom line

For most people, **linctl** looks like the best dedicated Linear CLI for Claude workflows right now, because it's purpose-built for agents like Claude Code and is designed around issue listing, creation, and workflow actions from the terminal.

## Spike findings (WB-391)

Measured on macOS Apple Silicon, 2026-05-23, with `linctl 0.1.8` against four stride-linked Linear workspaces.

### What works

- **Multi-workspace via env-var prefix** — `LINCTL_API_KEY=$LINEAR_<TEAM>_API_KEY linctl whoami` cleanly switches between Webventurer (`WB`), Personal (`MIK`), and Wordtracker (`WD`) workspaces. Each returns its own team UUID and issue count. No `~/.linctl-auth.json` persistence needed; one-line prefix per invocation works.
- **`sortOrder` mutation via raw GraphQL** — `linctl graphql 'mutation { issueUpdate(id: ..., input: { sortOrder: ... }) { success issue { sortOrder } } }'` works. Confirmed by reading-then-rewriting WB-391's `sortOrder` at value 36 (idempotent no-op). This gives us the **WB-388 outcome for free** — no Python-client extension needed if we migrate.
- **`--json` output** — issue read returns 12KB clean structured JSON; `issue list --newer-than 1_week_ago` returns 117KB. Same data MCP would surface, no schema preamble.
- **Latency** — read operations 170–220ms, network-bound to `api.linear.app`. Comparable to MCP per call; the CLI binary itself adds <10ms.

### What doesn't work / costs

- **Install footprint is 240MB, not 10MB.** `brew install linctl` on macOS ARM pulled Go 1.26.3 (228.6MB) as a build dependency *and* the linctl binary (9.9MB). The tap doesn't publish pre-built bottles for Apple Silicon, so brew compiles from source. The Go install persists. This is a real cost the README doesn't telegraph.
- **`brew install linctl` violates the Vision constraint** *"Plain markdown only — no runtime, no build step, no compiled binaries"* — not in stride's footprint, but in **stride consumers'**. Migrating to linctl means every stride user runs `brew install linctl` to use `/linear:*` skills. Not the same as a runtime *in* stride, but it's a runtime *next to* stride that stride now requires.

### Migration surface area

| Skill file | MCP call sites |
|:---|---:|
| `plan-work.md` | 14 |
| `finish.md` | 8 |
| `next-steps.md` | 6 |
| `start.md` | 5 |
| `fix.md` | 2 |
| `list-projects.md` | 1 |
| `update-vision.md` | 1 |
| **Total** | **37 across 7 files** |

Eight unique MCP tools referenced: `get_issue`, `list_issues`, `list_comments`, `list_projects`, `list_issue_statuses`, `list_milestones`, `save_issue`, `save_comment`. Each has a roughly direct linctl equivalent (`linctl issue get`, `linctl issue list`, `linctl comments list`, etc.) plus `linctl graphql` as the escape hatch for anything not covered (`list_milestones` may need this).

Moderate migration. One focused session at the larger files (`plan-work.md`, `finish.md`), one for the rest.

### Token economy

Not directly measurable from inside the spike session, but the structural argument holds:

- MCP session pays a one-time schema-load cost per Linear server (the r/Linear figure is ~60k tokens for the Linear MCP alone). With four `linear-*` servers wired in `.mcp.json`, the cost is multiplied — though only servers actually called in the session matter for the LLM's working memory.
- linctl pays *nothing* up front. Each bash call is a one-shot input/output pair.
- For a typical `/linear:start → /linear:finish` cycle (5–10 MCP operations), linctl saves roughly the schema-load cost — call it ~60k tokens — leaving the agent that much more headroom to reason.

### Decision

**Lean migrate, but the install cost is a Vision-level decision that must happen first.**

The agent-experience win is real and measurable in principle (token economy + same per-call latency). The migration is moderate. The win directly serves *"The common path through every `/linear:*` command runs without prompts; interruptions appear only when stride detects friction worth the user's judgement"* — schema bloat IS friction, just at the substrate level rather than the workflow level.

But: `brew install linctl` adds a 240MB Go-toolchain install to every stride consumer's machine. That fights *"Plain markdown only — no runtime, no build step, no compiled binaries"* in spirit even if stride's own footprint stays markdown.

**Recommended sequence:**

1. **First, evolve the Vision** — relax the constraint to read something like *"Plain markdown only in stride's own footprint. Consumer-side prerequisites must be lightweight binaries with one-step install paths."* That's the gating decision; without it, migration goes against the project's stated purpose.
2. **Then file the migration follow-ups** — (a) replace MCP calls in `/linear:*` skills with linctl invocations, (b) document `brew install linctl` (and the Go dependency) as a stride prereq, (c) deprecate `.claude/tools/linear_client.py` once no skill imports it, (d) close WB-388 (sortOrder kwarg) as superseded.
3. **WB-385 (`/linear:quick`) is unaffected** — it still wants ship-then-file behaviour; just calls linctl instead of MCP.

**If the Vision evolution doesn't pass:** keep MCP + `linear_client.py`. WB-388 stays in play. The schema-bloat cost remains but is an acceptable trade against the install-footprint constraint.

### End-to-end path benchmark (WB-393)

Measured 2026-05-24, WB workspace, against the same 6-step path that `/linear:start → /linear:finish` walks: **create → get → move to In Progress → comment → move to Done → cancel**. linctl runs the whole sequence in one scripted bash call (one agent round-trip); MCP needs one tool call per step (six agent round-trips).

| | `linctl` (1 round-trip) | MCP (6 round-trips) |
|:---|---:|---:|
| Runs (s) | 2.78 / 2.85 / 3.53 / 10.53 / 10.96 / 14.71 / 16.04 | 24.02 / 24.95 / 33.87 |
| **Median** | **10.53s** | **24.95s** |
| Min–max | 2.78–16.04 | 24.02–33.87 |
| Speed-up at median | **~2.4×** | — |

**The win is round-trip collapsing, not a faster API.** Both tools hit the same Linear backend at the same per-op latency (~0.5–2.5s/op, which is why linctl's time is bimodal). linctl wins because the agent scripts all six ops into a single bash call — one model turn — while MCP forces six model turns. Those five extra turns are a fixed ~20s tax that no network speed removes. The distributions **never overlap**: linctl's slowest run (16.04s) still beats MCP's fastest (24.02s).

**Caveat — this is linctl's best light.** The 2.4× holds wherever the agent can script the whole sequence up front (the mechanical guts of `/start` and `/finish`). At a human-gated step (`/plan-work` waiting for approval), both tools take one round-trip and the gap collapses to the per-op API difference.

**Reliability edge.** Across these runs, MCP `save_issue` accepted `state: "In Progress"` and **silently no-opped** (returned `Backlog`, no error); `Done`/`Canceled` applied. linctl resolved every state by name correctly. State transitions are the most error-prone Linear operation in the workflow, so this matters beyond speed.

### What stayed unchanged

- `.mcp.json` — Linear MCP servers still configured; spike didn't touch them.
- `.claude/tools/linear_client.py` — vendored module untouched on main.
- The Rust CLI (Finesssee/linear-cli) — not tested; remains the fallback option if linctl's `brew install` cost is a blocker and we want a `cargo install` alternative (which is *also* a runtime — same constraint problem, different package manager).

---

## Linear CLIs surveyed

- **linctl** — <https://github.com/dorkitude/linctl>
- **linear-cli** (schpet) — <https://github.com/schpet/linear-cli>
  - <https://www.claudepluginhub.com/marketplaces/schpet-linear-cli>
  - <https://crates.io/crates/linear-cli/0.3.8>
  - <https://github.com/Finesssee/linear-cli>
- **Composio** — <https://composio.dev/toolkits/linear/framework/cli>
- **Linearis** — <https://github.com/linearis-oss/linearis>
  - <https://zottmann.org/2025/09/03/linearis-my-linear-cli-built.html>
- **Linear developers** — <https://linear.app/developers>

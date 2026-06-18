# Vision: stride

> Apply guardrails, not walls. Encourage discipline but don't obstruct flow.

## What it delivers

Manage your own dev team on a Kanban board so everything's visible — except the team is AI.

stride turns AI speed into maintainable codebases. It gives Claude Code the discipline of atomic commits, a Linear-tracked story flow, and a shared vocabulary for sizing work. Plain markdown into `.claude/` — no runtime, no lock-in.

The result: a `git log` you can trust, a kanban board that reflects reality, and a codebase that stays navigable as it grows.

## Who it's for

Developers using Claude Code who care about codebases that survive past day 30 — solo builders, small teams, anyone running a real project. Explicitly *not* for vibe coders who want a working demo in an hour and never plan to touch it again — stride's setup friction would be pure cost in that case.

## Why it exists

Vibe coding feels best on day one. By day ten you can't tell which change broke things. By day thirty you're afraid to touch anything. By day ninety you're rewriting from scratch.

The problem isn't AI speed — it's the absence of structure around it. stride trades a few minutes of setup for months of maintainability, and the structure compounds: as AI models improve, structured docs get *more* from them, not less.

Structure doesn't have to mean obstruction. Stride's discipline is shaped as guardrails — they steer, they don't block. The common path runs without prompts; friction appears only where it carries signal worth your judgement.

## Why now

AI coding agents are improving fast, and the structure-vs-speed trade-off compounds with model quality: every model improvement gives more leverage to a structured codebase than to a vibe-coded one. Every month without structure is a month of debt that gets harder to undo — by day 30, untangling costs more than rewriting.

## Success criteria

- [ ] When new work strains against older criteria, the Vision can be updated to reflect what was learned — `VISION.md` evolves with the work, not separately from it
- [ ] You can improve stride through using it — friction hit while working *in* the project can be surfaced, fixed, and used *on* the project within the same session, so the tool compounds
- [ ] Every commit on a stride-managed branch passes four-pass atomicity — no monolithic commits, every message explains *why*
- [ ] Right tool for right job: every branch in a stride skill points at the artifact designed for its case — story drafts to `story.md`, epic drafts to `epic.md` — and never falls back to a generic "whatever's around" default
- [ ] Stride's command files (`.claude/commands/*.md`) stay scannable as they grow — a reader can locate a step, rule, or flag in seconds, not minutes
- [ ] Every `/linear:*` command produces the output its own spec documents — a documented column, sort, or field shows real data, never a silent blank or arbitrary order
- [ ] You can predict how stride will behave by reading the repo, not by knowing hidden rules — a default that changes behaviour is materialised in the file it governs (e.g. `.stride.json`'s `focus`), so the active behaviour is inspectable on disk, never knowable only from prose or fallback code
- [ ] The common path through every `/linear:*` command runs without prompts; interruptions appear only when stride detects friction worth the user's judgement
- [ ] You can review your working changes at any point without leaving the flow — `/linear:start` surfaces the diff at its review step, and (with diffity installed) `/diffity-diff` opens a visual diff on demand
- [ ] Parallel work streams run without leaving the editor — `--worktree` prepares a worktree you open as a terminal in the current VS Code window, so multiple cards run side by side without alt-tabbing between windows
- [ ] Every multi-step stride interaction discloses its scope upfront — number of steps, time estimate, escape hatch — so the user is never trapped in an open-ended sequence
- [ ] When you list the commits this branch is adding, the story reads naturally to a non-engineer scanning top-to-bottom (`git log main..HEAD --oneline` to check)
- [ ] Issue titles read as stakeholder outcomes, not implementation steps
- [ ] The card moves through Backlog → Doing → In Review → Done as `/linear:*` runs — no manual clicks on the board
- [ ] Stories with a shared purpose sit under one epic, and the epic traces back to a Vision outcome
- [ ] `git bisect` on a stride branch finds a regression in fewer than 5 commits
- [ ] stride's tests exercise the real code under test, never a reimplemented copy — so a regression in the real code fails the suite instead of passing green against a stale duplicate
- [ ] stride's own Python tooling stays consistently formatted and lint-clean — tidied on demand with a single command, never enforced on the commit path, so housekeeping stays cheap and off the critical path
- [ ] After `/linear:update-vision` runs, the Linear project description matches `VISION.md`
- [ ] `npx github:webventurer/stride` installs in under 30 seconds, no global side effects
- [ ] Setup gets a fresh user from `npx` to their first successful `/linear:start` in under 90 seconds on any supported OS. Authentication uses a Personal API Key in `~/.env`, feeding a single code path through every command. No external CLI dependencies that require building from source.
- [ ] Onboarding wall-clock time is measured by a smoke-test that runs end-to-end against a clean container on each release. A run that exceeds 90 seconds blocks the release until the regression is identified.
- [ ] Install is verified on macOS (Apple Silicon), Ubuntu LTS, and Windows-via-WSL2. Each supported OS has a tested install path that runs without compiling dependencies from source.
- [ ] The prereq-doctor names every missing prerequisite — tools to install **and** permissions to request — with the exact remediation step (a command, a Linear docs link, or a message template for the user to send their admin).

## What can't change

- Currently Claude Code is the only supported AI agent — AgentSDK integration would unlock others
- Plain text in stride's own footprint — markdown skills plus a small Python helper, no build step, no compiled binaries inside `.claude/`. Consumer-side prerequisites (e.g. `gh`, `uv`, `jq`) are acceptable when they're lightweight and install in a single step.
- Linear only — no Jira, no GitHub Projects support
- `npx` install — consumers need npm
- Bash/zsh required for hooks (Windows requires WSL)
- Opinionated: prescribes Linear, commit format, workflow. Disagreeing means fighting the tool

## What it won't do

- **Not a project orchestrator.** stride manages stories, not multi-sprint roadmaps. Autonomous loops and vision-refinement cycles belong in a separate tool
- **Not a vibe-coding accelerator.** stride adds friction up front for compounding returns by day 30+
- **Not installed globally.** Everything lives in the consumer's `.claude/` — no machine-wide state
- **Not lock-in.** Read the markdown, change it, fork it, remove it
- **Not replacing PR review.** stride structures the steps *before* review, not the review itself

---

*Generated via [`/vision`](docs/skills/vision.md). Re-run to evolve.*

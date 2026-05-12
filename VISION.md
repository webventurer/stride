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
- [ ] Every commit on a stride-managed branch passes four-pass atomicity — no monolithic commits, every message explains *why*
- [ ] Right tool for right job: every branch in a stride skill points at the artifact designed for its case — story drafts to `ISSUE-TEMPLATE.md`, epic drafts to `EPIC-TEMPLATE.md` — and never falls back to a generic "whatever's around" default
- [ ] The common path through every `/linear:*` command runs without prompts; interruptions appear only when stride detects friction worth the user's judgement
- [ ] Every multi-step stride interaction discloses its scope upfront — number of steps, time estimate, escape hatch — so the user is never trapped in an open-ended sequence
- [ ] When you list the commits this branch is adding, the story reads naturally to a non-engineer scanning top-to-bottom (`git log main..HEAD --oneline` to check)
- [ ] Issue titles read as stakeholder outcomes, not implementation steps
- [ ] The card moves through Backlog → Doing → In Review → Done as `/linear:*` runs — no manual clicks on the board
- [ ] Stories with a shared purpose sit under one epic, and the epic traces back to a Vision outcome
- [ ] `git bisect` on a stride branch finds a regression in fewer than 5 commits
- [ ] After `/linear:update-vision` runs, the Linear project description matches `VISION.md`
- [ ] `npx github:webventurer/stride` installs in under 30 seconds, no global side effects

## What can't change

- Currently Claude Code is the only supported AI agent — AgentSDK integration would unlock others
- Plain markdown only — no runtime, no build step, no compiled binaries
- Linear via MCP — no Jira, no GitHub Projects support
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

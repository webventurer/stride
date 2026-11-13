# Vision: stride

> Apply guardrails, not walls. Encourage discipline but don't obstruct flow.

## What it delivers

Manage your own dev team on a Kanban board so everything's visible — except the team is AI.

stride turns AI speed into maintainable codebases. It gives your coding agent the discipline of atomic commits, a Linear-tracked story flow, and a shared vocabulary for sizing work — Claude Code, Codex, Gemini, or any CLI that speaks the same open standards. Plain markdown, authored once in `.claude/` and generated out to whichever tool you run — no runtime, no lock-in.

The result: a `git log` you can trust, a kanban board that reflects reality, and a codebase that stays navigable as it grows.

### The principle

**Speed up whenever you can, but never at the cost of quality. Scheduling is stride's job, not yours. Every finished card teaches the next ones.**

In practice that means four things:

- **Fast:** cards that don't depend on each other run side by side, and a card waiting on another holds back until that card is done.
- **Quality:** a card in a batch gets every check it would get on its own.
- **No scheduling for you:** you decide what goes in Todo. Stride decides the order and how many run at once.
- **Agile:** take a small step, see what it taught you, and change the plan before the next step.

## Who it's for

Developers driving an AI coding CLI (Claude Code, Codex, Gemini, or the next one) who care about codebases that survive past day 30 — solo builders, small teams, anyone running a real project. Explicitly *not* for vibe coders who want a working demo in an hour and never plan to touch it again — stride's setup friction would be pure cost in that case.

## Why it exists

Vibe coding feels best on day one. By day ten you can't tell which change broke things. By day thirty you're afraid to touch anything. By day ninety you're rewriting from scratch.

The problem isn't AI speed — it's the absence of structure around it. stride trades a few minutes of setup for months of maintainability, and the structure compounds: as AI models improve, structured docs get *more* from them, not less.

Structure doesn't have to mean obstruction. Stride's discipline is shaped as guardrails — they steer, they don't block. The common path runs without prompts; friction appears only where it carries signal worth your judgement.

## Why now

AI coding agents are improving fast, and the structure-vs-speed trade-off compounds with model quality: every model improvement gives more leverage to a structured codebase than to a vibe-coded one. Every month without structure is a month of debt that gets harder to undo — by day 30, untangling costs more than rewriting.

## Success criteria

- [ ] When new work strains against the Success criteria, the Vision is updated with what was learned, so it evolves with the work
- [ ] Work is filed against a criterion it plainly serves, and when none fits without stretching, stride stops and says so before merging
- [ ] Every skill and command stride installs is described where a reader looks, with the same counts in the README, the docs site and the installer
- [ ] Stride's code and the examples in its docs follow one house style, so an agent reading either learns one way to write code
- [ ] Friction hit while working on stride can be surfaced, fixed and used within the same session, so the tool improves as you use it
- [ ] Every commit on a stride-managed branch does one job, with no monolithic commits, and its message explains why
- [ ] What ships is the simplest thing that works: before you review a change, a reviewer who never saw the reasoning names what to delete
- [ ] What merges does what its card promised: before merge, a reviewer who never saw the reasoning checks it, and any gap is fixed
- [ ] A card is never quietly rewritten to match the work: a revision needs your sign-off, or a note when behaviour and every ask stay unchanged
- [ ] Every case in a stride skill points at the artifact made for that case, such as the story template, never a generic fallback
- [ ] Stride's command files stay scannable as they grow, so a reader finds a step, rule or flag in seconds, not minutes
- [ ] Every `/linear:*` command shows what its own spec documents, so each column, sort and field holds real data, never a silent blank or arbitrary order
- [ ] You can predict stride's behaviour from the repo: a default that changes behaviour sits in the file it governs, not hidden in prose or code
- [ ] The common path through every `/linear:*` command runs without prompts; interruptions appear only when stride detects friction worth the user's judgement
- [ ] You can review your working changes at any point without leaving the flow
- [ ] Cards worked side by side each get a terminal in your current editor window, so you never switch between windows
- [ ] Cards in Todo reach Done as fast as they can, side by side where possible, without skipping a check or making you schedule them
- [ ] A lost network connection costs a batch a retry, not a job: a cut-off job resumes, and one that can't is reported as failed
- [ ] Every finished card teaches the next ones: before the next starts, its lessons are read and any Todo card they change is reworded, saying why
- [ ] Every multi-step stride interaction says upfront how many steps, how long, and how to stop, so you're never trapped in an open-ended sequence
- [ ] A branch's commit list, read top to bottom, tells a story a non-engineer can follow
- [ ] Anyone who doesn't know stride's commands or code can understand every Linear card: an outcome in its title, everyday words in its description and updates
- [ ] A card's problem and fix are checked against the code and anything it cites before drafting, so nobody starts a plan the code rules out
- [ ] A card reaches the board only with evidence it will move the needle, and what was left out is named in one line
- [ ] The card moves through Backlog → Doing → In Review → Done as `/linear:*` runs — no manual clicks on the board
- [ ] Stories with a shared purpose sit under one epic, and the epic traces back to a Vision outcome
- [ ] `git bisect` on a stride branch finds a regression in fewer than 5 commits
- [ ] stride's tests run the real code, never a copy, so a regression in the real code fails the suite
- [ ] stride's own Python tooling stays formatted and lint-clean through one command run on demand, never a check on the commit path
- [ ] After `/linear:update-vision` runs, the Linear project description matches `VISION.md`
- [ ] `npx github:webventurer/stride` installs in under 30 seconds, no global side effects
- [ ] Setup takes a fresh user from `npx` to a first successful `/linear:start` in under 90 seconds on any supported OS
- [ ] Every command authenticates through one Personal API Key in `~/.env`, and no setup step builds a dependency from source
- [ ] The same story flow, bare-commit block included, runs from any supported CLI, generated at install time from the one `.claude/` source
- [ ] Stride's guardrails reach the agent from any folder: the design principles arrive with every prompt and a bare `git commit` is still blocked
- [ ] Each release runs an end-to-end onboarding test in a clean container, and a run over 90 seconds blocks the release until the cause is found
- [ ] Install is tested on macOS (Apple Silicon), Ubuntu LTS and Windows via WSL2, each without compiling dependencies from source
- [ ] The prerequisite check names every missing tool or permission with the exact fix: a command, a Linear docs link, or a message for your admin

## What can't change

- A CLI is supported only where it already implements the open standards stride targets — Agent Skills, `AGENTS.md`, lifecycle hooks — and only through install-time generation. `.claude/` is the authoring source of truth: no hand-maintained second tree, no symlinks, no per-tool fork
- Plain text in stride's own footprint — markdown skills plus a small Python helper, no build step, no compiled binaries inside `.claude/`. Consumer-side prerequisites (e.g. `gh`, `uv`, `jq`) are acceptable when they're lightweight and install in a single step.
- Linear only — no Jira, no GitHub Projects support
- `npx` install — consumers need npm
- Bash/zsh required for hooks (Windows requires WSL)
- Opinionated: prescribes Linear, commit format, workflow. Disagreeing means fighting the tool

## What it won't do

- **Not a project orchestrator.** You decide what work exists and which cards go in Todo; stride ships the cards in Todo, in the best order it can find, and never adds cards to the board or decides by itself what to work on. Multi-sprint roadmaps and planning loops belong in a separate tool
- **Not a vibe-coding accelerator.** stride adds friction up front for compounding returns by day 30+
- **Not installed globally.** Everything lives in the consumer's repo — `.claude/` plus whatever per-tool footprint is generated beside it — no machine-wide state
- **Not lock-in.** Read the markdown, change it, fork it, remove it
- **Not replacing PR review.** stride structures the steps *before* review, not the review itself

---

*Generated via [`/vision`](docs/skills/vision.md). Re-run to evolve.*

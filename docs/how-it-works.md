# How it works

stride installs as plain markdown files in your project's `.claude/` directory. No runtime dependencies, no build step — Claude Code reads the files and follows the instructions.

## What gets installed

```
your-project/
├── VISION.md                # Project anchor — what it delivers, why,
│                            # Success criteria. Every issue traces back
└── .claude/
    ├── skills/
    │   ├── vision/          # /vision skill
    │   │   └── SKILL.md     # Seven-question walkthrough → VISION.md
    │   ├── commit/          # /commit skill
    │   │   ├── SKILL.md     # Principles, coherence test, atomicity rules
    │   │   └── WORKFLOW.md  # Four-pass execution sequence
    │   └── craft/           # /craft skill
    │       └── SKILL.md     # CRAFT prompt framework
    ├── commands/
    │   └── linear/          # /linear:* commands
    │       ├── start.md     # Implement an issue
    │       ├── finish.md    # Merge + mark Done
    │       ├── fix.md       # Address PR feedback
    │       ├── plan-work.md # Create + refine issues
    │       └── next-steps.md# Show priorities
    ├── docs/                # Foundational knowledge
    │   ├── concepts/        # Core ideas (atomicity, SRP)
    │   ├── patterns/        # Reusable approaches (git patterns)
    │   └── principles/      # Guiding rules
    └── hooks/               # Safety enforcement
        └── do_commit.sh     # Commit wrapper
```

`VISION.md` lives at the repo root, not under `.claude/` — it's a stakeholder-readable artefact, not a Claude Code internal. The `/vision` skill writes it; the `/linear:*` commands read it as the anchor for every issue, ranking, and implementation decision.

## The three layers

### 1. Knowledge (`.claude/docs/`)

Foundational concepts the agent needs to understand *why* things work a certain way. The commit skill references `atomic-git-commits.md` as required reading — without it, the agent would follow rules without understanding the reasoning behind them.

### 2. Skills and commands (`.claude/skills/`, `.claude/commands/`)

Executable instructions the agent follows step by step. Each skill has:

- **SKILL.md** — the principles, decision rules, and reference material
- **WORKFLOW.md** — the exact execution sequence

**Skills** live in `.claude/skills/` and are invoked directly (`/commit`, `/craft`). A skill has its own `SKILL.md` (principles and rules) and `WORKFLOW.md` (execution steps) — it's a self-contained methodology the agent internalises.

**Commands** live in `.claude/commands/` and are namespaced (`/linear:start`, `/linear:finish`). Each command is a single markdown file describing one discrete action. Commands are grouped by integration — all five Linear commands share context but execute independently.

The distinction: a skill teaches the agent *how to think* about a problem (atomic commits, prompt crafting). A command tells the agent *what to do* in a specific situation (start an issue, merge a PR).

### 3. Safety (`.claude/hooks/`)

Hooks that enforce discipline at the tool level:

- Block bare `git commit` — forces use of the `/commit` skill
- Run security checks on file edits
- Validate formatting standards

**Important:** the hooks are shell scripts. If they fail silently (permissions, wrong shell, Windows without WSL), the safety net disappears — the agent will use bare `git commit` without the four-pass methodology. See the [install guide's known limitations](/install#hook-scripts-require-bash) for how to verify they're working.

## The `/commit` four-pass methodology

When you run `/commit`, the agent doesn't just stage and commit. It runs four distinct passes, each with a different cognitive focus:

| Pass | Focus | What it catches |
|:-----|:------|:----------------|
| **Pre-flight** | Formatting, change inventory | Files grouped by session instead of by purpose |
| **Content** | Selective staging, coherence | Hitchhiker files that don't belong to this change |
| **Standards** | Message format, checklists | Missing prefix, "and" in the subject, wrong mood |
| **Review** | Sanity check, verification | Last chance to catch anything before it lands |

The separation matters because of **content focus blindness** — both people and AI consistently miss formatting standards while focused on content logic. Dedicated passes prevent this.

## The `/linear` five-command lifecycle

The five commands map to how work actually moves through a board:

```
/linear:plan-work  →  create an issue
/linear:next-steps →  see what needs doing
/linear:start      →  branch, implement, PR
/linear:fix        →  address review feedback
/linear:finish     →  merge, clean up, Done
```

Each command knows about Linear statuses, GitHub PRs, and git branches. The agent moves issues through Backlog → Todo → Doing → In review → Done automatically as work progresses.

Issues come in two sizes: **stories** (one PR) or **epics** (a parent issue with sub-issues, when several stories serve a common purpose smaller than the Vision). `/linear:plan-work` asks the sizing question and routes accordingly. See [Epics and stories](/reference/epics-and-user-stories) for the full mapping.

## Review on the fly

`/linear:start` has a built-in review checkpoint — it opens the new PR's diff (in diffity, when installed) before you approve. But you don't have to wait for it: **`/diffity-diff` opens a visual diff of your working tree at any point**, so you can review your changes whenever you want, not only when stride prompts you.

The full diffity command family — all run against your local repo; most open a view in the browser, while the resolve commands read comments and edit your code:

| Command | What it does |
|:--------|:-------------|
| **`/diffity-diff`** | Open the diff viewer on your working-tree changes (or any ref / PR URL). |
| **`/diffity-review`** | Get an AI code review of the current diff, left as inline comments in the viewer. |
| **`/diffity-resolve`** | Read the open comments on the diff (yours or the review's) and make the code fixes. |
| **`/diffity-tree`** | Browse the whole repo as a file tree and comment on any file — not just what changed. |
| **`/diffity-resolve-tree`** | Read the comments left in the tree browser and make the code fixes. |
| **`/diffity-tour`** | Create a guided, step-by-step walkthrough of the codebase to answer a question or explain a feature, with highlighted code. |
| **`/diffity-learn`** | Start a project-driven learning journey for a technical topic — taught through real projects and tours, at your pace. |

The first five stay within review — view a diff, browse the whole repo, leave comments (by hand or via the AI review), and resolve them. The last two go beyond review into code tours and guided learning.

The `/diffity-diff` path and the checkpoint are complementary — `/diffity-diff` for on-demand review of uncommitted work mid-implementation, the `/linear:start` checkpoint as the gate before a PR ships. (Jumping straight to `/linear:finish` skips that checkpoint's auto-open, so `/diffity-diff` is how you review on your own terms regardless.) It's for reviewing your own working changes in-flow — not a replacement for formal PR review. diffity is optional; see the [install guide](/install) for setup.

## The cross-model feedback loop

`/linear:plan-work` optionally sends issue drafts to ChatGPT via OpenRouter for a second opinion before creating the issue. Three voices — Claude proposes, ChatGPT challenges, you steer — sharpen the issue through cross-model perspectives.

This requires an OpenRouter API key. See the [install guide](/install) for setup.

## What the install script does

When you run `npx github:webventurer/stride`, the script (`bin/install.mjs`) does four things:

1. **Copies files** into your project's `.claude/` directory — skills, commands, hooks, tools, and supporting docs. Never writes outside `.claude/`
2. **Sets permissions** — makes hook scripts (`do_commit.sh`, `block_bare_git_commit.sh`) executable
3. **Merges settings** — if you already have a `.claude/settings.json`, it asks before merging. If you say no, nothing is touched. If you don't have one, it creates a minimal config with the commit hook wired up
4. **Prints a summary** — shows what was installed and which commands are available

The merge is additive — it adds stride's hooks alongside your existing config using a deep merge with deduplication. It never removes or overwrites your existing settings.

**If something goes wrong:** the script only writes under `.claude/`. Run `stride-uninstall` or delete the installed subdirs to remove everything. There are no global side effects.

## Customising

The "no lock-in" promise means you can change anything. Here's what's safe to edit and what to be careful with:

| What | Safe to edit? | Notes |
|:-----|:--------------|:------|
| Commit prefixes | Yes | Edit `.claude/skills/commit/SKILL.md` — change the prefix table |
| Commit message rules | Yes | Edit `SKILL.md` and `WORKFLOW.md` — your rules, your standards |
| Linear command behaviour | Yes | Edit files in `.claude/commands/linear/` — each command is a standalone markdown file |
| Hook scripts | Yes | Edit or remove scripts in `.claude/hooks/` — update `settings.json` to match |
| Foundational docs | Yes | Edit `.claude/docs/` — these shape the agent's understanding |
| Settings deny list | Yes | Add your own deny rules to `.claude/settings.json` |
| Adding new skills | Yes | Create a new directory under `.claude/skills/` with a `SKILL.md` — Claude Code auto-discovers it |

**Pulling upstream updates:** there's no automatic upgrade path. If you want to pick up changes from stride, re-run the install script — it will overwrite files but won't remove your additions. For heavy customisation, fork the repo and maintain your own version.

## Why markdown

Every file is readable, editable, and version-controlled. You can:

- **Read** the full methodology before installing
- **Customise** any rule or workflow to match your team's standards
- **Fork** the skills and evolve them independently
- **Review** changes to the skills in pull requests, just like code

There's no black box. The agent's instructions are your instructions.

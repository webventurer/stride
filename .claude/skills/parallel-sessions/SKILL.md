---
name: parallel-sessions
description: Run a batch of independent jobs (captures, transcripts, reviews, audits) as parallel side sessions, a set number at a time, each committing only its own work. Use when the user has several jobs that don't depend on each other and wants them run at once. Triggers on "parallel sessions", "run these in parallel", "batch these jobs", "side sessions".
---

# Parallel sessions

> Start every job's session on one "go" from the user, and let the sessions queue themselves through a fixed number of slots, so no more than N run together and each commits only its own files.

---

## The governing principle

> Independent jobs run as parallel sessions, a set number at a time, each committing only its own work.

---

## When to use

- The user has several jobs that don't depend on each other: recordings to capture, notes to transcribe, docs to review
- Each job's output is a set of paths that can be named before the job starts

## When NOT to use

- The jobs depend on each other's results: run them in order instead
- One job, or jobs small enough to finish in this session

---

## Quick reference

<mark>**Settle the batch and wait for "go", start every session in one turn, and let the slot store hold the limit.**</mark> A session that can't claim a slot waits and retries; the coordinator releases the slot of a session that exits, and a claim that is never renewed lapses as the backstop, so the batch never jams.

| Piece | What it does |
|:------|:-------------|
| **The coordinator** | This session: settles the batch, shows it for "go", writes each brief, starts every job session in one turn, hears from each, checks each commit, sends work back and reports |
| **A job session** | Claims a slot, does its one job, commits only its named paths, messages the coordinator when its work is ready, releases the slot, and stops once the coordinator says its work is done |
| **The slot store** | One folder for the whole batch; [`scripts/slots.py`](scripts/slots.py) claims, renews, releases and shows the slots |

---

## Process

### 1. Settle the batch

Before anything starts, settle the six things every batch needs. Take what the user's message already says, and ask about the rest in one question:

| What | Example |
|:-----|:--------|
| **The mission** | What the batch is for and the limits it must keep, in the user's words, such as "get the shop ready to sell in euros; existing stock files keep loading". Take it from the user's message; when the message gives none, the job is the mission |
| **The job** | The skill or instructions each session runs, such as `/capture-recording` on one recording |
| **The items** | The folders or files, one job each |
| **How many at once** | Suggest 3 |
| **The mode** | Shared checkout or one worktree per job; suggest one from the table below |
| **The model** | One per job: Sonnet for focused work where the plan is known, Opus where the plan is worked out during the work, as [the chain of command](reference/chain-of-command.md) sets out; suggest it rather than ask. Its effort and advisor setting come from [the chain of command config](reference/chain-of-command-config.md) |

| Mode | Suggest it when | How the sessions work |
|:-----|:----------------|:----------------------|
| **Shared checkout** | The jobs only create new files, such as transcripts or captures | Every session works in the main checkout with worktree isolation off; commits land on its current branch |
| **One worktree per job** | The jobs change existing code | Each session works on its own branch in its own worktree; the coordinator merges each finished branch into `main` |

`/parallel-sessions /capture-recording on ~/Webinars, 2 at a time, shared checkout` settles all but the model, which you suggest, so ask nothing. `/parallel-sessions on ~/Webinars` settles only the items, so ask the job, how many at once and the mode together.

### 2. Show the batch and wait for "go"

Show one summary: the six settled values, including any the user's message gave, then one line per item with the job's state, read from the new files that job creates:

| State | When |
|:------|:-----|
| **Done** | Every new file the job creates already exists |
| **Partly done** | Some of them exist, as when an earlier session stopped part-way |
| **Not started** | None of them exist |

A job that changes existing files, as in one worktree per job, is never marked done, because its files exist before it runs; leave it unmarked for the user to judge. Suggest starting the items not started, and ask whether to rerun each partly done one.

Start nothing until the user says "go". The "go" confirms the job, how many at once, the mode and the models as well as the items, and the user can drop or keep any item first.

When `/linear:start` runs a batch of cards, it settles the six values itself and, in unattended mode, gives the "go" itself, so the batch starts without a question. A batch of cards runs its jobs always as background `claude -p` sessions, even when a side-session tool exists: only the worktrees the skill makes get stride's settings.

### 3. Write one brief per job

Copy [BRIEF.md](BRIEF.md) once per job and fill it in: the mission, word for word, the job, the exact paths it may write, the holder name (the job's name, unique in the batch), the slot store, the limit, the commit route for the mode and the coordinator's session name, this session's name as `ListAgents` gives it. Name every path up front: the coordinator checks each commit against them.

A job running a stride card is the exception: its brief names the card in place of a path list, because the card's own "What we'll do" says what the job may change, and a card often mentions files it doesn't change. Everything below that checks paths against the brief, the commit check in step 5 and the report in step 6, applies to jobs that aren't a stride card; a card job's files are checked as step 5 sets out.

A question you can already see in a job, such as a choice that turns on another job, is cheapest settled in its brief. Settle it only with an answer that keeps every part of the mission: a default that would break one part, such as pounds for a branch that sells in euros, is not settled. Take it to `/advisor`, then to the user if the advisor can't settle it.

The slot store defaults to `work/slots` under the main checkout. The script finds that folder from git even inside a worktree, so every session reaches the same store. Give `--store` an absolute path only to use a different one.

**Everything the batch keeps lives under `work/` in the main checkout,** so the user and any coordinator find it in one place. Each batch has its own folder, `work/runs/<batch>/`, where `<batch>` is the time the batch's "go" was given, as `YYYY-MM-DD-HHMMSS`. The coordinator makes the folder at the "go" and never reuses a folder that exists, so a later batch never overwrites an earlier one.

| Path | Holds |
|:-----|:------|
| `work/runs/<batch>/progress.md` | One row per job: holder name, model, branch, log path and state |
| `work/runs/<batch>/briefs/<holder name>.md` | Each job's brief |
| `work/runs/<batch>/logs/<holder name>.jsonl` | Each session's log, with its errors in `<holder name>.err` and a resumed session's log in `<holder name>.resume-<n>.jsonl` |
| `work/slots/` | The slot store, shared by every batch so one limit holds for all |
| `work/stage-times/` | The record of how long each stage of each merged card took, written by [`scripts/stage_times.py`](scripts/stage_times.py); `uv run .claude/skills/parallel-sessions/scripts/stage_times.py report` shows where the time goes |

Add `/work` to the shared exclude file, `$(git rev-parse --git-common-dir)/info/exclude`, so git never sees it. Write the progress file before starting any session, with every job waiting for a slot, and update a job's row each time its state changes: working, sent back, ready, "exited, waiting to be resumed", merged, waiting on the user, or failed. It is what the user opens to see the batch, and what a new coordinator reads to pick the batch up: a new coordinator takes the newest folder under `work/runs/`.

### 4. Start every session in one turn

Start one side session per job, all in the turn the user's "go" begins, each with its own brief and nothing else. The app only lets a session be started on a turn the user began, so a session can't start another later; starting them all at once is what lets the slot store, not the user, decide when each one runs.

As you start each session, note its name from `ListAgents`, which is how you message it, and ask `SendMessage` for one notice when it next goes idle or exits (`notify_when_idle`), so a session that stops without messaging still reports. Ask again whenever you send a session back or resume it.

#### Without a side-session tool

When this session can't start side sessions, start each job as a background `claude -p` session instead. It claims a slot, runs its brief and messages you like a side session, and it ends when this session ends, so keep this session open until the batch is done.

1. **Make each job's checkout.** In worktree mode, find the main checkout from git, as the parent of `$(git rev-parse --git-common-dir)`, the way the slot store does, so a coordinator running inside a worktree doesn't nest new ones in its own. Make sure the main checkout ignores `.claude/worktrees/`, adding `/.claude/worktrees` to the shared exclude file (`$(git rev-parse --git-common-dir)/info/exclude`) when it doesn't, then add one worktree per job from `origin/main` at `.claude/worktrees/<holder name>` in the main checkout, beside the app's own session worktrees. In shared checkout mode, every session runs in the main checkout; skip to step 4.
2. **Link in what git doesn't carry.** A new worktree has no git-ignored files, so the commands, tools and settings the job's skills read are missing. Run stride's linking script for each worktree, with both paths absolute:

   ```bash
   "<main checkout>/.claude/tools/link_stride_install.sh" "<main checkout>" "<worktree>"
   ```

   When the main checkout has a `.stride.json`, the worktree needs it too: it holds the Linear project, its key and the `unattended` setting a stride card's job reads. Share it the way `/linear:start --worktree` does:

   ```bash
   "<main checkout>/.claude/tools/share_stride_settings.sh" "<main checkout>" "<worktree>"
   ```

   If it exits non-zero, report it and don't start that job: without the settings, the job's first Linear call fails.
3. **Check git sees nothing new.** `git status --porcelain` prints nothing in each worktree, and nothing new in the main checkout.
4. **Start every session in one turn,** each in the background in its job's checkout, on its model and effort with the advisor off and billed to the user's plan, as [the chain of command config](reference/chain-of-command-config.md) sets out, with its log in `work/runs/<batch>/logs/`:

   ```bash
   cd <checkout> && env -u ANTHROPIC_API_KEY CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 \
     claude -p "$(cat <brief>)" \
     --model <model> --effort <effort> \
     --dangerously-skip-permissions --output-format stream-json \
     --verbose > <main checkout>/work/runs/<batch>/logs/<holder name>.jsonl \
     2> <main checkout>/work/runs/<batch>/logs/<holder name>.err
   ```

   Every line of the log is JSON carrying the session's ID as `session_id`, which is what resumes it; errors go to the separate `.err` file so they don't break the JSON. Each session shows up in `ListAgents` under a name taken from its checkout's folder: note it and ask for its idle notice, as for a side session.
5. **Give the user the progress file's full path,** since these sessions don't appear in the app's sidebar; the logs are beside it in `work/runs/<batch>/logs/`.

### 5. Watch and check

While sessions run, `status` shows who holds each slot:

```bash
uv run --no-project --with diskcache --with click \
  python .claude/skills/parallel-sessions/scripts/slots.py --limit 3 status
```

When a job's session exits holding a slot, release its slot at once with `slots.py release <holder>`, before anything else, so the next waiting job can claim it. An idle notice releases nothing: a job that is only idle is still waiting for its go and keeps its slot. Whether or not it still held a slot, when a job's session exits before its card has merged, set the job's row in `work/runs/<batch>/progress.md` to "exited, waiting to be resumed"; a job already marked merged or failed keeps that state.

Each session messages you when its work is ready, when it hits an error it can't fix, and when it has a question about its job's purpose or scope. As each job's work is ready:

- For a job that isn't a stride card, check its commit holds only the paths its brief named (`git show --stat <commit>`), and report any that doesn't. For a stride card's job, list the pull request's files with `gh pr diff <number> --name-only` and report to the user any file the card's "What we'll do" doesn't call for, before you tell the job to run `/linear:finish`
- In worktree mode, before each merge after the first, build the code as it will look merged with `main` in a scratch worktree and run the project's checks and tests on it. Cards in one batch start from the same `main`, so each one's checks ran without the others' changes. A fresh worktree has no git-ignored files, so link stride's install into the scratch worktree with `link_stride_install.sh` and, when the main checkout has a `.stride.json`, share it with `share_stride_settings.sh`, both as in step 4. If either exits non-zero, report it and don't run the check: the failure would be the missing settings, not the code. Remove the scratch worktree afterwards the way a job's worktree is removed, below
- If that fails, send the failure back to the job's session rather than fixing it yourself, so the session that wrote the code fixes it and its own checks cover the fix
- If the job's session has already exited, resume it in its worktree with the message (`claude -p --resume <session-id>` for a `claude -p` session, with the environment, model, effort and permission options it started with, the ID taken from its log's `session_id`, and its log in `work/runs/<batch>/logs/<holder name>.resume-<n>.jsonl`). The message tells it to claim a slot before it carries on, and you resume an exited job only when `slots.py status` shows a free slot. Until one is free, give the go to a card whose job holds a slot, so each merge frees one, and no job waits for a slot that only its own merge could free
- For a job that isn't a stride card, once it passes, merge its branch into `main` in worktree mode; in either mode, then tell the session its work is done
- **A job running a stride card** opens a pull request instead of leaving a branch for you to merge, and its own `/linear:finish` does the merge, so the card's merge checks still run. Take these jobs one card at a time: build its branch merged with `main` as it stands now and run the checks on it, then tell its session to run `/linear:finish`, in interactive mode only once the user has approved its pull request. Check the next card's branch only once the job reports that its merge has landed, so no two cards are checked against the same `main`. A card job that reports a question instead of a pull request leaves its card out of the batch: report the question to the user and merge the rest
- Remove a job's worktree and archive its session only after that job's exit notice has arrived: a session removed while it winds down is killed, as WB-964's was. For a stride card's job, delete its local branch with the worktree: its `/linear:finish` deleted only the remote one

Before you put any question to the user, call `/advisor` and record what it said. Ask the user only what the advisor can't advise on: a job's purpose or scope, or something only the user knows. Name which of the three the question is; if it is none of them, such as a choice between two designs, take the advisor's recommendation instead of asking. See [the chain of command](reference/chain-of-command.md).

Never merge work that fills in something only the user can give with a guessed value, such as a made-up interest rate: keep it off `main` until the user answers.

The question reaches the user with none of the context the batch has built up, so put it in at most three short paragraphs, in this order: what the thing is and what the job asked of it; why that runs into trouble, as it would actually happen; then the options with your recommendation first, ending on a question the user can answer yes or no. Include a worked example, a before that shows the trouble and an after that shows the fix, taken from the real files or cards. Mention anything the user would be approving without knowing, such as a card line a session already added.

### 6. Report

Tell the user which jobs committed, which ended without a commit (a session that died, or a job that failed), and any commit from a job that is not a stride card that touched a path outside its brief. Leave `work/runs/<batch>/progress.md` showing each job's final state.

**Report once every job is merged or waiting on the user and every session has exited,** then end the session. Put any question for the user last, after the report and the progress file's path, so the question is the last thing the session says. A notice that arrives after the question, such as a session exiting or a background task finishing, changes nothing the user needs: handle it without a word to the user, and if you must reply, end on the question again. A `claude -p` coordinator exits when its final turn ends with nothing left running.

---

## The slot store

| Command | Does | Exit code |
|:--------|:-----|:----------|
| `claim <holder>` | Takes a free slot, or reports the one the holder already has | 0 with a slot, 1 when none is free |
| `renew <holder>` | Pushes the holder's claim back to a full expiry | 0, or 1 when the claim has lapsed |
| `release <holder>` | Frees the holder's slot | 0, or 1 when it held none |
| `status` | Lists each held slot, its holder and when the claim lapses | 0 |

Options, given before the command: `--limit` (default 3), `--expiry` in seconds (default two hours) and `--store`. Every session in a batch must use the same `--limit` and store.

A claim is a single atomic add in the store, so when several sessions claim at the same instant, each slot goes to exactly one of them. A claim that isn't renewed lapses at its expiry, which frees the slot of a session that died.

---

## Dependencies

- `uv` — runs the script with `diskcache` and `click` without installing them
- `diskcache` — the SQLite-backed store, safe across separate processes
- `click` — the command line

## Tests

The tests for `slots.py`, `measure_run.py` and `stage_times.py` live in stride's own repository, beside the skill's source, and run with `pnpm test:py` there. An install leaves them out.

---

## Cross-references

| Doc | Relationship |
|:----|:-------------|
| [commit](../commit/SKILL.md) | The commit route a job session uses |
| [A batch runs on a chain of command](reference/chain-of-command.md) | Which rank and model does what in a batch, and which decisions reach the user |
| [Each rank's model, effort and advisor setting](reference/chain-of-command-config.md) | The settings each rank runs on, the flags that apply them, and how to read a soldier's cost |
| [Two tests find each rank's sweet spot and keep the user out of the weeds](reference/testing-the-chain-of-command.md) | How questions are tested to stop at the right rank, and how the soldier's sweet-spot effort is found |
| [What each Claude model costs per million tokens](reference/model-costs.md) | The rates a rank's model is chosen and a card's cost is judged against |

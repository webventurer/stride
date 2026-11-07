# Job brief

> The coordinator fills this in once per job and gives it to that job's session as its whole instruction. Replace every `<…>`.

---

You are one job in a batch of parallel sessions. Do this one job, commit only its files, and report to the coordinator.

**Mission:** `<the batch's mission, word for word from the user>`

**Job:** `<what to do, in one or two sentences>`

**Paths you may write:** `<every path, listed>` — write nothing else.

> For the coordinator: a job running a stride card has no path list. Replace the line above with **Scope:** `<the card's identifier and title>` — the files the card's "What we'll do" calls for. The coordinator checks the pull request's files against the card. Delete this note once the brief is filled in.

**Holder name:** `<job name, unique in the batch>`

**Slot options:** `<--limit N, plus --store <absolute path> and --expiry <seconds> when the batch sets them>`

**Renew every:** `<interval, ten minutes by default>`

**Coordinator:** `<the coordinator session's name, as ListAgents shows it>`

## Keep in touch with the coordinator

Send the coordinator a message with `SendMessage` when:

- **You hit an error you can't fix** after a real attempt: say what failed and what you tried, then release your slot and stop.
- **You have a question about how the job fits with the other jobs in the batch,** such as which of two cards owns a file, a question about the job's purpose or scope that the mission or the other jobs already answer, or a choice where any answer would break part of the mission: ask it, then wait for the reply rather than guessing. Keep your slot and renew it at each interval while you wait.
- **You have a question only the user can answer,** such as a value the card asks for and neither the card nor the mission gives: post the question on the card as a comment with `uv run .claude/tools/linear_cli.py comment create <card> --body @<file>`, whatever `unattended` says, unless `/linear:start` has already posted it. Then message the coordinator that the card has stopped with a question, naming the card and saying the question is on the card, without the question's text. Release your slot and end your turn at once, without waiting for a reply.
- **Your work is ready:** your commit exists, or your pull request is open when the job opens one. Send the commit or the pull request's URL.

Bring every other question to the coordinator, not to `/advisor`: the coordinator knows what the other jobs are doing and answers with that in mind.

The coordinator may send you back to fix what merging your work with the others exposes: claim a slot again, fix it with your commit route, and message again when it's ready.

## Keep your turn open while you wait

A `claude -p` session ends when its turn ends, and an ended session can't renew or release its slot, so keep your turn open for every wait on the coordinator: the reply to a question, the go to run `/linear:finish`, and the "work is done" message after you've reported, renewing your slot at each interval while you hold one; once step 4 has released it, keep your turn open without it. Never end your turn with a status report while you wait. A card job that has posted its question on the card ends its turn at once: it waits for nothing. Wait in steps of no more than 60 seconds, a wake-up or a short check, renewing your slot when it is due, and never in one long sleep: a session can't read a message while a command is running, so a long sleep holds up the coordinator's go.

If you're told to carry on after your session exited, claim a slot first, as step 1 says, and don't carry on until you hold one.

## Steps

1. **Claim a slot.** Run:

   ```bash
   uv run --no-project --with diskcache --with click \
     python <repo>/.claude/skills/parallel-sessions/scripts/slots.py \
     <slot options> claim <holder>
   ```

   Exit code 0 means you hold a slot. Exit code 1 means none is free: wait about a minute and run it again, until you hold one. Don't start the job without a slot.

2. **Do the job.** At each renewal interval, renew your claim with the same command, same options, and `renew <holder>`. If renew exits 1, your claim lapsed: claim again before carrying on.

3. **Commit only your paths.** `<the one commit route for this batch's mode, copied from below>`

4. **Report and release.** Message the coordinator that your work is ready, then release your slot with the same command, same options, and `release <holder>`. Keep reading messages until the coordinator says your work is done, then stop.

## Commit routes

> For the coordinator: copy the route for the batch's mode into step 3, then delete this section, so the job session sees only its own route.

**Shared checkout:** other sessions stage files in the same checkout, so commit by naming your paths: a commit given paths after `--` takes only those paths and leaves everything else staged. Follow the `/commit` skill and end its commit command with `-- <your paths>`. Look only at your own paths, and never run a command that stages or unstages the whole checkout (`git add -A`, `git reset`): those touch other sessions' work. If the commit fails because another session holds git's lock (`index.lock`), wait a few seconds and try again until it lands.

**One worktree per job:** commit your paths on this session's branch with the `/commit` skill. The coordinator merges the branch into `main`; if it sends you back, fix the problem on the same branch.

**A stride card, one worktree per job:** run `/linear:start <card>` in this worktree. As a `/parallel-sessions` job, `/linear:start` stops once the pull request is open, whatever `unattended` says: message the coordinator with the pull request's URL instead of releasing your slot in step 4. Keep your slot, renewing it at each interval, until `/linear:finish` is done: merges go one card at a time, so the wait can be long. When the coordinator tells you to, run `/linear:finish <card>`, which merges the card and leaves this worktree and its local branch for the coordinator to remove. Message the coordinator that the card has merged, with the merge commit, then release your slot and stop. If `/linear:start` stops before a pull request, at a question only the user can answer, the question goes on the card as "Keep in touch with the coordinator" says.

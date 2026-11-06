# Job brief

> The coordinator fills this in once per job and gives it to that job's session as its whole instruction. Replace every `<…>`.

---

You are one job in a batch of parallel sessions. Do this one job, commit only its files, and report to the coordinator.

**Mission:** `<the batch's mission, word for word from the user>`

**Job:** `<what to do, in one or two sentences>`

**Paths you may write:** `<every path, listed>` — write nothing else.

**Holder name:** `<job name, unique in the batch>`

**Slot options:** `<--limit N, plus --store <absolute path> and --expiry <seconds> when the batch sets them>`

**Renew every:** `<interval, ten minutes by default>`

**Coordinator:** `<the coordinator session's name, as ListAgents shows it>`

## Keep in touch with the coordinator

Send the coordinator a message with `SendMessage` when:

- **You hit an error you can't fix** after a real attempt: say what failed and what you tried, then release your slot and stop.
- **You have a question about the job's purpose or scope,** or a choice where any answer would break part of the mission: ask it, then wait for the reply rather than guessing. Keep your slot and renew it at each interval while you wait.
- **Your work is ready:** your commit exists, or your pull request is open when the job opens one. Send the commit or the pull request's URL.

Bring every question to the coordinator, not to `/advisor`: the coordinator knows what the other jobs are doing and answers with that in mind.

The coordinator may send you back to fix what merging your work with the others exposes: claim a slot again, fix it with your commit route, and message again when it's ready.

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

**Shared checkout:** other sessions stage files in the same checkout, so commit by naming your paths: a commit given paths after `--` takes only those paths and leaves everything else staged. In a repo with codefu's hooks, follow the `/commit` skill and end its commit command with `-- <your paths>`. Look only at your own paths, and never run a command that stages or unstages the whole checkout (`git add -A`, `git reset`): those touch other sessions' work. If the commit fails because another session holds git's lock (`index.lock`), wait a few seconds and try again until it lands.

**One worktree per job:** commit your paths on this session's branch with the `/commit` skill. The coordinator merges the branch into `main`; if it sends you back, fix the problem on the same branch.

# Foreground loop, background structure

> **AI Assistant Note**: When the user is making a run of small changes to an app in a live session, reference this pattern. Keep each change to one request and one `/commit`. When a request needs real thought about structure, suggest a Linear card for the background instead of doing it in the live session.

Split the work by how much thought it needs. Quick changes you can see in the app run in the foreground, in the live Claude session, one request and one `/commit` at a time. Work that needs more thought goes on a Linear card, and Stride builds it in the background, which leaves the foreground free for the quick changes. An independent reviewer checks every commit as it lands and splits any that aren't atomic, so committing this fast doesn't cost a clean history.

**Goal:** Keep the fast changes fast by moving the slow ones out of the way.

The split moves what holds you up from waiting on the agent to [your own decisions](/concepts/attention-bottleneck).

---

## Quick reference

| Aspect | Description |
|:-------|:------------|
| **One-liner** | Small visible changes in the live session, committed one at a time. Work that needs thought on a Linear card, built in the background |
| **Use when** | You are working on an app and have a mix of small tweaks and bigger structural work |
| **Key benefit** | Features land quickly and you stay engaged, because you see each change in the app moments after asking for it |
| **The test** | Can you say the change in one sentence and see it in the app straight away? Foreground. Does it need a decision about structure first? Background |
| **Same files** | Both lanes may change the same files. A card that names a file you've changed by hand and not pushed waits until you push, and its batch report names the file. Before any card merges, stride tests it combined with `main`, including your pushed commits, and any clash is fixed before the merge. Working on another part of the app avoids both. [Working in both lanes costs one catch-up merge](#working-in-both-lanes-costs-one-catch-up-merge) says who pays it and when |

---

## The problem

Without the split, every kind of work shares one session:

- **Small changes queue behind big ones.** You want the button smaller, but the session is halfway through a change to the data model, so the tweak waits.
- **You drift off while the AI thinks.** A long piece of work leaves you watching a spinner. Your attention goes elsewhere, and so does the feedback that would have caught a wrong turn early.
- **Batched tweaks make tangled commits.** Saving five small changes for one commit at the end mixes five purposes, and the history can't say what each one did.

---

## The solution

Run two lanes at once, each suited to its kind of work.

| Lane | Where it runs | What goes in it | How it lands |
|:-----|:--------------|:----------------|:-------------|
| **Foreground** | Your own Claude session, on `main` in the main checkout | Changes you can say in a sentence and see in the app: sizes, labels, a new section | One request, then `/commit`, then the next |
| **Background** | Stride, working from Linear cards, in their own folders | Work that needs more thought: structure, data, anything that needs a decision before code | Its own branch. In interactive mode it stops at a pull request for you to review. In unattended mode it merges itself |

**The foreground is a loop.** Ask for a change, check it in the app, `/commit`, ask for the next. You can line the requests up: type the next one while the last is still running, and the live session takes them in order. Each change lands as its own commit as you go. Keep the foreground in its own session, not the one that runs the cards: that session spends its time waiting on them, so your tweaks would queue behind it. Push when you like. When a push is refused because cards have merged, `git pull --rebase` brings them in.

**The background holds the thinking.** Draft the card with `/linear:plan-work` and start it with `/linear:start`. Stride branches, builds, validates and reviews it without needing the live session. A card builds in its own folder when it runs from Todo, in a batch or an unattended run, or when you start it with `--worktree`. A card started alone without `--worktree` works in the main checkout on its own branch, so start it with `--worktree` to keep the foreground on `main`.

**The two lanes can change the same files.** Before a card merges, stride tests it combined with `main`, including your pushed commits, and any clash is fixed before the merge. Working on another part of the app than the card is a tip that avoids that fix, not a rule.

**A finishing card leaves your folder alone** when the folder holds uncommitted changes or commits you haven't pushed, is on a branch other than `main` or the card's own, or can't fetch. Its finish report says so, with the steps that bring the card's work in. When the folder is clean and pushed, the finishing card brings the work in itself.

**The reviewer keeps the commits atomic.** Each `/commit` ends with an independent atomicity review: a fresh sub-agent that never saw why the changes were grouped reads the commits and judges each one. If it finds a commit with two purposes, the same `/commit` run undoes the session's commits, regroups them and has a new reviewer check the result. The split happens on the fly, after the code is committed, and the loop carries on. [Pass 5 of the commit workflow](https://github.com/webventurer/stride/blob/main/.claude/skills/commit/WORKFLOW.md#pass-5-independent-atomicity-review) has the detail.

---

## Working in both lanes costs one catch-up merge

Two lanes at once means your quick changes and the cards progress together. The price is one catch-up merge when the lanes meet, in which your changes are replayed one at a time on top of what the cards built. The agent does the catch-up while you carry on.

**The lane that merges second pays.** If your commits are already pushed when a card finishes, the card pays, because stride fixes clashes before it merges. If you have unpushed commits when cards have merged, you pay when you run `git pull --rebase`.

**Pushing after every `/commit` is optional.** You don't need to push to dodge the catch-up: one catch-up covers a whole run of changes. Not pushing has a cost: a card that names a file you've changed and not pushed waits until you push, and the cards can't see your unpushed work while they build, so a card that reaches your code without naming its file can still restructure code your changes depend on. The catch-up then has more to adapt, and the adapting is still the agent's job. After a card merges, stride replays your unpushed commits and uncommitted changes on the new `main` in a separate folder and reports whether they still apply, without touching your folder.

**A line can merge cleanly and still break.** Few of your changes will clash outright. The risk is a line that replays without complaint but calls something a card removed or renamed. After each replayed commit, ask the agent to run:

- the tests
- the linter
- a search for the names the cards removed or renamed

Stride has no step that runs these checks today, so they are something to ask for. A fix goes into the commit that introduced the line, so each commit still does one job.

For example, you make 20 small app changes while a card renames a folder the app uses. When you pull, your 20 changes are replayed one at a time on the renamed code. After each one the checks run, and a change that still points at the old folder name is fixed in that change.

---

## Implementation

**Step 1: Sort the list.** Go through what you want done and put each item in a lane. A tweak you can see goes in the foreground. Anything where you would have to stop and think about how it should work goes on a Linear card.

**Step 2: Start the background first.** Write the cards and start them, so the slow work is running before the quick work begins.

**Step 3: Run the foreground loop.** One request, check it in the app, `/commit`. Line up the next request while the current one runs.

**Step 4: Move work that turns out bigger.** If a foreground change opens a question about structure, stop it, put it on a card and carry on with the next tweak.

**Step 5: Review the background when it finishes.** In interactive mode a finished card stops at a pull request to read and merge. In unattended mode it merges itself.

---

## Example

A run of foreground requests in one session:

```text
Make this button smaller.
/commit
Now a bit bigger.
/commit
Add a new section called "Group".
/commit
```

Each request is one change you can see in the app, and each `/commit` turns it into one commit. Meanwhile a Linear card for a change to how the app stores its data runs in the background on its own branch.

---

## Anti-patterns

### Thinking work in the foreground

**Problem:** A change that needs a structural decision goes into the live session because it is the session you have open.

**Why it fails:** The loop stops. Every tweak behind it waits, and you wait with them.

**Solution:** Put it on a Linear card and let Stride build it in the background.

### Saving the commits for the end

**Problem:** You make a run of tweaks and commit them all at once.

**Why it fails:** One commit now holds several purposes. The reviewer will split it, but each tweak's own `/commit` would have made the right commit straight away, while you still knew what each change was for.

**Solution:** `/commit` after every change.

---

## Related patterns

- One goal, one commit — each foreground request is one atomic goal, and its `/commit` is the proof
- Dial the ask — foreground requests are small and precise. Background cards are where the wider asks go
- Orchestrator-subagent — the independent reviewer is a fresh sub-agent, which is why it can judge the commits without the session's reasoning
- [Atomic git commits](https://github.com/webventurer/stride/blob/main/.claude/stride/docs/patterns/git/atomic-git-commits.md) — the standard the reviewer holds every commit to

---

*Quick changes in the foreground, thinking in the background, and a reviewer keeping every commit clean.*

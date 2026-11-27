# Todo run

> How [`/linear:start`](../start.md) works through Todo when no card is named and [unattended mode](unattended.md) is on: it starts a new card each time a place frees up, until no card is running and none in Todo can start. Interactive mode runs one batch and stops, as `start.md` says.

<mark>**The run keeps its slots filled instead of waiting for a batch to finish.**</mark> The cards started together run through [`/parallel-sessions`](../../../skills/parallel-sessions/SKILL.md) as one batch, and the same coordinator looks after every batch.

## The run keeps a list of the cards it has started

Start the list empty. Add each card when it starts, whether or not it later merges, so no later fill offers a card that has been handed to the launcher but has not reached Doing. A card that merges is Done and leaves Todo by itself. A card the run started that is still in Todo after its job ends stopped before it reached Doing, such as at its lesson-question or Vision stop, and the list keeps it out of every later fill, so the same card is never started twice. A card that stopped later, such as at its start check, is in Doing and no fill offers it.

## A card leaving its slot starts a fill

A fill is one look at Todo that starts cards into the free slots. The first happens as the run starts, with every slot free. After that, a card leaves its slot when it merges, ends Canceled, fails, stops on a question, or is released while held, and the coordinator fills the free slots without waiting for the rest of the cards.

- **A merged card:** the fill waits for the one-line lesson result its job sends from `/linear:finish` step 12, not for the merge or the Done status, because step 12 rewords Todo cards and posts lesson questions after the card is already Done. Pass the lessons to the cards still running first, as [`/parallel-sessions`](../../../skills/parallel-sessions/SKILL.md#5-watch-and-check) sets out.
- **A card that ended Canceled, failed or stopped on a question:** the fill follows its job's report.
- **No report or lesson result:** the session's exit counts as its card leaving, merged or not, so no card counts as running for ever. The exception is a session that the launcher (after a lost connection) or the coordinator (as `/parallel-sessions` step 5 resumes an exited job) is going to resume: its card counts as running until it reports or its row in `progress.md` says failed. A held card is not one of these: it left its slot when it was released.

<mark>**No fill starts a card while a merge is in flight.**</mark> From the go for a card's `/linear:finish` until its lesson result arrives, every fill waits, whatever triggered it: a card started in that gap reaches Doing before step 12 runs, so it would miss the lesson. The gap also closes when the job reports that the finish stopped without merging, or its session exits and will not be resumed. A fill that waited then runs, before the next go.

## Each fill

1. Run `/linear:next-steps`, the first step of `/linear:start` with no card named. It orders Todo again, and so applies what the merged cards taught: `/linear:finish` step 12 has already reworded the cards the lessons change.
2. Ask stride what to do, giving it every card on the list:

   ```bash
   uv run .claude/tools/linear_cli.py start-choice --project "<project>" --branch main --started <card> --started <card>
   ```

3. For `batch` or `single`, start no more cards than there are free slots: `parallel-sessions` minus the cards still running, taken in the order `start-choice` gives. It names up to the full `parallel-sessions` number, because it doesn't count the cards in Doing. Run them through `/parallel-sessions`, settled as `start.md` sets out. A `single` card runs the same way, as a batch of one, so a failure ends that card's job and not the run. Cards left over are looked at again at the next fill, after whatever has been learnt by then.
4. For `blocked` or `empty` while cards still run, start nothing and wait for the next card to leave its slot. The run is over only when no card is running and `start-choice` says `blocked` or `empty`. Go to the final report.

As each card merges, report one line for it: its lesson result from its `/linear:finish` summary (the cards it commented on and reworded, the one-off lessons named and left, or "no lesson for cards to come").

The reasons the run reports are the ones `start-choice` prints for a card that is out: a blocker that isn't Done, a lesson question with no answer, a card the run already started, or a card that names a file you have changed by hand in the main folder and not yet pushed (`waits for your work on <files> to be pushed`). The last one clears by itself: once none of the card's files has uncommitted or unpushed changes, the next `start-choice` offers the card again. A run with no card running and nothing else to start ends, and the final report lists the card under Waiting with its files named.

## Holding a card back

When the coordinator judges that a card `start-choice` offers should not start yet, such as one that edits files a running card is moving, it records the hold on the board before anything else:

```bash
uv run .claude/tools/linear_cli.py issue block <card> --by <blocker>
```

Add one line naming the card, the blocker and why to the `decisions.md` of the run's most recent batch folder. A hold made before the run has a folder makes the first fill's folder then, with a `progress.md` that opens with its `Run:` line, and the first fill uses that folder. Then ask `start-choice` again, so the slot goes to the next card that can start. The link keeps the card out as any other blocker does, so nothing about the hold lives only in the coordinator's memory. Once the blocker is Done, the next fill offers the held card. A blocker that fails or ends Canceled is never Done, so the link stays, the held card stays in Todo and the final report lists it under **Waiting** with `blocked by <blocker>`.

## A card that is already done

A card that ended in Canceled at its start check had nothing left to build. A card that ended in Canceled leaves the batch, merges nothing and is not a failure, and the other cards carry on. Its job reports that the card is Canceled in place of a pull request's URL.

## A card that fails or needs a decision

The card stays out of Done and out of every later fill. Post its reason on the card as a comment, unless its job already did: the check that failed, or the decision it needs. The other cards still merge, and the run carries on with the cards that don't depend on it. A card that waits on a failed card stays in Todo with `blocked by <card>` until its blocker is Done, which in this run it never is.

A blocker that sits in Backlog or Cancelled never becomes Done in this run either, so the card it blocks waits the same way, and the report names that blocker.

## A question for the user

A question carries the four labelled parts in order, as [asking the user](asking-the-user.md) sets out. It is posted on its card as a comment as it arises, whether a job's start check raised it or a lesson raised it, and the run holds it. No batch's report puts a question to the user, and the run stops for none: the cards that don't wait on an answer keep running. A lesson question leaves only its own card out of later fills, because `start-choice` reads the card's comments: the question is open while no later comment starts `Answer:`.

## The final report

The run's last message to the user lists, in this order:

- **Done:** each card that merged.
- **Canceled:** each card that ended in Canceled because its work was already done, with the reason in its comment.
- **Failed:** each card that failed, with the check that failed or the decision it needs.
- **Waiting:** each card still in Todo that isn't listed as failed, with the reason `start-choice` gave, and each card still held at merge time, with its pull request and what it waits for.
- **Lessons:** for each merged card, the lesson it carried and the cards it commented on and reworded, the one-off lessons named and left, or "no lesson for cards to come", read from its `/linear:finish` summary.
- **Decisions:** every line from the `decisions.md` of every batch in the run, with the note on overruling from [a batch's report](../../../skills/parallel-sessions/SKILL.md#6-report). When none was settled, say so.
- **Questions:** every question held during the run, each in the four labelled parts with its card. This comes last, so the user's answer is the last thing asked for. The user answers on the card, in a comment starting `Answer:`.

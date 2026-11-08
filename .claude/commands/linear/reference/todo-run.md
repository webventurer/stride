# Todo run

> How [`/linear:start`](../start.md) works through Todo when no card is named and [unattended mode](unattended.md) is on: batch after batch, until no card in Todo can start. Interactive mode runs one batch and stops, as `start.md` says.

<mark>**The run keeps going after a batch's report instead of ending there.**</mark> Each batch runs through [`/parallel-sessions`](../../../skills/parallel-sessions/SKILL.md), whose coordinator hands its report back to the run, so the run can order Todo again and start the next batch.

## The run keeps a list of the cards it has started

Start the list empty. After each batch, add every card in it, whether or not it merged. A card that merges is Done and leaves Todo by itself. A card the run started that is still in Todo stopped before it reached Doing, such as at its start check, and the list keeps it out of every later batch, so the same card is never started twice.

## Each round

1. Run `/linear:next-steps`, the first step of `/linear:start` with no card named. It orders Todo again, and so applies what the merged cards taught: `/linear:finish` step 12 has already reworded the cards the lessons change.
2. Ask stride what to do, giving it every card on the list:

   ```bash
   uv run .claude/tools/linear_cli.py start-choice --project "<project>" --branch main --started <card> --started <card>
   ```

3. For `batch` or `single`, run the cards through `/parallel-sessions`, settled as `start.md` sets out. A `single` card runs the same way, as a batch of one, so a failure ends that card's job and not the run. Add its cards to the list. When the report comes back, report one line for each merged card, its lesson result from its `/linear:finish` summary (the cards it reworded, the one-off lessons named and left, or "no lesson for Todo"), then go back to step 1.
4. For `blocked` or `empty`, the run is over: no card in Todo can start. Go to the final report.

The reasons the run reports are the ones `start-choice` prints for a card that is out: a blocker that isn't Done, a lesson question with no answer, or a card the run already started.

## A card that is already done

A card that ended in Canceled at its start check had nothing left to build. A card that ended in Canceled leaves the batch, merges nothing and is not a failure, and the rest of the batch carries on. Its job reports that the card is Canceled in place of a pull request's URL.

## A card that fails or needs a decision

The card stays out of Done and out of every later batch. Post its reason on the card as a comment, unless its job already did: the check that failed, or the decision it needs. The rest of its batch still merges, and the run carries on with the cards that don't depend on it. A card that waits on a failed card stays in Todo with `blocked by <card>` until its blocker is Done, which in this run it never is.

A blocker that sits in Backlog or Cancelled never becomes Done in this run either, so the card it blocks waits the same way, and the report names that blocker.

## A question for the user

A question carries the four labelled parts in order, as [asking the user](asking-the-user.md) sets out. It is posted on its card as a comment as it arises, whether a job's start check raised it or a lesson raised it, and the run holds it. No batch's report puts a question to the user, and the run stops for none: the cards that don't wait on an answer keep running. A lesson question leaves only its own card out of later batches, because `start-choice` reads the card's comments: the question is open while no later comment starts `Answer:`.

## The final report

The run's last message to the user lists, in this order:

- **Done:** each card that merged.
- **Canceled:** each card that ended in Canceled because its work was already done, with the reason in its comment.
- **Failed:** each card that failed, with the check that failed or the decision it needs.
- **Waiting:** each card still in Todo that isn't listed as failed, with the reason `start-choice` gave.
- **Lessons:** for each merged card, the lesson it carried and the cards it reworded, the one-off lessons named and left, or "no lesson for Todo", read from its `/linear:finish` summary.
- **Questions:** every question held during the run, each in the four labelled parts with its card. This comes last, so the user's answer is the last thing asked for. The user answers on the card, in a comment starting `Answer:`.

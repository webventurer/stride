# Asking the user

> The one shape for a question stride puts to the user.

A stop is only worth it if the user can decide in seconds.

## The four parts

A question has four labelled parts, in this order and nothing more:

1. **Context:** what this part of stride does, with an everyday comparison, and what recently changed.
2. **The gap:** what is still missing or wrong.
3. **The question:** one question, answerable yes or no, or by choosing one of two. When only the user can supply a value or their own wording, the question asks for that one thing instead.
4. **My answer:** the recommendation and why, kept short. When the answer is a change to a card, the new wording is quoted here, ready to approve.

A lesson question's heading, **Lesson question from <card>**, stays as the first line of its comment. It is a heading, not a fifth part.

## Who it is written for

Write for a reader of about 16 who doesn't know the code. Leave out file names and class names. Explain any stride term in the same sentence it first appears in, as the example explains "slot" with "like tickets for a ride".

## The question that settled this shape

On WB-1017, word for word:

> **Context:** stride runs a few jobs at once, and each job needs one of a limited number of slots, like tickets for a ride. Until now, a job's session was started first and then sat there waiting for a slot, wasting effort. WB-1018 fixed that: a job's session now starts only once its slot is free.
>
> **The gap:** that fix only covers a job's first run. When a job gets cut off, say by a lost connection, and is restarted, it's back to starting first and then waiting. WB-1017 is the card that adds restarting cut-off jobs.
>
> **The question:** should WB-1017 also make restarted jobs wait for a free slot before they start, the same way first runs now do?
>
> **My answer:** yes. Otherwise WB-1017 brings back the waiting WB-1018 just got rid of. It's a small addition to the same card.

## What this does not cover

The approval and confirmation questions in `start.md`, `finish.md` and `quick.md`, such as "Does this look right?", and the questions `/linear:plan-work` asks while drafting a card.

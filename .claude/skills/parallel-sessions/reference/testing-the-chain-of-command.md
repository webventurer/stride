# Two tests find each rank's sweet spot and keep the user out of the weeds

> **AI Assistant Note**: Read this before running or changing the tests of the chain of command, or when reporting their results. The tests run in a throwaway practice repo, never on real cards, and every result is judged by rules fixed before the first run.

## What the tests found: questions reach the right rank, and soldiers run on Sonnet at high

Both tests ran on 2026-11-06 through a sealed relay, on cases written by a fresh session the coordinator never read. They found three things:

- **Questions reach the right rank.** In every measured run, each question was settled at its rank or lower, the general was called before any question reached the user, and no card waiting on the user's answer was merged into the shared code (`main`) with a guessed value in its place, such as a made-up interest rate.
- **Soldiers run on Sonnet at high effort for planned work.** In fifteen runs on three cards, every setting above Sonnet at medium scored the same quality within chance, and Sonnet at high used the least. Sonnet at medium scored lower on one card in every run.
- **A hard card didn't change that.** One hard card, run at six settings including Opus at xhigh, was solved in full at every setting, so it couldn't show whether harder work needs a stronger setting.

The soldiers' settings in [the chain of command config](chain-of-command-config.md) follow from these results. The [appendix](#appendix-the-results-of-each-round) holds each round's evidence.

## The principle: each rank works at its sweet spot, and only the user's decisions reach the user

<mark>The sweet spot is where more effort stops buying better work: below it you lose quality, above it you pay for nothing. The user's attention is the dearest resource in the chain, so a question climbs only as high as it has to.</mark>

The principle has two halves, and each test checks one:

- **Quality for the cost, at every rank.** Each rank runs at the lowest effort whose work is as good as the effort above it. A cheap attempt that fails, scores low or comes back from the captain is not cheap.
- **The user stays out of the weeds.** Questions about how to do the work stop at the soldier, the captain or the general. Only questions about what a card is for, or how far it goes, reach the user.

The tests vary the soldier's effort first, because a batch runs more soldiers than any other rank. The captain's effort can be tested the same way once the soldier's is settled.

Three existing patterns shape how the tests find the sweet spot:

- **Split-test the world:** run every setting on the same work, rather than reasoning about which would win.
- **Predict, then probe:** write the pass marks, the checks that decide whether a run passed, and the decision rule before the first run, so the results can't be read to fit what was already believed.
- **Sealed relay:** run each round as a sealed relay, so a fresh writer builds the cases and checker, a fresh judge rules on each failure, and whoever fixes the skill never marks its own homework.

## 🚨 Quick reference

| Test | Question it answers | Runs | Result |
|:-----|:--------------------|:-----|:-------|
| **1. Questions go up the chain** | Does each question reach the rank that should answer it, and no further, so only the user's questions reach the user? | One per launch route | Pass or fail |
| **2. The soldier's sweet spot** | Which soldier model and effort does the best work for the least use? | Fifteen: Sonnet at medium, high and xhigh, and Opus at medium and high, three times each | A chosen setting, or a tie the setting with less use wins |

The two tests stay separate because planted questions would add escalation costs to every card in Test 2 and hide the difference between efforts.

## Test 1: questions go up the chain to the right rank

Four cards run with three slots, each planted with a different kind of question, so the fourth also checks a card waits for a free slot:

| Card | Planted question | Settled by |
|:-----|:-----------------|:-----------|
| **A** | None: a plain task | Nobody: the soldier finishes without a question |
| **B** | A choice between two approaches that turns on what card C is doing | The captain, which alone sees both cards |
| **C** | A question about the code that looks like one about the card's purpose, and that the mission answers | The captain or the general, never the user |
| **D** | A question about how far the card should go, which only the user can answer | The user, once the general has seen it |

A question counts as settled at a rank whether that rank settles it when a soldier asks or before the soldier starts, as when the captain answers it in the soldier's brief. The general is called only before a question would go to the user, so it can't be made to answer: it is tested by what it lets through.

The test runs once for each route the batch can start soldiers by: background `claude -p` sessions and side sessions. It passes when the transcripts show all of these:

- **No soldier called the advisor.**
- **Each planted question was settled by the rank in the table or a lower one.**
- **The captain called the advisor before every question it put to the user.**
- **Exactly one question reached the user, card D's,** in the form the skill sets out: what the thing is, why it runs into trouble, and the options with a recommendation, ending on a yes-or-no question.

The result of each round is in the [appendix](#appendix-the-results-of-each-round).

## Test 2: the soldier's sweet spot is where more effort stops improving the work

**The same work every run.** Three cards in a practice repo frozen at one commit, so every run starts from identical code. The cards are of different kinds: a mechanical change, a feature with a judgement call inside it, and a bug to find and fix. The bug must be hard enough that effort could change the outcome; if every card is easy, every setting ties.

**No planted questions.** Escalations that happen on their own are counted, never forced.

**Quality measured twice.** Each card has hidden tests, automatic checks on its code that the soldier never sees; the captain runs them after merging, and a card that fails them scores nothing. A card that passes is then scored out of 10 against a rubric written with the card: correctness beyond the tests, readability, and the house rules. The scorer is a fresh session that sees the finished work and the rubric but not the effort that produced it, so the score can't lean towards the setting expected to win.

**Only the soldier's model and effort change.** Every soldier in a run uses the same setting, set in the kickoff, so the captain doesn't pick a model per card. The captain stays on Opus at high effort, the general on Fable, the reviews on the models their workflows name, and every soldier runs with the advisor off. The settings are in [the chain of command config](chain-of-command-config.md).

**Fifteen runs in three waves:** five settings, Sonnet at medium, high and xhigh and Opus at medium and high. A wave is one run of each of the five settings, started together and run side by side; the next wave starts when every run in it has finished. Three runs of each setting show how far results move by chance alone, and running the settings side by side in each wave keeps drift across the day from landing on one setting. Opus at xhigh joins as a follow-up of three runs only if Opus at high's average quality beats Opus at medium's by more than the noise. Max effort is left out on cost.

### What each card reports

| Measure | What it is |
|:--------|:-----------|
| **Tokens by model** | Input, cache writes, cache reads and output, for the soldier, every subagent it started, and any advisor calls |
| **Weighted use** | The same tokens weighted by each model's [API rate](model-costs.md), which puts every model and cache read on one scale, reported against a baseline run set at 1.0: a card at 1.4 used 40% more. The raw tokens by model stay in the results files |
| **Hidden tests** | Passed or failed after merging |
| **Quality score** | Out of 10 against the card's rubric, from a scorer who doesn't know the effort |
| **Sent back** | How many times the captain returned the work |
| **Review findings** | How many findings the card's reviews raised |
| **Escalations** | Questions the soldier sent the captain unprompted |
| **Wall-clock time** | From the soldier's start to its work being ready |

Each run also reports the captain's tokens in two parts: planning, from its start until the first soldier starts, and running the batch after that. Set against the soldiers' tokens, they show how the work splits between the ranks, and whether the captain's planning saves the soldiers more than it costs.

Each test also records the plan's weekly usage from `/usage` before and after. Other sessions running at the same time blur that figure, so it checks the weighted use rather than replacing it.

### The decision rule

1. **A setting qualifies only if every card passes its hidden tests in all three runs.**
2. **The sweet spot is the qualifying setting with the lowest weighted use per finished card whose average quality score is within the noise of the best.** The noise is the average of the two settings' own spreads, each spread being the difference between that setting's highest and lowest run; a costlier setting that scores better by less than the noise has bought nothing.
3. **A tie on use goes to the cheaper setting.** If two settings within the noise of the best use the same, the lower effort wins, and Sonnet wins over Opus at the same effort.
4. **If no setting qualifies,** the cards or the setup are at fault, and the result goes to the user before any setting changes.

The result of each round is in the [appendix](#appendix-the-results-of-each-round).

## Each run has its own config file and results row

| File | Holds |
|:-----|:------|
| **One config file per run** | The soldier's model and effort, the captain's and general's settings, the practice repo's commit, the cards, and which repeat it is: seventeen files, fifteen for Test 2 and one per launch route for Test 1 |
| **The cards and their hidden tests** | Kept in the practice repo, with the hidden tests outside the soldiers' paths |
| **The results table** | One row per card per run, with the measures above, and a summary per setting once the decision rule is applied |

## Appendix: the results of each round

### Test 1's result: questions reach the right rank on unseen cards

Test 1 ran on the background `claude -p` route on 2026-11-06. The side-session route hasn't run yet. **The routing works.** Every measured run settled each question at its rank or lower, called the general before any question reached the user, and never merged a card that was waiting on the user's answer with a guessed value in its place. One fault turned up in how a headless captain ends its run, and it is fixed but not yet confirmed.

| Round | Cards | Runs | What it showed |
|:------|:------|:-----|:---------------|
| **Practice** | A shop selling in pounds and euros, written by the coordinator | 8 | The last three passed every mark once the skill sent design questions to the general and stopped merging a card with a guessed value in place of the user's answer. The cards were the ones those rules were written against, so the passes don't show the rules work elsewhere |
| **Unseen 1** | Race timing, written by a fresh session the coordinator never read | 3 | One run passed every mark. The judge put the other runs' four failures down to the test: its checker looked for soldiers' logs in one folder and misread the closing question. No fault in the skill |
| **Unseen 2** | A new setting, written by a fresh session with round 1's lessons as rules | 3 | Every run settled each question at the right rank, consulted the general first and merged no card with a guessed value in place of the user's answer. In two runs the question to the user wasn't the last thing the captain said: the judge found the skill never said it must be. The checker misread the soldiers' advisor calls in all three runs; round 1's logs show soldiers made none |

**What changed in the skill as a result:**

- Every session starts with `env -u ANTHROPIC_API_KEY`, so it bills the user's plan
- The batch's mission goes into every brief, and an answer settled in a brief keeps the whole mission
- The coordinator names the kind of question before asking the user, and takes the general's advice on any other kind
- A card waiting on the user's answer isn't merged with a guessed value in its place: it stays on its branch until the user answers
- A batch keeps its state in `work/`: a progress file, every session's log, the briefs and the slot store
- The coordinator reports once every job is settled and every session has exited, puts the question last, and ends

**Still open:**

- **The question-last fix is unconfirmed.** The first real batch shows whether a captain now ends on its question and exits.
- **The side-session route hasn't been tested.** Its one risk is a side-session soldier calling the general, since side sessions take no launch flags.
- **Hand-built checkers misread runs in both unseen rounds,** so the next round of any test uses a shared checker, tested once, that each writer only fills in.

The rounds' records, with every step, fingerprint and verdict, are in `~/Projects/sandbox/chain-of-command-kit/`: `results-test1.md` for the practice runs, and `results-unseen-1.md` and `results-unseen-2.md` with their judges' verdicts.

### Test 2's result: Sonnet at high is the soldiers' sweet spot

Test 2 ran on 2026-11-06 through `/sealed-relay`: a fresh writer built three cards in a new setting, with their hidden tests and marking guides, and a blind scorer marked each run's work from copies that carry no sign of the setting. **All fifteen runs passed every hidden test, so every setting qualifies. Above Sonnet at medium, quality is flat, and Sonnet at high does that work for the least use.**

| Setting | Quality by run (average of three cards) | Average quality | Spread | Use per finished card | Soldiers' use per finished card |
|:--------|:----------------------------------------|:----------------|:-------|:----------------------|:--------------------------------|
| **Sonnet, medium** | 7.7, 8.7, 8.0 | 8.11 | 1.00 | 0.33 | 0.20 |
| **Sonnet, high** | 9.0, 9.0, 8.7 | 8.89 | 0.33 | 0.46 | 0.23 |
| **Sonnet, xhigh** | 9.3, 9.0, 9.0 | 9.11 | 0.33 | 0.62 | 0.37 |
| **Opus, medium** | 8.7, 9.3, 8.3 | 8.78 | 1.00 | 0.53 | 0.33 |
| **Opus, high** | 8.7, 9.3, 9.0 | 9.00 | 0.67 | 0.53 | 0.37 |

Use is weighted use against the first wave's Sonnet-at-medium run set at 1.0, shared across its three cards; the soldiers' column leaves out the captain and the general.

**How the decision rule settles it:**

- **The best average is Sonnet at xhigh's, 9.11.** Sonnet at high is 0.22 behind it, inside a noise of 0.33; Opus at medium is 0.33 behind, inside 0.67; Opus at high is 0.11 behind, inside 0.50. Those three tie with the best.
- **Sonnet at medium falls outside.** It is 1.00 behind, against a noise of 0.67. It scored 7 on card C in all three runs, the one score that repeats below 8 anywhere in the test.
- **Of the four that tie, Sonnet at high uses least,** on total use and on the soldiers' own use alike: Opus at medium's soldiers use about 45% more, and Sonnet at xhigh's and Opus at high's about 60% more, for the same quality.
- **Opus at xhigh's follow-up isn't triggered.** Opus at high is 0.22 ahead of Opus at medium, inside a noise of 0.83.

**What the result rests on:**

- **The captain's use varies by chance more than the soldier settings do.** Every captain ran on Opus at high, yet its share of a run ranged from 0.36 to 1.04. Total use carries that chance with it, so the soldiers' own use sits beside it; here both pick the same setting.
- **The three cards may be too easy to separate the higher settings.** A flat 9 fits two readings: the higher levels add nothing to this kind of work, or these cards can't show a difference. The [hard-card round](#the-hard-card-round-every-setting-solved-the-hard-card-so-it-couldnt-separate-them) below set out to tell the two apart, and every setting solved its card, so the question stays open.

The round's record, with every run's checker lines, scores, use and fingerprints, is `~/Projects/sandbox/chain-of-command-kit/results-test2.md`; the hard-card round's is `results-test2-hard-card.md` beside it.

### The hard-card round: every setting solved the hard card, so it couldn't separate them

The hard-card round ran on 2026-11-06 to test whether Test 2's three cards were too easy to show what the higher settings add. A fresh writer built one card in a new setting whose obvious solution looks right and is subtly wrong, with 20 hidden tests in three tiers of difficulty, and checked that its own obvious solution scored in the agreed range of 6 to 10 out of 20 before committing. One wave ran the card at six settings side by side.

| Setting | Hidden tests passed | Quality out of 10 | Soldiers' use |
|:--------|:--------------------|:------------------|:--------------|
| **Sonnet, medium** | 20/20 | 10 | 0.18 |
| **Sonnet, high** | 20/20 | 9 | 0.31 |
| **Sonnet, xhigh** | 20/20 | 9 | 0.96 |
| **Opus, medium** | 20/20 | 10 | 0.39 |
| **Opus, high** | 20/20 | 8 | 0.53 |
| **Opus, xhigh** | 20/20 | 10 | 1.01 |

Use is on the same scale as Test 2's: Test 2's first Sonnet-at-medium run set at 1.0.

**Every setting passed every hidden test, so under the round's own rule the card was mis-set and the round measured nothing on the hidden tests.** Sonnet at high matched the best, which keeps it the default, but the question of whether harder work needs a stronger setting stays open. The quality scores, one run each, sit between 8 and 10 in no order by setting, and the soldiers' use rises with effort as in Test 2, from 0.18 at Sonnet at medium to 1.01 at Opus at xhigh.

**A writer can't set a card's difficulty with its own obvious solution.** The obvious solution it wrote on purpose failed in the way the pass marks asked, but every coding session, with the card's tests and time to work, went past it. A card's difficulty only shows in a real run, so a future hard card is checked against a real Sonnet-at-medium soldier run before the wave starts. Real batches are the cheaper check: if a batch on Sonnet at high hands in weak work on a hard card, that card is the next hard-card round.

The round's record is `~/Projects/sandbox/chain-of-command-kit/results-test2-hard-card.md`, with its pass marks in `pass-marks-test2-hard-card.md`.

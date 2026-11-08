# Each rank's model, effort and advisor setting

> **AI Assistant Note**: Read this when starting, resuming or costing a session in a batch. It holds the settings each rank runs on and the flags that apply them; [the chain of command](chain-of-command.md) holds the reasons.

## 🚨 Quick reference

| Rank | Model | Effort | Advisor | Set by |
|:-----|:------|:-------|:--------|:-------|
| **General** | `fable` | Not set by the batch | — | `advisorModel` in the user's settings, or `/advisor fable` |
| **Captain** | `opus` | `high` | `fable` | The user, when starting the batch's session |
| **Soldier** | `sonnet` for focused work where the plan is known; `opus` where the plan is worked out during the work | `high` | Off | The captain, in the soldier's launch command |
| **Inspectors** | The model each review workflow names | The workflow's own | — | The review workflow, whatever the soldier runs on |

## The soldier runs at high effort with the advisor off

A soldier started as a background `claude -p` session takes its settings and its billing on its launch line. `scripts/launch_jobs.py` builds this line for each job's first start; a resume builds it by hand:

```bash
cd <checkout> && env -u ANTHROPIC_API_KEY CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1 \
  claude -p "$(cat <brief>)" \
  --model sonnet --effort high \
  --dangerously-skip-permissions --output-format stream-json \
  --verbose > <main checkout>/work/runs/<batch>/logs/<holder name>.jsonl \
  2> <main checkout>/work/runs/<batch>/logs/<holder name>.err
```

`CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` switches the advisor off for that session alone. Without it the soldier inherits `advisorModel` from the user's settings, and Sonnet 5.5 accepts Fable as an advisor, so the soldier consults Fable directly and pays Fable's rates. `env -u ANTHROPIC_API_KEY` removes an API key the shell has loaded, such as one a project's `.envrc` reads from `~/.env`. Without it the session bills the key at API rates instead of logging in through the user's Claude plan. Resume a soldier with the same environment, model and effort.

A soldier started as a side session takes no launch flags, so its brief tells it to bring every question to the coordinator rather than to `/advisor`.

## The captain runs at high effort with Fable as advisor

```bash
env -u ANTHROPIC_API_KEY claude --model opus --effort high
```

The advisor comes from `"advisorModel": "fable"` in `~/.claude/settings.json`. Opus 5.5 accepts Fable as an advisor; Claude Code drops an advisor the main model doesn't accept without raising an error, so check `/advisor` names Fable at the start of a batch.

## Sonnet at high effort is the soldiers' sweet spot

Sonnet 5.5 costs $2 per million input tokens and $10 per million output tokens, half the rate of Opus 5.5; every model's rates are in [what each model costs](model-costs.md). The per-token saving doesn't settle the cost of a card, because a higher effort spends more tokens on it, so [Test 2](testing-the-chain-of-command.md#test-2-the-soldiers-sweet-spot-is-where-more-effort-stops-improving-the-work) ran the same three cards at five settings, three times each, on 2026-11-06.

Every setting passed every hidden test. Above Sonnet at medium, quality was the same within chance, and Sonnet at high used the least of those settings: Opus at medium's soldiers used about 45% more, and Sonnet at xhigh's and Opus at high's about 60% more, for the same quality. Sonnet at medium used less again but scored lower on one card in every run. A follow-up on one hard card at six settings ended with every setting solving it, so it couldn't show whether harder work needs a stronger setting; until a real batch shows weak work on a hard card, Sonnet at high runs every planned card. Work whose plan is worked out during the work still goes to Opus, at the same effort: no test has measured that kind of card.

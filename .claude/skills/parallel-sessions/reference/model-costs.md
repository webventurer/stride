# What each Claude model costs per million tokens

> **AI Assistant Note**: Read this when choosing a rank's model or working out what a soldier's card cost. Prices are Anthropic's first-party API rates in US dollars, taken from the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing) on 5 November 2026; check that page before relying on them for a decision.

## 🚨 Quick reference

| Model | Input | Cache write, 5 minutes | Cache write, 1 hour | Cache read | Output |
|:------|------:|-----------------------:|--------------------:|-----------:|-------:|
| **Fable 5.1** | $10 | $12.50 | $20 | $0.25 | $50 |
| Fable 5 | $10 | $12.50 | $20 | $1 | $50 |
| **Opus 5.5** | $4 | $5 | $8 | $0.20 | $20 |
| Opus 5, 4.8, 4.7, 4.6, 4.5 | $5 | $6.25 | $10 | $0.50 | $25 |
| **Sonnet 5.5** | $2 | $2.50 | $4 | $0.10 | $10 |
| Sonnet 5 | $2 | $2.50 | $4 | $0.20 | $10 |
| Sonnet 4.6, 4.5 | $3 | $3.75 | $6 | $0.30 | $15 |
| **Haiku 5.5**, prompts up to 100,000 tokens | $0.10 | $0.125 | $0.20 | $0.01 | $0.50 |
| Haiku 5.5, prompts over 100,000 tokens | $0.50 | $0.625 | $1 | $0.05 | $2.50 |
| Haiku 4.5 | $1 | $1.25 | $2 | $0.10 | $5 |

The four models in bold are the current generation. A cache write costs 1.25 times the input price for a 5-minute cache and twice the input price for a 1-hour cache. A cache read costs a tenth of the input price, except on Fable 5.1 (a fortieth) and on Opus 5.5 and Sonnet 5.5 (a twentieth).

## Fast mode and batches change the price

| Option | Opus 5.5 input | Opus 5.5 output | Applies to |
|:-------|---------------:|----------------:|:-----------|
| **Fast mode** | $8 | $40 | Opus 5.5, Opus 5 and Opus 4.8 (Opus 5 and 4.8 at $10 and $50) |
| **Batch API** | $2 | $10 | Every model: half the input and output price, for requests that can wait |

Asking for US-only inference adds 10% to every price on Claude 4.6 and later models.

## An advisor call is priced as the advisor's model

A soldier's log records each advisor call as an `advisor_message` entry under the advisor's model. One Fable call on card WB-896 read 107,071 tokens and wrote 13,686: $1.75 at Fable 5.1's rates, against $0.35 for the same tokens on Sonnet 5.5.

## A session's cost is an estimate at these rates

The `result` line at the end of a `claude -p` log carries `total_cost_usd`, Claude Code's estimate of the session's cost at these rates; a resumed session's figure includes its earlier spend. On a subscription plan the session isn't billed per token, so the figure measures how much of the plan's usage a card takes rather than money spent.

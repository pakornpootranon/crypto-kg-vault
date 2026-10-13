---
type: schema
tags:
  - schema
---

# Horizon scoring: short-term vs long-term
Two separate scores per token, because a good trade and a good hold are different things. Extends [[Schema - Scoring Rubric]] (the four original families are reused, nothing is thrown away). Computed by `python3 scripts/kg.py rank`.

## Short-term score ST (1 to 4 weeks, max 20)
ST = `score_momentum` + `score_flows` + `score_sentiment` + `score_catalysts`

| Field | Who sets it | 0 | 3 | 5 |
|---|---|---|---|---|
| score_momentum | `market.py update` (mechanical) | lagging BTC on 7d and 30d | beating BTC on 30d, flat 7d | beating BTC 30d by 20%+ and 7d by 8%+, turnover 5%+ of mcap |
| score_flows | weekly run (judgement) | outflows accelerating | stablecoin/TVL inflow to its chain | inflow + whale accumulation + falling exchange balances |
| score_sentiment | weekly run, Bigdata.com first | negative, deteriorating | neutral, attention rising | positive, sentiment z > 2 (also a crowding warning) |
| score_catalysts | weekly run | big unlock < 30d, nothing offsetting | neutral | several dated bullish catalysts, no unlock |

Penalties (applied by the script):
- Unlock inside 14 days: -3 if `unlock_pct_supply` >= 1, -2 if >= 0.3
- `extended: true` (30d > +100%): -1. Chasing a vertical chart is a separate bet
- `risk_flag` set (exploit, delisting, regulatory action, depeg): -2 on both horizons
- `liquidity_ok: false` (24h volume < $5 m): no short-term bucket at all

Every short-term pick in the weekly report must carry `st_setup` (breakout / catalyst run-up / reclaim / mean reversion), `st_entry` (zone) and `st_invalidation` (price or event that kills it). No invalidation, no pick.

## Long-term score LT (6 to 24 months, max 20)
LT = `score_fundamentals` + `score_adoption` + `score_tokenomics` + `score_narrative`

| Field | Who sets it | 0 | 3 | 5 |
|---|---|---|---|---|
| score_fundamentals | weekly run | no revenue, no usage | revenue growing, value accrual pending | revenue growing and reaching holders |
| score_adoption | weekly run, seeded by `hint_adoption` (TVL 7d + fees 30d trend) | users/TVL/fees shrinking | flat to growing | share gains, fees +25% |
| score_tokenomics | weekly run, seeded by `hint_tokenomics` (mc/FDV) | heavy unlock overhang, high inflation | moderate overhang | fully diluted or net deflationary via buyback/burn |
| score_narrative | weekly run | narrative dead or cooling | live narrative, crowded | early in a durable narrative tied to [[Thesis - 2027 Ethereum DeFi bull]] |

If a judgement field is blank the script falls back to the hint and marks it `~hint` in the Gaps column; blanks without a hint count 0 and show `?`. Fill gaps before trusting a rank.

## Buckets
| Bucket | Rule | Meaning |
|---|---|---|
| core (both horizons) | ST >= 13 and LT >= 13 | best of both; size normally |
| short-term setup | ST >= 13 | trade with an invalidation, not a hold |
| long-term accumulate | LT >= 13 | scale in on weakness, ignore weekly noise |
| quiet accumulation | fundamentals >= 4, sentiment <= 2 | good business nobody is talking about |
| narrative blow-off | sentiment 5, fundamentals <= 2 | crowded; only trade, never hold |
| fade | ST < 8 and LT < 8 | candidate for `status: dormant` after 4 weeks |
| watch | everything else | |

## Status lifecycle
`discovery` (new this week) > `watch` > `candidate` > `position` > `exit` or `dormant`. Status only moves on a written trigger in [[Watchlist Ranking]]; the score alone never moves it. `dormant` tokens are skipped by the ranker but keep their notes and edges.

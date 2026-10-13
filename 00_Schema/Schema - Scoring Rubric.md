---
type: schema
tags:
  - schema
---

# Scoring rubric (four signal families)
Matches the four families in the inflow radar: on-chain flows, news/sentiment, protocol fundamentals, catalysts and unlocks. Each is 0 to 5 in token frontmatter (`score_flows`, `score_sentiment`, `score_fundamentals`, `score_catalysts`). Composite is computed in [[Token Board]].

## score_flows (on-chain)
0 outflows accelerating; 2 flat; 3 stablecoin/TVL inflow to the protocol's chain; 4 inflow to the protocol itself; 5 inflow plus whale accumulation (Lookonchain) and falling exchange balances.

## score_sentiment (Bigdata first)
Use `bigdata_sentiment_tearsheet` where an entity resolves, otherwise a smart search and read tone.
- 0: negative and deteriorating (momentum < 0, attention z < -1)
- 2: neutral / fading attention (Aave on 2026-10-13)
- 3: neutral tone, rising attention
- 4: positive tone, normal attention
- 5: positive tone with sentiment z > 2 (Starknet on 2026-10-13). Note: 5 is also a crowding warning; pair with score_catalysts.

## score_fundamentals
0 no revenue, no usage; 2 usage, no value accrual (ARB); 3 revenue growing, accrual pending (MORPHO); 4 revenue growing, accrual partly on (AAVE); 5 revenue growing and reaching holders (UNI, HYPE).

## score_catalysts
0 large unlock inside 30 days with nothing offsetting; 2 unlock offset by a known catalyst; 3 neutral; 4 dated bullish catalyst inside 30 days (CME listing, buyback vote); 5 multiple dated catalysts, no unlock.

## Composite and action
- composite = flows + sentiment + fundamentals + catalysts (max 20)
- 15+: candidate for position; 10 to 14: candidate, wait for trigger; under 10: watch
- Divergence flag: fundamentals 4+ with sentiment 2 or less = "quiet accumulation" bucket (MORPHO, SKY, HYPE right now). Sentiment 5 with fundamentals 2 or less = "narrative blow-off" bucket (STRK).

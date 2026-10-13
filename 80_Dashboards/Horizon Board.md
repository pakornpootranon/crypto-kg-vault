---
type: dashboard
tags:
  - dashboard
---

# Horizon board
Short-term vs long-term ranks written by `python3 scripts/kg.py rank --write`. Rules in [[Schema - Horizon Scoring]]. Requires Dataview.

## Short-term setups (1 to 4 weeks)
```dataview
TABLE WITHOUT ID file.link AS Token, st_score AS ST, bucket AS Bucket, st_setup AS Setup, st_entry AS Entry, st_invalidation AS Invalidation,
  chg_7d AS "7d %", rs_btc_30d AS "RS 30d", unlock_next_date AS Unlock
FROM "30_Tokens"
WHERE type = "token" AND status != "dormant"
SORT st_score DESC
LIMIT 10
```

## Long-term accumulate (6 to 24 months)
```dataview
TABLE WITHOUT ID file.link AS Token, lt_score AS LT, bucket AS Bucket, lt_thesis AS Thesis,
  score_fundamentals AS Fund, score_adoption AS Adopt, score_tokenomics AS Tokenomics, score_narrative AS Narr, mc_fdv AS "MC/FDV"
FROM "30_Tokens"
WHERE type = "token" AND status != "dormant"
SORT lt_score DESC
LIMIT 10
```

## New this week (discovery)
```dataview
TABLE WITHOUT ID file.link AS Token, added_date AS Added, st_score AS ST, lt_score AS LT, mcap_usd_m AS "Mcap $ m"
FROM "30_Tokens"
WHERE status = "discovery"
SORT added_date DESC
```

## Risk flags and unlocks
```dataview
TABLE WITHOUT ID file.link AS Token, risk_flag AS Risk, unlock_next_date AS Unlock, unlock_pct_supply AS "% supply", extended AS Extended
FROM "30_Tokens"
WHERE risk_flag OR unlock_next_date OR extended = "true"
SORT unlock_next_date ASC
```

## Weekly reports
```dataview
TABLE WITHOUT ID file.link AS Report, regime AS Regime, date AS Date
FROM "90_Weekly"
WHERE type = "weekly"
SORT date DESC
```

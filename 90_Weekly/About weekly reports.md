---
type: note
tags:
  - weekly
---

# 90_Weekly
One `YYYY-Www Screener.md` report per Monday run, written by the scheduled task following [[How to - Weekly Screener Run]].

`data/` holds the machine history the ranker diffs against:
- `market-DATE.json` prices, RS vs BTC, TVL and fee trends (from `scripts/market.py update`)
- `discover-DATE.json` all-chain discovery scan (from `scripts/market.py discover`)
- `scores-DATE.json` ST/LT scores and buckets (from `scripts/kg.py rank --write`); next week's dWk column reads the latest one

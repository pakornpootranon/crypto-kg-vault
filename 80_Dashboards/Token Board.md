---
type: dashboard
tags:
  - dashboard
---

# Token board
Requires the Dataview community plugin.

```dataview
TABLE WITHOUT ID
  file.link AS Token, status, tier, social_heat AS Heat,
  score_sentiment AS Sent, score_fundamentals AS Fund, score_catalysts AS Cat,
  (default(score_sentiment,0) + default(score_fundamentals,0) + default(score_catalysts,0) + default(score_flows,0)) AS Composite,
  value_accrual AS "Value accrual", next_catalyst AS "Next catalyst"
FROM "30_Tokens"
WHERE type = "token"
SORT (default(score_sentiment,0) + default(score_fundamentals,0) + default(score_catalysts,0) + default(score_flows,0)) DESC, social_heat DESC
```

## Divergence buckets
```dataview
TABLE WITHOUT ID file.link AS Token, score_fundamentals AS Fund, score_sentiment AS Sent, social_heat AS Heat
FROM "30_Tokens"
WHERE score_fundamentals >= 4 AND score_sentiment <= 2
```
Quiet accumulation above; narrative blow-off below.
```dataview
TABLE WITHOUT ID file.link AS Token, score_fundamentals AS Fund, score_sentiment AS Sent, next_catalyst AS "Next catalyst"
FROM "30_Tokens"
WHERE score_sentiment >= 5 AND score_fundamentals <= 2
```

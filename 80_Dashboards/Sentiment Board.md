---
type: dashboard
tags:
  - dashboard
---

# Sentiment board (Bigdata.com fields)
```dataview
TABLE WITHOUT ID
  file.link AS Token, bigdata_entity_id AS "Entity", sentiment_current AS "Sent", sentiment_momentum AS "Mom",
  sentiment_z_1m AS "Sent z1m", attention_momentum_pct AS "Attn mom %", attention_z_1m AS "Attn z1m", sentiment_date AS "As of"
FROM "30_Tokens"
WHERE sentiment_date != ""
SORT sentiment_z_1m DESC
```

## Tokens with no usable sentiment yet
```dataview
LIST bigdata_entity_note
FROM "30_Tokens"
WHERE sentiment_date = ""
```

---
type: schema
tags:
  - schema
---

# Node types
One note = one node. The file name is the node id, so wikilinks must match file names exactly. `type` in frontmatter is the node label.

| type | folder | what it is | key properties |
|---|---|---|---|
| chain | 10_Chains | L1, L2, app-chain | layer, stack, native_token, social_heat |
| protocol | 20_Protocols | the business (like a company) | category, token, bigdata_entity_id, lending_share_pct, fee_switch |
| token | 30_Tokens | the tradeable claim (like a ticker) | status, tier, social_heat, price_usd, sentiment_*, attention_*, score_*, value_accrual, next_catalyst |
| narrative | 40_Narratives | a story capital is rotating into or out of | heat (1 to 5), stage, direction |
| entity | 50_Entities | people, firms, research houses, data sources | kind, stance |
| event | 60_Events | dated catalyst, unlock, incident, research note | date, kind, impact, direction, status |
| thesis | 70_Research | your own standing view | horizon, conviction, kill_switches |

## Token status vocabulary
- `watch`: in the graph, no action
- `candidate`: scored, could become a position on a trigger
- `position`: held (set this yourself; the seed vault ships with no positions)
- `avoid`: explicitly excluded (keep the note so the graph remembers why)

## Tiers
1 = blue chip, 2 = established mid-cap, 3 = speculative / context

## social_heat (1 to 5)
Subjective composite of Bigdata attention z-score, Stocktwits chatter level, and how often the name shows up in weekly gainer lists. Re-set every update.

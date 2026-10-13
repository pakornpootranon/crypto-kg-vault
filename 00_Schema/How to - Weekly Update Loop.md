---
type: schema
tags:
  - schema
  - howto
---

# Weekly update loop (Monday, after the chip-kg screener)
Superseded for the automated run by [[How to - Weekly Screener Run]], which adds market data, all-chain discovery and short/long-term ranking. This note stays as the manual version.

Same pattern as chip-kg: news enters as *proposed* edges and event nodes, never silent rewrites.

1. Run the narrative scan queries in [[Bigdata Query Cookbook]].
2. For every dated item, create a note in `60_Events` from `_templates/event`. Set `status: upcoming` or `happened`.
3. Add `affects::` edges from the event to tokens, `part_of::` to narratives.
4. For each `candidate` and `position` token, run [[How to - Pull Bigdata Sentiment]] and update the sentiment fields and `snapshot_date`.
5. Re-score the four families; update `status` only on a trigger written in [[Watchlist Ranking]].
6. Narrative `heat`: +1 if two or more new events attached this week, -1 if none in two weeks.
7. Open [[Token Board]], [[Sentiment Board]], [[Catalyst Calendar]], [[Narrative Heat]]; write the week's read into [[Weekly Log]].
8. Run `python scripts/kg.py stats` and `python scripts/kg.py check` to catch dangling links.

Anything the research cannot confirm stays tagged `[[VERIFY: ...]]` and shows up in the Verify Queue dashboard.

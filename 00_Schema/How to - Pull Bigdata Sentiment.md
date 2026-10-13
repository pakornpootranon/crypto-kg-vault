---
type: schema
tags:
  - schema
  - howto
---

# How to pull sentiment from Bigdata.com for a crypto token
Bigdata's knowledge graph is company-centric. Tokens map to one of three entity classes, and only some give a usable `bigdata_sentiment_tearsheet`. Record the working ID in the token note's `bigdata_entity_id` and what it is in `bigdata_entity_note`.

## Three entity classes
1. **Owner company** (best): `Aave Sagl` C49D02, `StarkWare Ltd.` D2I3AN, `Morpho Labs SAS` SFBBUN, `Pendle Finance Inc.` 65J94F, `Chainlink Labs Ltd.` FTJ76O, `Offchain Labs Inc.` UBXYMO. Tearsheet returns quantitative sentiment, attention and a 90-day evidence table.
2. **Product proxy** (usable): HYPE resolves to `21Shares Hyperliquid Staking ETP` EE3703. Sentiment is about HYPE flow even though the entity is an ETP.
3. **Unresolved or empty** (fallback): Uniswap (find_securities returns a French supermarket, TM0ANJ), `Ethena GmbH` 55SK7Y (no coverage), `Defi Ltd.` V4LM1K for Lido and `U7YI88` for EigenLayer (no tagged chunks in the last month). Use a smart `bigdata_search` and read tone from the chunks; also check Stocktwits sentiment zones quoted inside articles.

## Procedure (per token, weekly)
1. `find_securities(query="<project name>", listing_type="PRIVATE")`. Read the description; keep the one that says "owner of ... token".
2. `bigdata_sentiment_tearsheet(rp_entity_id)`. Copy into frontmatter: `sentiment_current`, `sentiment_baseline`, `sentiment_momentum`, `attention_momentum_pct`, `attention_z_1m`, `sentiment_z_1m`, `sentiment_date`.
3. If "No Coverage": `bigdata_search` smart mode, text like "<Project> <TOKEN> token news and sentiment in the last month". Check `audit.queries[].filters.entity` for the ID the search resolved (this is how EE3703 and U7YI88 were found). Retry fast mode with that ID in `any_of` if chunks are thin.
4. Paste the 2 to 3 strongest bullish and risk drivers into the token note with `[Source - MMM DD, YYYY](url)` citations.
5. Re-set `social_heat` and `score_sentiment` per [[Schema - Scoring Rubric]].

## Pitfalls seen in this build
- `all_of` with two entities starves results; use `any_of`.
- Smart search auto-adds a 30-day window; widen with fast mode `timestamp` if a name has little coverage.
- Presale spam (Pepeto, Remittix) pollutes "trending DeFi" searches; filter by `document_type NEWS` and ignore GLOBE NEWSWIRE promo.

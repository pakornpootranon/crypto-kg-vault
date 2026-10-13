# crypto-kg-vault

Foundation Obsidian vault for an Ethereum and L2 DeFi knowledge graph, seeded 2026-10-13 from Bigdata.com. Built to the same pattern as the chip-kg stock screener: nodes are notes, edges are typed inline fields, news enters as event nodes and proposed edges, Claude reads the graph to rank the watchlist.

## Open it
1. Obsidian > Open folder as vault > this folder.
2. Install community plugin **Dataview** (required for `80_Dashboards`). Optional: **Breadcrumbs** or **Juggl** to render the typed edges, **Templater** for `_templates`.
3. Start at `80_Dashboards/Token Board.md`, then `70_Research/Watchlist Ranking.md`.

## Layout
```
00_Schema/       node and edge vocabulary, scoring rubric, Bigdata how-tos and query cookbook
10_Chains/       Ethereum, Arbitrum, Base, Optimism, Starknet, Unichain, Robinhood Chain, Arc, Hyperliquid L1, Polygon, Solana
20_Protocols/    Aave, Uniswap, Morpho, Ethena, Pendle, Lido, EigenLayer, Chainlink, Ondo, Sky, Securitize
30_Tokens/       20 tokens (ETH, AAVE, UNI, MORPHO, ENA, PENDLE, LDO, EIGEN, LINK, ONDO, SKY, ARB, OP, STRK, POL, HYPE, ZEC, NEAR, VVV, QNT)
40_Narratives/   13 narratives with heat, stage, direction and beneficiary edges
50_Entities/     research houses, founders, operators, data sources
60_Events/       dated catalysts, unlocks, incidents (status: upcoming / happened)
70_Research/     2027 thesis, watchlist ranking, weekly log
80_Dashboards/   Dataview boards: tokens, sentiment, catalysts, narrative heat, verify queue, graph queries
_templates/      one template per node type
scripts/kg.py    stdlib-only graph loader: stats, neighbors, paths, finds, link check, JSON export
```

## Conventions
- File name = node id. Wikilinks must match exactly.
- Edges: `- relation:: [[Target]]` under `## Edges`. Relation names from `00_Schema/Schema - Edge Types.md`.
- Unconfirmed facts stay as `[[VERIFY: ...]]` links; they are listed by `scripts/kg.py verify`.
- Citations: `[Source - MMM DD, YYYY](bigdata url)`. Prices and metrics carry a date.
- Sentiment fields come from `bigdata_sentiment_tearsheet`; see `00_Schema/How to - Pull Bigdata Sentiment.md` for which entity ID works per token.

## What is seeded with real data vs placeholder
- Real Bigdata sentiment: AAVE (C49D02), STRK (D2I3AN), HYPE (EE3703 proxy). Ethena GmbH returned no coverage.
- Real prices/metrics (dated): ETH, AAVE, UNI, ARB, STRK, ENA, HYPE, Ethereum chain stats, Uniswap fees, Aave share data, Robinhood Chain numbers.
- Placeholder: on-chain flow scores for all tokens; prices for MORPHO, LDO, EIGEN, LINK, ONDO, SKY, OP, PENDLE, POL, QNT.

## Weekly loop
`00_Schema/How to - Weekly Update Loop.md`. Suggested cadence: Monday after the chip-kg screener, Bigdata first, web second.

## Disclaimer
Educational research tooling, not investment advice. Snapshot data is dated 2026-10-13 and goes stale quickly; prices, scores and rankings are illustrative of the method. Crypto assets are volatile and several names here are speculative. Verify everything marked `[[VERIFY: ...]]` and do your own research.

## Data and links
The seed notes summarise (paraphrase) news and research surfaced through Bigdata.com. Links of the form `app.bigdata.com/documents/...` open only for Bigdata.com subscribers. The vault works without them; to refresh the sentiment fields you need your own Bigdata.com access or can substitute another source. See `00_Schema/How to - Pull Bigdata Sentiment.md`.

## License
Vault structure, schema, templates and `scripts/kg.py`: MIT (see LICENSE). Third-party facts and quoted sources remain with their owners.

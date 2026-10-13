---
type: chain
name: Ethereum
snapshot_date: 2026-10-13
tags:
  - chain
layer: L1
native_token: "[[ETH]]"
defi_tvl_usd_b: 53.3
stablecoin_supply_usd_b: 146.5
stablecoin_share_pct: 47.5
monthly_fees_usd_m: 15.9
monthly_active_addresses_m: 10.3
social_heat: 4
---

# Ethereum
Settlement layer for the whole graph. Everything in `30_Tokens` is scored partly on whether it adds to, or drains from, Ethereum block space and ETH demand.

## Snapshot (Oct 2026)
- DeFi TVL about $53.3 b, DEX volume about $1.29 b/day [Analytics Insight - Oct 01, 2026](https://app.bigdata.com/documents/B1A1E290BFA799F252FCFFDB0755A4BF?cnum=1)
- Stablecoin supply about $146.5 b, 47 to 48% of on-chain supply; added $243 m in one October week [Crypto Briefing - Oct 09, 2026](https://app.bigdata.com/documents/F411F6425D320D5D1823B37C45945C79?cnum=1)
- September fees $15.9 m (+53% m/m), monthly active addresses 10.3 m (+6%) [21Shares - Oct 06, 2026](https://app.bigdata.com/documents/150886607272549850FFAC8301B80D00?cnum=6)
- Average transaction fee fell to $0.095 after Fusaka, higher blob throughput and 60 m gas limit [Benzinga - Sep 18, 2026](https://app.bigdata.com/documents/FC1B7C1AE003848E79FC3E81294238FE?cnum=2)
- Tokenized RWA on public chains above $31 b, about two thirds settle on Ethereum (BitMine/Bit Digital commentary, Aug 2026)

## Why it matters for the graph
- L2s now absorb execution; mainnet captures almost no "rent" from them (Base paid Ethereum about $15 k in September vs $711 k to the Optimism Collective). The bull case is market share first, fee capture later [Anue - Oct 11, 2026](https://app.bigdata.com/documents/7D11EFCBA2C3437E006ED788DC842DF5?cnum=3)
- Economic density: roughly $200 k TVL per active user vs about $2.5 k on Solana (Raoul Pal, Oct 2026)

## Open questions
- [[VERIFY: does Fusaka-era fee compression hold when activity returns, or does it reprice ETH as "cheap block space"]]


## Edges
- native_token:: [[ETH]]
- rides_narrative:: [[Tokenization and RWA]]
- rides_narrative:: [[Stablecoin Settlement Layer]]
- rides_narrative:: [[L2 Consolidation and L1 Exit]]
- threatened_by:: [[Quantum Resistance]]
- competes_with:: [[Solana]]

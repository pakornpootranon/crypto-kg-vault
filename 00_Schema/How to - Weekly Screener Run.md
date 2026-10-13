---
type: schema
tags:
  - schema
  - howto
  - weekly
---

# Weekly screener run (playbook for the scheduled task)
Fires every Monday 07:50 Bangkok. The scheduled task points here, so editing this note changes the next run; no need to touch the task. Goal: every week, name the best **short-term setups** (1 to 4 weeks) and **long-term accumulation** names (6 to 24 months) from the vault, plus up to 5 **new coins from any chain**.

Rules that never bend:
- Bigdata.com is the primary research source (news, sentiment, catalysts). Web search only fills gaps (unlock schedules, on-chain dashboards). CoinGecko and DefiLlama are used through the scripts for numbers only.
- News enters as event nodes and proposed edges, never silent rewrites. Unconfirmed facts stay `[[VERIFY: ...]]`.
- Every token is ranked every week. No pick without an invalidation.
- Do not use git inside the vault (the run cannot delete lock files). History lives in `90_Weekly/data/*.json`.
- Not investment advice; write caveats plainly.

## Step 0. Setup
Vault root is the `crypto-kg-vault` folder. Let `W` = ISO week label (`date +%G-W%V`) and `D` = today.
Read: [[Schema - Horizon Scoring]], last week's report in `90_Weekly/`, [[Watchlist Ranking]], [[Thesis - 2027 Ethereum DeFi bull]].

## Step 1. Market data (mechanical, about 1 minute)
```
python3 scripts/market.py update
python3 scripts/market.py discover
```
If the shell has no network, run the same scripts in the cloud workspace on a copy and carry back only the JSON + changed token notes. If CoinGecko rate-limits (429), wait 60 s and retry once; then continue with whatever came back and say so in the report.

## Step 2. Market regime (Bigdata.com)
3 to 4 smart searches, one aspect each: Bitcoin and Ethereum price drivers this week; crypto ETF flows this week; stablecoin supply and funding/leverage this week; macro or regulatory event that moved crypto this week. Write a 3-line regime read: risk-on / neutral / risk-off. In risk-off, short-term picks are capped at 2.

## Step 3. Update existing tokens
For each token with status `candidate`, `position`, or tier 1 (others only if their price moved more than 20% on 7d):
1. `bigdata_sentiment_tearsheet` where `bigdata_entity_id` works (see [[How to - Pull Bigdata Sentiment]]); else one smart search on the token's news this week. Update sentiment fields, `sentiment_date`, `score_sentiment`.
2. One smart search for catalysts and unlocks in the next 30 days. Set `unlock_next_date`, `unlock_pct_supply`, `next_catalyst`, `score_catalysts`. New dated items become `60_Events` notes from `_templates/event` with `affects::` edges.
3. Set `score_flows` from what is evidenced (ETF/ETP flows, exchange balances, whale reports, stablecoin inflow to its chain). If nothing is evidenced, leave it blank rather than guessing.
4. Long-term fields: confirm or adjust `score_adoption` (start from `hint_adoption`), `score_tokenomics` (start from `hint_tokenomics`, adjust for buybacks, emissions, unlocks), `score_fundamentals`, `score_narrative`. Change them only with a reason written under `## Weekly notes` in the token note (`- D: reason`).
5. Set `risk_flag` for exploits, depegs, delistings, enforcement. Clear it when resolved.

## Step 4. Discovery (all chains, max 5 new nodes)
From `90_Weekly/data/discover-D.json` (momentum leaders, CoinGecko trending, DefiLlama fee growth) shortlist up to 10. For each, one Bigdata.com smart search ("why is X rising this week", "X protocol revenue and token value accrual"). Promote at most 5 that have (a) mcap >= $150 m and 24h volume >= $10 m, and (b) an identifiable driver: a real catalyst, revenue growth, or a narrative already in `40_Narratives`. Skip pure memes without a driver, and say so in the report.
For each promoted coin:
```
python3 scripts/market.py add SYMBOL coingecko_id "Name"
```
then fill sentiment/catalyst/LT fields, add `rides_narrative::` edges (create a narrative note if it is genuinely new), and set `status: discovery`. Run `python3 scripts/market.py update` again so the new notes get market fields.

## Step 5. Rank
```
python3 scripts/kg.py rank --write
python3 scripts/kg.py check
```
Then for the top short-term names, write `st_setup`, `st_entry`, `st_invalidation`; for the top long-term names write `lt_thesis` (one line). Review buckets against judgement; if you disagree with the math, say why in the report rather than editing scores to force a result.
Status changes: apply only triggers already written in [[Watchlist Ranking]]. Tokens in `fade` for 4 straight weekly score files go to `status: dormant`.

## Step 6. Write outputs
1. `90_Weekly/W Screener.md` (e.g. `2026-W42 Screener.md`) using the structure below.
2. Replace the table in [[Watchlist Ranking]] with this week's ST and LT ranks (keep the trigger column).
3. Append a dated section to [[Weekly Log]]: searches run, notes created, scores changed, open VERIFY items.
4. Narrative `heat`: +1 if 2+ new events attached this week, -1 if none in two weeks.

### Report structure
```
---
type: weekly
week: W
date: D
regime: risk-on | neutral | risk-off
tags: [weekly]
---
# Crypto screener W
Purpose line. Data as of D; prices from CoinGecko, research from Bigdata.com.
## Regime (3 lines)
## Short-term setups (1 to 4 weeks), max 5
| Token | ST | Setup | Entry zone | Invalidation | Catalyst / date | Why now |
## Long-term accumulate (6 to 24 months), max 5
| Token | LT | Thesis line | What would break it | Accumulation plan |
## New this week (discovery)
## Moves vs last week (bucket changes, biggest score deltas)
## Avoid / crowded (blow-offs, unlock overhangs, risk flags)
## Full ranking (paste kg.py rank output)
## Caveats and open VERIFY items
## Sources (Bigdata.com citations as [Source - MMM DD, YYYY](url))
```
Write in English. Use `$100 m` / `$10 b` notation. No `---` separators in the body, no em dashes.

## Step 7. Notify
Final message of the run (this becomes the push notification): one line regime, top 3 short-term with invalidation, top 3 long-term, new coins added, and the report file name. Keep it under 900 characters.

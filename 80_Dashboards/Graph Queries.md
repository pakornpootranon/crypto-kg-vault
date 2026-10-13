---
type: dashboard
tags:
  - dashboard
---

# Graph queries (kg.py)
```
python scripts/kg.py stats
python scripts/kg.py node AAVE
python scripts/kg.py neighbors "Robinhood Chain Effect" --depth 2
python scripts/kg.py path STRK ETH
python scripts/kg.py find --type token --where status=candidate
python scripts/kg.py narrative "Fee Switch and Buybacks"
python scripts/kg.py events --upcoming
python scripts/kg.py check
python scripts/kg.py verify
python scripts/kg.py export graph.json
```

## Obsidian graph view colour groups (Settings > Graph view > Groups)
- `tag:#token` green, `tag:#protocol` blue, `tag:#chain` grey, `tag:#narrative` orange, `tag:#event` red, `tag:#entity` purple
- Filter `-path:_templates -path:80_Dashboards` to keep the graph clean

## Asking Claude
Open a token note and its narrative notes, then ask: "Given the edges in these notes and the latest Bigdata sentiment fields, which upcoming event changes the composite score most, and in which direction." The answer should cite node names; if it cannot, the graph is missing an edge.

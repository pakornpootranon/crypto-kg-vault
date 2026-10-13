---
type: schema
tags:
  - schema
---

# Edge types
Edges live in an `## Edges` section at the bottom of each note as Dataview inline fields:

```
- rides_narrative:: [[Tokenization and RWA]]
```

Obsidian's graph view draws them as plain links; Dataview and `scripts/kg.py` read the relation name. Keep relation names snake_case and from this list so queries stay predictable.

## Structural
- `built_on`, `deployed_on`, `uses_stack`, `hosts`, `operates`, `operated_by`, `owns`, `owned_by`
- `native_token`, `native_token_of`, `gas_token_of`
- `developed_by`, `founded_by`, `founded`, `leads`, `led_by`
- `depends_on` (oracle, collateral, yield source)
- `competes_with` (symmetric by convention; write it on both notes when it matters)
- `routes_swaps_via`, `yield_via`, `serves`, `uses`

## Narrative
- `rides_narrative` (token/protocol/chain -> narrative)
- `beneficiary`, `laggard`, `threatens`, `threatened_by`, `tailwind_for`, `headwind_for` (narrative -> token)
- `sub_narrative`, `anchored_on`, `promoted_by`, `promotes`, `enabled_by`

## Events and coverage
- `catalyst` (upcoming), `event` (happened), `risk` (event or narrative that hurts)
- `affects`, `part_of`, `source` (event -> token / narrative / entity)
- `covered_by`, `covers`, `issues_product_on`, `holds`, `incident_affected`, `resists`
- `thesis` (token -> research note)

## Rule
A new edge you cannot name from this list is a sign to either add the relation here first or to write it as prose. Unnamed links are fine for navigation; they just will not be queryable.

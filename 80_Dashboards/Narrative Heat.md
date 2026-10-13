---
type: dashboard
tags:
  - dashboard
---

# Narrative heat
```dataview
TABLE WITHOUT ID file.link AS Narrative, heat, stage, direction, beneficiary AS Beneficiaries, laggard AS Laggards
FROM "40_Narratives"
SORT heat DESC
```

## Which tokens ride the most hot narratives
```dataview
TABLE WITHOUT ID file.link AS Token, length(rides_narrative) AS "Narratives", rides_narrative
FROM "30_Tokens"
WHERE rides_narrative
SORT length(rides_narrative) DESC
```

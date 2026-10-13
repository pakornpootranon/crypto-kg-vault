---
type: dashboard
tags:
  - dashboard
---

# Verify queue
Everything tagged `[[VERIFY: ...]]` is a dangling link on purpose. This lists the notes that still contain one.

```dataview
LIST
FROM ""
WHERE contains(file.outlinks, [[VERIFY]]) OR econtains(string(file.outlinks), "VERIFY")
```

If Dataview cannot match the pattern on your version, run `python scripts/kg.py verify` instead.

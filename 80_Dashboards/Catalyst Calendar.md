---
type: dashboard
tags:
  - dashboard
---

# Catalyst calendar
```dataview
TABLE WITHOUT ID file.link AS Event, date, kind, impact, direction, affects
FROM "60_Events"
WHERE status = "upcoming"
SORT date ASC
```

## Last 30 days
```dataview
TABLE WITHOUT ID file.link AS Event, date, impact, direction, affects
FROM "60_Events"
WHERE status = "happened" AND date >= date(today) - dur(30 days)
SORT date DESC
```

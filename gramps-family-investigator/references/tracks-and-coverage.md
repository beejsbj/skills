# Tracks and Coverage

Read this when planning a campaign, auditing coverage, or deciding where the garden needs tending. Tracks are maps, not rails: they exist so no bed is forgotten, not to force session order.

## Coverage Status Vocabulary

Used for every track cell in `coverage-matrix.json`:

- `not_started` — no meaningful work yet.
- `candidate` — relevant but not the active focus.
- `in_progress` — actively being worked.
- `open_leads` — leads exist but are unresolved.
- `blocked` — a missing answer or access issue prevents progress.
- `ready_for_write_plan` — confident enough to propose Gramps writes.
- `written_to_gramps` — promoted to Gramps and verified.
- `needs_audit` — likely stale, contradictory, duplicated, or weakly sourced.

## The Seven Tracks

### Skeleton Tree

Goal: a navigable trusted skeleton. Check identity, relationships, rough birth/death/marriage facts, places, and confidence for immediate family, parents, grandparents, siblings, spouses, children.

### Interview Sources

Goal: use living memory while access exists. Check reachable people, what each likely knows, question sets, consent/context, oral-history source records, follow-ups.

### Evidence Intake

Goal: turn documents and media into classified evidence. Check documents, photos, certificates, IDs, grave photos, old messages, existing trees/GEDCOMs, OCR/transcription, media attachment, source quality.

### Identity Resolution

Goal: stop people and names from splitting or merging incorrectly. Check legal names, call names, nicknames, transliterations, duplicate people/families, relationship conflicts.

### Place and Timeline

Goal: keep geography and chronology coherent. Check villages/neighborhoods, addresses, migrations, schools/workplaces, graves, mosques/shrines, life events, timeline conflicts.

### Branch Campaigns

Goal: focused effort without losing the whole map. One branch, surname, person, place, migration story, missing parent pair, or date range at a time. Check branch focus, campaign goal, sources checked, open questions, and an explicit stopping condition.

### Cleanup and Audit

Goal: keep Gramps and the notebook trustworthy. Check unsourced facts, missing dates, duplicate people/places, stale leads, privacy review, report generation.

## Coverage Targets

A target in `coverage-matrix.json` is a person, family cluster, branch, place, or mystery. Each active target carries a status per track. Add a target when the investigation genuinely opens it; retire (status the target `dormant`) rather than delete when attention moves on.

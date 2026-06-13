# Templates

Use these when creating durable Design Lab methodology artifacts in a repo. These templates support the run; they are not the generated design system itself.

## DESIGN_MAP.md

```markdown
# Design Map

## Run Spine
- ...

## Artifact Mode
- chat-only audit | light durable handoff | full workflow

## Artifact Location
- ...

## Inventory Depth
- sample | focused | exhaustive

## Doctrine Compass
| Axis | Law | Pattern | Forbidden Move | Evidence |
|---|---|---|---|---|
| palette | ... | ... | ... | ... |
| typography | ... | ... | ... | ... |
| geometry | ... | ... | ... | ... |
| motion | ... | ... | ... | ... |
| interaction | ... | ... | ... | ... |
| composition | ... | ... | ... | ... |
| copy | ... | ... | ... | ... |
| assets | ... | ... | ... | ... |

## Source Map
- Design System File Source Map: ...
- Supporting archaeology: ...

## Taxonomy Map
| Layer | Source Of Truth | Current Scope | Closure Artifact |
|---|---|---|---|
| tokens | ... | ... | ... |
| primitives | ... | ... | ... |
| unique specimens | ... | ... | ... |
| compounds | ... | ... | ... |
| compositions | ... | ... | ... |

## Formalization Surfaces
| Surface | Role | Owns | Does Not Own |
|---|---|---|---|
| Design System File | visual truth | ... | runtime behavior |
| Live Style Guide | implementation proof | ... | visual source of truth when Figma is canonical |
| Repo components | runtime behavior | ... | raw visual decisions without token/taxonomy resolution |
| Code probes | behavioral truth checks | ... | full style-guide coverage |

## Gate And Audit Index
| Artifact | Role | Link | Current State |
|---|---|---|---|
| DESIGN_LOG.md | gate decision history | ... | ... |
| RAW_RECIPE_INVENTORY.md | pre-extraction raw grammar | ... | ... |
| PROMOTION_AUDIT.md | promote/prune/keep-local decisions | ... | ... |
| RESIDUE_PROOF.md | cross-cutting residue proof | ... | ... |
| COVERAGE_AUDIT.md | per-source coverage | ... | ... |

## Code Map
| Design Artifact | Code Target | Implementation Status | Proof |
|---|---|---|---|
| ... | ... | pending / implemented / deferred / blocked | ... |

## Current Finish Line
- ...
```

## DESIGN_INTAKE.md

```markdown
# Design Intake

## Inputs
- ...

## Current Stage
- ...

## Evidence
- ...

## Impressions
- ...

## Must Survive
- ...

## Must Change
- ...

## Unknowns
- ...

## Next Gate
- ...
```

## SURFACE_GATE.md

```markdown
# Surface Gate

## Evidence
- ...

## Figma Availability
- wanted: yes/no
- accessible: yes/no
- tool callable: yes/no/unknown
- authenticated/edit access: yes/no/unknown
- file/project: existing / create / unavailable

## Recommended First Extraction Surface
Design System File / no-Figma code workflow

## Visual Source-Of-Truth Surface
- ...

## Implementation Proof Surface
- ...

## Methodology Artifacts
- DESIGN_MAP.md
- DESIGN_LOG.md
- audits and gate packets

## Recommendation
- ...

## Alternatives Rejected
- ...

## Unresolved Risk
- ...

## Decision Needed
- ...

## Unblocks
- ...

## Gate Decision
accepted / continue / pause
```

## TAXONOMY_SCHEMA.md

```markdown
# Taxonomy Schema

This is not the Live Style Guide. It maps taxonomy, ownership, and source-of-truth decisions; rendered component truth lives in the Design System File, repo components, or Live Style Guide according to Surface Gate.

## Tokens
- ...

## Primitives
- ...

## Unique Specimens
- ...

## Compounds
- ...

## Compositions
- ...

## Anatomy Artifacts
- Inline in Design System File when available.
- Markdown summaries only when needed for handoff.

## Naming Rules
- Derived From Existing Repo
- New Names Introduced
- Casing / File Pattern
- Forbidden Naming Drift

## Artifact Ledger
| Source artifact | Layer | Source Of Truth | Resolution | Notes |
|---|---|---|---|---|
| ... | token / primitive / unique specimen / compound / composition | ... | promote / prune / keep local / unresolved / deferred | ... |
```

## REPOSITORY_CONVENTIONS.md

```markdown
# Repository Conventions

## Token Source Format
- CSS variables | JSON | TS/JS module | Figma variables/styles | framework-local | existing repo pattern

## Token Source Location
- ...

## Design System File
- none / create / existing: ...

## Primitive Component Location
- ...

## Unique Specimen / Compound Location
- ...

## Style-Guide Surface Location
- ...

## Live Style Guide Route Or Entry
- ...

## Verification Command
- ...

## Branch And Worktree State
- branch: ...
- dirty files: ...
- untracked files: ...

## Ignored / Generated Outputs
- ...

## Docs / Config Mismatches
- ...

## Edit Ownership
- user-owned changes to preserve: ...
- files safe to edit: ...
- files not safe to edit: ...

## Checkpoint Plan
- commit/checkpoint cadence: ...
- rollback handholds: ...

## Naming Case And File Pattern
- ...

## Evidence
- ...

## Recommendation
- ...

## Alternatives Rejected
- ...

## Unresolved Risk
- ...

## Decision Needed
- ...

## Unblocks
- ...

## Gate Decision
accepted / continue / pause
```

## RAW_RECIPE_INVENTORY.md

```markdown
# Raw Recipe Inventory

## Scope
- ...

## Inventory Depth
sample / focused / exhaustive

## Sources Inspected
- ...

## Inventory
| Raw recipe | Found in | Evidence | Candidate layer | Proposed resolution | Gate |
|---|---|---|---|---|---|
| ... | ... | ... | candidate token / primitive / unique specimen / compound / composition-only / drift | promote / prune / keep local / decide | ... |

## Repeated Grammar
- ...

## Singular But Important
- ...

## Drift
- ...

## Ready For Extraction
yes / no
```

## LAYER_CLOSURE.md

```markdown
# Layer Closure

## Layer
token / primitive / unique specimen / compound / composition

## Source Artifacts
- ...

## Source Of Truth
- ...

## Closure Checklist
| Check | Status | Proof | Linked Artifacts |
|---|---|---|---|
| source artifacts listed | pass/fail | ... | ... |
| raw recipes resolved or gate-parked | pass/fail | ... | ... |
| source of truth named | pass/fail | ... | ... |
| style-guide surfaces demonstrate, not define | pass/fail | ... | ... |
| coverage rows have Resolution | pass/fail | ... | ... |

## Per-Layer Closure Proof
Fill only the section for the layer being closed.

### Token Closure
| Check | Status | Proof | Linked Artifacts |
|---|---|---|---|
| token groups documented | pass/fail/n/a | ... | ... |
| semantic aliases documented | pass/fail/n/a | ... | ... |
| naming rules documented | pass/fail/n/a | ... | ... |
| allowed raw-value exceptions documented | pass/fail/n/a | ... | ... |
| token candidates from raw recipe inventory resolved | pass/fail/n/a | ... | ... |
| next layer has enough token vocabulary | pass/fail/n/a | ... | ... |

### Primitive Closure
| Check | Status | Proof | Linked Artifacts |
|---|---|---|---|
| primitive families have anatomy | pass/fail/n/a | ... | ... |
| APIs, states, and variants are named | pass/fail/n/a | ... | ... |
| token dependencies are named | pass/fail/n/a | ... | ... |
| primitives consume tokens or approved lower-level constants | pass/fail/n/a | ... | ... |
| style-guide surfaces import/demonstrate primitive source files | pass/fail/n/a | ... | ... |

### Unique Specimen Closure
| Check | Status | Proof | Linked Artifacts |
|---|---|---|---|
| singular-role justification exists | pass/fail/n/a | ... | ... |
| reusable material inside the unique specimen is resolved downward | pass/fail/n/a | ... | ... |
| unique specimen is marked to prevent accidental generalization | pass/fail/n/a | ... | ... |
| any local variations are named as local, not standard reusable variants | pass/fail/n/a | ... | ... |

### Compound Closure
| Check | Status | Proof | Linked Artifacts |
|---|---|---|---|
| child primitive and unique-specimen dependencies are explicit | pass/fail/n/a | ... | ... |
| slot contracts are explicit | pass/fail/n/a | ... | ... |
| compounds compose children instead of duplicating internals | pass/fail/n/a | ... | ... |
| repeated child patterns are promoted or gate-parked | pass/fail/n/a | ... | ... |

### Composition Closure
| Check | Status | Proof | Linked Artifacts |
|---|---|---|---|
| compositions use approved lower layers | pass/fail/n/a | ... | ... |
| composition-only content/orchestration/app state is separated from component grammar | pass/fail/n/a | ... | ... |
| residue proof has no unresolved cross-cutting grammar | pass/fail/n/a | ... | ... |

## Promote / Prune / Keep-Local Decisions
| Item | Decision | Reason | Gate |
|---|---|---|---|
| ... | promote / prune / keep local / gate-parked | ... | ... |

## Gate-Parked Decisions
| Decision | Gate | Owner | Date | Unblock Condition | May Advance? |
|---|---|---|---|---|---:|
| ... | Promotion Gate / Taxonomy Gate / Taste Gate | ... | YYYY-MM-DD | ... | yes/no |

Gate-parked decisions marked `May Advance: yes` permit next-layer work. They do not count as complete unless the item is out of scope or explicitly accepted as deferred at Finish Gate.

## Handoff To Next Layer
| Next layer may build from | Next layer must not assume yet | Proof | Linked Artifacts |
|---|---|---|---|
| ... | ... | ... | ... |

## Next Layer Readiness
ready / continue / pause
```

## STYLE_GUIDE_PLAN.md

```markdown
# Style Guide Plan

## Proof Surfaces
| Layer | Design System File Surface | Live Style Guide Surface | Status |
|---|---|---|---|
| tokens | ... | ... | pending / ready / deferred |
| primitives | ... | ... | pending / ready / deferred |
| unique specimens | ... | ... | pending / ready / deferred |
| compounds | ... | ... | pending / ready / deferred |
| compositions | ... | ... | pending / ready / deferred |

## Anatomy Requirements
| Artifact | Layer | Anatomy Location | Needed For |
|---|---|---|---|
| ... | primitive / unique specimen / compound / composition | Design System File / markdown summary / none | extraction / taste / handoff |

## Behavior Fidelity Boundaries
| Artifact | Behavior | Figma Enough? | Code Probe Needed? |
|---|---|---:|---:|
| ... | ... | yes/no | yes/no |

## Verification
- ...
```

## ANATOMY.md

```markdown
# Anatomy: <Artifact>

## Canonical Instance
...

## Source Of Truth
- Design System File node/frame/component: ...
- Code source, when runtime behavior matters: ...

## Part Tree
- ...

## Slot Map
| Slot | Required | Allowed Child Layers | Notes |
|---|---:|---|---|
| ... | yes/no | token / primitive / unique specimen / compound / content | ... |

## Token Dependencies By Part
| Part | Tokens |
|---|---|
| ... | ... |

## State Matrix
| State | Expected Change | Source Of Truth |
|---|---|---|
| rest | ... | ... |
| hover | ... | ... |
| focus | ... | ... |
| active | ... | ... |
| disabled | ... | ... |

## Variant Or Local Variation Axes
- ...

## Child Dependencies
- ...

## Forbidden Mutations
- ...

## Promotion Items
| Item | Decision Needed | Proposed Resolution |
|---|---|---|
| ... | ... | promote / prune / keep local / gate |

## Anti-Patterns Checked
- no behavior defined inside Anatomy
- no duplicated source component markup
- no local unique-specimen variations presented as standard reusable variants
```

## PROMOTION_AUDIT.md

```markdown
# Promotion Audit

## Raw Recipe Inventory Link
- See RAW_RECIPE_INVENTORY.md produced before extraction.

## New Items Found During Extraction
| Recipe | Found in | Candidate layer | Evidence | Proposed resolution |
|---|---|---|---|---|
| ... | ... | token / primitive / unique specimen / compound / composition-only / drift | ... | promote / prune / keep local / decide |

## Clear Promote
- ...

## Prune / Replace With Existing
- ...

## Keep Local
- ...

## Needs User Decision
- ...

## Recipe Gaps
- ...

## Residue Audit
- See RESIDUE_PROOF.md for pattern-by-pattern proof after rebuild.
```

## RESIDUE_PROOF.md

```markdown
# Residue Proof

## Scope
- ...

## Sources Searched
- ...

## Patterns Checked
| Pattern | Where Searched | Hit Count | Hits | Resolution |
|---|---|---:|---|---|
| raw hex colors | ... | 0 | ... | clean / promoted / pruned / kept local / gate |
| raw px outside tokens | ... | 0 | ... | clean / promoted / pruned / kept local / gate |
| raw durations/easings | ... | 0 | ... | clean / promoted / pruned / kept local / gate |
| raw cubic-bezier | ... | 0 | ... | clean / promoted / pruned / kept local / gate |
| repeated clip-paths | ... | 0 | ... | clean / promoted / pruned / kept local / gate |
| duplicated primitive internals | ... | 0 | ... | clean / promoted / pruned / kept local / gate |
| unmarked unique specimens | ... | 0 | ... | clean / promoted / pruned / kept local / gate |
| style-guide-surface-defined behavior | ... | 0 | ... | clean / promoted / pruned / kept local / gate |

## Justified Exceptions
- ...

## Gate-Parked Residue
| Item | Gate | Owner | Date | Unblock Condition |
|---|---|---|---|---|
| ... | ... | ... | YYYY-MM-DD | ... |

## Verdict
clean / hits-with-resolution / blocked
```

## COVERAGE_AUDIT.md

```markdown
# Coverage Audit

Coverage is per-artifact mapping. Every meaningful source input gets one row.

## Scope
- ...

## Source Artifacts
| Artifact | Type | In scope | Taxonomy layer | Surface role | Resolution | Proof |
|---|---|---:|---|---|---|---|
| ... | repo / file / screenshot / component / page / note / Design System File / Figma frame / style-guide surface | yes/no | token / primitive / unique specimen / compound / composition / n/a | visual truth / implementation proof / methodology support / reference only / out of scope | promoted / pruned / kept local / implemented / deferred / unresolved | ... |

## Unresolved Residue
- Link to RESIDUE_PROOF.md. This section should summarize, not replace, the cross-cutting residue scan.

## Deferred By Gate
- ...

## Completion Verdict
complete / continue / blocked
```

## ARCHAEOLOGY.md

```markdown
# Archaeology Pass

Visual archaeology uses this same template when the source is moodboards, screenshots, image references, sites, or Claude Design previews.

## Source Evidence
- ...

## Design Sources Of Truth
- ...

## Reference-Only Material
- ...

## Prior Attempts
- ...

## Git History Notes
- ...

## Repeated Grammar
- ...

## Drift / Dead Ends
- ...

## Candidate Raw Recipes
| Raw recipe | Source | Evidence | Likely layer |
|---|---|---|---|
| ... | ... | ... | token / primitive / unique specimen / compound / composition |

## Follow-Up Gates
- ...
```

## COMPONENT_EXTRACTION_PLAN.md

```markdown
# Component Extraction Plan

## Source Material
- ...

## Accepted Design Artifacts
| Artifact | Layer | Visual Source | Code Target |
|---|---|---|---|
| ... | primitive / unique specimen / compound / composition | Design System File / source repo / no-Figma workflow | ... |

## Extraction Order
1. ...

## Component API Decisions
- ...

## Token Dependencies
- ...

## Child Component Dependencies
- ...

## Style-Guide Surface Updates
- ...

## Verification
- ...
```

## DESIGN_LOG.md

```markdown
# Design Log

Append one row whenever a gate decision is made or reopened.

| Date | Gate | Decision | Artifact Link | Notes |
|---|---|---|---|---|
| YYYY-MM-DD | Surface / Scope / Intent / Doctrine / Repository Conventions / Taxonomy / Taste / Promotion / Finish | accepted / continue / pause / reopened | ... | ... |
```

## TASTE_CHECK.md

```markdown
# Taste Check

## What The Design Wants
- ...

## Evidence
- ...

## Tensions
- ...

## Options
- ...

## Recommendation
- ...

## Alternatives Rejected
- ...

## Unresolved Risk
- ...

## Decision Needed
- ...

## Unblocks
- ...

## Gate Decision
accepted / continue / pause
```

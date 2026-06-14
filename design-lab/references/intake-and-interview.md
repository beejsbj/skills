# Intake And Interview

Use this reference when the design material is incomplete, ambiguous, or spread across repos, screenshots, moodboards, old sites, text, metaphors, or partial implementations.

## Intake Router

Classify each input before acting:

- `repo`: inspect file structure, design assets, components, style tokens, routes/views, git history, and open docs.
- `old site`: inspect live/static pages, CSS, imagery, interaction patterns, and salvageable recurring ideas.
- `Claude Design HTML`: treat as visual reference, not production architecture.
- `moodboard/image`: extract palette, texture, density, typography, geometry, composition, tone, and repeated motifs.
- `words/metaphors`: translate into impressions and constraints, then verify with the user.
- `existing component`: inspect anatomy, props/API, CSS dependencies, state logic, token usage, and raw recipes.
- `partial style guide`: check whether it demonstrates source-of-truth components or duplicates them.
- `Figma / Design System File`: check Figma Availability, existing pages, variables/styles, component sets, frames, anatomy artifacts, and whether it is canonical for this run.

## Read-First Recon

Start read-only unless the user explicitly asks to implement. Gather:

- Existing tokens and CSS variables.
- Components and their boundaries.
- Style-guide surfaces or pages.
- Screenshots, assets, moodboards, reference folders.
- Notes, docs, TODOs, planning files.
- `.gitignore`, README/setup docs, package scripts, and config files that may disagree about routes, ports, or verification commands.
- Ignored/generated output folders, treated as excluded evidence unless the user explicitly names them.
- Git history themes: when did tokens, visual language, or components change?
- Current worktree status.

Do not flatten all evidence into one summary. Preserve source categories so later decisions can distinguish law, vibe, accident, and singular local artifact.

## Archaeology Pass

Use this for repos, old sites, forks, abandoned previews, or prior attempts before doctrine or extraction.

Read in this order:

1. current structure: routes/views, components, token files, style-guide/kitchen-sink files, docs, assets
2. `.gitignore` and obvious generated/cache output so source evidence is not polluted
3. current worktree status and branch names
4. README/config/script mismatches that affect verification or live preview
5. git history for token, CSS, component, and visual-language changes
6. deleted/renamed design files and old preview folders
7. fork/origin comparison when a repo was forked from a mentor/template

Output target:

```markdown
## Archaeology Pass

### Source Map
- ...

### Design Sources Of Truth
- ...

### Reference-Only Material
- ...

### Prior Attempts
- ...

### Repeated Grammar
- ...

### Drift / Dead Ends
- ...

### Generated / Ignored Outputs
- ...

### Docs / Config Mismatches
- ...

### Candidate Raw Recipes
- ...
```

Tie this output to `RAW_RECIPE_INVENTORY.md`; do not leave archaeology as a chat-only summary when extraction will follow.

## Visual Archaeology

Use this for moodboards, screenshots, image references, sites, and Claude Design previews.

Extract:

- palette swatches and semantic roles
- type pairings, weight/scale relationships, casing, and rhythm
- geometry repetitions: radii, clips, angles, strokes, proportions, density
- texture, lighting, shadow, glow, noise, material cues
- composition rituals: alignment, framing, hierarchy, viewport priority
- motion-implied cues: reveal direction, tempo, easing feel, gesture affordance
- repeated motifs and singular brand-defining artifacts that may become unique specimens

Output each finding as a candidate raw recipe with evidence and likely layer. Feed these rows into `RAW_RECIPE_INVENTORY.md`.

## Midstream Recovery

Use this when the user enters with an existing style guide, kitchen sink, Design System File, partially extracted component, or app integration already underway.

Read first:

- existing `TAXONOMY_SCHEMA.md`, `COVERAGE_AUDIT.md`, `PROMOTION_AUDIT.md`, `RESIDUE_PROOF.md`, and `LAYER_CLOSURE.md`
- current style-guide route/page, Design System File, and anatomy/style-guide helpers
- source-of-truth component folders, token files, and app entry points
- recent git history for extracted components, deleted preview files, and token changes
- open notes/TODOs that mention drift, recipe gaps, or unresolved gates

Skip or compress:

- broad Intent/Doctrine interviews when current doctrine already exists and still matches the evidence
- full archaeology when coverage/residue audits already identify source artifacts

Re-open earlier gates only when:

- doctrine conflicts with current implemented taste
- the source of truth is ambiguous or scattered
- a component/style-guide-surface boundary is unclear
- raw recipes appear in higher layers without promotion/prune decisions
- verification route or command is unknown

Midstream output should name the current layer, the last trustworthy gate, the next gate, and the shortest path to closure.

## Scope Gate

Run this after initial intake, and after Surface Gate when Figma is relevant, before doctrine or implementation. The goal is to prevent the workflow from silently expanding or stopping early.

Required outputs:

- `target surfaces`: repos, pages, screens, components, assets, files, or flows included in this run.
- `excluded surfaces`: relevant material intentionally out of scope.
- `source of truth`: where implementation should land, and which files are reference-only.
- `expected layer depth`: tokens only, tokens+primitives, through compounds, through compositions, or full style-guide completion.
- `completion proof`: concrete artifact that will demonstrate done-ness, such as a running style guide, schema, component extraction PR, or coverage audit.
- `allowed autonomy`: what the agent may decide without asking, and what needs user taste/check approval.
- `artifact mode`: chat-only audit, light durable handoff, or full workflow.
- `artifact location`: where durable methodology files should live if artifacts are created.
- `inventory depth`: sample, focused, or exhaustive.

Scope gate packet:

```markdown
## Scope Gate

### Evidence
- ...

### Included
- ...

### Excluded
- ...

### Source Of Truth
- ...

### Target Layer Depth
- ...

### Completion Proof
- ...

### Artifact Mode
- chat-only audit | light durable handoff | full workflow

### Artifact Location
- ...

### Inventory Depth
- sample | focused | exhaustive

### Recommendation
- ...

### Alternatives Rejected
- ...

### Unresolved Risk
- ...

### Requires User Decision
- ...

### Allowed Autonomy
- Agent may decide: obvious naming cleanup, local file organization that follows repo convention, documentation wording.
- User decides: taxonomy ambiguity, taste direction, promotion/prune choices that change the system grammar.

### Pending Scope Decisions
- ...

### Unblocks
- ...

### Gate Decision
- accepted | continue | pause
```

Cannot define scope branch:

- Default to the smallest reversible scope: tokens plus primitives for the most visually repeated in-scope material.
- Use `sample` inventory depth for scouting/pilots, then require focused or exhaustive inventory before extraction/layer closure.
- Mark unique specimens, compounds, and compositions as deferred unless they are needed to prove the primitive.
- Create `Pending Scope Decisions` and stop before irreversible extraction or route/file moves.

## Surface Gate

Run this before Scope Gate when Figma support is relevant or when the user mentions Figma. The goal is to choose the first formalization surface without pretending Figma is available just because a plugin exists.

If the user explicitly says not to use Figma for this run, record `wanted: no`, `accessible: not tested`, and choose the no-Figma code workflow. Do not call Figma tools merely because Figma was mentioned.

Required outputs:

- `Figma Availability`: whether the user wants Figma used and whether the agent can create/edit the Design System File.
- `Figma Trust State`: parked, probe-only, approved for scratch, or approved for production file.
- `first extraction surface`: Design System File when Figma is wanted and accessible; otherwise the current no-Figma code workflow.
- `visual source-of-truth surface`: where visual truth will live.
- `implementation proof surface`: Live Style Guide, reusable components, composition views, or code probes when implementation is in scope.
- `methodology artifacts`: `DESIGN_MAP.md`, gates, audits, and logs that support the run without becoming design artifacts.

Figma is accessible only when all are true:

- the user wants Figma for this run
- the relevant Figma tool is callable in the current environment
- authentication/access permits creating or editing the target file
- the target file exists or the agent can create it

If any condition fails, recommend the no-Figma code workflow unless the user wants to pause and fix Figma access.

Figma is still parked when:

- the user says not to use it
- the user does not trust the agent's Figma ability yet
- the connector can create files but canvas mutation or screenshot verification has not been proven
- the last Figma write was cancelled, failed, or could not be visually verified

In a parked state, the agent may run a separate Figma capability probe only if the user asks for one. The probe must use a scratch file, avoid existing production files, report exact tools/actions/blockers, and must not make Figma the Design Lab source of truth.

Surface gate packet:

```markdown
## Surface Gate

### Evidence
- ...

### Figma Availability
- wanted: yes/no
- accessible: yes/no
- tool callable: yes/no/unknown
- authenticated/edit access: yes/no/unknown
- file/project: existing | create | unavailable

### Figma Trust State
- parked | probe-only | approved-for-scratch | approved-for-production
- last capability proof: ...
- blocker: ...

### Recommended First Extraction Surface
- Design System File | no-Figma code workflow

### Visual Source-Of-Truth Surface
- ...

### Implementation Proof Surface
- ...

### Methodology Artifacts
- ...

### Recommendation
- ...

### Alternatives Rejected
- ...

### Unresolved Risk
- ...

### Decision Needed
- ...

### Unblocks
- ...

### Gate Decision
- accepted | continue | pause
```

## Repository Conventions Gate

Run this before extraction edits in a repo. Do not invent paths silently.

Resolve verification by reading `package.json` scripts, README docs, existing style-guide/storybook commands, or asking the user. Record the chosen command here before the Finish Gate.

Compare README/setup instructions against package scripts and framework config. Record mismatches such as a README port that differs from the configured dev server.

```markdown
## Repository Conventions Gate

### Evidence
- ...

### Token Source Format
- CSS variables | JSON | TS/JS module | framework-local | existing repo pattern

### Token Source Location
- ...

### Primitive Component Location
- ...

### Unique Specimen / Compound Location
- ...

### Style-Guide Surface Location
- ...

### Style-Guide Route Or Entry
- ...

### Verification Command
- ...

### Branch And Worktree State
- branch: ...
- dirty files: ...
- untracked files: ...

### Ignored / Generated Outputs
- ...

### Docs / Config Mismatches
- ...

### Edit Ownership
- user-owned changes to preserve: ...
- files safe to edit: ...
- files not safe to edit: ...

### Checkpoint Plan
- commit/checkpoint cadence: ...
- rollback handholds: ...

### Naming Case And File Pattern
- ...

### Recommendation
- ...

### Alternatives Rejected
- ...

### Unresolved Risk
- ...

### Decision Needed
- ...

### Unblocks
- ...

### Gate Decision
- accepted | continue | pause
```

## Interview Questions

Ask questions tied to evidence. Prefer 3-6 high-signal questions at a time.

Good question forms:

- "This shape appears in the drawer, tabs, and card labels. Is it a system law or an accident from one mockup?"
- "This color is used both as brand decoration and functional status. Should it be allowed to do both?"
- "The moodboard feels [adjective], but the current UI feels [different adjective]. Which impression should survive?"
- "Is this component intended as a reusable family, or is it a singular artifact?"
- "If this gets themed radically differently, what must stay recognizable?"

## Intent Gate

Fires once before doctrine. Captures the design's initial intent.

Before doctrine, produce:

- `impressions`: 5-10 adjectives or phrases, each backed by evidence.
- `must-survive`: forms, motions, voice, interaction rituals, or constraints that cannot be lost.
- `must-change`: drift, awkward inheritance, stale source, or ideas that no longer fit.
- `unknowns`: decisions requiring the user.

Do not proceed to doctrine until the user accepts or corrects the intent summary, unless they asked for autonomous assumptions.

Intent gate packet:

```markdown
## Intent Gate

### Evidence
- ...

### Impressions
- ...

### Must Survive
- ...

### Must Change
- ...

### Recommendation
- ...

### Alternatives Rejected
- ...

### Unresolved Risk
- ...

### Decision Needed
- ...

### Unblocks
- ...

### Gate Decision
- accepted | continue | pause
```

## Gate Packets

Use these packets when a gate is reached.

After the decision for any gate is accepted, continued, paused, or reopened, append a row to `DESIGN_LOG.md` with date, gate name, decision, artifact link, and notes.

### Doctrine Gate

```markdown
## Doctrine Gate

### Proposed Laws
- ...

### Evidence
- ...

### Recommendation
- ...

### Alternatives Rejected
- ...

### Unresolved Risk
- ...

### Decision Needed
- ...

### Unblocks
- ...

### Gate Decision
- accepted | continue | pause
```

### Promotion Gate

```markdown
## Promotion Gate: <recipe>

### Raw Recipe
- ...

### Proposed Resolution
- promote | prune | keep local

### Recommendation
- ...

### Evidence
- ...

### Alternatives Rejected
- ...

### Unresolved Risk
- ...

### Consequence
- ...

### User Decision Needed
- ...

### Unblocks
- ...

### Gate Decision
- accepted | continue | pause
```

### Finish Gate

```markdown
## Finish Gate

### Evidence
- ...

### Completion Proof
- ...

### Coverage Result
- ...

### Remaining Residue
- ...

### Deferred Decisions
- ...

### Alternatives Rejected
- ...

### Unresolved Risk
- ...

### User Decision
- accepted | continue | pause

### Decision Date
- ...

### Recommendation
- complete | continue | pause for decision

### Unblocks
- ...

### Gate Decision
- accepted | continue | pause
```

## Taste Gate

Fires whenever a visual direction would change after doctrine is set. Updates doctrine rather than replacing it.

Use taste gates before visual direction changes, not after a large implementation.

Taste gate output:

```markdown
## Taste Check

### What I Think The Design Wants
- ...

### Evidence
- ...

### Tensions
- ...

### Recommendation
- ...

### Alternatives Rejected
- ...

### Unresolved Risk
- ...

### Decision Needed
- ...

### Unblocks
- ...

### Gate Decision
- accepted | continue | pause
```

When the user reacts, update the doctrine or taxonomy rather than treating the reaction as loose preference.

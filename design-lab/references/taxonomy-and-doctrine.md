# Taxonomy And Doctrine

Use this reference to define design laws, classify artifacts, and ideate within a layer.

## Doctrine

Doctrine is the taste layer above tokens. It names rules that cannot be fully enforced by a linter.

Common doctrine categories:

- `palette`: what colors mean, where they are allowed, what is forbidden.
- `typography`: display/body/mono roles, casing, tracking, voice.
- `geometry`: spacing, radii, clipping, tilt, stroke caps, shadow grammar.
- `motion`: durations, easings, beat/tempo rules, reduced-motion behavior.
- `interaction`: hover, press, selected, disabled, focus, gestures, drawer behavior.
- `composition`: density, viewport priorities, content hierarchy, layout rituals.
- `copy`: tone, punctuation, symbols, labels, metadata separators.
- `assets`: when imagery, texture, icons, or generated assets are allowed.

Doctrine should distinguish:

- `law`: must hold across the system.
- `pattern`: reusable named way of achieving a law.
- `vibe`: useful intent but not enforceable yet.
- `local`: preserved singular or context-specific artifact.
- `drift`: artifact that should be pruned or rewritten.

## Taxonomy

Use these layers unless a repo already has a stronger local convention. `Specimen` means `unique specimen`; do not use it for generic documentation or inspection surfaces.

### Tokens

Values, semantic aliases, constraints, and named low-level patterns that do not render as standalone UI. Examples:

- color roles and semantic aliases
- type scale and type role shorthands
- spacing/radius/shadow/clip/rotation tokens
- motion durations/easings/keyframes
- data maps such as note labels or palette constants when they drive presentation

Decision test: "Could this be replaced by reading variables/constants?" If yes, it is token-layer.

### Primitives

Smallest named renderable ideas. They may be visual, control, or container primitives.

Examples:

- icon button, key, tab, knob, mark, sticker, card shell, drawer shell

Decision test: "Does it have a single identity and stand alone without named child components?" If yes, it can be primitive.

Primitive does not mean tiny. A drawer can be primitive if its job is a structural shell with slots and behavior.

### Unique Specimens

Singular preserved artifacts that matter to the system but should not become a reusable family. They may be visually complex, may appear directly in compositions or inside compounds, and may have local variations without gaining standard reusable variant axes.

Examples:

- brand logo
- loading splash mark
- specialized code strip if the system only has one
- a singular hero artifact or signature sticker

Decision test: "Would standard variants clarify a reusable family, or dilute a singular artifact?" If variants would dilute it, it may be a unique specimen.

### Compounds

Stable assemblies of primitives and/or unique specimens that travel together.

Examples:

- pattern card
- pattern reel
- panel header if it has a stable child set
- a card assembly that includes a unique code strip

Decision test: "Is it a repeatable assembly built from named lower-layer artifacts, and would using half of it break the concept?" If yes, it is compound.

### Compositions

Real screens, screen regions, or app states. They prove the grammar in context and may include actual content and orchestration.

Decision test: "Is this what the user sees as a meaningful screen or region?" If yes, it is composition.

## Boundary Rubric

When classification is unclear, answer these questions in order:

1. `Does it render?`
   - No: token, constant, pattern, doctrine, or data.
   - Yes: continue.
2. `Does it own behavior?`
   - Single affordance or shell behavior: primitive may fit.
   - Coordinates several child behaviors: compound or composition.
3. `Does it own child orchestration?`
   - No named child components: primitive may fit.
   - Stable named children, including unique specimens, always travel together: compound.
   - Content/state varies by screen or user flow: composition.
4. `Are slots part of the concept?`
   - Generic slots with stable shell behavior can still be a container primitive.
   - Slots with prescribed child set and layout become compound.
5. `Is it reusable across contexts?`
   - Reusable with standard variant axes: primitive or compound.
   - Singular but important, even if complex: unique specimen.
   - Only meaningful as a final app region: composition.
6. `Would removing content leave the thing recognizably itself?`
   - Yes: primitive shell or compound shell.
   - No: composition or content-specific unique specimen.

Shell rule:

- A drawer shell can be primitive if it owns reveal behavior, position, slots, and panel anatomy, while child content is arbitrary.
- A drawer with fixed header, tabs, controls, and data-specific content is compound or composition.
- A visual artifact should not be a unique specimen just because it is hard to extract; uniqueness requires a singular role in the system.

## Layer-Scoped Ideation

Ideate inside the current layer.

- Token ideation produces token groups, patterns, maps, constraints, and semantic aliases.
- Primitive ideation produces primitive families, anatomy, state matrices, variants, and API ideas.
- Unique specimen ideation preserves singular artifacts and clarifies why they are not reusable families.
- Compound ideation produces stable assemblies and child-component contracts.
- Composition ideation produces real screens, stateful regions, flow examples, and proof cases.

Do not jump to broad "visual directions" if the current task is primitive extraction. If a new visual direction is needed, make that an explicit Taste Gate.

Ideation procedure:

1. List candidates from intake, archaeology, raw recipe inventory, current components, Design System File artifacts, and style-guide surfaces.
2. Sketch only the artifact shape for the current layer: token schema, primitive anatomy/API, unique specimen justification, child contract, or composition proof case.
3. Name states, variants, dependencies, and forbidden mutations that belong to this layer.
4. Declare what is not in this layer and where it will be handled.
5. For ambiguous candidates, write a Promotion Gate or Taxonomy Gate before implementation.
6. Hold the Taxonomy Gate before moving artifacts across layers.

Layer-specific prompts:

- `tokens`: What values, aliases, maps, constraints, effects, or motion rules recur before anything renders?
- `primitives`: What renderable identities stand alone once content is removed?
- `unique specimens`: Which singular artifacts matter enough to preserve but should not become a reusable family?
- `compounds`: Which primitive/unique-specimen assemblies always travel together and need a child contract?
- `compositions`: Which screens, regions, or states prove the grammar in real usage?

## Layer Closure

Do not advance to the next layer just because one gate passed. Close the current layer with an explicit checklist and artifact.

Layer closure output must record:

- generic closure checks that apply to every layer
- per-layer closure proof for the specific layer
- unresolved decisions with owner, date, gate name, and unblock condition
- handoff contract: what the next layer may now build from, and what it must not assume yet

All layers require:

- source artifacts for the layer are listed
- source of truth is named
- raw recipes are promoted, pruned, kept local, or parked behind a named gate
- unresolved decisions have owner/date/unblock condition
- style-guide surfaces demonstrate source-of-truth artifacts rather than defining them
- coverage audit rows for this layer have non-empty `Resolution`

Token closure requires:

- token groups, semantic aliases, naming rules, and allowed raw-value exceptions are documented
- token candidates from raw recipe inventory are resolved
- higher layers have enough token vocabulary to avoid inventing new raw values immediately

Primitive closure requires:

- primitive families have anatomy, API, states, variants, and token dependencies
- primitives consume tokens or approved lower-level data/constants
- style-guide surfaces import/demonstrate primitive source files

Compound closure requires:

- child primitive dependencies and slot contracts are explicit
- compounds compose children instead of duplicating internals
- any new repeated child pattern is promoted or gate-parked

Unique specimen closure requires:

- each unique specimen has a singular-role justification
- any reusable material inside the unique specimen is resolved downward
- the unique specimen is marked so future agents do not generalize it by accident

Composition closure requires:

- compositions use approved lower layers
- composition-only content, orchestration, and app state are separated from component grammar
- residue audit has no unresolved cross-cutting grammar

## Taxonomy Gate

When an artifact is hard to classify, show the decision table:

```markdown
## Taxonomy Gate: <artifact>

Candidate layer: <token|primitive|unique specimen|compound|composition>

Evidence:
- ...

Why not lower:
- ...

Why not higher:
- ...

Alternatives rejected:
- ...

Unresolved risk:
- ...

Decision needed:
- ...

Unblocks:
- ...
```

If the user decides differently, update names/files/schema to match the decision.

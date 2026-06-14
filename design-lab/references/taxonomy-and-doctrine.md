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

Values, semantic aliases, constraints, and named low-level recipes that do not render as standalone UI. Examples:

- color roles and semantic aliases
- type scale and type role shorthands
- spacing/radius/shadow/clip/rotation tokens
- motion durations/easings/keyframes
- data maps such as note labels or palette constants when they drive presentation

Decision test: "Could this be replaced by reading variables/constants?" If yes, it is token-layer.

Expressive utility classes such as `firm-voice`, `loud-voice`, or `points` are usually token-layer role utilities or doctrine shorthand, not primitives. Promote them to primitives only when they own a renderable identity with anatomy, states, slots, or behavior beyond applying a named recipe.

### Primitives

Smallest named renderable ideas. They may be visual, control, or container primitives.

Examples:

- icon button, key, tab, knob, mark, sticker, card shell, drawer shell

Decision test: "Does it have a single identity and stand alone without named child components?" If yes, it can be primitive.

Primitive does not mean tiny. A drawer can be primitive if its job is a structural shell with slots and behavior.

Primitive does not mean "whatever is low-level." A primitive section must be made of named primitive families, not a grab bag of unrelated low-level items.

Common primitive families:

- `control primitives`: button, text link, icon button, toggle, tab, key, knob.
- `visual primitives`: mark, sticker, badge, indicator, decorative label.
- `container primitives`: card shell, drawer shell, panel shell, stage shell.
- `field primitives`: pattern field, texture field, grid field only when the field has renderable identity, constraints, and usage rules beyond a token class.

Usually not primitive:

- raw CSS variables, utility classes, texture classes, and pattern backgrounds that can be represented as tokens or doctrine shorthand
- singular decorative assets that do not form a reusable family
- one-off composition helpers, proof cards, demo frames, or style-guide labels

If a style-guide section contains a button class, text link class, toggle, arrow, and pattern-background swatches together, do not accept it as "the primitive layer." Split it into control primitives, pattern/texture tokens or field primitives, visual primitives, and unique specimens, or open a Layer Purity Gate.

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

- Token ideation produces token groups, low-level recipes, maps, constraints, and semantic aliases.
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

Cross-layer discovery rule:

If work in a higher layer reveals a missing lower-layer idea, pause the current layer, record the candidate in `RAW_RECIPE_INVENTORY.md`, open the needed Promotion or Taxonomy Gate, update the lower layer, then resume. Do not keep building the higher layer on unnamed grammar.

Layer-specific prompts:

- `tokens`: What values, aliases, maps, constraints, effects, or motion rules recur before anything renders?
- `primitives`: What renderable identities stand alone once content is removed, and which primitive family does each belong to?
- `unique specimens`: Which singular artifacts matter enough to preserve but should not become a reusable family?
- `compounds`: Which primitive/unique-specimen assemblies always travel together and need a child contract?
- `compositions`: Which screens, regions, or states prove the grammar in real usage?

## Layer Purity Gate

Run this before presenting or closing a style-guide section as one taxonomy layer. This gate prevents the common failure where "primitives" becomes a random mix of controls, utilities, one-offs, pattern swatches, and proof cards.

Layer purity checks:

1. Every item in the section has an artifact row with candidate layer, source of truth, and proof.
2. Every primitive item names its primitive family: control, visual, container, or field.
3. Token demonstrations and utility recipes are not counted as primitive components unless they have anatomy, states, variants, and usage rules.
4. Unique specimens are not placed inside primitive sections merely because they are small or visual.
5. A mixed section is either split into layer-pure subsections or labeled as a mixed proof surface, not a closed layer.
6. Any item that cannot pass the layer test opens a Taxonomy Gate or Promotion Gate before extraction.

Gate packet:

```markdown
## Layer Purity Gate: <section or surface>

Claimed layer:
- ...

Items:
| Item | Current label | Candidate layer | Primitive family | Source of truth | Decision |
|---|---|---|---|---|---|
| ... | ... | token / primitive / unique specimen / compound / composition / style-guide-only | control / visual / container / field / n/a | ... | keep / split / reclassify / gate |

Mixed-section risk:
- ...

Recommendation:
- split into ... / relabel as mixed proof surface / continue as layer-pure

Alternatives rejected:
- ...

Unresolved risk:
- ...

Decision needed:
- ...

Unblocks:
- ...

Gate Decision:
- accepted | continue | pause
```

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
- primitive style-guide sections are layer-pure or explicitly split by primitive family

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

Recommendation:
- ...

Unresolved risk:
- ...

Decision needed:
- ...

Unblocks:
- ...

Gate Decision:
- accepted | continue | pause
```

If the user decides differently, update names/files/schema to match the decision.

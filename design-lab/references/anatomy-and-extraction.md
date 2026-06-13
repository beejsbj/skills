# Anatomy And Extraction

Use this reference when turning preview material, Design System File artifacts, or style-guide surfaces into source-of-truth components, or when auditing a design system for hidden recipes.

Blocking rule: a layer cannot be closed while any artifact at that layer has an unresolved promote/prune/keep-local decision. Unresolved items must be parked behind a named Promotion Gate before the next layer begins.

## Key Distinction

```text
Anatomy
  visual formalization artifact

Reusable component
  implementation source of truth

Style-guide surface
  proof surface that imports or demonstrates the source of truth
```

Style-guide surfaces demonstrate components. They should not become component source of truth.

## Anatomy Pass

Use Anatomy or the local equivalent to display:

- canonical instance
- named parts
- token dependencies
- child component dependencies
- states
- variants
- usage rules
- forbidden uses
- unresolved promotion decisions

Anatomy is not just visual labeling. It is the mechanism that forces the design object to become explicit.

Required Anatomy schema:

```text
canonical instance
  the single representative rendering

part tree
  named internal parts and their hierarchy

slot map
  child slots, required/optional content, and allowed child layers

token dependencies by part
  colors, type, geometry, motion, data maps, effects

state matrix
  rest, hover, focus, active, selected, disabled, loading, reduced-motion where relevant

variant or local variation axes
  primitives/compounds use standard reusable axes such as size, density, tone, geometry, content mode, motion mode, or data mode
  unique specimens use local variation notes, not standard reusable variant axes

child dependencies
  lower-level components imported or required

forbidden mutations
  changes that would violate doctrine

promotion items
  raw recipes that must be promoted, pruned, kept local, or decided by user
```

If an artifact cannot fill this schema, do not force it. Reclassify it, split it, or mark it as drift/unique specimen.

Inspiring example from Emotitone `Sticker.vue`:

Note: Emotitone currently uses the repo-local spelling `primatives`; preserve repo-local path spelling when citing source files.

```markdown
## Anatomy: Sticker Primitive

### Canonical Instance
`<Sticker variant="outline" color="ivory">Piano</Sticker>`

### Part Tree
- root sticker
- default text slot
- badge edge, for `variant="badge"` only
- badge text, for `variant="badge"` only

### Slot Map
| Slot | Required | Allowed Child Layers | Notes |
|---|---:|---|---|
| default | yes | text/content | short decorative label |

### Token Dependencies By Part
| Part | Tokens |
|---|---|
| root | --font-display, --ivory, --shadow-cut, --sticker-clip, --sticker-transform |
| outline/fill color | --ink, --ivory, --brass, --tomato, --pine, --plum, --bone, --mustard |
| brass sheen/glow | --brass-fill, --brass-sheen, --shadow-glow-brass |
| randomized geometry | getRandomGeometry("sticker"), --rot-sticker, --rot-sticker-lg |
| badge | --ink-2, --brass-fill, brass-sheen motion |

### State Matrix
| State | Expected Change | Source Of Truth |
|---|---|---|
| outline | transparent fill, 1px color wire, randomized cut-paper geometry | components/primatives/Sticker.vue |
| fill | color surface, foreground inversion, randomized cut-paper geometry | components/primatives/Sticker.vue |
| badge | fixed brass shimmer edge/text, ignores color, no random geometry | components/primatives/Sticker.vue |
| reduced motion | brass sheen animations disabled | components/primatives/Sticker.vue media query |

### Variant Axes
- variant: outline, fill, badge
- color: ink, ink-5, ivory, brass, brass-sheen, brass-glow, brass-sheen-glow, tomato, pine, plum, bone, mustard
- geometry mode: randomized for outline/fill, fixed for badge

### Child Dependencies
- `getRandomGeometry("sticker")`

### Forbidden Mutations
- duplicating the color list in style-guide surfaces without a shared vocabulary decision
- defining sticker markup inside the style-guide surface instead of importing `Sticker.vue`
- treating badge as a settled variant if it is actually a separate brass badge primitive

### Promotion Items
- Promote shared sticker color vocabulary to a TS constant/map if other primitives use it.
- Decide whether `badge` remains a Sticker variant or becomes a separate brass badge primitive.
- Keep style-guide layout wrappers local to the style guide.
```

Why this is a good model: `Sticker.vue` is the reusable primitive source of truth, while `PrimitiveSticker.vue` imports it as a style-guide surface. The example also preserves a real unresolved taxonomy decision instead of pretending every component is already clean.

Mini walkthrough:

1. Archaeology finds a static sticker style-guide surface and the extracted `Sticker.vue` component.
2. Raw recipe inventory records randomized cut-paper geometry, brass sheen/glow, sticker color vocabulary, and badge behavior.
3. Taxonomy classifies sticker as a decoration primitive because it has stable identity, API, and anatomy.
4. Extraction keeps `Sticker.vue` as source of truth and keeps `PrimitiveSticker.vue` as the style-guide surface.
5. Promotion audit marks sticker geometry as token-backed, color vocabulary as a candidate shared map, and badge as a Promotion Gate.
6. Anatomy documents parts, token dependencies, variants, state matrix, forbidden mutations, and promotion items.
7. Residue proof checks that compounds/compositions import `Sticker.vue` rather than copying sticker internals.
8. Layer closure may advance only when the badge/color decisions are resolved or gate-parked.

Anti-patterns:

- Defining component behavior inside Anatomy instead of the source file.
- Duplicating component markup in the style-guide surface rather than importing the real component.
- Inventing variants in Anatomy that the source component does not support.

## Raw Recipe Inventory

Run this before extraction when source material includes moodboards, screenshots, static previews, compositions, existing components, or compiled component source. The goal is to catch reusable grammar before it hides inside one component.

Use the canonical loop in `SKILL.md`. This reference covers the extraction segment:

```text
raw recipe inventory -> extraction/formalization -> promotion decisions -> anatomy -> residue proof -> layer closure
```

Inventory depth:

- `sample`: scouting/pilot mode. Capture representative rows that test taxonomy and gates. Do not close layers from a sample inventory.
- `focused`: inspect one accepted layer, component family, surface, or composition deeply enough to extract it.
- `exhaustive`: inspect all in-scope sources before layer closure or Finish Gate.

Inventory:

- repeated colors or semantic color roles
- repeated shapes, clips, strokes, shadows, textures, or proportions
- repeated timing/easing/motion gestures
- repeated type treatments, casing, rhythm, labels, or copy structure
- repeated layout rituals or interaction patterns
- repeated data-to-visual mappings
- singular but brand-defining artifacts
- component CSS, computed styles, prop usage, state selectors, and duplicated markup in existing source files

Classify each item as `candidate token`, `candidate primitive`, `candidate unique specimen`, `candidate compound`, `composition-only`, or `drift`.

Create a standalone `RAW_RECIPE_INVENTORY.md` before component extraction starts. Later promotion audits may reference it, but should not be the first place the inventory appears.

## Extraction / Formalization Loop

For each artifact being formalized:

1. Identify the intended source of truth: token file, primitive component, unique specimen source, compound component, or composition view.
2. Extract a reusable component only if it has stable identity, API, and lifecycle.
3. Replace style-guide-internal markup with imports/composition from the real component.
4. Inspect every visual decision in the component:
   - raw colors
   - raw lengths
   - raw durations/easings
   - clip paths
   - transforms
   - shadows/glows
   - typography choices
   - SVG stroke grammar
   - state names and selectors
   - data maps/constants
   - layout proportions
5. Resolve every item through promote/prune/keep-local.

## Promote / Prune / Keep Local

Use this decision rule:

```text
If raw/new/unique material appears during extraction:
  promote it downward if it is reusable, repeated, law-like, or needed by multiple components.
  prune it if it is drift and a close lower-level idea already exists.
  keep it local if it is truly unique, style-guide-only, or specific content.
```

Promotion examples:

- A repeated clip path becomes a geometry token.
- Repeated tab timing becomes a motion token or named duration.
- Repeated brass glow becomes a shadow/effect token.
- A repeated label stack becomes primitive anatomy.
- A repeated note-label map becomes a shared constant.

Prune examples:

- A local color close to an existing token is replaced by the token.
- Local CSS that recreates a global brass finish is removed.
- A component-specific shadow is replaced with the existing ring/shadow recipe.
- Style-guide staging wrappers stay in the style guide and do not enter the component.

Keep-local examples:

- Demo layout and stage wrappers.
- Style-guide-only labels and captions.
- Real content examples.
- Truly singular brand artwork.

## Recipe Gap Audit

Recipe audit happens during extraction, not as a late phase.

Use `recipe gap` when low-level tokens exist but component-specific grammar is still unnamed.

Record recipe gaps in `PROMOTION_AUDIT.md` under the `Recipe Gaps` section. Surface unresolved gaps to the affected layer's `LAYER_CLOSURE.md` as gate-parked items.

Example:

```text
Generic clip tokens exist, but key-specific strip/pill/tall/wide recipes are still local.
```

Recipe gap output:

```markdown
## Recipe Gaps: <artifact>

### Promote
- ...

### Prune / Replace With Existing
- ...

### Keep Local
- ...

### Needs User Decision
- ...
```

## Residue Audit

Run this after compositions, major style-guide surfaces, or Design System File artifacts are rebuilt.

Residue is a cross-cutting check. It scans the built system for unnamed grammar regardless of which source artifact introduced it.

Record the result in `RESIDUE_PROOF.md`, using a pattern-by-pattern table rather than a free-form paragraph.

Check:

- raw CSS values left in higher layers
- duplicate primitive internals copied into compounds/compositions
- unnamed visual recipes repeated in multiple places
- components that use generic tokens but still hide component-specific grammar
- singular artifacts not marked unique specimen
- style-guide surfaces that define behavior instead of demonstrating source-of-truth components

Residue must be resolved as promote, prune, keep-local, or deferred behind a named gate.

## Completion Check For One Component

A component is formalized when:

- it imports or consumes lower-level tokens/components instead of duplicating them
- its props/API match real usage
- states and variants are named
- style-guide staging has been removed from the component
- the style-guide surface imports and demonstrates the component
- raw recipes have been promoted, pruned, or kept local with a reason
- unresolved decisions are documented as Promotion Gates

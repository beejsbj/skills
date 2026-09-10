# Systematizing (System Axis Reference)

The System axis is fully autonomous. Use this to classify artifacts into the taxonomy, run the cohesion self-audit, and formalize a component with anatomy. Never turn any of this into a user question — resolve it and assert it done.

## Taxonomy layers

Source of truth, low → high. Classify every artifact into exactly one.

- **tokens** — values, semantic aliases, constraints, low-level recipes that do not render as standalone UI (color roles, type scale, spacing/radius/shadow/clip, motion durations/easings, data maps that drive presentation). Test: "Could this be replaced by reading a variable/constant?" → token.
- **primitives** — smallest named renderable ideas with a single identity that stand alone without named child components. Families: control (button, tab, key, knob, toggle), visual (mark, sticker, badge, indicator), container (card/drawer/panel shell), field (pattern/texture/grid field, only if it has renderable identity beyond a token class). Primitive ≠ tiny: a drawer shell is primitive if its job is a structural shell with slots + behavior. Primitive ≠ "anything low-level": a primitive section must be named families, not a grab bag.
- **unique specimens** — singular preserved artifacts that matter but should NOT become a reusable family (brand logo, loading splash, a one-of-a-kind code strip). May be complex; use local variation notes, not standard reusable variant axes. Test: "Would standard variants clarify a family or dilute a singular artifact?" → if dilute, unique specimen.
- **compounds** — stable assemblies of primitives and/or unique specimens that travel together (pattern card, pattern reel, panel header with a fixed child set). Test: "Repeatable assembly of named lower-layer artifacts, where using half of it breaks the concept?" → compound.
- **compositions** — real screens, regions, or app states that prove the grammar in context, with real content and orchestration.

## Boundary rubric

When classification is unclear, answer in order:

1. **Does it render?** No → token / constant / data / doctrine. Yes → continue.
2. **Does it own behavior?** Single affordance or shell behavior → primitive. Coordinates several child behaviors → compound or composition.
3. **Does it own child orchestration?** No named children → primitive. Stable named children that always travel together → compound. Content/state varies by screen → composition.
4. **Reusable across contexts?** Reusable with standard variant axes → primitive/compound. Singular but important, even if complex → unique specimen. Only meaningful as a final region → composition.
5. **Would removing content leave it recognizably itself?** Yes → primitive/compound shell. No → composition or content-specific unique specimen.

Shell rule: a drawer shell with arbitrary slot content is a primitive; a drawer with fixed header/tabs/data is a compound. Hard-to-extract is not the same as unique — uniqueness requires a singular role.

## Cohesion self-audit

Run this across the built system before the taste handoff. Every hit is resolved, not reported to the user.

For each raw/new/unique decision: **promote** it downward if reusable/repeated/law-like; **prune** it if a close lower-level idea already exists; **keep local** if truly singular or style-guide-only.

Residue scan (each must be 0 or justified):

- raw hex colors outside tokens
- raw px / lengths outside tokens
- raw durations / easings / cubic-beziers outside tokens
- repeated clip-paths, shadows, or transforms not promoted to tokens
- duplicated primitive internals copied into compounds/compositions instead of imported
- singular artifacts not marked as unique specimens
- style-guide surfaces that define behavior instead of importing the real component

If a built composition re-declares a primitive's markup instead of importing it, that is drift — fix it by importing.

## Reuse decision

When a surface needs something close to an existing component, decide whether the difference earns a variant or a separate identity. Apply the boundary rubric above to classify the result.

- **Snap** to an existing component when its identity, anatomy, behavior, and meaning are already covered; change only content or allowed configuration. Sprout's “Needs water” status fits `<Chip tone="clay">Needs water</Chip>`; making a second `CareTag` would duplicate the same contract.
- **Promote as a variant** when it is the same concept and contract, but a recurring, named difference needs a stable axis with its own states or semantics. If Sprout needs a second muted status, add a `muted` `Chip` tone with explicit tokens and states; do not create a separate `DormantChip`.
- **Promote as new** when sharing the existing component would obscure a distinct identity or force incompatible anatomy or behavior into its API. Sprout's `MoistureMeter` may be as compact as `Chip`, but its range, fill, and current-value semantics need their own contract; create a meter that shares foundation tokens instead of a `Chip mode="meter"` with irrelevant label states.

Preserve a singular artifact as a unique specimen when the taxonomy calls for it; a new identity does not automatically need a reusable family or standard variants.

## Anatomy

Formalize each non-trivial component by capturing (inline beside it, or in its specimen):

- **canonical instance** — the single representative rendering
- **part tree + slot map** — named internal parts; slots with required/optional content and allowed child layers
- **token dependencies by part** — every color/type/geometry/motion value, by part
- **state matrix** — rest, hover, focus, active, selected, disabled, loading, reduced-motion where relevant
- **variant axes** — standard reusable axes (size, tone, geometry, mode) for primitives/compounds; local variation notes for unique specimens
- **child dependencies** — lower components imported/required
- **forbidden mutations** — changes that would violate the direction
- **promotion items** — raw recipes resolved via promote/prune/keep-local

If an artifact can't fill this, don't force it — reclassify, split, or mark it a unique specimen.

## Worked examples

These use one invented design system — **Sprout**, a calm plant-care app — so the examples interlock. There is one worked example per taxonomy layer, plus a cross-layer drift case. They are illustrative, not a dependency on any real repo. Foundation tokens assumed throughout:

```css
--ink:#2b2a26; --paper:#f4f1ea; --sage:#7c9885; --clay:#c9785b; --sage-1:#e7ede8; --clay-1:#f1ddd3;
--radius-soft:14px; --shadow-soft:0 2px 8px rgba(43,42,38,.12);
--ease-gentle:cubic-bezier(.4,0,.2,1); --dur-calm:240ms; --font-display; --font-body;
```

### 1. Token promotion

A raw value that shows up in more than one place is a token that hasn't been promoted yet.

❌ Bad — `#c9785b` is typed 3× and the shadow literal 2× across two components:

```astro
---
// SaveButton.astro
---
<button class="save">Save sprout</button>
<style>
  .save { background:#c9785b; border-radius:14px; box-shadow:0 2px 8px rgba(43,42,38,.12); }
</style>

---
// CareTag.astro
---
<span class="tag">Needs water</span>
<style>
  .tag { color:#c9785b; border:1px solid #c9785b; box-shadow:0 2px 8px rgba(43,42,38,.12); }
</style>
```
- `#c9785b` is a **raw hex that should resolve to `--clay`**; `0 2px 8px rgba(43,42,38,.12)` is **`--shadow-soft` re-typed**. A brand tweak now means hunting every literal by hand — miss one and the two drift apart.

✅ Good — both resolve to the foundation:

```astro
.save { background: var(--clay); border-radius: var(--radius-soft); box-shadow: var(--shadow-soft); }
.tag  { color: var(--clay); border: 1px solid var(--clay); box-shadow: var(--shadow-soft); }
```
- Tweaking `--clay` once re-skins every accent surface at the source; the two components can never drift.

### 2. Formalizing a primitive (the quality bar)

A primitive is one importable component, a token for every value, an explicit variant + state API, and a specimen that **imports** it. Anything copy-pasted with raw values is markup, not a primitive.

❌ Bad — chip markup pasted in two files with raw values, no API, no states; the style-guide demo re-declares it:

```astro
---
// PlantCard.astro — chip markup pasted inline
---
<span style="background:#e7ede8; color:#2b2a26; border-radius:14px; padding:4px 12px;">Thriving</span>

---
// styleguide/status.astro — the "demo" RE-DECLARES the same markup
---
<span style="background:#f1ddd3; color:#2b2a26; border-radius:14px; padding:4px 12px;">Needs water</span>
```
- No single source of truth; raw `#e7ede8 / #f1ddd3 / #2b2a26 / 14px / 4px 12px`; no `tone` API; no states; the specimen proves nothing because it copies rather than imports.

✅ Good — one importable, fully tokenized `Chip.astro` with a variant + state API; the specimen imports it:

```astro
---
// primitives/Chip.astro
interface Props { tone?: 'sage' | 'clay' | 'ink'; disabled?: boolean; }
const { tone = 'sage', disabled = false } = Astro.props;
---
<span class:list={['chip', `chip--${tone}`]} aria-disabled={disabled || undefined}><slot /></span>
<style>
  .chip { display:inline-flex; padding:4px 12px; border-radius:var(--radius-soft);
          box-shadow:var(--shadow-soft); font-family:var(--font-body); color:var(--ink);
          transition:transform var(--dur-calm) var(--ease-gentle); }
  .chip--sage { background:var(--sage-1); }
  .chip--clay { background:var(--clay-1); }
  .chip--ink  { background:var(--paper); }
  .chip:hover { transform:translateY(-1px); }
  .chip[aria-disabled] { opacity:.5; pointer-events:none; }
</style>
```
```astro
---
// styleguide/StatusSpecimen.astro — IMPORTS the primitive, never copies it
import Chip from '../primitives/Chip.astro';
---
<Chip tone="sage">Thriving</Chip>
<Chip tone="clay">Needs water</Chip>
<Chip tone="ink" disabled>Dormant</Chip>
```

Anatomy:
- part tree: `Chip` (root `span`) → label slot. Single part.
- tokens by part: background → `--sage-1 / --clay-1 / --paper` (per tone); text → `--ink`; shape → `--radius-soft`, `--shadow-soft`; type → `--font-body`; motion → `--dur-calm`, `--ease-gentle`.
- states: rest, hover (`translateY(-1px)` over `--dur-calm`), disabled (`aria-disabled`, dimmed, non-interactive).
- variant axes: `tone ∈ { sage, clay, ink }` mapped to semantic status, not raw color.
- open decision (promotion item): is "Dormant" a muted `tone` or its own primitive? Recorded, not flattened — revisit when a second muted status appears.

### 3. Cross-layer drift

❌ Bad — a `PlantCard` compound re-declares the Chip's internals with raw colors instead of importing it:

```astro
---
// PlantCard.astro
const { name, status } = Astro.props;
---
<article class="plant-card"><h3>{name}</h3><span class="chip">{status}</span></article>
<style>
  .plant-card { border-radius:14px; box-shadow:0 2px 8px rgba(43,42,38,.12); }
  .chip { background:#7c9885; color:#f4f1ea; border-radius:999px; padding:2px 10px; }
</style>
```
- Residue rule broken: **duplicated primitive internals copied into a compound instead of imported** — the chip and its raw `#7c9885` are re-declared.

✅ Good — the compound imports the primitive and keeps only card-specific decisions, in tokens:

```astro
---
// PlantCard.astro
import Chip from '../primitives/Chip.astro';
const { name, status } = Astro.props;
---
<article class="plant-card"><h3>{name}</h3><Chip tone="sage">{status}</Chip></article>
<style>
  .plant-card { border-radius: var(--radius-soft); box-shadow: var(--shadow-soft); }
</style>
```

### 4. Unique specimen

A singular artifact earns its place by being one-of-a-kind — parameterizing it into a "family" destroys it.

❌ Bad — the hand-drawn Sprout mascot over-generalized into a fake reusable family:

```astro
---
// Mascot.astro
interface Props { size?: 'sm'|'md'|'lg'; tone?: 'sage'|'clay'|'ink'; outline?: boolean; }
const { size='md', tone='sage', outline=false } = Astro.props;
---
<svg class:list={['mascot',`mascot--${size}`,`mascot--${tone}`, outline && 'mascot--outline']}>…</svg>
```
- invents `size` / `tone` / `outline` axes for an artifact that appears **once** — dilutes a singular brand mark into a pseudo-family of dead variants nobody renders; `tone` even re-introduces colors the artwork already owns.

✅ Good — one canonical mark, marked so nobody generalizes it:

```astro
---
// unique-specimens/SproutMascot.astro
// unique specimen: singular brand mark — do NOT add variants or promote to a primitive
---
<svg class="sprout-mascot" viewBox="0 0 64 64" role="img" aria-label="Sprout">…</svg>
<style>.sprout-mascot { width: 40px; color: var(--sage); }</style>
```
- one rendering, used once; the comment stops a future agent from adding a `size` axis; if a smaller instance is ever needed that's a **local one-off**, not a reusable variant.

**Test:** would standard variants clarify a reusable family, or dilute a singular artifact? Dilute → unique specimen.

### 5. Compound

A compound is a reusable assembly defined by its **child contract** — if it re-declares its children, it isn't a compound, it's drift.

❌ Bad — a "compound" that flattens its children's internals with raw values:

```astro
---
// PlantCard.astro
const { name } = Astro.props;
---
<article class="plant-card">
  <h3>{name}</h3>
  <span class="chip" style="background:#e7ede8;color:#2b2a26;border-radius:14px;padding:4px 12px;">Thriving</span>
  <button style="background:#c9785b;color:#f4f1ea;border-radius:14px;">Water</button>
</article>
```
- not an assembly — it's a flat copy of the Chip and Button internals with raw values; no child contract; changing the Chip means editing every card.

✅ Good — composes named primitives through an explicit contract (assume a `Button` primitive built like `Chip`):

```astro
---
// compounds/PlantCard.astro
import Chip from '../primitives/Chip.astro';
import Button from '../primitives/Button.astro';
interface Props { name: string; status: 'sage'|'clay'|'ink'; }
const { name, status } = Astro.props;
---
<article class="plant-card">
  <h3 class="plant-card__name">{name}</h3>
  <Chip tone={status}><slot name="status" /></Chip>
  <Button tone="clay"><slot name="action">Water</slot></Button>
</article>
<style>.plant-card { border-radius: var(--radius-soft); box-shadow: var(--shadow-soft); padding: 12px; }</style>
```
- the child contract is explicit (a name + a status Chip + an action Button); composes by import; only card-specific layout/tokens live here; using half of it would break the concept → compound, not composition.

**Test:** repeatable assembly of named lower-layer artifacts, where using half of it breaks the concept? → compound.

### 6. Composition

A composition is a real screen — it owns content and orchestration, composes compounds, and is the destination, not a reusable part.

✅ Good — a real view that owns data and composes compounds:

```astro
---
// compositions/GardenView.astro
import PlantCard from '../compounds/PlantCard.astro';
const plants = await getPlants(); // real content + orchestration
---
<main class="garden">
  <h1>Your garden</h1>
  {plants.map((p) => <PlantCard name={p.name} status={p.status} />)}
</main>
```
- owns real data/state and page layout; composes the `PlantCard` compound; **not** parameterized for reuse — it *is* the screen.

❌ The drift version is example 3 one layer up: a `GardenView` that re-declares `PlantCard`/`Chip` markup inline instead of importing them. Fix by importing.

**Test:** remove the content — still recognizably itself? Yes → compound shell; No → composition.

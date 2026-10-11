# Systematizing

Own the classification, reuse, and lineage decisions. Resolve engineering questions autonomously; report evidence and remaining gaps rather than asserting unverified completion.

## Categories and dependencies

The reusable hierarchy is `tokens -> primitives -> compounds -> compositions`. **Unique specimens are a separate category**, with dependencies determined by their anatomy rather than a fixed rung. Every artifact has one classification; imports form an acyclic graph.

- **Tokens** — shared values, semantic aliases, constraints, and presentation recipes that do not render independently: color roles, type scales, spacing, geometry, shadows, motion, or presentation maps. A private implementation constant is not automatically a system token.
- **Primitives** — renderable ideas with one identity or affordance: controls, marks, indicators, fields, or container shells. Size and file count do not determine the category. A drawer shell with arbitrary slots can be a primitive; private helpers can implement a single primitive's public contract.
- **Compounds** — stable assemblies of named components that travel together under a reusable child contract. A card with a fixed status and action is a compound; its children retain ownership of their own grammar.
- **Compositions** — real screens, regions, or app states that own content and orchestration. In an existing app these are production surfaces, not a further component layer preceding production. A greenfield composition can prove a realistic use case before an app exists.
- **Unique specimens** — artifacts with a singular identity worth preserving, such as a brand mark or a product-specific notation editor. They may be complex, own behavior, compose reusable components, and have multiple consumers. Singularity concerns identity, not instance count. Preserve meaningful configuration; do not manufacture a reusable family merely to fill a variant grid.

**Guide example** means a demonstration of any category. A Button demonstration is an example of a primitive, not a unique specimen. Guide scaffolding is neither component anatomy nor a new taxonomy category.

## Boundary rubric

Use these questions together; the first matching property is not a premature classification:

1. Does it render, or is it a value/recipe? Shared non-rendering grammar belongs to tokens; private mechanics stay with their owner.
2. Is its identity deliberately singular? Preserve it as a unique specimen even if it composes other components or appears in several contexts.
3. What public contract does it own? One affordance or structural shell suggests a primitive; a stable assembly suggests a compound; screen-specific content and orchestration suggest a composition.
4. Would variants express actual supported use, or invent a family nobody needs? Extract a public abstraction only for a real contract; keep implementation helpers private.

For example, an arbitrary-content drawer shell can be a primitive, a fixed settings assembly a compound, and a product's distinctive integrated drawer a unique. Classify from the actual identity and contract, not its name or extraction difficulty.

## Reuse decision

When something is close to an existing component, decide whether the difference earns a variant or a separate identity. This decision is separate from classification.

- **Snap** when identity, anatomy, behavior, and meaning are already covered. In the invented plant-care system Sprout, use `<Chip tone="attention">Needs water</Chip>` instead of creating an equivalent `CareTag`.
- **Promote as a variant** when the same contract needs a recurring, meaningful difference. Add a `muted` Chip tone when muted statuses need their own presentation, instead of creating `DormantChip`.
- **Promote as new** when reuse would force incompatible anatomy or behavior into the API. A `MoistureMeter` needs range, fill, and value semantics; give it that contract instead of `Chip mode="meter"`.

A new identity can remain a unique specimen. It does not automatically need standard family variants.

## Token ownership and local rules

Promote values and recipes that express shared design grammar, named variation, or a system-wide constraint. A newly chosen foundation may earn a token before its second use when its role and intended consumer are concrete. Repeated literals are clues, not proof: unrelated values that happen to match need not share ownership.

Reuse existing tokens for spacing, type, colors, geometry, and motion where their meaning fits. Keep structural CSS (`0`, `100%`, `inherit`, layout mechanics), private calculations, and genuinely singular optical or host adjustments local. Document a consequential exception beside its owner or in the tracker; trivial structural constants need no ledger entry.

Promote a local rule when it acquires shared meaning or real reuse. Avoid tokens or public components created only to achieve a zero-literal count. Conversely, a unique specimen still consumes shared grammar; uniqueness does not excuse copying a primitive or inventing a rival palette.

### Worked example: shared values, local structure

These excerpts illustrate ownership; they are not a complete application. Sprout's shared tokens include:

```css
:root {
  --ink: #2b2a26;
  --paper: #f4f1ea;
  --sage-1: #e7ede8;
  --clay-1: #f1ddd3;
  --space-xs: 4px;
  --space-sm: 12px;
  --radius-soft: 14px;
  --font-body: "Source Sans 3", sans-serif;
}
```

Duplicating the Chip's background, padding, and shape in each consumer makes those consumers competing owners. One source fixes that:

```astro
---
// primitives/Chip.astro
interface Props { tone?: 'healthy' | 'attention' | 'neutral'; }
const { tone = 'healthy' } = Astro.props;
---
<span class:list={['chip', `chip--${tone}`]}><slot /></span>
<style>
  .chip {
    display: inline-flex;
    padding: var(--space-xs) var(--space-sm);
    border-radius: var(--radius-soft);
    font-family: var(--font-body);
    color: var(--ink);
  }
  .chip--healthy { background: var(--sage-1); }
  .chip--attention { background: var(--clay-1); }
  .chip--neutral { background: var(--paper); }
</style>
```

This Chip is a noninteractive status label. Hover, pressed, disabled, and loading states would misrepresent its contract. An interactive control needs its own appropriate semantics and state behavior.

```astro
---
// compounds/PlantCard.astro
import Chip from '../primitives/Chip.astro';
interface Props { name: string; status: string; tone?: 'healthy' | 'attention' | 'neutral'; }
const { name, status, tone = 'healthy' } = Astro.props;
---
<article class="plant-card">
  <h3>{name}</h3>
  <Chip tone={tone}>{status}</Chip>
</article>
<style>
  .plant-card { padding: var(--space-sm); border-radius: var(--radius-soft); }
  h3 { margin: 0; } /* Structural reset, not a missing token. */
</style>
```

The compound owns arrangement and its fixed child contract; Chip owns status presentation. A `GardenView` composition supplies plant data and imports PlantCard. A guide example also imports PlantCard and supplies realistic controlled values. Neither copies Chip's internals.

A `SproutMark` unique instead preserves the canonical brand artwork. It may consume shared colors and allow sizing for real hosts without becoming a fake family of interchangeable logos. An illustration's intrinsic coordinates stay with its artwork; reusable geometry shared with other components belongs to tokens.

## Anatomy

Capture the useful contract alongside each nontrivial source or its final guide example:

- canonical instance, named parts, and required/optional slots;
- token and child dependencies, with consequential local rules identified;
- supported variants and relevant states, including keyboard focus and Reduced Motion for interactive/moving components;
- consumer-controlled sizing, content, and state versus component-owned behavior;
- constraints that preserve identity and accepted intent.

Use actual states and consumers. Unique specimens get configuration notes where useful; private helpers do not need invented public variant grids.

## Cohesion and lineage audit

For each changed visual rule, identify its owner, any duplicate, and its real or intended consumer. Inspect source imports and rendered use, not just names in a tracker. Resolve findings through reuse, promotion, or justified locality.

Scan for:

- unexplained raw colors, lengths, durations, easing, shadows, clips, and transforms outside their owners;
- shared recipes repeated beside or above their lowest appropriate owner;
- component internals copied into compounds, uniques, compositions, or guide examples;
- parallel production and guide implementations, or public callers bypassing a component's public seam;
- guide scaffolding, demo states, or global gallery styles leaking into production;
- unsupported taxonomy, unused abstractions, and hidden provisional adapters.

Literal and import searches locate candidates; inspect each in context. A pass means the scoped ownership checks have evidence and findings are resolved or explicitly justified. It is not proof of visual quality or production adoption. The delivery checks in `workflow.md` establish those separately.

Finish with a disposition for scoped sources that have no consumer: connect an intended consumer, merge equivalent ownership, remove an owned unused source, or retain it with a reason. A directly demonstrated foundation or a terminal composition can be intentional; neither needs an invented higher layer. Verify runtime mounting before calling a composition adopted.

## Keep settled rules executable

When recurring drift has an objective rule, encode it in the project's existing checks if that earns its maintenance cost. Examples include import boundaries, production isolation from guide fixtures, or a palette policy limited to named surfaces. Derive the rule and exceptions from accepted contracts; keep taste judgments in rendered review.

Scope rules explicitly and test representative violations, bypasses, and legitimate exceptions. In a mature product, existing debt can have a reviewed baseline that prevents growth while fixes reduce it. Report remaining debt separately from check success. Counts alone can miss a new violation replacing an old one, so inspect the changed code as well. A changed design decision revises the rule deliberately; an inconvenient failure does not justify silently broadening exceptions.

This pattern comes from EmotiTone's design-law lint (`f97b59ea`, inspected at `f1526054`). Its specific colour zones and service boundaries belong to that instrument, not every Design Lab system.

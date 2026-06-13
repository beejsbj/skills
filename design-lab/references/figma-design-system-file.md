# Figma Design System File

Use this reference when Figma is wanted and accessible, or when the run already has a Design System File.

When using Figma tools, first load the relevant Figma skill instructions for the tool being called. Do not call Figma tools from memory.

Typical routing:

- Create a new file: load `figma:figma-create-new-file`, then the required Figma tool instructions.
- Read or edit an existing file: load `figma:figma-use`.
- Generate or update a component library/design system from source material: load `figma:figma-generate-library` when available.
- Translate app pages/views into Figma: load `figma:figma-generate-design` when available.

If the needed Figma tool is not callable, authenticated, or authorized for the target file, Surface Gate should recommend the no-Figma code workflow or pause for access repair.

## Surface Rule

Run the Surface Gate before choosing the first extraction surface.

If Figma is wanted and accessible, the Design System File is the first extraction surface. The no-Figma code workflow is used only when Figma is unavailable or the user does not want to use it for the run.

The Design System File owns visual design truth. Code owns runtime behavior, generated behavior, data flow, accessibility implementation, platform constraints, and audio/music timing.

## Methodology Vs Generated Design System

Keep these separate:

- Methodology artifacts: `DESIGN_MAP.md`, gate packets, audits, logs, repository conventions, implementation plans.
- Generated design artifacts: Source Map, tokens, primitives, unique specimens, compounds, compositions, and inline Anatomy inside the Design System File.

Do not turn gates, audits, residue tables, or implementation process notes into generated design-system pages. A Design System File may include a visual mirror of `DESIGN_MAP.md`, but markdown remains canonical for methodology truth.

## Page Structure

Use this page order unless an existing file has a stronger convention:

1. `00 Design Map`: visual mirror of `DESIGN_MAP.md`; doctrine may appear as a Doctrine Compass here.
2. `01 Source Map`: moodboards, screenshots, old repo captures, code fossils, references, metaphors, and prior attempts.
3. `02 Tokens`: variables, styles, color/type/motion/effect/geometry vocabularies.
4. `03 Primitives`: reusable renderable units with standard variants and states.
5. `04 Unique Specimens`: singular preserved artifacts with local variations, not reusable variant families.
6. `05 Compounds`: reusable assemblies made from primitives and/or unique specimens.
7. `06 Compositions`: final screens, regions, or states that prove the grammar in context.

Anatomy lives inline beside the object it explains. Do not create a separate Anatomy page unless the user explicitly asks.

## Create Or Update Decision

Use an existing Design System File when:

- the user provides one
- the repo already references one
- the file already contains relevant tokens/components/source material

Create a new Design System File when:

- Figma is accessible
- no existing file is provided or discoverable
- Scope Gate confirms a durable Figma-backed run

Stay in no-Figma workflow when:

- Figma is unavailable
- the user does not want Figma for this run
- the task is only a chat-only audit or quick code implementation

Proof of update must include the file URL/id and the page/frame/component names created or changed.

## Artifact Rules

Tokens:
- Prefer Figma variables/styles for visual token truth.
- Mirror repo token names when they already exist and are valid.
- Record unresolved token ownership in `REPOSITORY_CONVENTIONS.md`.

Primitives:
- Build component sets only when the object has stable identity and standard reusable variation axes.
- Show states and variants that the system actually supports.
- Keep behavior-heavy decisions behind a Behavior Fidelity Boundary if Figma cannot prove them.

Unique specimens:
- Preserve singular artifacts that matter to the system.
- Allow local variations, but do not invent standard reusable variant axes.
- Mark why the artifact is not a primitive or compound.

Compounds:
- Compose primitives and/or unique specimens.
- Name child dependencies and slot contracts.
- Do not copy primitive internals into compound visuals unless a Promotion Gate approves a new lower-layer idea.

Compositions:
- Show final context.
- Use compositions to reveal missing primitives, compounds, or unique specimens before implementation.
- Push repeated grammar back down through the promote/prune/keep-local rule.

Anatomy:
- Place callouts, part maps, state/pose examples, dependencies, rules, and open decisions beside the design object.
- Link or summarize Anatomy in markdown only when needed for cross-session handoff.

## Figma Extraction Loop

1. Create or update `DESIGN_MAP.md`.
2. Run Surface Gate and record the decision.
3. Build or update the Design System File Source Map from raw material.
4. Create the initial `RAW_RECIPE_INVENTORY.md` from the Source Map and source files before layer extraction starts.
5. Classify candidates and scope the current layer.
6. Create the layer currently in scope: tokens, primitives, unique specimens, compounds, or compositions.
7. Add inline Anatomy where the object needs explanation or extraction support.
8. Update the raw recipe inventory and promote/prune/keep-local decisions as the file reveals new grammar.
9. Close the layer with `LAYER_CLOSURE.md`.
10. Move accepted artifacts into the Implementation Pass when code or a Live Style Guide is in scope.

## Finish Proof

For a Figma-backed Design Lab run, the Finish Gate must name:

- Design System File URL or file identifier.
- Source Map coverage.
- Token ownership.
- Layer closure artifacts.
- Any Behavior Fidelity Boundaries requiring code probes.
- Implementation Pass status, if live code is in scope.

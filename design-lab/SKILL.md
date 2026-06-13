---
name: design-lab
description: Design-system workflow for turning ambiguous design material into a formal, decomposed design system. Use when Codex is asked to work from any mix of repos, existing UI, Claude Design HTML, screenshots, moodboards, inspiration sites, metaphors, words, notes, Figma files, or partial components to discover intent, interview the user, define doctrine, classify tokens/primitives/unique specimens/compounds/compositions, create anatomy artifacts, extract reusable components, audit recipe gaps, and drive the design to a finished Design System File, live style guide, or code implementation with the user involved at taste and decision gates.
---

# Design Lab

Design Lab moves design work from raw taste-material to a finished, decomposed design system. It supports entry at any stage: early moodboard/metaphor, old rough site, Claude Design HTML, existing app repo, Figma Design System File, midstream style-guide surface, or extracted production component.

Core doctrine:

> When formalizing a component, every design decision must resolve to an existing lower-level idea, be promoted into one, or be pruned.

Glossary:

- `pattern`: a reusable doctrine tag for a named way of achieving a law.
- `raw recipe`: an unpromoted visual, structural, motion, interaction, or copy choice discovered in source material.
- `recipe gap`: a raw recipe that uses lower-level tokens but still lacks a named component-specific grammar.
- `drift`: an artifact that has wandered from doctrine and should be pruned or rewritten.
- `residue`: cross-cutting unnamed grammar discovered after extraction, regardless of which source artifact introduced it.
- `Design System File`: Figma file that owns visual design truth when Figma is wanted and accessible.
- `Anatomy`: visual formalization artifact with faces, poses, parts, dependencies, states, rules, and open decisions. Anatomy is not a taxonomy layer.
- `unique specimen`: singular preserved artifact that matters to the system but should not become a reusable family.
- `style-guide surface`: code or Figma surface that demonstrates, inspects, or proves the system without becoming source of truth.
- `visual source-of-truth surface`: the surface that owns visual design truth for this run, usually a Design System File when Figma is available or repo tokens/components when it is not.

## Operating Model

Treat this as a loop, not a waterfall:

```text
material -> archaeology <-> interview -> raw recipe inventory -> doctrine
         -> classify -> ideate within layer -> extract/formalize
         -> promote/prune -> anatomy -> residue proof
         -> layer closure -> user gate -> next layer
```

Archaeology and interview can iterate; use read-first evidence to ask better questions, then let answers redirect the archaeology.

Preflight order:

1. Run read-only recon.
2. If Figma is mentioned, wanted, or already part of the project, run Surface Gate. If the user explicitly forbids Figma for this run, record `wanted: no`, skip Figma tool checks, and choose the no-Figma workflow.
3. Run Scope Gate.
4. Run Intent and Doctrine gates.
5. Run Repository Conventions Gate before edits, implementation, route moves, file moves, or Figma writes.

See `references/taxonomy-and-doctrine.md` for the layer-scoped ideation procedure. See `references/anatomy-and-extraction.md` for anatomy, extraction, recipe-gap, and residue-proof procedure.

The taxonomy layers are:

- `tokens`: values, low-level recipes, constraints, semantic aliases.
- `primitives`: smallest named renderable ideas.
- `unique specimens`: singular preserved artifacts that may be complex, may appear directly in compositions or inside compounds, and do not become reusable families.
- `compounds`: stable assemblies of primitives and/or unique specimens that travel together.
- `compositions`: real screens, screen regions, or app states.

Anatomy is not a taxonomy layer. Use Anatomy artifacts inline beside any design object that needs formal explanation, extraction, or decision support.

Do not use `specimen` to mean generic documentation/inspection surface. In this methodology, `specimen` belongs to `unique specimen`. If a repo already uses "specimen" for guide cards, treat that as legacy/local wording and translate it to `style-guide surface`.

## First Move

Before executing, route the request by entry point:

- Raw words, metaphors, moodboards, screenshots: run intake and interview first.
- Existing repo or old site: run archaeology before proposing doctrine.
- Existing repo with generated output: read `.gitignore` and exclude ignored build/cache folders from source archaeology unless the user names them as evidence.
- Claude Design HTML or static preview files: preserve visual intent, then decompose.
- Existing style guide or kitchen sink: audit taxonomy and recipe gaps.
- Existing component extraction: run raw recipe inventory first, then formalize the component while enforcing promote/prune decisions.
- Midstream app integration: keep the style guide as a demonstration surface and make reusable components the implementation source of truth.
- Figma wanted and accessible: run Surface Gate, then create or update the Design System File first.

Read only as much reference as the current entry point needs:

| Entry point | Read |
|---|---|
| words, metaphors, moodboards, screenshots, old sites, repos | `references/intake-and-interview.md` |
| taxonomy, doctrine, layer boundaries, layer ideation, closure | `references/taxonomy-and-doctrine.md` |
| existing components, style guides, anatomy, extraction, recipe gaps, residue | `references/anatomy-and-extraction.md` |
| existing style guide, kitchen sink, partial components, midstream app integration | `references/intake-and-interview.md`, `references/taxonomy-and-doctrine.md`, then `references/anatomy-and-extraction.md` |
| Figma wanted/available or a Design System File exists | `references/intake-and-interview.md`, then `references/figma-design-system-file.md` |
| accepted Design System File needs code/live style guide | `references/implementation-pass.md` |
| durable workflow artifacts | `references/templates.md` |

## User Gates

Keep the user involved at decision points. Ask concise, evidence-tied questions rather than broad preference surveys.

Required gates:

- `Surface Gate`: before deciding whether the run starts in a Design System File or uses the current no-Figma code workflow.
- `Scope Gate`: before deciding how far the run must go.
- `Intent Gate`: before turning impressions into doctrine.
- `Doctrine Gate`: before treating rules as law.
- `Repository Conventions Gate`: before extraction changes where tokens, components, style-guide surfaces, Figma pages, or routes live.
- `Taxonomy Gate`: before moving artifacts between token/primitive/unique specimen/compound/composition.
- `Taste Gate`: before committing to a visual direction or major family.
- `Promotion Gate`: before promoting a raw design recipe downward or pruning it.
- `Finish Gate`: before calling the requested design-system or style-guide finish line complete. Record the user's accept/continue/pause decision.

If the user asks for autonomous execution, still preserve gates by making concrete assumptions explicit and marking unresolved decisions in the output.

Every gate needs a decision packet with: evidence, recommendation, alternatives rejected, unresolved risk, decision, and what unblocks the next step. After the decision is recorded, append a row to `DESIGN_LOG.md` when a durable log exists. Do not treat a named gate as complete if it only restates preferences.

A layer cannot close while any artifact in that layer has an unresolved promote/prune/keep-local decision, unless that decision is explicitly parked behind a named user gate.

Gate-parked does not mean complete. It can mean:

- `may advance`: next-layer work may continue because the unresolved item is bounded and marked `May Advance: yes`.
- `paused`: work should stop at the gate until the user or external state resolves it.
- `complete`: only allowed at Finish Gate when unresolved items are out of scope or explicitly accepted as deferred.

For long-running or resumed work, append gate decisions to `DESIGN_LOG.md` with date, gate name, decision, and artifact link.

Gate-to-loop mapping:

- `Surface Gate`: after read-only recon and Figma availability check, before first extraction surface is chosen.
- `Scope Gate`: after Surface Gate when Figma is relevant; otherwise after intake/recon and before doctrine or implementation.
- `Intent Gate`: after interview, before doctrine.
- `Doctrine Gate`: after doctrine draft, before classification becomes law.
- `Repository Conventions Gate`: before extraction edits or route/file moves.
- `Taxonomy Gate`: during classification and layer-scoped ideation.
- `Taste Gate`: whenever a visual direction would change after doctrine is set.
- `Promotion Gate`: during raw recipe inventory, extraction, and recipe-gap audit.
- `Finish Gate`: after residue proof, coverage audit, layer closure, and verification.

## Subagents

Use subagents when the work is parallelizable and mostly read-only. Give each one a narrow job and raw artifacts, not your conclusions.

Useful subagent roles:

- `repo-archaeologist`: read git history, old branches, implementation conventions, prior attempts.
- `visual-archaeologist`: inspect moodboards, images, screenshots, sites, and recurring visual language.
- `doctrine-drafter`: turn evidence into candidate design laws.
- `taxonomy-auditor`: classify artifacts and flag layer drift.
- `recipe-gap-hunter`: find raw values, shapes, motions, states, or CSS tricks trapped in higher layers.
- `component-extractor`: extract approved primitives/compounds into reusable app components.
- `taste-skeptic`: challenge whether the result still matches the intended impression.

Subagent rules:

- Default to read-only subagent tasks unless a gate has already approved implementation.
- Subagents cannot pass gates, close layers, or call the style guide complete.
- The main agent reconciles contradictions and presents the decision packet.
- Each subagent brief should include the relevant output schema or gate packet it must fill.
- If subagents are unavailable, run these roles sequentially as named phases and label artifacts with the role for traceability.

Example brief:

```text
Subagent: recipe-gap-hunter
Read-only: yes
Inputs: components/**, current RAW_RECIPE_INVENTORY.md, current TAXONOMY_SCHEMA.md
Output schema: "## Recipe Gaps: <artifact>" from anatomy-and-extraction.md
Do not: propose promotions, edit files, close gates
Return: filled output, plus candidates that do not fit the schema
```

Parallelize reconnaissance. Rejoin before decisions.

For pilots or environments without callable subagents, run the roles as labeled read-only passes in the main session and say they are simulated. Do not let a simulated role pass gates or close layers.

## Completion Definition

A Design Lab run is complete only when the requested finish line is met. For a fully decomposed design system or live style guide, require:

- Token groups are named, documented, and closed by the layer-closure checklist for current scope.
- Primitives consume tokens and expose clear APIs, states, variants, and anatomy.
- Unique specimens are explicitly marked and justified.
- Compounds compose primitives and/or unique specimens instead of copy-pasting their internals.
- Compositions prove the grammar in real context.
- Style-guide surfaces import or demonstrate the source of truth; they do not become the source of truth.
- Raw/new/unique material is promoted, pruned, or intentionally kept local.
- Style guide route/page renders or builds with the repo's closest verification command, recorded in `REPOSITORY_CONVENTIONS.md`.
- `RESIDUE_PROOF.md` records checked patterns such as raw hex colors, raw px values, raw durations/easings, repeated clip-paths, duplicated component internals, and unmarked unique specimens. Each hit must be zero or justified.
- Coverage audit maps every meaningful source artifact to a layer and resolution state, with no empty `Resolution` cells.
- Unresolved residue is zero or parked behind a named gate with owner, date, and unblock condition.
- Gate-parked work is not counted as complete unless it is out of scope or the user explicitly accepts it as deferred at Finish Gate.
- Remaining open decisions are listed as gates, not hidden in implementation.
- User explicitly accepts, continues, or pauses at the Finish Gate.

## Output Shape

Prefer durable repo artifacts over long chat-only analysis only after Scope Gate confirms that durable workflow files are wanted.

Choose an artifact mode:

- `chat-only audit`: no repo artifacts; use for scouting, comparing approaches, or testing the skill on a project without changing it.
- `light durable handoff`: create only the minimum handoff artifacts needed to resume safely.
- `full workflow`: create the full artifact set and update it throughout the run.

Default to `chat-only audit` for first contact with an unfamiliar repo. Upgrade to `light durable handoff` or `full workflow` only after Scope Gate names the artifact location.

Artifact location:

- Use an existing project planning/docs convention when one is clear.
- If no convention exists, recommend `docs/design-lab/` for durable methodology artifacts and record the decision in Repository Conventions Gate.
- Do not scatter methodology artifacts across the repo root unless the user or existing repo convention calls for that.

Full workflow artifacts:

- `DESIGN_MAP.md`: canonical methodology map for the run.
- `DESIGN_LOG.md`: append-only gate decisions for resumed work.
- `TAXONOMY_SCHEMA.md`: current taxonomy and source-of-truth map. This is not the Live Style Guide and does not own rendered component truth.
- `REPOSITORY_CONVENTIONS.md`: paths, naming, route/entry, and verification command.
- `COVERAGE_AUDIT.md`: per-source artifact mapping.

When applicable:

- `DESIGN_INTAKE.md`: ambiguous/raw input and intent capture.
- `SURFACE_GATE.md`: required when Figma is mentioned, wanted, available, or already part of the run.
- `ARCHAEOLOGY.md`: repo, old-site, fork, moodboard, or prior-attempt evidence.
- `RAW_RECIPE_INVENTORY.md`: required before extraction from previews, components, or compositions.
- `COMPONENT_EXTRACTION_PLAN.md`: extraction order and API decisions.
- `STYLE_GUIDE_PLAN.md`: style-guide/live-proof coverage plan.
- `ANATOMY.md`: per artifact formalization sheet when markdown handoff is needed.
- `PROMOTION_AUDIT.md`: promote/prune/keep-local decisions and recipe gaps.
- `RESIDUE_PROOF.md`: required for Finish Gate.
- `LAYER_CLOSURE.md`: required before advancing layers.
- `TASTE_CHECK.md`: visual-direction changes after doctrine.

When editing an app repo, follow its actual component conventions. For Vue/React/etc., make real reusable components first, then have style-guide surfaces import those components. When Figma is wanted and accessible, create/update the Design System File first, then implement accepted artifacts through the Implementation Pass.

---
name: design-lab
description: Compose or extend a cohesive design system from repos, existing UI, design HTML, screenshots, moodboards, or a written brief. Produces authoritative tokens and components, distinct unique specimens, and a final style guide. Use for a whole system or a sustained system-building pass, not a one-off visual tweak.
---

# Design Lab

Develop a chosen visual direction into a coherent, importable system. Explore and build in a temporary workbench; assemble the **style guide as the final output** from the resulting sources.

Material is a seed: extend it creatively where the brief leaves room. Existing accepted intent and production contracts are constraints to preserve.

## Two responsibilities

- **Creative direction — the user's taste authority.** Make and explain creative calls. Default to a concrete final taste review, with earlier clarification when missing intent or conflicting references would materially change the result. Use the workbench to make such a decision visible before multiplying it across the system. Follow any established project acceptance gates; an agent proposal is not user acceptance.
- **System coherence — the agent's responsibility.** Resolve taxonomy, tokens, imports, and component seams autonomously. Report scoped verification evidence and gaps; ownership of the work does not make a self-audit an unconditional guarantee.

Ask about meaningful intent or UX alternatives, not whether a hex should become a token. State reversible assumptions and keep working where an answer is unnecessary. Revisit a frozen direction only for user steering, a concrete contradiction, or a failed creative-floor review; record what changed and why.

## Two quality checks

**Cohesion:** every design decision has one appropriate owner. Reuse existing grammar, promote shared rules, or keep a justified singular rule local. Components consume their owners through real imports.

**Creative floor:** the result reads as a chosen direction, with clear hierarchy and meaningful interaction feedback. A coherent system can still look generic. Use [references/creative-floor.md](references/creative-floor.md) during exploration and on rendered results; structural correctness does not establish taste quality.

## The loop

```text
intake -> explore in workbench -> freeze direction -> build and systematize
       -> verify sources and compositions -> assemble final style guide
       -> verify delivered surfaces -> taste handoff
```

1. **Orient.** Read existing project design truth and inspect live Git/source state. Identify the brief, accepted constraints, production behavior, references, and intended deliverables. A reference export or current implementation is evidence, not automatic acceptance. Read [references/workflow.md](references/workflow.md) now to establish the tracker, temporary paths, and delivery claims.
2. **Explore.** Use the creative-floor protocol: treatments within an established direction, otherwise several concretely distinct directions. Try the consequential visual or UX uncertainty in a small temporary workbench before extending it everywhere.
3. **Freeze.** Write one visible direction block in the tracker: visual choices, rationale, liked details to preserve, and alternatives considered. Mark it proposed, chosen under delegated authority, or user-accepted accurately. Resolve any required intent question before dependent implementation.
4. **Build and systematize.** Work one coherent unit at a time in dependency order. Read [references/systematizing.md](references/systematizing.md) for classification, reuse, anatomy, and ownership. Establish one source, drive it in the workbench, and prove it in a realistic composition. In an authorized migration, adopt it through real production consumers while preserving behavior. Advance the tracker after each completed unit or settled decision.
5. **Verify the system.** Check ownership and rendered creative quality, plus relevant build, responsive, accessibility, and behavior evidence as specified in `references/workflow.md`. Fix findings at their owners. Keep unaccepted or unverified claims visible.
6. **Assemble the final style guide.** Curate the resulting tokens, primitives, compounds, unique specimens, and compositions into a coherent reference surface. Import their authoritative sources; add useful anatomy, supported variants/states, and at least one substantial hero composition. Move useful demonstration harnesses from the workbench without copying component implementations. Experimental alternatives remain in the workbench.
7. **Verify and hand off.** Inspect the actual guide and any changed production surfaces, including isolation from temporary/gallery code. Retire only owned temporary artifacts whose purpose is complete. Deliver the review report and leave the tracker ready for continuation.

The guide can evolve on later passes, but it is the publication of each pass's system, not its scratchpad. A guide implementation defect is fixed in the guide; a design or component defect is fixed at its source and reflected back into the guide.

## Taxonomy

The reusable hierarchy is:

`tokens` → `primitives` → `compounds` → `compositions`

**Unique specimens are their own category, outside that ladder.** They may consume tokens, primitives, or compounds and be consumed where their contract fits. Their actual dependencies must remain acyclic. Singularity concerns identity, not size, complexity, or how many places use them.

A **guide example** demonstrates any category; it is not automatically a unique specimen. Classification chooses what an artifact is; the reuse decision chooses whether to snap to an existing component, extend a variant, or establish a new identity.

## Framework and source policy

- Authoritative components match the consuming app: Vue for Vue, React for React. Use the repo's existing component and guide conventions.
- With no consuming app or stronger convention, Astro components and a static Astro guide are a reasonable default. Interactive examples may require client JavaScript; static output does not imply zero JavaScript.
- When using Astro to host Vue/React examples, the app's sources remain native to its framework. Adding a guide framework to an existing app must earn its integration cost.
- Both guide and production consume the same public component seam. Private helpers stay beside that source. Identify the actual document/state/runtime owner before adapting a mature component; a visually shared wrapper beside a parallel runtime is incomplete integration.
- Workbench and guide own demonstration controls and fixture state. Their framing, styles, and prototype copy stay isolated from production.

## Continuity and delegation

Use one current tracker, preferably an existing project record; otherwise create `design-lab/TRACKER.md`. It preserves direction, independent unit claims, path ownership, verification, and the next unresolved decision. Detailed format and temporary-path lifecycle live in `references/workflow.md`. Keep historical receipts in an existing design log or Git rather than multiplying methodology files.

Keep one hand on construction so dependent source changes share a visual point of view. Delegate bounded read-only recon when useful. A fresh reviewer can inspect the rendered creative floor or the final lineage/behavior diff; give it the brief, sources, and evidence, then fix findings and recheck affected claims. Delegation is optional, not ceremony.

## Ready-for-review report

Keep it short and concrete:

- **Direction realized:** the chosen direction, useful alternates, and creative extensions beyond the input.
- **Look here first:** the guide URL/path and hero composition; show visual evidence where available.
- **Needs your eye:** remaining taste/UX judgments and acceptance status.
- **System and adoption:** source, guide, and production claims separately, with checks actually run and unresolved limitations.
- **Continuation:** tracker path, next unit or decision, and any temporary artifact still needed.

A passing build does not prove visual quality; a guide does not prove adoption; a review-ready proposal does not prove acceptance.

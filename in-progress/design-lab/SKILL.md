---
name: design-lab
description: Build, tighten, extend, or reimagine a design system from raw references or an existing product. Repeatedly resolve design and source-ownership gaps through temporary workbenches, real components, and a final style guide. Use for sustained system work, not a one-off visual tweak.
---

# Design Lab

Turn raw material or an existing product into a coherent, importable system. Keep choosing and resolving the next concrete gap until the agreed pass is complete. Explore in temporary workbenches; publish the resulting sources through the **final style guide**.

Material is evidence and a creative seed. Preserve accepted intent and production contracts while developing what the brief leaves open. A finished site can enter at inspection and reconciliation; an established system can enter with one new unit or a scoped reimagining pass.

## Two responsibilities

- **Creative direction — the user's taste authority.** Make and explain creative calls. Default to a concrete final taste review, with earlier clarification when missing intent or conflicting references would materially change the result. Use the workbench to make such a decision visible before multiplying it across the system. Follow any established project acceptance gates; an agent proposal is not user acceptance.
- **System coherence — the agent's responsibility.** Resolve taxonomy, tokens, imports, and component seams autonomously. Report scoped verification evidence and gaps; ownership of the work does not make a self-audit an unconditional guarantee.

Ask about meaningful intent or UX alternatives, not whether a hex should become a token. State reversible assumptions and keep working where an answer is unnecessary. Reassess a frozen direction for user steering, a concrete contradiction, or a failed creative-floor review. Correct implementation or revise proposals within delegated scope; changing a protected accepted direction needs authority from the current brief or a concrete user decision. Record what changed and why.

When the input has no clear direction, propose and build a direction for review within the brief. Record it as a proposal; the user's permission to explore does not itself accept the result.

## Two quality checks

**Cohesion:** every design decision has one appropriate owner. Reuse existing grammar, promote shared rules, or keep a justified singular rule local. Components consume their owners through real imports.

**Creative floor:** the result reads as a chosen direction, with clear hierarchy and meaningful interaction feedback. A coherent system can still look generic. Use [references/creative-floor.md](references/creative-floor.md) during exploration and on rendered results; structural correctness does not establish taste quality.

## The loop

```text
inspect material + current truth -> bound the pass and map gaps
                                      |
             choose next gap -> explore / reconcile -> formalize
                    ^                                      |
                    +---- record result <---- verify in use-+
                               |
                  scope satisfied -> publish + verify guide
                               |
                     taste review / new evidence
                               +----> reopen affected gaps
```

1. **Orient and bound.** Read the project's accepted direction and current tracker, then inspect live Git, source, and available rendered material. Read [references/workflow.md](references/workflow.md) for intake and continuation. Establish the input's identity, scope, preserved behavior, adoption authority, and observable finish. Inventory enough real surfaces and states to expose the system's gaps; distinguish observed material from inferred contracts.
2. **Choose the next gap.** Use the tracker to select a concrete unresolved definition, ownership conflict, missing consumer, or verification failure. Follow the user's named priority; otherwise choose the gap that unlocks useful dependent work. Name its owner, evidence, affected consumers, and finish condition. Skip already-established claims. Exploration may compare a whole layer; source promotion follows actual dependencies.
3. **Resolve the uncertainty.** Reconcile structural drift directly. For a visual question, use [references/creative-floor.md](references/creative-floor.md) to build the smallest useful comparison in a temporary workbench. Make units inspectable and show them in realistic context. Record the direction, rationale, and liked details as proposed, chosen under delegated authority, or user-accepted. Ask at a consequential taste/intent fork or an established gate; continue independent work while that answer is pending.
4. **Formalize and consume.** Apply [references/systematizing.md](references/systematizing.md): snap to an existing contract, extend it, establish a new owner, or keep a justified local rule. Preserve distinct uniques. Drive the authoritative source through a real specimen and composition. When adoption is in scope and its gates are met, wire real production consumers through that same seam. Keep defects found in experiments attached to the unit's adoption brief, with their fix or deferral authority explicit.
5. **Verify and repeat.** Check source lineage, rendered creative quality, and the relevant build, behavior, responsive, and accessibility evidence in `references/workflow.md`. Fix each finding at its owner and recheck affected consumers. Update independent claims and the queue after a meaningful result; then select the next actionable gap without waiting for another prompt. Required unresolved work keeps the pass open. A repeated failure calls for a changed diagnosis or a concrete blocker, not more unexamined variation.
6. **Publish and review.** Once scoped sources and in-scope adoptions are verified, assemble or update the final guide from authoritative sources, with useful anatomy, supported states, and a substantial representative composition. Verify the delivered guide and changed production surfaces, account for unused sources and temporary artifacts, and report remaining taste decisions precisely. A proposal may be ready for review while acceptance remains pending. Feedback reopens the affected claims and their dependents; it does not restart the whole system.

The guide publishes each pass's resulting system. Move useful demonstration harnesses into it without copying implementations; experiments remain identifiable as experiments. Fix guide layout in the guide and component defects at their source. Subsequent passes reuse the accepted baseline, tracker, sources, and guide.

## Taxonomy

The reusable hierarchy is:

`tokens` → `primitives` → `compounds` → `compositions`

**Unique specimens are their own category, outside that ladder.** They may consume tokens, primitives, or compounds and be consumed where their contract fits. Their actual dependencies must remain acyclic. Singularity concerns identity, not size, complexity, or how many places use them.

A **guide example** demonstrates any category; it is not automatically a unique specimen. Classification chooses what an artifact is; the reuse decision chooses whether to snap to an existing component, extend a variant, or establish a new identity.

## Framework and source policy

- The workflow separates direction, ownership, demonstration, and adoption across media. Its current implementation guidance and verification are for web interfaces; establish the target medium's source and demonstration contracts before claiming support elsewhere.
- Authoritative components match the consuming app: Vue for Vue, React for React. Use the repo's existing component and guide conventions.
- With no consuming app or stronger convention, Astro components and a static Astro guide are a reasonable default. Interactive examples may require client JavaScript; static output does not imply zero JavaScript.
- When using Astro to host Vue/React examples, the app's sources remain native to its framework. Adding a guide framework to an existing app must earn its integration cost.
- Both guide and production consume the same public component seam. Private helpers stay beside that source. Identify the actual document/state/runtime owner before adapting a mature component; a visually shared wrapper beside a parallel runtime is incomplete integration.
- Workbench and guide own demonstration controls and fixture state. Their framing, styles, and prototype copy stay isolated from production.

## Continuity and delegation

Use one current tracker, preferably an existing project record; otherwise create `design-lab/TRACKER.md`. It preserves direction, independent unit claims, path ownership, verification, and the next unresolved decision. Detailed format and temporary-path lifecycle live in `references/workflow.md`. Keep historical receipts in an existing design log or Git rather than multiplying methodology files.

Keep one owner for direction and shared sources. Delegate bounded recon, independent implementation, or verification when the work separates cleanly. Give each worker a concrete outcome, allowed paths, preserved contracts, and required evidence; serialize shared tokens and tracker integration. Inspect and integrate their results before closing claims. A fresh reviewer can check rendered quality or lineage against the brief. Use delegation when it shortens the loop.

## Ready-for-review report

Keep it short and concrete:

- **Direction realized:** the chosen direction, useful alternates, and creative extensions beyond the input.
- **Look here first:** the guide URL/path and hero composition; show visual evidence where available.
- **Needs your eye:** remaining taste/UX judgments and acceptance status.
- **System and adoption:** source, guide, and production claims separately, with checks actually run and unresolved limitations.
- **Continuation:** tracker path, next unit or decision, and any temporary artifact still needed.

A passing build does not prove visual quality; a guide does not prove adoption; a review-ready proposal does not prove acceptance.

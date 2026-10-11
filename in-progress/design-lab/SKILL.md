---
name: design-lab
description: Orchestrate subagents to build, tighten, extend, or reimagine a design system from raw references or an existing product. Present 3–5 variations when direction is open, then coordinate sources, verification, and a final style guide. Use for sustained system work, not a one-off visual tweak.
---

# Design Lab

Orchestrate subagents to turn raw material or an existing product into a coherent, importable system. Own the scope, brief, work queue, human review, and integration; dispatch bounded execution to workers. Keep selecting and integrating the next concrete gap until the agreed pass is complete. Explore in temporary workbenches; publish the resulting sources through the **final style guide**.

Material is evidence and a creative seed. Preserve accepted intent and production contracts while developing what the brief leaves open. A finished site can enter at inspection and reconciliation; an established system can enter with one new unit or a scoped reimagining pass.

## Two responsibilities

- **Creative direction — the user's taste authority.** Make visual choices reviewable before multiplying them across the system. For an open direction, present alternatives for selection as below. Within an established direction, make and explain scoped creative calls, with clarification where intent or conflicting references would materially change the result. Follow project acceptance gates; an agent proposal is not user acceptance.
- **System coherence — the orchestrator's responsibility.** Coordinate taxonomy, tokens, imports, and component seams autonomously. Inspect worker results and report scoped verification evidence and gaps; delegating execution leaves responsibility for the whole with you.

Ask about meaningful intent or UX alternatives, not whether a hex should become a token. State reversible assumptions and keep working where an answer is unnecessary. Reassess a frozen direction for user steering, a concrete contradiction, or a failed creative-floor review. Correct implementation or revise proposals within delegated scope; changing a protected accepted direction needs authority from the current brief or a concrete user decision. Record what changed and why.

When direction is open, have workers build **3–5 meaningfully distinct rendered variations** under a shared brief. Present comparable previews with stable names, rationale, and tradeoffs, then wait for the user's choice or requested revisions before promoting a direction or building its full system. You may recommend; that is not the selection. Continue work that does not depend on the choice. Only an explicit instruction delegating selection for this pass changes this gate.

## Two quality checks

**Cohesion:** every design decision has one appropriate owner. Reuse existing grammar, promote shared rules, or keep a justified singular rule local. Components consume their owners through real imports.

**Creative floor:** the result reads as a chosen direction, with clear hierarchy and meaningful interaction feedback. A coherent system can still look generic. Use [references/creative-floor.md](references/creative-floor.md) during exploration and on rendered results; structural correctness does not establish taste quality.

## The loop

```text
inspect material + current truth -> bound the pass and map gaps
                                      |
           choose + dispatch -> explore / reconcile -> formalize
                    ^                                      |
                    +---- record result <---- verify in use-+
                               |
                  scope satisfied -> publish + verify guide
                               |
                     taste review / new evidence
                               +----> reopen affected gaps
```

1. **Orient and bound.** Read the project's accepted direction and current tracker, then inspect live Git, source, and available rendered material. Read [references/workflow.md](references/workflow.md) for intake and continuation. Establish the input's identity, scope, preserved behavior, adoption authority, and observable finish. Inventory enough real surfaces and states to expose the system's gaps; distinguish observed material from inferred contracts.
2. **Choose and dispatch the next gap.** Use the tracker to select a concrete unresolved definition, ownership conflict, missing consumer, or verification failure. Follow the user's named priority; otherwise choose the gap that unlocks useful dependent work. Give a worker its owner, evidence, affected consumers, write boundary, and finish condition using `references/workflow.md`. Skip already-established claims. Exploration may compare a whole layer; source promotion follows actual dependencies.
3. **Resolve the uncertainty.** Delegate structural reconciliation directly. For a visual question, brief exploration workers using [references/creative-floor.md](references/creative-floor.md) and integrate their work into the smallest useful comparison. Make units inspectable and show them in realistic context. Record direction and liked details as proposed, chosen under delegated authority, or user-accepted. Apply the open-direction selection gate above; within accepted direction, ask only at a consequential taste/intent fork or an established gate.
4. **Commission formalization and adoption.** Brief implementation workers using [references/systematizing.md](references/systematizing.md): snap to an existing contract, extend it, establish a new owner, or keep a justified local rule. Preserve distinct uniques. Require the authoritative source to be driven through a real specimen and composition. When adoption is in scope and its gates are met, assign real production consumers to that same seam. Keep defects found in experiments attached to the unit's adoption brief, with their fix or deferral authority explicit.
5. **Verify, integrate, and repeat.** Inspect worker changes and evidence; use a separate review worker for meaningful lineage, behavior, or visual risks. Check the relevant evidence in `references/workflow.md` against the integrated result. Route findings back to their owners and recheck affected consumers. Update independent claims and the queue after a meaningful result; then dispatch the next actionable gap without waiting for another prompt. Required unresolved work keeps the pass open. A repeated failure calls for a changed diagnosis or a concrete blocker, not more unexamined variation.
6. **Publish and review.** Once scoped sources and in-scope adoptions are verified, commission final-guide assembly or updates from authoritative sources, with useful anatomy, supported states, and a substantial representative composition. Inspect the integrated guide and changed production surfaces against the verification evidence, account for unused sources and temporary artifacts, and report remaining taste decisions precisely. A proposal may be ready for review while acceptance remains pending. Feedback reopens the affected claims and their dependents; it does not restart the whole system.

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

## Orchestration and continuity

Use one current tracker, preferably an existing project record; otherwise create `design-lab/TRACKER.md`. It preserves direction, independent unit claims, path ownership, verification, and the next unresolved decision. Detailed format and temporary-path lifecycle live in `references/workflow.md`. Keep historical receipts in an existing design log or Git rather than multiplying methodology files.

Scoped inspection, exploration, implementation, verification, and guide assembly run through subagents. Keep planning, user decisions, cross-unit judgment, tracker updates, and final integration with the orchestrator. Direct edits should serve integration or a small correction, rather than replace a delegated unit.

Use available worker routes and the smallest capable model for each brief. Parallelize independent units or candidate explorations with separate write ownership; serialize shared tokens, registrations, and dependent promotions. Workers return bounded results to the orchestrator, which decides the next assignment. Three to five variations is a review-set size, not a required worker count.

Read the dispatch contract in `references/workflow.md` before assigning work. If no delegation route works, prepare the scope and worker briefs, report the execution blocker, and leave a precise resume action; do not silently turn the whole pass into solo implementation.

## Ready-for-review report

Keep it short and concrete:

- **Direction realized:** the chosen direction, useful alternates, and creative extensions beyond the input.
- **Look here first:** the guide URL/path and hero composition; show visual evidence where available.
- **Needs your eye:** remaining taste/UX judgments and acceptance status.
- **System and adoption:** source, guide, and production claims separately, with checks actually run and unresolved limitations.
- **Continuation:** tracker path, next unit or decision, and any temporary artifact still needed.

A passing build does not prove visual quality; a guide does not prove adoption; a review-ready proposal does not prove acceptance.

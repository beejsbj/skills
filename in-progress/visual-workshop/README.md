# Visual Workshop — candidate packet

Status: in progress. This is not an installed skill or a settled workflow.

## Thesis

Visual Workshop is a persistent, inspectable **surface** where a person and an agent can develop visual work together. It should exist beyond EmotiTone and should not hard-code one production sequence. The surface keeps the visual state, references, alternatives, annotations, and current judgments available so collaboration happens against the work rather than through prose alone.

The agent may use browser previews, screenshots, Figma, image generation, code, or domain-specific design skills behind the surface. Those are instruments; the workshop is the shared place where their results can be seen and judged together.

## Boundaries to test

- `design-lab` composes or extends a whole design system. Visual Workshop should also serve smaller or differently scoped visual work.
- Project skills such as `emotitone-design-system` hold project-specific doctrine and state. Visual Workshop should remain portable across projects.
- Figma, browser preview, image generation, and implementation tools produce or inspect artifacts. Visual Workshop should coordinate what becomes visible without replacing those capabilities.
- The surface should preserve taste decisions and visual continuity without growing into a general project manager.

## Evidence so far

The current concept comes from the September 2026 T3 Code skill review:

- “Visual workshop could exist beyond just EmotiTone.”
- “Visual workshop is less about a flow … and more about a surface.”

The broader session history still needs to be mined for repeated examples, failure modes, and the actual visual objects that belonged on the surface.

## Open questions

- Is the surface one concrete implementation, such as a local web canvas, or a contract that can inhabit T3 preview, Figma, and other environments?
- What persists between sessions: screenshots, selected directions, annotations, comparison states, implementation receipts, or some smaller set?
- Which requests should invoke it instead of `design-lab`, a project-specific design skill, or ordinary visual implementation?
- What marks a workshop engagement complete without turning the surface into a rigid flow?
- How should the human point, compare, reject, and preserve visual alternatives with minimal prose?

## Promotion bar

Promote this into a `SKILL.md` only after:

1. repeated T3 Code sessions supply concrete evidence for the shared-surface need;
2. a prototype supports at least two materially different visual contexts;
3. its boundary from `design-lab` and project-specific design skills is observable in realistic requests;
4. the surface and persistence contracts are clear enough to forward-test.


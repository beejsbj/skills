# Implementation Pass

Use this reference when accepted design artifacts need working repo tokens, components, composition views, code probes, or a Live Style Guide.

Implementation Pass is part of the Design Lab methodology. It is not a Design System File page and it is not automatic Figma-to-code export.

## Inputs

- `DESIGN_MAP.md`, especially Doctrine Compass, Formalization Surfaces, and Code Map.
- Surface Gate decision.
- `REPOSITORY_CONVENTIONS.md`.
- Accepted Design System File artifacts, when Figma is used.
- `RAW_RECIPE_INVENTORY.md`, `PROMOTION_AUDIT.md`, and relevant `LAYER_CLOSURE.md`.
- Existing repo token files, components, routes, and style-guide surfaces.

## Ownership Boundary

When a Design System File exists:

- Figma owns visual design truth for tokens, primitives, unique specimens, compounds, compositions, and inline Anatomy.
- Code owns runtime behavior, data flow, generated visuals, accessibility implementation, platform details, audio/music timing, persistence, and integration.
- The Live Style Guide is implementation proof and part of the finished code deliverable, not the canonical generated design system.

When no Design System File is used, repo tokens/components and the Live Style Guide may be the primary formalization surfaces.

## Pass Order

1. Confirm Repository Conventions Gate: token source, component locations, style-guide route, verification command.
2. Confirm branch, dirty files, untracked files, user-owned changes, safe edit scope, and checkpoint plan.
3. Map accepted design artifacts to code targets in `DESIGN_MAP.md` Code Map.
4. Implement or update token sources first.
5. Implement primitives before unique specimens or compounds that depend on them.
6. Implement unique specimens with singular-role markers and without standard reusable variant axes.
7. Implement compounds by composing primitives and/or unique specimens.
8. Implement composition views only after their lower-layer dependencies are accepted or gate-parked with `May Advance: yes`.
9. Update Live Style Guide surfaces to import real source-of-truth components.
10. Run residue proof and verification.

## Code Probe Rule

Create a Code Probe when a decision crosses a Behavior Fidelity Boundary:

- generated visuals or randomized geometry
- live interaction, gestures, transitions, or focus behavior
- state machines, persistence, data flow, or async loading
- audio/music timing
- platform-specific accessibility or layout behavior

Record each probe in `STYLE_GUIDE_PLAN.md` and link the result from `DESIGN_MAP.md`.

## Extraction Rule

During implementation, every raw/new/unique decision must resolve through the same rule:

```text
promote downward, prune, keep local, or gate-park
```

Do not introduce raw visual values in code just because they were easy to copy from Figma. If the Design System File exposes a new reusable idea, promote it into the right layer before coding against it.

## Live Style Guide Rule

The Live Style Guide should prove the implemented system with real components:

- import reusable components rather than duplicate markup
- expose states and variants that exist in code
- include unique specimens only as marked singular artifacts
- include compositions when they prove final context
- show code-probe outputs when behavior cannot be judged from Figma alone

## Verification

Choose the closest repo command by reading `package.json`, README docs, existing Storybook/style-guide scripts, or prior repo convention. Record it in `REPOSITORY_CONVENTIONS.md`.

Verification should not create dependency or manifest churn. Before installing or running a package manager command, identify the repo's current package manager and lockfile, use no-autopin/no-save behavior when the tool supports it, and record any generated output or manifest changes. Do not keep changes to `package.json`, lockfiles, package-manager fields, `.npmrc`, `.yarnrc`, or equivalent dependency metadata unless dependency scope was explicitly accepted by the user.

Before Finish Gate:

- run the verification command when feasible
- visually inspect the Live Style Guide when frontend output changed
- run residue proof patterns for raw values and duplicated internals
- update `COVERAGE_AUDIT.md` with implemented/deferred status
- record open decisions as named gates, not hidden TODOs

# Workbench, tracker, and delivery

Use this reference at intake, when promoting temporary work, and before handoff. Its purpose is continuity and verifiable ownership across a design-system pass.

## Establish the boundary

Inspect the current branch and dirty tree. Read any existing tracker and accepted definitions before revisiting design questions; compare those decisions with source and observed behavior. Raise a material contradiction instead of silently treating the newest code as accepted intent.

State the current unit or pass, preserved behavior, intended deliverables, and observable completion condition. For a migration, identify real production consumers and the state/document/runtime owner. For greenfield work, name the realistic composition that will prove the system. Work through dependencies without forcing an entire system to be complete before one useful unit can advance.

Production adoption is a separate scope decision: perform it when requested or implied by the task, subject to established acceptance gates. A style-guide-only request does not authorize product replacement. Preserve existing behavior while changing visual ownership; record unrelated functional defects or ideas with a durable pointer and continue the design scope.

## Separate the places

Resolve these roles from the actual repo. Example paths are choices, not a required scaffold:

| Role | Example | Responsibility |
| --- | --- | --- |
| Current truth | `design-lab/TRACKER.md` or the existing project tracker | Direction, unit claims, paths, unresolved decisions, evidence |
| Raw references | An existing export, screenshot folder, or sibling repo | Input evidence; no inferred acceptance or runtime authority |
| Temporary workbench | `src/design-lab/workbench/` with a development-only route | Exploration, comparison controls, candidate compositions, realistic fixtures |
| Authoritative sources | Existing token and component directories | One implementation per contract, outside workbench and guide |
| Final style guide | Existing guide route, or a dedicated static guide | Curated reference importing authoritative sources |
| Production | Existing app screens/compositions | Real state, content, actions, and consumers when adoption is in scope |

The workbench is temporary **in role**. Keep it in the repository when unresolved work must survive sessions; a disposable system temp directory alone is a poor handoff. Isolate its route, fixtures, and styles from normal production entry points. Use the smallest harness needed to expose the current uncertainty, not a second design-system app.

Build stable components at their intended authoritative paths. When a candidate needs a provisional source path, record its current owner, consumers, intended destination, and promotion/retirement condition in the tracker. Move and rewire that source on promotion; do not leave a copied workbench implementation behind. A temporary adapter must name the unresolved downstream dependency it preserves and remain visible until that dependency closes.

A production-only preservation adapter has no design authority or final-guide entry merely because it keeps existing functionality reachable. For example, EmotiTone's temporary `LegacyKeyboardControls.vue` preserved displaced settings until the accepted Control Bar replaced it; the adapter then retired rather than becoming another component family.

At the end of a pass, move reusable demonstration harnesses into guide examples and remove owned dead imports/routes/styles after checking their consumers. Retain experiments that still answer an open question and mark their status. Preserve unrelated work and reference artifacts. Record the resolved paths so the next session does not rediscover or resurrect retired authorities.

## One tracker for current truth

Reuse an existing tracker, including a differently named `DESIGN_SYSTEM_TRACKER.md`. Otherwise create `design-lab/TRACKER.md` outside the final guide. Its location does not make it a component source. Keep a small pointer in the project's agent instructions when cross-session discovery needs one; avoid copying the workflow there.

The tracker holds:

- **Mission and constraints:** scope, preserved behavior, accepted direction/liked details, and current proposal where still unaccepted.
- **Current frontier:** active unit, dependencies, the next unresolved decision, and any question awaiting the user.
- **Unit map:** the independent claims below, exact source/consumer paths, and evidence pointers.
- **Temporary-path map:** workbench, provisional sources/adapters, intended destinations, and exit conditions.
- **Latest verification:** scoped checks and visual evidence, gaps, and the next action.

Keep these claims independent:

| Claim | Record | Does not establish |
| --- | --- | --- |
| Definition | Proposed, accepted with a receipt, disputed, or not yet defined | A file or render does not establish user acceptance |
| Authoritative source | Exact owner/public seam, competing source if unresolved | A tidy component does not establish adoption |
| Real demonstration | Workbench and final-guide example paths/status separately; each imports the real source | A mock or copied renderer does not establish a real example |
| Production adoption | Named actual consumers; partial, complete, deferred, or not in scope | An importable library or greenfield demo does not establish production use |

For example, a Button can have a proposed definition, a working source, and a real workbench while its guide entry is pending and production adoption is out of scope. That is a valid intermediate state, not an accepted or fully delivered unit. Conversely, existing production use does not settle a disputed definition.

Update current truth after settled decisions, promotions, meaningful verification, and handoff. Replace resolved frontier questions rather than appending the conversation. A short acceptance receipt records what was accepted and its source; silence or an agent recommendation is not that receipt. Maintain named design constraints at the level needed to prevent their loss; keep implementation detail and historical receipts in sources, Git, or an existing `DESIGN_LOG.md`. Add a separate log only when chronology outgrows the tracker.

Avoid stale claims about ahead counts, dirty files, running servers, or other sessions; recompute them live. Mark recorded verification with its revision/date and refresh affected claims after changes. One unit closing does not accept its siblings or a whole composition.

## Delivery checks

Choose checks proportional to the changed surface and use the repo's actual commands. Record what was observed, not an aspirational checklist.

1. **Source and runtime lineage.** Apply `systematizing.md` to the changed dependency graph. Confirm real imports and the public seam, including underlying document/state signals for complex integrations. Search remaining legacy/provisional paths and identify any still-needed consumer. Check that adjacent controls, events, and product access survived migration.
2. **Executable verification.** Run relevant existing focused checks, type-check, and build where available. Add regression coverage when a changed contract or discovered bug warrants it; do not write tests merely to restate token values. Separate unrelated baseline failures from introduced failures.
3. **Rendered evidence.** Inspect the real composition and final guide, not only isolated components. Include representative narrow and wide hosts plus consequential variants/states: long or empty content, loading/errors, overflow, and coupled density where applicable. Inspect the guide's own layout as well as its component hosts; a narrow example inside an overflowing gallery does not establish a responsive guide. Run the creative-floor review on these rendered surfaces.
4. **Interaction and accessibility.** For changed interactive surfaces, exercise native pointer and keyboard behavior, accessible names, focus visibility and reachability, disabled states, and relevant contrast. Check Reduced Motion for moving components and forced colors when custom paint affects visibility. In migrations, compare against existing behavior; a visually correct result that removes input or control access is incomplete.
5. **Isolation and cleanup.** Confirm production does not depend on workbench fixtures, gallery typography, comparison state, or prototype copy. Guide examples drive the authoritative source with realistic controlled inputs; they do not invent a second clock, document, or behavior path. Inspect scoped temporary removal and remaining tracker pointers.

Save useful screenshots or measurements using the repo's evidence convention and link them from the tracker. If capture fails, try an available supported alternative; label DOM, computed-style, interaction, or screenshot evidence accurately. A build, HTTP 200, or DOM check does not substitute for rendered inspection. If a required check cannot be completed, report the limit and keep that claim unverified instead of declaring the whole pass successful.

After a correction, rerun affected checks and update their evidence. A fresh read-only lineage review is useful for substantial migration or complex state integration; it should check ownership, behavior preservation, production/guide seams, and hidden adapters, not merely count tokens.

## Provenance

Adapted from Burooj's EmotiTone visual-migration work in August–September 2026 and the repo-owned `emotitone-design-system/SKILL.md`. Specific evidence in `emotitone-solfrege` includes `12c594b` (independent unit claims), `1c2267c` (tracker/log consolidation), `5da92b2` (one public Knob source), `4b3e49a` (CodeStrip's real editor ownership), `6867a42` (preserving displaced controls and selection), and `5516c05` (shared instrument-bar tokens). These are provenance, not runtime dependencies or authority for another project's taste. The temporary-workbench/final-guide separation follows Burooj's September 11 correction; EmotiTone's workbenches historically lived inside its guide.

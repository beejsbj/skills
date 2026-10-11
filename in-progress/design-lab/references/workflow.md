# Workbench, tracker, and delivery

Use this reference at intake, when promoting temporary work, and before handoff. Its purpose is continuity and verifiable ownership across a design-system pass.

## Establish the boundary

Inspect the current branch and dirty tree. Read any existing tracker and accepted definitions before revisiting design questions; compare those decisions with source and observed behavior. Raise a material contradiction instead of silently treating the newest code as accepted intent.

State the current unit or pass, preserved behavior, intended deliverables, and observable completion condition. For a migration, identify real production consumers and the state/document/runtime owner. For greenfield work, name the realistic composition that will prove the system. Work through dependencies without forcing an entire system to be complete before one useful unit can advance.

Production adoption is a separate scope decision: perform it when requested or implied by the task, subject to established acceptance gates. A style-guide-only request does not authorize product replacement. Preserve existing behavior while changing visual ownership; record unrelated functional defects or ideas with a durable pointer and continue the design scope.

### Enter from the material that exists

| Starting point | First useful work |
| --- | --- |
| Brief, screenshots, moodboard, or disconnected design files | Identify source provenance, intended use, liked details, and missing states. Propose contracts where evidence is incomplete; when direction is open, commission the 3–5 variations and user selection defined in `SKILL.md`. |
| Finished site or application | Compare production, any guide, and accepted references. Map actual owners and behavior before extracting or consolidating. Existing implementation is a baseline, not automatic taste acceptance. |
| Established system with new work or drift | Start from the affected units and consumers. Reuse settled definitions and reopen only claims touched by the change. |
| Requested reimagining | Keep the accepted baseline available beside experiments. Explore the named scope; promote selected treatments through the real source and adoption gates. |

Inputs can mix these cases. Inspect representative surfaces across the agreed scope, not just the landing page: repeated grammar, distinctive artifacts, interaction states, and host constraints. Record missing source, runtime, or render access precisely. A screenshot can establish visible anatomy; it cannot establish hidden behavior or an import graph. Build an explicitly proposed reconstruction where useful, keeping unavailable evidence unverified.

Keep the inventory in the existing tracker. For each relevant unit or family, capture its category, current or candidate owner, consumers, independent claims, and concrete gap. Start with enough coverage to choose a useful slice; refine the map as new evidence appears. Every inventoried item in the pass eventually needs a disposition: verified as-is, changed and verified, intentionally retained/deferred, or removed within scope. Discovery of unrelated work does not silently widen the pass.

## Run the queue

The tracker is the agent's continuation state. Each actionable gap needs a unit/owner, reason to act, dependencies, next action, and observable finish. A compact entry is enough:

> Status Chip · source conflict · Card copies the Chip's paint · replace that copy with the existing Chip contract · finish when both consumers and the guide render the shared source in their real states.

Choose work in this order: the user's named priority, a failed required check or contradiction affecting the current slice, a dependency that unlocks blocked work, then another gap within scope. Classify from the real contract; do not march through empty categories or complete every token before examining a composition. Shared grammar discovered higher up returns to its appropriate owner before dependent work closes.

For each iteration:

1. **Read current claims.** Reconcile the tracker with live sources and existing evidence. A new session resumes the earliest unresolved claim; it does not replay completed exploration.
2. **Dispatch the next useful action.** Assign bounded work to inspect missing evidence, expose a visual choice, formalize a source, adopt it, or verify it. Match the action to the gap instead of rebuilding every unit through every phase. Use the dispatch contract below.
3. **Inspect and integrate the result.** Check the actual artifacts, diff, and evidence before updating claims, decisions, and dependent gaps. A worker's completion message alone does not close a claim. A rejected experiment is useful progress when it settles a question. Keep required failures open; deferral needs a reason consistent with the brief and authority.
4. **Continue or yield precisely.** Dispatch the next unblocked action without asking whether to continue. If a required taste/intent answer is pending, progress independent units. If nothing useful can proceed, hand off the concrete choice or access blocker and the exact resume action. Repeated attempts with no new evidence need a revised diagnosis, narrower experiment, or that handoff.

Ready for final-guide assembly means the scoped inventory is accounted for and required source, workbench/composition, and in-scope adoption checks are resolved. Guide assembly and its delivered-surface checks remain open until performed. Before declaring the pass complete, verify the delivered guide and any changed production surfaces; required acceptance gates must also be satisfied. Open taste approval may instead be reported as **ready for review**. Explicit retentions and accepted limitations can remain visible without forcing needless redesign. A later finding reopens its affected claim even if an earlier pass closed.

### Dispatch contract

Discover available worker routes using the environment's guidance; where available, `cockpit handbook` routes worker/access decisions. Choose a capable economical model and effort for the assignment, without hardcoding a provider into the project workflow. Give each worker a self-contained brief:

- **Purpose and finish:** the gap, why it matters, the required artifact, and the observable completion condition.
- **Current truth:** relevant source revision, accepted direction or proposed candidate, tracker excerpt, dependencies, and reference/evidence paths. Specify whether selection is still pending.
- **Ownership:** checkout, exact writable paths, shared sources to leave to their owner, preserved behavior, and permitted side effects. Exploration stays in candidate/workbench paths until selection; production scope is explicit.
- **Verification and return:** relevant checks, required rendered evidence, changed files or commits, unresolved findings, and next dependency. Follow the consuming repository's check commands and resource limits.

Keep assignments and evidence pointers in the existing tracker. Assign each shared source to one writer at a time; other workers propose needed changes to that owner. Use isolated candidate directories or worktrees where competing treatments would otherwise overwrite each other. A worker finishes its bounded assignment and returns; the orchestrator integrates shared registrations and updates the queue.

Inspect returned artifacts against the brief, including renders when visual claims matter. Resolve competing ownership before integrating, then verify the affected combined surface: individually passing workers can still conflict. A fresh review worker gets the brief, relevant sources, diff, and evidence; route concrete findings back to the responsible worker and recheck the correction. On worker failure, inspect partial changes before retrying or reassigning so the next worker does not duplicate or overwrite them.

### Turn review into the next action

Ask for judgments the user can actually make. A review surface should identify the unit and question, show the baseline and meaningful alternatives under comparable content, state, and host size, and state the intended gain and cost of each choice. Include the unchanged baseline as a valid outcome. A system workbench exposes its units and their relationships; compositions demonstrate them in context.

Record feedback at its actual scope: source identity, liked detail, rejected treatment, accepted definition, or delegated choice. Accepting a layout does not accept every child. Apply the decision at its owner, mark affected demonstrations and consumers for recheck, and select the next gap. If a lower-layer change alters a closed consumer's presentation, inspect that consumer before preserving its closure claim.

For deliberate reimagining, keep exploratory artifacts separate from production adoption. Promote the selected treatment into the authoritative source, update its real guide example, and check actual consumers. Carry defects found in that unit into the adoption brief; fix those covered by the task or project's defect policy, and make any remaining required decision explicit. Neither preserving the baseline nor choosing a new face settles a known behavior defect.

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
- **Current frontier:** active gap, ordered next actions and their finish conditions, dependencies, and any question awaiting the user.
- **Unit map:** the independent claims below, exact source/consumer paths, and evidence pointers.
- **Temporary-path map:** workbench, provisional sources/adapters, intended destinations, and exit conditions.
- **Latest verification:** scoped checks and visual evidence, gaps, and the next action.

If an existing direction document owns stable taste principles, link it instead of duplicating it. Resolve conflicts using the project's authority order and the user's current instruction. Put receipts in its existing history mechanism, including PR bodies when used; a frozen log stays frozen.

Keep these claims independent:

| Claim | Record | Does not establish |
| --- | --- | --- |
| Input identity | Which source/version the pass uses, and any user recognition of it | Recognizing the original does not accept a redesign |
| Definition | Proposed, chosen under delegated authority, user-accepted with a receipt, disputed, or not yet defined | A file or render does not establish user acceptance |
| Authoritative source | Exact owner/public seam, competing source if unresolved | A tidy component does not establish adoption |
| Real demonstration | Workbench and final-guide example paths/status separately; each imports the real source | A mock or copied renderer does not establish a real example |
| Production adoption | Named actual consumers; partial, complete, deferred, or not in scope | An importable library or greenfield demo does not establish production use |

For example, a Button can have a proposed definition, a working source, and a real workbench while its guide entry is pending and production adoption is out of scope. That is a valid intermediate state, not an accepted or fully delivered unit. Conversely, existing production use does not settle a disputed definition.

When the user explicitly delegates selection for this pass (for example, “show the options, then choose for me”), record **chosen under delegated authority** and the instruction that grants it. Permission to explore, build candidates, or act autonomously on system coherence does not waive the open-direction choice gate. Reserve **user-accepted** for an actual acceptance of the result; delegated selection and personal taste approval are different claims.

Update current truth after settled decisions, promotions, meaningful verification, and handoff. Replace resolved frontier questions rather than appending the conversation. A short acceptance receipt records what was accepted and its source; silence or an agent recommendation is not that receipt. Maintain named design constraints at the level needed to prevent their loss; keep implementation detail and historical receipts in sources, Git, or the project's receipt mechanism. Add a separate log only when chronology outgrows the tracker and no existing mechanism fits.

Avoid stale claims about ahead counts, dirty files, running servers, or other sessions; recompute them live. Mark recorded verification with its revision/date and refresh affected claims after changes. One unit closing does not accept its siblings or a whole composition.

## Delivery checks

Choose checks proportional to the changed surface and use the repo's actual commands. Record what was observed, not an aspirational checklist.

1. **Source and runtime lineage.** Apply `systematizing.md` to the changed dependency graph. Confirm real imports and the public seam, including underlying document/state signals for complex integrations. Search remaining legacy/provisional paths and identify any still-needed consumer. Check that adjacent controls, events, and product access survived migration.
2. **Executable verification.** Run relevant existing focused checks, type-check, and build where available. Add regression coverage when a changed contract or discovered bug warrants it; do not write tests merely to restate token values. Separate unrelated baseline failures from introduced failures.
3. **Rendered evidence.** Inspect the real composition and final guide, not only isolated components. Include representative narrow and wide hosts plus consequential variants/states: long or empty content, loading/errors, overflow, and coupled density where applicable. Motion needs observation over time; a still cannot prove a transition. Inspect the guide's own layout as well as its component hosts; a narrow example inside an overflowing gallery does not establish a responsive guide. Run the creative-floor review on these rendered surfaces.
4. **Interaction and accessibility.** For changed interactive surfaces, exercise native pointer and keyboard behavior, accessible names, focus visibility and reachability, disabled states, and relevant contrast. Check Reduced Motion for moving components and forced colors when custom paint affects visibility. In migrations, compare against existing behavior; a visually correct result that removes input or control access is incomplete.
5. **Isolation and cleanup.** Confirm production does not depend on workbench fixtures, gallery typography, comparison state, or prototype copy. Guide examples drive the authoritative source with realistic controlled inputs; they do not invent a second clock, document, or behavior path. Inspect scoped temporary removal and remaining tracker pointers.

Save useful screenshots or measurements using the repo's evidence convention and link them from the tracker. If capture fails, try an available supported alternative; label DOM, computed-style, interaction, or screenshot evidence accurately. A build, HTTP 200, or DOM check does not substitute for rendered inspection. If a required check cannot be completed, report the limit and keep that claim unverified instead of declaring the whole pass successful.

After a correction, rerun affected checks and update their evidence. A fresh read-only lineage review is useful for substantial migration or complex state integration; it should check ownership, behavior preservation, production/guide seams, and hidden adapters, not merely count tokens.

## Provenance

Adapted from Burooj's EmotiTone visual-migration work in August–September 2026 and the repo-owned `emotitone-design-system/SKILL.md`. Specific evidence in `emotitone-solfrege` includes `12c594b` (independent unit claims), `1c2267c` (tracker/log consolidation), `5da92b2` (one public Knob source), `4b3e49a` (CodeStrip's real editor ownership), `6867a42` (preserving displaced controls and selection), and `5516c05` (shared instrument-bar tokens). These are provenance, not runtime dependencies or authority for another project's taste. The temporary-workbench/final-guide separation follows Burooj's September 11 correction; EmotiTone's workbenches historically lived inside its guide.

The repeat-and-reopen workflow also draws on EmotiTone's September–October reimagining pass, inspected at `f152605498a7ce57c63bf42114fd56194b4f520d`: selected Button adoption `a9c0a938`, lab-defect carryover `78c0c4c6`, and the Plan's independent lab/adoption stages. Its strict layer order, mandatory picks, deployment setup, and visual doctrine remain project-specific.

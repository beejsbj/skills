---
name: emotitone-design-system
description: Guide the temporary EmotiTone production visual-design pass on implementing-design-system. Use for EmotiTone style-guide review, visual grilling, design-unit definition, token or component promotion, production adoption, visual verification, or final lineage audit; do not use for standalone functionality or bug-fix work.
---

# EmotiTone Design System

Finish the current visual pass one unit at a time. The design already exists in substantial form; tighten it, recover liked ideas, resolve drift, and promote it into a coherent production system. Do not redesign the product from zero.

This skill is temporary. Retire it after the tracker records the visual pass and final lineage audit as complete.

## Start from current truth

Resolve the repository root and verify that the work belongs to `emotitone-solfrege` on `implementing-design-system`. Read these files completely:

1. `src/style-guide/DESIGN_SYSTEM_TRACKER.md` — current design truth, active unit, dependencies, and next gate.
2. `src/style-guide/DESIGN_LOG.md` — only when the current unit needs its acceptance or implementation receipt.

Then inspect live Git state. Treat ahead counts, dirty files, worktrees, tests, and running sessions as current facts to recompute, never facts to copy from a document.

Use this truth order when sources disagree:

1. Burooj's current explicit instruction.
2. The tracker’s mission, checkpoint, unit row, and active frontier.
3. Current production code and observed live behavior.
4. The design log for chronological evidence.
5. Linear `BJS-35` for workflow state and receipts.
6. Git history for archaeology.

Raise a material contradiction instead of quietly choosing a convenient source. The external `emotitone-design-system` repository, style-guide specimens, screenshots, and old preview HTML are reference evidence, not acceptance authority.

## Hold one unit

One session owns one design unit. It starts at that unit's earliest unresolved mode—**Define**, **Formalize and adopt**, or **Verify and hand off**—and may continue through later modes in the same session once their gates are genuinely met. Derive the unit from the tracker unless Burooj names it.

If Burooj names a unit later than the tracker’s active frontier, proceed with that unit unless an unresolved dependency would change its visual definition. Name the dependency and risk in the unit brief; do not block on it by default.

If the tracker names a coupled unit, inventory each artifact separately: current source, current specimen, current production host, and any missing surface. Declare the temporary session boundary before asking taste questions.

Before acting, state a compact unit brief:

- current definition, source, specimen, and production-adoption status;
- production authority and consumers;
- reference surfaces worth comparing;
- unresolved visual deltas that genuinely require taste;
- behavior and unrelated-file preservation boundary;
- observable completion condition.

Adjacent unit sessions may run concurrently when their files and lineage do not overlap. A session that discovers a shared lower-layer dependency must announce it immediately. Serialize that promotion or coordinate ownership before either dependent unit closes.

## The lineage gate

The system is:

```text
tokens -> primitives -> compounds + uniques -> compositions
```

Compositions are production surfaces. Every reusable visual rule has one lowest appropriate owner and is consumed upward from there.

For every changed visual rule, answer:

- Who owns it?
- Is it duplicated above or beside that owner?
- Does a real production consumer use it?

If a compound, unique, or composition invents reusable visual grammar, promote that grammar into a token or primitive, define it, and make the higher unit consume it before closure. If a lower-level abstraction has no real reuse or consumer, keep the rule local instead of manufacturing taxonomy. Style-guide staging, captions, tiles, controls, and hard-coded demo states remain specimen-local.

Lineage is a completion criterion, not optional cleanup.

## Define

Assume most design intent is already present. Compare three surfaces before questioning Burooj:

- current production anatomy, density, motion, interaction, and consumer contracts;
- the current style-guide specimen;
- relevant external reference material or earlier accepted visual evidence.

Autonomously reconcile obvious omissions, source drift, taxonomy, and preservation constraints in the proposed definition. Ask only where two plausible visual outcomes remain and Burooj's taste changes the result.

Let the unresolved visual decision determine the conversation length. A unit may need one question or sustained visual back-and-forth; every question must earn its place by changing a plausible outcome. Keep each batch coherent and easy to answer. If questioning starts rediscovering settled design, treating functionality as visual definition, or mistaking gallery scaffolding for component anatomy, stop and reset the scope.

Keep questions visual and concrete. Show or compare the actual surfaces whenever possible. Record liked ideas as first-class constraints rather than smoothing them into generic consistency.

In the first response, name the exact surfaces to compare—component files and routes when known. If an expected surface does not exist, say so and treat the absence as a scoping fact, not an invitation to redesign from zero.

Update the tracker after each settled batch: replace resolved frontier questions with current truth and expose only the next unresolved visual frontier. Do not turn the tracker into a transcript. An agent recommendation becomes definition truth only after Burooj explicitly accepts the shared-understanding summary.

No component implementation begins before that acceptance.

When Burooj asks for definition through production adoption in one request, begin at the earliest unresolved mode and queue later modes behind their gates. Continue within the same unit session after acceptance; do not prematurely implement or end the session merely because the mode changed.

## Formalize and adopt

Require an acceptance receipt. Characterize current production behavior before changing presentation.

The authoritative source component should also be the component production uses. The style guide imports and drives that same source through inert or controlled inputs. Do not create parallel `ProductionX` and design-system implementations. A thin provisional adapter is allowed only when an undefined downstream unit makes it necessary; name it in the tracker and preserve the downstream definition as unaccepted.

Change only the accepted visual treatment and the ownership needed for lineage. Preserve interaction, audio, routing, state, persistence, APIs, accessibility behavior, haptics, and motion unless the accepted visual definition specifically governs state presentation or Burooj separately authorizes functionality work.

When functional defects or ideas appear:

- reproduce or describe them accurately;
- park them outside this visual slice with a durable pointer;
- continue the visual unit without making them acceptance conditions.

Specimens must use real source components, realistic values, and real states. Gallery markup cannot become production anatomy by accident.

Commit coherent checkpoints: accepted definition, source/production implementation, specimen integration, and receipt may be separate commits when that keeps each claim reversible and reviewable.

## Verify and hand off

Verify both production at `/` and the guide at `/style-guide/`. Use a matrix proportional to the unit: relevant responsive widths, variants, states, themes, Reduced Motion, forced colors, motion, or live interaction. Do not manufacture exhaustive matrices that add no confidence.

Run focused touched tests first, then type-check and build. Report repository-wide failures as a separate baseline when they are unrelated. Never claim pixel or screenshot verification when capture failed; name DOM, computed-style, motion-state, or live-interaction evidence exactly.

Before closure, run a fresh read-only lineage audit—normally with a bounded subagent—against the diff and unit brief. It checks:

- every new token or primitive has a real consumer;
- higher layers compose lower sources instead of copying CSS or markup;
- production and the style guide cross the same public component seam;
- no specimen scaffold or demo state leaked into production;
- no behavior changed without separate authorization and evidence;
- no provisional adapter or duplicated recipe is hidden.

Fix audit findings in a separate atomic slice, then update the tracker’s four claims independently: **defined**, **authoritative source**, **real specimen**, and **production adoption**. Append a concise design-log receipt. If Cockpit/Linear is active for the session, leave the corresponding `BJS-35` receipt without changing lifecycle state beyond the evidence.

End with exact branch, commits, pushed status, checks, visual evidence, residual risk, and next unit. Do not push unless Burooj explicitly authorizes it.

## Boundaries

- Do not invoke `design-lab` for this pass; its old workflow is historical input, not current doctrine.
- Do not reopen accepted units unless current evidence reveals a concrete contradiction or Burooj asks.
- Do not mix visual migration with functionality, bug fixes, broad accessibility redesign, audio, routing, or state architecture.
- Use at most one bounded scout before definition and one bounded lineage auditor after implementation. Orchestration must shorten the loop, not become the work.
- Respect the dirty tree and adjacent sessions. Stage only owned files.

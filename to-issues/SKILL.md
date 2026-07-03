---
name: to-issues
description: Break a plan, spec, or grilling outcome into independently-grabbable tracer-bullet Linear issues with goal-grade briefs.
disable-model-invocation: true
---

# To Issues

Break a plan, spec, or grilling outcome into independently-grabbable Linear issues using vertical slices (tracer bullets).

Read the `linear` skill first — issue body shape, lanes, and the write path come from it.

## Process

### 1. Gather the source

Work from what is already in the conversation. If given an issue reference, fetch it with `./cockpit.py issue BJS-X` (run from `/Users/burooj/Projects/cockpit`) and read the body and comments.

### 2. Ground in the codebase

Ground the slices in the code they touch: use the project's domain vocabulary, respect its ADRs, and hunt for prefactoring — "make the change easy, then make the easy change."

### 3. Draft vertical slices

Each issue is a **tracer bullet**: a thin but COMPLETE path through every layer end-to-end (schema, API, UI, tests) — never a horizontal slice of one layer.

- A completed slice is demoable or verifiable on its own.
- Prefactoring slices come first.
- Slice until a small model can execute it: the intelligence goes into the brief, not the worker — "the plan is the product" (shadcn/improve).

### 4. Quiz the user

Present the breakdown as a numbered list — per slice: title, blocked-by (sibling slices), user stories covered (if the source has them). Ask: is the granularity right? are the dependencies right? should anything merge or split? Iterate until the user approves.

### 5. Write goal-grade briefs

Each body uses the linear skill's shape — `## Goal / ## Context / ## Done when / ## Constraints`:

- **Goal** — the end-to-end behavior of the slice, not layer-by-layer implementation.
- **Context** — source (parent issue, plan, or grilling session), repo and entry points, prior decisions. Don't prescribe per-file edits; they go stale. Exception: a prototype snippet that encodes a decision more precisely than prose can (state machine, schema, type shape) — inline the decision-rich part and note its origin.
- **Done when** — **goal-grade**: one measurable end state, a stated check (the command to run or the artifact that proves it), and the constraints that must hold. Self-contained, so a worker can adopt it verbatim as its `/goal` condition (Claude Code and Codex both take `/goal` as a completion contract). Shape:

  ```markdown
  ## Done when

  - Exported CSV re-imports losslessly (one end state).
  - Check: `npm test -- csv-roundtrip` passes.
  - Holding: no schema changes outside `export/`.
  ```

- **Constraints** — boundaries and non-goals; at minimum, what neighbouring slices own, so the worker doesn't creep into them, plus the stop rule: when reality doesn't match the brief, stop and comment rather than improvise.
- **Executor class** — one line naming the smallest model class that can run the brief (roster: `profiles.json` in the cockpit skill). If only a frontier model could execute it, the slice is too big or the brief too thin — split or thicken until gpt-5.5/sonnet/glm class suffices.

A brief is complete when a cold worker could start from the body alone.

### 6. Create, route, receipt

`cockpit.py` has **no issue-create verb**. Draft every body in full, then create the issues with whatever Linear tooling the harness has — Linear MCP or the Linear app. Do not invent a cockpit create command.

- Create in dependency order (blockers first) and record inter-slice ordering as Linear blocked-by relations, not body text.
- Lane: complete brief → `Ready for agent`; anything less → `Inbox`. Set it at creation, or with `./cockpit.py move BJS-X "Ready for agent"`.
- Receipt, via `./cockpit.py comment` (run from `/Users/burooj/Projects/cockpit`): if the source was an issue, comment on it listing every created identifier; otherwise leave a one-line origin receipt on each new issue. Receipts land as replies under the issue's Cockpit Thread — see the `linear` skill.
- Do not move or close the source issue — that is a triage decision, not this skill's.

Done when every approved slice exists in Linear, sits in its lane with its relations, and the receipt is posted.

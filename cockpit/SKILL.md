---
name: cockpit
description: "Use when coordinating Burooj's cockpit — the manager-coworker layer over Linear: triaging the board, preparing native worker launches, binding Codex/Claude/opencode/Cursor sessions to Linear issues through session:* labels, handling issue comments, auditing local sessions, or updating cockpit's Linear-first orchestration rules."
---

# Cockpit

## 0. Governing principle: wu-wei / ergonomic discipline

Cockpit's rules are **river banks, not cages**. They shape where attention flows so the right move is the *easy* move — they do not constrain the agent against the grain.

**Under-discipline beats over-discipline.** Over-constrained agents fail because they are trying to comply. When in doubt, slim. Trust the agent; give it banks, not a script.

When Burooj expands into broad ambition, comparison, tooling, or despair, preserve the seed object and recenter on the nearest real completion: the smallest artifact, missing decision, and next reversible move.

---

## 1. Interaction model

```
You  <->  Cockpit (manager-coworker / Linear truth layer)  <->  Native orchestration  <->  Workers
```

- **You** talk to **cockpit**, not to worker sessions — live (a cockpit session) or async (Linear comments from phone/web).
- **Cockpit** is the manager-coworker and Linear/session truth layer: it triages with you, prepares launch context, binds worker sessions, leaves receipts, handles comments, and audits drift.
- **Native orchestration** is the active surface's own session/thread machinery: Codex Desktop thread creation, provider CLIs, Matt Pocock's orchestration layer, or native subagents.
- **Workers** are provider sessions (Codex/Claude/opencode/Cursor) or native subagents launched through the active orchestration surface. They do the actual project work in the project's own repo.

`cockpit.py` is an actuator and ledger: inspect, prepare, comment, question, bind, release, move, audit. It is not the orchestration brain and should not hide provider-specific lifecycle logic that the active environment can perform natively.

### Layers

Every cockpit concern lives in exactly one layer; when unsure where something belongs, name its layer first.

| Layer | Lives in |
|---|---|
| Truth | Linear board — `linear` skill |
| Actuator + ledger | `cockpit.py` — this skill |
| Session plane | acpx (ACP control plane) + native provider tools; the `acpx` skill's `profiles.json` picks the model; `sessions` discovery feeds this ledger |
| Workflow discipline | `triage`, `grill-me`/`grill-with-docs`, `to-issues`, `implement`, `tdd`, `two-axis-review`, `diagnosing-bugs`, `prototype` |
| Intelligence | the scout pass (§5) |
| Operator | Burooj live/async; scheduled scout sessions; Hermes/OpenClaw candidate, gated on the scout pass being doctrine |

---

## 2. Depends on

Cockpit depends on the `linear` skill for board ontology, lane meanings, label taxonomy, issue body shape, and the comment model. Do not restate those rules here; reference that skill.

---

## 3. Status lanes (9 + Canceled)

Lane names, meanings, and invariants live in the `linear` skill's lane table — read it there; this file does not carry a second copy (it drifted once already). Cockpit's own layer on top is *who acts next* and *how work moves*: the shaping pipeline, routing decisions, and artifact-gated lifecycle below.

### Shaping pipeline

```
Inbox → [Grilling?] → [Needs-info?] → Ready for agent / Ready for Burooj
                                    ↘ Blocked (real external block)
```

- Meaty issue: grill out the approach, then gather the context that approach needs, then ready.
- Simple issue: skip grilling; maybe skip Needs-info; go straight to Ready.
- `Grilling` and `Needs-info` are distinct lanes because they split by *who acts* (you interactively vs an agent/quick-fact) and by *depth* (approach vs context).

### Routing decisions

- Say "this needs triage" when an `Inbox` issue/comment has not been classified into a next actor or lane.
- Say "this needs grilling" when the core approach is still unclear and interactive shaping with Burooj is the real next move.
- Use `Needs-info` only for bounded context gathering: name the missing question, likely source, next actor, and stop condition. It is not a vague uncertainty bucket.
- Use `Ready for Burooj` when Burooj must decide, approve, judge taste/priority, supply private context, or take physical/account action.
- Use `Ready for agent` when a fresh worker can start from the issue body or latest authoritative Agent Brief.

**Gate:** moving to `Ready for Burooj` without a current `For Burooj` brief (§4) is not ready — same bar as landing in `Ready for agent` without a goal-grade Done-when. `move` warns loudly (not a hard fail) when the thread is missing or stale; treat that warning as a to-do, not noise.

**Research routing rule:** research/brainstorm output routes to whoever acts next, not into the issue body wholesale. Ends in a Burooj decision → it becomes the `For Burooj` brief (§4). Feeds an agent's next step → distilled into the body's Context section. Long-form → a linked Linear document, with the brief/Context holding only the pointer and the settled takeaway.

### Artifact-gated lifecycle

Linear state must not be more confident than the artifacts.

- Move to `In Progress` only when a worker/session is actually bound and executing.
- Move implementation work to `In Review` only when the review artifact exists. For git worktree implementation, the normal artifact is a pushed branch plus draft/ready PR.
- Move to `Done` only after the review artifact is merged/accepted, or Burooj explicitly says to close without review.
- Local commits, launch success, or a worker saying "done" are not enough for `Done`.
- Do not archive/release the worker session until the PR/review artifact exists and the Linear issue has a receipt naming it.
- Worker final receipts should include: branch, commit, pushed yes/no, PR/review artifact URL, checks run, residual risks, and recommended next state.
- `workflow:*` labels are removed (see the `linear` skill); lifecycle meaning lives in the lane alone.

---

## 4. Comments (cockpit's async channel)

Five roles:

1. **Your async channel to cockpit.** From phone/web you drop notes: clarity, "split this," "move it," "this is done," instructions. `inbox` surfaces your unresolved comments as the work queue; cockpit handles each (often by spawning a per-issue native subagent).
2. **Cockpit Thread (one per issue).** A single top-level comment; all receipts / audit / log trails are replies under it. `comment`, `bind`, `release`, and `move` create or reuse it automatically. Cockpit resolves this thread after posting a receipt, so it stays collapsed; a Burooj reply after resolution still counts as new/unresolved and surfaces in `inbox`.
3. **Questions thread (one per issue).** Questions *for you* live as a dedicated top-level comment thread with each question as a reply — NOT checkboxes in the issue body. Cockpit creates/reuses this thread when adding a question. Never auto-resolved by receipt-posting.
4. **For Burooj thread (one per issue).** The decision brief that gates `Ready for Burooj` (§3): the exact decision/question, minimum facts, options with a recommendation, and a one-line pointer to the Cockpit Thread's receipt trail. `comment --brief` creates/reuses this top-level thread titled `For Burooj`. You read only this comment and reply there. Never auto-resolved by receipt-posting.
5. **Grilling thread (one per issue).** Interactive shaping dialogue with Burooj — multi-turn, can span sessions; the thread is the working-out. `comment --grilling` creates/reuses this top-level thread titled `Grilling`. When grilling converges, conclusions graduate into the issue body and the thread resolves. Never auto-resolved by receipt-posting.

Resolution semantics: resolving a thread asserts the issue body no longer needs it — content graduated into the body, or the thread became moot. Unresolved threads are live context: `prepare` (§7) builds launch briefs from the body plus unresolved comments, so a cold worker sees exactly which threads still matter. The Cockpit Thread is auto-resolved by cockpit and therefore never load-bearing for a cold start. Questions, For Burooj, and Grilling resolve only when a reply says what closed them — for Grilling, that means its conclusions have graduated into the body.

---

## 5. First move — the scout pass

```bash
cd /Users/burooj/Projects/cockpit
./cockpit.py status
./cockpit.py audit
./cockpit.py sessions
./cockpit.py linear-doctor
```

Use `./cockpit.py issue BJS-X` before steering or launching work for an issue.

Check `./cockpit.py inbox` to see both issues needing a triage decision and your unresolved comments as a combined work queue.

Then reconcile — `audit` catches label mechanics, but lanes must not be more confident than reality:

- Every `In Progress` binding: does the bound session still exist and is it live? Archived Codex sessions live in `~/.codex/archived_sessions/`, which `sessions` does not scan — check there before trusting a binding. Is there branch/PR evidence of motion?
- `In Review`: does the named review artifact actually exist?
- Sample the oldest `Inbox` and `Ready for Burooj` issues: still real? Has evolution already satisfied a Done-when (tooling built since, work landed elsewhere)? Propose closure with evidence.
- Every unresolved Burooj comment: handle or route it, then resolve with a reply.

Receipt every drift you find — a finding left only in your report is a failed pass; it must land on the board via `comment`. Then apply the correction the evidence supports: release a stale/false binding; move a lane the evidence unambiguously contradicts (completed archived research → `Ready for Burooj`; `In Progress` without a live session → `Ready for agent`, or `Blocked` with the blocker named). Where a move needs Burooj's judgment, state the proposal in the receipt and leave the lane. Batch the decisions he owes into one crisp question each — streamline his queue, don't just inventory it.

A scheduled scout session (codex automation) runs this same pass and ends with a short digest. Receipts and mechanical binding corrections are not lifecycle writes — they are required; the Stop Gates (Done moves, launching/archiving sessions, editing repos) still bind.

---

## 6. Commands

```bash
# Board
./cockpit.py status
./cockpit.py board
./cockpit.py issue BJS-X
./cockpit.py issue BJS-X --show-cockpit   # include cockpit-authored comments/receipts

# Triage / inbox
./cockpit.py inbox

# Prepare / native orchestration / binding
./cockpit.py prepare BJS-X
./cockpit.py bind BJS-X codex <session-id>
./cockpit.py bind BJS-X session:claude:<session-id>
./cockpit.py release BJS-X
./cockpit.py label BJS-X --add executor:standard --remove type:seed   # non-session labels only
./cockpit.py move BJS-X "In Review"
./cockpit.py move BJS-X Done
./cockpit.py project-move chat-scrobbler Completed

# Comments
./cockpit.py comment BJS-X "text"
./cockpit.py comment BJS-X --question "Question for Burooj (goes to the Questions thread)"
./cockpit.py comment BJS-X --brief "Decision brief (goes to the For Burooj thread)"
./cockpit.py comment BJS-X --grilling "Shaping note (goes to the Grilling thread)"
./cockpit.py comment BJS-X --reply-to <comment-id> "text"
./cockpit.py comment-resolve <comment-id>
./cockpit.py comment-unresolve <comment-id>

# Audit
./cockpit.py audit
./cockpit.py sessions
./cockpit.py linear-doctor
```

Removed verbs (do not use): `dispatch`, `dispatch-prepare`, `done`, `issue-doctor`, `dispatch-prompt`, `inbox-review`, `comments-review`.

---

## 7. Prepare and native orchestration

Cockpit prepares deterministic launch context; the active environment orchestrates.

`./cockpit.py prepare BJS-X` should:

1. Resolve the Linear issue, project, project root, and repo.
2. Ensure only boring prerequisites when safe, such as root project registration needed by native thread creation.
3. Print/return an agent-ready launch brief from the issue body and unresolved comments.
4. Include branch/worktree metadata and preflight any branch collision that would make native worktree creation ambiguous.
5. Leave session creation, provider launch, worktree-thread creation, and lifecycle decisions to native orchestration.

The launch brief should tell the worker to adopt the issue's Done-when as its native goal condition (`/goal` in both Claude Code and Codex), so completion is judged by the issue's own condition rather than the worker's judgment. A `Ready for agent` issue whose Done-when cannot serve as a goal condition is not actually ready — route it back through shaping.

Route on the issue's `site:*` label before picking a launch surface: `site:cloud` may go to a native agent cloud when one provider is sufficient, or to Fly.io Sprites when the work needs a provider-neutral, persistent Linux sandbox or should be isolated from bjslab's live services; `site:bjslab` launches headless on bjslab; `site:macbook` launches locally on the Mac; `site:multi` needs a plan naming both devices. The machine invoking `sprite` is only the control surface — installing the CLI on bjslab does not make Sprite-hosted work `site:bjslab`. An issue entering `Ready for agent` without a `site:*` label gets one during preparation using the criteria in the `linear` skill. See [references/execution-sites.md](references/execution-sites.md) for the target-selection and Sprites launch contract.

Launch on the issue's `executor:*` class, defaulting to the smallest sufficient model from the `acpx` skill's `profiles.json` (which holds the launch recipes). This is the payoff of the readiness bar, not a separate planning step: a smart model already distilled the issue into a `/goal` at preparation time, so a cheaper model can now execute it cold. After launch, `bind` the session; when the worker reports done, review the diff against the issue before `In Review` (`two-axis-review` for repo diffs) — the worker's "done" is a claim, the review is the evidence — then leave the receipt.

For Codex Desktop implementation work in a git repo:

- Use the **root saved project id** with native `create_thread`.
- Use `target.environment.type = "worktree"`; do not use a local/root environment for implementation work.
- Prefer `startingState: { "type": "working-tree" }` and treat the issue branch as branch intent for the worker to create/switch to inside the new worktree.
- Do not pass an existing issue branch as the native starting state unless `prepare` shows that branch is not checked out in another worktree.
- After creation, verify the worker cwd is the native worktree path, not `/Users/burooj/Projects/<repo>`.
- Do not register each issue worktree as its own saved Codex project.

For headless workers, `bunx --bun acpx <agent> …` in the project dir (see the `acpx` skill) is a sanctioned launch surface — ACP-launched sessions land in the native provider store, so binding works unchanged.

After native orchestration creates a worker, bind it with `./cockpit.py bind BJS-X session:provider:<id>` and move to `In Progress`.

For `Needs-info` work: cockpit spawns a **native subagent** (harness Task), read-only, writing findings back as an issue comment. No separate verb.

---

## 8. Stop Gates

Stop and ask Burooj before:

- Deletion or provider-side purge.
- Secrets / private keys / account / security actions.
- Money or email-send actions.
- Canonical source-of-truth decisions.
- Pushing, rewriting history, or broad workflow changes.

---

## 9. Related skills and references

- `linear` skill — board ontology, lane semantics, labels, issue body shape, comment model. Read it before creating or editing issues.
- `acpx` skill — mechanics for reaching other models/providers over ACP (sessions, exec, permissions, flows), the launch recipes, plus the model-taste roster (`profiles.json`); native provider CLIs are the fallback pipe. Policy stays here: premium tokens for judgment, cheap classes for execution, briefs written so the smallest sufficient model can execute.
- `triage` skill — use for inbox sorting, issue clarification, duplicate/out-of-scope checks, and agent-ready briefs. Its "Cockpit lane translation" section is the single source for mapping its generic lane names onto cockpit lanes.
- `grill-me` skill — use when the issue needs interactive design/plan stress-testing with Burooj. Route the issue to `Grilling`; ask one question at a time; inspect code instead of asking when the answer is discoverable.
- `grill-with-docs` skill — use for `Grilling` when the project has domain docs, `CONTEXT.md`, `CONTEXT-MAP.md`, or ADRs and the session should sharpen language against those docs. It may update project docs during the grilling session when explicitly in execution scope.
- `to-issues` skill — use to break a grilled plan/spec into vertical-slice issues with goal-grade Done-whens, feeding `Ready for agent`.
- `implement` skill — the worker discipline for issue-bound implementation sessions: goal adoption, tdd, review, artifact gate, final receipt.
- `two-axis-review` skill — standards + spec review of a diff against its originating issue; the normal review shape before `In Review`.
- `tdd`, `diagnosing-bugs`, `prototype` skills — execution-support disciplines workers reach for during implementation, debugging, and design questions.
- [references/linear-discipline.md](references/linear-discipline.md) — cockpit's write-auth config and session-binding mechanics (verbatim app-actor rules).
- [references/session-discipline.md](references/session-discipline.md) — native orchestration boundary, session lifecycle, review, and cleanup.
- [references/execution-sites.md](references/execution-sites.md) — concrete launch targets behind `site:*`, including native clouds, Sprites, bjslab, and MacBook.

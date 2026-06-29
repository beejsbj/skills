---
name: cockpit
description: Use when coordinating Burooj's cockpit — the manager-coworker layer over Linear: triaging the board, preparing native worker launches, binding Codex/Claude/opencode/Cursor sessions to Linear issues through session:* labels, handling issue comments, auditing local sessions, or updating cockpit's Linear-first orchestration rules.
---

# Cockpit

## 0. Governing principle: wu-wei / ergonomic discipline

Cockpit's rules are **river banks, not cages**. They shape where attention flows so the right move is the *easy* move — they do not constrain the agent against the grain.

**Under-discipline beats over-discipline.** Over-constrained agents fail because they are trying to comply. When in doubt, slim. Trust the agent; give it banks, not a script.

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

---

## 2. Depends on

Cockpit depends on the `linear` skill for board ontology, lane meanings, label taxonomy, issue body shape, and the comment model. Do not restate those rules here; reference that skill.

---

## 3. Status lanes (9 + Canceled)

| Lane | Meaning | Who acts next |
|---|---|---|
| `Inbox` | Intake. Everything new or unclarified. | Cockpit + you (triage) |
| `Needs-info` | Context gathering. Bounded; does not linger. An agent digs or you supply a fact. | Agent or you |
| `Grilling` | Deep shaping — clarify intent, sketch approach. Interactive, can linger. Session-ownable. | You + a grilling session |
| `Ready for Burooj` | You are the next actor: a decision / approval / judgment / physical action. | You |
| `Ready for agent` | Cold-launchable. A worker can start from the issue body. | Cockpit prepares, native orchestration launches |
| `Blocked` | Waiting on a real external dependency. NOT "needs investigation" — that is `Needs-info`. | Blocker resolves |
| `In Progress` | A worker session is bound and executing. Exactly one `session:*` label. Local commits are not completion evidence. | Worker |
| `In Review` | A review artifact exists: normally a draft/ready PR for git implementation work, or another explicit review artifact named in the issue. | You / reviewer |
| `Done` | Accepted closure: PR/review artifact merged or accepted, or Burooj explicitly accepts closure without review. No `session:*` label. Final receipt left. | — |
| `Canceled` | Dead idea (Linear-native). | — |

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

### Artifact-gated lifecycle

Linear state must not be more confident than the artifacts.

- Move to `In Progress` only when a worker/session is actually bound and executing.
- Move implementation work to `In Review` only when the review artifact exists. For git worktree implementation, the normal artifact is a pushed branch plus draft/ready PR.
- Move to `Done` only after the review artifact is merged/accepted, or Burooj explicitly says to close without review.
- Local commits, launch success, or a worker saying "done" are not enough for `Done`.
- Do not archive/release the worker session until the PR/review artifact exists and the Linear issue has a receipt naming it.
- Worker final receipts should include: branch, commit, pushed yes/no, PR/review artifact URL, checks run, residual risks, and recommended next state.
- Do not rely on opaque `workflow:*` labels for user-facing lifecycle meaning.

---

## 4. Comments (cockpit's async channel)

Three roles:

1. **Your async channel to cockpit.** From phone/web you drop notes: clarity, "split this," "move it," "this is done," instructions. `inbox` surfaces your unresolved comments as the work queue; cockpit handles each (often by spawning a per-issue native subagent).
2. **Cockpit Thread (one per issue).** A single top-level comment; all receipts / audit / log trails are replies under it. `comment`, `bind`, `release`, and `move` create or reuse it automatically.
3. **Questions thread (one per issue).** Questions *for you* live as a dedicated top-level comment thread with each question as a reply — NOT checkboxes in the issue body. Cockpit creates/reuses this thread when adding a question.

Resolution rule: reply before resolving; resolve only when the reply says what closed it.

---

## 5. First move

```bash
cd /Users/burooj/Projects/cockpit
./cockpit.py status
./cockpit.py audit
./cockpit.py sessions
./cockpit.py linear-doctor
```

Use `./cockpit.py issue BJS-X` before steering or launching work for an issue.

Check `./cockpit.py inbox` to see both issues needing a triage decision and your unresolved comments as a combined work queue.

---

## 6. Commands

```bash
# Board
./cockpit.py status
./cockpit.py board
./cockpit.py issue BJS-X

# Triage / inbox
./cockpit.py inbox

# Prepare / native orchestration / binding
./cockpit.py prepare BJS-X
./cockpit.py bind BJS-X codex <session-id>
./cockpit.py bind BJS-X session:claude:<session-id>
./cockpit.py release BJS-X
./cockpit.py move BJS-X "In Review"
./cockpit.py move BJS-X Done

# Comments
./cockpit.py comment BJS-X "text"
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
4. Include branch/worktree metadata when useful.
5. Leave session creation, provider launch, worktree-thread creation, and lifecycle decisions to native orchestration.

For Codex Desktop, prefer the root saved project plus native `create_thread` with a worktree environment. Do not register each issue worktree as its own saved Codex project.

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
- `agents` skill — start, resume, fork, inspect, message, attach to, or archive provider sessions. Cockpit drives sessions through `agents`.
- `triage` skill — use for inbox sorting, issue clarification, duplicate/out-of-scope checks, and agent-ready briefs. Translate its older lane names into cockpit lanes: `Needs triage` -> `Inbox`, `Needs Burooj` -> `Ready for Burooj`, `Parked` -> usually `Ready for Burooj` or `Canceled` unless cockpit later adds a parked lane. Cockpit's `Needs-info` is allowed only as a bounded fact-gathering lane with an owner and stop condition.
- `grill-me` skill — use when the issue needs interactive design/plan stress-testing with Burooj. Route the issue to `Grilling`; ask one question at a time; inspect code instead of asking when the answer is discoverable.
- `grill-with-docs` skill — use for `Grilling` when the project has domain docs, `CONTEXT.md`, `CONTEXT-MAP.md`, or ADRs and the session should sharpen language against those docs. It may update project docs during the grilling session when explicitly in execution scope.
- [references/linear-discipline.md](references/linear-discipline.md) — cockpit's write-auth config and session-binding mechanics (verbatim app-actor rules).
- [references/session-discipline.md](references/session-discipline.md) — native orchestration boundary, session lifecycle, review, and cleanup.

---
name: cockpit
description: Use when coordinating Burooj's cockpit — the manager-coworker layer over Linear: triaging the board, dispatching and binding Codex/Claude/opencode/Cursor sessions to Linear issues through session:* labels, handling issue comments, auditing local sessions, or updating cockpit's Linear-first orchestration rules.
---

# Cockpit

## 0. Governing principle: wu-wei / ergonomic discipline

Cockpit's rules are **river banks, not cages**. They shape where attention flows so the right move is the *easy* move — they do not constrain the agent against the grain.

**Under-discipline beats over-discipline.** Over-constrained agents fail because they are trying to comply. When in doubt, slim. Trust the agent; give it banks, not a script.

---

## 1. Interaction model

```
You  ⇄  Cockpit (manager-coworker)  ⇄  Workers
```

- **You** talk to **cockpit**, not to worker sessions — live (a cockpit session) or async (Linear comments from phone/web).
- **Cockpit** is the manager-coworker in the Linear space: it triages with you, dispatches and binds workers, handles your comments, keeps the board honest.
- **Workers** are dispatched provider sessions (Codex/Claude/opencode/Cursor) or native subagents. They do the actual project work in the project's own repo.

Cockpit rarely makes you talk to a worker directly. You delegate to cockpit; cockpit delegates to workers.

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
| `Ready for agent` | Cold-dispatchable. A worker can start from the issue body. | Cockpit dispatches |
| `Blocked` | Waiting on a real external dependency. NOT "needs investigation" — that is `Needs-info`. | Blocker resolves |
| `In Progress` | A worker session is executing it. Exactly one `session:*` label. | Worker |
| `In Review` | PR / checks / review phase. | You / reviewer |
| `Done` | Complete. No `session:*` label. Final receipt left. | — |
| `Canceled` | Dead idea (Linear-native). | — |

### Shaping pipeline

```
Inbox → [Grilling?] → [Needs-info?] → Ready for agent / Ready for Burooj
                                    ↘ Blocked (real external block)
```

- Meaty issue: grill out the approach, then gather the context that approach needs, then ready.
- Simple issue: skip grilling; maybe skip Needs-info; go straight to Ready.
- `Grilling` and `Needs-info` are distinct lanes because they split by *who acts* (you interactively vs an agent/quick-fact) and by *depth* (approach vs context).

---

## 4. Comments (cockpit's async channel)

Three roles:

1. **Your async channel to cockpit.** From phone/web you drop notes: clarity, "split this," "move it," "this is done," instructions. `inbox` surfaces your unresolved comments as the work queue; cockpit handles each (often by spawning a per-issue native subagent).
2. **Cockpit Thread (one per issue).** A single top-level comment; all receipts / audit / log trails are replies under it. `comment`, `bind`, `release`, and `done` create or reuse it automatically.
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

# Dispatch and binding
./cockpit.py dispatch BJS-X
./cockpit.py bind BJS-X codex <session-id>
./cockpit.py bind BJS-X session:claude:<session-id>
./cockpit.py release BJS-X
./cockpit.py done BJS-X

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

Removed verbs (do not use): `issue-doctor`, `dispatch-prompt`, `inbox-review`, `comments-review`.

---

## 7. Dispatch

`./cockpit.py dispatch BJS-X` is the heavy verb. Steps:

1. Resolve the project's directory/repo from the issue's project — deterministic, no asking.
2. Ensure the working dir exists: clone if missing and a repo is known; create the dir if a brand-new project.
3. For Codex sessions: ensure the dir is a saved Codex project via `codex app <dir>`.
4. Launch a session in that dir (via the `agents` skill / provider CLI / Codex thread tools) with a brief derived from the issue body and unresolved comments.
5. Bind it and move the issue to `In Progress`.

Dispatch does not stop for folder-create / clone / `codex app`. It **does** respect the stop gates below.

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
- `triage` skill — use only when explicitly requested or when an issue needs deeper product/decision shaping than cockpit's triage pass.
- [references/linear-discipline.md](references/linear-discipline.md) — cockpit's write-auth config and session-binding mechanics (verbatim app-actor rules).
- [references/session-discipline.md](references/session-discipline.md) — dispatcher check, session lifecycle, closing and cleanup.

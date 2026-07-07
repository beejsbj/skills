---
name: linear
description: "Use when you need to understand or update Burooj's Linear board as configured: board ontology, lanes, labels, issue bodies, comments, dependencies, receipts, and the cockpit app-actor write path."
---

# Linear Board Discipline

Linear is canonical. Do not track workflow state anywhere else.

This skill defines Burooj's Linear board discipline and write path. It is shared context for any session that needs to read or update Linear state without inventing a parallel workflow.

Use this skill to:

- understand issue lanes, labels, comments, dependencies, and receipt expectations;
- make or request durable board updates through cockpit commands;
- avoid inventing parallel workflow state in chat, local files, or provider session titles.

This is not an orchestration skill. Do not use it to choose workers, launch sessions, or manage cockpit flow; use the `cockpit` skill for that.

---

## Ontology

- **Team:** `Bjs-projects` / key `BJS`.
- **Project:** a durable repo, area, or outcome lane. Read the live project list; do not trust this file for current project names.
- **Issue:** a packet of attention with enough context for a fresh worker to start cold.
- **Session:** one active attempt by Codex, Claude, opencode, Cursor, or another provider.
- **PR:** review artifact when an issue produces code.
- **Comment:** durable trail — receipts, questions, decisions. Never leave important state trapped in chat.
- **Dependency:** a Linear issue relation. Do not mark `Blocked` without a blocker issue or explicit comment.

---

## Issue Body Shape

```markdown
## Goal

One concrete outcome.

## Context

Source, repo/path, links, prior decisions — anything needed to avoid re-asking.

## Done when

- Observable completion condition.
- PR, checks, receipt, or review expectation where relevant.

Write Done-when **goal-grade**: one measurable end state, a stated check that proves it (a command, artifact, or count), and the constraints that must hold on the way — so a worker can adopt it verbatim as its native `/goal` condition (Claude Code and Codex both evaluate one after every turn).

## Constraints

- Boundaries, non-goals, approval gates, taste/security/account/money limits.
```

**Questions go to the Questions comment thread, not the body.** If you have a question for Burooj, post it as a reply under the issue's `Questions` top-level comment (create one if absent). Do not add question checkboxes to the issue body.

Omit any section that does not apply; do not write `N/A`.

Title discipline: plain verb + object + outcome. Prefer repo/path names when they disambiguate. Avoid vague umbrella titles.

---

## Status Lanes

| Lane | One-line meaning |
|---|---|
| `Inbox` | Intake; everything new or unclarified. |
| `Needs-info` | Context-gathering; an agent digs or you supply a fact. Bounded — does not linger. |
| `Grilling` | Deep shaping — clarify intent, sketch approach. Interactive with Burooj; can span sessions. |
| `Ready for Burooj` | Burooj is the next actor: a decision, approval, judgment, or physical action. |
| `Ready for agent` | Cold-dispatchable: a smart model has distilled the issue into a self-contained `/goal` a cheaper executor can run without judgment. |
| `Blocked` | Real external dependency (another issue or outside party). NOT "needs investigation." |
| `In Progress` | A worker session is executing it. Exactly one `session:*` label must be present. |
| `In Review` | PR / checks / review phase. |
| `Done` | Accepted closure: review artifact merged/accepted, or Burooj explicitly accepts closure without review. No `session:*` label. Final receipt left in the Cockpit Thread. |
| `Canceled` | Dead idea (Linear-native). |

Lane invariants:
- `In Progress` → exactly one `session:*` label.
- `Done` / `Canceled` / `Inbox` → no `session:*` label.
- `Blocked` → must have a Linear dependency relation or an explicit blocker comment.
- `Ready for agent` → must have Goal, Context, Done-when, Constraints, an `executor:*` class, and no hidden blocker. The readiness bar is the whole point of this lane: preparing an issue for it *is* a smart model writing a plan a less-smart model can execute cold. The Done-when must be goal-grade (see Issue Body Shape) — adoptable verbatim as the executor's `/goal` — and the `executor:*` class names the smallest model that plan is written for. If only a frontier model could run it, it isn't ready; sharpen the plan, don't reach for a bigger executor.

---

## Label Taxonomy

Labels encode metadata, never workflow position.

| Prefix | Purpose | Notes |
|---|---|---|
| `type:*` | Work kind | `bug`, `feature`, `improvement`, `cleanup`, `research`, `chore`, `seed`, `grilling`, `context`, `one-off`, `polish` |
| `executor:*` | Smallest model class the brief is written for | `frontier` (opus/fable judgment), `standard` (gpt-5.5/sonnet/glm/minimax implementation), `small` (haiku/flash bulk work) |
| `session:<provider>:<id>` | Active session binding | Live issues only; remove on `Done`/`Canceled` |

`formation:*`, `mode:*`, `agent:*`, and `workflow:*` labels are **removed** (mode/agent encoded dispatch-era routing that lanes now carry; `workflow:issue-pr` was an opaque, unused training rail) — do not read, write, or reference them. Use `type:*` instead of Linear's default `Feature`/`Improvement`/`Bug` labels.

---

## Comment Model

**Cockpit Thread** (one per issue): a single top-level comment. All receipts, binding events, and audit trail live as replies under it. `bind`, `release`, `move`, and `comment` commands create or reuse this thread automatically.

**Questions thread** (one per issue): a top-level comment titled `Questions`. Each question is a reply under it. Burooj replies per-question. Do not put questions in the issue body.

Use cockpit commands for all writes so authorship stays on the Cockpit app actor (not Burooj's personal account):

```bash
./cockpit.py bind BJS-123 codex <session-id>
./cockpit.py release BJS-123
./cockpit.py comment BJS-123 "Receipt or update."
./cockpit.py comment BJS-123 --reply-to <comment-id> "Reply body."
./cockpit.py comment-resolve <comment-id>
./cockpit.py comment-unresolve <comment-id>
./cockpit.py move BJS-123 "In Review"
```

Resolve a comment only when its question or blocker has actually been handled. Do not use raw Linear API/CLI writes for cockpit comments.

---

## Write Path

The app-actor GraphQL API (`https://api.linear.app/graphql`) is the **only** write path. All status moves, label changes, and comment writes go through cockpit commands, which author activity as the Cockpit app actor — not as Burooj.

Auth (in priority order):
1. `COCKPIT_LINEAR_APP_ACCESS_TOKEN` — OAuth access token with `actor=app`.
2. `COCKPIT_LINEAR_APP_CLIENT_ID` + `COCKPIT_LINEAR_APP_CLIENT_SECRET` — client-credentials app token.
3. Mac-local: `.linear.toml` with `app_actor.keychain_service` pointing to the client secret in macOS Keychain.
4. Emergency only: `COCKPIT_ALLOW_PERSONAL_LINEAR_WRITES=1`.

Run `./cockpit.py linear-doctor` to verify. It should report `write actor: app OK`.

Before any board touch, verify the action satisfies the lane invariants above and leaves a durable receipt in the Cockpit Thread when state changes.

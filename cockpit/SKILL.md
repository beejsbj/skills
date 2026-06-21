---
name: cockpit
description: Use when coordinating Burooj's cockpit in /Users/burooj/Projects/cockpit, using Linear as cockpit's issue board and source of workflow state, binding Codex/Claude/opencode/Cursor sessions to Linear issues through session:* labels, auditing open local sessions, or updating cockpit's Linear-first orchestration rules.
---

# Cockpit

Cockpit is Burooj's local orchestrator. Linear is cockpit's work surface and source of truth for issue state. Cockpit should make it harder to drift into random sessions by starting from issues, not from ambient chats.

The skill bundle owns the operating contract and CLI implementation:

```text
/Users/burooj/Projects/skills/cockpit/SKILL.md
/Users/burooj/Projects/skills/cockpit/scripts/cockpit.py
```

The cockpit repo links to these files as the local launch pad.

## First Move

```bash
cd /Users/burooj/Projects/cockpit
./cockpit.py status
./cockpit.py audit
./cockpit.py sessions
./cockpit.py linear-doctor
```

Use `./cockpit.py issue BJS-123` before steering or launching work for an issue.

## Linear Contract

Treat Linear as canonical for:

- project/lane
- issue content
- workflow status
- priority
- labels
- dependencies
- comments and receipts
- session binding labels

Do not create a parallel cockpit workflow state. Local provider sessions are an audit/resume lens only.

## Linear Shape

Use this ontology:

- Team: `Bjs-projects` / key `BJS`.
- Project: durable repo, area, or outcome lane. Prefer plain repo/dir names when they already carry meaning, but read the live Linear project list instead of trusting this file for current projects.
- Issue: packet of attention with enough context to pick up, review, or ask a concrete question.
- Session: one active attempt by Codex, Claude, opencode, Cursor, or another provider.
- PR: review artifact when an issue produces code.
- Comment: durable trail, receipt, question, or decision. Do not leave important state trapped only in chat.
- Dependency: Linear issue relation. Do not mark `Blocked` without a blocker issue or clear comment.

## Issue Structure

Use issue bodies as the durable packet. A good issue should let a fresh agent or Burooj answer: what is this, why now, where is the work, what counts as done, and what must not happen. Omit sections that do not apply; do not write `N/A`.

Default issue body:

```markdown
## Goal

One concrete outcome.

## Context

Source, repo/path, links, prior decisions, and anything needed to avoid re-asking.

## Done when

- Observable completion condition.
- Checks, PR, receipt, or review expectation where relevant.

## Constraints

- Boundaries, non-goals, approval gates, or taste/security/account/money limits.

## Questions

- [ ] Questions to answer, decide, or keep open while reviewing.

Use checkboxes for questions, including open or non-blocking questions. Do not couple questions to status.
```

Adjust by status:

- `Needs triage`: must preserve source/context and name the ambiguity. It may not have a full done-when yet.
- `Needs Burooj`: Burooj is the next actor. Put the needed review, approval, physical task, decision, or question near the top; use checkbox questions for questions, including open/non-blocking questions.
- `Ready for agent`: must have goal, context, done-when, constraints, project/repo/path, and no hidden blocker.
- `Blocked`: must have a Linear dependency relation or an explicit `Blocked by` comment.
- `In Progress`: must have exactly one active `session:*` label.
- `In Review`: must point to PR/checks/review surface when code was changed.
- `Done`: must have no `session:*` label and must have a final receipt or clear completion comment.

Split an issue when it would naturally produce multiple PRs, requires unrelated decisions, spans unrelated repos, mixes research with implementation, or has more than one independent done condition. Use parent/child issues for bundles; keep executable child issues atomic.

Title discipline:

- Use a plain verb + object + outcome.
- Prefer repo/path names when they disambiguate.
- Avoid poetic umbrella names and vague nouns.
- Keep seed titles honest with verbs like `Capture`, `Research`, `Clarify`, or `Park`.

## Status Meaning

Use statuses for workflow position:

- `Needs triage`: backlog intake that is not ready to execute.
- `Parked`: preserved but intentionally inactive.
- `Todo`: active, Burooj-needed or nextable work.
- `Needs Burooj`: active work where Burooj is the next actor for review, approval, physical action, judgment, or answer.
- `Ready for agent`: active work safe for an agent session.
- `Blocked`: active work blocked by an explicit dependency or comment.
- `In Progress`: active session is moving it.
- `In Review`: PR/review/check phase.
- `Done`: complete; no active session label should remain.

Use labels for metadata:

- `type:*`: kind of packet.
- `mode:*`: autonomy/HITL posture.
- `agent:*`: suitable agent/provider family.
- `workflow:issue-pr`: training rail for issue -> session -> PR -> receipt.
- `session:<provider>:<id>`: active session binding only.

Never use labels for workflow position.

## Discipline

Default loop:

1. Start from a Linear issue.
2. If there is no issue, create or identify the issue before starting work.
3. Clarify unclear work in `Needs triage`.
4. Move work to `Needs Burooj` when Burooj is the next actor, whether that is review, approval, physical action, judgment, or answer.
5. Move bounded agent work to `Ready for agent`.
6. Bind exactly one active session when an agent starts the attempt.
7. Move implementation to `In Progress`, review/checks to `In Review`, and finished work to `Done`.
8. On `Done`, remove `session:*`, archive the provider session where possible, and leave a receipt.

Rules:

- Prefer single issue -> single focused session -> single focused PR for code work.
- Discovery or planning can span multiple sessions, but each session must leave a receipt comment.
- Do not start from repo vibes, loose chat context, or remembered plans when a Linear issue exists.
- If the issue needs an answer from Burooj, put the question as a checkbox in the issue; do not hide it in an agent chat.
- Do not create permanent project steward sessions. Use project descriptions, issue bodies, comments, and temporary subagents for depth.
- Keep seeds cheap: preserve them as `type:seed` in `Needs triage`, `Parked`, or an appropriate holding lane until they earn a concrete loop.
- Use `workflow:issue-pr` when the work is intended to train the issue/session/PR loop.
- If the work involves money, account state, email sending, deletion, or security, stop for explicit Burooj approval.

## Session Binding

Bind sessions through Linear labels, not a cockpit table:

```bash
./cockpit.py bind BJS-123 codex <session-id>
./cockpit.py bind BJS-123 session:claude:<session-id>
./cockpit.py release BJS-123
./cockpit.py done BJS-123
```

Invariants:

- One active issue should have at most one `session:*` label.
- `session:*` labels belong only on active statuses.
- Backlog, parked, done, canceled, and duplicate issues should have no `session:*` labels.
- Issue body carries intent and done-when.
- Issue comments carry binding/release receipts and work trail.
- `done` moves the issue to `Done`, removes `session:*` labels, and archives provider sessions where possible.

Run `./cockpit.py audit` to find drift.

## Local Sessions

Keep `./cockpit.py sessions` as an audit/cleanup lens. Use it to find:

- local provider sessions not bound to an issue
- stale sessions still open after an issue is done
- sessions that need to be archived
- resume commands for known sidebar-visible sessions

Do not treat local session state as workflow truth.

## CLI Backend

Cockpit uses Kyaukyuai's Linear CLI through the local pinned npm package:

```bash
cd /Users/burooj/Projects/skills/cockpit
./node_modules/.bin/linear capabilities
./node_modules/.bin/linear issue list --team BJS --all-states --all-assignees --sort priority --json
```

Credentials must stay outside the repo. Use `LINEAR_API_KEY` or:

```bash
cd /Users/burooj/Projects/skills/cockpit
./node_modules/.bin/linear auth login --profile human-debug --interactive
```

Use MCP/connector access only to bootstrap missing facts or recover from CLI gaps. Cockpit's normal path should be CLI-first.

## Dispatcher Rule

Before doing work inside another project, ask:

1. Which Linear issue is this?
2. Is an active `session:*` label already bound?
3. Can cockpit inspect or resume that session instead of taking over?
4. Is the next move synthesis, unblocking, review, or handoff?
5. Has Burooj explicitly assigned cockpit itself as the worker?

Edit outside `/Users/burooj/Projects/cockpit` only after that check.

## Receipt Shape

When a session moves an issue, leave a concise Linear comment:

```text
Agent:
Session:
Workspace:
Branch:
Issue:
Result:
Checks:
PR:
Next:
Blocked by:
```

Skip fields only when they truly do not apply.

## Stop Gates

Stop and ask before deletion, provider-side purge, secrets/private keys, account/security/money/email-send actions, canonical source-of-truth decisions, pushing, rewriting history, or broad workflow changes.

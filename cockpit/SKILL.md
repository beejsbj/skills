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

The cockpit repo links to this skill folder as its local launch pad.

## First Move

```bash
cd /Users/burooj/Projects/cockpit
./cockpit.py status
./cockpit.py audit
./cockpit.py sessions
./cockpit.py linear-doctor
```

Use `./cockpit.py issue BJS-123` before steering or launching work for an issue.

Read [references/linear-discipline.md](references/linear-discipline.md) before creating or editing Linear issues, changing statuses or labels, marking work done, auditing workflow drift, or updating cockpit's Linear rules.

Read [references/session-discipline.md](references/session-discipline.md) before driving provider sessions: launching, resuming, messaging, binding, releasing, archiving, or auditing them. For pure local session discovery with `./cockpit.py sessions`, the reference is usually not needed.

## Related Skills

Use `triage` for issue triage, inbox clarification, Needs Burooj vs Ready for agent decisions, agent-ready briefs, and out-of-scope or prior-decision records. Cockpit owns the local CLI/session bridge; `triage` owns issue-formation judgment.

Use `agents` when cockpit needs to start, resume, fork, inspect, message, attach to, or archive top-level provider-visible Codex/Claude/opencode/Cursor sessions. Cockpit may drive sessions through `agents`, but it should not become the executor for ordinary project work.

## Commands

```bash
./cockpit.py status
./cockpit.py board
./cockpit.py issue BJS-123
./cockpit.py bind BJS-123 codex <session-id>
./cockpit.py bind BJS-123 session:claude:<session-id>
./cockpit.py release BJS-123
./cockpit.py done BJS-123
./cockpit.py audit
./cockpit.py sessions
./cockpit.py linear-doctor
```

Use `bind`, `release`, `done`, and `audit` according to [references/linear-discipline.md](references/linear-discipline.md) and [references/session-discipline.md](references/session-discipline.md).

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
5. Has Burooj explicitly assigned cockpit itself as the executor?

Edit outside `/Users/burooj/Projects/cockpit` only after that check.

## Stop Gates

Stop and ask before deletion, provider-side purge, secrets/private keys, account/security/money/email-send actions, canonical source-of-truth decisions, pushing, rewriting history, or broad workflow changes.

# Session Discipline (cockpit reference)

Cockpit is the manager-coworker. It prepares work, binds sessions, and keeps Linear honest; it does not become the executor for ordinary project work.

---

## Orchestrate, Don't Execute

Read the board, pick the next move, prepare the launch brief, and let native orchestration create the worker in the issue's own repo. A cockpit chat binds itself only when the issue *is* cockpit's own work. Inspecting a repo before launch is fine — keep it read-only, then hand execution to a worker unless Burooj names cockpit as the executor.

---

## Dispatcher Check

Before doing work inside another project, confirm:

1. Which Linear issue is this?
2. Is an active `session:*` label already bound?
3. Can cockpit inspect or resume that session instead of taking over?
4. Is the next move synthesis, unblocking, review, or handoff?
5. Has Burooj explicitly assigned cockpit itself as the executor?

Edit outside `/Users/burooj/Projects/cockpit` only after that check.

---

## Preparing Work

Cockpit prepares and records; native orchestration launches.

Use `prepare BJS-X` to resolve issue/project/repo, produce the launch brief, and expose any branch/worktree metadata. Use the active surface's native tools to create the worker session/thread. Then bind the resulting session with `bind`.

`cockpit.py` is an actuator and ledger, not the orchestration brain. It should not own provider-specific thread lifecycle logic when Codex Desktop, provider CLIs, Matt Pocock's orchestration layer, or native subagents can perform it directly.

For `Needs-info` work, cockpit spawns a **native subagent** (harness Task) pointed at the project dir, read-only, writing its findings back as an issue comment. No separate CLI launch verb needed.

---

## Review, Closing, and Cleanup

- `release BJS-X` drops the binding without closing the issue.
- `move BJS-X "In Review"` is allowed when a PR or explicit review artifact exists and the issue receipt names it.
- `move BJS-X Done` is allowed only after acceptance/merge, or when Burooj explicitly accepts closure without review.
- Do not archive/release worker sessions before the PR/review artifact exists and is recorded.
- `audit` catches mechanical drift: orphan labels, bound-but-done, double bindings.
- `sessions` finds unbound or stale local sessions to resume or archive.

Cockpit can only catch *mechanical* drift. Artifact gates require checking actual repo/review state, not opaque `workflow:*` labels. The worker is responsible for writing durable state back to its issue before review or closure.

# Session Discipline (cockpit reference)

Cockpit is the manager-coworker. It dispatches sessions; it does not become the executor for ordinary project work.

---

## Orchestrate, Don't Execute

Read the board, pick the next move, and dispatch a session to do the work in the issue's own repo. A cockpit chat binds itself only when the issue *is* cockpit's own work. Inspecting a repo before dispatch is fine — keep it read-only, then hand execution to a dispatched session unless Burooj names cockpit as the executor.

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

## Dispatching a Session (`dispatch BJS-X`)

`./cockpit.py dispatch BJS-X` is the heavy verb. Cockpit:

1. Resolves the project's directory/repo from the issue's project (deterministic — every project is coupled to a dir and/or GitHub repo).
2. Ensures the working dir exists: clones if missing and a repo is known; creates the dir if it is a brand-new project.
3. For Codex sessions: ensures the dir is a saved Codex project via `codex app <dir>`.
4. Launches a session in that dir (via the `agents` skill / provider CLI / Codex thread tools) with a brief derived from the issue body and its unresolved comments.
5. Binds it (`./cockpit.py bind BJS-X <provider> <id>`) and moves the issue to `In Progress`.

Dispatch does not stop for folder-create / clone / `codex app`. It **does** respect the global stop gates (money / accounts / security / deletion / email-send / broad workflow changes).

For `Needs-info` work, cockpit spawns a **native subagent** (harness Task) pointed at the project dir, read-only, writing its findings back as an issue comment. No `dispatch` verb needed.

---

## Closing and Cleanup

- `./cockpit.py release BJS-X` — drop the binding without closing the issue.
- `./cockpit.py done BJS-X` — move to `Done`, remove `session:*`, archive the provider session. Leave the receipt comment first.
- `./cockpit.py audit` — catch mechanical drift: orphan labels, bound-but-done, double bindings.
- `./cockpit.py sessions` — find unbound or stale local sessions to resume or archive.

Cockpit can only catch *mechanical* drift. The dispatched session is responsible for writing durable state back to its issue.

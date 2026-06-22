# Session Discipline

Cockpit is the intended reader of this file. A dispatched session is a cold provider session running in the issue's own repo; do not assume it has read cockpit's rules. The main behavior cockpit can shape inside it is the text cockpit hands over at launch or resume (see Dispatch Prompt).

This file governs what cockpit does *around* sessions. Linear stays the board of record; label mechanics and receipt shape live in [linear-discipline.md](linear-discipline.md).

## Orchestrate, Don't Execute

Cockpit reads the board, picks the next move, and dispatches a session to do the work in the issue's own repo. It does not become the executor for ordinary project issues.

A cockpit chat binds itself only when the issue *is* cockpit's own work. Inspecting a repo before dispatch is fine — keep it read-only and hand execution to a dispatched session unless Burooj names cockpit as the executor.

## Dispatching A Session

Before launching or resuming a session for an issue:

1. Read it: `./cockpit.py issue BJS-123`.
2. Confirm it is `Ready for agent`, `In Progress`, or explicitly assigned, and that no active `session:*` label already owns it.
3. Pick the repo/folder from the issue body, project, or comments. If that is unclear, move the issue to `Needs Burooj` instead of guessing.
4. Launch or resume the session **in that folder** using the `agents` skill, provider CLI, or a resume command from `./cockpit.py sessions`.
5. Hand it the dispatch prompt below.
6. Bind it: `./cockpit.py bind BJS-123 <provider> <session-id>`, then move the issue to `In Progress`.

Bind the session actually doing the work — never cockpit as a proxy, never a session that is only advising or ranking, never before it has accepted a concrete issue.

## Closing And Cleanup

- `./cockpit.py release BJS-123` — drop the binding without closing the issue.
- `./cockpit.py done BJS-123` — move to `Done`, remove `session:*`, archive the provider session. Leave the receipt first.
- `./cockpit.py audit` — catch mechanical drift: orphan labels, bound-but-done, double bindings.
- `./cockpit.py sessions` — find unbound or stale local sessions to resume or archive.

Cockpit can only catch *mechanical* drift; it cannot read truth out of a session's chat. The dispatched session is responsible for writing durable state back to its issue, which is why the dispatch prompt makes that its job.

## Dispatch Prompt

Hand every dispatched session a prompt of this shape:

> You own **BJS-123** — `<title>`.
> Start from this repo and keep changes scoped to this issue.
> Use these commands when you need to inspect or update the issue:
>
> ```bash
> /Users/burooj/Projects/cockpit/cockpit.py issue BJS-123
> /Users/burooj/Projects/skills/cockpit/node_modules/.bin/linear issue update BJS-123 --state "In Progress" --comment "Started work." --text
> /Users/burooj/Projects/skills/cockpit/node_modules/.bin/linear issue comment add BJS-123 "Progress update, blocker, discovered work, or receipt."
> /Users/burooj/Projects/skills/cockpit/node_modules/.bin/linear issue comment list BJS-123
> /Users/burooj/Projects/cockpit/cockpit.py release BJS-123
> /Users/burooj/Projects/cockpit/cockpit.py done BJS-123
> ```
>
> Ask cockpit if a command fails or if you need a board-level change outside this issue.
> Scope every change to this one issue. When you discover unrelated, board-wide, or follow-up work, record it as a `Discovered` comment — or a linked issue if it blocks you — and leave it for cockpit to triage rather than acting on it or moving sibling issues yourself.

This prompt is the only place a dispatched session's boundaries exist. Everything it should or should not do belongs here, not in a rules section it will never read.

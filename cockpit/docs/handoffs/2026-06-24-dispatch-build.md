# Handoff: Build cockpit's `dispatch` launch step

Date: 2026-06-24
For: a Codex session running **inside Codex Desktop** (it has the native app tools
and can empirically test the Desktop sidebar — a standalone CLI cannot).
Repo: `/Users/burooj/Projects/skills/cockpit` · CLI: `scripts/cockpit.py`
Design source of truth: `docs/specs/2026-06-24-cockpit-redesign.md` (§8 dispatch).

Update: dispatch now prepares and launches in a per-issue git worktree under
`~/.codex/worktrees` when the resolved project dir is a git repo. Brand-new or
non-git dirs still launch in the project dir.

## Why this is handed to you

The cockpit redesign is done **except dispatch's launch step**. Everything else —
the GraphQL-only Linear surface, the 9-lane model, formation removal, the comment
model, the `linear` skill, and the deterministic dispatch *prep* — is built and
committed. The launch step was left to you because the clean path to a
**project-native, sidebar-visible Codex Desktop thread** is only reachable from
inside Codex Desktop / its app-server, not from the Claude Code CLI that did the rest.

## What `dispatch` already does (don't rebuild)

`dispatch_issue()` in `scripts/cockpit.py` already wires the full chain:

1. Load the issue + comments (GraphQL app-actor).
2. `resolve_issue_project_dir()` → find the project dir (path in body, or
   `/Users/burooj/Projects/<project-name>`). **TODO(dispatch):** a real project→dir
   registry (e.g. a `[projects]` table in `.linear.toml`) and git-clone when a repo
   URL is in the body but the dir is missing.
3. `ensure_project_dir()` → mkdir for a brand-new project.
4. `ensure_dispatch_worktree()` → create/reuse a per-issue worktree when the project dir is a git repo.
5. `ensure_codex_project()` → runs `codex app <launch-dir>` (opens/registers the workspace).
6. `build_dispatch_brief()` → brief from issue body + unresolved comments + stop gates.
7. **`launch_session_for_issue()` → originally the stub this handoff asked you to implement.**
8. On a real session id: `bind_linear_issue(..., move_state="In Progress")` already
   binds the `session:<provider>:<id>` label and moves the issue. Done for you.

So you only need to make `launch_session_for_issue()` return a real session id.

## Verified launch facts (tested 2026-06-24, codex-cli 0.139.0)

Three paths, empirically checked:

| Path | Sidebar-visible | Auto-starts | Returns id | Driveable from cockpit.py |
|---|---|---|---|---|
| `codex exec -C <dir> --json "<brief>"` | ❌ no | ✅ | ✅ `thread.started.thread_id` (first --json line) | ✅ |
| `open "codex://threads/new?prompt=&path="` deep link | ✅ yes | ❌ waits for ⏎ | ❌ none | ✅ (`open`) |
| **App Server JSON-RPC** | ❓ untested (likely yes) | ✅ | ✅ `thread.id` | ✅ |

- `codex exec` proved CLI-only (Burooj confirmed it does NOT appear in the app sidebar).
- The deep link proved sidebar-native but stops at the composer (no auto-submit, no id).

## Recommended approach: the App Server

Build `launch_session_for_issue()` on the Codex **app-server** JSON-RPC (2.0 over
NDJSON). It is the only path that is auto-starting AND id-returning AND likely
sidebar-visible. Sequence (from the app-server docs):

```
1. ensure a server: `codex app-server` (stdio subprocess) OR
   `codex app-server daemon start` (idempotent) + connect the unix socket at
   $CODEX_HOME/app-server-control/app-server-control.sock
2. JSON-RPC: initialize  (clientInfo: {name:"cockpit",...})
3. JSON-RPC: thread/start { cwd: "<project_dir>", approvalPolicy:..., sandbox:... }
   → result.thread.id  (e.g. "thr_123") + result.thread.sessionId
4. JSON-RPC: turn/start  { threadId, input:[{type:"text", text:"<brief>"}] }
   → auto-runs the turn; stream events until turn/completed
5. return the thread id for bind_linear_issue()
```

Minimal stdio driver (reference, verify method names/params against your local
`codex app-server` build before trusting):

```python
proc = subprocess.Popen(["codex","app-server"], stdin=PIPE, stdout=PIPE, text=True)
send({"method":"initialize","id":0,"params":{"clientInfo":{"name":"cockpit","version":"0.1.0"}}})
recv()
send({"method":"thread/start","id":1,"params":{"cwd":str(project_dir),"approvalPolicy":"never"}})
thread_id = recv()["result"]["thread"]["id"]
send({"method":"turn/start","id":2,"params":{"threadId":thread_id,"input":[{"type":"text","text":brief}]}})
# drain events to turn/completed
return thread_id
```

### 2026-06-24 Codex Desktop result

Direct `codex app-server` JSON-RPC can return a thread id, but the thread did not
persist into Codex Desktop's `state_5.sqlite` / sidebar session list on this Mac.
The official Python SDK (`openai-codex`) did persist into Desktop state and is
discoverable through `./cockpit.py sessions`; cockpit dispatch now launches through
that SDK via a background helper so the parent command can bind the returned id
while the turn continues to run.

However, SDK-created threads may not appear in an already-open Codex Desktop
sidebar until the app is restarted. The live-refreshing path is the native
Codex Desktop `create_thread` tool. Cockpit now exposes
`./cockpit.py dispatch-prepare BJS-X --provider codex` for Desktop callers:
prepare JSON with `project_dir` + `brief`, call native `create_thread`, then bind
the returned id with `./cockpit.py bind BJS-X codex <thread-id> --force
--move-state "In Progress"`.

### The one thing to verify empirically (you can; the CLI couldn't)

**Do app-server-created threads appear in the Codex Desktop sidebar, live?** Run the
`thread/start`+`turn/start` sequence with `cwd` = a real project (e.g.
`/Users/burooj/Projects/bjslab`) while the Desktop app is open, and watch the
bjslab workspace sidebar. If yes → app-server is the spine, ship it. If no → fall
back to the **in-app `create_thread`/`list_projects` MCP tools** you (a Desktop
session) have natively, which definitively create sidebar threads; cockpit.py would
then resolve/clone/`codex app`/build-brief and hand you the thread params to launch,
and bind by polling the session store (as `./cockpit.py sessions` already reads it).

## Acceptance criteria

- [ ] `./cockpit.py dispatch BJS-X` launches a real, auto-running Codex session
      rooted in an issue worktree when the project is a git repo, falling back to
      the project dir for non-git projects, and returns its id.
- [ ] The session is **visible in the Codex Desktop sidebar** in that workspace
      (verify; record which path achieved it).
- [ ] cockpit binds `session:codex:<id>` and moves the issue to `In Progress`
      (already wired via `bind_linear_issue`).
- [ ] `python3 -m py_compile scripts/cockpit.py` passes; `git diff --check` clean.
- [ ] Resolve the open `# TODO(dispatch):` markers in `scripts/cockpit.py` you rely
      on (project→dir registry, repo clone) or leave them clearly scoped.

## Constraints / stop gates

- Linear writes go through cockpit's app-actor commands only (never personal auth,
  never raw Linear writes). Reads/writes already implemented.
- Respect the global stop gates (money / accounts / security / deletion / email /
  broad workflow changes) — see `SKILL.md` §8.
- Don't change the lane model, comment model, or the `linear` skill; just the launch.

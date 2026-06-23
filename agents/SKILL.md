---
name: agents
description: Choose and operate top-level provider-visible agents/sessions across Claude, opencode, and Cursor. Use when the user says use an agent, start a session, resume an agent session, fork a session, hand work to another visible non-Codex agent, get a quick one-off answer from a non-Codex provider, throwaway cross-provider second opinion, use claude, use opencode, use cursor, ask opus, ask sonnet, or ask haiku. Do not use for Codex Desktop thread creation or harness-native subagents.
---

# Agents

Use this skill for **top-level provider-visible non-Codex agents/sessions**: durable Claude, opencode, or Cursor sessions that can be discovered, inspected, resumed, forked, attached to, or archived.

Do not use this skill to create or manage Codex Desktop threads. When a user asks to create, fork, inspect, continue, hand off, pin, archive, rename, or otherwise manage a Codex thread from inside Codex Desktop, use the built-in app thread tools instead. For new Codex threads, call `list_projects` first, then `create_thread` with the returned `projectId`; after success, report the created thread directive/link handle back to the user.

Do not use this skill for harness-native internal delegation:

- Codex Desktop threads and Codex subagents
- Claude subagents
- Claude agent teams
- Claude `/tasks`
- opencode subagents (via `@general` etc.)
- provider-internal background work

Rule of thumb:

- If the work should report back inside the current conversation and can run in the current harness, use the current harness's native subagent system.
- If the work is a quick one-shot but needs a *different non-Codex* provider, use `agents.py run`.
- If the work should become a visible resumable non-Codex session/thread, use `agents.py` (`start`/`resume`/`fork`) or the native top-level provider CLI.
- If the work should become a visible Codex Desktop thread, use the Codex app thread tools (`list_projects` -> `create_thread`) instead of `agents.py` or `codex exec`.

Everything else is a modifier:

- **Provider**: the CLI or harness used to run the agent.
- **Lineage**: started, resumed, or forked.
- **Workspace**: current checkout, worktree, sandbox, or another working directory.
- **Run configuration**: model, effort/thinking level, output format, permissions, and tool access.
- **Intent**: ask, review, do, steward, inspect, or coordinate.

Provider, lineage, workspace/isolation, run configuration, and intent are modifiers on top of the visible-session primitive.

## agents.py

The Python CLI lives beside this file:

```bash
python /Users/burooj/Projects/skills/agents/agents.py --help
```

It is stateless and JSON-first. It reads provider stores for discovery, uses native provider commands for actions, and does not edit provider transcript stores.

V1 verbs:

```text
discover
inspect
start
run
resume
fork
archive
unarchive
attach
```

`run` is a **cross-provider ephemeral one-shot**: prompt a non-Codex provider, get the answer back here, no durable handoff. It exists because native subagents only run inside the current harness — they cannot reach another provider. Use `run` when you want a quick second opinion or cheap pass from a *different non-Codex* provider. For claude (`--no-session-persistence`) this is truly non-persistent; opencode and cursor have no ephemeral flag, so `run` creates a disposable session whose row still persists and is surfaced with a warning.

There is intentionally no subagent or team command — that work belongs to each harness's native subagent system.

Model guidance lives in `profiles.json`. Profiles guide but do not restrict; unknown model names are passed through with a warning.

## Decision Rule

- Use native subagents for quick ask/review/summarize/classify/debug-hypothesis work where only the returned result matters and the current harness can do it.
- Use `agents.py run` for that same quick work when it needs a *different non-Codex* provider — a throwaway cross-provider second opinion or cheap pass.
- Use a visible top-level non-Codex session for work the user may want to see, resume, fork, attach to, archive, or hand off later.
- Use the Codex app's built-in thread tools for Codex Desktop sessions; do not create Codex Desktop handoffs through `agents.py start` or `codex exec`.
- Use a worktree/workspace modifier when independent edits may collide with the current checkout.
- Use the provider the user named. If unnamed, choose the provider whose strengths fit the task, or stay in the current session for small work.
- Use **opencode** when the task benefits from opencode's TUI, its built-in provider integrations (opencode-go models), or when resuming an existing opencode session.
- Use **cursor** when the task needs the Cursor agent CLI, particularly for Composer 2.5 models. cursor discovery is minimal (workspace only); prefer start/resume.
- When creating a visible session, report the session ID, name, working directory, and attach/resume command back to the user.
- When the spawned agent needs to report back automatically, pass an explicit callback target such as a parent session ID, output file path, issue, or command. Otherwise poll logs or transcripts.

## Worked Examples

User says: "Use opus to audit this skill, but keep it as a root session."

- Topology: root session, because the user wants a durable audit surface.
- Provider: Claude, because Opus is a Claude model alias.
- Workspace: current repo.
- Run configuration: Opus, high effort.
- Command:

```bash
claude --bg --name "agents-skill-audit" --model opus --effort high \
  "Read agents/SKILL.md and audit it. Do not edit files. Return findings and recommendations."
```

Report back:

```text
Created root session agents-skill-audit (<id>) in $PWD.
Attach: claude attach <id>
Logs: claude logs <id>
```

User says (while working in Codex): "Get a quick throwaway second opinion from Claude on this diff."

- Intent: ask, one-shot. Only the returned answer matters and no session is wanted.
- Why not a native subagent: the user asked for a provider-visible Claude pass. Cross-provider one-shot -> `run`.
- Command:

```bash
python /Users/burooj/Projects/skills/agents/agents.py run \
  --provider claude \
  --workspace "$PWD" \
  --message "Run git diff in this repo and review the working changes. Return correctness findings only."
```

`run` does not forward stdin to the provider, so put the instruction in `--message` and let the agent read the repo itself.

User says: "Start a Codex thread for this repo."

- Do not use this skill. Use the Codex Desktop thread tools from the app context:
  - call `list_projects`
  - choose the returned `projectId` for the target repo
  - call `create_thread` with `target: { type: "project", projectId, environment: { type: "local" } }`
  - report the created thread directive/link handle to the user

User says: "Ask Claude to start a visible review session for this repo."

- Provider: Claude.
- Workspace: current repo.
- Run configuration: visible durable session.
- Command:

```bash
python /Users/burooj/Projects/skills/agents/agents.py start \
  --provider claude \
  --workspace "$PWD" \
  --wait \
  --message "Review this repository state. Return correctness findings only."
```

User says: "Start an opencode session with kimi-k2.7-code to implement auth."

- Provider: opencode.
- Workspace: current repo.
- Run configuration: kimi-k2.7-code model.
- Command:

```bash
python /Users/burooj/Projects/skills/agents/agents.py start \
  --provider opencode \
  --workspace "$PWD" \
  --model opencode-go/kimi-k2.7-code \
  --wait \
  --message "Implement the auth feature described in the README."
```

User says: "Use Cursor with composer-2.5 to review this PR."

- Provider: cursor.
- Workspace: current repo.
- Run configuration: Composer 2.5, print mode.
- Command:

```bash
python /Users/burooj/Projects/skills/agents/agents.py start \
  --provider cursor \
  --workspace "$PWD" \
  --model composer-2.5 \
  --message "Review this PR for correctness issues."
```

## Model And Effort

- Use the user's named model or effort exactly when provided.
- Use stronger models and higher effort for architecture, security, ambiguous bugs, code review with real risk, and handoffs that may guide implementation.
- Use faster/cheaper models and lower effort for extraction, summarization, classification, and simple checks.
- Prefer native CLI flags when available, such as Claude `--model` and `--effort`.
- Increase effort for durable root sessions that will become a source of truth for later work.
- Verify provider flags with local `--help` when portability matters. These examples were written against Claude Code `2.1.138`.

## Claude CLI Examples

```bash
# Root session in print mode
claude -p --name "auth-review" --model opus --effort high \
  "Review this architecture and keep the session available for follow-up."

# Managed/background root session
claude --bg --name "auth-review" --model opus --effort high \
  "Review this architecture and keep working until you have findings."

# Resume/fork root session
claude --resume <session-id-or-name> -p \
  "Continue the previous investigation."

claude --resume <session-id-or-name> --fork-session -p \
  "Explore an alternate path."
```

For implementation work, prefer a root session and an isolated workspace:

```bash
claude --worktree feature-auth --bg --name "feature-auth" \
  "Implement this bounded change and report verification."
```

## Codex Desktop Threads

Inside Codex Desktop, Codex session creation belongs to the built-in thread tools, not this skill:

```text
list_projects -> create_thread -> report ::created-thread{threadId="..."}
```

Use a project target with `environment: { type: "local" }` for repo-scoped work unless the user explicitly asks for a worktree. Do not substitute `codex exec` when the user wants a visible Codex app thread.

## opencode CLI Examples

```bash
# Start a new session (prints JSON)
opencode run --format json \
  --model opencode-go/glm-5.1 \
  "Implement this bounded change and report verification."

# Start in a specific directory
opencode run --format json --dir /path/to/project \
  --model opencode-go/kimi-k2.7-code \
  "Review this architecture and keep the session available for follow-up."

# Resume a session
opencode run --format json --session ses_xxx \
  "Continue the previous investigation."

# Fork a session
opencode run --format json --session ses_xxx --fork \
  "Explore an alternate path."

# List sessions (JSON)
opencode session list --format json

# Export a session transcript
opencode export ses_xxx
```

opencode sessions are discovered via `opencode session list --format json` (with SQLite fallback). Session state is stored in `~/.local/share/opencode/opencode.db`.

opencode has no archive verb. Use cockpit-level state tracking for archival semantics.

## Cursor Agent CLI Examples

```bash
# Start a new session (print mode)
cursor agent --print \
  --model composer-2.5-fast \
  "Implement this bounded change and report verification."

# Start in a specific workspace
cursor agent --print --workspace /path/to/project \
  --model composer-2.5 \
  "Review this architecture and produce findings."

# Resume a session
cursor agent --resume <chatId> --print \
  "Continue the previous investigation."

# Continue the last session
cursor agent --continue --print \
  "Continue from where we left off."

# Start in an isolated worktree
cursor agent --print --worktree feature-branch \
  --model composer-2.5 \
  "Implement this bounded change."
```

Cursor agent has limited discovery (`cursor agent ls` requires a TTY). Session metadata is minimal (workspace only). Use `agents.py discover --provider cursor` for best-effort metadata, or prefer start/resume.

Cursor agent has no archive/fork verbs. Use cockpit-level state tracking for archival semantics.

## Notes

- A returned session/thread ID is not proof of durability; inspect or resume before treating it as a durable handoff.
- Multiple root sessions can be simulated with multiple shell terminals or background sessions.
- Keep prompts bounded and name the output shape.
- **opencode** session IDs use the `ses_` prefix (e.g., `ses_abc123`). Discovery uses `opencode session list --format json` with SQLite fallback at `~/.local/share/opencode/opencode.db`.
- **cursor** agent sessions are thin-metadata (workspace/cwd only, no rich transcript). Prefer start/resume over discover/inspect. Cursor's `--print` flag is required for non-interactive use.

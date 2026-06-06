---
name: agents
description: Choose and spawn agents or sessions as ephemeral helpers or durable root sessions. Use when the user says use an agent, start a session, spawn a parent/root session, resume an agent session, fork a session, create an ephemeral helper, hand work to another agent, use claude, use codex, use opus, ask sonnet, or ask haiku.
---

# Agents

Use one simple topology for agents and sessions:

- **Ephemeral helper**: a bounded agent call that returns an answer here and does not need durable history.
- **Root session**: a parent agent session with durable history that can be resumed, forked, attached to, or inspected later.

Everything else is a modifier:

- **Provider**: the CLI or harness used to run the agent.
- **Lineage**: fresh, resumed, or forked.
- **Body**: current checkout, worktree, sandbox, or another working directory.
- **Run configuration**: model, effort/thinking level, output format, permissions, and tool access.
- **Intent**: ask, review, do, monitor, or coordinate.

Do not treat worktree, ask, review, or do as topology modes. Worktree is where the agent acts. Ask/do is what the agent is asked to do.

## Decision Rule

- Use an **ephemeral helper** for quick ask/review/summarize/classify/debug-hypothesis work where only the returned result matters.
- Use a **root session** for work the user may want to see, resume, fork, attach to, or hand off later.
- Use a worktree/body modifier when independent edits may collide with the current checkout.
- Use the provider the user named. If unnamed, choose the provider whose strengths fit the task, or stay in the current session for small work.

## Model And Effort

- Use the user's named model or effort exactly when provided.
- Use stronger models and higher effort for architecture, security, ambiguous bugs, code review with real risk, and handoffs that may guide implementation.
- Use faster/cheaper models and lower effort for extraction, summarization, classification, simple checks, and disposable helper passes.
- Prefer native CLI flags when available, such as Claude `--model` and `--effort`.
- For Codex, use `--model` when the user names a Codex model. Use config overrides only when the local Codex CLI/provider documents the relevant setting.
- Keep effort lower for ephemeral helpers unless disagreement or uncertainty would be expensive.
- Increase effort for durable root sessions that will become a source of truth for later work.

## Claude CLI Examples

```bash
# Ephemeral helper
claude -p --no-session-persistence --model sonnet --effort medium \
  "Review this plan. Return findings only."

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

For implementation work, prefer a root session and an isolated body:

```bash
claude --worktree feature-auth --bg --name "feature-auth" \
  "Implement this bounded change and report verification."
```

## Codex CLI Examples

```bash
# Ephemeral helper
codex exec --cd "$PWD" --sandbox read-only --ephemeral \
  "Review this diff. Return findings only."

# Root session
codex exec --cd "$PWD" --sandbox read-only \
  "Review this architecture and keep the session available for follow-up."

# Add --model <model> when the user names a Codex model.

# Resume root session
codex exec resume <thread-id> \
  "Continue the previous investigation."
```

For implementation work, prefer a root session and an isolated body:

```bash
codex exec --cd "<worktree-path>" --sandbox workspace-write \
  "Implement this bounded change and report verification."
```

## Notes

- A returned session/thread ID is not proof of durability. Ephemeral/no-persistence runs may still emit an ID that cannot be resumed.
- Multiple root sessions can be simulated with multiple shell terminals or background sessions.
- Keep prompts bounded and name the output shape.
- Report root session IDs/names back to the user when created.

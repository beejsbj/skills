---
name: cockpit-agents
description: Delegate to another agent or model under one rule - T3 is the orchestrator, so use its MCP tools (delegate_task for a piece of your task, including a review; T3 threads for an independent workstream) or `t3 thread` and T3's MCP sign-in from outside a T3 session. Use `cockpit agents` only for what T3 lacks - live availability; native and persona sessions; and handing off or moving work to the cloud (Claude cloud sessions, Codex Cloud). Environment installation and upgrades follow the Cockpit handbook.
---

# Cockpit agents

A request to run, create, or message a session authorizes that operation within the stated scope; skill discovery alone does not authorize new work. Resolve `cockpit handbook agents` for the rule and command details.

## The rule

T3 is the orchestrator.

- **A piece of your task:** your own subagent tool when your harness and model are right; otherwise `delegate_task` on any provider and model T3 lists.
- **An independent workstream Burooj may want to watch or steer:** a T3 thread. For one that writes, use `t3_thread_launch` with a `worktree` workspace strategy, because `create_threads` shares the parent's branch and checkout.
- **A review, consult, or scout:** `delegate_task` whose brief says to only read. Run `git status` in that checkout before and after, and compare them. That sees only what git sees: not ignored paths or writes outside the checkout. T3 does not enforce this: `role: review` and Codex plan mode both wrote in tests. Point it where a stray write is cheap to undo, and never at the canonical cockpit checkout.
- **Which model ran:** read the child's T3 thread.
- **Limits:** there is no job count. Memory caps are the limit, and past one the kernel kills a process, so route heavy commands through `cockpit resources run`.
- **Hermes:** the `hermes-klaw` and `hermes-otto` T3 instances run them as `delegate_task` children. Always pass a model.
- **From outside a T3 session:** scripts use `t3 thread start|send|show|list`; agents that speak MCP over HTTP with OAuth can sign in to T3's `/mcp`, and Klaw and Otto are signed in. Start a thread from outside with `t3_thread_launch`, passing `message` and `modelSelection`; `create_threads` fails there.

Everything below is for what T3 lacks: `options` when choosing a model, native and persona sessions, and cloud handoff. `cockpit agents run`, `create`, `receipt`, `resume-limited`, `projects`, `models`, and `threads` were removed on 2026-11-04, and `show`, `send`, and `resume` no longer take T3 threads, which use `t3 thread` or T3's MCP tools.

## Select the environment and route

Run Cockpit on the machine that owns the project files, harness credentials, and session. For remote work, resolve that machine's access guidance through `cockpit handbook` and use its documented connection. A T3 desktop connection does not synchronize files or make a remote checkout local.

```bash
cockpit agents options --intent work --json
cockpit agents sessions --harness all --json
```

Use live `options` for route availability, account limits, and fallback order when choosing a model. Preserve requested models and effort; use [model-taste](../model-taste/SKILL.md) for unspecified choices. For independent judgment, see [consult](../consult/SKILL.md). A `native` route is your own subagent tool (Agent tool, `spawn_agent`, `delegate_task`), used from inside your session, not through Cockpit; a catalog model is not necessarily an allowed override there, so check the tool's advertised choices.

## Continue a persona or native session

T3 threads are T3's: use its MCP tools or `t3 thread`. Cockpit's `send` refuses a T3 id and names them. For a persona session (Otto, Rose), or a native Codex or Claude session T3 did not start:

```bash
cockpit agents show hermes:SESSION_ID --profile PROFILE
cockpit agents send hermes:SESSION_ID --profile PROFILE \
  --message-file /absolute/path/follow-up.md [--dry-run]
cockpit agents resume codex:SESSION_ID        # interactive, in the recorded cwd
```

Keep the harness, exact session ID, and Hermes profile together when selecting a target. Cockpit refuses a bare ID or `t3:` ID as a T3 thread. `show` returns metadata only; keep raw personal transcripts out of output and saved artifacts. Resolve refusals from observed state rather than bypassing guards.

## Hand off to the cloud

When asked to hand off, move, or continue work in the cloud, commit and push first: the cloud sees only the pushed branch, so uncommitted work does not travel. Write a brief a fresh agent can start from, then run:

```bash
cockpit agents cloud claude --message-file /absolute/path/brief.md --cwd /absolute/path/checkout [--model MODEL] [--trust-cwd] [--dry-run]
cockpit agents cloud codex --message-file /absolute/path/brief.md --cwd /absolute/path/checkout [--dry-run]
```

It refuses an unpushed branch and warns about uncommitted changes. Run it directly rather than `claude --cloud`, which needs a real terminal. `--trust-cwd` lets a folder's hooks and MCP servers load in later local `claude` runs, so pass it only when the command reports `folder not trusted by the Claude CLI` and the user's handoff request covers that checkout. Exit 3 means `uncertain`: a session may exist, so check before retrying. The brief is visible in the host's process list while `claude` starts, so keep secrets out of it.

Report the `claude-cloud:…` or `codex-cloud:…` id and URL it prints. `show`, `send`, `resume`, and `sessions --harness` take those ids. A Codex Cloud task takes no follow-up, so `send` refuses it. `cockpit handbook agents` has environment setup and failures. For portable heavy commands, `cockpit resources run` has its own Codex Cloud route.

## Verify the result

For a T3 child or thread, read the thread: it records the provider and model. For a session T3 did not start, read the harness record, not the agent's self-report; `cockpit handbook linear/session-discipline` lists where each harness keeps it. An absent record means model unknown.

For an authorized issue receipt, refresh the issue's full body and comments through `cockpit linear issue ISSUE --json`, then post the work-log line with `cockpit linear comment`, in the format `session-discipline` gives. Keep credentials and prompt or transcript bodies out of receipts.

<!-- Adapted from Burooj's September 2026 T3 orchestration skill and local t3ctl workflow; T3's MCP tools now own delegation. -->

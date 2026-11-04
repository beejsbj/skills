---
name: cockpit-agents
description: Delegate to another agent or model under one rule - T3 is the orchestrator, so use its MCP tools (delegate_task for a piece of your task, including a review; T3 threads for an independent workstream) or `t3 thread` and T3's MCP sign-in from outside a T3 session. Use `cockpit agents` only for what T3 lacks - live availability, model receipts for the Linear work log, and persona sessions. Environment installation and upgrades follow the Cockpit handbook.
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

Everything below is for what T3 lacks: `options` when choosing a model, `receipt` for the Linear work-log line, and persona sessions. `cockpit agents run`, `create`, and `resume-limited` were removed on 2026-11-04, and `cockpit agents send` no longer takes T3 threads, which use `t3 thread send` or T3's MCP tools.

## Select the environment and route

Run Cockpit on the machine that owns the project files, harness credentials, and session. For remote work, resolve that machine's access guidance through `cockpit handbook` and use its documented connection. A T3 desktop connection does not synchronize files or make a remote checkout local.

```bash
cockpit agents options --intent work --json
cockpit agents projects
cockpit agents models --instance codex
cockpit agents threads --project PROJECT_ID
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

Keep the harness, exact session ID, and Hermes profile together when selecting a target. Bare IDs mean T3 threads. Use `show --messages` only when transcript access is needed and authorized; keep raw personal transcripts out of output and saved artifacts. Resolve refusals from observed state rather than bypassing guards.

## Cloud work

Codex Cloud and Claude cloud sessions are dispatched by hand, not through `cockpit agents`. Resolve `cockpit handbook bjslab/capabilities/harness-cloud`. For portable heavy commands, `cockpit resources run` still has a Codex Cloud route.

## Verify the result

For a T3 child or thread, read the thread: it records the provider and model. For a session T3 did not start, or for the Linear work-log line, read the harness record, not the agent's self-report:

```bash
cockpit agents receipt codex HARNESS_SESSION_ID --json
```

Use the underlying harness session ID, which may differ from the T3 thread ID. For an authorized issue receipt, refresh its full body and comments through `cockpit linear issue ISSUE --json`, then use `receipt` with `--issue`, `--role`, and `--outcome`. Report the target, IDs, model evidence, and work outcome separately; an absent harness record means model unknown. Keep credentials and prompt or transcript bodies out of receipts.

<!-- Adapted from Burooj's September 2026 T3 orchestration skill and local t3ctl workflow; T3's MCP tools now own delegation. -->

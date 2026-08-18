---
name: bjslab-context
description: Resolve bjslab Cockpit, agents, tools, and authority.
---

# Bjslab Context Skill

Resolve the current bjslab environment before guessing paths, capabilities, or execution routes. The command reports live facts and points into the bjslab handbook; it does not replace the handbook or authorize mutations.

## When to Use

Use this skill for work involving bjslab, Mac-to-bjslab boundaries, T3 Code, Hermes/Otto/Rose, Cockpit/Linear, Bitwarden Secrets Manager, OpenCodex, OpenCode, K3, DeepSeek, Terra/Luna, subagents, or uncertainty about which host or checkout owns something.

## Prerequisites

- Run on bjslab with the `terminal` tool.
- Prefer the installed commands. If installation drifted, invoke the scripts from `/mnt/server-ssd/BJsWorkspace/Projects/skills/bjslab-context/scripts/`.
- Treat `/home/admin/bjslab/AGENTS.md` as the handbook router. Read only the task-relevant files it names.

## How to Run

Start every matching task with:

```bash
bjslab-context
```

Then use the narrow view that matches the task:

```bash
bjslab-context agents
bjslab-context tools
bjslab-context handbook
bjslab-context doctor
```

## Quick Reference

| Need | Command |
| --- | --- |
| Environment and authority capsule | `bjslab-context` |
| K3, DeepSeek, Terra/Luna, OpenCode, Hermes routes | `bjslab-context agents` |
| Codex/OpenCodex worker | `codex exec -m <model> ...` |
| Installed wrappers and capability handles | `bjslab-context tools` |
| Handbook routing | `bjslab-context handbook` |
| Read-only installation and health checks | `bjslab-context doctor` |
| Linear/Cockpit | `bjslab-cockpit <command>` |
| Bitwarden Secrets Manager | `bjslab-bws <command>` |

## Procedure

1. Run `bjslab-context` before inferring the host, project root, or authoritative checkout.
2. Run the relevant narrow view. Prefer its live command/path over remembered transcript details.
3. Read the handbook route for operational context before bjslab service, T3, Hermes, backup, networking, or secret work.
4. Use `bjslab-cockpit` for Cockpit. It loads the app-actor environment without printing it and invokes the portable Python entrypoint.
5. Use `bjslab-bws` for BWS. It loads the protected machine token without placing the token in command arguments or output.
6. Delegate when another bounded pass would help. Run `bjslab-context agents` instead of asking Burooj how K3, DeepSeek, Terra, Luna, OpenCode, or Hermes are reached.
7. Resolve authority again before a mutation if the task crossed machines, checkouts, services, or providers.

## Pitfalls

- OpenCodex and Codex advertise at most five native subagent overrides. On the released Codex 0.148 runtime, bjslab's live sixth-model probe still returned `model not found`; rotate a frequent model into the five slots or launch a separate `codex exec -m <exact-id>` worker.
- Plain `codex exec` is the canonical headless worker. With OpenCodex WebSockets disabled, Codex may log an initial HTTP 426 and then fall back successfully to HTTP/SSE.
- The restricted Codex CLI sandbox on bjslab currently fails while creating its loopback namespace. Tool-using workers need the verified `-s danger-full-access` route, but only for work Burooj already authorized; constrain the worker with a narrow cwd, explicit scope, and validation.
- Use `opencode-go/kimi-k3` and `opencode-go/deepseek-v4-flash` for the featured routed workers. They remain Codex-harness subagents through OpenCodex; OpenCode Go is the upstream account, not the agent harness.
- Keep new sessions on OpenCodex v1 while native-to-routed v2 tasks arrive backend-encrypted. `ocx agent subagents set` currently restores the mode defaults, so re-run `ocx v2 mode v1` after changing the roster and verify with `ocx v2 status`.
- T3 Connect carries control and events. It does not mount or synchronize Mac files onto bjslab.
- A remembered path, old session cwd, issue body, or capability note can be stale. Verify the live owner before acting.
- The wrappers expose credentials only to their child process. Do not print their environment or replace them with inline tokens.
- Do not load the whole handbook. Follow the router from `AGENTS.md` and read the branch the task needs.

## Verification

Run:

```bash
bjslab-context doctor
bjslab-cockpit linear-doctor
bjslab-bws project list --output table
```

The doctor must identify host `bjslab`, find the handbook and wrappers, and report the preferred worker routes. Cockpit must report the app actor as healthy. The BWS check may list project metadata but must never print secret values.

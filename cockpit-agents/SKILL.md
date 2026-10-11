---
name: cockpit-agents
description: Delegate work, create or continue agent sessions, and verify model receipts through cockpit agents. Use for T3 threads and native Hermes, Codex, or Claude sessions; environment installation and upgrades follow the Cockpit handbook.
---

# Cockpit agents

Use `cockpit agents` as the session surface. A request to create or message a session authorizes that operation within the stated scope; skill discovery alone does not authorize new work. Resolve `cockpit handbook agents` for command details and recovery guidance. Inspect `cockpit agents --help` on the target machine before using a newly deployed command; if it is missing, report the deployment gap.

## Select the environment and route

Run Cockpit on the machine that owns the project files, harness credentials, and session. For remote work, resolve that machine's access guidance through `cockpit handbook` and use its documented connection. A T3 desktop connection does not synchronize files or make a remote checkout local.

```bash
cockpit agents options --intent work --json
cockpit agents projects
cockpit agents models --instance codex
cockpit agents threads --project PROJECT_ID
cockpit agents sessions --harness all --json
```

Use live `options` for route availability, account limits, and fallback order. Preserve requested models and effort; use [model-taste](../model-taste/SKILL.md) for unspecified choices. For independent judgment, use `--intent judgment` and [consult](../consult/SKILL.md). A catalog model is not necessarily an allowed native subagent override: check the tool's advertised choices.

Resolve a T3 project by workspace path and full ID, since grouped titles can repeat. Inspect model slugs and option descriptors on that server; `--instance` selects its configured provider instance. Native sessions use their own harness records. Keep the harness, exact session ID, and Hermes profile together when selecting a target; bare IDs retain T3 compatibility.

T3 commands discover the local server and use temporary authentication that is revoked on exit. `--base-dir` selects another T3 home. An explicit `--origin` needs that server's caller-owned `T3_AUTH_TOKEN`; pair it with `--expect-environment ID`. Keep tokens out of arguments and receipts. Remote T3 reads belong to the target server, not a local database substitute.

## Create or continue work

Write the exact prompt to a file. Choose access mode deliberately: automatic invocation does not imply `full-access`. T3 also supports `approval-required`, `auto-accept-edits`, and `auto`; choose from the authorized scope and provider policy.

```bash
cockpit agents create --project PROJECT_ID --title "Investigate the failing build" \
  --instance codex --model MODEL_SLUG --effort high \
  --runtime-mode full-access --worktree --base-branch main --branch agent/build-fix \
  --message-file /absolute/path/prompt.md
```

A fresh worktree needs a Git repository, an existing base ref, and a first prompt. Worktree failure must not fall back to the shared checkout. Add `--run-setup` only when the project's setup script should run; it is skipped by default. Keep canonical checkouts on their required branch.

For an existing worktree, use `--worktree-path /absolute/path --branch existing-branch`. Without worktree flags, the thread uses the project's checkout; `--branch` checks its branch and does not switch it. Omitting the message creates an empty real T3 thread without starting an agent, not a client-local Draft card. Omit effort when unsupported; `--option KEY=VALUE` selects other advertised options. Preserve namespaced model slugs.

```bash
cockpit agents show THREAD_ID
cockpit agents send t3:THREAD_ID --project EXPECTED_PROJECT_ID \
  --message-file /absolute/path/follow-up.md
cockpit agents send hermes:SESSION_ID --profile PROFILE \
  --message-file /absolute/path/follow-up.md
cockpit agents send codex:SESSION_ID --message-file /absolute/path/follow-up.md
cockpit agents send claude:SESSION_ID --message-file /absolute/path/follow-up.md
```

Inspect metadata before delivery. Use `show --messages` only when transcript access is needed and authorized; keep raw personal transcripts out of output and saved artifacts. Native resume flags and profile support follow the installed command's help; T3-specific model and checkout flags do not imply native-harness support.

T3 send inherits the thread's model, options, and modes. Explicit model/effort/option or mode overrides are persisted before the turn, subject to provider capabilities. An existing thread keeps its project and checkout; create another when either must change. Send checks the recorded branch against the actual checkout. Inspect an active turn before using `--allow-active` for steering or queueing; wait for it to finish before changing model or modes. Resolve refusals from observed state rather than bypassing guards.

Use `--dry-run` on create/send when choices need inspection; it is not an extra approval requirement. For a batch, keep an explicit mapping of prompt file to environment, project, and session, verify one intended delivery, then continue the authorized batch.

## Verify the result

T3 dispatch emits intent IDs and verifies the message and settings in the server projection. `prompt-recorded` proves delivery, not provider startup or completed work. Check session status and errors. On timeout or partial failure, inspect those same IDs with `show` before retrying: a bootstrap can persist a prompt before worktree preparation or provider startup. Uncertain delivery is not permission to create a replacement session. Never borrow another session for a smoke test.

Verify the actual model from its harness record, not the agent's self-report:

```bash
cockpit agents receipt codex HARNESS_SESSION_ID --json
```

Use the underlying harness session ID, which may differ from the T3 thread ID. For an authorized issue receipt, refresh its full body/comments through `cockpit linear issue ISSUE --json`, then use `receipt` with `--issue`, `--role`, and `--outcome`. Report verified target, IDs, model evidence, and work outcome separately; an absent harness record means model unknown. Keep credentials and prompt/transcript bodies out of receipts.

<!-- Adapted from Burooj's September 2026 T3 orchestration skill and local t3ctl workflow; Cockpit now owns the session interface and transport. -->

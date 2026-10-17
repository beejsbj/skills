---
name: cockpit-agents
description: Delegate work through cockpit agents - run a one-shot native job as a cross-provider subagent for work that is part of your task but needs another provider or model (it writes in your work branch by default; --read-only for a review, consult, or scout); create or continue a T3 thread only for an independent workstream to watch or steer; verify model receipts. Use for native Codex, Claude, or Hermes jobs and T3 threads; environment installation and upgrades follow the Cockpit handbook.
---

# Cockpit agents

Use `cockpit agents` as the delegation surface. A request to run, create, or message a session authorizes that operation within the stated scope; skill discovery alone does not authorize new work. Resolve `cockpit handbook agents` for command details and recovery guidance. Inspect `cockpit agents --help` on the target machine before using a newly deployed command; if it is missing, report the deployment gap.

## Subagent, job, or thread

Decide the shape before the route:

- **Your own subagent tool** (Claude's Agent tool, Codex `spawn_agent`, Hermes `delegate_task`) when the work is part of your task and your own harness and model are right for it.
- **A job** (`cockpit agents run`) when the work is still part of your task but needs another provider or model: Cockpit's cross-provider subagent. It runs the route's native CLI once, holds no T3 thread, shows nothing in the sidebar, and leaves an answer file plus a native session id that `receipt` proves. Like a subagent it writes in your checkout by default; judgments (reviews, consults, second opinions, scouts; every `--intent judgment` dispatch) pass `--read-only`.
- **A T3 thread or session** (`cockpit agents create`) only for an independent workstream Burooj may want to watch, steer, or keep in his sidebar: visible, steerable, kept in history, and holding a provider process until archived.

`options` shows each route's shape in its `via` column (`run`, `run+create`, `native`); `create` nudges toward `run` when a thread reads as a review, and never refuses.

## Select the environment and route

Run Cockpit on the machine that owns the project files, harness credentials, and session. For remote work, resolve that machine's access guidance through `cockpit handbook` and use its documented connection. A T3 desktop connection does not synchronize files or make a remote checkout local.

```bash
cockpit agents options --intent work --json
cockpit agents projects
cockpit agents models --instance codex
cockpit agents threads --project PROJECT_ID
cockpit agents sessions --harness all --json
```

Use live `options` for route availability, account limits, and fallback order. Preserve requested models and effort; use [model-taste](../model-taste/SKILL.md) for unspecified choices. For independent judgment, use `--intent judgment` and [consult](../consult/SKILL.md); those routes run as jobs. A `native` route is your own subagent tool (Agent tool, `spawn_agent`, `delegate_task`), used from inside your session, not through Cockpit; a catalog model is not necessarily an allowed override there, so check the tool's advertised choices.

## Run a job

Write the exact brief to a file, pick a `run` route from `options`, and pass the checkout as `--cwd`. A job has two modes.

**Write, the default**, for an implementation piece of your task, briefed like a subagent and run in your own work branch:

```bash
cockpit agents run claude:claude-sonnet-5-5 --cwd /absolute/path/your-worktree \
  --message-file /absolute/path/brief.md
cockpit agents run --status RUN_ID        # mode, branch, tree before and after, files touched, commits, diff summary
```

Claude gets `--permission-mode bypassPermissions` and Codex `-s danger-full-access` (the only sandbox that runs on bjslab); Hermes has no switch, its toolsets decide and the receipt says whether they write. `--write` is accepted as an explicit alias. Your feature worktree may be dirty with your own work: the receipt records the tree before and after and lists the files the job `touched`, comparing dirty files by content. A write job is refused only in the canonical cockpit checkout, on a detached HEAD, and on the default branch; the refusal names both ways out (a work branch, or `--read-only`). Brief the files, the change, and what done looks like; leave those files alone until the job finishes, since anything written to the tree meanwhile counts as touched; then review its piece before building on it.

**`--read-only`, for every judgment** (review, consult, second opinion, scout). It skips the checkout guard, so a review may run against any checkout or branch, the canonical one included:

```bash
cockpit agents run codex:gpt-6-astra --read-only --message-file /absolute/path/brief.md \
  --cwd /absolute/path/checkout --effort high [--background]
cockpit agents run --resume codex:SESSION_ID --read-only --message-file /absolute/path/followup.md
```

Pass `--read-only` on a judgment's `--resume` too: the mode is per run. Claude enforces it with denied edits; Codex with `-s read-only` where user namespaces work. Elsewhere (Codex on bjslab, Hermes, OpenCode, agy) Cockpit prepends a read-only preamble to the brief, and the receipt's `mode` row says `by brief only`. In a Git checkout the receipt compares the tree and shows a `VIOLATION` row if anything git can see changed while the job ran (ignored paths and files outside the checkout are not seen; outside Git nothing is checked). Cloud routes take no `--read-only`: a cloud job is a writing agent, so pick a local route for a judgment.

The receipt names the output file, the native session (`codex:…`, `claude:…`, `hermes:…`), the exact `receipt` command, and the exit status. `--background` returns at once; read `--status` until it is `done`, `failed`, `timeout`, `deferred`, or `lost` (`queued` and `running` are still on their way). `--resume` continues in the same context through the harness's own resume, under the same checkout and ownership checks as `send`. Read the answer from `output.md`; the record in `run.json` carries no credentials.

Where `cockpit agents run --status` with no run id prints a `jobs` line (the agent guard is deployed; older builds reject the bare flag), every job is bounded and counted. On bjslab it runs in its own scope under `app-t3agents.slice` (2G per job, no swap; the receipt's `scope` line names it), and at most four jobs run on the host at once, yours and every other session's, background ones included. Over the limit your run waits its turn (`queued`, with its position) and after `--wait` seconds (default 900) is `deferred`, exit 75, with nothing started: wait and retry, or raise `--wait`; do not reach for `--unbounded` to jump the queue. If the run refuses because the slice has no finite budget or the user bus is unreachable, report that as an environment gap; `--unbounded` runs in your own cgroup and the receipt says so, so use it only when the user accepts that. `cockpit agents run --status` with no id shows the slots, holders and waiters. The four slots also bound your fan-out: extra jobs queue rather than fail, so launch the jobs a pass needs, collect them, then launch more; two reviewers per pass already take half the host's slots. Each bounded job is told the bjslab heavy-work rule at launch (the same text T3 sessions get), so a job that needs a build or test suite routes it through `cockpit resources run`.

Resolve a T3 project by workspace path and full ID, since grouped titles can repeat. Inspect model slugs and option descriptors on that server; `--instance` selects its configured provider instance. Native sessions use their own harness records. Keep the harness, exact session ID, and Hermes profile together when selecting a target; bare IDs retain T3 compatibility.

T3 commands discover the local server and use temporary authentication that is revoked on exit. `--base-dir` selects another T3 home. An explicit `--origin` needs that server's caller-owned `T3_AUTH_TOKEN`; pair it with `--expect-environment ID`. Keep tokens out of arguments and receipts. Remote T3 reads belong to the target server, not a local database substitute.

## Create or continue a thread

For work the user will watch or steer, write the exact prompt to a file. Choose access mode deliberately: automatic invocation does not imply `full-access`. T3 also supports `approval-required`, `auto-accept-edits`, and `auto`; choose from the authorized scope and provider policy.

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

Use the underlying harness session ID, which may differ from the T3 thread ID; a job's receipt prints it ready to paste. For an authorized issue receipt, refresh its full body/comments through `cockpit linear issue ISSUE --json`, then use `receipt` with `--issue`, `--role`, and `--outcome`. Report verified target, IDs, model evidence, and work outcome separately; an absent harness record means model unknown. Keep credentials and prompt/transcript bodies out of receipts.

<!-- Adapted from Burooj's September 2026 T3 orchestration skill and local t3ctl workflow; Cockpit now owns the session interface and transport. -->

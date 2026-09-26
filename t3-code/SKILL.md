---
name: t3-code
description: Create and message T3 Code threads, inspect sessions, and choose their environment, project, model, effort, branch, or worktree. Use when delegating work into T3 sessions or continuing an existing T3 thread. Excludes implementing T3 itself and server installation or upgrades.
---

# T3 Code

Use the bundled helper to operate real T3 threads through the running server. It works from Codex and Claude and is available for automatic agent invocation. A request to create or message threads authorizes that operation within the user's stated scope; carry it through without asking for the same permission again. Loading this skill alone does not authorize unrelated sessions or prompts.

## Locate the target

A T3 environment is the machine that owns the project files, server, providers, and threads. Run the helper on that machine. On bjslab, resolve `cockpit handbook bjslab capabilities/t3-code.md` for environment and service guidance. For a remote machine, use its documented SSH route and run its installed skill there. A connected desktop client does not make every environment accessible from the current shell.

Set `T3CTL` to this skill's `scripts/t3ctl.mjs` (resolve it from the skill path, not the current repository). It requires Node 22.16+ and has no package dependencies:

```bash
node "$T3CTL" projects
node "$T3CTL" models --instance codex
node "$T3CTL" threads --project PROJECT_ID
```

Every result identifies the server and environment. Resolve the project by its workspace path and full ID. Titles may repeat when T3 groups multiple physical projects under one repository. Inspect model slugs and option descriptors on this server; `instanceId` identifies the configured harness/provider instance. Preserve requested models and effort; use the adjacent `model-taste` skill when making an unspecified choice.

The helper discovers the local server and installed CLI from the selected T3 home, issues a temporary auth session, and revokes it on exit. `--base-dir` selects a different T3 home. An explicit `--origin` requires `T3_AUTH_TOKEN` for that server; use `--expect-environment ID` to check its identity. Remote reads come from the target server, never a local SQLite surrogate. Keep tokens out of arguments, printed output, and saved plans.

## Create or continue

Write the exact prompt to a file. Choose the project, provider/model, access mode, and checkout using the request and known context. Choose `--runtime-mode` deliberately: `full-access` allows autonomous execution; `approval-required`, `auto-accept-edits`, and `auto` use the corresponding T3 provider policy. Automatic skill invocation does not imply full access.

Create a thread in the project's current checkout and send its first prompt:

```bash
node "$T3CTL" create --project PROJECT_ID --title "Investigate the failing build" \
  --instance codex --model MODEL_SLUG --effort high \
  --runtime-mode full-access --message-file /absolute/path/prompt.md
```

Omit `--message-file` to create an empty real thread without starting an agent. T3's client-local Draft cards are separate; this helper creates server threads. Omit effort if the model does not expose it. `--option KEY=VALUE` selects other advertised options, including boolean values. Keep model slugs intact, including any `/` characters.

Choose where the new thread works:

| Intended checkout | Arguments |
| --- | --- |
| Project's existing checkout | No worktree flag. Optional `--branch main` checks the current branch; it does not switch it. |
| Fresh worktree and branch | `--worktree --base-branch main --branch agent/build-fix` with a first prompt. T3 prepares it before running the agent. |
| Existing worktree | `--worktree-path /absolute/path --branch existing-branch`, running the helper on the owning machine. It verifies the path belongs to the project's Git repository. |

Fresh worktrees require a Git repository and a base ref with a commit. The helper requires successful worktree creation rather than falling back to the shared checkout. Add `--run-setup` when the project's configured setup script should run. Without it, setup is skipped. A new branch name on its own does not create or check out that branch.

Continue a thread by its exact ID:

```bash
node "$T3CTL" show THREAD_ID --messages
node "$T3CTL" send THREAD_ID --project EXPECTED_PROJECT_ID \
  --message-file /absolute/path/follow-up.md
```

Sending inherits the thread's model, options, and modes. To change its model or effort, use `--instance`, `--model`, `--effort`, or `--option`; the helper saves the selection before starting the turn, subject to provider capabilities. Explicit mode overrides use T3's mode-setting commands before the turn. An existing thread keeps its project and checkout; start a new one when those must change. The helper checks that the checkout is still on the thread's recorded branch. Inspect an active turn before using `--allow-active`, which allows the provider's steering or queueing behavior with its existing settings; wait for it to finish before changing model or modes.

For batches, keep one explicit mapping from prompt file to environment, project, and thread. Start with one intended thread, verify its receipt, then continue the authorized batch. Use `--dry-run` on create/send when target choices need inspection: it reports the planned settings and prompt hash without dispatching thread commands. It is a convenience, not a required approval step.

## Verify delivery

The helper emits an intent containing thread, message, and command IDs before dispatch, then checks the server's thread projection for the exact prompt and selected settings. Report the IDs and verified target to the user. `prompt-recorded` means the command was accepted and the message was found; it does not mean the agent finished or its provider started successfully. Inspect the returned session status and any error.

On a timeout or partial failure, inspect those same IDs with `show`. A bootstrap can persist the prompt before preparing the worktree or starting the provider. Reconcile the observed state before retrying; blindly repeating `create` can leave duplicate sessions. Never reuse another thread as a delivery smoke test.

Read [references/protocol.md](references/protocol.md) only when debugging protocol changes, missing capabilities, or a partial dispatch. Server upgrades and auth/pairing changes follow the environment's handbook.

<!-- Origin: Burooj's September 2026 T3 orchestration workflow and local t3ctl prototype. Protocol verified against beejsbj/t3code, packages/contracts and apps/server; the helper replaces the prototype's version pins and client-local database lookups. -->

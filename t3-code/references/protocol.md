# T3 command contract

Verified against Burooj's T3 Code fork (`beejsbj/t3code`, build 0.0.42, September 2026). The running server and its matching source are authoritative after an upgrade. Inspect `packages/contracts/src/{orchestration,rpc,environmentHttp,model,git}.ts` and `apps/server/src/ws.ts` in the fork when a contract changes. On bjslab, resolve the checkout and runtime through the handbook; do not pin a version directory into callers.

## Transport and environment

`~/.t3/userdata/server-runtime.json` supplies the local origin. The CLI may be outside PATH: `~/.t3/runtime/service-state.json` identifies `activeVersion`, whose executable is `runtime/versions/<version>/t3`. Older installations may use `node_modules/t3/dist/bin.mjs` there.

The helper captures `t3 auth session issue --base-dir <home> --ttl 10m --label t3-code-skill --json` privately, and revokes the returned session ID in `finally`. A caller-supplied `T3_AUTH_TOKEN` is owned by the caller. The helper never prints auth material and refuses authenticated HTTP redirects.

Read `/.well-known/t3/environment` for public identity, `/api/orchestration/snapshot` for project and thread metadata, and `/api/orchestration/threads/<id>` for one thread's details. Provider catalogs and model option descriptors come from RPC `server.getConfig` with `{}`; do not dump that whole configuration into receipts.

For RPC, POST `/api/auth/websocket-ticket` with the bearer token. Connect to the same origin's `/ws?wsTicket=<ticket>&orchestrationProtocol=1`. The Effect RPC envelope is:

```json
{
  "_tag": "Request",
  "id": "REQUEST_UUID",
  "tag": "orchestration.dispatchCommand",
  "payload": { "type": "thread.create", "commandId": "COMMAND_UUID" },
  "headers": []
}
```

This envelope illustrates framing only; the command needs its full fields below. Match the `requestId` on an `Exit` response. `exit._tag: Success` contains the receipt; `Failure`, `Defect`, disconnect, or timeout must not become a success. No automatic mutation retries.

Both HTTP `/api/orchestration/dispatch` and WebSocket dispatch accept orchestration commands, but this build's **worktree/bootstrap preparation lives in the WebSocket handler**. Use WebSocket for `thread.turn.start` with `bootstrap`; sending that payload straight to the HTTP engine does not run the preparation flow.

## Commands

`thread.create` needs `commandId`, `threadId`, `projectId`, `title`, `modelSelection`, `runtimeMode`, `interactionMode`, `branch`, `worktreePath`, and ISO `createdAt`. It creates a real empty thread; it does not start an agent. The two checkout fields describe an actual checkout, so assigning a branch string alone is not Git checkout.

`thread.turn.start` needs a new command ID, the target thread ID, ISO timestamp, modes, and a message:

```json
{
  "messageId": "MESSAGE_UUID",
  "role": "user",
  "text": "Exact prompt text",
  "attachments": []
}
```

For a new thread, include `bootstrap.createThread` with the create metadata above (without type/commandId/threadId). For a new worktree, also include:

```json
{
  "prepareWorktree": {
    "projectCwd": "/path/on/target/machine",
    "baseBranch": "main",
    "branch": "agent/build-fix",
    "requireWorktree": true
  },
  "runSetupScript": false
}
```

These are fields inside `bootstrap`. The bootstrap may persist a thread and its user message before preparation completes. Success is not atomic across all side effects; inspect the thread and worktree after a lost reply. The helper does not auto-delete partial results.

For an existing thread, omit `bootstrap` and preserve its access/interaction settings unless deliberately changing them via `thread.runtime-mode.set` or `thread.interaction-mode.set`. Merely placing different mode strings on `thread.turn.start` does not change existing thread settings in this build. To persist a changed model or effort in the thread's selection, first use `thread.meta.update` with `modelSelection`, then send the same selection on the turn command.

`modelSelection` is `{instanceId, model, options?: [{id, value}]}`. The provider catalog determines option names and values: Codex commonly advertises `reasoningEffort`; Claude commonly advertises `effort`. Some providers expose `variant` instead. Preserve namespaced model slugs. Do not infer live availability from an old thread's model or a static roster.

## Recovery

Compare the receipt's environment, project ID, thread ID, message ID/hash, selected model/options, and branch/worktree with a fresh thread read. A recorded message with no completed turn is not proof of agent execution. A timeout after dispatch is uncertain delivery, even if the client exits nonzero.

For a bootstrap that persisted the message, T3's internal `thread.message.user.append` records without starting a turn; a later `thread.turn.start` can reference the same message ID. This is a recovery detail, not an editable Draft card. Inspect the server's state and error before choosing a recovery command. Stop if the state cannot distinguish already-started work from a missing send; report the exact IDs instead of creating replacements.

Only the server API mutates T3 state. SQLite may be inspected read-only during diagnosis; it is not an editing surface. Remote environments must use their own server, project IDs, provider catalog, and filesystem paths. Changing an endpoint while reading another environment's database can silently misroute work.

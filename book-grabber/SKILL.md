---
name: book-grabber
description: "Safely operate the bjslab book-grabber CLI: inspect health and local reading state, search the configured private source, interpret JSON envelopes, and perform explicitly authorized grabs or queue/list changes. Use for book-grabber availability, book searches, requested downloads, wanted/not-found/failed lists, or its bjslab service."
---

# Book Grabber

Operate the installed `book-grabber` command on bjslab. Its private-source session is ASN-bound to bjslab, so run network-facing commands there, never from the Mac itself.

## Safety gate

Treat these as read-only: `health`, `search`, `history`, and `queue|not-found|failed list`.

Obtain explicit user authorization before `grab`, `queue add`, `not-found add|remove`, `failed remove`, or any service change (including `serve`). A search result is not authorization to grab it; confirm the exact source ID and item first.

Keep credentials out of both commands and reports. Never read, print, or relay environment values, cookies, passwords, or configuration files. Do not infer or reveal session details.

## JSON discipline

For every non-service command, include `--json`, capture stdout, and parse the single JSON object. Do not scrape formatted or human-oriented output; regard stderr only as a diagnostic channel.

Check the envelope before using `data`:

```text
schemaVersion: "1"
ok: true | false
command: command name
data: present on success
error: { code, message, retryable } on failure
```

On failure, report the code and a concise sanitized message. Exit codes are: `2` arguments, `3` configuration, `4` authentication, `5` upstream, `6` qBittorrent, `7` state, and `8` internal. Retry only a clearly transient failure (`retryable: true`) and only within the already-authorized scope.

Keep help text out of this skill. For option drift, refer to the installed command's `--help` when that version provides it; otherwise treat the current CLI contract as authoritative.

## Read-only workflows

Run a health check:

```bash
book-grabber health --json
```

Search with a user-supplied placeholder query and optional non-negative page:

```bash
book-grabber search '<query>' --page 0 --json
```

Read local state:

```bash
book-grabber history --json
book-grabber queue list --json
book-grabber not-found list --json
book-grabber failed list --json
```

Interpret search `data.results` as candidates. Use each result's `sourceId` only after the user chooses it. `history` records accepted handoffs; it is not proof that a download completed. List results are the stored entries for that state category.

From a Mac, run the read only command remotely and still parse its stdout as JSON:

```bash
ssh -T admin@bjslab 'book-grabber search "<query>" --page 0 --json'
```

## Authorized changes

After the user explicitly identifies a selected `sourceId`, hand it to qBittorrent:

```bash
book-grabber grab '<source-id>' --json
```

Success with `data.accepted: true` means the handoff was accepted, not that content is complete. Report that distinction and use read-only history only if the user asks for a follow-up check.

After explicit authorization, record a deliberately stated entry:

```bash
book-grabber queue add '<book or request>' --json
book-grabber not-found add '<book or request>' --json
book-grabber not-found remove '<exact entry>' --json
book-grabber failed remove '<exact entry>' --json
```

Confirm the intended category and exact text before mutating it. Do not start, stop, bind, reconfigure, or otherwise change the service without a separate explicit authorization.

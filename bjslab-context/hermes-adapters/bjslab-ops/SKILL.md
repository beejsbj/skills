---
name: bjslab-ops
description: Route bjslab operations through the canonical handbook.
---

# Bjslab Operations Adapter

Use the current bjslab handbook and live context command for server work. This adapter replaces an OpenClaw-era copy; it grants no additional mutation authority.

## How to Run

Use the `terminal` tool:

```bash
bjslab-context
bjslab-context handbook
```

Read `/mnt/server-ssd/BJsWorkspace/Projects/bjslab/AGENTS.md` first, then only the task-relevant map, runbook, or capability file it names. Verify live host, authority, backup posture, and current config before a persistent change.

## Pitfalls

- `/home/admin/.openclaw` is retired archive lineage, not a live context or tooling root.
- Hermes is a resident assistant and bjslab tenant, not the homelab control-plane authority.
- A remembered path or old session cwd is evidence to verify, not authority.

## Verification

`bjslab-context doctor` must pass before relying on the installed routes.

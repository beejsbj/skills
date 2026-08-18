---
name: cockpit-linear-board
description: Route bjslab Cockpit through the canonical wrapper.
---

# Cockpit / Linear Board Adapter

Resolve bjslab authority through `bjslab-context`, then use the shared Cockpit source. This adapter carries no board ontology or credentials.

## How to Run

Use the `terminal` tool:

```bash
bjslab-context
bjslab-cockpit linear-doctor
bjslab-cockpit status
bjslab-cockpit issue BJS-XXX
```

Read `/mnt/server-ssd/BJsWorkspace/Projects/skills/cockpit/SKILL.md` before board writes or orchestration. Use `bjslab-cockpit` for every command; it loads the app-actor environment and invokes the server-compatible Python entrypoint.

## Pitfalls

- `/home/admin/Projects/skills` and `/Users/burooj/Projects/cockpit` are not bjslab command roots.
- Never print or manually reproduce the Cockpit credential environment.
- Board state is live; verify the issue before acting.

## Verification

`bjslab-cockpit linear-doctor` must report `app actor: OK (cockpit)`.

---
name: tududi
description: "Manage Burooj's life admin in tududi through its native MCP: tasks, inbox, projects, areas, habits, goals, and notes. Use for personal tasks or a requested braindump; project implementation and Cockpit issues remain in Linear."
---

# tududi

Use the configured `tududi` MCP server. It connects to the private instance at
`https://tududi.burooj.dev/api/mcp`; discover current tool schemas from the server.
The host needs LAN or Tailscale access. On another machine, use the documented
bjslab SSH route; credentials stay on bjslab.

Start from the relevant existing records. Preserve task/project IDs and links;
use the user's dates and timezone (America/Toronto). An uncertain deadline is a
question, not an invented due date. A requested interview can capture rough items
in the inbox before organizing them with the user.

Perform the requested changes within the current task's authorization. A request
to inspect tasks does not authorize completing or deleting them. Loading this
skill alone does not authorize imports, bulk migration, recurring jobs, or
notifications. Life-admin population starts with the owner's interview; a service
installation is not a reason to copy the Linear board.

Memry remains the writing/thinking space; its integration is deferred. Keep links
when useful, rather than duplicating entire notes. Donetick is retired.

## Current trial

Burooj chose to try the existing tududi instance on 2026-10-03. New personal
life-admin captures go into its Inbox; sort them into actions after the owner
clarifies what is current. Historical issue suggestions remain candidates until
confirmed. Areas organize practical administration; keep the broader ecology
and its seasonal states in the writing/thinking space.

Otto is the default planning steward for this trial when planning is requested;
the owner can name another agent. Other agents capture or perform the particular
changes requested. Before changing shared organization, read the current records
and preserve concurrent edits. Weekly triage is an owner-invoked review; a
cadence in these instructions does not create a scheduled job.

Stage at most five discretionary actions, with genuine dated obligations visible
separately. Habit floors retain their chosen thresholds and Wake/Day/Sleep
anchors. Record completions and declared skips as they happened; returning after
absence does not require repairing missed days. Prefer archiving when parking
work; deleting or changing habit history requires the owner's specific request.

The app's Doing view uses a daily plan separate from the task's `today` flag.
Discover plan tools before staging; if MCP still lacks them, use the supported
daily-plan HTTP API with the existing protected credential loader. Preserve the
current plan's items rather than replacing it from an old snapshot. Planning
suggestions currently select active-project tasks; loose actions can be selected
explicitly, and genuinely due tasks remain visible. Phone reminder delivery is
pending the owner's channel choice; a recorded date is not proof of delivery.

The MCP adapter reads the protected host credential file at startup. Use the
configured server rather than displaying the token or placing it in command
arguments. If discovery fails, inspect the MCP connection status and private
reachability. Token expiry is an authentication problem, not permission to mint a
replacement automatically.

<!-- Native transport: https://github.com/chrisvel/tududi; local deployment and
agent access authorized by Burooj on 2026-09-30. -->

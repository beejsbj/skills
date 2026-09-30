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

The MCP adapter reads the protected host credential file at startup. Use the
configured server rather than displaying the token or placing it in command
arguments. If discovery fails, inspect the MCP connection status and private
reachability. Token expiry is an authentication problem, not permission to mint a
replacement automatically.

<!-- Native transport: https://github.com/chrisvel/tududi; local deployment and
agent access authorized by Burooj on 2026-09-30. -->

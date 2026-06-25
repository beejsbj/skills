# Linear Discipline (cockpit reference)

Board ontology, lane meanings, label taxonomy, issue body shape, and comment model live in the `linear` skill. Cockpit **depends on** that skill; do not restate those rules here.

This file covers only cockpit's own write-surface and session-binding mechanics.

---

## Write Auth

Cockpit's write system is intentionally app-authored:

- Preferred: set `COCKPIT_LINEAR_APP_ACCESS_TOKEN` to an OAuth access token created with `actor=app`.
- Local/server-friendly: set `COCKPIT_LINEAR_APP_CLIENT_ID` and `COCKPIT_LINEAR_APP_CLIENT_SECRET`; cockpit will fetch a client-credentials app token with `read,write,comments:create` scope.
- Mac-local: put the non-secret client id and Keychain service name in `.linear.toml`; store the client secret in macOS Keychain under that service.
- Optional display override: set `COCKPIT_LINEAR_COMMENT_CREATE_AS_USER` and `COCKPIT_LINEAR_COMMENT_DISPLAY_ICON_URL` when the app comment should show a provider-specific name or icon.
- Emergency only: set `COCKPIT_ALLOW_PERSONAL_LINEAR_WRITES=1` to permit the old personal-auth CLI write path.

Run `./cockpit.py linear-doctor` after changing credentials. It should report `write actor: app OK`.

---

## Session Binding

Bind sessions through Linear labels, not a cockpit table:

```bash
./cockpit.py bind BJS-123 codex <session-id>
./cockpit.py bind BJS-123 session:claude:<session-id>
./cockpit.py release BJS-123
./cockpit.py done BJS-123
```

Invariants:

- One active issue should have at most one `session:*` label.
- `session:*` labels belong only on active statuses (`In Progress`, `Grilling`).
- Done, canceled, and inbox issues should have no `session:*` labels.
- Issue comments carry binding/release receipts and the work trail.
- Cockpit writes must use the app-actor token so comments, status moves, and label activity are authored by the Cockpit app, not by Burooj's personal account.
- `done` moves the issue to `Done`, removes `session:*` labels, and archives provider sessions where possible.

Run `./cockpit.py audit` to find drift.

---

## Comment Writes

Use cockpit commands for all comment writes and resolution so authorship stays on the Cockpit app actor:

```bash
./cockpit.py comment BJS-123 "Progress update, blocker, discovered work, or receipt."
./cockpit.py comment BJS-123 --reply-to <comment-id> "Reply body."
./cockpit.py comment-resolve <comment-id>
./cockpit.py comment-unresolve <comment-id>
```

Routine receipts and updates live as replies under the single **Cockpit Thread** top-level comment per issue. `comment`, `bind`, `release`, and `done` create or reuse that thread automatically.

Questions for Burooj live in a dedicated **Questions** top-level comment thread (one per issue). Each question is a reply under it — not a checkbox in the issue body. Cockpit creates/reuses this thread when adding a question.

Resolution rule: reply before resolving; resolve only when the reply says what closed it.

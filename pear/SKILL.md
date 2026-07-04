---
name: pear
description: Use Pear/Holepunch guidance when Codex is evaluating or building local-first, peer-to-peer, offline-capable, serverless, or decentralized personal tools; syncing data between devices such as Mac and bjslab; using Hypercore, Corestore, Hyperbee, Hyperdrive, Hyperblobs, Hyperswarm, Bare, or pear:// app distribution; deciding whether an idea should use P2P replication instead of a central server, cloud sync, Syncthing, Git, Nostr, or blockchain.
---

# Pear

Pear is the default P2P/local-first option to consider when the real problem is replication, offline continuity, app distribution, or peer availability without a central server.

## First Judgment

Ask what problem Pear would solve.

- Use Pear when the pain is multi-device sync, offline-first continuity, peer discovery, peer-to-peer app delivery, append-only logs, shared files, or reducing dependence on a hosted server.
- Do not use Pear just because the idea says "decentralized." If the actual problem is a normal hosted CRUD app, a simple local file, a Git repo, or a one-machine CLI, keep it simpler.
- Do not confuse Pear with blockchain. Pear handles peer replication and P2P app/runtime distribution. Blockchain handles public settlement, adversarial shared state, public timestamping, payments, and cross-party trust.
- Prefer a reversible spike before making Pear canonical for a project.

## Burooj Defaults

Use these defaults unless the project proves otherwise:

- Treat bjslab as an availability peer or always-on seed, not as unquestioned authority.
- Keep user-owned source data local and plain where possible.
- Keep indexes rebuildable from canonical data.
- Prefer append-only logs and content-addressed assets before attempting mutable multi-writer file sync.
- Keep secrets, tokens, and private keys outside replicated stores unless explicitly encrypted and intentionally shared.
- Make conflict behavior visible to Burooj before using Pear for mutable notes, drafts, or vaults.

## Fit Patterns

Strong fits:

- Mac to bjslab replication for personal tools.
- Chat archives, agent receipts, capture feeds, and append-only memory/action logs.
- Local-first apps that should keep working offline and sync later.
- P2P file or media availability where a peer can stay online.
- Small desktop/terminal apps that benefit from pear:// distribution.

Maybe fits:

- Obsidian-adjacent workflows. Prefer Pear for an append-only feed that writes into a vault, not automatic whole-vault sync, until conflict rules are proven.
- Writing assistants. Use Pear for source replication and trace logs; keep editor state simple.
- Skill/research/demo apps. Use Pear when the demo's point is local-first or peer-to-peer behavior.

Weak fits:

- Marketing sites, dashboards, ordinary frontend apps, and one-off prototypes with no sync/offline need.
- Private notes where Syncthing, Git, or local backups already solve the problem cleanly.
- Anything whose real requirement is public payment, marketplace trust, or tokenized ownership. Consider blockchain/Nostr/payment protocols separately.

## Architecture Heuristic

Prefer this shape:

```text
capture or edit event
  -> signed/content-addressed append-only record
  -> Pear/Corestore/Hypercore replication
  -> local rebuildable indexes/views
  -> human surfaces such as Obsidian, chat-scrobbler, cockpit, or a writing UI
```

Avoid this shape:

```text
mutable app database
  -> unclear merge rules
  -> replicated everywhere
  -> no human-visible recovery path
```

## Project Notes

For chat-scrobbler-style systems, replicate canonical session JSON and assets; rebuild SQLite/vector indexes on each machine.

For Obsidian-style systems, start with a replicated append-only feed of snippets, citations, edits, and receipts. Generate or append markdown deliberately rather than syncing the entire vault first.

For agent systems, use Pear for transport and availability, then use signing keys or delegated session keys for identity and provenance. A key can prove which agent/session signed a message; it does not make the agent accountable by itself.

For blockchain or Nostr ideas, separate layers:

- Pear: private/local-first replication and app distribution.
- Nostr: signed public/relay event distribution and lightweight identity.
- Blockchain: settlement, public commitments, payments, and adversarial shared state.

Use the smallest layer that actually matches the claim.

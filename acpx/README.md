# acpx (adapted skill)

Adapted from the official skill for [openclaw/acpx](https://github.com/openclaw/acpx) — the headless ACP client CLI (MIT; imported at acpx 0.11.2, 2026-07-03). All credit upstream.

No longer a verbatim vendored copy: local additions are the "Model taste (local)" section, `profiles.json` (Burooj's model roster), and machine notes (`bunx --bun`, adapter status). Do **not** blind-refresh from upstream — merge upstream changes manually so the local sections survive.

The `cockpit` skill owns dispatch policy (executor classes, briefs); this skill owns how to reach models over ACP.

# acpx (adapted skill)

Adapted from the official skill for [openclaw/acpx](https://github.com/openclaw/acpx) — the headless ACP client CLI (MIT; imported at acpx 0.11.2, 2026-07-03). All credit upstream.

No longer a verbatim vendored copy: local additions are the "Model taste (local)" section, `profiles.json` (Burooj's model roster, executor classes, and source-dated cost metadata), and machine notes (`bunx --bun`, adapter status). Do **not** blind-refresh from upstream — merge upstream changes manually so the local sections survive.

The roster follows the same broad pattern as machine-readable catalogs such as OpenRouter's Models API and Google's Gemini Models endpoint — stable model id plus capability/pricing metadata — then adds Burooj's subjective `good_for`, `avoid_for`, and executor-class judgments. Costs are intentionally heterogeneous: exact per-token prices where the provider or access route publishes them, subscription price/access notes where it does not. Dispatch surfaces stay outside the model records because the same model may be reached through Codex CLI, OpenCode CLI, Hermes, or another compatible harness.

The `cockpit` skill owns dispatch policy (executor classes, briefs); this skill owns how to reach models over ACP.

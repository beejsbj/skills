---
name: agents
description: Give the current agent access to other models and providers — a second opinion from a different model, a cheap codex/opencode pass to save premium tokens, a durable cross-provider session, or choosing which model fits a task. Use when the user names a provider or model (claude, codex, opencode, cursor, gemini, opus, sonnet, haiku, kimi, glm, composer) or asks to hand work to another model. Not for Codex Desktop threads, harness-native subagents, or session-ledger topology — cockpit owns those.
---

# Agents

One job: reach **other models** from the current session. Decide which model, then which pipe.

Session topology — discovery, binding, lifecycle truth — belongs to the `cockpit` skill. Harness-native subagents stay native. Codex Desktop threads stay on the Desktop's own thread tools.

## Which model

`profiles.json` beside this file is the roster: per provider/model, what it is good for, what to avoid, default effort.

Burooj's standing preference: spend premium tokens on judgment, not legwork. Scouting, extraction, classification, and bulk passes go to codex or opencode-go models; deep architecture, hard review, and taste calls go to opus-class. Use the user's named model exactly when given.

## Which pipe

1. **acpx — preferred.** The ACP control plane: one structured command surface for claude, codex, gemini, pi, and openclaw agents. Read the `acpx` skill for mechanics (sessions, exec, queueing, permissions, flows).
   - This Mac: the default node is v16 (too old) — invoke as `bunx --bun acpx …`, and put global flags **before** the agent subcommand.
   - Verified 2026-07-03: `bunx --bun acpx --approve-reads --timeout 90 claude exec "…"` round-trips. ACP-launched sessions land in the native provider store, so cockpit `bind` works on them unchanged.
   - Known issue 2026-07-03: the codex adapter exits 1 against codex-cli 0.139.0 — use the codex CLI directly until an acpx or codex update lands.
   - acpx is alpha; interfaces may change. Prefer it for agent-to-agent work because it returns typed ACP output instead of PTY scraping.
2. **Native provider CLIs** — when acpx lacks a working adapter or provider-native behavior matters:
   - codex: `codex exec "…"`, `codex exec resume <id>`
   - claude: `claude -p "…"`, `claude --resume <id>`, `claude --resume <id> --fork-session`
   - opencode: `opencode run --format json [--model opencode-go/…] "…"`, `--session ses_x [--fork]`
   - cursor: `cursor agent --print [--model composer-…] "…"`, `--resume <chatId>`
3. **agents.py — residue.** `/Users/burooj/Projects/skills/agents/agents.py`, JSON-first: `discover`/`inspect` read native session stores (this is what feeds cockpit's ledger), `archive`/`unarchive` where providers support it. Its `run`/`start`/`resume`/`fork` verbs still work as native-CLI wrappers, but prefer acpx or the native CLI directly.

## Rules of thumb

- Result-only, same harness → native subagent, not this skill.
- Result-only, different model → `bunx --bun acpx <agent> exec "…"` (or the native CLI one-shot).
- Durable, resumable, user-visible → an acpx or native-CLI session; report the session id, workspace, and resume command.
- Work bound to a Linear issue → after launch, `./cockpit.py bind BJS-X session:<provider>:<id>`; cockpit owns everything after that.
- Codex Desktop threads: `list_projects` → `create_thread` with the returned projectId, on the Desktop's native tools. If the exact repo path isn't a saved project, stop and tell Burooj rather than falling back to a parent project.

# Rose journal engine

Deterministic journaling for Rose (Hermes profile `rose` on bjslab). Code owns the parts that must not fail: sending prompts, dating, saving Burooj's replies, folding old prompts. Rose (her model chain) only writes the opener, converses, and drafts annotations, and every model step degrades to a plain, correct result.

Built 2026-10-13 after an audit found two weeks of failed prompts, invented context ("Bus run today"), misdated entries, no reply saved to Brain since 2026-08-25, and Rose editing Klaw's model config.

## Pieces

| Piece | Where it runs | Does |
| --- | --- | --- |
| `rose_journal/tick.py` | Rose `no_agent` cron job every 5 min (`scripts/journal_tick.py` stub) | Sends due prompts, folds answered/expired ones, writes annotations, prunes the ledger |
| `plugin/` | Hermes gateway, Rose profile only | `pre_gateway_dispatch`: saves typed replies on arrival; `pre_llm_call`: saves voice transcripts; `pre_tool_call`: the guard |
| `SKILL.md` (`journal-system`) | Rose's conversation | How she answers a journal reply; what not to do herself |
| `/home/admin/.config/rose/journal.json` | config | Root, timezone, location, chat, local schedule, windows |
| `/home/admin/.local/state/rose-journal/` | state | `ledger.json` (sent prompts, message ids, captures), `packs/` (context packs) |

## Flow

1. **Due** — `schedule.due` checks local wall time (`timezone` in config). Travel = edit `timezone`/`location`; no cron changes, no DST drift.
2. **Opener** — `context.build` gathers a dated pack (recent journal entries, Rose Telegram messages, tududi, chat-scrobbler, ListenBrainz, book-grabber). `agent.ask` runs `hermes -p rose chat --oneshot` (Rose's chain and tools). `validate.check` rejects uncited claims and quotes not found in the pack. Any failure → plain opener.
3. **Send** — Bot API `sendMessage` (HTML): header, opener, full question bank in `<blockquote expandable>`. The message id goes into the ledger. Brain gets nothing yet.
4. **Capture** — direct reply to a journal message (any age) → that prompt; else the first message while a prompt is visible (< `collapse_hours`) → most recent visible prompt. Written verbatim to `<root>/YYYY/MM/YYYY-MM-DD-<kind>.md`; later direct replies append. The agent sees a `[Journal reply — …]` note before the text.
5. **Fold** — answered or after `collapse_hours`: the Telegram message is edited to header + folded questions (`answered ✓` / `missed — reply anytime`). The archive never expires.
6. **Annotate** — `annotate_after_minutes` after the first capture, Rose drafts annotations from the entry and her chat reply; code writes them. Up to 3 attempts.

## Guard

`guard.py` blocks, for Rose only: `execute_code`; file writes under Hermes homes, `~/.config/rose`, the engine state, the skills repo, systemd units and `Brain/Journal`; `hermes` subcommands other than `chat`, `cron list|status|runs`, `status`; `systemctl`/`crontab`; write-ish shell commands that mention protected paths; `skill_manage` and `cronjob_manage` writes. It is a guardrail against well-meaning edits, not a security boundary (same Unix user).

## Known limits

- A message sent while Rose is mid-reply takes Hermes' busy path, which skips `pre_gateway_dispatch`; it is not captured. Replying directly to the journal message afterwards appends it.
- Voice capture depends on Hermes STT; if transcription fails the entry records that.
- Not connected: Google Calendar (gog `invalid_grant`), Trakt (API key 403).

## Operate

```sh
cd /mnt/server-ssd/BJsWorkspace/Projects/skills/rose-journal
/home/admin/.hermes/hermes-agent/venv/bin/python -m rose_journal.tick --send morning --dry-run   # preview, no send
/home/admin/.hermes/hermes-agent/venv/bin/python -m unittest discover -s tests                    # tests
hermes -p rose cron runs <tick-job-id>                                                            # tick output
```

Deployment links: `~/.hermes/profiles/rose/plugins/rose-journal -> plugin/`, `~/.hermes/profiles/rose/skills/journaling/journal-system -> .` (this directory), `~/.hermes/profiles/rose/scripts/journal_tick.py` (copy of `bin/journal_tick.py`).

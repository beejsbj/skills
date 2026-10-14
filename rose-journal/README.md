# Rose journal engine

Deterministic journaling for Rose (Hermes profile `rose` on bjslab). Code owns the parts that must not fail: sending prompts, dating, saving Burooj's replies, folding old prompts. Rose (her model chain) only writes the opener, converses, and drafts annotations, and every model step degrades to a plain, correct result.

Built 2026-10-13 after an audit found two weeks of failed prompts, invented context ("Bus run today"), misdated entries, no reply saved to Brain since 2026-08-25, and Rose editing Klaw's model config.

## Pieces

| Piece | Where it runs | Does |
| --- | --- | --- |
| `rose_journal/tick.py` | Rose `no_agent` cron job every 5 min (`scripts/journal_tick.py` stub) | Sends due prompts, folds answered/expired ones, writes annotations, prunes the ledger |
| `plugin/` | Hermes gateway, Rose profile only | `pre_gateway_dispatch`: saves typed replies and `/j` notes on arrival; `pre_llm_call`: saves voice transcripts; `pre_tool_call`: the guard; tool `journal_add_note` for Rose's own notes |
| `SKILL.md` (`journal-system`) | Rose's conversation | How she answers a journal reply; what not to do herself |
| `/home/admin/.config/rose/journal.json` | config | Root, timezone, location, chat, local schedule, windows |
| `/home/admin/.hermes/profiles/rose/plugin-data/rose-journal/` (SSD, in the nightly backup) | state | `ledger.json` (sent prompts, message ids, captures), `packs/` (context packs) |

## Flow

1. **Due** — `schedule.due` checks local wall time (`timezone` in config). Travel = edit `timezone`/`location`; no cron changes, no DST drift.
2. **Opener** — `context.build` gathers a dated pack (recent journal entries, Rose Telegram messages, tududi, chat-scrobbler, ListenBrainz, reading progress from Storyteller/Grimmory/Audiobookshelf). `agent.ask` runs `hermes -p rose chat --oneshot` with Rose's chain and tools; she is told to read further. `validate.check` rejects claims about Burooj with no citation, and journal/Telegram quotes that don't exist in the real records (`context.make_verifier`). Any failure → plain opener.
2b. **Woven questions** — Rose gets the set with ids (`3`, `9.2`) and weaves in as many as fit, reworded; she returns `asked` ids, which are validated against the set and recorded in the entry (`_Woven in: …_`). The full set is always attached, folded.
3. **Send** — Bot API `sendMessage` (HTML): header, opener, full question bank in `<blockquote expandable>`. The message id goes into the ledger. Brain gets nothing yet.
4. **Capture** — direct reply to a journal message (any age) → that prompt; else the first message while a prompt is visible (< `collapse_hours`) → most recent visible prompt. Written verbatim to its own entry at the Journal root, `<root>/YYYY-MM-DD-<kind>.md` (flat, one file per entry, like Burooj's own library): prompt with the question set in a folded Obsidian callout, his words, annotations, Rose's notes; later direct replies append. Voice audio is saved beside its entry with the same name (`2026-10-13-evening.ogg`, then `-2`…) and embedded. The agent sees a `[Journal reply — …]` note before the text.
5. **Fold** — answered or after `collapse_hours`: the Telegram message is edited down to its header line (`answered ✓` / `missed — reply anytime`); replying to it still works. The archive never expires.
6. **`/j`** — a message starting with `/j` or `/journal` (text, or a voice note captioned `/j`) is saved verbatim as its own entry, `YYYY-MM-DD-j.md`, `-j-2.md`, ….
7. **Rose's notes** — the `journal_add_note` tool appends a timestamped note under `### Rose's notes` in a day's section; it never edits his words or annotations.
8. **Annotate** — `annotate_after_minutes` after the first capture, Rose drafts annotations from the entry and her chat reply; code writes them. Up to 3 attempts. Annotation runs with no tools and may use only the entry's content.

## Rose's notebook

Private to Rose: `notebook.json` in the state dir, written only by the `rose_notebook` tool and by `FOLLOW-UP:` lines in annotation drafts. Open items are injected into every Rose turn (`pre_llm_call` context) and into the opener pack. Resolved items move to `notebook-archive.jsonl`; open items untouched for 21 days are archived as stale; at most 40 stay open.

## Manual triggers

Plugin commands `/morning`, `/evening`, `/midweek`, `/weekly` (aliases `/morning-journal`, `/evening-journal`) spawn `tick --send <kind>` in the background; it waits for a running tick. A re-send for a ritual already sent today becomes the current message; the old one is marked "sent again below" and still accepts direct replies (`previous_message_ids`). Output goes to `manual-trigger.log` in the state dir.

## Travel

`journal_set_location` (plugin tool) geocodes a place with Open-Meteo and writes `location`, `timezone` and `coordinates` to `journal.json`, appending the change to `location-history.jsonl` in the state dir. Schedules are local, so nothing else changes.

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

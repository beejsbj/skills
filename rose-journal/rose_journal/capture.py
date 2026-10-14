"""Decide whether an incoming Telegram message is a journal reply, and save it.

Rules:
1. A direct Telegram reply to a journal prompt is always a journal reply, at
   any age. Every direct reply is appended to that entry.
2. Otherwise, the first message after a prompt while it is still visible
   (before it collapses) answers the most recent visible prompt.
3. Anything else is ordinary conversation.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from . import entries, ledger
from .config import Config


def _aware(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def match(data: dict, cfg: Config, chat_id: str, reply_to: str | None, now: datetime) -> tuple[dict | None, str]:
    if str(chat_id) != str(cfg.chat_id):
        return None, ""
    if reply_to:
        p = ledger.by_message_id(data, chat_id, reply_to)
        if p:
            return p, "direct-reply"
    window = timedelta(hours=cfg.collapse_hours)
    visible = [
        p for p in data["prompts"]
        if p.get("message_id") and not p.get("collapsed_at") and not p.get("captures")
        and now - _aware(p["sent_at"]) < window
    ]
    if visible:
        return max(visible, key=lambda p: p["sent_at"]), "next-message"
    return None, ""


def record(cfg: Config, prompt: dict, rule: str, text: str, now: datetime,
           source: str = "text", platform_message_id: str | None = None, audio: str | None = None) -> dict:
    """Write the reply into Brain and note it on the ledger prompt (caller holds the lock)."""
    local_now = now.astimezone(cfg.tz)
    prompt.setdefault("stem", entries.stem_for(prompt["local_date"], prompt["kind"]))
    path = entries.record_reply(cfg.root, prompt, text, local_now, source, audio)
    prompt.setdefault("captures", []).append({
        "at": now.isoformat(),
        "rule": rule,
        "source": source,
        "platform_message_id": platform_message_id,
    })
    prompt["entry_path"] = str(path)
    prompt["needs_edit"] = True
    return {"prompt": dict(prompt), "path": str(path), "rule": rule}


def capture(cfg: Config, chat_id: str, reply_to: str | None, text: str, now: datetime,
            source: str = "text", platform_message_id: str | None = None) -> dict | None:
    """Save the message if it is a journal reply. Returns capture info or None."""
    if not text or not text.strip() or text.lstrip().startswith("/"):
        return None
    with ledger.locked(cfg.ledger_path) as data:
        prompt, rule = match(data, cfg, chat_id, reply_to, now)
        if not prompt:
            return None
        return record(cfg, prompt, rule, text, now, source, platform_message_id)


def capture_to(cfg: Config, pid: str, rule: str, text: str, now: datetime,
               source: str, platform_message_id: str | None = None, audio: str | None = None) -> dict | None:
    """Save into a known prompt (voice notes: matched at arrival, written after transcription)."""
    with ledger.locked(cfg.ledger_path) as data:
        prompt = ledger.find(data, pid)
        if not prompt:
            return None
        return record(cfg, prompt, rule, text, now, source, platform_message_id, audio)


JOURNAL_COMMAND = re.compile(r"^\s*/(?:j|journal)(?:@\w+)?(?:\s+|$)", re.I)
def strip_command(text: str) -> str | None:
    """Return the text after a /j or /journal command, or None if it isn't one."""
    m = JOURNAL_COMMAND.match(text or "")
    return text[m.end():] if m else None


def new_note_prompt(data: dict, cfg: Config, now: datetime) -> dict:
    """A fresh record for one /j note: each note is its own entry file (…-j.md, …-j-2.md)."""
    local_date = now.astimezone(cfg.tz).date().isoformat()
    taken = {p.get("stem") for p in data["prompts"]}
    n, stem = 1, entries.stem_for(local_date, "j")
    while stem in taken or entries.entry_path(cfg.root, stem).exists():
        n += 1
        stem = entries.stem_for(local_date, "j", n)
    p = {"id": stem, "stem": stem, "kind": "j", "local_date": local_date, "chat_id": cfg.chat_id,
         "message_id": None, "sent_at": now.isoformat(), "opener": "", "opener_source": "/j"}
    data["prompts"].append(p)
    return p


def capture_note(cfg: Config, text: str, now: datetime, source: str = "text",
                 platform_message_id: str | None = None, audio: str | None = None) -> dict:
    with ledger.locked(cfg.ledger_path) as data:
        p = new_note_prompt(data, cfg, now)
        info = record(cfg, p, "/j", text, now, source, platform_message_id, audio)
        p["needs_edit"] = False  # nothing to fold in Telegram
        return info


def reserve_note(cfg: Config, now: datetime) -> dict:
    """For a /j voice note: create its record now; the transcript is written after STT."""
    with ledger.locked(cfg.ledger_path) as data:
        return dict(new_note_prompt(data, cfg, now))


def note_context(info: dict) -> str:
    return (
        f"[Journal note — Burooj used /j; the journal system saved this verbatim to {info['path']}. "
        f"Acknowledge briefly and respond naturally if there's something to respond to. "
        f"Don't edit the file.]\n\n"
    )


def add_rose_note(cfg: Config, text: str, now: datetime, local_date: str | None = None,
                  kind: str | None = None) -> str:
    """Rose's own addition, appended under "Rose's notes" in an entry; never touches his words."""
    if not text or not text.strip():
        raise ValueError("note text is empty")
    local_now = now.astimezone(cfg.tz)
    local_date = local_date or local_now.date().isoformat()
    datetime.strptime(local_date, "%Y-%m-%d")  # validate
    if kind and kind not in ("morning", "evening", "midweek", "weekly", "j"):
        raise ValueError(f"unknown kind {kind!r}")
    day = entries.entries_on(cfg.root, local_date)
    if kind:
        day = [p for p in day if entries.kind_of(p) == kind]
    if day:
        path = day[-1]
    else:  # nothing that day: a Rose-started note entry
        stem = entries.next_stem(cfg.root, local_date, "note")
        path = entries.entry_path(cfg.root, stem)
    entries.add_rose_note(path, text, local_now, {"kind": "note", "local_date": local_date})
    return str(path)


def planned_info(cfg: Config, prompt: dict) -> dict:
    stem = prompt.get("stem") or entries.stem_for(prompt["local_date"], prompt["kind"])
    return {"prompt": prompt, "path": str(entries.entry_path(cfg.root, stem))}


def context_note(info: dict) -> str:
    """Prefix the agent sees, so Rose knows which prompt this answers."""
    p = info["prompt"]
    opener = (p.get("opener") or "").strip()
    asked = f" Rose's opener for that prompt was: “{opener}”" if opener else ""
    return (
        f"[Journal reply — saved verbatim by the journal system as Burooj's answer to the "
        f"{p['kind']} journal of {p['local_date']} ({info['path']}).{asked} "
        f"Respond as Rose following the journal-system skill. Do not edit the journal file; "
        f"annotations are written automatically.]\n\n"
    )

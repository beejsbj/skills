"""Decide whether an incoming Telegram message is a journal reply, and save it.

Rules:
1. A direct Telegram reply to a journal prompt is always a journal reply, at
   any age. Every direct reply is appended to that entry.
2. Otherwise, the first message after a prompt while it is still visible
   (before it collapses) answers the most recent visible prompt.
3. Anything else is ordinary conversation.
"""
from __future__ import annotations

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
           source: str = "text", platform_message_id: str | None = None) -> dict:
    """Write the reply into Brain and note it on the ledger prompt (caller holds the lock)."""
    local_now = now.astimezone(cfg.tz)
    path = entries.record_reply(cfg.root, prompt, text, local_now, source)
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
               source: str, platform_message_id: str | None = None) -> dict | None:
    """Save into a known prompt (voice notes: matched at arrival, written after transcription)."""
    with ledger.locked(cfg.ledger_path) as data:
        prompt = ledger.find(data, pid)
        if not prompt:
            return None
        return record(cfg, prompt, rule, text, now, source, platform_message_id)


def planned_info(cfg: Config, prompt: dict) -> dict:
    return {"prompt": prompt, "path": str(entries.entry_path(cfg.root, prompt["local_date"], prompt["kind"]))}


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

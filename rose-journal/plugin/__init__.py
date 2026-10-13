"""Rose journal plugin (Rose profile only).

pre_gateway_dispatch  typed journal replies are written to Brain verbatim on
                      arrival, before any model runs; voice notes are matched
                      here and written once transcribed (pre_llm_call).
pre_tool_call         the guard: Rose can't change Hermes settings.

Every callback fails open for capture (a bug must never drop a message) and
the guard fails open too (a bug must never block all of Rose's tools); errors
are logged.
"""
from __future__ import annotations

import logging
import os
import re
import sys
import threading
import time
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from rose_journal import capture, config as jconfig, guard, ledger  # noqa: E402

log = logging.getLogger("rose_journal.plugin")
_VOICE_TTL = 900
_pending_voice: dict = {}
_lock = threading.Lock()
_REPLY_PREFIX = re.compile(r'^\[Replying to[^\n]*\]\s*', re.S)


def _platform(src) -> str:
    p = getattr(src, "platform", "")
    return str(getattr(p, "value", p)).lower()


def on_dispatch(event=None, **_kw):
    try:
        src = getattr(event, "source", None)
        if src is None or "telegram" not in _platform(src):
            return None
        cfg = jconfig.load()
        chat_id = str(getattr(src, "chat_id", ""))
        reply_to = getattr(event, "reply_to_message_id", None)
        reply_to = str(reply_to) if reply_to else None
        msg_id = str(getattr(event, "message_id", "") or "")
        now = datetime.now(timezone.utc)
        text = getattr(event, "text", "") or ""
        kind = str(getattr(getattr(event, "message_type", ""), "name", getattr(event, "message_type", ""))).upper()

        if kind in ("VOICE", "AUDIO"):
            prompt, rule = capture.match(ledger.snapshot(cfg.ledger_path), cfg, chat_id, reply_to, now)
            if not prompt:
                return None
            info = capture.planned_info(cfg, prompt)
            note = capture.context_note(info)
            with _lock:
                _pending_voice["slot"] = {
                    "pid": prompt["id"], "rule": rule, "msg_id": msg_id, "note": note,
                    "caption": text, "deadline": time.time() + _VOICE_TTL,
                }
            return {"action": "rewrite", "text": note + text}

        info = capture.capture(cfg, chat_id, reply_to, text, now, "text", msg_id)
        if not info:
            return None
        log.info("journal reply captured: %s (%s)", info["path"], info["rule"])
        return {"action": "rewrite", "text": capture.context_note(info) + text}
    except Exception:
        log.exception("rose-journal dispatch hook failed; message passed through uncaptured")
        return None


def _transcript(user_message: str, pend: dict) -> str:
    text = user_message.replace(pend["note"], "")
    text = _REPLY_PREFIX.sub("", text.strip())
    if pend.get("caption"):
        text = text.replace(pend["caption"], "").strip()
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1].strip()
    return text or "(voice note — no transcript was available)"


def on_llm_call(user_message=None, platform=None, **_kw):
    try:
        if "telegram" not in str(platform or "").lower():
            return None
        with _lock:
            pend = _pending_voice.get("slot")
            if not pend or time.time() > pend["deadline"] or pend["note"] not in (user_message or ""):
                return None
            _pending_voice.pop("slot", None)
        cfg = jconfig.load()
        text = _transcript(user_message or "", pend)
        if pend.get("caption"):
            text = f"{text}\n\n{pend['caption']}"
        info = capture.capture_to(cfg, pend["pid"], pend["rule"], text,
                                  datetime.now(timezone.utc), "voice", pend["msg_id"])
        if info:
            log.info("journal voice reply captured: %s", info["path"])
    except Exception:
        log.exception("rose-journal voice capture failed")
    return None


def on_tool_call(tool_name=None, args=None, **_kw):
    try:
        msg = guard.check(str(tool_name or ""), args if isinstance(args, dict) else {})
    except Exception:
        log.exception("rose-journal guard failed open")
        return None
    if msg:
        log.warning("rose-journal guard blocked %s", tool_name)
        return {"action": "block", "message": msg}
    return None


def register(ctx):
    ctx.register_hook("pre_gateway_dispatch", on_dispatch)
    ctx.register_hook("pre_llm_call", on_llm_call)
    ctx.register_hook("pre_tool_call", on_tool_call)

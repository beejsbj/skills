"""Rose journal plugin (Rose profile only).

pre_gateway_dispatch  typed journal replies are written to Brain verbatim on
                      arrival, before any model runs; voice notes are matched
                      here and written once transcribed (pre_llm_call).
pre_tool_call         the guard: Rose can't change Hermes settings.
journal_add_note      tool: Rose appends her own notes to an entry (never his words).
journal_set_location  tool: Rose moves location/timezone/weather when he travels.
/j or /journal        a message starting with it is saved as that day's freeform entry.
/morning … /weekly    send that ritual now (engine, background); /morning_journal and /evening_journal alias.

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

from rose_journal import capture, config as jconfig, guard, ledger, location  # noqa: E402

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

        after_j = capture.strip_command(text)

        if kind in ("VOICE", "AUDIO"):
            if after_j is not None:
                if str(chat_id) != str(cfg.chat_id):
                    return None
                prompt, rule = capture.reserve_note(cfg, now), "/j"
                text = after_j
                info = capture.planned_info(cfg, prompt)
                note = capture.note_context(info)
            else:
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

        if after_j is not None:
            if str(chat_id) != str(cfg.chat_id) or not after_j.strip():
                return None
            info = capture.capture_note(cfg, after_j, now, "text", msg_id)
            log.info("journal note captured: %s", info["path"])
            return {"action": "rewrite", "text": capture.note_context(info) + after_j}

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


NOTE_SCHEMA = {
    "name": "journal_add_note",
    "description": (
        "Add your own note to Burooj's journal in Brain: an observation, a connection you found while "
        "reading his records, or something from conversation worth keeping. It is appended, timestamped, "
        "under \"Rose's Notes\" in that day's entry and never changes his words or the annotations. "
        "Use it when something is genuinely worth keeping, not for every turn."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "note": {"type": "string", "description": "The note, in your voice. Mark inference as inference."},
            "date": {"type": "string", "description": "Local date YYYY-MM-DD of the entry; defaults to today."},
            "kind": {"type": "string", "enum": ["morning", "evening", "midweek", "weekly", "note"],
                     "description": "Which entry of that day; defaults to the most recent existing one."},
        },
        "required": ["note"],
    },
}


def journal_add_note(params, **_kw):
    import json
    try:
        cfg = jconfig.load()
        path = capture.add_rose_note(cfg, str(params.get("note", "")), datetime.now(timezone.utc),
                                     params.get("date") or None, params.get("kind") or None)
        return json.dumps({"success": True, "path": path})
    except Exception as e:
        return json.dumps({"success": False, "error": f"{type(e).__name__}: {e}"})


LOCATION_SCHEMA = {
    "name": "journal_set_location",
    "description": (
        "Update where Burooj is, when he tells you he has moved or is travelling. Looks the place up, then "
        "sets the journal's location, timezone and weather coordinates; prompts follow his new local time "
        "automatically. Confirm the place with him first if it's ambiguous. Returns the new local schedule."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "place": {"type": "string", "description": "City or town, e.g. 'Srinagar' or 'Toronto, Canada'."},
            "timezone": {"type": "string", "description": "Optional IANA timezone override, e.g. 'Asia/Kolkata'."},
        },
        "required": ["place"],
    },
}


def journal_set_location(params, **_kw):
    import json
    try:
        result = location.set_location(str(params.get("place", "")).strip(), params.get("timezone") or None)
        return json.dumps({"success": True, **result})
    except Exception as e:
        return json.dumps({"success": False, "error": f"{type(e).__name__}: {e}"})


def _trigger(kind: str):
    """Slash-command handler: send this ritual now, through the engine, in the background."""
    def handler(raw_args: str = "", **_kw):
        import subprocess
        try:
            cfg = jconfig.load()
            cfg.state_dir.mkdir(parents=True, exist_ok=True)
            with open(cfg.state_dir / "manual-trigger.log", "a") as out:
                subprocess.Popen([sys.executable, "-m", "rose_journal.tick", "--send", kind], cwd=_REPO,
                                 stdout=out, stderr=out, start_new_session=True)
            return f"🌹 Your {kind} journal is on its way."
        except Exception as e:
            log.exception("manual %s trigger failed", kind)
            return f"Couldn't start the {kind} journal ({type(e).__name__}). Otto can look into it."
    return handler


def _j_usage(raw_args: str = "", **_kw):
    # Text after /j is captured before command routing; this only runs for a bare /j.
    return "Write it right after the command: /j <anything worth keeping>. A voice note captioned /j works too."


def register(ctx):
    ctx.register_command("j", _j_usage, description="Save a note to today's journal: /j <text>")
    for kind in ("morning", "evening", "midweek", "weekly"):
        ctx.register_command(kind, _trigger(kind), description=f"Send the {kind} journal now")
    for alias, kind in (("morning-journal", "morning"), ("evening-journal", "evening")):
        ctx.register_command(alias, _trigger(kind), description=f"Send the {kind} journal now")
    ctx.register_tool(
        name="journal_set_location",
        toolset="rose_journal",
        schema=LOCATION_SCHEMA,
        handler=journal_set_location,
        description="Move the journal to where Burooj is now (location, timezone, weather).",
        emoji="🧭",
    )
    ctx.register_tool(
        name="journal_add_note",
        toolset="rose_journal",
        schema=NOTE_SCHEMA,
        handler=journal_add_note,
        description="Append Rose's own note to a journal entry in Brain.",
        emoji="🌹",
    )
    ctx.register_hook("pre_gateway_dispatch", on_dispatch)
    ctx.register_hook("pre_llm_call", on_llm_call)
    ctx.register_hook("pre_tool_call", on_tool_call)

"""Minimal Telegram Bot API client for Rose's bot (send + edit, HTML mode).

The token comes from the same secrets helper the Rose profile uses
(`bjs-env hermes-rose`), read into memory only; it is never logged.
"""
from __future__ import annotations

import html
import json
import os
import re
import subprocess
import urllib.error
import urllib.request

SECRETS_HELPER = ["/home/admin/.local/bin/bjs-env", "hermes-rose"]


class TelegramError(RuntimeError):
    pass


def _token() -> str:
    tok = os.environ.get("ROSE_TELEGRAM_BOT_TOKEN")
    if tok:
        return tok
    out = subprocess.run(SECRETS_HELPER, capture_output=True, text=True, timeout=30)
    for line in out.stdout.splitlines():
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise TelegramError("TELEGRAM_BOT_TOKEN unavailable from secrets helper")


def _call(method: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{_token()}/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = json.loads(e.read() or b"{}")
    if not body.get("ok"):
        raise TelegramError(f"{method}: {body.get('description', 'unknown error')}")
    return body["result"]


def send_html(chat_id: str, text: str) -> str:
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML",
               "link_preview_options": {"is_disabled": True}}
    try:
        result = _call("sendMessage", payload)
    except TelegramError as e:
        if "parse entities" not in str(e):
            raise
        payload.pop("parse_mode")  # never lose a prompt to a markup error
        payload["text"] = html.unescape(re.sub(r"<[^>]+>", "", text))
        result = _call("sendMessage", payload)
    return str(result["message_id"])


def edit_html(chat_id: str, message_id: str, text: str) -> None:
    try:
        _call("editMessageText", {
            "chat_id": chat_id, "message_id": int(message_id), "text": text, "parse_mode": "HTML",
            "link_preview_options": {"is_disabled": True},
        })
    except TelegramError as e:
        if "message is not modified" not in str(e):
            raise

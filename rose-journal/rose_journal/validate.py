"""Grounding check for model-written openers.

The opener is the only model text in a prompt. It may reference Burooj's life
only through citations; citations from the journal or Telegram must quote
text that actually exists in the context pack. Anything else falls back to
the plain opener, so a weak or confused model degrades to "plain", never to
"invented".
"""
from __future__ import annotations

import json
import re

CLAIM_MARKERS = re.compile(
    r"\b(you (mentioned|said|wrote|told|shared|had|were|did|have been|'ve been|landed|flew)"
    r"|yesterday|last night|earlier today|this morning you|you're (still|back)"
    r"|bus run|your shift)\b",
    re.I,
)
VERIFIABLE = ("journal:", "telegram:")
LIMITS = {"morning": 700, "evening": 700, "midweek": 500, "weekly": 1600}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def parse(raw: str) -> dict | None:
    raw = raw.strip()
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def check(kind: str, data: dict | None, pack_text: str) -> tuple[bool, str]:
    """Return (ok, reason)."""
    if not data:
        return False, "unparseable"
    opener = data.get("opener")
    cites = data.get("citations") or []
    if not isinstance(opener, str) or not opener.strip():
        return False, "empty opener"
    if len(opener) > LIMITS[kind]:
        return False, f"too long ({len(opener)})"
    if len(re.findall(r"(?m)^\s*\d+[.)]\s", opener)) >= 3:
        return False, "repeats question bank"
    if not isinstance(cites, list):
        return False, "citations not a list"
    pack = _norm(pack_text)
    for c in cites:
        if not isinstance(c, dict) or not str(c.get("quote", "")).strip():
            return False, "citation without quote"
        src = str(c.get("source", ""))
        if src.startswith(VERIFIABLE) and _norm(str(c["quote"])) not in pack:
            return False, f"unverified quote from {src}"
    if not cites and CLAIM_MARKERS.search(opener):
        return False, "claim without citation"
    return True, "ok"

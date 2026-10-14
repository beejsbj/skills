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
LIMITS = {"morning": 1400, "evening": 1400, "midweek": 900, "weekly": 2200}


def norm(s: str) -> str:
    return _norm(s)


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


def check(kind: str, data: dict | None, pack_text: str, verify=None) -> tuple[bool, str]:
    """Return (ok, reason).

    `verify(source, quote) -> bool` checks journal/Telegram quotes against the real records, so Rose
    can cite things she read with her own tools beyond the pack. Default: the pack only.
    """
    if not data:
        return False, "unparseable"
    opener = data.get("opener")
    cites = data.get("citations") or []
    if not isinstance(opener, str) or not opener.strip():
        return False, "empty opener"
    if len(opener) > LIMITS[kind]:
        return False, f"too long ({len(opener)})"
    if len(re.findall(r"(?m)^\s*\d+[.)]\s", opener)) >= 6:
        return False, "pastes the question set"
    if not isinstance(cites, list):
        return False, "citations not a list"
    pack = _norm(pack_text)
    for c in cites:
        if not isinstance(c, dict) or not str(c.get("quote", "")).strip():
            return False, "citation without quote"
        src = str(c.get("source", ""))
        if src.startswith(VERIFIABLE):
            q = _norm(str(c["quote"]))
            if q not in pack and not (verify and verify(src, q)):
                return False, f"unverified quote from {src}"
    if not cites and CLAIM_MARKERS.search(opener):
        return False, "claim without citation"
    return True, "ok"


def asked(kind: str, data: dict) -> list[dict]:
    """The bank questions Rose wove in, keeping only ids that exist (bad ids are dropped, not fatal)."""
    from .questions import bank_items
    items = bank_items(kind)
    out = []
    for a in data.get("asked") or []:
        if isinstance(a, dict) and str(a.get("id")) in items:
            out.append({"id": str(a["id"]), "question": items[str(a["id"])], "as": str(a.get("as", "")).strip()})
    return out

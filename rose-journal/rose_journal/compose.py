"""Deterministic prompt assembly: header + opener + folded question bank."""
from __future__ import annotations

import html
import re
from datetime import datetime

from .questions import TITLES, bank_text

PLAIN_OPENERS = {
    "morning": "Morning, Burooj 🌹 Start wherever something feels alive — one line or a voice note is plenty.",
    "evening": "Evening, Burooj 🌹 Let the day land. Answer whatever pulls at you; you don't need to do them all.",
    "midweek": "Midweek check-in. Quick pulse — a sentence or two is enough.",
    "weekly": "End of the week. Let's look back — take whichever thread matters.",
}

HINT = "Reply to this message anytime — it goes in the journal."


def header(kind: str, local_dt: datetime, status: str = "") -> str:
    day = local_dt.strftime("%a %-d %b")
    suffix = f" · {status}" if status else ""
    return f"🌹 {TITLES[kind]} · {day}{suffix}"


def _md_to_html(text: str) -> str:
    """Escape model text, keeping **bold** and _italic_ as the only markup."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    out = re.sub(r"(?<![\w*])_(.+?)_(?![\w*])", r"<i>\1</i>", out)
    return out


def telegram_html(kind: str, local_dt: datetime, opener: str | None, status: str = "") -> str:
    parts = [f"<b>{html.escape(header(kind, local_dt, status), quote=False)}</b>"]
    if opener:
        parts.append(_md_to_html(opener.strip()))
    parts.append(f"<blockquote expandable>{html.escape(bank_text(kind), quote=False)}</blockquote>")
    if not status:
        parts.append(f"<i>{HINT}</i>")
    return "\n\n".join(parts)


def plain_text(kind: str, local_dt: datetime, opener: str | None) -> str:
    """The archived orientation prompt: exactly what was sent, minus markup."""
    parts = [header(kind, local_dt)]
    if opener:
        parts.append(opener.strip())
    parts.append(bank_text(kind))
    return "\n\n".join(parts)

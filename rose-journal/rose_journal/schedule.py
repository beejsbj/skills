"""Which rituals are due, evaluated in Burooj's local timezone.

The tick runs every few minutes on the host clock; due-ness is decided here
in local wall time, so travel and DST never require rewriting cron schedules.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from .config import KINDS, Config


def due(cfg: Config, now_local: datetime, sent_ids: set[str]) -> list[tuple[str, datetime]]:
    """Return (kind, scheduled_local_dt) for rituals due now and not yet sent."""
    out = []
    for kind in KINDS:
        spec = cfg.schedule.get(kind)
        if not spec or spec.get("enabled") is False:
            continue
        hh, mm = (int(x) for x in spec["time"].split(":"))
        weekday = spec.get("weekday")
        if weekday is not None and now_local.weekday() != int(weekday):
            continue
        at = now_local.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if not (at <= now_local < at + timedelta(hours=cfg.grace_hours)):
            continue
        if f"{at.date().isoformat()}-{kind}" in sent_ids:
            continue
        out.append((kind, at))
    return out

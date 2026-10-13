"""Journal configuration: one file decides root, timezone, location and schedule.

`/home/admin/.config/rose/journal.json` is the single source of truth. Travel
changes edit `timezone`/`location` there; schedules are local wall-clock times
in that timezone, so nothing else needs converting.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo

CONFIG_PATH = Path(os.environ.get("ROSE_JOURNAL_CONFIG", "/home/admin/.config/rose/journal.json"))
STATE_DIR = Path(os.environ.get("ROSE_JOURNAL_STATE", "/home/admin/.local/state/rose-journal"))

KINDS = ("morning", "evening", "midweek", "weekly")

DEFAULT_SCHEDULE = {
    "morning": {"time": "06:00"},
    "evening": {"time": "23:00"},
    "midweek": {"time": "12:00", "weekday": 2},  # Wednesday
    "weekly": {"time": "20:00", "weekday": 6},   # Sunday
}


@dataclass
class Config:
    root: Path
    timezone: str = "Asia/Kolkata"
    location: str = ""
    chat_id: str = "579876880"
    profile: str = "rose"
    schedule: dict = field(default_factory=lambda: dict(DEFAULT_SCHEDULE))
    collapse_hours: float = 6.0
    grace_hours: float = 2.0
    opener_budget_seconds: int = 240
    annotate_after_minutes: int = 20
    state_dir: Path = STATE_DIR

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

    @property
    def ledger_path(self) -> Path:
        return self.state_dir / "ledger.json"


def load(path: Path | None = None) -> Config:
    path = Path(path or CONFIG_PATH)
    data = json.loads(path.read_text(encoding="utf-8"))
    root = data.get("root")
    if not isinstance(root, str) or not root.strip():
        raise ValueError(f"invalid journal root in {path}")
    schedule = dict(DEFAULT_SCHEDULE)
    schedule.update(data.get("schedule") or {})
    cfg = Config(
        root=Path(root).expanduser(),
        timezone=data.get("timezone", "Asia/Kolkata"),
        location=data.get("location", ""),
        chat_id=str(data.get("telegram_chat_id", "579876880")),
        profile=data.get("profile", "rose"),
        schedule=schedule,
        collapse_hours=float(data.get("collapse_hours", 6)),
        grace_hours=float(data.get("grace_hours", 2)),
        opener_budget_seconds=int(data.get("opener_budget_seconds", 240)),
        annotate_after_minutes=int(data.get("annotate_after_minutes", 20)),
        state_dir=Path(data.get("state_dir", str(STATE_DIR))),
    )
    cfg.tz  # validate timezone name early
    return cfg

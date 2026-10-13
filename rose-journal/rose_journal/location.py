"""Travel: one call moves the journal's location, timezone and weather coordinates.

Rose calls this through the `journal_set_location` tool when Burooj says he has
moved. The place is geocoded with Open-Meteo (no key), which also returns its
IANA timezone. Prompts follow the new local time automatically; every change
is appended to a history file so it can be undone.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from . import config as jconfig


def geocode(place: str) -> dict:
    tries = [place] + ([place.split(",")[0].strip()] if "," in place else [])
    for q in tries:
        url = ("https://geocoding-api.open-meteo.com/v1/search?count=1&language=en&format=json&name="
               + urllib.parse.quote(q))
        out = subprocess.run(["curl", "-4", "-s", "--max-time", "15", url], capture_output=True, text=True, timeout=20)
        results = json.loads(out.stdout or "{}").get("results") or []
        if results:
            return results[0]
    raise ValueError(f"couldn't find a place called {place!r}")


def set_location(place: str, tz_override: str | None = None, path: Path | None = None) -> dict:
    path = Path(path or jconfig.CONFIG_PATH)
    hit = geocode(place)
    tz = tz_override or hit.get("timezone")
    ZoneInfo(tz)  # raises on an invalid name
    label = ", ".join(x for x in (hit.get("name"), hit.get("admin1"), hit.get("country")) if x)
    data = json.loads(path.read_text(encoding="utf-8"))
    before = {k: data.get(k) for k in ("location", "timezone", "coordinates")}
    data.update(location=label, timezone=tz,
                coordinates={"lat": hit["latitude"], "lon": hit["longitude"], "place": label})
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".journal-")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)
    cfg = jconfig.load(path)
    hist = cfg.state_dir / "location-history.jsonl"
    hist.parent.mkdir(parents=True, exist_ok=True)
    with open(hist, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "before": before,
                             "after": {k: data[k] for k in before}, "query": place}) + "\n")
    now = datetime.now(cfg.tz)
    times = {k: v["time"] + (f" ({['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][v['weekday']]})" if "weekday" in v else "")
             for k, v in cfg.schedule.items()}
    return {"location": label, "timezone": tz, "local_time_now": now.strftime("%a %H:%M"),
            "schedule_local": times, "previous": before}

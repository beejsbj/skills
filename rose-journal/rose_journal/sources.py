"""External, read-only context sources for the pack.

Each returns a list of short dated lines. Access routes were verified on
2026-10-13; Google Calendar (gog: invalid_grant) and Trakt (HTTP 403) need
re-authorisation by Burooj before they can be added.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
from datetime import datetime, timedelta, timezone

from .config import Config

TUDUDI_MCP = "/mnt/server-ssd/BJsWorkspace/Projects/skills/tududi/scripts/mcp-stdio.py"


def _mcp_call(tool: str, arguments: dict) -> dict:
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "rose-journal", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": tool, "arguments": arguments}},
    ]
    out = subprocess.run(["/usr/bin/python3", TUDUDI_MCP], input="\n".join(json.dumps(m) for m in msgs) + "\n",
                         capture_output=True, text=True, timeout=20)
    for line in out.stdout.splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("id") == 2:
            if "error" in msg:
                raise RuntimeError(str(msg["error"])[:150])
            return json.loads(msg["result"]["content"][0]["text"])
    raise RuntimeError("no tools/call reply from tududi")


def tududi(cfg: Config, now_local: datetime) -> list[str]:
    data = _mcp_call("list_tasks", {"type": "all", "limit": 200})
    today = now_local.date().isoformat()
    week_ago = (now_local - timedelta(days=7)).isoformat()
    lines = []
    for t in data.get("tasks", []):
        name = t.get("name", "")
        project = (t.get("Project") or {}).get("name") if isinstance(t.get("Project"), dict) else None
        tag = f" [{project}]" if project else ""
        if t.get("completed_at") and t["completed_at"] >= week_ago:
            lines.append(f"- tududi: done {t['completed_at'][:10]} — {name}{tag}")
        elif t.get("habit_mode"):
            last = (t.get("habit_last_completion_at") or "never")[:10]
            lines.append(f"- tududi habit: {name} (streak {t.get('habit_current_streak', 0)}, last {last})")
        elif t.get("due_date") and t["due_date"][:10] <= today:
            lines.append(f"- tududi: due {t['due_date'][:10]} — {name}{tag}")
        else:
            lines.append(f"- tududi: open — {name}{tag}")
    return lines[:30]


def scrobbler(cfg: Config, now_local: datetime) -> list[str]:
    out = subprocess.run(["/home/admin/.local/bin/chat-scrobbler", "list", "--limit", "50", "--json"],
                         capture_output=True, text=True, timeout=20)
    since = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
    lines = []
    for s in json.loads(out.stdout or "[]"):
        if str(s.get("updated_at", "")) >= since:
            lines.append(f"- scrobbler:{s['id']} ({s.get('source')}, {str(s.get('updated_at'))[:16]}) — {s.get('title')}")
    return lines[:12]


def listenbrainz(cfg: Config, now_local: datetime) -> list[str]:
    since = int((datetime.now(timezone.utc) - timedelta(days=2)).timestamp())
    out = subprocess.run(["curl", "-4", "--tls-max", "1.2", "-s", "--max-time", "15",
                          f"https://api.listenbrainz.org/1/user/beejsbj/listens?count=15&min_ts={since}"],
                         capture_output=True, text=True, timeout=20)
    listens = json.loads(out.stdout or "{}").get("payload", {}).get("listens", [])
    lines = []
    for l in listens:
        md = l.get("track_metadata", {})
        when = datetime.fromtimestamp(l.get("listened_at", 0), timezone.utc).astimezone(cfg.tz)
        lines.append(f"- listenbrainz:{when.isoformat(timespec='minutes')} — {md.get('artist_name')} · {md.get('track_name')}")
    return lines


STORYTELLER_DB = "/mnt/server-ssd/library/data/storyteller/storyteller.db"
ABS_DB = "/mnt/server-ssd/library/configs/audiobookshelf/absdatabase.sqlite"
GRIMMORY_DB_CONTAINER = "mariadb-e4k444cc08s00cscs4o80wc0"


def _sqlite(path: str, sql: str, args: tuple = ()) -> list:
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=10)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def reading(cfg: Config, now_local: datetime) -> list[str]:
    """What he has actually been reading or listening to, across his three readers."""
    since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    lines: list[tuple[str, str]] = []
    errors = []
    try:  # Storyteller (read-along ebooks); positions are UTC
        for updated, title, locator in _sqlite(STORYTELLER_DB,
                """select p.updated_at, b.title, p.locator from position p join book b on b.uuid = p.book_uuid
                   where p.updated_at >= ? order by p.updated_at desc limit 8""", (since,)):
            pct = json.loads(locator).get("locations", {}).get("totalProgression")
            pct_s = f"{round(pct * 100)}%" if isinstance(pct, (int, float)) else "?"
            local = datetime.fromisoformat(updated).replace(tzinfo=timezone.utc).astimezone(cfg.tz)
            lines.append((local.isoformat(), f"- book:{title} — Storyteller, {pct_s} through, last read "
                                              f"{local.isoformat(timespec='minutes')}"))
    except Exception as e:
        errors.append(f"Storyteller unavailable ({type(e).__name__})")
    try:  # Grimmory (ebook library, MariaDB); credentials stay inside the container
        sql = ("select p.last_read_time, m.title, coalesce(p.epub_progress_percent, p.pdf_progress_percent, "
               "p.koreader_progress_percent, p.kobo_progress_percent), p.read_status from user_book_progress p "
               f"left join book_metadata m on m.book_id = p.book_id where p.last_read_time >= '{since}' "
               "order by p.last_read_time desc limit 8")
        out = subprocess.run(["docker", "exec", GRIMMORY_DB_CONTAINER, "sh", "-c",
                              f'mariadb -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" booklore -N -B -e "{sql}"'],
                             capture_output=True, text=True, timeout=20)
        for row in out.stdout.splitlines():
            when, title, pct, status = (row.split("\t") + ["", "", "", ""])[:4]
            pct_s = f"{float(pct):.0f}%" if pct not in ("", "NULL") else "?"
            lines.append((when, f"- book:{title} — Grimmory, {pct_s} ({status.lower()}), last read {when[:16]}"))
    except Exception as e:
        errors.append(f"Grimmory unavailable ({type(e).__name__})")
    try:  # Audiobookshelf; never touch its users table
        for updated, title, audio, ebook, finished in _sqlite(ABS_DB,
                """select mp.updatedAt, b.title, round(mp.currentTime / nullif(mp.duration, 0), 3), mp.ebookProgress,
                          mp.isFinished from mediaProgresses mp left join books b on b.id = mp.mediaItemId
                   where mp.updatedAt >= ? order by mp.updatedAt desc limit 5""", (since,)):
            pct = audio if audio is not None else ebook
            pct_s = "finished" if finished else (f"{round(float(pct) * 100)}%" if pct is not None else "?")
            lines.append((str(updated), f"- book:{title} — Audiobookshelf, {pct_s}, last {str(updated)[:16]}"))
    except Exception as e:
        errors.append(f"Audiobookshelf unavailable ({type(e).__name__})")
    out = [l for _, l in sorted(lines, reverse=True)]
    return out + ([f"_{'; '.join(errors)}_"] if errors else [])


WMO = {0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast", 45: "fog", 48: "freezing fog",
       51: "light drizzle", 53: "drizzle", 55: "heavy drizzle", 61: "light rain", 63: "rain", 65: "heavy rain",
       66: "freezing rain", 67: "heavy freezing rain", 71: "light snow", 73: "snow", 75: "heavy snow",
       77: "snow grains", 80: "light showers", 81: "showers", 82: "violent showers", 85: "snow showers",
       86: "heavy snow showers", 95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with hail"}


def weather(cfg: Config, now_local: datetime) -> list[str]:
    """Open-Meteo (no key): now, today and tomorrow at the configured coordinates."""
    if not cfg.coordinates:
        return ["_no coordinates in journal.json_"]
    lat, lon = cfg.coordinates
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
           "&current=temperature_2m,apparent_temperature,weather_code"
           "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code,sunrise,sunset"
           f"&timezone={cfg.timezone.replace('/', '%2F')}&forecast_days=2")
    out = subprocess.run(["curl", "-4", "-s", "--max-time", "15", url], capture_output=True, text=True, timeout=20)
    d = json.loads(out.stdout)
    cur, day = d["current"], d["daily"]
    lines = [f"- weather:now ({cur['time']}) — {WMO.get(cur['weather_code'], 'code ' + str(cur['weather_code']))}, "
             f"{cur['temperature_2m']}°C (feels {cur['apparent_temperature']}°C)"]
    for i, label in enumerate(("today", "tomorrow")):
        lines.append(f"- weather:{label} ({day['time'][i]}) — {WMO.get(day['weather_code'][i], '?')}, "
                     f"{day['temperature_2m_min'][i]}–{day['temperature_2m_max'][i]}°C, "
                     f"rain chance {day['precipitation_probability_max'][i]}%, "
                     f"sunrise {day['sunrise'][i][-5:]}, sunset {day['sunset'][i][-5:]}")
    return lines


ALL = [
    ("Weather where he is (Open-Meteo)", weather),
    ("tududi — open tasks, habits, done this week", tududi),
    ("AI chats in the last 3 days (chat-scrobbler: ChatGPT/Claude/Gemini browser chats)", scrobbler),
    ("Music in the last 2 days (ListenBrainz)", listenbrainz),
    ("Reading in the last 30 days (Storyteller, Grimmory, Audiobookshelf)", reading),
]
GAPS = "Calendar (Google auth expired) and Trakt watch history (API key rejected) are not connected."

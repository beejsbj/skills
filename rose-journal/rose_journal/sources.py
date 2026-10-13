"""External, read-only context sources for the pack.

Each returns a list of short dated lines. Access routes were verified on
2026-10-13; Google Calendar (gog: invalid_grant) and Trakt (HTTP 403) need
re-authorisation by Burooj before they can be added.
"""
from __future__ import annotations

import json
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


def books(cfg: Config, now_local: datetime) -> list[str]:
    out = subprocess.run(["/home/admin/.local/bin/book-grabber", "history", "--json"],
                         capture_output=True, text=True, timeout=20)
    since = (now_local - timedelta(days=45)).date().isoformat()
    rows = json.loads(out.stdout or "{}").get("data", [])
    return [f"- book:{r.get('title')} — {r.get('author')} (grabbed {str(r.get('date'))[:10]})"
            for r in rows if str(r.get("date", "")) >= since][:8]


ALL = [
    ("tududi — open tasks, habits, done this week", tududi),
    ("AI chats in the last 3 days (chat-scrobbler: ChatGPT/Claude/Gemini browser chats)", scrobbler),
    ("Music in the last 2 days (ListenBrainz)", listenbrainz),
    ("Books grabbed in the last 45 days (book-grabber; not reading progress)", books),
]
GAPS = "Calendar (Google auth expired) and Trakt watch history (API key rejected) are not connected."

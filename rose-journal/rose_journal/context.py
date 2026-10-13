"""Context pack: a dated, sourced snapshot of Burooj's recent life.

Gathered by code before Rose writes an opener, so even a weak model has real
material to work from, and so the validator can check her quotes. Every source
is read-only, time-bounded and optional: a failing source is listed as
unavailable rather than guessed at. Rose may read further with her own tools.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from . import entries, sources
from .config import Config

ROSE_STATE_DB = Path("/home/admin/.hermes/profiles/rose/state.db")
_NOISE = re.compile(r"Gateway message origin \(JSON data.*?insufficient\.\s*", re.S)
_JOURNAL_NOTE = re.compile(r"^\[Journal reply — .*?\]\s*", re.S)


def clean_user_text(text: str) -> str:
    text = _NOISE.sub("", text or "")
    text = _JOURNAL_NOTE.sub("", text)
    return text.strip()


def journal_entries(cfg: Config, limit: int = 6) -> list[str]:
    """Newest journal sections, from daily files and the older one-file-per-ritual layout."""
    found = []
    for p in cfg.root.rglob("*.md"):
        m = re.match(r"(\d{4}-\d{2}-\d{2})(?:-(morning|evening|midweek|weekly|note))?\.md$", p.name)
        if not m or p.parent == cfg.root:  # top-level files are his older hand-written journal
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        if m.group(2):  # legacy layout
            raw = re.search(r"## Raw Entry\n(.*?)(?=\n## |\Z)", body, re.S)
            ann = re.search(r"## Rose's Annotations\n(.*?)(?=\n## |\Z)", body, re.S)
            found.append((m.group(1), m.group(2), raw.group(1).strip() if raw else "",
                          ann.group(1).strip() if ann else ""))
            continue
        for kind in entries.kinds_in(body):
            sec = entries.section(body, kind)
            ann = re.search(r"### Rose's annotations\n(.*?)(?=\n### |\Z)", sec, re.S)
            found.append((m.group(1), kind, entries.raw_entry(body, kind), ann.group(1).strip() if ann else ""))
    out = []
    for date, kind, text, notes in sorted(found, key=lambda f: (f[0], f[1]), reverse=True):
        if text:
            out.append(f"### journal:{date}-{kind}\n{text[:1500]}\n\n_Rose's annotations:_ {notes[:600]}")
        if len(out) >= limit:
            break
    return out


def telegram_messages(tz=None, days: int = 7, limit: int = 25, db: Path = ROSE_STATE_DB) -> list[str]:
    since = (datetime.now() - timedelta(days=days)).timestamp()
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=10)
    try:
        rows = con.execute(
            """select m.timestamp, m.content from messages m join sessions s on s.id = m.session_id
               where s.source = 'telegram' and m.role = 'user' and m.timestamp > ?
                 and m.content not like '[Cron delivery:%' and m.content not like '[IMPORTANT:%'
               order by m.timestamp desc limit ?""",
            (since, limit),
        ).fetchall()
    finally:
        con.close()
    out = []
    for ts, content in reversed(rows):
        text = clean_user_text(content)
        if text:
            stamp = datetime.fromtimestamp(ts).astimezone(tz).isoformat(timespec="minutes")
            out.append(f"- telegram:{stamp} — {text[:700]}")
    return out


def make_verifier(cfg: Config, db: Path = ROSE_STATE_DB):
    """Check a quoted journal/Telegram passage against the full records, not just the pack."""
    from .validate import norm
    cache: dict[str, str] = {}

    def corpus(kind: str) -> str:
        if kind not in cache:
            if kind == "journal":
                texts = [p.read_text(encoding="utf-8", errors="replace") for p in cfg.root.rglob("*.md")]
            else:
                con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=10)
                try:
                    texts = [r[0] or "" for r in con.execute(
                        """select m.content from messages m join sessions s on s.id = m.session_id
                           where s.source = 'telegram' and m.role = 'user'""")]
                finally:
                    con.close()
            cache[kind] = norm("\n".join(texts))
        return cache[kind]

    def verify(source: str, quote_norm: str) -> bool:
        kind = "journal" if source.startswith("journal:") else "telegram"
        return bool(quote_norm) and quote_norm in corpus(kind)

    return verify


def _run(cmd: list[str], timeout: int = 20, env: dict | None = None) -> str:
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                         env={**os.environ, **(env or {})})
    if out.returncode != 0:
        raise RuntimeError((out.stderr or out.stdout).strip()[:200])
    return out.stdout




def build(cfg: Config, now_local: datetime) -> str:
    sections = [
        "# Context pack",
        f"Generated {now_local.isoformat(timespec='minutes')} ({cfg.timezone}). "
        f"Burooj's current location per journal config: {cfg.location or 'not set'}.",
        "Only the facts below (and anything you read yourself in this run) are known. "
        "Do not assume routines, work, or travel that aren't stated here.",
    ]

    def add(title: str, fn) -> None:
        try:
            body = fn()
            body = "\n".join(body) if isinstance(body, list) else str(body)
            sections.append(f"## {title}\n{body.strip() or '_nothing recent_'}")
        except Exception as e:  # a source failing must never block the prompt
            sections.append(f"## {title}\n_unavailable: {type(e).__name__}: {str(e)[:120]}_")

    add("Recent journal entries (newest first)", lambda: journal_entries(cfg))
    add("Burooj's recent Telegram messages to Rose (last 7 days)", lambda: telegram_messages(cfg.tz))
    for title, fn in sources.ALL:
        add(title, lambda fn=fn: fn(cfg, now_local))
    sections.append(f"## Not connected\n{sources.GAPS}")
    return "\n\n".join(sections) + "\n"


def save(cfg: Config, pid: str, text: str) -> Path:
    d = cfg.state_dir / "packs"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{pid}.md"
    p.write_text(text, encoding="utf-8")
    os.chmod(p, 0o600)
    return p

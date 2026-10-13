"""The journal tick: run every few minutes by a Rose `no_agent` cron job.

1. Send any ritual that is due in Burooj's local time.
2. Fold prompts that were answered, or have been visible for collapse_hours.
3. Write Rose's annotations for captured entries that don't have them yet.

Silent when there is nothing to report; prints a line per action otherwise.
"""
from __future__ import annotations

import fcntl
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import agent, compose, context, entries, ledger, prompts, schedule, telegram, validate
from .config import Config, load
from .questions import bank_text

ANNOTATE_ATTEMPTS = 3
KEEP_DAYS = 120


def _opener(cfg: Config, kind: str, now_local: datetime, pid: str) -> tuple[str, str, list]:
    pack = context.build(cfg, now_local)
    context.save(cfg, pid, pack)
    query = prompts.opener_request(kind, now_local, cfg.timezone, cfg.location, pack, bank_text(kind))
    raw = agent.ask(cfg, query, cfg.opener_budget_seconds)
    if raw is None:
        return compose.PLAIN_OPENERS[kind], "plain:agent-failed", []
    data = validate.parse(raw)
    ok, reason = validate.check(kind, data, pack)
    if not ok:
        return compose.PLAIN_OPENERS[kind], f"plain:{reason}", []
    return data["opener"].strip(), "rose", data.get("citations") or []


def send_due(cfg: Config, now_local: datetime, log: list[str], only: str | None = None, dry_run: bool = False) -> None:
    sent_ids = {p["id"] for p in ledger.snapshot(cfg.ledger_path)["prompts"]}
    if only:
        due = [(only, now_local)]
    else:
        due = schedule.due(cfg, now_local, sent_ids)
    for kind, at in due:
        local_date = at.date().isoformat()
        pid = ledger.prompt_id(kind, local_date)
        opener, source, cites = _opener(cfg, kind, now_local, pid)
        html = compose.telegram_html(kind, now_local, opener)
        record = {
            "id": pid, "kind": kind, "local_date": local_date, "scheduled": at.isoformat(),
            "chat_id": cfg.chat_id, "opener": opener, "opener_source": source, "citations": cites,
            "plain_text": compose.plain_text(kind, now_local, opener), "html": html,
        }
        if dry_run:
            log.append(f"[dry-run] {pid} opener_source={source}\n{html}")
            continue
        try:
            record["message_id"] = telegram.send_html(cfg.chat_id, html)
        except telegram.TelegramError as e:
            log.append(f"{pid}: send failed ({e}); retrying plain")
            plain = compose.telegram_html(kind, now_local, compose.PLAIN_OPENERS[kind])
            record.update(opener=compose.PLAIN_OPENERS[kind], opener_source="plain:send-retry", html=plain,
                          plain_text=compose.plain_text(kind, now_local, compose.PLAIN_OPENERS[kind]))
            record["message_id"] = telegram.send_html(cfg.chat_id, plain)
        record["sent_at"] = datetime.now(timezone.utc).isoformat()
        with ledger.locked(cfg.ledger_path) as data:
            if not ledger.find(data, pid):
                data["prompts"].append(record)
        log.append(f"sent {pid} (opener: {source})")


def fold(cfg: Config, now: datetime, log: list[str]) -> None:
    """Shrink answered or expired prompts to a header plus folded questions."""
    window = timedelta(hours=cfg.collapse_hours)
    todo = []
    for p in ledger.snapshot(cfg.ledger_path)["prompts"]:
        if not p.get("message_id"):
            continue
        expired = not p.get("collapsed_at") and now - datetime.fromisoformat(p["sent_at"]) >= window
        if expired or p.get("needs_edit"):
            todo.append(p)
    for p in todo:  # network calls happen outside the ledger lock
        answered = bool(p.get("captures"))
        status = "answered ✓" if answered else "missed — reply anytime"
        sent_local = datetime.fromisoformat(p["sent_at"]).astimezone(cfg.tz)
        error = None
        try:
            telegram.edit_html(p["chat_id"], p["message_id"],
                               compose.telegram_html(p["kind"], sent_local, None, status))
        except telegram.TelegramError as e:
            error = str(e)
            log.append(f"{p['id']}: fold failed ({e})")
        with ledger.locked(cfg.ledger_path) as data:
            q = ledger.find(data, p["id"])
            if q is None:
                continue
            q["collapsed_at"] = q.get("collapsed_at") or now.isoformat()
            if len(q.get("captures", [])) == len(p.get("captures", [])):
                q["needs_edit"] = False  # a reply that landed mid-edit keeps its flag
            if error:
                q["fold_error"] = error
        log.append(f"folded {p['id']} ({status})")


def _rose_reply_after(ts: datetime, db: Path = context.ROSE_STATE_DB) -> str | None:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=10)
    try:
        row = con.execute(
            """select m.content from messages m join sessions s on s.id = m.session_id
               where s.source = 'telegram' and m.role = 'assistant' and m.timestamp > ? and m.timestamp < ?
                 and coalesce(m.content, '') != '' and coalesce(m.tool_calls, '') in ('', '[]')
               order by m.timestamp limit 1""",
            (ts.timestamp(), ts.timestamp() + 3600),
        ).fetchone()
    finally:
        con.close()
    return row[0] if row else None


def annotate(cfg: Config, now: datetime, log: list[str]) -> None:
    snap = ledger.snapshot(cfg.ledger_path)
    for p in snap["prompts"]:
        path = Path(p.get("entry_path") or "")
        if not p.get("captures") or not path.is_file() or p.get("annotate_attempts", 0) >= ANNOTATE_ATTEMPTS:
            continue
        first = datetime.fromisoformat(p["captures"][0]["at"])
        if now - first < timedelta(minutes=cfg.annotate_after_minutes):
            continue
        body = path.read_text(encoding="utf-8")
        if not entries.annotations_pending(body):
            continue
        text = agent.ask(cfg, prompts.annotation_request(body, _rose_reply_after(first)), 180)
        ok = bool(text) and len(text) < 5000 and not text.lstrip().startswith("{")
        if ok:
            entries.write_annotations(path, text)
            log.append(f"annotated {p['id']}")
        with ledger.locked(cfg.ledger_path) as data:
            q = ledger.find(data, p["id"])
            if q is not None:
                q["annotate_attempts"] = q.get("annotate_attempts", 0) + 1
        if not ok:
            log.append(f"{p['id']}: annotation attempt failed")


def prune(cfg: Config, now: datetime) -> None:
    cutoff = (now - timedelta(days=KEEP_DAYS)).isoformat()
    with ledger.locked(cfg.ledger_path) as data:
        data["prompts"] = [p for p in data["prompts"] if p.get("sent_at", p.get("scheduled", "")) >= cutoff]


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cfg = load()
    cfg.state_dir.mkdir(parents=True, exist_ok=True)
    with open(cfg.state_dir / "tick.lock", "a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0  # previous tick still running (e.g. writing an opener)
        now = datetime.now(timezone.utc)
        now_local = now.astimezone(cfg.tz)
        log: list[str] = []
        errors = 0
        only = argv[argv.index("--send") + 1] if "--send" in argv else None
        dry = "--dry-run" in argv
        steps = [lambda: send_due(cfg, now_local, log, only, dry)]
        if not dry and not only:
            steps += [lambda: fold(cfg, now, log), lambda: annotate(cfg, now, log), lambda: prune(cfg, now)]
        for step in steps:
            try:
                step()
            except Exception as e:  # one failing step must not stop the others
                errors += 1
                log.append(f"error: {type(e).__name__}: {e}")
        if log:
            print("\n".join(log))
        return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

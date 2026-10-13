"""Prompt ledger: what was sent, where, and what has been captured.

Lives outside Brain (Brain only ever receives answered entries) and outside
Hermes' home. The gateway plugin and the cron tick both write it, so every
mutation happens under an exclusive flock.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import os
import tempfile
from pathlib import Path


@contextlib.contextmanager
def locked(path: Path):
    """Yield the ledger dict; persist it atomically on clean exit."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(".lock")
    with open(lock_path, "a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            data = _read(path)
            yield data
            _write(path, data)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def snapshot(path: Path) -> dict:
    return _read(path)


def _read(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        data = {}
    data.setdefault("version", 1)
    data.setdefault("prompts", [])
    return data


def _write(path: Path, data: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".ledger-")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def prompt_id(kind: str, local_date: str) -> str:
    return f"{local_date}-{kind}"


def find(data: dict, pid: str) -> dict | None:
    return next((p for p in data["prompts"] if p["id"] == pid), None)


def by_message_id(data: dict, chat_id: str, message_id: str) -> dict | None:
    return next(
        (p for p in data["prompts"]
         if str(p.get("chat_id")) == str(chat_id) and str(p.get("message_id")) == str(message_id)),
        None,
    )

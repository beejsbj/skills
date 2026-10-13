"""Brain journal entries. Code, not the model, owns these files.

An entry exists only once Burooj has answered. Raw text is written verbatim;
later direct replies to the same prompt are appended under their own timestamp.
Annotations are written into their own section and never touch the raw entry.
"""
from __future__ import annotations

import os
import re
import tempfile
from datetime import datetime
from pathlib import Path

from .questions import TITLES

PENDING = "_Pending._"


def entry_path(root: Path, local_date: str, kind: str) -> Path:
    y, m, _ = local_date.split("-")
    return root / y / m / f"{local_date}-{kind}.md"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


def _raw_block(captured_at: datetime, text: str, source: str) -> str:
    label = "voice transcript" if source == "voice" else "text"
    return f"### {captured_at.strftime('%Y-%m-%d %H:%M %Z')} · {label}\n\n{text.rstrip()}\n"


def record_reply(root: Path, prompt: dict, text: str, captured_at: datetime, source: str = "text") -> Path:
    """Write or append Burooj's verbatim reply. Returns the entry path."""
    path = entry_path(root, prompt["local_date"], prompt["kind"])
    block = _raw_block(captured_at, text, source)
    if path.exists():
        body = path.read_text(encoding="utf-8")
        if "## Raw Entry\n\n_None._" in body:  # a shell Rose started; his words go first
            body = body.replace("## Raw Entry\n\n_None._", "## Raw Entry\n\n" + block.rstrip(), 1)
            if "## Rose's Annotations" not in body:
                ann = f"## Rose's Annotations\n\n{PENDING}\n"
                if NOTES_HEADING in body:
                    body = body.replace(NOTES_HEADING, ann + "\n" + NOTES_HEADING, 1)
                else:
                    body = body.rstrip() + "\n\n" + ann
        elif "\n## Rose's Annotations" in body:
            head, tail = body.split("\n## Rose's Annotations", 1)
            body = head.rstrip() + "\n\n" + block + "\n## Rose's Annotations" + tail
        else:
            body = body.rstrip() + "\n\n" + block
        body = set_frontmatter(body, "status", "captured")
        _atomic_write(path, body)
        return path

    fm = [
        "---",
        f"date: {prompt['local_date']}",
        f"kind: {prompt['kind']}",
        "source: telegram",
        "status: captured",
        f"prompt_id: {prompt['id']}",
        f"delivered_at: {prompt.get('sent_at', '')}",
        f"telegram_chat_id: {prompt.get('chat_id', '')}",
        f"telegram_message_id: {prompt.get('message_id') or ''}",
        f"opener_source: {prompt.get('opener_source', '')}",
        "---",
    ]
    title = TITLES[prompt["kind"]].replace(" journal", " Journal").replace(" check-in", " Check-in")
    body = "\n".join(fm) + f"""

# {title} — {prompt['local_date']}

## Orientation Prompt

{prompt.get('plain_text', '').rstrip()}

## Raw Entry

{block}
## Rose's Annotations

{PENDING}
"""
    _atomic_write(path, body)
    return path


def set_frontmatter(body: str, key: str, value: str) -> str:
    m = re.match(r"---\n(.*?)\n---\n", body, re.S)
    if not m:
        return body
    lines = m.group(1).split("\n")
    for i, line in enumerate(lines):
        if line.startswith(f"{key}:"):
            lines[i] = f"{key}: {value}"
            break
    else:
        lines.append(f"{key}: {value}")
    return "---\n" + "\n".join(lines) + "\n---\n" + body[m.end():]


def raw_entry(body: str) -> str:
    m = re.search(r"## Raw Entry\n(.*?)(?=\n## Rose's Annotations|\Z)", body, re.S)
    return m.group(1).strip() if m else ""


_ANNOTATIONS = re.compile(r"## Rose's Annotations\n(.*?)(?=\n## |\Z)", re.S)
NOTES_HEADING = "## Rose's Notes"


def annotations_pending(body: str) -> bool:
    m = _ANNOTATIONS.search(body)
    return bool(m) and m.group(1).strip() in ("", PENDING)


def write_annotations(path: Path, annotations: str) -> None:
    """Replace only the annotations section; raw entry and Rose's notes are untouched."""
    body = path.read_text(encoding="utf-8")
    section = "## Rose's Annotations\n\n" + annotations.strip() + "\n"
    m = _ANNOTATIONS.search(body)
    if m:
        rest = body[m.end():].lstrip("\n")
        body = body[:m.start()] + section + ("\n" + rest if rest else "")
    else:
        body = body.rstrip() + "\n\n" + section
    body = set_frontmatter(body, "status", "complete")
    _atomic_write(path, body)


def add_rose_note(path: Path, text: str, at: datetime) -> None:
    """Append Rose's own timestamped note. Append-only; never touches the raw entry or annotations."""
    body = path.read_text(encoding="utf-8")
    block = f"### {at.strftime('%Y-%m-%d %H:%M %Z')}\n\n{text.strip()}\n"
    if NOTES_HEADING not in body:
        body = body.rstrip() + f"\n\n{NOTES_HEADING}\n\n"
    else:
        body = body.rstrip() + "\n\n"
    _atomic_write(path, body + block)


def create_shell(root: Path, local_date: str, kind: str, orientation: str) -> Path:
    """An entry with no raw text yet (used when Rose adds a note to a day Burooj hasn't written)."""
    path = entry_path(root, local_date, kind)
    if path.exists():
        return path
    title = TITLES[kind].replace(" journal", " Journal").replace(" note", " Note")
    body = f"""---
date: {local_date}
kind: {kind}
source: rose
status: rose-note
---

# {title} — {local_date}

## Orientation Prompt

{orientation}

## Raw Entry

_None._
"""
    _atomic_write(path, body)
    return path

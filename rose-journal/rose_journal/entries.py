"""Brain journal entries: one Markdown file per entry, alongside Burooj's own journal.

Rituals land in `<root>/YYYY-MM-DD-<kind>.md` (morning, evening, midweek, weekly);
each `/j` note is its own `<root>/YYYY-MM-DD-j.md`, `-j-2.md`, … — the same flat,
one-file-per-entry library as his older entries. A file holds the prompt, his
verbatim words (later direct replies append), Rose's annotations and Rose's own
notes. Code, not the model, owns these files; his words are never rewritten.
"""
from __future__ import annotations

import os
import re
import tempfile
from datetime import datetime
from pathlib import Path

from .questions import TITLES, bank_lines

PENDING = "_Pending._"
NO_WORDS = "_Nothing from Burooj yet._"
TITLES_ALL = {**TITLES, "j": "Journal note", "note": "Rose's note"}


def stem_for(local_date: str, kind: str, n: int = 1) -> str:
    suffix = "" if n <= 1 else f"-{n}"
    return f"{local_date}-{kind}{suffix}"


def entry_path(root: Path, stem: str) -> Path:
    return root / f"{stem}.md"


def next_stem(root: Path, local_date: str, kind: str) -> str:
    """First unused stem for a kind that can repeat in a day (/j notes)."""
    n = 1
    while entry_path(root, stem_for(local_date, kind, n)).exists():
        n += 1
    return stem_for(local_date, kind, n)


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


def _prompt_md(prompt: dict) -> str:
    kind = prompt["kind"]
    if kind == "j":
        return "_Freeform — sent with /j._"
    if kind == "note":
        return "_Started by Rose's note._"
    sent = prompt.get("sent_at_local") or ""
    meta = f"_Sent {sent} · opener: {prompt.get('opener_source', '')}_\n\n" if sent else ""
    if prompt.get("asked"):
        meta += "_Woven in: " + "; ".join(f"[{a['id']}] {a['question']}" for a in prompt["asked"]) + "_\n\n"

    def fmt(line: str) -> str:
        if line.startswith("   "):
            return f"> - {line.strip(' •')}"
        return f"> {line}" if kind == "morning" else f"> **{line}**"
    lines = "\n".join(fmt(l) for l in bank_lines(kind))
    opener = (prompt.get("opener") or "").strip()
    return f"{meta}{opener}\n\n> [!question]- Questions\n{lines}".strip()


def _new_file(prompt: dict) -> str:
    date, kind = prompt["local_date"], prompt["kind"]
    day = datetime.strptime(date, "%Y-%m-%d").strftime("%a %-d %b %Y")
    return (f"---\ndate: {date}\nkind: {kind}\ntype: journal\nsource: rose-journal\n---\n\n"
            f"# {TITLES_ALL[kind]} — {day}\n\n## Prompt\n\n{_prompt_md(prompt)}\n\n"
            f"## Burooj\n\n{NO_WORDS}\n\n## Rose's annotations\n\n{PENDING}\n")


def _sub_span(body: str, heading: str) -> tuple[int, int] | None:
    m = re.search(rf"^{re.escape(heading)}\n", body, re.M)
    if not m:
        return None
    nxt = re.search(r"^## ", body[m.end():], re.M)
    return m.end(), (m.end() + nxt.start()) if nxt else len(body)


def _raw_block(at: datetime, text: str, source: str, audio: str | None = None) -> str:
    label = "voice transcript" if source == "voice" else "text"
    embed = f"![[{audio}]]\n\n" if audio else ""
    return f"### {at.strftime('%H:%M %Z')} · {label}\n\n{embed}{text.rstrip()}\n\n"


def record_reply(root: Path, prompt: dict, text: str, captured_at: datetime, source: str = "text",
                 audio: str | None = None) -> Path:
    """Write or append Burooj's verbatim words to this prompt's entry file."""
    path = entry_path(root, prompt["stem"])
    body = path.read_text(encoding="utf-8") if path.exists() else _new_file(prompt)
    span = _sub_span(body, "## Burooj")
    if span is None:  # a file Rose started with a note: add his section before hers
        body = body.replace("## Rose's notes", f"## Burooj\n\n{NO_WORDS}\n\n## Rose's annotations\n\n"
                            f"{PENDING}\n\n## Rose's notes", 1)
        span = _sub_span(body, "## Burooj")
    s, e = span
    words = body[s:e].strip()
    words = "" if words == NO_WORDS else words + "\n\n"
    body = body[:s] + "\n" + words + _raw_block(captured_at, text, source, audio) + body[e:]
    _atomic_write(path, body)
    return path


def raw_entry(body: str) -> str:
    span = _sub_span(body, "## Burooj")
    text = body[span[0]:span[1]].strip() if span else ""
    return "" if text == NO_WORDS else text


def annotations_pending(body: str) -> bool:
    span = _sub_span(body, "## Rose's annotations")
    return bool(span) and body[span[0]:span[1]].strip() in ("", PENDING) and bool(raw_entry(body))


def write_annotations(path: Path, annotations: str) -> None:
    """Replace only the annotations; his words and Rose's notes are untouched."""
    body = path.read_text(encoding="utf-8")
    s, e = _sub_span(body, "## Rose's annotations")
    rest = body[e:].lstrip("\n")
    body = body[:s] + "\n" + annotations.strip() + "\n" + ("\n" + rest if rest else "")
    _atomic_write(path, body)


def add_rose_note(path: Path, text: str, at: datetime, prompt: dict | None = None) -> Path:
    """Append Rose's own timestamped note (creating a Rose-started entry if needed). Append-only."""
    if path.exists():
        body = path.read_text(encoding="utf-8")
    else:
        body = _new_file(prompt).split("## Burooj")[0].rstrip() + "\n"
    note = f"### {at.strftime('%H:%M %Z')}\n\n{text.strip()}\n"
    if "\n## Rose's notes\n" in body:
        body = body.rstrip() + "\n\n" + note
    else:
        body = body.rstrip() + "\n\n## Rose's notes\n\n" + note
    _atomic_write(path, body)
    return path


def entries_on(root: Path, local_date: str) -> list[Path]:
    """Engine entries for a day (not his hand-written files), oldest first."""
    pat = re.compile(rf"^{re.escape(local_date)}-(morning|evening|midweek|weekly|j|note)(-\d+)?\.md$")
    return sorted((p for p in root.glob(f"{local_date}-*.md") if pat.match(p.name)),
                  key=lambda p: p.stat().st_mtime)


def kind_of(path: Path) -> str | None:
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(morning|evening|midweek|weekly|j|note)(-\d+)?\.md$", path.name)
    return m.group(1) if m else None

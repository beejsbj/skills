"""Brain journal entries: one Markdown file per local day. Code, not the model, owns them.

`<root>/YYYY/MM/YYYY-MM-DD.md` holds a section per ritual (morning, evening,
midweek, weekly, /j notes), in the order they happened. Each section has the
prompt, Burooj's verbatim words, Rose's annotations and Rose's own notes.
A section exists only once something was written to it. Raw text is never
rewritten; later replies append under their own timestamp.
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
SECTION_TITLES = {**TITLES, "note": "Notes (/j)"}
_MARK = "<!-- rose-journal:{} -->"
_BLOCK = re.compile(r"^## [^\n]*\n<!-- rose-journal:(\w+) -->\n", re.M)
_SUBS = ("### Prompt", "### Burooj", "### Rose's annotations", "### Rose's notes")


def entry_path(root: Path, local_date: str, kind: str | None = None) -> Path:
    y, m, _ = local_date.split("-")
    return root / y / m / f"{local_date}.md"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


def _skeleton(local_date: str) -> str:
    day = datetime.strptime(local_date, "%Y-%m-%d").strftime("%a %-d %b %Y")
    return f"---\ndate: {local_date}\ntype: journal\nsource: rose-journal\nkinds: []\n---\n\n# {day}\n"


def _span(body: str, kind: str) -> tuple[int, int] | None:
    marks = list(_BLOCK.finditer(body))
    for i, m in enumerate(marks):
        if m.group(1) == kind:
            end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
            return m.start(), end
    return None


def _sub_span(block: str, heading: str) -> tuple[int, int] | None:
    """Span of a ### subsection's body inside a block."""
    m = re.search(rf"^{re.escape(heading)}\n", block, re.M)
    if not m:
        return None
    nxt = re.search(r"^### ", block[m.end():], re.M)
    return m.end(), (m.end() + nxt.start()) if nxt else len(block)


def _set_kinds(body: str) -> str:
    kinds = [m.group(1) for m in _BLOCK.finditer(body)]
    return re.sub(r"^kinds: .*$", f"kinds: [{', '.join(kinds)}]", body, count=1, flags=re.M)


def _prompt_md(prompt: dict) -> str:
    kind = prompt["kind"]
    if kind == "note":
        return "_Freeform — sent with /j._"
    opener = (prompt.get("opener") or "").strip()
    sent = prompt.get("sent_at_local") or ""
    meta = f"_Sent {sent} · opener: {prompt.get('opener_source', '')}_\n\n" if sent else ""
    if prompt.get("asked"):
        meta += "_Woven in: " + "; ".join(f"[{a['id']}] {a['question']}" for a in prompt["asked"]) + "_\n\n"
    def fmt(line: str) -> str:
        if line.startswith("   "):
            return f"> - {line.strip(' •')}"
        return f"> {line}" if kind == "morning" else f"> **{line}**"
    lines = "\n".join(fmt(l) for l in bank_lines(kind))
    return f"{meta}{opener}\n\n> [!question]- Questions\n{lines}".strip()


def _new_block(prompt: dict) -> str:
    kind = prompt["kind"]
    return (f"## {SECTION_TITLES[kind]}\n{_MARK.format(kind)}\n\n### Prompt\n\n{_prompt_md(prompt)}\n\n"
            f"### Burooj\n\n{NO_WORDS}\n\n### Rose's annotations\n\n{PENDING}\n\n")


def _with_block(body: str, prompt: dict) -> tuple[str, tuple[int, int]]:
    span = _span(body, prompt["kind"])
    if span is None:
        body = body.rstrip() + "\n\n" + _new_block(prompt)
        body = _set_kinds(body)
        span = _span(body, prompt["kind"])
    return body, span


def _raw_block(at: datetime, text: str, source: str) -> str:
    label = "voice transcript" if source == "voice" else "text"
    return f"#### {at.strftime('%H:%M %Z')} · {label}\n\n{text.rstrip()}\n\n"


def record_reply(root: Path, prompt: dict, text: str, captured_at: datetime, source: str = "text") -> Path:
    """Write or append Burooj's verbatim words to the day's section for this prompt."""
    path = entry_path(root, prompt["local_date"])
    body = path.read_text(encoding="utf-8") if path.exists() else _skeleton(prompt["local_date"])
    body, (s, e) = _with_block(body, prompt)
    block = body[s:e]
    ss, se = _sub_span(block, "### Burooj")
    words = block[ss:se].strip()
    words = "" if words == NO_WORDS else words + "\n\n"
    block = block[:ss] + "\n" + words + _raw_block(captured_at, text, source) + block[se:]
    _atomic_write(path, body[:s] + block + body[e:])
    return path


def section(body: str, kind: str) -> str:
    span = _span(body, kind)
    return body[span[0]:span[1]] if span else ""


def raw_entry(body: str, kind: str) -> str:
    block = section(body, kind)
    sub = _sub_span(block, "### Burooj")
    text = block[sub[0]:sub[1]].strip() if sub else ""
    return "" if text == NO_WORDS else text


def annotations_pending(body: str, kind: str) -> bool:
    block = section(body, kind)
    sub = _sub_span(block, "### Rose's annotations")
    return bool(sub) and block[sub[0]:sub[1]].strip() in ("", PENDING) and bool(raw_entry(body, kind))


def write_annotations(path: Path, kind: str, annotations: str) -> None:
    """Replace only this section's annotations; his words and Rose's notes are untouched."""
    body = path.read_text(encoding="utf-8")
    s, e = _span(body, kind)
    block = body[s:e]
    ss, se = _sub_span(block, "### Rose's annotations")
    block = block[:ss] + "\n" + annotations.strip() + "\n\n" + block[se:].lstrip("\n")
    _atomic_write(path, body[:s] + block + body[e:])


def add_rose_note(root: Path, local_date: str, kind: str, text: str, at: datetime) -> Path:
    """Append Rose's own timestamped note to a section (created as needed). Append-only."""
    path = entry_path(root, local_date)
    body = path.read_text(encoding="utf-8") if path.exists() else _skeleton(local_date)
    body, (s, e) = _with_block(body, {"kind": kind, "local_date": local_date})
    block = body[s:e]
    note = f"#### {at.strftime('%H:%M %Z')}\n\n{text.strip()}\n\n"
    sub = _sub_span(block, "### Rose's notes")
    if sub:
        block = block[:sub[1]].rstrip("\n") + "\n\n" + note + block[sub[1]:]
    else:
        block = block.rstrip("\n") + "\n\n### Rose's notes\n\n" + note
    _atomic_write(path, body[:s] + block + body[e:])
    return path


def has_section(root: Path, local_date: str, kind: str) -> bool:
    path = entry_path(root, local_date)
    return path.exists() and _span(path.read_text(encoding="utf-8"), kind) is not None


def kinds_in(body: str) -> list[str]:
    return [m.group(1) for m in _BLOCK.finditer(body)]

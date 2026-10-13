"""Ask Rose (full agent: her model chain, tools and MCP servers) for text.

Rose only ever returns text here; code decides what to do with it. A failure,
timeout or invalid answer returns None and the caller degrades gracefully.
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

from .config import Config

HERMES = "/home/admin/.local/bin/hermes"


def ask(cfg: Config, query: str, budget: int, toolsets: str | None = None) -> str | None:
    with tempfile.NamedTemporaryFile("w", suffix=".md", dir=cfg.state_dir, delete=False) as fh:
        fh.write(query)
        qpath = Path(fh.name)
    try:
        out = subprocess.run(
            [HERMES, "-p", cfg.profile, "chat", "--oneshot", "--query-file", str(qpath),
             "--run-budget", str(budget), "--source", "tool", "-Q",
             *(["-t", toolsets] if toolsets else [])],
            capture_output=True, text=True, timeout=budget + 60, cwd=str(cfg.state_dir),
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    finally:
        qpath.unlink(missing_ok=True)
    if out.returncode != 0:
        return None
    text = re.sub(r"\n*session_id:\s*\S+\s*$", "", out.stdout.strip())
    text = "\n".join(l for l in text.splitlines() if not l.startswith("  Command helper:"))
    return text.strip() or None

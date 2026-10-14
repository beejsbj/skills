"""Rose may not change Hermes settings, schedules, skills or the journal engine.

Enforced through Hermes' `pre_tool_call` hook in Rose's profile only. This is
a guardrail against a "helpful" model fixing infrastructure (2026-10-12), not
a security boundary: Rose still runs as the same Unix user, and a shell
denylist cannot be complete. Reads stay allowed so she can investigate and
report; changes go to Otto or Burooj.
"""
from __future__ import annotations

import os
import re

PROTECTED = [
    "/home/admin/.hermes",
    "/mnt/server-ssd/agent-data/admin/.hermes",
    "/home/admin/.config/rose",
    "/home/admin/.local/state/rose-journal",  # pre-2026-10-14 state location
    "/mnt/server-ssd/BJsWorkspace/Projects/skills",
    "/home/admin/.config/systemd",
]
# Brain is Burooj's; Rose may write notes there, but the journal tree belongs to the engine.
JOURNAL_ROOT = "/mnt/server-ssd/BJsWorkspace/Brain/Journal"
ALLOWED_WRITE = ["/home/admin/.hermes/profiles/rose/cache/scratch"]

REFUSAL = (
    "Blocked by the journal guard: Rose doesn't change Hermes settings, cron jobs, skills, "
    "plugins, model routing, or the journal engine. Tell Burooj what you found, or ask Otto "
    "to look into it."
)

_HERMES_ALLOWED = re.compile(
    r"^\s*(?:\S*/)?hermes\s+(?:-p\s+\S+\s+)?(?:chat\b|cron\s+(?:list|status|runs)\b|status\b|--version\b|version\b)"
)
_WRITE_TOKENS = re.compile(
    r"((?<![0-9&])>(?!\s*/dev/null)|\btee\b|\bsed\s+-i|\bcp\b|\bmv\b|\brm\b|\bln\b|\bchmod\b|\bchown\b|\btruncate\b|\binstall\b"
    r"|\brsync\b|\bpython\d?\b|\bperl\b|\bdd\b|\bgit\s+(?:commit|push|checkout|reset|apply|am|stash|merge|rebase)\b)"
)
_SYSTEM = re.compile(r"\b(systemctl|crontab|loginctl|journalctl\s+--vacuum)\b")


def _protected(path: str) -> bool:
    try:
        real = os.path.realpath(os.path.expanduser(path))
    except (TypeError, ValueError):
        return True
    if any(real == a or real.startswith(a + "/") for a in ALLOWED_WRITE):
        return False
    roots = PROTECTED + [JOURNAL_ROOT]
    return any(real == r or real.startswith(r + "/") for r in roots)


def _mentions_protected(cmd: str) -> bool:
    return any(r in cmd for r in PROTECTED + [JOURNAL_ROOT, ".hermes", "config/rose", "rose-journal"])


def _hermes_segments(cmd: str) -> list[str]:
    return [s for s in re.split(r"&&|\|\||;|\||\n|\$\(|`", cmd) if re.search(r"(^|/|\s)hermes(\s|$)", s)]


def check(tool_name: str, args: dict) -> str | None:
    """Return a refusal message, or None to allow."""
    args = args or {}
    if tool_name == "execute_code":
        return REFUSAL + " (execute_code is disabled for Rose; use read-only tools.)"
    if tool_name in ("write_file", "patch"):
        path = args.get("path") or args.get("file_path") or ""
        if not path and isinstance(args.get("patch"), str):
            paths = re.findall(r"^\*\*\* (?:Update|Add|Delete) File: (.+)$", args["patch"], re.M)
            return REFUSAL if any(_protected(p) for p in paths) else None
        return REFUSAL if _protected(path) else None
    if tool_name == "skill_manage":
        return None if str(args.get("action", "")).lower() in ("view", "list", "read") else REFUSAL
    if tool_name == "cronjob_manage":
        return None if str(args.get("action", "")).lower() in ("list", "status", "runs", "get") else REFUSAL
    if tool_name in ("terminal", "process_manage"):
        cmd = str(args.get("command") or args.get("cmd") or "")
        if not cmd:
            return None
        for seg in _hermes_segments(cmd):
            if not _HERMES_ALLOWED.search(seg.strip()):
                return REFUSAL
        if _SYSTEM.search(cmd):
            return REFUSAL
        if _mentions_protected(cmd) and _WRITE_TOKENS.search(cmd):
            return REFUSAL
    return None

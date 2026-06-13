#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
PROFILES_PATH = ROOT / "profiles.json"
HOME = Path.home()
CODEX_SESSIONS = HOME / ".codex" / "sessions"
CLAUDE_PROJECTS = HOME / ".claude" / "projects"
CLAUDE_JOBS = HOME / ".claude" / "jobs"
OPENCODE_DB = HOME / ".local" / "share" / "opencode" / "opencode.db"
CURSOR_ACP_SESSIONS = HOME / ".cursor" / "acp-sessions"
UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)


@dataclass
class Result:
    ok: bool
    verb: str
    provider: str | None
    data: dict[str, Any] | None = None
    warnings: list[str] | None = None
    debug: dict[str, Any] | None = None
    error: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "ok": self.ok,
            "verb": self.verb,
            "provider": self.provider,
            "data": self.data or {},
            "warnings": self.warnings or [],
        }
        if self.debug:
            out["debug"] = self.debug
        if self.error:
            out["error"] = self.error
        return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Provider-neutral top-level agent/session wrapper.")
    sub = parser.add_subparsers(dest="verb", required=True)

    discover = sub.add_parser("discover", help="List non-archived provider-visible sessions.")
    discover.add_argument("--provider", choices=["all", "codex", "claude", "opencode", "cursor"], default="all")
    discover.add_argument("--pretty", action="store_true")

    inspect_p = sub.add_parser("inspect", help="Inspect one provider-visible session.")
    add_provider_id(inspect_p)
    inspect_p.add_argument("--pretty", action="store_true")

    start = sub.add_parser("start", help="Start a durable visible session.")
    add_provider(start)
    start.add_argument("--workspace")
    start.add_argument("--message", required=True)
    start.add_argument("--model")
    start.add_argument("--effort")
    start.add_argument("--isolate", choices=["auto", "none"], default="none")
    start.add_argument("--wait", action="store_true")
    start.add_argument("--attach", action="store_true")
    start.add_argument("--pretty", action="store_true")

    run = sub.add_parser(
        "run",
        help="Cross-provider ephemeral one-shot: prompt a provider, return the answer here, no durable handoff.",
    )
    add_provider(run)
    run.add_argument("--workspace")
    run.add_argument("--message", required=True)
    run.add_argument("--model")
    run.add_argument("--effort")
    run.add_argument("--pretty", action="store_true")

    resume = sub.add_parser("resume", help="Resume or prompt an existing visible session.")
    add_provider_id(resume)
    resume.add_argument("--message")
    resume.add_argument("--no-wait", action="store_true")
    resume.add_argument("--attach", action="store_true")
    resume.add_argument("--pretty", action="store_true")

    fork = sub.add_parser("fork", help="Fork a visible session where the provider supports it.")
    add_provider_id(fork)
    fork.add_argument("--message")
    fork.add_argument("--isolate", choices=["auto", "none"], default="none")
    fork.add_argument("--wait", action="store_true")
    fork.add_argument("--pretty", action="store_true")

    archive = sub.add_parser("archive", help="Archive a visible session where supported.")
    add_provider_id(archive)
    archive.add_argument("--pretty", action="store_true")

    unarchive = sub.add_parser("unarchive", help="Unarchive a visible session where supported.")
    add_provider_id(unarchive)
    unarchive.add_argument("--pretty", action="store_true")

    attach = sub.add_parser("attach", help="Attach/open a visible session interactively.")
    add_provider_id(attach)
    attach.add_argument("--pretty", action="store_true")

    args = parser.parse_args(argv)
    pretty = bool(getattr(args, "pretty", False))

    if getattr(args, "attach", False) and getattr(args, "wait", False):
        return emit(
            Result(
                ok=False,
                verb=args.verb,
                provider=getattr(args, "provider", None),
                error={
                    "code": "attach_wait_conflict",
                    "message": "--attach and --wait are mutually exclusive.",
                },
            ),
            pretty,
        )

    if getattr(args, "isolate", "none") == "auto" and not getattr(args, "workspace", None):
        return emit(
            Result(
                ok=False,
                verb=args.verb,
                provider=getattr(args, "provider", None),
                error={
                    "code": "isolation_requires_workspace",
                    "message": "--isolate auto requires --workspace.",
                },
            ),
            pretty,
        )

    try:
        result = dispatch(args)
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        result = Result(
            ok=False,
            verb=args.verb,
            provider=getattr(args, "provider", None),
            error={"code": "unexpected_error", "message": str(exc)},
        )
    return emit(result, pretty)


def add_provider(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--provider", choices=["codex", "claude", "opencode", "cursor"], required=True)


def add_provider_id(parser: argparse.ArgumentParser) -> None:
    add_provider(parser)
    parser.add_argument("--id", required=True)


def dispatch(args: argparse.Namespace) -> Result:
    if args.verb == "discover":
        return discover(args.provider)
    if args.verb == "inspect":
        return inspect_session(args.provider, args.id)
    if args.verb == "start":
        return start_session(args)
    if args.verb == "run":
        return run_ephemeral(args)
    if args.verb == "resume":
        return resume_session(args)
    if args.verb == "fork":
        return fork_session(args)
    if args.verb == "archive":
        return archive_session(args.provider, args.id)
    if args.verb == "unarchive":
        return unarchive_session(args.provider, args.id)
    if args.verb == "attach":
        return attach_session(args.provider, args.id)
    return Result(
        ok=False,
        verb=args.verb,
        provider=getattr(args, "provider", None),
        error={"code": "unknown_verb", "message": f"Unknown verb: {args.verb}"},
    )


def discover(provider: str) -> Result:
    sessions: list[dict[str, Any]] = []
    warnings: list[str] = []
    if provider in ("all", "codex"):
        try:
            sessions.extend(discover_codex())
        except Exception as exc:
            warnings.append(f"codex discovery failed: {exc}")
    if provider in ("all", "claude"):
        try:
            sessions.extend(discover_claude())
        except Exception as exc:
            warnings.append(f"claude discovery failed: {exc}")
    if provider in ("all", "opencode"):
        try:
            sessions.extend(discover_opencode())
        except Exception as exc:
            warnings.append(f"opencode discovery failed: {exc}")
    if provider in ("all",):
        try:
            sessions.extend(discover_cursor())
        except Exception as exc:
            warnings.append(f"cursor discovery failed: {exc}")
    if provider == "cursor":
        warnings.append("cursor discovery is not supported; sessions have minimal metadata. Use start/resume only.")
    sessions.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return Result(
        ok=True,
        verb="discover",
        provider=provider,
        data={"sessions": sessions},
        warnings=warnings,
    )


def discover_codex() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not CODEX_SESSIONS.exists():
        return out
    for path in CODEX_SESSIONS.rglob("*.jsonl"):
        session = parse_codex_session(path, tail=False)
        if session:
            out.append(session)
    return out


def discover_claude() -> list[dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if CLAUDE_PROJECTS.exists():
        for path in CLAUDE_PROJECTS.rglob("*.jsonl"):
            if "subagents" in path.parts:
                continue
            session = parse_claude_session(path, tail=False)
            if session:
                out[session["id"]] = session

    for job in claude_jobs().values():
        sid = job.get("sessionId") or job.get("resumeSessionId")
        if not isinstance(sid, str):
            continue
        existing = out.get(sid, {})
        updated = merge_session(
            existing,
            {
                "provider": "claude",
                "id": sid,
                "workspace": job.get("cwd") or job.get("originCwd"),
                "title": job.get("name") or existing.get("title") or "Claude session",
                "updated_at": normalize_time(job.get("updatedAt")) or existing.get("updated_at"),
                "created_at": normalize_time(job.get("createdAt")) or existing.get("created_at"),
                "archived": False,
                "source": job.get("linkScanPath") or existing.get("source"),
                "mode": "background",
                "status": job.get("state") or job.get("tempo") or "unknown",
                "cwd_confidence": "high" if job.get("cwd") else existing.get("cwd_confidence"),
            },
        )
        out[sid] = updated
    return list(out.values())


def inspect_session(provider: str, session_id: str) -> Result:
    if provider == "codex":
        session = find_codex_session(session_id, tail=True)
    elif provider == "opencode":
        session = find_opencode_session(session_id, tail=True)
    elif provider == "cursor":
        return Result(
            ok=False,
            verb="inspect",
            provider="cursor",
            error={"code": "cursor_inspect_unsupported", "message": "Cursor agent sessions have minimal metadata. Use start/resume only."},
        )
    else:
        session = find_claude_session(session_id, tail=True)
    if not session:
        return Result(
            ok=False,
            verb="inspect",
            provider=provider,
            error={"code": "session_not_found", "message": f"{provider} session not found: {session_id}"},
        )
    return Result(ok=True, verb="inspect", provider=provider, data={"session": session})


def start_session(args: argparse.Namespace) -> Result:
    warnings = model_warnings(args.provider, args.model)
    if args.provider == "claude":
        return start_claude(args, warnings)
    if args.provider == "opencode":
        return start_opencode(args, warnings)
    if args.provider == "cursor":
        return start_cursor(args, warnings)
    return start_codex(args, warnings)


def start_claude(args: argparse.Namespace, warnings: list[str]) -> Result:
    command = ["claude"]
    if args.attach:
        pass
    elif args.wait:
        command.extend(["--print", "--output-format", "json"])
    else:
        command.append("--bg")

    if args.workspace:
        command = with_cwd(command, args.workspace)
    if args.model:
        command.extend(["--model", args.model])
    if args.effort:
        command.extend(["--effort", args.effort])
    if args.isolate == "auto":
        command.extend(["--worktree", isolate_name(args.workspace)])
    command.append(args.message)

    if args.attach:
        return run_attached(command, "start", "claude")
    completed = run_command(command, cwd=args.workspace)
    data = command_result_data(completed)
    sid = extract_uuid(completed.stdout) or extract_uuid(completed.stderr)
    if sid:
        data["id"] = sid
    return Result(
        ok=completed.returncode == 0,
        verb="start",
        provider="claude",
        data=data,
        warnings=warnings,
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def start_codex(args: argparse.Namespace, warnings: list[str]) -> Result:
    if args.attach:
        command = ["codex"]
        add_codex_run_flags(command, args)
        command.append(args.message)
        return run_attached(command, "start", "codex", cwd=args.workspace)
    if not args.wait:
        return unsupported(
            "start",
            "codex",
            "codex_detached_start_unsupported",
            "Codex CLI v0.136.0 has no local detached start. Use --wait, --attach, or a Codex app/thread tool.",
            warnings=warnings,
        )
    command = ["codex", "exec"]
    add_codex_run_flags(command, args)
    command.append(args.message)
    completed = run_command(command, cwd=args.workspace)
    data = command_result_data(completed)
    sid = extract_codex_session_id(completed.stdout) or extract_codex_session_id(completed.stderr)
    if sid:
        data["id"] = sid
    return Result(
        ok=completed.returncode == 0,
        verb="start",
        provider="codex",
        data=data,
        warnings=warnings,
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def run_ephemeral(args: argparse.Namespace) -> Result:
    """Cross-provider one-shot. Returns the answer here; no durable session is handed off.

    codex and claude support true no-persistence. opencode and cursor have no
    ephemeral flag, so they create a disposable session whose row still persists;
    we surface that session id and warn so it can be archived or ignored.
    """
    warnings = model_warnings(args.provider, args.model)
    if args.provider == "claude":
        return run_claude(args, warnings)
    if args.provider == "opencode":
        return run_opencode(args, warnings)
    if args.provider == "cursor":
        return run_cursor(args, warnings)
    return run_codex(args, warnings)


def run_codex(args: argparse.Namespace, warnings: list[str]) -> Result:
    if args.effort:
        warnings.append("codex exec has no effort flag; --effort ignored.")
    command = ["codex", "exec"]
    if args.workspace:
        command.extend(["--cd", args.workspace])
    if args.model:
        command.extend(["--model", args.model])
    command.extend(["--sandbox", "read-only", "--ephemeral"])
    command.append(args.message)
    completed = run_command(command, cwd=args.workspace)
    return Result(
        ok=completed.returncode == 0,
        verb="run",
        provider="codex",
        data=command_result_data(completed),
        warnings=warnings,
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def run_claude(args: argparse.Namespace, warnings: list[str]) -> Result:
    command = ["claude", "--print", "--no-session-persistence", "--output-format", "json"]
    if args.model:
        command.extend(["--model", args.model])
    if args.effort:
        command.extend(["--effort", args.effort])
    command.append(args.message)
    completed = run_command(command, cwd=args.workspace)
    return Result(
        ok=completed.returncode == 0,
        verb="run",
        provider="claude",
        data=command_result_data(completed),
        warnings=warnings,
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def run_opencode(args: argparse.Namespace, warnings: list[str]) -> Result:
    command = ["opencode", "run", "--format", "json"]
    if args.model:
        command.extend(["--model", args.model])
    if args.effort:
        command.extend(["--variant", args.effort])
    if args.workspace:
        command.extend(["--dir", args.workspace])
    command.append(args.message)
    completed = run_command(command, cwd=args.workspace)
    data = command_result_data(completed)
    sid = extract_opencode_session_id(completed.stdout) or extract_opencode_session_id(completed.stderr)
    if sid:
        data["id"] = sid
        warnings.append(
            f"opencode has no ephemeral mode; session {sid} persists. Archive it or ignore it."
        )
    return Result(
        ok=completed.returncode == 0,
        verb="run",
        provider="opencode",
        data=data,
        warnings=warnings,
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def run_cursor(args: argparse.Namespace, warnings: list[str]) -> Result:
    if args.effort:
        warnings.append("cursor agent has no effort flag; --effort ignored.")
    command = ["cursor", "agent", "--print"]
    if args.model:
        command.extend(["--model", args.model])
    if args.workspace:
        command.extend(["--workspace", args.workspace])
    command.append(args.message)
    completed = run_command(command, cwd=args.workspace)
    warnings.append("cursor agent has no ephemeral mode; a session may persist and cannot be reliably discovered.")
    return Result(
        ok=completed.returncode == 0,
        verb="run",
        provider="cursor",
        data=command_result_data(completed),
        warnings=warnings,
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def resume_session(args: argparse.Namespace) -> Result:
    if args.provider == "claude":
        return resume_claude(args)
    if args.provider == "opencode":
        return resume_opencode(args)
    if args.provider == "cursor":
        return resume_cursor(args)
    return resume_codex(args)


def resume_claude(args: argparse.Namespace) -> Result:
    command = ["claude", "--resume", args.id]
    if args.attach:
        if args.message:
            command.append(args.message)
        return run_attached(command, "resume", "claude")
    if args.no_wait:
        command.insert(1, "--bg")
    else:
        command.extend(["--print", "--output-format", "json"])
    if args.message:
        command.append(args.message)
    completed = run_command(command)
    return Result(
        ok=completed.returncode == 0,
        verb="resume",
        provider="claude",
        data=command_result_data(completed),
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def resume_codex(args: argparse.Namespace) -> Result:
    if args.attach:
        command = ["codex", "resume", args.id]
        if args.message:
            command.append(args.message)
        return run_attached(command, "resume", "codex")
    if args.no_wait:
        return unsupported(
            "resume",
            "codex",
            "codex_detached_resume_unsupported",
            "Codex CLI v0.136.0 has no local detached resume submission.",
        )
    command = ["codex", "exec", "resume", args.id]
    if args.message:
        command.append(args.message)
    completed = run_command(command)
    return Result(
        ok=completed.returncode == 0,
        verb="resume",
        provider="codex",
        data=command_result_data(completed),
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def fork_session(args: argparse.Namespace) -> Result:
    if args.provider == "claude":
        command = ["claude", "--resume", args.id, "--fork-session"]
        if args.wait:
            command.extend(["--print", "--output-format", "json"])
        else:
            command.append("--bg")
        if args.isolate == "auto":
            command.extend(["--worktree", isolate_name(None)])
        if args.message:
            command.append(args.message)
        completed = run_command(command)
        data = command_result_data(completed)
        sid = extract_uuid(completed.stdout) or extract_uuid(completed.stderr)
        if sid:
            data["id"] = sid
        return Result(
            ok=completed.returncode == 0,
            verb="fork",
            provider="claude",
            data=data,
            debug={"native_action": command},
            error=error_from_completed(completed),
        )

    if args.provider == "opencode":
        command = ["opencode", "run", "--session", args.id, "--fork"]
        if args.wait:
            command.extend(["--format", "json"])
        else:
            command.extend(["--format", "json"])
        if args.model:
            command.extend(["--model", args.model])
        if args.isolate == "auto":
            command.extend(["--dir", isolate_name(args.workspace)])
        if args.message:
            command.extend(args.message.split())
        completed = run_command(command, cwd=args.workspace)
        data = command_result_data(completed)
        sid = extract_opencode_session_id(completed.stdout) or extract_opencode_session_id(completed.stderr)
        if sid:
            data["id"] = sid
        return Result(
            ok=completed.returncode == 0,
            verb="fork",
            provider="opencode",
            data=data,
            warnings=args.isolate == "auto" and ["opencode fork isolation uses --dir, not native worktrees."] or [],
            debug={"native_action": command},
            error=error_from_completed(completed),
        )

    if args.provider == "cursor":
        return unsupported(
            "fork",
            "cursor",
            "cursor_fork_unsupported",
            "Cursor agent CLI does not support forking sessions.",
        )

    if args.isolate == "auto":
        return unsupported(
            "fork",
            "codex",
            "codex_fork_isolation_unsupported",
            "Codex CLI fork has no local isolation/worktree flag. Fork first, then move/handoff with native app tooling if needed.",
        )
    command = ["codex", "fork", args.id]
    if args.message:
        command.append(args.message)
    return run_attached(command, "fork", "codex")


def archive_session(provider: str, session_id: str) -> Result:
    if provider == "claude":
        return unsupported(
            "archive",
            "claude",
            "claude_archive_unsupported",
            "Claude CLI exposes stop/rm, but no non-destructive archive matching cockpit semantics.",
        )
    if provider == "opencode":
        return unsupported(
            "archive",
            "opencode",
            "opencode_archive_unsupported",
            "opencode session delete is destructive. Use cockpit-level state tracking instead.",
        )
    if provider == "cursor":
        return unsupported(
            "archive",
            "cursor",
            "cursor_archive_unsupported",
            "Cursor agent CLI does not support archiving sessions.",
        )
    command = ["codex", "archive", session_id]
    completed = run_command(command)
    return Result(
        ok=completed.returncode == 0,
        verb="archive",
        provider="codex",
        data={"id": session_id, "archived": completed.returncode == 0, **command_result_data(completed)},
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def unarchive_session(provider: str, session_id: str) -> Result:
    if provider == "claude":
        return unsupported(
            "unarchive",
            "claude",
            "claude_unarchive_unsupported",
            "Claude CLI exposes no archive/unarchive pair matching cockpit semantics.",
        )
    if provider == "opencode":
        return unsupported(
            "unarchive",
            "opencode",
            "opencode_unarchive_unsupported",
            "opencode has no archive/unarchive pair. Use cockpit-level state tracking instead.",
        )
    if provider == "cursor":
        return unsupported(
            "unarchive",
            "cursor",
            "cursor_unarchive_unsupported",
            "Cursor agent CLI does not support unarchiving sessions.",
        )
    command = ["codex", "unarchive", session_id]
    completed = run_command(command)
    return Result(
        ok=completed.returncode == 0,
        verb="unarchive",
        provider="codex",
        data={"id": session_id, "archived": False, **command_result_data(completed)},
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def attach_session(provider: str, session_id: str) -> Result:
    if provider == "codex":
        return run_attached(["codex", "resume", session_id], "attach", "codex")
    if provider == "opencode":
        return run_attached(["opencode", "--session", session_id], "attach", "opencode")
    if provider == "cursor":
        return run_attached(["cursor", "agent", "--resume", session_id], "attach", "cursor")
    job = find_claude_job(session_id)
    if job and job.get("daemonShort"):
        return run_attached(["claude", "attach", str(job["daemonShort"])], "attach", "claude")
    return run_attached(["claude", "--resume", session_id], "attach", "claude")


def discover_opencode() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    completed = run_command(["opencode", "session", "list", "--format", "json"])
    if completed.returncode == 0 and completed.stdout.strip():
        try:
            sessions = json.loads(completed.stdout)
            if isinstance(sessions, list):
                for s in sessions:
                    if not isinstance(s, dict):
                        continue
                    sid = s.get("id")
                    if not sid:
                        continue
                    model_raw = s.get("model")
                    model_str = None
                    if isinstance(model_raw, dict):
                        model_str = model_raw.get("id")
                    elif isinstance(model_raw, str):
                        model_str = model_raw
                    out.append(prune_none({
                        "provider": "opencode",
                        "id": str(sid),
                        "workspace": s.get("directory"),
                        "title": s.get("title") or "opencode session",
                        "updated_at": normalize_time(opencode_ts_to_iso(s.get("updated"))),
                        "created_at": normalize_time(opencode_ts_to_iso(s.get("created"))),
                        "archived": False,
                        "source": "opencode session list",
                        "model": model_str,
                        "mode": "interactive",
                        "cwd_confidence": "high" if s.get("directory") else "low",
                        "status": "unknown",
                        "running": None,
                    }))
                return out
        except (json.JSONDecodeError, TypeError):
            pass
    return discover_opencode_from_db()


def discover_opencode_from_db() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not OPENCODE_DB.exists():
        return out
    try:
        import sqlite3
        conn = sqlite3.connect(str(OPENCODE_DB))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, title, directory, model, time_created, time_updated FROM session ORDER BY time_updated DESC"
        ).fetchall()
        conn.close()
    except Exception:
        return out
    for row in rows:
        model_raw = row["model"]
        model_str = None
        if model_raw:
            try:
                model_data = json.loads(model_raw)
                model_str = model_data.get("id") if isinstance(model_data, dict) else str(model_raw)
            except (json.JSONDecodeError, TypeError):
                model_str = str(model_raw)
        out.append(prune_none({
            "provider": "opencode",
            "id": row["id"],
            "workspace": row["directory"],
            "title": row["title"] or "opencode session",
            "updated_at": normalize_time(opencode_ts_to_iso(row["time_updated"])),
            "created_at": normalize_time(opencode_ts_to_iso(row["time_created"])),
            "archived": False,
            "source": f"sqlite:{OPENCODE_DB}",
            "model": model_str,
            "mode": "interactive",
            "cwd_confidence": "high" if row["directory"] else "low",
            "status": "unknown",
            "running": None,
        }))
    return out


def discover_cursor() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not CURSOR_ACP_SESSIONS.exists():
        return out
    for meta_path in CURSOR_ACP_SESSIONS.glob("*/meta.json"):
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        sid = meta_path.parent.name
        cwd = data.get("cwd")
        out.append(prune_none({
            "provider": "cursor",
            "id": sid,
            "workspace": cwd,
            "title": "cursor agent session",
            "updated_at": file_time(meta_path),
            "created_at": file_time(meta_path),
            "archived": False,
            "source": str(meta_path),
            "mode": "interactive",
            "cwd_confidence": "high" if cwd else "low",
            "status": "unknown",
            "running": None,
        }))
    return out


def find_opencode_session(session_id: str, tail: bool) -> dict[str, Any] | None:
    completed = run_command(["opencode", "export", session_id])
    if completed.returncode == 0 and completed.stdout.strip():
        try:
            data = json.loads(completed.stdout)
            info = data.get("info", {})
            model_raw = info.get("model")
            model_str = None
            if isinstance(model_raw, dict):
                model_str = model_raw.get("id")
            elif isinstance(model_raw, str):
                model_str = model_raw
            session: dict[str, Any] = prune_none({
                "provider": "opencode",
                "id": info.get("id", session_id),
                "workspace": info.get("directory"),
                "title": info.get("title") or "opencode session",
                "updated_at": normalize_time(opencode_ts_to_iso(info.get("time", {}).get("updated"))),
                "created_at": normalize_time(opencode_ts_to_iso(info.get("time", {}).get("created"))),
                "archived": False,
                "source": "opencode export",
                "model": model_str,
                "mode": "interactive",
                "cwd_confidence": "high" if info.get("directory") else "low",
                "status": "unknown",
                "running": None,
            })
            if tail:
                messages = data.get("messages", [])
                tail_events: list[dict[str, Any]] = []
                last_user = ""
                last_assistant = ""
                for msg in messages[-20:]:
                    role = msg.get("role", "unknown")
                    text = text_from_content(msg.get("content")) if isinstance(msg.get("content"), (str, list)) else str(msg.get("content", ""))
                    compacted = compact(text, 1000)
                    tail_events.append({"role": role, "text": compacted, "timestamp": None})
                    if role == "user":
                        last_user = compact(text, 600)
                    if role == "assistant":
                        last_assistant = compact(text, 600)
                session["tail"] = {
                    "last_user": last_user,
                    "last_assistant": last_assistant,
                    "last_events": tail_events,
                }
            return session
        except (json.JSONDecodeError, TypeError):
            pass
    return find_opencode_session_from_db(session_id, tail)


def find_opencode_session_from_db(session_id: str, tail: bool) -> dict[str, Any] | None:
    if not OPENCODE_DB.exists():
        return None
    try:
        import sqlite3
        conn = sqlite3.connect(str(OPENCODE_DB))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, title, directory, model, time_created, time_updated FROM session WHERE id = ?",
            (session_id,),
        ).fetchall()
        conn.close()
    except Exception:
        return None
    if not rows:
        return None
    row = rows[0]
    model_raw = row["model"]
    model_str = None
    if model_raw:
        try:
            model_data = json.loads(model_raw)
            model_str = model_data.get("id") if isinstance(model_data, dict) else str(model_raw)
        except (json.JSONDecodeError, TypeError):
            model_str = str(model_raw)
    return prune_none({
        "provider": "opencode",
        "id": row["id"],
        "workspace": row["directory"],
        "title": row["title"] or "opencode session",
        "updated_at": normalize_time(opencode_ts_to_iso(row["time_updated"])),
        "created_at": normalize_time(opencode_ts_to_iso(row["time_created"])),
        "archived": False,
        "source": f"sqlite:{OPENCODE_DB}",
        "model": model_str,
        "mode": "interactive",
        "cwd_confidence": "high" if row["directory"] else "low",
        "status": "unknown",
        "running": None,
        "tail": None,
    })


def start_opencode(args: argparse.Namespace, warnings: list[str]) -> Result:
    command = ["opencode", "run"]
    if args.model:
        command.extend(["--model", args.model])
    if args.workspace:
        command.extend(["--dir", args.workspace])
    if args.isolate == "auto":
        command.extend(["--worktree", isolate_name(args.workspace)])
    command.extend(["--format", "json"])
    command.extend(args.message.split())
    if args.attach:
        non_json_cmd = ["opencode", "run"]
        if args.model:
            non_json_cmd.extend(["--model", args.model])
        if args.workspace:
            non_json_cmd.extend(["--dir", args.workspace])
        non_json_cmd.extend(args.message.split())
        return run_attached(non_json_cmd, "start", "opencode", cwd=args.workspace)
    completed = run_command(command, cwd=args.workspace)
    data = command_result_data(completed)
    sid = extract_opencode_session_id(completed.stdout) or extract_opencode_session_id(completed.stderr)
    if sid:
        data["id"] = sid
    return Result(
        ok=completed.returncode == 0,
        verb="start",
        provider="opencode",
        data=data,
        warnings=warnings,
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def start_cursor(args: argparse.Namespace, warnings: list[str]) -> Result:
    command = ["cursor", "agent"]
    if args.model:
        command.extend(["--model", args.model])
    if args.workspace:
        command.extend(["--workspace", args.workspace])
    if args.isolate == "auto":
        command.extend(["--worktree", isolate_name(args.workspace)])
    if args.attach:
        if args.message:
            command.extend(args.message.split())
        return run_attached(command, "start", "cursor", cwd=args.workspace)
    command.extend(["--print"])
    if args.message:
        command.extend(args.message.split())
    completed = run_command(command, cwd=args.workspace)
    data = command_result_data(completed)
    return Result(
        ok=completed.returncode == 0,
        verb="start",
        provider="cursor",
        data=data,
        warnings=warnings,
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def resume_opencode(args: argparse.Namespace) -> Result:
    command = ["opencode", "run", "--session", args.id, "--format", "json"]
    if args.model:
        command.extend(["--model", args.model])
    if args.message:
        command.extend(args.message.split())
    if args.attach:
        non_json_cmd = ["opencode", "--session", args.id]
        if args.message:
            non_json_cmd.extend(args.message.split())
        return run_attached(non_json_cmd, "resume", "opencode")
    completed = run_command(command)
    data = command_result_data(completed)
    sid = extract_opencode_session_id(completed.stdout) or args.id
    data["id"] = sid
    return Result(
        ok=completed.returncode == 0,
        verb="resume",
        provider="opencode",
        data=data,
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def resume_cursor(args: argparse.Namespace) -> Result:
    command = ["cursor", "agent", "--resume", args.id]
    if args.model:
        command.extend(["--model", args.model])
    if args.attach:
        if args.message:
            command.extend(args.message.split())
        return run_attached(command, "resume", "cursor")
    command.append("--print")
    if args.message:
        command.extend(args.message.split())
    completed = run_command(command)
    return Result(
        ok=completed.returncode == 0,
        verb="resume",
        provider="cursor",
        data=command_result_data(completed),
        debug={"native_action": command},
        error=error_from_completed(completed),
    )


def opencode_ts_to_iso(ts: Any) -> str | None:
    if ts is None:
        return None
    try:
        ms = int(ts)
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    except (ValueError, TypeError, OSError):
        return None


def extract_opencode_session_id(text: str) -> str | None:
    match = re.search(r"(ses_[A-Za-z0-9]+)", text or "")
    return match.group(1) if match else None


def parse_codex_session(path: Path, tail: bool) -> dict[str, Any] | None:
    meta: dict[str, Any] = {}
    title = ""
    updated_at = ""
    created_at = ""
    model = None
    tail_events: deque[dict[str, Any]] = deque(maxlen=20)
    last_user = ""
    last_assistant = ""

    for obj in iter_jsonl(path):
        typ = obj.get("type")
        timestamp = normalize_time(obj.get("timestamp"))
        if timestamp:
            updated_at = timestamp
            if not created_at:
                created_at = timestamp
        payload = obj.get("payload")
        if typ == "session_meta" and isinstance(payload, dict):
            meta = payload
        if isinstance(payload, dict):
            model = payload.get("model") or model
        text, role = text_from_codex_obj(obj)
        if text:
            if not title and role == "user":
                title = compact(text, 80)
            if role == "user":
                last_user = compact(text, 600)
            if role == "assistant":
                last_assistant = compact(text, 600)
            if tail:
                tail_events.append({"role": role or "unknown", "text": compact(text, 1000), "timestamp": timestamp})

    sid = meta.get("id") or extract_uuid(path.name)
    if not sid:
        return None
    workspace = meta.get("cwd")
    return prune_none(
        {
            "provider": "codex",
            "id": sid,
            "workspace": workspace,
            "title": title or "Codex session",
            "updated_at": updated_at or file_time(path),
            "archived": False,
            "source": str(path),
            "created_at": normalize_time(meta.get("timestamp")) or created_at,
            "model": model,
            "mode": "noninteractive" if meta.get("thread_source") == "exec" else "interactive",
            "cwd_confidence": "high" if workspace else "low",
            "status": "unknown",
            "running": None,
            "tail": {
                "last_user": last_user,
                "last_assistant": last_assistant,
                "last_events": list(tail_events),
            }
            if tail
            else None,
        }
    )


def parse_claude_session(path: Path, tail: bool) -> dict[str, Any] | None:
    sid = path.stem
    workspace = None
    title = ""
    updated_at = ""
    created_at = ""
    model = None
    tail_events: deque[dict[str, Any]] = deque(maxlen=20)
    last_user = ""
    last_assistant = ""

    for obj in iter_jsonl(path):
        timestamp = normalize_time(obj.get("timestamp"))
        if timestamp:
            updated_at = timestamp
            if not created_at:
                created_at = timestamp
        sid = obj.get("sessionId") or sid
        workspace = obj.get("cwd") or workspace
        model = obj.get("model") or model
        text, role = text_from_claude_obj(obj)
        if text:
            if not title and role == "user":
                title = compact(text, 80)
            if role == "user":
                last_user = compact(text, 600)
            if role == "assistant":
                last_assistant = compact(text, 600)
            if tail:
                tail_events.append({"role": role or "unknown", "text": compact(text, 1000), "timestamp": timestamp})

    if not sid:
        return None
    job = find_claude_job(str(sid))
    status = (job or {}).get("state") or (job or {}).get("tempo") or "unknown"
    return prune_none(
        {
            "provider": "claude",
            "id": str(sid),
            "workspace": workspace,
            "title": title or (job or {}).get("name") or "Claude session",
            "updated_at": normalize_time((job or {}).get("updatedAt")) or updated_at or file_time(path),
            "archived": False,
            "source": str(path),
            "created_at": normalize_time((job or {}).get("createdAt")) or created_at,
            "model": model,
            "mode": "background" if job else "interactive",
            "cwd_confidence": "high" if workspace else "low",
            "status": status,
            "running": status in {"running", "active", "busy"},
            "tail": {
                "last_user": last_user,
                "last_assistant": last_assistant,
                "last_events": list(tail_events),
            }
            if tail
            else None,
        }
    )


def find_codex_session(session_id: str, tail: bool) -> dict[str, Any] | None:
    if not CODEX_SESSIONS.exists():
        return None
    for path in CODEX_SESSIONS.rglob(f"*{session_id}*.jsonl"):
        session = parse_codex_session(path, tail=tail)
        if session and session.get("id") == session_id:
            return session
    for path in CODEX_SESSIONS.rglob("*.jsonl"):
        session = parse_codex_session(path, tail=tail)
        if session and session.get("id") == session_id:
            return session
    return None


def find_claude_session(session_id: str, tail: bool) -> dict[str, Any] | None:
    if CLAUDE_PROJECTS.exists():
        for path in CLAUDE_PROJECTS.rglob(f"{session_id}.jsonl"):
            if "subagents" not in path.parts:
                return parse_claude_session(path, tail=tail)
        for path in CLAUDE_PROJECTS.rglob("*.jsonl"):
            if "subagents" in path.parts:
                continue
            session = parse_claude_session(path, tail=tail)
            if session and session.get("id") == session_id:
                return session
    job = find_claude_job(session_id)
    if job:
        return prune_none(
            {
                "provider": "claude",
                "id": session_id,
                "workspace": job.get("cwd") or job.get("originCwd"),
                "title": job.get("name") or "Claude session",
                "updated_at": normalize_time(job.get("updatedAt")),
                "created_at": normalize_time(job.get("createdAt")),
                "archived": False,
                "source": job.get("linkScanPath"),
                "mode": "background",
                "status": job.get("state") or job.get("tempo") or "unknown",
                "running": job.get("state") in {"running", "active", "busy"},
            }
        )
    return None


def iter_jsonl(path: Path):
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def text_from_codex_obj(obj: dict[str, Any]) -> tuple[str, str | None]:
    payload = obj.get("payload")
    if not isinstance(payload, dict):
        return "", None
    role = payload.get("role")
    content = payload.get("content")
    return text_from_content(content), role


def text_from_claude_obj(obj: dict[str, Any]) -> tuple[str, str | None]:
    typ = obj.get("type")
    message = obj.get("message")
    if isinstance(message, dict):
        role = message.get("role") or typ
        return text_from_content(message.get("content")), role
    return text_from_content(obj.get("content")), typ


def text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                value = item.get("text") or item.get("content")
                if isinstance(value, str):
                    parts.append(value)
        return "\n".join(parts)
    if isinstance(content, dict):
        value = content.get("text") or content.get("content")
        if isinstance(value, str):
            return value
    return ""


def claude_jobs() -> dict[str, dict[str, Any]]:
    jobs: dict[str, dict[str, Any]] = {}
    if not CLAUDE_JOBS.exists():
        return jobs
    for path in CLAUDE_JOBS.glob("*/state.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        sid = data.get("sessionId") or data.get("resumeSessionId")
        if isinstance(sid, str):
            data["daemonShort"] = path.parent.name
            jobs[sid] = data
    return jobs


def find_claude_job(session_id: str) -> dict[str, Any] | None:
    for sid, job in claude_jobs().items():
        if session_id in {sid, job.get("resumeSessionId"), job.get("daemonShort")}:
            return job
    return None


def model_warnings(provider: str, model: str | None) -> list[str]:
    if not model:
        return []
    try:
        profiles = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ["profiles.json could not be read; passing model through."]
    for profile in profiles:
        if profile.get("provider") == provider and profile.get("model") == model:
            return []
    return [f"Model {provider}:{model} not found in profiles.json; passing through to provider CLI."]


def add_codex_run_flags(command: list[str], args: argparse.Namespace) -> None:
    if args.workspace:
        command.extend(["--cd", args.workspace])
    if args.model:
        command.extend(["--model", args.model])
    if args.isolate == "auto":
        worktree = create_git_worktree(Path(args.workspace))
        command[command.index(args.workspace)] = str(worktree)


def create_git_worktree(workspace: Path) -> Path:
    root = git_root(workspace)
    if not root:
        raise RuntimeError(f"Cannot isolate non-git workspace: {workspace}")
    name = isolate_name(str(root))
    parent = root.parent / ".agent-worktrees"
    parent.mkdir(exist_ok=True)
    target = parent / name
    if target.exists():
        return target
    subprocess.run(["git", "worktree", "add", "-b", name, str(target)], cwd=root, check=True)
    return target


def git_root(path: Path) -> Path | None:
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return None
    return Path(completed.stdout.strip())


def isolate_name(workspace: str | None) -> str:
    base = "agent"
    if workspace:
        base = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(workspace).name).strip("-") or "agent"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{base}-agent-{stamp}"


def with_cwd(command: list[str], workspace: str) -> list[str]:
    return command


def run_command(command: list[str], cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_attached(command: list[str], verb: str, provider: str, cwd: str | None = None) -> Result:
    completed = subprocess.run(command, cwd=cwd)
    return Result(
        ok=completed.returncode == 0,
        verb=verb,
        provider=provider,
        data={"exit_code": completed.returncode},
        debug={"native_action": command},
        error=None
        if completed.returncode == 0
        else {"code": "native_command_failed", "message": f"Native command exited {completed.returncode}."},
    )


def command_result_data(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    return {
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def error_from_completed(completed: subprocess.CompletedProcess[str]) -> dict[str, str] | None:
    if completed.returncode == 0:
        return None
    return {
        "code": "native_command_failed",
        "message": (completed.stderr or completed.stdout or f"Native command exited {completed.returncode}.").strip(),
    }


def unsupported(
    verb: str,
    provider: str,
    code: str,
    message: str,
    warnings: list[str] | None = None,
) -> Result:
    return Result(
        ok=False,
        verb=verb,
        provider=provider,
        warnings=warnings or [],
        error={"code": code, "message": message},
    )


def merge_session(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in extra.items():
        if value is not None:
            out[key] = value
    out.setdefault("archived", False)
    return out


def prune_none(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if item is not None}


def compact(text: str, limit: int) -> str:
    one = re.sub(r"\s+", " ", text).strip()
    if len(one) <= limit:
        return one
    return one[: limit - 1].rstrip() + "..."


def extract_uuid(text: str) -> str | None:
    match = UUID_RE.search(text or "")
    return match.group(0) if match else None


def extract_codex_session_id(text: str) -> str | None:
    match = re.search(r"session id:\s*([0-9a-f-]{36})", text or "", re.IGNORECASE)
    return match.group(1) if match else extract_uuid(text)


def normalize_time(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    if value.endswith("Z"):
        return value
    return value


def file_time(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def emit(result: Result, pretty: bool) -> int:
    payload = result.as_dict()
    if pretty:
        print_pretty(payload)
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.ok else 1


def print_pretty(payload: dict[str, Any]) -> None:
    print(f"{payload['verb']} {payload.get('provider')}: {'ok' if payload['ok'] else 'failed'}")
    for warning in payload.get("warnings", []):
        print(f"warning: {warning}")
    if not payload["ok"] and payload.get("error"):
        print(f"error: {payload['error'].get('code')}: {payload['error'].get('message')}")
    data = payload.get("data") or {}
    if "sessions" in data:
        for session in data["sessions"]:
            print(
                f"- {session.get('provider')} {session.get('id')} "
                f"{session.get('workspace') or '<no workspace>'} "
                f"{session.get('title') or ''}"
            )
    elif data:
        print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())

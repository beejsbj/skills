#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[1] if SCRIPT_PATH.parent.name == "scripts" else SCRIPT_PATH.parent
AGENTS_CLI = Path("/Users/burooj/Projects/skills/agents/agents.py")
CODEX_STATE_DB = Path.home() / ".codex/state_5.sqlite"
CODEX_GLOBAL_STATE_JSON = Path.home() / ".codex/.codex-global-state.json"
CLAUDE_CODE_SESSIONS_DIR = (
    Path.home() / "Library/Application Support/Claude/claude-code-sessions"
)
AGENTS_DISCOVER_PROVIDERS = ("opencode",)
LINEAR_CLI_PACKAGE = "@kyaukyuai/linear-cli@3.2.0"


def load_linear_config() -> dict[str, Any]:
    config_path = ROOT / ".linear.toml"
    if not config_path.exists():
        return {}
    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


LINEAR_CONFIG = load_linear_config()
LINEAR_WORKSPACE = str(LINEAR_CONFIG.get("workspace") or "bjs-projects")
LINEAR_TEAM_KEY = str(LINEAR_CONFIG.get("team_id") or LINEAR_CONFIG.get("team") or "BJS")
LINEAR_DEFAULT_SORT = str(LINEAR_CONFIG.get("issue_sort") or "priority")
LINEAR_DECISION_STATUS_ORDER = [
    "In Progress",
    "In Review",
    "Needs Burooj",
    "Ready for agent",
    "Blocked",
    "Todo",
]
LINEAR_STATUS_ORDER = [
    "Needs triage",
    "Todo",
    "Needs Burooj",
    "Ready for agent",
    "Blocked",
    "In Progress",
    "In Review",
    "Parked",
    "Backlog",
    "Done",
    "Canceled",
    "Duplicate",
]
LINEAR_ACTIVE_STATUS_NAMES = {
    "Todo",
    "Needs Burooj",
    "Ready for agent",
    "Blocked",
    "In Progress",
    "In Review",
}
LINEAR_INACTIVE_STATUS_TYPES = {"backlog", "completed", "canceled", "duplicate"}
SESSION_LABEL_RE = re.compile(r"^session:([a-z][a-z0-9_-]*):(.+)$")


def compact(text: str, limit: int = 180) -> str:
    one_line = re.sub(r"\s+", " ", text).strip()
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 1].rstrip() + "..."


class LinearCliError(RuntimeError):
    def __init__(self, command: list[str], completed: subprocess.CompletedProcess[str]):
        self.command = command
        self.completed = completed
        super().__init__(linear_error_message(completed))


def linear_base_command() -> list[str]:
    configured = os.environ.get("COCKPIT_LINEAR_BIN")
    if configured:
        return shlex.split(configured)
    local = ROOT / "node_modules" / ".bin" / "linear"
    if local.exists():
        return [str(local)]
    path = shutil.which("linear")
    if path:
        return [path]
    npx = shutil.which("npx")
    if npx:
        return [npx, "-y", LINEAR_CLI_PACKAGE]
    raise RuntimeError(f"linear CLI is unavailable; run `npm install` in {ROOT}.")


def linear_command_label() -> str:
    return shlex.join(linear_base_command())


def linear_common_args() -> list[str]:
    return ["--workspace", LINEAR_WORKSPACE]


def run_linear(
    args: list[str],
    *,
    check: bool = True,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    command = linear_base_command() + args
    completed = subprocess.run(
        command,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )
    if check and completed.returncode != 0:
        raise LinearCliError(command, completed)
    return completed


def run_linear_json(args: list[str]) -> Any:
    completed = run_linear(args)
    output = completed.stdout.strip()
    if not output:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"linear CLI returned non-JSON output for `{shlex.join(completed.args)}`: {exc}"
        ) from exc


def linear_error_message(completed: subprocess.CompletedProcess[str]) -> str:
    text = (completed.stdout or completed.stderr or "").strip()
    if text:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return text
        error = payload.get("error") if isinstance(payload, dict) else None
        if isinstance(error, dict):
            bits = [
                str(error.get("message") or "linear CLI failed"),
                str(error.get("suggestion") or "").strip(),
                str(error.get("context") or "").strip(),
            ]
            return " ".join(bit for bit in bits if bit)
    return f"linear CLI exited {completed.returncode}"


def linear_auth_hint() -> str:
    local_linear = ROOT / "node_modules" / ".bin" / "linear"
    return (
        "Set LINEAR_API_KEY or run "
        f"`{local_linear} auth login --profile human-debug --interactive`."
    )


def print_status(*, project: str | None = None) -> int:
    return print_linear_status(project=project)


def print_sessions(limit: int = 40, *, include_archive: bool = False) -> int:
    try:
        discovered = discover_agent_sessions()
    except Exception as exc:
        print(f"Could not discover provider sessions: {exc}")
        return 1
    sessions = discovered.get("data", {}).get("sessions", [])
    if not isinstance(sessions, list):
        print("Provider discovery returned no sessions list.")
        return 1

    visible = filtered_discovered_sessions(sessions, include_archive=include_archive)
    print("Local provider sessions:")
    for session in visible[:limit]:
        print(session_status_line(session))
        print(f"  resume: {resume_command(session)}")
    hidden = len(sessions) - len(visible)
    if len(visible) > limit:
        print(f"- ... {len(visible) - limit} more sessions.")
    if hidden:
        print(f"- {hidden} archive/worktree session(s) hidden; pass --archive to show.")
    warnings = discovered.get("warnings", [])
    if warnings:
        for warning in warnings:
            print(f"- warning: {warning}")
    return 0


def filtered_discovered_sessions(
    sessions: list[dict[str, Any]], *, include_archive: bool = False
) -> list[dict[str, Any]]:
    if include_archive:
        return sessions
    return [session for session in sessions if not session_is_archive_like(session)]


def session_is_archive_like(session: dict[str, Any]) -> bool:
    workspace = str(session.get("workspace") or "")
    if "/.codex/worktrees/" in workspace:
        return True
    project = project_for_workspace(workspace)
    bucket, _label = project_bucket(
        {
            "id": project["id"],
            "root_path": project.get("root_path"),
            "last_seen_at": session.get("updated_at"),
        }
    )
    return bucket in HIDDEN_BUCKETS


def discover_agent_sessions() -> dict[str, Any]:
    sessions: list[dict[str, Any]] = []
    warnings: list[str] = []

    for discovered in (discover_codex_sidebar_sessions(), discover_claude_sidebar_sessions()):
        provider_sessions = discovered.get("data", {}).get("sessions", [])
        if not isinstance(provider_sessions, list):
            raise RuntimeError("sidebar discover returned no sessions list")
        sessions.extend(session for session in provider_sessions if isinstance(session, dict))
        warnings.extend(str(warning) for warning in discovered.get("warnings", []))

    for provider in AGENTS_DISCOVER_PROVIDERS:
        discovered = discover_agent_provider(provider)
        provider_sessions = discovered.get("data", {}).get("sessions", [])
        if not isinstance(provider_sessions, list):
            raise RuntimeError(f"agents.py discover returned no sessions list for {provider}")
        sessions.extend(session for session in provider_sessions if isinstance(session, dict))
        warnings.extend(str(warning) for warning in discovered.get("warnings", []))

    sessions.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return {"ok": True, "data": {"sessions": sessions}, "warnings": warnings}


def discover_agent_provider(provider: str) -> dict[str, Any]:
    command = [sys.executable, str(AGENTS_CLI), "discover", "--provider", provider]
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout).strip())
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"agents.py discover returned invalid JSON for {provider}: {exc}") from exc


def discover_codex_sidebar_sessions() -> dict[str, Any]:
    if not CODEX_STATE_DB.exists():
        return {
            "ok": True,
            "data": {"sessions": []},
            "warnings": [f"codex sidebar state missing: {CODEX_STATE_DB}"],
        }

    sessions: list[dict[str, Any]] = []
    workspace_hints = load_codex_workspace_hints()
    uri = f"file:{CODEX_STATE_DB.as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(
            """
            select
                id,
                cwd,
                title,
                preview,
                source,
                thread_source,
                model_provider,
                model,
                agent_nickname,
                agent_role,
                updated_at,
                updated_at_ms
            from threads
            where archived = 0
              and source = 'vscode'
            order by updated_at_ms desc, updated_at desc, id desc
            """
        ).fetchall()

    for row in rows:
        item = dict(row)
        session_id = str(item.get("id") or "")
        if not session_id:
            continue
        updated_at = (
            iso_from_epoch_ms(item.get("updated_at_ms"))
            or iso_from_epoch_seconds(item.get("updated_at"))
            or now_utc()
        )
        title = str(item.get("title") or item.get("preview") or "untitled Codex thread")
        sessions.append(
            {
                "provider": "codex",
                "id": session_id,
                "title": title,
                "workspace": workspace_hints.get(session_id) or item.get("cwd"),
                "updated_at": updated_at,
                "source": "codex-sidebar",
                "codex_source": item.get("source"),
                "thread_source": item.get("thread_source"),
                "agent_nickname": item.get("agent_nickname"),
                "agent_role": item.get("agent_role"),
                "model_provider": item.get("model_provider"),
                "model": item.get("model"),
                "resume_command": f"codex exec resume {session_id}",
            }
        )

    return {"ok": True, "data": {"sessions": sessions}, "warnings": []}


def load_codex_workspace_hints() -> dict[str, str]:
    if not CODEX_GLOBAL_STATE_JSON.exists():
        return {}
    try:
        data = json.loads(CODEX_GLOBAL_STATE_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    hints = data.get("thread-workspace-root-hints")
    if not isinstance(hints, dict):
        return {}
    return {
        str(thread_id): str(workspace)
        for thread_id, workspace in hints.items()
        if isinstance(workspace, str) and workspace
    }


def discover_claude_sidebar_sessions() -> dict[str, Any]:
    if not CLAUDE_CODE_SESSIONS_DIR.exists():
        return {
            "ok": True,
            "data": {"sessions": []},
            "warnings": [f"claude sidebar state missing: {CLAUDE_CODE_SESSIONS_DIR}"],
        }

    sessions: list[dict[str, Any]] = []
    warnings: list[str] = []
    for path in sorted(CLAUDE_CODE_SESSIONS_DIR.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            warnings.append(f"could not read claude sidebar session {path}: {exc}")
            continue
        if data.get("isArchived"):
            continue
        session_id = str(data.get("cliSessionId") or data.get("sessionId") or "")
        if not session_id:
            continue
        updated_at = (
            iso_from_epoch_ms(data.get("lastActivityAt"))
            or iso_from_epoch_ms(data.get("lastFocusedAt"))
            or iso_from_epoch_ms(data.get("createdAt"))
            or now_utc()
        )
        sessions.append(
            {
                "provider": "claude",
                "id": session_id,
                "title": data.get("title") or "untitled Claude session",
                "workspace": data.get("cwd") or data.get("originCwd"),
                "updated_at": updated_at,
                "source": "claude-code-sessions",
                "app_session_id": data.get("sessionId"),
                "model": data.get("model"),
                "resume_command": f"claude --resume {session_id}",
            }
        )

    sessions.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return {"ok": True, "data": {"sessions": sessions}, "warnings": warnings}


def project_for_workspace(workspace: Any) -> dict[str, Any]:
    if not isinstance(workspace, str) or not workspace:
        return {"id": "chats", "name": "chats", "root_path": None}
    path = Path(workspace).expanduser()
    if path == Path("/"):
        return {"id": "chats", "name": "chats", "root_path": None}
    root = git_root(path) or path
    root_text = str(root)
    return {
        "id": root_text,
        "name": root.name or root_text,
        "root_path": root_text,
    }


def git_root(path: Path) -> Path | None:
    if not path.exists():
        return None
    cwd = path if path.is_dir() else path.parent
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return None
    return Path(completed.stdout.strip())


def print_linear_doctor() -> int:
    warnings: list[str] = []
    print("Linear cockpit doctor:")
    try:
        version = run_linear(["--version"], check=False).stdout.strip() or "unknown"
        print(f"- CLI: {version} via `{linear_command_label()}`")
    except RuntimeError as exc:
        print(f"- WARN: {exc}")
        return 1

    try:
        capabilities = run_linear_json(["capabilities", *linear_common_args()])
        cli = capabilities.get("cli", {}) if isinstance(capabilities, dict) else {}
        contracts = capabilities.get("contractVersions", {}) if isinstance(capabilities, dict) else {}
        automation = contracts.get("automation", {}) if isinstance(contracts, dict) else {}
        print(
            "- capabilities: "
            f"schema {capabilities.get('schemaVersion', 'unknown') if isinstance(capabilities, dict) else 'unknown'}, "
            f"automation {automation.get('latest', 'unknown') if isinstance(automation, dict) else 'unknown'}, "
            f"binary {cli.get('binary', 'linear') if isinstance(cli, dict) else 'linear'}"
        )
    except Exception as exc:
        warnings.append(f"capabilities failed: {exc}")

    auth_check = run_linear(["auth", "whoami", *linear_common_args()], check=False)
    if auth_check.returncode == 0:
        print("- auth: OK")
    else:
        warnings.append(f"auth not ready: {linear_error_message(auth_check)} {linear_auth_hint()}")

    config_path = ROOT / ".linear.toml"
    if config_path.exists():
        print(f"- config: {config_path}")
    else:
        warnings.append(".linear.toml missing; cockpit should declare workspace/team/sort.")
    print(f"- workspace/team: {LINEAR_WORKSPACE}/{LINEAR_TEAM_KEY}")
    print("- session binding: Linear issue labels named `session:<provider>:<id>`")

    if warnings:
        for warning in warnings:
            print(f"- WARN: {warning}")
        return 1
    return 0


def load_linear_issues(*, limit: int = 0, project: str | None = None) -> list[dict[str, Any]]:
    args = [
        "issue",
        "list",
        *linear_common_args(),
        "--team",
        LINEAR_TEAM_KEY,
        "--all-states",
        "--all-assignees",
        "--sort",
        LINEAR_DEFAULT_SORT,
        "--json",
        "--limit",
        str(limit),
    ]
    if project:
        args.extend(["--project", project])
    payload = run_linear_json(args)
    return issues_from_payload(payload)


def load_linear_issue(issue_id: str) -> dict[str, Any]:
    payload = run_linear_json(["issue", "view", issue_id, *linear_common_args(), "--json"])
    if isinstance(payload, dict) and isinstance(payload.get("issue"), dict):
        return dict(payload["issue"])
    if isinstance(payload, dict):
        return payload
    raise RuntimeError(f"linear issue view returned unexpected payload for {issue_id}")


def issues_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("issues", "nodes", "data"):
        value = payload.get(key)
        if isinstance(value, list):
            return [dict(item) for item in value if isinstance(item, dict)]
    return []


def issue_identifier(issue: dict[str, Any]) -> str:
    for key in ("identifier", "id", "issueId"):
        value = issue.get(key)
        if isinstance(value, str) and value:
            return value
    team = issue.get("team")
    number = issue.get("number")
    if isinstance(team, dict) and number:
        key = team.get("key")
        if key:
            return f"{key}-{number}"
    return "unknown"


def issue_title(issue: dict[str, Any]) -> str:
    return str(issue.get("title") or "untitled issue")


def issue_status_name(issue: dict[str, Any]) -> str:
    value = issue.get("status") or issue.get("state")
    if isinstance(value, dict):
        return str(value.get("name") or value.get("type") or "unknown")
    if isinstance(value, str) and value:
        return value
    return "unknown"


def issue_status_type(issue: dict[str, Any]) -> str:
    for key in ("statusType", "stateType"):
        value = issue.get(key)
        if isinstance(value, str) and value:
            return value
    value = issue.get("status") or issue.get("state")
    if isinstance(value, dict):
        return str(value.get("type") or "")
    return ""


def issue_project_name(issue: dict[str, Any]) -> str:
    value = issue.get("project")
    if isinstance(value, dict):
        return str(value.get("name") or value.get("id") or "")
    return str(value or "")


def issue_labels(issue: dict[str, Any]) -> list[str]:
    labels = issue.get("labels") or []
    if not isinstance(labels, list):
        return []
    names: list[str] = []
    for label in labels:
        if isinstance(label, str):
            names.append(label)
        elif isinstance(label, dict):
            value = label.get("name") or label.get("id")
            if value:
                names.append(str(value))
    return names


def session_labels(issue: dict[str, Any]) -> list[str]:
    return [label for label in issue_labels(issue) if SESSION_LABEL_RE.match(label)]


def issue_is_active(issue: dict[str, Any]) -> bool:
    status = issue_status_name(issue)
    status_type = issue_status_type(issue)
    if status in LINEAR_ACTIVE_STATUS_NAMES:
        return True
    if status_type in LINEAR_INACTIVE_STATUS_TYPES:
        return False
    return status_type in {"unstarted", "started"}


def issue_is_doneish(issue: dict[str, Any]) -> bool:
    return issue_status_name(issue) in {"Done", "Canceled", "Duplicate"} or issue_status_type(issue) in {
        "completed",
        "canceled",
        "duplicate",
    }


def issue_is_in_progress(issue: dict[str, Any]) -> bool:
    return issue_status_name(issue) == "In Progress"


def normalize_session_label(provider_or_label: str, session_id: str | None) -> str:
    if provider_or_label.startswith("session:") and session_id is None:
        label = provider_or_label
    elif session_id:
        provider = provider_or_label.strip().lower()
        label = f"session:{provider}:{session_id.strip()}"
    else:
        raise RuntimeError("pass either `session:<provider>:<id>` or `<provider> <session-id>`")
    if not SESSION_LABEL_RE.match(label):
        raise RuntimeError("session labels must look like `session:<provider>:<id>`")
    return label


def split_session_label(label: str) -> tuple[str, str] | None:
    match = SESSION_LABEL_RE.match(label)
    if not match:
        return None
    return match.group(1), match.group(2)


def group_issues_by_status(issues: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for issue in issues:
        grouped.setdefault(issue_status_name(issue), []).append(issue)
    return grouped


def print_linear_status(*, project: str | None = None) -> int:
    try:
        issues = load_linear_issues(project=project)
    except Exception as exc:
        print("Where we are: Linear board unavailable through cockpit.")
        print(f"- {exc}")
        print(f"- {linear_auth_hint()}")
        print("\nSafe next:")
        print("- Run `./cockpit.py linear-doctor`.")
        print("- Keep `./cockpit.py sessions` for local session audit while CLI auth is being wired.")
        return 1

    grouped = group_issues_by_status(issues)
    print(f"Where we are: Linear status {LINEAR_WORKSPACE}/{LINEAR_TEAM_KEY}")
    print(f"- issues loaded: {len(issues)}")
    print(f"- binding labels: {sum(len(session_labels(issue)) for issue in issues)}")
    if project:
        print(f"- project filter: {project}")

    print("\nDecision lanes:")
    printed_decision_lane = False
    for status in LINEAR_DECISION_STATUS_ORDER:
        rows = grouped.get(status, [])
        if rows:
            print_linear_issue_group(status, rows)
            printed_decision_lane = True
    if not printed_decision_lane:
        print("- none")

    print("\nOther lanes:")
    printed_other_lane = False
    known_statuses = set(LINEAR_DECISION_STATUS_ORDER)
    for status in LINEAR_STATUS_ORDER:
        if status in known_statuses:
            continue
        rows = grouped.get(status, [])
        if rows:
            print(f"- {status}: {len(rows)}")
            known_statuses.add(status)
            printed_other_lane = True
    for status in sorted(set(grouped) - known_statuses):
        print(f"- {status}: {len(grouped[status])}")
        printed_other_lane = True
    if not printed_other_lane:
        print("- none")

    print("\nSafe next:")
    print("- Use `./cockpit.py issue BJS-123` before launching work.")
    print("- Use `./cockpit.py bind BJS-123 codex <session-id>` when a session takes an issue.")
    print("- Use `./cockpit.py board` for the full grouped board.")
    print("- Use `./cockpit.py audit` to find drift between session labels and issue state.")
    return 0


def print_linear_board(limit: int = 0, *, project: str | None = None) -> int:
    try:
        issues = load_linear_issues(limit=limit, project=project)
    except Exception as exc:
        print("Where we are: Linear board unavailable through cockpit.")
        print(f"- {exc}")
        print(f"- {linear_auth_hint()}")
        print("\nSafe next:")
        print("- Run `./cockpit.py linear-doctor`.")
        print("- Keep `./cockpit.py sessions` for local session audit while CLI auth is being wired.")
        return 1

    grouped = group_issues_by_status(issues)

    print(f"Where we are: Linear board {LINEAR_WORKSPACE}/{LINEAR_TEAM_KEY}")
    print(f"- issues loaded: {len(issues)}")
    print(f"- binding labels: {sum(len(session_labels(issue)) for issue in issues)}")
    if project:
        print(f"- project filter: {project}")

    for status in LINEAR_STATUS_ORDER:
        rows = grouped.pop(status, [])
        if rows:
            print_linear_issue_group(status, rows)
    for status in sorted(grouped):
        print_linear_issue_group(status, grouped[status])

    print("\nSafe next:")
    print("- Use `./cockpit.py issue BJS-123` before launching work.")
    print("- Use `./cockpit.py bind BJS-123 codex <session-id>` when a session takes an issue.")
    print("- Use `./cockpit.py audit` to find drift between session labels and issue state.")
    return 0


def print_linear_issue_group(status: str, rows: list[dict[str, Any]]) -> None:
    print(f"\n{status} ({len(rows)}):")
    for issue in rows:
        labels = session_labels(issue)
        binding = f" {' '.join(labels)}" if labels else ""
        project = issue_project_name(issue)
        project_part = f" [{project}]" if project else ""
        print(f"- {issue_identifier(issue)}{project_part}: {compact(issue_title(issue), 100)}{binding}")


def print_linear_issue(issue_id: str) -> int:
    try:
        issue = load_linear_issue(issue_id)
    except Exception as exc:
        print(f"Could not read {issue_id}: {exc}")
        print(linear_auth_hint())
        return 1
    labels = issue_labels(issue)
    session = session_labels(issue)
    print(f"{issue_identifier(issue)}: {issue_title(issue)}")
    print(f"- status: {issue_status_name(issue)} ({issue_status_type(issue) or 'unknown type'})")
    print(f"- project: {issue_project_name(issue) or 'none'}")
    if issue.get("url"):
        print(f"- url: {issue['url']}")
    print(f"- labels: {', '.join(labels) if labels else 'none'}")
    print(f"- session: {', '.join(session) if session else 'unbound'}")
    description = issue.get("description")
    if isinstance(description, str) and description.strip():
        print(f"\nDescription:\n{compact(description, 900)}")
    return 0


def ensure_linear_label(label: str) -> None:
    completed = run_linear(
        [
            "label",
            "create",
            *linear_common_args(),
            "--team",
            LINEAR_TEAM_KEY,
            "--name",
            label,
            "--color",
            "#5E6AD2",
            "--description",
            "Cockpit session binding label.",
        ],
        check=False,
    )
    if completed.returncode == 0:
        return
    message = linear_error_message(completed).lower()
    if "already" in message or "exists" in message:
        return
    # Some CLI versions do not expose structured duplicate errors. The add step is authoritative.


def remove_issue_label(issue_id: str, label: str) -> None:
    completed = run_linear(
        ["issue", "label", "remove", issue_id, label, *linear_common_args()],
        check=False,
    )
    if completed.returncode != 0:
        message = linear_error_message(completed).lower()
        if "not found" not in message and "does not" not in message:
            raise LinearCliError(list(completed.args), completed)


def add_issue_label(issue_id: str, label: str) -> None:
    ensure_linear_label(label)
    run_linear(["issue", "label", "add", issue_id, label, *linear_common_args()])


def add_issue_comment(issue_id: str, body: str) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md", delete=False) as handle:
        handle.write(body)
        temp_path = handle.name
    try:
        run_linear(
            [
                "issue",
                "comment",
                "add",
                issue_id,
                *linear_common_args(),
                "--body-file",
                temp_path,
                "--json",
            ]
        )
    finally:
        Path(temp_path).unlink(missing_ok=True)


def bind_linear_issue(
    issue_id: str,
    provider_or_label: str,
    session_id: str | None,
    *,
    force: bool = False,
    move_state: str | None = None,
) -> int:
    try:
        label = normalize_session_label(provider_or_label, session_id)
        issue = load_linear_issue(issue_id)
        if move_state:
            run_linear(["issue", "move", issue_id, move_state, *linear_common_args(), "--json"])
            issue = load_linear_issue(issue_id)
        if not issue_is_active(issue) and not force:
            print(
                f"{issue_id} is `{issue_status_name(issue)}`; bind only active issues. "
                "Move it to Todo/Ready for agent/In Progress first, or pass --force."
            )
            return 2
        old_labels = session_labels(issue)
        for old_label in old_labels:
            if old_label != label:
                remove_issue_label(issue_id, old_label)
        if label not in old_labels:
            add_issue_label(issue_id, label)
        add_issue_comment(
            issue_id,
            "\n".join(
                [
                    f"Bound session: `{label}`",
                    "",
                    f"Issue: `{issue_id}`",
                    f"Status: `{issue_status_name(issue)}`",
                    "Reason: cockpit session binding.",
                ]
            ),
        )
    except Exception as exc:
        print(f"Bind failed: {exc}")
        if "api key" in str(exc).lower() or "auth" in str(exc).lower():
            print(linear_auth_hint())
        return 1
    print(f"Bound {issue_id} -> {label}")
    return 0


def release_linear_issue(
    issue_id: str,
    *,
    move_state: str | None = None,
    reason: str = "cockpit release",
    archive_sessions: bool = False,
    comment: bool = True,
) -> int:
    archived: list[str] = []
    labels: list[str] = []
    try:
        issue = load_linear_issue(issue_id)
        labels = session_labels(issue)
        if move_state:
            run_linear(["issue", "move", issue_id, move_state, *linear_common_args(), "--json"])
        for label in labels:
            remove_issue_label(issue_id, label)
        if archive_sessions:
            for label in labels:
                pair = split_session_label(label)
                if not pair:
                    continue
                provider, session_id = pair
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(AGENTS_CLI),
                        "archive",
                        "--provider",
                        provider,
                        "--id",
                        session_id,
                    ],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                if completed.returncode == 0:
                    archived.append(label)
                else:
                    print(f"WARN: could not archive {label}: {(completed.stderr or completed.stdout).strip()}")
        if comment:
            body = [
                f"Released session binding for `{issue_id}`.",
                "",
                f"Reason: {reason}",
                f"Removed: {', '.join(f'`{label}`' for label in labels) if labels else 'none'}",
            ]
            if move_state:
                body.append(f"Moved state: `{move_state}`")
            if archived:
                body.append(f"Archived sessions: {', '.join(f'`{label}`' for label in archived)}")
            add_issue_comment(issue_id, "\n".join(body))
    except Exception as exc:
        print(f"Release failed: {exc}")
        if "api key" in str(exc).lower() or "auth" in str(exc).lower():
            print(linear_auth_hint())
        return 1
    print(f"Released {issue_id}; removed {len(labels)} session label(s).")
    return 0


def audit_linear_bindings(limit: int = 250) -> int:
    try:
        issues = load_linear_issues(limit=limit)
    except Exception as exc:
        print(f"Audit failed: {exc}")
        print(linear_auth_hint())
        return 1

    inactive_with_session: list[dict[str, Any]] = []
    in_progress_unbound: list[dict[str, Any]] = []
    multi_bound: list[dict[str, Any]] = []
    done_bound: list[dict[str, Any]] = []
    by_label: dict[str, list[str]] = {}

    for issue in issues:
        labels = session_labels(issue)
        ident = issue_identifier(issue)
        for label in labels:
            by_label.setdefault(label, []).append(ident)
        if labels and not issue_is_active(issue):
            inactive_with_session.append(issue)
        if labels and issue_is_doneish(issue):
            done_bound.append(issue)
        if len(labels) > 1:
            multi_bound.append(issue)
        if issue_is_in_progress(issue) and not labels:
            in_progress_unbound.append(issue)

    duplicate_labels = {label: ids for label, ids in by_label.items() if len(ids) > 1}

    print(f"Linear binding audit ({len(issues)} issues loaded):")
    print(f"- inactive/done with session labels: {len(inactive_with_session)}")
    print(f"- In Progress without session label: {len(in_progress_unbound)}")
    print(f"- issues with multiple session labels: {len(multi_bound)}")
    print(f"- duplicate session labels across issues: {len(duplicate_labels)}")

    print_audit_bucket("Inactive with session", inactive_with_session)
    print_audit_bucket("In Progress without session", in_progress_unbound)
    print_audit_bucket("Multiple session labels", multi_bound)
    if duplicate_labels:
        print("\nDuplicate session labels:")
        for label, ids in sorted(duplicate_labels.items()):
            print(f"- {label}: {', '.join(ids)}")
    return 1 if inactive_with_session or in_progress_unbound or multi_bound or duplicate_labels else 0


def print_audit_bucket(title: str, rows: list[dict[str, Any]]) -> None:
    print(f"\n{title} ({len(rows)}):")
    if not rows:
        print("- none")
        return
    for issue in rows:
        labels = session_labels(issue)
        print(
            f"- {issue_identifier(issue)} [{issue_status_name(issue)}]: "
            f"{compact(issue_title(issue), 90)}"
            f"{' ' + ' '.join(labels) if labels else ''}"
        )


ARCHIVE_BUCKETS = {"dated_codex", "scratch_repo", "app_data", "broad_container", "temp_noise"}
WORKTREE_BUCKETS = {"worktree"}
HIDDEN_BUCKETS = ARCHIVE_BUCKETS | WORKTREE_BUCKETS


def session_status_line(session: dict[str, Any]) -> str:
    project = session.get("project_id")
    if not project:
        project = project_for_workspace(session.get("workspace")).get("id") or "chats"
    title = session.get("title") or session.get("task") or "untitled session"
    return (
        f"- {session['provider']}:{session['id']} "
        f"{project} — {compact(str(title), 120)}"
    )


def resume_command(session: dict[str, Any]) -> str:
    provider = session.get("provider")
    session_id = session.get("id")
    if provider == "codex":
        return f"codex exec resume {session_id}"
    if provider == "claude":
        return f"claude --resume {session_id} -p '<plain evidence + exact ask>'"
    return f"/Users/burooj/Projects/skills/agents/agents.py resume --provider {provider} --id {session_id}"


def project_bucket_order() -> list[tuple[str, str]]:
    return [
        ("recent_repo", "Likely current project roots"),
        ("dated_codex", "Dated Codex thread folders"),
        ("worktree", "Codex worktree roots"),
        ("older_repo", "Older project roots"),
        ("scratch_repo", "Scratch repo roots"),
        ("app_data", "App data roots"),
        ("broad_container", "Broad container roots"),
        ("temp_noise", "Temp/noise roots"),
        ("chats", "Workspace-less chats"),
    ]


def project_bucket(row: dict[str, Any]) -> tuple[str, str]:
    project_id = str(row.get("id") or "")
    root = str(row.get("root_path") or project_id)
    labels = dict(project_bucket_order())

    if project_id == "chats":
        return "chats", labels["chats"]
    if is_temp_or_noise_root(root):
        return "temp_noise", labels["temp_noise"]
    if "/.codex/worktrees/" in root:
        return "worktree", labels["worktree"]
    if root in {"/Users/burooj/Projects", "/Users/burooj/Documents", "/home/admin"}:
        return "broad_container", labels["broad_container"]
    if root.startswith("/Users/burooj/Library/Application Support/Open Design/"):
        return "app_data", labels["app_data"]
    if root.startswith("/Users/burooj/Documents/Codex/"):
        return "dated_codex", labels["dated_codex"]
    if root.startswith("/Users/burooj/Projects/codex-random/"):
        return "scratch_repo", labels["scratch_repo"]
    if project_seen_within(row.get("last_seen_at"), days=10):
        return "recent_repo", labels["recent_repo"]
    return "older_repo", labels["older_repo"]


def is_temp_or_noise_root(root: str) -> bool:
    return (
        root == "/private/tmp"
        or root.startswith("/private/var/folders/")
        or root.startswith("/var/folders/")
    )


def project_seen_within(value: Any, *, days: int) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        seen = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return (datetime.now(timezone.utc) - seen).days <= days


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def iso_from_epoch_seconds(value: Any) -> str | None:
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat().replace("+00:00", "Z")


def iso_from_epoch_ms(value: Any) -> str | None:
    try:
        milliseconds = float(value)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(milliseconds / 1000, timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cockpit Linear board and local session audit.")
    sub = parser.add_subparsers(dest="command")
    status_parser = sub.add_parser("status", help="Print decision lanes from the Linear issue board.")
    status_parser.add_argument("--project", help="Filter by Linear project name.")
    board_parser = sub.add_parser("board", help="Print the full Linear issue board.")
    board_parser.add_argument("--limit", type=int, default=0, help="Maximum issues to load; 0 means all.")
    board_parser.add_argument("--project", help="Filter by Linear project name.")
    issue_parser = sub.add_parser("issue", help="Show one Linear issue and its session binding.")
    issue_parser.add_argument("issue_id")
    bind_parser = sub.add_parser("bind", help="Bind a Linear issue to a provider session label.")
    bind_parser.add_argument("issue_id")
    bind_parser.add_argument("provider_or_label")
    bind_parser.add_argument("session_id", nargs="?")
    bind_parser.add_argument(
        "--move-state",
        help="Move the issue before binding, for example `In Progress` or `Ready for agent`.",
    )
    bind_parser.add_argument("--force", action="store_true", help="Allow binding outside active states.")
    release_parser = sub.add_parser("release", help="Remove session:* labels from a Linear issue.")
    release_parser.add_argument("issue_id")
    release_parser.add_argument("--move-state", help="Move the issue while releasing.")
    release_parser.add_argument("--reason", default="cockpit release")
    release_parser.add_argument("--archive-session", action="store_true", help="Archive released provider sessions.")
    release_parser.add_argument("--no-comment", action="store_true", help="Do not add a release comment.")
    done_parser = sub.add_parser("done", help="Move issue to Done, remove session labels, archive sessions.")
    done_parser.add_argument("issue_id")
    done_parser.add_argument("--no-archive", action="store_true", help="Do not archive provider sessions.")
    done_parser.add_argument("--no-comment", action="store_true", help="Do not add a release comment.")
    audit_parser = sub.add_parser("audit", help="Audit Linear session labels against issue status.")
    audit_parser.add_argument("--limit", type=int, default=0, help="Maximum issues to load; 0 means all.")
    sub.add_parser("linear-doctor", help="Check Kyaukyuai linear-cli integration and auth.")
    sessions_parser = sub.add_parser(
        "sessions", help="List local provider sessions and resume commands."
    )
    sessions_parser.add_argument(
        "--archive",
        action="store_true",
        help="Include archive and worktree sessions (hidden by default).",
    )
    sessions_parser.add_argument(
        "--limit",
        type=int,
        default=40,
        help="Maximum sessions to print.",
    )
    args = parser.parse_args(argv)

    command = args.command or "status"

    if command == "status":
        return print_status(project=args.project)
    if command == "board":
        return print_linear_board(limit=args.limit, project=args.project)
    if command == "issue":
        return print_linear_issue(args.issue_id)
    if command == "bind":
        return bind_linear_issue(
            args.issue_id,
            args.provider_or_label,
            args.session_id,
            force=args.force,
            move_state=args.move_state,
        )
    if command == "release":
        return release_linear_issue(
            args.issue_id,
            move_state=args.move_state,
            reason=args.reason,
            archive_sessions=args.archive_session,
            comment=not args.no_comment,
        )
    if command == "done":
        return release_linear_issue(
            args.issue_id,
            move_state="Done",
            reason="issue moved to Done",
            archive_sessions=not args.no_archive,
            comment=not args.no_comment,
        )
    if command == "audit":
        return audit_linear_bindings(limit=args.limit)
    if command == "linear-doctor":
        return print_linear_doctor()
    if command == "sessions":
        return print_sessions(limit=args.limit, include_archive=args.archive)
    parser.error(f"unknown command: {command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())

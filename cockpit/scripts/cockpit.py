#!/opt/homebrew/bin/python3
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[1] if SCRIPT_PATH.parent.name == "scripts" else SCRIPT_PATH.parent
CODEX_STATE_DB = Path.home() / ".codex/state_5.sqlite"
CODEX_GLOBAL_STATE_JSON = Path.home() / ".codex/.codex-global-state.json"
CODEX_ARCHIVED_SESSIONS_DIR = Path.home() / ".codex/archived_sessions"
CLAUDE_CODE_SESSIONS_DIR = (
    Path.home() / "Library/Application Support/Claude/claude-code-sessions"
)
OPENCODE_DB = Path.home() / ".local/share/opencode/opencode.db"
LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"
LINEAR_OAUTH_TOKEN_URL = "https://api.linear.app/oauth/token"
LINEAR_APP_KEYCHAIN_SERVICE = "cockpit-linear-app-client-secret"


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
LINEAR_APP_CONFIG = LINEAR_CONFIG.get("app_actor") if isinstance(LINEAR_CONFIG.get("app_actor"), dict) else {}
# Decision lanes shown prominently in `status`.
LINEAR_DECISION_STATUS_ORDER = [
    "In Progress",
    "In Review",
    "Ready for Burooj",
    "Ready for agent",
    "Blocked",
    "Grilling",
    "Needs-info",
]
# Full lane order for `board`.
LINEAR_STATUS_ORDER = [
    "Inbox",
    "Needs-info",
    "Grilling",
    "Ready for Burooj",
    "Ready for agent",
    "Blocked",
    "In Progress",
    "In Review",
    "Done",
    "Canceled",
    "Duplicate",
]
# Lanes that are considered "active" (an issue is being worked or queued).
LINEAR_ACTIVE_STATUS_NAMES = {
    "Inbox",
    "Needs-info",
    "Grilling",
    "Ready for Burooj",
    "Ready for agent",
    "Blocked",
    "In Progress",
    "In Review",
}
LINEAR_INACTIVE_STATUS_TYPES = {"completed", "canceled", "duplicate"}
SESSION_LABEL_RE = re.compile(r"^session:([a-z][a-z0-9_-]*):(.+)$")
# All lanes that may appear in inbox triage view.
INBOX_TRIAGE_STATUSES = {
    "Inbox",
    "Needs-info",
    "Grilling",
    "Ready for Burooj",
    "Ready for agent",
    "Blocked",
    "In Progress",
    "In Review",
}
COCKPIT_THREAD_MARKER = "<!-- cockpit-thread-root -->"
COCKPIT_THREAD_ROOT_BODY = "\n".join(
    [
        "## Cockpit Thread",
        "",
        COCKPIT_THREAD_MARKER,
        "",
        "Cockpit receipts, progress updates, blockers, and follow-up notes live in replies here.",
    ]
)
QUESTIONS_THREAD_MARKER = "<!-- cockpit-questions-thread-root -->"
QUESTIONS_THREAD_ROOT_BODY = "\n".join(
    [
        "## Questions",
        "",
        QUESTIONS_THREAD_MARKER,
        "",
        "Questions for Burooj. Each question is a reply here — reply to the specific question to answer it.",
    ]
)
FOR_BUROOJ_THREAD_MARKER = "<!-- cockpit-for-burooj-thread-root -->"
FOR_BUROOJ_THREAD_ROOT_BODY = "\n".join(
    [
        "## For Burooj",
        "",
        FOR_BUROOJ_THREAD_MARKER,
        "",
        "Decision briefs for Burooj: the exact decision, minimum facts, options with a recommendation, "
        "and a pointer to the receipt trail. Burooj reads and replies only here.",
    ]
)
GRILLING_THREAD_MARKER = "<!-- cockpit-grilling-thread-root -->"
GRILLING_THREAD_ROOT_BODY = "\n".join(
    [
        "## Grilling",
        "",
        GRILLING_THREAD_MARKER,
        "",
        "Interactive shaping dialogue with Burooj. Can span sessions; resolve once conclusions graduate into the issue body.",
    ]
)


class CockpitUsageError(RuntimeError):
    """User-facing command error that does not need an auth hint."""


def compact(text: str, limit: int = 180) -> str:
    one_line = re.sub(r"\s+", " ", text).strip()
    if len(one_line) <= limit:
        return one_line
    return one_line[: limit - 1].rstrip() + "..."


def linear_app_auth_hint() -> str:
    service = linear_app_keychain_service()
    return (
        "Set COCKPIT_LINEAR_APP_ACCESS_TOKEN to a Linear OAuth `actor=app` access token, "
        "or set COCKPIT_LINEAR_APP_CLIENT_ID and COCKPIT_LINEAR_APP_CLIENT_SECRET for "
        "client-credentials app tokens. On this Mac, cockpit can also read the client "
        f"secret from Keychain service `{service}`."
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

    sessions.extend(discover_opencode_sessions())

    sessions.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return {"ok": True, "data": {"sessions": sessions}, "warnings": warnings}


def discover_opencode_sessions() -> list[dict[str, Any]]:
    completed = subprocess.run(
        ["opencode", "session", "list", "--format", "json"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode == 0 and completed.stdout.strip():
        try:
            sessions = json.loads(completed.stdout)
        except (json.JSONDecodeError, TypeError):
            sessions = None
        if isinstance(sessions, list):
            out: list[dict[str, Any]] = []
            for session in sessions:
                if not isinstance(session, dict):
                    continue
                sid = session.get("id")
                if not sid:
                    continue
                out.append(format_opencode_session(session, source="opencode session list"))
            return out
    return discover_opencode_sessions_from_db()


def discover_opencode_sessions_from_db() -> list[dict[str, Any]]:
    if not OPENCODE_DB.exists():
        return []
    try:
        conn = sqlite3.connect(str(OPENCODE_DB))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, title, directory, model, time_created, time_updated FROM session ORDER BY time_updated DESC"
        ).fetchall()
        conn.close()
    except Exception:
        return []

    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            prune_none(
                {
                    "provider": "opencode",
                    "id": row["id"],
                    "workspace": row["directory"],
                    "title": row["title"] or "opencode session",
                    "updated_at": normalize_opencode_time(row["time_updated"]),
                    "created_at": normalize_opencode_time(row["time_created"]),
                    "archived": False,
                    "source": f"sqlite:{OPENCODE_DB}",
                    "model": opencode_model_id(row["model"]),
                    "mode": "interactive",
                    "cwd_confidence": "high" if row["directory"] else "low",
                    "status": "unknown",
                    "running": None,
                }
            )
        )
    return out


def format_opencode_session(session: dict[str, Any], *, source: str) -> dict[str, Any]:
    return prune_none(
        {
            "provider": "opencode",
            "id": str(session["id"]),
            "workspace": session.get("directory"),
            "title": session.get("title") or "opencode session",
            "updated_at": normalize_opencode_time(session.get("updated")),
            "created_at": normalize_opencode_time(session.get("created")),
            "archived": False,
            "source": source,
            "model": opencode_model_id(session.get("model")),
            "mode": "interactive",
            "cwd_confidence": "high" if session.get("directory") else "low",
            "status": "unknown",
            "running": None,
        }
    )


def opencode_model_id(value: Any) -> str | None:
    if isinstance(value, dict):
        model = value.get("id")
        return str(model) if model else None
    if isinstance(value, str) and value:
        try:
            data = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
        if isinstance(data, dict):
            model = data.get("id")
            return str(model) if model else value
        return value
    return None


def normalize_opencode_time(value: Any) -> str | None:
    if value is None:
        return None
    try:
        ms = int(value)
    except (ValueError, TypeError):
        return None
    try:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    except OSError:
        return None


def prune_none(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if item is not None}


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
    """Check the GraphQL app-actor surface only (no linear CLI checks)."""
    warnings: list[str] = []
    print("Linear cockpit doctor (app-actor GraphQL surface):")

    config_path = ROOT / ".linear.toml"
    if config_path.exists():
        print(f"- config: {config_path}")
    else:
        warnings.append(".linear.toml missing; cockpit should declare workspace/team/sort.")
    print(f"- workspace/team: {LINEAR_WORKSPACE}/{LINEAR_TEAM_KEY}")
    print("- session binding: Linear issue labels named `session:<provider>:<id>`")

    try:
        data = run_linear_graphql(
            """
            query CockpitViewer {
              viewer { name displayName }
            }
            """,
            {},
        )
        viewer = data.get("viewer") if isinstance(data, dict) else None
        name = (
            viewer.get("displayName")
            or viewer.get("name")
            if isinstance(viewer, dict)
            else None
        )
        print(f"- app actor: OK ({name or 'Linear app actor'})")
    except Exception as exc:
        warnings.append(f"app actor auth failed: {exc} — {linear_app_auth_hint()}")

    # Verify team + states are accessible.
    try:
        meta = linear_team_metadata()
        states = [s["name"] for s in (meta.get("states", {}).get("nodes") or []) if isinstance(s, dict) and s.get("name")]
        print(f"- team states: {', '.join(states) if states else 'none'}")
    except Exception as exc:
        warnings.append(f"team metadata fetch failed: {exc}")

    if warnings:
        for warning in warnings:
            print(f"- WARN: {warning}")
        return 1
    return 0


def load_linear_issues(*, limit: int = 0, project: str | None = None) -> list[dict[str, Any]]:
    return load_linear_issues_graphql(limit=limit, project=project)


def load_linear_issue(issue_id: str) -> dict[str, Any]:
    return load_linear_issue_graphql(issue_id)


def load_linear_issues_graphql(*, limit: int = 0, project: str | None = None) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    after: str | None = None
    page_size = 100
    while True:
        remaining = limit - len(issues) if limit else page_size
        first = max(1, min(page_size, remaining if limit else page_size))
        data = run_linear_graphql(
            """
            query CockpitIssues($teamKey: String!, $first: Int!, $after: String) {
              issues(first: $first, after: $after, filter: { team: { key: { eq: $teamKey } } }) {
                nodes {
                  id
                  identifier
                  title
                  description
                  url
                  priority
                  priorityLabel
                  state { id name type }
                  project { name }
                  labels { nodes { id name } }
                }
                pageInfo { hasNextPage endCursor }
              }
            }
            """,
            {"teamKey": LINEAR_TEAM_KEY, "first": first, "after": after},
        )
        conn = data.get("issues") if isinstance(data, dict) else None
        nodes = conn.get("nodes") if isinstance(conn, dict) else None
        if not isinstance(nodes, list):
            raise RuntimeError("Linear GraphQL issues query returned no nodes.")
        for node in nodes:
            if not isinstance(node, dict):
                continue
            if project and issue_project_name(node) != project:
                continue
            issues.append(node)
            if limit and len(issues) >= limit:
                return issues
        page_info = conn.get("pageInfo") if isinstance(conn, dict) else None
        if not isinstance(page_info, dict) or not page_info.get("hasNextPage"):
            return issues
        after = page_info.get("endCursor")
        if not after:
            return issues



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
    if isinstance(labels, dict):
        labels = labels.get("nodes") or []
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


def issue_description(issue: dict[str, Any]) -> str:
    for key in ("description", "body", "content"):
        value = issue.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def issue_text(issue: dict[str, Any], comments: list[dict[str, Any]] | None = None) -> str:
    project = issue_project_name(issue)
    parts = [issue_title(issue), issue_description(issue)]
    if project:
        parts.append(f"Linear project: {project}")
    if comments:
        parts.extend(comment_body(comment) for comment in comments if unresolved_comment(comment))
    return "\n\n".join(part for part in parts if part.strip())


def unresolved_comment(comment: dict[str, Any]) -> bool:
    return not comment.get("archivedAt") and not comment.get("resolvedAt")


def top_level_unresolved_comments(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        comment
        for comment in comments
        if unresolved_comment(comment) and not comment.get("parentId")
    ]


def actionable_unresolved_comments(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        comment
        for comment in top_level_unresolved_comments(comments)
        if not comment_is_cockpit_authored(comment)
    ]




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


def issue_is_pr_work(issue: dict[str, Any]) -> bool:
    return "workflow:issue-pr" in issue_labels(issue)


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


def archived_codex_session_files() -> dict[str, str]:
    """Map codex session id -> archived rollout filename.

    Archived Codex sessions are a flat dir of
    `rollout-<timestamp>-<session-id>.jsonl`. Missing dir is not an error:
    return an empty map so callers skip the check cleanly.
    """
    out: dict[str, str] = {}
    try:
        if not CODEX_ARCHIVED_SESSIONS_DIR.is_dir():
            return out
        for path in CODEX_ARCHIVED_SESSIONS_DIR.iterdir():
            name = path.name
            if not name.startswith("rollout-") or not name.endswith(".jsonl"):
                continue
            stem = name[len("rollout-") : -len(".jsonl")]
            # `<YYYY-MM-DDTHH-MM-SS>-<session-id>`; timestamp is 5 dash-parts
            match = re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}-(.+)$", stem)
            if not match:
                continue
            session_id = match.group(1)
            if session_id:
                out.setdefault(session_id, name)
    except OSError:
        return {}
    return out


def archived_session_findings(
    issue: dict[str, Any],
    labels: list[str],
    archived: dict[str, str],
) -> list[tuple[dict[str, Any], str, str]]:
    findings: list[tuple[dict[str, Any], str, str]] = []
    if not archived:
        return findings
    for label in labels:
        parsed = split_session_label(label)
        if not parsed:
            continue
        provider, session_id = parsed
        if provider != "codex":
            # only the codex archive store is knowable; never guess others
            continue
        rollout = archived.get(session_id)
        if rollout:
            findings.append((issue, label, rollout))
    return findings


def session_lookup() -> dict[tuple[str, str], dict[str, Any]]:
    try:
        discovered = discover_agent_sessions()
    except Exception:
        return {}
    sessions = discovered.get("data", {}).get("sessions", [])
    if not isinstance(sessions, list):
        return {}
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for session in sessions:
        if not isinstance(session, dict):
            continue
        provider = session.get("provider")
        session_id = session.get("id")
        if isinstance(provider, str) and isinstance(session_id, str):
            out[(provider, session_id)] = session
    return out


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
        print(f"- {linear_app_auth_hint()}")
        print("\nSafe next:")
        print("- Run `./cockpit.py linear-doctor`.")
        print("- Run `./cockpit.py sessions` for local session audit.")
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
    print("- Use `./cockpit.py issue BJS-X` before launching work.")
    print("- Use `./cockpit.py prepare BJS-X` to get native launch context.")
    print("- Create the worker/session/thread with the active orchestration surface.")
    print("- Use `./cockpit.py bind BJS-X codex <session-id> --move-state \"In Progress\"` to bind it.")
    print("- Use `./cockpit.py board` for the full grouped board.")
    print("- Use `./cockpit.py audit` to find drift between session labels and issue state.")
    return 0


def print_linear_board(limit: int = 0, *, project: str | None = None) -> int:
    try:
        issues = load_linear_issues(limit=limit, project=project)
    except Exception as exc:
        print("Where we are: Linear board unavailable through cockpit.")
        print(f"- {exc}")
        print(f"- {linear_app_auth_hint()}")
        print("\nSafe next:")
        print("- Run `./cockpit.py linear-doctor`.")
        print("- Run `./cockpit.py sessions` for local session audit.")
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
    print("- Use `./cockpit.py issue BJS-X` before launching work.")
    print("- Use `./cockpit.py prepare BJS-X` to get native launch context.")
    print("- Create the worker/session/thread with the active orchestration surface.")
    print("- Use `./cockpit.py bind BJS-X codex <session-id> --move-state \"In Progress\"` to bind it.")
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


def comment_context_label(comment: dict[str, Any]) -> str:
    body = comment_body(comment)
    if COCKPIT_THREAD_MARKER in body:
        return "Cockpit Thread"
    if QUESTIONS_THREAD_MARKER in body:
        return "Questions Thread"
    if FOR_BUROOJ_THREAD_MARKER in body:
        return "For Burooj Thread"
    if GRILLING_THREAD_MARKER in body:
        return "Grilling Thread"
    if is_run_receipt(comment):
        return "run receipt"
    if comment_is_cockpit_authored(comment):
        return "cockpit"
    if comment_is_burooj_authored(comment):
        return "Burooj"
    return "comment"


def comment_body_hint(comment: dict[str, Any], *, limit: int = 220) -> str:
    lines = []
    for raw_line in comment_body(comment).splitlines():
        line = raw_line.strip()
        if not line or line in {
            COCKPIT_THREAD_MARKER,
            QUESTIONS_THREAD_MARKER,
            FOR_BUROOJ_THREAD_MARKER,
            GRILLING_THREAD_MARKER,
        }:
            continue
        if line in {"## Cockpit Thread", "## Questions", "## For Burooj", "## Grilling"}:
            continue
        lines.append(line)
    return compact(" ".join(lines), limit)


def print_parent_context(
    comment: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    *,
    indent: str = "  ",
) -> None:
    parent_id = comment.get("parentId")
    if not parent_id:
        return
    parent = by_id.get(parent_id)
    if parent is None:
        print(f"{indent}parent: {parent_id} (not loaded)")
        return
    label = comment_context_label(parent)
    hint = comment_body_hint(parent)
    suffix = f" - {hint}" if hint else ""
    print(f"{indent}parent: {label} {parent_id}{suffix}")


def print_linear_issue(issue_id: str, *, full: bool = False, show_cockpit: bool = False) -> int:
    try:
        issue = load_linear_issue(issue_id)
    except Exception as exc:
        print(f"Could not read {issue_id}: {exc}")
        print(linear_app_auth_hint())
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
        if full:
            print(f"\nDescription:\n{description.strip()}")
        else:
            print(f"\nDescription:\n{compact(description, 900)}")
            if len(description) > 900:
                print(f"({len(description)} chars; use --full for all)")

    # Surface Burooj's unresolved comments so `issue` reflects the async channel,
    # using the same filters as the inbox backlog (see
    # burooj_unresolved_comments_across_issues).
    try:
        comments = load_issue_comments(issue_identifier(issue))
    except Exception as exc:
        print(f"\nComments unavailable: {exc}")
        return 0
    by_id = {c.get("id"): c for c in comments if c.get("id")}
    burooj_comments = [
        c
        for c in comments
        if unresolved_comment(c)
        and comment_is_burooj_authored(c)
        and not is_run_receipt(c)
        and reply_is_post_resolution(c, by_id)
    ]
    if burooj_comments:
        print(f"\nBurooj unresolved comments: {len(burooj_comments)}")
        for comment in burooj_comments:
            comment_id = str(comment.get("id") or "unknown")
            print(f"\n{comment_id}")
            print_parent_context(comment, by_id)
            print(f"  body: {compact(comment_body(comment), 400)}")
            print(f"  resolve: ./cockpit.py comment-resolve {comment_id}")
    if show_cockpit:
        cockpit_comments = [
            c
            for c in comments
            if unresolved_comment(c)
            and (comment_is_cockpit_authored(c) or is_run_receipt(c))
            and not comment_is_thread_root(c)
        ]
        if cockpit_comments:
            print(f"\nCockpit comments/receipts: {len(cockpit_comments)}")
            for comment in cockpit_comments:
                comment_id = str(comment.get("id") or "unknown")
                print(f"\n{comment_id}")
                print_parent_context(comment, by_id)
                print(f"  kind: {comment_context_label(comment)}")
                print(f"  body: {compact(comment_body(comment), 500)}")
    return 0


def env_first(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def config_string(mapping: dict[str, Any], key: str) -> str | None:
    value = mapping.get(key)
    return str(value) if value else None


def linear_app_keychain_service() -> str:
    return (
        env_first("COCKPIT_LINEAR_APP_KEYCHAIN_SERVICE")
        or config_string(LINEAR_APP_CONFIG, "keychain_service")
        or LINEAR_APP_KEYCHAIN_SERVICE
    )


def linear_app_client_id() -> str | None:
    return (
        env_first("COCKPIT_LINEAR_APP_CLIENT_ID", "LINEAR_APP_CLIENT_ID")
        or config_string(LINEAR_APP_CONFIG, "client_id")
    )


def linear_app_client_secret() -> str | None:
    secret = env_first("COCKPIT_LINEAR_APP_CLIENT_SECRET", "LINEAR_APP_CLIENT_SECRET")
    if secret:
        return secret
    return read_keychain_password(linear_app_keychain_service())


def linear_app_scope() -> str:
    return (
        env_first("COCKPIT_LINEAR_APP_SCOPE")
        or config_string(LINEAR_APP_CONFIG, "scope")
        or "read,write,comments:create"
    )


def read_keychain_password(service: str) -> str | None:
    security = shutil.which("security")
    if not security:
        return None
    completed = subprocess.run(
        [security, "find-generic-password", "-s", service, "-w"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return None
    password = completed.stdout.strip()
    return password or None


def fetch_linear_app_access_token() -> str:
    token = env_first("COCKPIT_LINEAR_APP_ACCESS_TOKEN", "LINEAR_APP_ACCESS_TOKEN")
    if token:
        return token
    client_id = linear_app_client_id()
    client_secret = linear_app_client_secret()
    if not client_id or not client_secret:
        raise RuntimeError(f"Linear app-actor writes are not configured. {linear_app_auth_hint()}")
    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "scope": linear_app_scope(),
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        LINEAR_OAUTH_TOKEN_URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    payload = linear_http_json(request)
    access_token = payload.get("access_token") if isinstance(payload, dict) else None
    if not access_token:
        raise RuntimeError("Linear OAuth token response did not include access_token.")
    return str(access_token)


def linear_http_json(request: urllib.request.Request) -> Any:
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Linear HTTP {exc.code}: {raw.strip()}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Linear HTTP request failed: {exc}") from exc
    if not raw.strip():
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Linear returned non-JSON HTTP response: {exc}") from exc


def run_linear_graphql(query: str, variables: dict[str, Any], *, token: str | None = None) -> Any:
    access_token = token or fetch_linear_app_access_token()
    request = urllib.request.Request(
        LINEAR_GRAPHQL_URL,
        data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    payload = linear_http_json(request)
    errors = payload.get("errors") if isinstance(payload, dict) else None
    if errors:
        raise RuntimeError(f"Linear GraphQL error: {errors}")
    return payload.get("data") if isinstance(payload, dict) else payload


def load_linear_issue_graphql(issue_id: str) -> dict[str, Any]:
    data = run_linear_graphql(
        """
        query CockpitIssue($id: String!) {
          issue(id: $id) {
            id
            identifier
            title
            description
            url
            state { id name type }
            team { id key name }
            project { name }
            labels { nodes { id name } }
          }
        }
        """,
        {"id": issue_id},
    )
    issue = data.get("issue") if isinstance(data, dict) else None
    if not isinstance(issue, dict):
        raise RuntimeError(f"Linear GraphQL could not load issue {issue_id}.")
    return issue


def linear_team_metadata() -> dict[str, Any]:
    data = run_linear_graphql(
        """
        query CockpitTeam($key: String!) {
          teams(filter: { key: { eq: $key } }) {
            nodes {
              id
              key
              name
              states { nodes { id name type } }
              labels { nodes { id name color } }
            }
          }
        }
        """,
        {"key": LINEAR_TEAM_KEY},
    )
    teams = data.get("teams", {}).get("nodes") if isinstance(data, dict) else None
    if not isinstance(teams, list) or not teams:
        raise RuntimeError(f"Linear GraphQL could not load team {LINEAR_TEAM_KEY}.")
    return dict(teams[0])


def workflow_state_id(status_name: str) -> str:
    states = linear_team_metadata().get("states", {}).get("nodes")
    if not isinstance(states, list):
        raise RuntimeError(f"Linear GraphQL returned no states for team {LINEAR_TEAM_KEY}.")
    for state in states:
        if isinstance(state, dict) and state.get("name") == status_name and state.get("id"):
            return str(state["id"])
    raise RuntimeError(f"Linear status `{status_name}` not found for team {LINEAR_TEAM_KEY}.")


def issue_label_id(label: str) -> str | None:
    data = run_linear_graphql(
        """
        query CockpitIssueLabelByName($name: String!) {
          issueLabels(filter: { name: { eqIgnoreCase: $name } }, first: 50) {
            nodes {
              id
              name
              team { id key }
            }
          }
        }
        """,
        {"name": label},
    )
    labels = data.get("issueLabels", {}).get("nodes") if isinstance(data, dict) else None
    if not isinstance(labels, list):
        return None
    target = label.casefold()
    for item in labels:
        if isinstance(item, dict) and str(item.get("name") or "").casefold() == target:
            label_id = item.get("id")
            return str(label_id) if label_id else None
    return None


def is_duplicate_label_name_error(exc: RuntimeError) -> bool:
    return "duplicate label name" in str(exc).casefold()


def ensure_linear_label_with_app_actor(label: str) -> str:
    existing = issue_label_id(label)
    if existing:
        return existing
    try:
        data = run_linear_graphql(
            """
            mutation CockpitIssueLabelCreate($input: IssueLabelCreateInput!) {
              issueLabelCreate(input: $input) {
                success
                issueLabel { id name }
              }
            }
            """,
            {
                "input": {
                    "name": label,
                    "color": "#5E6AD2",
                    "description": "Cockpit session binding label.",
                }
            },
        )
    except RuntimeError as exc:
        if not is_duplicate_label_name_error(exc):
            raise
        existing = issue_label_id(label)
        if existing:
            return existing
        raise
    result = data.get("issueLabelCreate") if isinstance(data, dict) else None
    created = result.get("issueLabel") if isinstance(result, dict) else None
    if not isinstance(result, dict) or not result.get("success") or not isinstance(created, dict):
        raise RuntimeError(f"Linear issueLabelCreate did not succeed: {result}")
    return str(created["id"])


def update_issue_with_app_actor(issue_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
    issue = load_linear_issue_graphql(issue_id)
    data = run_linear_graphql(
        """
        mutation CockpitIssueUpdate($id: String!, $input: IssueUpdateInput!) {
          issueUpdate(id: $id, input: $input) {
            success
            issue {
              id
              identifier
              state { id name type }
              labels { nodes { id name } }
            }
          }
        }
        """,
        {"id": issue["id"], "input": input_payload},
    )
    result = data.get("issueUpdate") if isinstance(data, dict) else None
    updated = result.get("issue") if isinstance(result, dict) else None
    if not isinstance(result, dict) or not result.get("success") or not isinstance(updated, dict):
        raise RuntimeError(f"Linear issueUpdate did not succeed: {result}")
    return updated


def move_issue_with_app_actor(issue_id: str, status_name: str) -> None:
    update_issue_with_app_actor(issue_id, {"stateId": workflow_state_id(status_name)})


def load_linear_projects() -> list[dict[str, Any]]:
    projects: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        data = run_linear_graphql(
            """
            query CockpitProjects($first: Int!, $after: String) {
              projects(first: $first, after: $after) {
                nodes {
                  id
                  name
                  status { id name type }
                }
                pageInfo { hasNextPage endCursor }
              }
            }
            """,
            {"first": 100, "after": after},
        )
        conn = data.get("projects") if isinstance(data, dict) else None
        nodes = conn.get("nodes") if isinstance(conn, dict) else None
        if not isinstance(nodes, list):
            raise RuntimeError("Linear GraphQL returned no projects.")
        projects.extend(node for node in nodes if isinstance(node, dict))
        page_info = conn.get("pageInfo") if isinstance(conn, dict) else None
        if not isinstance(page_info, dict) or not page_info.get("hasNextPage"):
            return projects
        after = page_info.get("endCursor")
        if not after:
            return projects


def load_linear_project_by_id(project_id: str) -> dict[str, Any]:
    data = run_linear_graphql(
        """
        query CockpitProject($id: String!) {
          project(id: $id) {
            id
            name
            status { id name type }
          }
        }
        """,
        {"id": project_id},
    )
    project = data.get("project") if isinstance(data, dict) else None
    if not isinstance(project, dict):
        raise CockpitUsageError(f"Linear project `{project_id}` not found.")
    return project


def resolve_linear_project(project_ref: str) -> dict[str, Any]:
    ref = project_ref.strip()
    if re.fullmatch(r"[0-9a-fA-F-]{36}", ref):
        return load_linear_project_by_id(ref)

    target = ref.casefold()
    matches = [
        project
        for project in load_linear_projects()
        if str(project.get("name") or "").strip().casefold() == target
    ]
    if not matches:
        raise CockpitUsageError(f"Linear project `{project_ref}` not found.")
    if len(matches) > 1:
        choices = ", ".join(
            f"{project.get('name') or '(unnamed)'} ({project.get('id')})"
            for project in matches
        )
        raise CockpitUsageError(f"Linear project `{project_ref}` is ambiguous: {choices}")
    return matches[0]


def linear_project_statuses() -> list[dict[str, Any]]:
    data = run_linear_graphql(
        """
        query CockpitProjectStatuses {
          projectStatuses(first: 250) {
            nodes { id name type position }
          }
        }
        """,
        {},
    )
    statuses = data.get("projectStatuses", {}).get("nodes") if isinstance(data, dict) else None
    if not isinstance(statuses, list):
        raise RuntimeError("Linear GraphQL returned no project statuses.")
    return sorted(
        (status for status in statuses if isinstance(status, dict)),
        key=lambda item: item.get("position") if isinstance(item.get("position"), int) else 999,
    )


def project_status_by_name(status_name: str) -> dict[str, Any]:
    statuses = linear_project_statuses()
    target = status_name.strip().casefold()
    matches = [
        status
        for status in statuses
        if str(status.get("name") or "").strip().casefold() == target
    ]
    if not matches:
        valid = ", ".join(str(status.get("name")) for status in statuses if status.get("name"))
        raise CockpitUsageError(
            f"Linear project status `{status_name}` not found. Valid states: {valid}."
        )
    if len(matches) > 1:
        choices = ", ".join(
            f"{status.get('name') or '(unnamed)'} ({status.get('id')})"
            for status in matches
        )
        raise CockpitUsageError(f"Linear project status `{status_name}` is ambiguous: {choices}")
    return matches[0]


def update_project_with_app_actor(project_id: str, input_payload: dict[str, Any]) -> dict[str, Any]:
    data = run_linear_graphql(
        """
        mutation CockpitProjectUpdate($id: String!, $input: ProjectUpdateInput!) {
          projectUpdate(id: $id, input: $input) {
            success
            project {
              id
              name
              status { id name type }
            }
          }
        }
        """,
        {"id": project_id, "input": input_payload},
    )
    result = data.get("projectUpdate") if isinstance(data, dict) else None
    project = result.get("project") if isinstance(result, dict) else None
    if not isinstance(result, dict) or not result.get("success") or not isinstance(project, dict):
        raise RuntimeError(f"Linear projectUpdate did not succeed: {result}")
    return project


def move_project_with_app_actor(project_ref: str, status_name: str) -> dict[str, Any]:
    project = resolve_linear_project(project_ref)
    status = project_status_by_name(status_name)
    status_id = status.get("id")
    if not status_id:
        raise RuntimeError(f"Linear project status `{status_name}` has no id.")
    return update_project_with_app_actor(str(project["id"]), {"statusId": str(status_id)})


def load_project_issues(project_id: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        data = run_linear_graphql(
            """
            query CockpitProjectIssues($id: String!, $first: Int!, $after: String) {
              project(id: $id) {
                issues(first: $first, after: $after) {
                  nodes {
                    id
                    identifier
                    title
                    state { id name type }
                  }
                  pageInfo { hasNextPage endCursor }
                }
              }
            }
            """,
            {"id": project_id, "first": 100, "after": after},
        )
        project = data.get("project") if isinstance(data, dict) else None
        conn = project.get("issues") if isinstance(project, dict) else None
        nodes = conn.get("nodes") if isinstance(conn, dict) else None
        if not isinstance(nodes, list):
            raise RuntimeError(f"Linear GraphQL returned no issues for project {project_id}.")
        issues.extend(issue for issue in nodes if isinstance(issue, dict))
        page_info = conn.get("pageInfo") if isinstance(conn, dict) else None
        if not isinstance(page_info, dict) or not page_info.get("hasNextPage"):
            return issues
        after = page_info.get("endCursor")
        if not after:
            return issues


def project_open_issues(project_id: str) -> list[dict[str, Any]]:
    return [issue for issue in load_project_issues(project_id) if not issue_is_doneish(issue)]


def project_open_issues_note(issues: list[dict[str, Any]]) -> str:
    identifiers = [issue_identifier(issue) for issue in issues]
    shown = identifiers[:5]
    suffix = f", +{len(identifiers) - len(shown)} more" if len(identifiers) > len(shown) else ""
    issue_word = "issue remains" if len(issues) == 1 else "issues remain"
    return (
        f"note: {len(issues)} open {issue_word} in this project "
        f"({', '.join(shown)}{suffix})"
    )


def project_id_by_name(name: str) -> str:
    data = run_linear_graphql(
        """
        query CockpitProjects {
          projects(first: 250) {
            nodes { id name }
          }
        }
        """,
        {},
    )
    nodes = data.get("projects", {}).get("nodes") if isinstance(data, dict) else None
    if not isinstance(nodes, list):
        raise RuntimeError("Linear GraphQL returned no projects.")
    target = name.strip().lower()
    for node in nodes:
        if isinstance(node, dict) and str(node.get("name", "")).strip().lower() == target:
            return str(node["id"])
    raise RuntimeError(f"Linear project `{name}` not found.")


def create_issue_with_app_actor(
    title: str,
    *,
    project: str | None = None,
    state: str | None = None,
    description: str | None = None,
    labels: list[str] | None = None,
) -> dict[str, Any]:
    team_id = linear_team_metadata().get("id")
    if not team_id:
        raise RuntimeError(f"Linear GraphQL could not resolve team id for {LINEAR_TEAM_KEY}.")
    input_payload: dict[str, Any] = {"teamId": str(team_id), "title": title}
    if description:
        input_payload["description"] = description
    if state:
        input_payload["stateId"] = workflow_state_id(state)
    if project:
        input_payload["projectId"] = project_id_by_name(project)
    if labels:
        input_payload["labelIds"] = [ensure_linear_label_with_app_actor(label) for label in labels]
    data = run_linear_graphql(
        """
        mutation CockpitIssueCreate($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue { id identifier url title state { name } }
          }
        }
        """,
        {"input": input_payload},
    )
    result = data.get("issueCreate") if isinstance(data, dict) else None
    created = result.get("issue") if isinstance(result, dict) else None
    if not isinstance(result, dict) or not result.get("success") or not isinstance(created, dict):
        raise RuntimeError(f"Linear issueCreate did not succeed: {result}")
    return created


def add_issue_label_with_app_actor(issue_id: str, label: str) -> None:
    label_id = ensure_linear_label_with_app_actor(label)
    issue = load_linear_issue_graphql(issue_id)
    labels = issue.get("labels", {}).get("nodes")
    if isinstance(labels, list) and any(
        isinstance(item, dict) and item.get("id") == label_id for item in labels
    ):
        return
    update_issue_with_app_actor(issue_id, {"addedLabelIds": [label_id]})


def remove_issue_label_with_app_actor(issue_id: str, label: str) -> None:
    issue = load_linear_issue_graphql(issue_id)
    labels = issue.get("labels", {}).get("nodes")
    if not isinstance(labels, list):
        return
    label_id = None
    for item in labels:
        if isinstance(item, dict) and item.get("name") == label:
            label_id = item.get("id")
            break
    if not label_id:
        return
    update_issue_with_app_actor(issue_id, {"removedLabelIds": [str(label_id)]})


def move_linear_issue(issue_id: str, state_name: str) -> None:
    move_issue_with_app_actor(issue_id, state_name)


def linear_issue_uuid(issue_id: str) -> str:
    if re.fullmatch(r"[0-9a-fA-F-]{36}", issue_id):
        return issue_id
    issue = load_linear_issue_graphql(issue_id)
    uuid = issue.get("id")
    if not uuid:
        raise RuntimeError(f"Could not resolve Linear issue UUID for {issue_id}.")
    return str(uuid)


def normalize_comment_payload(comment: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(comment)
    parent = normalized.get("parent")
    if isinstance(parent, dict) and parent.get("id") and not normalized.get("parentId"):
        normalized["parentId"] = parent.get("id")
    normalized.setdefault("archivedAt", None)
    normalized.setdefault("resolvedAt", None)
    return normalized


def load_issue_comments_graphql(issue_id: str) -> list[dict[str, Any]]:
    issue_uuid = linear_issue_uuid(issue_id)
    comments: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        data = run_linear_graphql(
            """
            query CockpitIssueComments($id: String!, $after: String) {
              issue(id: $id) {
                comments(first: 100, after: $after) {
                  nodes {
                    id
                    body
                    parentId
                    archivedAt
                    resolvedAt
                    createdAt
                    updatedAt
                    user { name displayName }
                    url
                  }
                  pageInfo { hasNextPage endCursor }
                }
              }
            }
            """,
            {"id": issue_uuid, "after": after},
        )
        issue = data.get("issue") if isinstance(data, dict) else None
        conn = issue.get("comments") if isinstance(issue, dict) else None
        nodes = conn.get("nodes") if isinstance(conn, dict) else None
        if not isinstance(nodes, list):
            return comments
        comments.extend(normalize_comment_payload(node) for node in nodes if isinstance(node, dict))
        page_info = conn.get("pageInfo") if isinstance(conn, dict) else None
        if not isinstance(page_info, dict) or not page_info.get("hasNextPage"):
            return comments
        after = page_info.get("endCursor")
        if not after:
            return comments


def load_issue_comments(issue_id: str) -> list[dict[str, Any]]:
    return load_issue_comments_graphql(issue_id)


def cockpit_comment_author_names() -> set[str]:
    names = {"cockpit"}
    override = os.environ.get("COCKPIT_LINEAR_COMMENT_CREATE_AS_USER")
    if override:
        names.add(override.strip().lower())
    aliases = os.environ.get("COCKPIT_LINEAR_COMMENT_AUTHOR_ALIASES")
    if aliases:
        names.update(name.strip().lower() for name in aliases.split(",") if name.strip())
    return names


def comment_body(comment: dict[str, Any]) -> str:
    value = comment.get("body") or comment.get("text") or comment.get("content")
    return str(value or "")


def comment_is_thread_root(comment: dict[str, Any]) -> bool:
    body = comment_body(comment)
    return (
        COCKPIT_THREAD_MARKER in body
        or QUESTIONS_THREAD_MARKER in body
        or FOR_BUROOJ_THREAD_MARKER in body
        or GRILLING_THREAD_MARKER in body
    )


def comment_is_cockpit_authored(comment: dict[str, Any]) -> bool:
    user = comment.get("user")
    names: list[str] = []
    if isinstance(user, dict):
        for key in ("name", "displayName"):
            value = user.get(key)
            if value:
                names.append(str(value).strip().lower())
    for key in ("createAsUser", "author", "authorName"):
        value = comment.get(key)
        if value:
            names.append(str(value).strip().lower())
    allowed = cockpit_comment_author_names()
    return any(name in allowed for name in names)


def remove_issue_label(issue_id: str, label: str) -> None:
    remove_issue_label_with_app_actor(issue_id, label)


def add_issue_label(issue_id: str, label: str) -> None:
    add_issue_label_with_app_actor(issue_id, label)


def cockpit_thread_root_comment_id(issue_id: str) -> str | None:
    for comment in load_issue_comments(issue_id):
        if comment.get("archivedAt") or comment.get("parentId"):
            continue
        if COCKPIT_THREAD_MARKER not in comment_body(comment):
            continue
        if comment_is_cockpit_authored(comment):
            comment_id = comment.get("id")
            return str(comment_id) if comment_id else None
    return None


def ensure_cockpit_thread_root(issue_id: str) -> str:
    existing = cockpit_thread_root_comment_id(issue_id)
    if existing:
        return existing
    created = add_issue_comment_with_app_actor(
        issue_id,
        COCKPIT_THREAD_ROOT_BODY,
        parent_id=None,
        thread=False,
    )
    return created["id"]


def questions_thread_root_comment_id(issue_id: str) -> str | None:
    """Return the id of the existing Questions top-level thread comment, or None."""
    for comment in load_issue_comments(issue_id):
        if comment.get("archivedAt") or comment.get("parentId"):
            continue
        if QUESTIONS_THREAD_MARKER not in comment_body(comment):
            continue
        if comment_is_cockpit_authored(comment):
            comment_id = comment.get("id")
            return str(comment_id) if comment_id else None
    return None


def ensure_questions_thread_root(issue_id: str) -> str:
    """Return (creating if needed) the id of the Questions top-level thread comment."""
    existing = questions_thread_root_comment_id(issue_id)
    if existing:
        return existing
    created = add_issue_comment_with_app_actor(
        issue_id,
        QUESTIONS_THREAD_ROOT_BODY,
        parent_id=None,
        thread=False,
    )
    return created["id"]


def add_question_to_issue(issue_id: str, question_body: str) -> dict[str, str]:
    """Add a question as a reply under the issue's Questions thread."""
    parent_id = ensure_questions_thread_root(issue_id)
    return add_issue_comment_with_app_actor(
        issue_id,
        question_body,
        parent_id=parent_id,
        thread=False,
    )


def for_burooj_thread_root_comment_id(issue_id: str) -> str | None:
    """Return the id of the existing For Burooj top-level thread comment, or None."""
    for comment in load_issue_comments(issue_id):
        if comment.get("archivedAt") or comment.get("parentId"):
            continue
        if FOR_BUROOJ_THREAD_MARKER not in comment_body(comment):
            continue
        if comment_is_cockpit_authored(comment):
            comment_id = comment.get("id")
            return str(comment_id) if comment_id else None
    return None


def for_burooj_thread_root_comment(issue_id: str) -> dict[str, Any] | None:
    """Return the existing For Burooj top-level thread comment dict, or None."""
    for comment in load_issue_comments(issue_id):
        if comment.get("archivedAt") or comment.get("parentId"):
            continue
        if FOR_BUROOJ_THREAD_MARKER not in comment_body(comment):
            continue
        if comment_is_cockpit_authored(comment):
            return comment
    return None


def ensure_for_burooj_thread_root(issue_id: str) -> str:
    """Return (creating if needed) the id of the For Burooj top-level thread comment."""
    existing = for_burooj_thread_root_comment_id(issue_id)
    if existing:
        return existing
    created = add_issue_comment_with_app_actor(
        issue_id,
        FOR_BUROOJ_THREAD_ROOT_BODY,
        parent_id=None,
        thread=False,
    )
    return created["id"]


def add_brief_to_issue(issue_id: str, brief_body: str) -> dict[str, str]:
    """Add a decision brief as a reply under the issue's For Burooj thread."""
    parent_id = ensure_for_burooj_thread_root(issue_id)
    return add_issue_comment_with_app_actor(
        issue_id,
        brief_body,
        parent_id=parent_id,
        thread=False,
    )


def grilling_thread_root_comment_id(issue_id: str) -> str | None:
    """Return the id of the existing Grilling top-level thread comment, or None."""
    for comment in load_issue_comments(issue_id):
        if comment.get("archivedAt") or comment.get("parentId"):
            continue
        if GRILLING_THREAD_MARKER not in comment_body(comment):
            continue
        if comment_is_cockpit_authored(comment):
            comment_id = comment.get("id")
            return str(comment_id) if comment_id else None
    return None


def ensure_grilling_thread_root(issue_id: str) -> str:
    """Return (creating if needed) the id of the Grilling top-level thread comment."""
    existing = grilling_thread_root_comment_id(issue_id)
    if existing:
        return existing
    created = add_issue_comment_with_app_actor(
        issue_id,
        GRILLING_THREAD_ROOT_BODY,
        parent_id=None,
        thread=False,
    )
    return created["id"]


def add_grilling_note_to_issue(issue_id: str, note_body: str) -> dict[str, str]:
    """Add a shaping note as a reply under the issue's Grilling thread."""
    parent_id = ensure_grilling_thread_root(issue_id)
    return add_issue_comment_with_app_actor(
        issue_id,
        note_body,
        parent_id=parent_id,
        thread=False,
    )


def add_issue_comment_with_app_actor(
    issue_id: str,
    body: str,
    *,
    parent_id: str | None = None,
    thread: bool = True,
) -> dict[str, str]:
    input_payload: dict[str, Any] = {
        "issueId": linear_issue_uuid(issue_id),
        "body": body,
    }
    if thread:
        input_payload["parentId"] = parent_id or ensure_cockpit_thread_root(issue_id)
    elif parent_id:
        input_payload["parentId"] = parent_id
    create_as_user = os.environ.get("COCKPIT_LINEAR_COMMENT_CREATE_AS_USER")
    display_icon_url = os.environ.get("COCKPIT_LINEAR_COMMENT_DISPLAY_ICON_URL")
    if create_as_user:
        input_payload["createAsUser"] = create_as_user
    if display_icon_url:
        input_payload["displayIconUrl"] = display_icon_url
    data = run_linear_graphql(
        """
        mutation CockpitCommentCreate($input: CommentCreateInput!) {
          commentCreate(input: $input) {
            success
            comment { id url }
          }
        }
        """,
        {"input": input_payload},
    )
    result = data.get("commentCreate") if isinstance(data, dict) else None
    comment = result.get("comment") if isinstance(result, dict) else None
    if not isinstance(result, dict) or not result.get("success") or not isinstance(comment, dict):
        raise RuntimeError(f"Linear commentCreate did not succeed: {result}")
    return {"id": str(comment["id"]), "url": str(comment.get("url") or "")}


def add_issue_comment(
    issue_id: str,
    body: str,
    *,
    parent_id: str | None = None,
    thread: bool = True,
) -> None:
    add_issue_comment_with_app_actor(issue_id, body, parent_id=parent_id, thread=thread)


def read_comment_body(*, body: str | None = None, body_file: str | None = None) -> str:
    if body is not None and body_file:
        raise RuntimeError("Use either a positional comment body or --body-file, not both.")
    if body_file:
        return Path(body_file).read_text(encoding="utf-8")
    if body is not None:
        return body
    if sys.stdin.isatty():
        raise RuntimeError("Provide a comment body, --body-file, or pipe comment text on stdin.")
    return sys.stdin.read()


def comment_linear_issue(
    issue_id: str,
    *,
    body: str | None = None,
    body_file: str | None = None,
    reply_to: str | None = None,
    top_level: bool = False,
) -> int:
    try:
        if reply_to and top_level:
            print("Comment failed: use either --reply-to or --top-level, not both.")
            return 2
        text = read_comment_body(body=body, body_file=body_file).strip()
        if not text:
            print("Comment failed: empty comment body.")
            return 2
        add_issue_comment(issue_id, text, parent_id=reply_to, thread=not top_level)
        if not reply_to and not top_level:
            # Default path: a reply landed under the Cockpit Thread — a receipt.
            resolve_cockpit_thread_after_receipt(issue_id)
    except Exception as exc:
        print(f"Comment failed: {exc}")
        print(linear_app_auth_hint())
        return 1
    print(f"Commented on {issue_id}.")
    return 0


def resolve_linear_comment(comment_id: str, *, unresolve: bool = False) -> int:
    mutation_name = "commentUnresolve" if unresolve else "commentResolve"
    action = "unresolve" if unresolve else "resolve"
    try:
        data = run_linear_graphql(
            f"""
            mutation CockpitCommentResolve($id: String!) {{
              {mutation_name}(id: $id) {{
                success
                comment {{ id resolvedAt url }}
              }}
            }}
            """,
            {"id": comment_id},
        )
        result = data.get(mutation_name) if isinstance(data, dict) else None
        if not isinstance(result, dict) or not result.get("success"):
            raise RuntimeError(f"Linear {mutation_name} did not succeed: {result}")
    except Exception as exc:
        print(f"Comment {action} failed: {exc}")
        print(linear_app_auth_hint())
        return 1
    print(f"Comment {action}d as Linear app actor: {comment_id}")
    return 0


def resolve_cockpit_thread_after_receipt(issue_id: str) -> None:
    """Resolve the Cockpit Thread after cockpit posts a receipt to it.

    Best-effort: receipts are audit trail, not attention, so a resolve failure
    here must not fail the calling command (bind/release/move/comment already
    succeeded at that point). Idempotent — resolving an already-resolved
    comment is a no-op on Linear's side.

    Only the Cockpit Thread is touched. Questions, For Burooj, and Grilling
    threads are never auto-resolved (see reply_is_post_resolution(), which
    keeps a Burooj reply posted after resolution surfacing as new/unresolved).
    """
    try:
        root_id = cockpit_thread_root_comment_id(issue_id)
        if not root_id:
            return
        run_linear_graphql(
            """
            mutation CockpitThreadAutoResolve($id: String!) {
              commentResolve(id: $id) {
                success
              }
            }
            """,
            {"id": root_id},
        )
    except Exception:
        # Non-fatal: the receipt itself already landed.
        pass


def burooj_comment_author_names() -> set[str]:
    """Names that identify comments written by Burooj (not cockpit)."""
    names: set[str] = set()
    direct = os.environ.get("COCKPIT_BUROOJ_LINEAR_USER_NAME")
    if direct:
        names.update(name.strip().lower() for name in direct.split(",") if name.strip())
    # Fall back: names NOT in the cockpit author set are assumed Burooj's.
    return names


def comment_is_burooj_authored(comment: dict[str, Any]) -> bool:
    """Return True when the comment was written by Burooj (non-cockpit human author)."""
    # If cockpit authored it, it's definitely not Burooj.
    if comment_is_cockpit_authored(comment):
        return False
    burooj_names = burooj_comment_author_names()
    if not burooj_names:
        # No explicit Burooj names configured → assume any non-cockpit comment is Burooj's.
        return True
    user = comment.get("user")
    names: list[str] = []
    if isinstance(user, dict):
        for key in ("name", "displayName"):
            value = user.get(key)
            if value:
                names.append(str(value).strip().lower())
    return any(name in burooj_names for name in names)


# Prefixes that identify automated "run receipt" comments posted by worker
# processes under Burooj's personal Linear token.  Match case-insensitively
# against the *start* of the stripped comment body.
# NOTE: the durable fix is worker-side: workers should post receipts via the
# Cockpit app actor instead of Burooj's personal token so that
# comment_is_cockpit_authored() catches them.  Until that lands, this
# prefix-list is the lightweight guard on the inbox side.
_RUN_RECEIPT_PREFIXES: tuple[str, ...] = (
    "run receipt",
    "correction run receipt",
    "chrome apply run receipt",
    "run continuation receipt",
)


def is_run_receipt(comment: dict[str, Any]) -> bool:
    """Return True when the comment body looks like an automated worker receipt.

    Workers post receipts under Burooj's personal Linear token, so they pass
    comment_is_burooj_authored().  We detect them by their leading text so the
    inbox stays clean.  Add new prefixes to _RUN_RECEIPT_PREFIXES above.
    """
    body = comment_body(comment).strip().lower()
    return any(body.startswith(prefix) for prefix in _RUN_RECEIPT_PREFIXES)


def reply_is_post_resolution(
    comment: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
) -> bool:
    """Whether a reply should still surface in the comment backlog.

    A reply's own ``resolvedAt`` can't be set through the Linear API — resolving
    a child comment errors out — so we use its parent thread's ``resolvedAt`` as
    the proxy for "this thread was dealt with at time T". Resolving the
    *top-level* comment is the supported way to clear handled replies.

    A reply surfaces while its thread is still open, or when the reply was
    created *after* the thread was last resolved (a fresh note dropped on a
    closed thread). Top-level comments (no parentId) always pass here; they use
    their own resolved state via unresolved_comment().
    """
    parent_id = comment.get("parentId")
    if not parent_id:
        return True
    parent = by_id.get(parent_id)
    if parent is None:
        return True  # parent not in the fetched set; surface to be safe
    parent_resolved = parent.get("resolvedAt")
    if not parent_resolved:
        return True  # thread still open
    # Linear timestamps are ISO-8601 UTC, so string comparison is chronological.
    return (comment.get("createdAt") or "") > parent_resolved


def burooj_unresolved_comments_across_issues(
    issues: list[dict[str, Any]],
    *,
    limit_per_issue: int = 25,
) -> list[dict[str, Any]]:
    """
    Return a flat list of unresolved comments authored by Burooj,
    annotated with ``_issue_identifier`` and ``_issue_title``.

    Includes both top-level comments and replies so that genuine async notes
    left from phone/web are surfaced regardless of threading depth. A reply is
    only surfaced while its thread is open or if it was added after the thread
    was last resolved (see reply_is_post_resolution()), so resolving the
    top-level comment clears handled replies.

    Excludes:
    - Archived or resolved comments.
    - Replies whose thread was resolved at/after the reply.
    - Comments not authored by Burooj (cockpit-authored, etc.).
    - Automated run-receipt comments (posted under Burooj's token by workers;
      see is_run_receipt()).

    Only fetches comments for issues in active lanes; stops at
    ``limit_per_issue`` Burooj comments per issue to keep it fast (raised from 5
    to 25 so a handful of worker receipts can't mask real notes — receipts are
    now filtered out anyway).
    """
    results: list[dict[str, Any]] = []
    for issue in issues:
        if not issue_is_active(issue):
            continue
        try:
            comments = load_issue_comments(issue_identifier(issue))
        except Exception:
            continue
        by_id = {c.get("id"): c for c in comments if c.get("id")}
        count = 0
        for comment in comments:
            # The parentId guard was removed so genuine Burooj replies surface.
            if not unresolved_comment(comment):
                continue
            if not comment_is_burooj_authored(comment):
                continue
            if is_run_receipt(comment):
                continue
            # A reply can't carry its own resolvedAt (Linear errors on resolving
            # a child), so drop it once its thread was resolved at/after it.
            if not reply_is_post_resolution(comment, by_id):
                continue
            annotated = dict(comment)
            annotated["_issue_identifier"] = issue_identifier(issue)
            annotated["_issue_title"] = issue_title(issue)
            results.append(annotated)
            count += 1
            if count >= limit_per_issue:
                break
    return results


def print_inbox(*, limit: int = 20) -> int:
    """
    Print cockpit's work queue:

    1. Issues in Inbox or Ready-for-Burooj lanes (needing a triage decision).
    2. Burooj's unresolved comments across active issues (async channel backlog).
    """
    try:
        issues = load_linear_issues(limit=0)
    except Exception as exc:
        print(f"Inbox failed: {exc}")
        print(linear_app_auth_hint())
        return 1

    # --- Part 1: issues needing triage ---
    triage_candidates = [
        issue for issue in issues
        if issue_status_name(issue) in {"Inbox", "Ready for Burooj"}
    ][:limit]

    print(f"Inbox: {len(triage_candidates)} issue(s) needing triage decision")
    if triage_candidates:
        for issue in triage_candidates:
            labels = session_labels(issue)
            binding = f" {' '.join(labels)}" if labels else ""
            project = issue_project_name(issue)
            project_part = f" [{project}]" if project else ""
            print(
                f"- {issue_identifier(issue)}{project_part} "
                f"[{issue_status_name(issue)}]: "
                f"{compact(issue_title(issue), 90)}{binding}"
            )
            print(f"  inspect: ./cockpit.py issue {issue_identifier(issue)}")
    else:
        print("- none")

    # --- Part 2: Burooj's unresolved comments ---
    try:
        burooj_comments = burooj_unresolved_comments_across_issues(issues, limit_per_issue=25)
    except Exception as exc:
        print(f"\nComment backlog unavailable: {exc}")
        burooj_comments = []

    burooj_comments = burooj_comments[:limit]
    print(f"\nBurooj comment backlog: {len(burooj_comments)} unresolved comment(s)")
    if burooj_comments:
        for comment in burooj_comments:
            issue_id_str = str(comment.get("_issue_identifier") or "?")
            comment_id = str(comment.get("id") or "unknown")
            print(f"\n{comment_id} on {issue_id_str} — {compact(comment.get('_issue_title') or '', 60)}")
            print(f"  body: {compact(comment_body(comment), 200)}")
            print(f"  resolve: ./cockpit.py comment-resolve {comment_id}")
    else:
        print("- none")

    print("\nSafe next:")
    print("- Use `./cockpit.py issue BJS-X` to inspect a specific issue.")
    print("- Use `./cockpit.py prepare BJS-X` to get native launch context.")
    print("- Create the worker/session/thread with the active orchestration surface, then bind it.")
    print("- Use `./cockpit.py comment-resolve <id>` after handling a comment.")
    return 0


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
            move_linear_issue(issue_id, move_state)
            issue = load_linear_issue(issue_id)
        if not issue_is_active(issue) and not force:
            print(
                f"{issue_id} is `{issue_status_name(issue)}`; bind only active issues. "
                "Move it to an active lane first (e.g., In Progress / Ready for agent), or pass --force."
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
        resolve_cockpit_thread_after_receipt(issue_id)
    except Exception as exc:
        print(f"Bind failed: {exc}")
        print(linear_app_auth_hint())
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
            move_linear_issue(issue_id, move_state)
        for label in labels:
            remove_issue_label(issue_id, label)
        if archive_sessions:
            for label in labels:
                pair = split_session_label(label)
                if not pair:
                    continue
                provider, session_id = pair
                archived_session, message = archive_provider_session(provider, session_id)
                if archived_session:
                    archived.append(label)
                else:
                    print(f"WARN: could not archive {label}: {message}")
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
            resolve_cockpit_thread_after_receipt(issue_id)
    except Exception as exc:
        print(f"Release failed: {exc}")
        print(linear_app_auth_hint())
        return 1
    print(f"Released {issue_id}; removed {len(labels)} session label(s).")
    return 0


def archive_provider_session(provider: str, session_id: str) -> tuple[bool, str]:
    if provider == "claude":
        return (
            False,
            archive_result_json(
                provider,
                "claude_archive_unsupported",
                "Claude CLI exposes stop/rm, but no non-destructive archive matching cockpit semantics.",
            ),
        )
    if provider == "opencode":
        return (
            False,
            archive_result_json(
                provider,
                "opencode_archive_unsupported",
                "opencode session delete is destructive. Use cockpit-level state tracking instead.",
            ),
        )
    if provider == "cursor":
        return (
            False,
            archive_result_json(
                provider,
                "cursor_archive_unsupported",
                "Cursor agent CLI does not support archiving sessions.",
            ),
        )
    if provider != "codex":
        return False, archive_result_json(provider, "unknown_provider", f"unknown provider: {provider}")

    completed = subprocess.run(
        ["codex", "archive", session_id],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode == 0:
        return True, ""
    message = (completed.stderr or completed.stdout or f"Native command exited {completed.returncode}.").strip()
    return (
        False,
        json.dumps(
            {
                "data": {
                    "archived": False,
                    "exit_code": completed.returncode,
                    "id": session_id,
                    "stderr": completed.stderr,
                    "stdout": completed.stdout,
                },
                "debug": {"native_action": ["codex", "archive", session_id]},
                "error": {"code": "native_command_failed", "message": message},
                "ok": False,
                "provider": "codex",
                "verb": "archive",
                "warnings": [],
            },
            indent=2,
            sort_keys=True,
        ),
    )


def archive_result_json(provider: str, code: str, message: str) -> str:
    return json.dumps(
        {
            "data": {},
            "error": {"code": code, "message": message},
            "ok": False,
            "provider": provider,
            "verb": "archive",
            "warnings": [],
        },
        indent=2,
        sort_keys=True,
    )


def audit_linear_bindings(limit: int = 250) -> int:
    try:
        issues = load_linear_issues(limit=limit)
    except Exception as exc:
        print(f"Audit failed: {exc}")
        print(linear_app_auth_hint())
        return 1

    inactive_with_session: list[dict[str, Any]] = []
    in_progress_unbound: list[dict[str, Any]] = []
    ready_missing_executor: list[dict[str, Any]] = []
    multi_bound: list[dict[str, Any]] = []
    done_bound: list[dict[str, Any]] = []
    by_label: dict[str, list[str]] = {}
    root_checkout_sessions: list[tuple[dict[str, Any], str, str]] = []
    archived_bound: list[tuple[dict[str, Any], str, str]] = []
    sessions_by_key = session_lookup()
    archived_sessions = archived_codex_session_files()

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
        if issue_status_name(issue) == "Ready for agent" and not any(
            label.startswith("executor:") for label in issue_labels(issue)
        ):
            ready_missing_executor.append(issue)
        if issue_is_in_progress(issue) and labels and issue_is_pr_work(issue):
            root_checkout_sessions.extend(root_checkout_session_findings(issue, labels, sessions_by_key))
        if issue_is_in_progress(issue) and labels:
            archived_bound.extend(archived_session_findings(issue, labels, archived_sessions))

    duplicate_labels = {label: ids for label, ids in by_label.items() if len(ids) > 1}

    print(f"Linear binding audit ({len(issues)} issues loaded):")
    print(f"- inactive/done with session labels: {len(inactive_with_session)}")
    print(f"- In Progress without session label: {len(in_progress_unbound)}")
    print(f"- issues with multiple session labels: {len(multi_bound)}")
    print(f"- duplicate session labels across issues: {len(duplicate_labels)}")
    print(f"- Codex implementation sessions in root checkouts: {len(root_checkout_sessions)}")
    print(f"- In Progress bound to archived session: {len(archived_bound)}")
    print(f"- Ready for agent without executor:* label: {len(ready_missing_executor)}")

    print_audit_bucket("Inactive with session", inactive_with_session)
    print_audit_bucket("Ready for agent without executor label", ready_missing_executor)
    print_audit_bucket("In Progress without session", in_progress_unbound)
    print_audit_bucket("Multiple session labels", multi_bound)
    print_root_checkout_session_bucket(root_checkout_sessions)
    print_archived_session_bucket(archived_bound, archived_sessions)
    if duplicate_labels:
        print("\nDuplicate session labels:")
        for label, ids in sorted(duplicate_labels.items()):
            print(f"- {label}: {', '.join(ids)}")
    return (
        1
        if inactive_with_session
        or in_progress_unbound
        or multi_bound
        or duplicate_labels
        or root_checkout_sessions
        or archived_bound
        else 0
    )


def print_archived_session_bucket(
    rows: list[tuple[dict[str, Any], str, str]],
    archived_sessions: dict[str, str],
) -> None:
    print(f"\nIn Progress bound to archived session ({len(rows)}):")
    if not rows:
        if not archived_sessions:
            print(f"- none (no archived codex sessions found at {CODEX_ARCHIVED_SESSIONS_DIR})")
        else:
            print("- none")
        return
    for issue, label, rollout in rows:
        print(
            f"- {issue_identifier(issue)} [{issue_status_name(issue)}]: "
            f"{compact(issue_title(issue), 80)} {label} archived={rollout}"
        )
        print("  expected: session is archived; re-bind to a live session or move the issue off In Progress")


def root_checkout_session_findings(
    issue: dict[str, Any],
    labels: list[str],
    sessions_by_key: dict[tuple[str, str], dict[str, Any]],
) -> list[tuple[dict[str, Any], str, str]]:
    project_dir = resolve_issue_project_dir(issue)
    if project_dir is None or git_root(project_dir) is None:
        return []
    findings: list[tuple[dict[str, Any], str, str]] = []
    project_root = git_root(project_dir)
    if project_root is None:
        return []
    for label in labels:
        parsed = split_session_label(label)
        if not parsed:
            continue
        provider, session_id = parsed
        if provider != "codex":
            continue
        session = sessions_by_key.get((provider, session_id))
        workspace = session.get("workspace") if session else None
        if not isinstance(workspace, str) or not workspace:
            continue
        workspace_path = Path(workspace).expanduser()
        workspace_root = git_root(workspace_path)
        if workspace_root == project_root and "/.codex/worktrees/" not in str(workspace_path):
            findings.append((issue, label, workspace))
    return findings


def print_root_checkout_session_bucket(rows: list[tuple[dict[str, Any], str, str]]) -> None:
    print(f"\nCodex implementation sessions in root checkouts ({len(rows)}):")
    if not rows:
        print("- none")
        return
    for issue, label, workspace in rows:
        print(
            f"- {issue_identifier(issue)} [{issue_status_name(issue)}]: "
            f"{compact(issue_title(issue), 80)} {label} cwd={workspace}"
        )
        print("  expected: create/bind a Codex Desktop worktree session, not a root local-project session")


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
    if provider == "opencode":
        return f'opencode run --format json --session {session_id} "<prompt>"'
    return f"{provider} resume {session_id}"


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


def _projects_registry() -> dict[str, str]:
    """
    Return the optional [projects] table from .linear.toml.

    The table maps Linear project name (or slug) to an absolute local directory:

        [projects]
        "My Project" = "/Users/burooj/Projects/my-project"
        skills       = "/Users/burooj/Projects/skills"

    Entries override the name-based fallback in resolve_issue_project_dir.
    """
    projects = LINEAR_CONFIG.get("projects")
    if isinstance(projects, dict):
        return {str(k): str(v) for k, v in projects.items()}
    return {}


def resolve_issue_project_dir(issue: dict[str, Any]) -> Path | None:
    """
    Attempt to resolve the local directory for the issue's Linear project.

    Strategy (best-effort, deterministic):
    1. [projects] registry in .linear.toml — keyed by project name or slug.
    2. Explicit absolute path embedded in the issue description.
    3. GitHub repo URL in the issue body (``repo: https://github.com/...``):
       derive the target dir from the repo name under /Users/burooj/Projects.
    4. Match the issue's project name / slug against existing dirs under
       /Users/burooj/Projects.
    5. Return None if no mapping can be determined.
    """
    registry = _projects_registry()

    # 1. Project→dir registry from .linear.toml [projects].
    project_name = issue_project_name(issue)
    if project_name:
        slug = re.sub(r"[^a-z0-9-]", "", project_name.lower().replace(" ", "-"))
        for key in (project_name, slug):
            if key in registry:
                candidate = Path(registry[key]).expanduser()
                if candidate.exists():
                    return candidate
                # Entry exists but dir is missing — treat as authoritative; caller
                # will handle creation / cloning via ensure_project_dir.
                return candidate

    text = issue_description(issue)

    # 2. Explicit absolute path in the issue body.
    path_match = re.search(r"(/Users/[^\s`),]+|~/[^\s`),]+)", text)
    if path_match:
        candidate = Path(path_match.group(1)).expanduser()
        if candidate.exists():
            return candidate

    # 3. Explicit repo URL in the issue body (``repo: https://github.com/...``).
    repo_match = re.search(
        r"(?:repo|repository)\s*:\s*(https?://github\.com/[^\s]+)",
        text,
        re.IGNORECASE,
    )
    if repo_match:
        url = repo_match.group(1).rstrip("/")
        repo_name = url.rstrip(".git").split("/")[-1]
        target_dir = Path("/Users/burooj/Projects") / repo_name
        if target_dir.exists():
            return target_dir
        return target_dir

    # 4. Match project name to a directory under /Users/burooj/Projects.
    if project_name:
        slug = re.sub(r"[^a-z0-9-]", "", project_name.lower().replace(" ", "-"))
        projects_root = Path("/Users/burooj/Projects")
        for candidate_name in (project_name, slug):
            candidate = projects_root / candidate_name
            if candidate.is_dir():
                return candidate

    return None


def ensure_project_dir(issue: dict[str, Any], resolved: Path | None) -> Path | None:
    """
    Ensure the project dir exists.  If resolved is None (no mapping could be
    determined) return None immediately.  If resolved points to a missing path,
    create it (brand-new, non-git project).

    Repository cloning is outside cockpit.py; use native orchestration or an
    explicit project setup step when a repo needs to be cloned.
    """
    if resolved is None:
        return None

    if resolved.exists():
        return resolved

    # Path was determined but doesn't exist → create it (brand-new project).
    try:
        resolved.mkdir(parents=True, exist_ok=True)
        print(f"prepare: created directory {resolved}")
        return resolved
    except OSError as exc:
        print(f"prepare: could not create {resolved}: {exc}")
        return None


def slugify_for_path(value: str, *, default: str = "work") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or default


def issue_branch_name(issue: dict[str, Any]) -> str:
    issue_id = issue_identifier(issue)
    issue_slug = slugify_for_path(issue_id)
    title_slug = slugify_for_path(issue_title(issue), default="issue")[:48].strip("-")
    return f"codex/{issue_slug}-{title_slug}" if title_slug else f"codex/{issue_slug}"


def git_branch_exists(repo_dir: Path, branch_name: str) -> bool:
    completed = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
        cwd=repo_dir,
    )
    return completed.returncode == 0


def git_worktrees_for_branch(repo_dir: Path, branch_name: str) -> list[str]:
    completed = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return []
    current_path: str | None = None
    paths: list[str] = []
    for line in completed.stdout.splitlines():
        if line.startswith("worktree "):
            current_path = line.removeprefix("worktree ").strip()
        elif line.startswith("branch ") and current_path:
            ref = line.removeprefix("branch ").strip()
            if ref == f"refs/heads/{branch_name}":
                paths.append(current_path)
    return paths


def git_branch_preflight(repo_dir: Path, branch_name: str) -> dict[str, Any]:
    repo_root = git_root(repo_dir)
    if repo_root is None:
        return {
            "name": branch_name,
            "repo": None,
            "exists": False,
            "checked_out_worktrees": [],
            "safe_to_start_from_branch": False,
        }
    checked_out = git_worktrees_for_branch(repo_root, branch_name)
    exists = git_branch_exists(repo_root, branch_name)
    return {
        "name": branch_name,
        "repo": str(repo_root),
        "exists": exists,
        "checked_out_worktrees": checked_out,
        "safe_to_start_from_branch": exists and not checked_out,
    }


def ensure_codex_project(project_dir: Path) -> bool:
    """
    Run `codex app <dir>` to register the directory as a Codex saved project.
    Returns True on success, False on failure (non-fatal; prepare proceeds).

    Verified correct for codex-cli 0.139.0: `codex app [PATH]` opens/registers
    a workspace in Codex Desktop.
    """
    codex_bin = shutil.which("codex")
    if not codex_bin:
        print("prepare: WARN: codex binary not found; skipping `codex app` registration.")
        return False
    completed = subprocess.run(
        [codex_bin, "app", str(project_dir)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        print(
            f"prepare: WARN: `codex app {project_dir}` failed "
            f"(exit {completed.returncode}): {(completed.stderr or completed.stdout).strip()[:200]}"
        )
        return False
    return True


def build_worker_brief(issue: dict[str, Any], comments: list[dict[str, Any]]) -> str:
    """
    Derive a plain-text worker brief from the issue body + unresolved comments.
    """
    issue_id = issue_identifier(issue)
    title = issue_title(issue)
    description = issue_description(issue)
    unresolved_bodies: list[str] = []
    for c in comments:
        if c.get("archivedAt") or c.get("parentId"):
            continue
        if not unresolved_comment(c):
            continue
        body_text = comment_body(c).strip()
        if COCKPIT_THREAD_MARKER in body_text or QUESTIONS_THREAD_MARKER in body_text:
            continue
        if body_text:
            unresolved_bodies.append(body_text)

    parts = [
        f"# {issue_id}: {title}",
        "",
        description or "(no description)",
    ]
    if unresolved_bodies:
        parts.append("\n## Unresolved comments")
        for body_text in unresolved_bodies:
            parts.append(f"\n---\n{body_text}")
    parts.extend([
        "",
        "## Stop gates (always apply)",
        "- Do not spend money, send email, delete accounts/data, or make broad workflow changes without explicit Burooj approval.",
        "- Do not bind/release sessions or move this issue's status unless cockpit explicitly asks you to.",
        "- For implementation work, do not claim Done from local commits alone. Produce a review artifact first: normally a pushed branch plus draft/ready PR.",
        "",
        "## Cockpit commands for this issue",
        f"./cockpit.py issue {issue_id}",
        f"./cockpit.py comment {issue_id} \"<update>\"",
        f"./cockpit.py move {issue_id} \"In Review\"  # only after PR/review artifact exists",
        f"./cockpit.py move {issue_id} Done         # only after acceptance/merge or explicit no-review closure",
    ])
    return "\n".join(parts)

def prepare_issue(
    issue_id: str,
    *,
    provider: str = "codex",
    ensure_root_project: bool = False,
    create_dir: bool = False,
) -> dict[str, Any]:
    """
    Prepare native orchestration context without creating issue worktrees or sessions.

    This is the preferred Desktop path: cockpit emits the root project, branch intent,
    and brief; the active surface creates the thread/session natively and binds it.
    """
    issue = load_linear_issue(issue_id)
    comments = load_issue_comments(issue_id)
    resolved_dir = resolve_issue_project_dir(issue)
    project_dir = ensure_project_dir(issue, resolved_dir) if create_dir else resolved_dir
    if project_dir is None:
        project_name = issue_project_name(issue) or "(unknown)"
        raise RuntimeError(
            f"could not determine working directory for {issue_id} (project: {project_name}). "
            "Fix: add a path (/Users/burooj/Projects/my-repo) or repo URL "
            "(repo: https://github.com/owner/my-repo) to the issue body, "
            f'or add "{project_name}" = "/path/to/dir" under [projects] in cockpit/.linear.toml.'
        )
    if not project_dir.exists() and not create_dir:
        raise RuntimeError(
            f"resolved project directory does not exist: {project_dir}. "
            "Pass --create-dir if this is an intentional brand-new local project."
        )
    if provider == "codex" and ensure_root_project:
        ensure_codex_project(project_dir)
    branch_name = issue_branch_name(issue)
    branch_preflight = git_branch_preflight(project_dir, branch_name)
    codex_target = {
        "type": "project",
        "projectId": str(project_dir),
        "environment": {
            "type": "worktree",
            "startingState": {"type": "working-tree"},
        },
    } if provider == "codex" else None
    bind_example = f"./cockpit.py bind {issue_identifier(issue)} {provider} <session-id> --move-state \"In Progress\""
    return {
        "issue_id": issue_identifier(issue),
        "title": issue_title(issue),
        "provider": provider,
        "project_dir": str(project_dir),
        "root_project_dir": str(project_dir),
        "codex_project_id": str(project_dir) if provider == "codex" else None,
        "branch": branch_preflight,
        "codex_desktop_target": codex_target,
        "brief": build_worker_brief(issue, comments),
        "next_actions": [
            "Create the native worker/session/thread in the active orchestration surface.",
            "For Codex Desktop, use codex_desktop_target exactly: project root plus environment.type=worktree.",
            "After the thread opens, verify the worker cwd is not the root checkout and have it create/switch to the branch name from branch.name.",
            bind_example,
        ],
        "notes": [
            "For Codex Desktop, never use target.environment.type=local for implementation work in a git repo.",
            "Do not register the issue worktree as its own saved Codex project.",
            "branch.name is branch intent, not the native worktree startingState. Reusing it as startingState can collide with stale branches/worktrees.",
            "If branch.checked_out_worktrees is non-empty, resume or clean that worktree before launching a new worker.",
        ],
    }


def print_prepare(
    issue_id: str,
    *,
    provider: str = "codex",
    ensure_root_project: bool = False,
    create_dir: bool = False,
) -> int:
    try:
        with contextlib.redirect_stdout(sys.stderr):
            prepared = prepare_issue(
                issue_id,
                provider=provider,
                ensure_root_project=ensure_root_project,
                create_dir=create_dir,
            )
    except Exception as exc:
        print(f"prepare: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(prepared, indent=2))
    return 0

def create_issue_command(
    title: str,
    *,
    project: str | None = None,
    state: str | None = None,
    description: str | None = None,
    labels: list[str] | None = None,
) -> int:
    try:
        created = create_issue_with_app_actor(
            title,
            project=project,
            state=state,
            description=description,
            labels=labels,
        )
    except Exception as exc:
        print(f"Create failed: {exc}")
        print(linear_app_auth_hint())
        return 1
    print(f"Created {created.get('identifier') or created.get('id')}: {created.get('title')}")
    if created.get("url"):
        print(f"- url: {created['url']}")
    if isinstance(created.get("state"), dict):
        print(f"- lane: {created['state'].get('name')}")
    return 0


def warn_if_ready_for_burooj_missing_brief(issue_id: str, state_name: str) -> None:
    """Loud (non-fatal) warning when moving to Ready for Burooj without a current brief.

    Mirrors the Ready-for-agent readiness bar: a Ready-for-Burooj issue without
    a For Burooj brief isn't ready. Does not block the move — Burooj's calls
    on his own board are not cockpit's to veto.
    """
    if state_name.strip().lower() != "ready for burooj":
        return
    try:
        root = for_burooj_thread_root_comment(issue_id)
    except Exception as exc:
        print(f"WARN: could not check For Burooj thread for {issue_id}: {exc}")
        return
    if root is None:
        print(
            f"WARN: {issue_id} moved to `Ready for Burooj` with no For Burooj brief. "
            f"Post one with `./cockpit.py comment {issue_id} --brief \"...\"` — this lane's "
            "readiness bar is the brief, same as Ready-for-agent's goal-grade Done-when."
        )
        return
    if not unresolved_comment(root):
        print(
            f"WARN: {issue_id} moved to `Ready for Burooj` but its For Burooj thread is resolved "
            f"(stale). Post a current brief with `./cockpit.py comment {issue_id} --brief \"...\"`."
        )


def move_issue_command(issue_id: str, state_name: str, *, comment: bool = True) -> int:
    try:
        move_linear_issue(issue_id, state_name)
        if comment:
            add_issue_comment(
                issue_id,
                "\n".join(
                    [
                        f"Moved `{issue_id}` to `{state_name}`.",
                        "",
                        "Reason: explicit cockpit state move.",
                    ]
                ),
            )
            resolve_cockpit_thread_after_receipt(issue_id)
        warn_if_ready_for_burooj_missing_brief(issue_id, state_name)
    except Exception as exc:
        print(f"Move failed: {exc}")
        print(linear_app_auth_hint())
        return 1
    print(f"Moved {issue_id} -> {state_name}")
    return 0


def move_project_command(project_ref: str, state_name: str) -> int:
    try:
        moved = move_project_with_app_actor(project_ref, state_name)
        status = moved.get("status") if isinstance(moved.get("status"), dict) else {}
        open_issues = project_open_issues(str(moved["id"]))
    except CockpitUsageError as exc:
        print(f"Project move failed: {exc}")
        return 1
    except Exception as exc:
        print(f"Project move failed: {exc}")
        print(linear_app_auth_hint())
        return 1
    print(f"Moved project {moved.get('name')} -> {status.get('name') or state_name}")
    if open_issues:
        print(project_open_issues_note(open_issues))
    return 0


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
    issue_parser.add_argument("--full", action="store_true", help="Print the full untruncated description.")
    issue_parser.add_argument(
        "--show-cockpit",
        action="store_true",
        help="Also show unresolved cockpit-authored comments and run receipts.",
    )
    inbox_parser = sub.add_parser(
        "inbox",
        help="List issues needing triage and Burooj's unresolved comment backlog.",
    )
    inbox_parser.add_argument("--limit", type=int, default=20)
    prepare_parser = sub.add_parser(
        "prepare",
        help="Resolve issue/project context and print a native orchestration launch brief as JSON.",
    )
    prepare_parser.add_argument("issue_id")
    prepare_parser.add_argument(
        "--provider",
        default="codex",
        choices=["codex", "claude", "opencode"],
        help="Worker provider to prepare (default: codex).",
    )
    prepare_parser.add_argument(
        "--ensure-root-project",
        action="store_true",
        help="For Codex, run `codex app <root-project-dir>`; never registers issue worktrees.",
    )
    prepare_parser.add_argument(
        "--create-dir",
        action="store_true",
        help="Create a missing resolved project directory for brand-new local projects.",
    )
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
    move_parser = sub.add_parser("move", help="Explicitly move a Linear issue to a workflow state.")
    move_parser.add_argument("issue_id")
    move_parser.add_argument("state_name")
    move_parser.add_argument("--no-comment", action="store_true", help="Do not add a state-move comment.")
    project_move_parser = sub.add_parser("project-move", help="Move a Linear project to a project status.")
    project_move_parser.add_argument("project")
    project_move_parser.add_argument("state_name")
    label_parser = sub.add_parser("label", help="Add or remove issue labels as the Cockpit app actor.")
    label_parser.add_argument("issue_id")
    label_parser.add_argument("--add", action="append", default=[], help="Label to add (repeatable).")
    label_parser.add_argument("--remove", action="append", default=[], help="Label to remove (repeatable).")
    create_parser = sub.add_parser("create", help="Create a Linear issue as the Cockpit app actor.")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--project", help="Linear project name.")
    create_parser.add_argument("--state", help="Initial workflow lane, e.g. 'Ready for agent'.")
    create_parser.add_argument("--description", help="Issue body markdown.")
    create_parser.add_argument("--description-file", help="Read the issue body from a markdown/text file.")
    create_parser.add_argument("--label", action="append", dest="labels", help="Label to attach (repeatable).")
    comment_parser = sub.add_parser("comment", help="Add a Cockpit-authored Linear issue comment.")
    comment_parser.add_argument("issue_id")
    comment_parser.add_argument("body", nargs="?")
    comment_parser.add_argument("--body-file", help="Read the comment body from a markdown/text file.")
    comment_parser.add_argument("--reply-to", help="Reply to an existing Linear comment id.")
    comment_parser.add_argument(
        "--top-level",
        action="store_true",
        help="Create a top-level comment instead of replying under the issue's Cockpit Thread.",
    )
    comment_parser.add_argument(
        "--question",
        action="store_true",
        help="Add the comment as a reply under the issue's Questions thread (for Burooj).",
    )
    comment_parser.add_argument(
        "--brief",
        action="store_true",
        help="Add the comment as a reply under the issue's For Burooj thread (decision brief).",
    )
    comment_parser.add_argument(
        "--grilling",
        action="store_true",
        help="Add the comment as a reply under the issue's Grilling thread (shaping note).",
    )
    resolve_parser = sub.add_parser("comment-resolve", help="Resolve a Linear comment as Cockpit.")
    resolve_parser.add_argument("comment_id")
    unresolve_parser = sub.add_parser("comment-unresolve", help="Unresolve a Linear comment as Cockpit.")
    unresolve_parser.add_argument("comment_id")
    audit_parser = sub.add_parser("audit", help="Audit Linear session labels against issue status.")
    audit_parser.add_argument("--limit", type=int, default=0, help="Maximum issues to load; 0 means all.")
    sub.add_parser("linear-doctor", help="Check the Linear GraphQL app-actor surface and auth.")
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
        return print_status(project=getattr(args, "project", None))
    if command == "board":
        return print_linear_board(limit=args.limit, project=args.project)
    if command == "issue":
        return print_linear_issue(args.issue_id, full=args.full, show_cockpit=args.show_cockpit)
    if command == "inbox":
        return print_inbox(limit=args.limit)
    if command == "prepare":
        return print_prepare(
            args.issue_id,
            provider=args.provider,
            ensure_root_project=args.ensure_root_project,
            create_dir=args.create_dir,
        )
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
    if command == "move":
        return move_issue_command(
            args.issue_id,
            args.state_name,
            comment=not args.no_comment,
        )
    if command == "project-move":
        return move_project_command(args.project, args.state_name)
    if command == "label":
        if not args.add and not args.remove:
            print("Nothing to do: pass --add and/or --remove.")
            return 1
        if any(SESSION_LABEL_RE.match(label) for label in args.add + args.remove):
            print("Refusing to touch session:* labels here; use bind/release.")
            return 1
        try:
            for label in args.add:
                add_issue_label_with_app_actor(args.issue_id, label)
                print(f"Added {label} to {args.issue_id}.")
            for label in args.remove:
                remove_issue_label_with_app_actor(args.issue_id, label)
                print(f"Removed {label} from {args.issue_id}.")
        except Exception as exc:
            print(f"Label update failed: {exc}")
            print(linear_app_auth_hint())
            return 1
        return 0
    if command == "create":
        description = args.description
        if getattr(args, "description_file", None):
            try:
                description = Path(args.description_file).read_text()
            except OSError as exc:
                print(f"Create failed: could not read {args.description_file}: {exc}")
                return 1
        return create_issue_command(
            args.title,
            project=args.project,
            state=args.state,
            description=description,
            labels=args.labels,
        )
    if command == "comment":
        exclusive_flags = [
            name
            for name in ("question", "brief", "grilling")
            if getattr(args, name, False)
        ]
        if len(exclusive_flags) > 1:
            print(f"Comment failed: use only one of --question/--brief/--grilling, not {exclusive_flags}.")
            return 2
        if getattr(args, "question", False):
            try:
                text = read_comment_body(body=args.body, body_file=args.body_file).strip()
                if not text:
                    print("Comment failed: empty comment body.")
                    return 2
                result = add_question_to_issue(args.issue_id, text)
                print(f"Question added to {args.issue_id}: {result.get('url') or result.get('id')}")
                return 0
            except Exception as exc:
                print(f"Comment (question) failed: {exc}")
                print(linear_app_auth_hint())
                return 1
        if getattr(args, "brief", False):
            try:
                text = read_comment_body(body=args.body, body_file=args.body_file).strip()
                if not text:
                    print("Comment failed: empty comment body.")
                    return 2
                result = add_brief_to_issue(args.issue_id, text)
                print(f"Brief added to {args.issue_id}: {result.get('url') or result.get('id')}")
                return 0
            except Exception as exc:
                print(f"Comment (brief) failed: {exc}")
                print(linear_app_auth_hint())
                return 1
        if getattr(args, "grilling", False):
            try:
                text = read_comment_body(body=args.body, body_file=args.body_file).strip()
                if not text:
                    print("Comment failed: empty comment body.")
                    return 2
                result = add_grilling_note_to_issue(args.issue_id, text)
                print(f"Grilling note added to {args.issue_id}: {result.get('url') or result.get('id')}")
                return 0
            except Exception as exc:
                print(f"Comment (grilling) failed: {exc}")
                print(linear_app_auth_hint())
                return 1
        return comment_linear_issue(
            args.issue_id,
            body=args.body,
            body_file=args.body_file,
            reply_to=args.reply_to,
            top_level=args.top_level,
        )
    if command == "comment-resolve":
        return resolve_linear_comment(args.comment_id)
    if command == "comment-unresolve":
        return resolve_linear_comment(args.comment_id, unresolve=True)
    if command == "audit":
        return audit_linear_bindings(limit=args.limit)
    if command == "linear-doctor":
        return print_linear_doctor()
    if command == "sessions":
        return print_sessions(limit=args.limit, include_archive=args.archive)
    parser.error(f"unknown command: {command}")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:
        if os.environ.get("COCKPIT_DEBUG"):
            raise
        print(f"cockpit: error: {exc}", file=sys.stderr)
        sys.exit(1)

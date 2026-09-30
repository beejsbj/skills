#!/usr/bin/env python3
"""HTTP-to-stdio MCP relay for Tududi."""

import json
import os
import stat
import sys
import urllib.error
import urllib.request

MCP_ENDPOINT = "https://tududi.burooj.dev/api/mcp"
CONFIG_PATH = os.path.expanduser("~/.config/tududi/agent.env")
TIMEOUT_SECS = 60


def load_token(path: str = CONFIG_PATH) -> str:
    """Load TUDUDI_API_TOKEN from config file without executing it."""
    st = os.stat(path)
    if not stat.S_ISREG(st.st_mode):
        raise PermissionError(f"Config path {path} is not a regular file")
    if (st.st_mode & 0o077) != 0:
        raise PermissionError(
            f"Config file {path} has insecure permissions (mode {oct(st.st_mode)}): owner-only required"
        )
    token = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" in line:
                key, val = line.split("=", 1)
                if key.strip() == "TUDUDI_API_TOKEN":
                    val = val.strip()
                    if (val.startswith('"') and val.endswith('"')) or (
                        val.startswith("'") and val.endswith("'")
                    ):
                        val = val[1:-1]
                    elif " #" in val:
                        val = val.split(" #", 1)[0].strip()
                    token = val
    if not token:
        raise ValueError(f"TUDUDI_API_TOKEN not found in {path}")
    return token


def parse_sse(text: str) -> list[dict]:
    """Parse Server-Sent Events stream, joining multiline data per event."""
    events: list[dict] = []
    data_lines: list[str] = []

    def flush_event():
        nonlocal data_lines
        if data_lines:
            raw = "\n".join(data_lines)
            data_lines = []
            try:
                events.append(json.loads(raw))
            except Exception:
                sys.stderr.write("Malformed SSE event skipped\n")
                sys.stderr.flush()

    for line in text.splitlines():
        if line.startswith(":"):
            continue
        if line.startswith("data:"):
            val = line[5:]
            if val.startswith(" "):
                val = val[1:]
            data_lines.append(val)
        elif line == "data":
            data_lines.append("")
        elif not line:
            flush_event()
    flush_event()
    return events


def parse_response(body: str, content_type: str = "", status_code: int = 200) -> list[dict]:
    """Parse HTTP response body as JSON or SSE records."""
    if (status_code == 202 and not body.strip()) or not body.strip():
        return []
    ct = content_type.lower()
    if "text/event-stream" in ct or body.lstrip().startswith(("data:", "event:", ":")):
        return parse_sse(body)
    data = json.loads(body)
    return data if isinstance(data, list) else [data]


def emit_json(obj: object) -> None:
    """Emit compact JSON line to stdout and flush."""
    sys.stdout.write(json.dumps(obj, separators=(",", ":")) + "\n")
    sys.stdout.flush()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def forward_request(msg: dict, token: str) -> None:
    """Forward a single JSON-RPC message to the fixed MCP endpoint."""
    is_notification = "id" not in msg
    req_id = msg.get("id") if not is_notification else None

    req_data = json.dumps(msg).encode("utf-8")
    req = urllib.request.Request(
        MCP_ENDPOINT,
        data=req_data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json,text/event-stream",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )

    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=TIMEOUT_SECS) as resp:
            status = getattr(resp, "status", resp.getcode())
            ct = resp.headers.get("Content-Type", "")
            body = resp.read().decode("utf-8", errors="replace")
            messages = parse_response(body, content_type=ct, status_code=status)
            for m in messages:
                emit_json(m)
    except urllib.error.HTTPError as e:
        if is_notification:
            sys.stderr.write(f"Notification delivery failed: HTTP {e.code}\n")
            sys.stderr.flush()
        else:
            emit_json({"jsonrpc": "2.0", "id": req_id,
                       "error": {"code": -32603, "message": f"HTTP {e.code}"}})

    except Exception:
        if is_notification:
            sys.stderr.write("Notification delivery failed: network error\n")
            sys.stderr.flush()
        else:
            emit_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32603,
                    "message": "Network error",
                },
            })


def main() -> None:
    try:
        token = load_token()
    except Exception as e:
        sys.stderr.write(f"Failed to load token: {e}\n")
        sys.stderr.flush()
        sys.exit(1)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            emit_json({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error",
                },
            })
            continue

        if not isinstance(msg, dict):
            emit_json({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request",
                },
            })
            continue

        forward_request(msg, token)


if __name__ == "__main__":
    main()

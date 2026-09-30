#!/usr/bin/env python3
"""Minimal meaningful parser tests for tududi mcp-stdio relay."""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
import io
import contextlib
import urllib.error

# Import mcp-stdio.py dynamically without side effects
script_path = Path(__file__).parent / "mcp-stdio.py"
spec = importlib.util.spec_from_file_location("mcp_stdio", script_path)
mcp_stdio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_stdio)


class TestMcpStdioParser(unittest.TestCase):
    def test_http_error_does_not_echo_response_body(self):
        opener = MagicMock()
        opener.open.side_effect = urllib.error.HTTPError(
            "https://tududi.burooj.dev/api/mcp", 401, "Unauthorized", {},
            io.BytesIO(b'{"secret":"test-credential"}'))
        output = io.StringIO()
        with patch.object(mcp_stdio.urllib.request, "build_opener", return_value=opener), contextlib.redirect_stdout(output):
            mcp_stdio.forward_request({"jsonrpc": "2.0", "id": 7, "method": "tools/list"}, "dummy")
        response = mcp_stdio.json.loads(output.getvalue())
        self.assertEqual(response["id"], 7)
        self.assertEqual(response["error"]["message"], "HTTP 401")
        self.assertNotIn("test-credential", output.getvalue())

    def test_redirect_is_not_followed(self):
        self.assertIsNone(mcp_stdio.NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.invalid"))

    def test_plain_json(self):
        # Plain JSON response
        body = '{"jsonrpc":"2.0","result":{"tools":[]},"id":1}'
        res = mcp_stdio.parse_response(body, content_type="application/json", status_code=200)
        self.assertEqual(res, [{"jsonrpc": "2.0", "result": {"tools": []}, "id": 1}])

    def test_sse_multiline_crlf(self):
        # SSE event with CRLF and multiline data
        sse = (
            "data: {\r\n"
            'data: "jsonrpc": "2.0",\r\n'
            'data: "result": "ok",\r\n'
            'data: "id": 2\r\n'
            "data: }\r\n\r\n"
        )
        res = mcp_stdio.parse_response(sse, content_type="text/event-stream", status_code=200)
        self.assertEqual(res, [{"jsonrpc": "2.0", "result": "ok", "id": 2}])

    def test_empty202(self):
        # HTTP 202 with empty response
        res1 = mcp_stdio.parse_response("", content_type="application/json", status_code=202)
        self.assertEqual(res1, [])

        res2 = mcp_stdio.parse_response("   \r\n  ", content_type="", status_code=202)
        self.assertEqual(res2, [])

    def test_malformed_events(self):
        # Malformed event skipped while valid event is retained
        sse = (
            "data: {not valid json\r\n\r\n"
            'data: {"jsonrpc": "2.0", "result": "recovered", "id": 3}\r\n\r\n'
            "data: another broken event\r\n\r\n"
        )
        res = mcp_stdio.parse_response(sse, content_type="text/event-stream", status_code=200)
        self.assertEqual(res, [{"jsonrpc": "2.0", "result": "recovered", "id": 3}])

        res_empty = mcp_stdio.parse_response("data: {broken\n\n", content_type="text/event-stream")
        self.assertEqual(res_empty, [])


if __name__ == "__main__":
    unittest.main()

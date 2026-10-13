#!/usr/bin/env python3
"""
Golden tests for scripts/active/postman_api_request.sh — the helper the Makefile cleanup
targets use for every Postman API call. Before 2026-10-13 those targets called
`curl --silent` directly, which exits 0 on HTTP errors: a refused list call read as an
empty workspace and a refused delete was ignored (and the spec-delete loops could spin).

A local HTTP server stands in for the Postman API.

Run via:
    python -m pytest scripts/validation/tests/test_postman_api_request.py -v
or:
    make validate-collections-conformance-test
"""

import http.server
import socket
import subprocess
import threading
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
HELPER = REPO_ROOT / "scripts" / "active" / "postman_api_request.sh"

# path -> (status, body)
ROUTES = {
    "/ok": (200, b'{"mocks": []}'),
    "/denied": (401, b'{"error": {"name": "AuthenticationError"}}'),
    "/missing": (404, b'{"error": {"name": "instanceNotFoundError"}}'),
    "/bad": (400, b'{"detail": "The query parameter /status is invalid."}'),
}


class _Handler(http.server.BaseHTTPRequestHandler):
    def _reply(self):
        status, body = ROUTES.get(self.path.split("?")[0], (500, b"{}"))
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_DELETE = _reply

    def log_message(self, *_args):
        pass


class TestPostmanApiRequest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def run_helper(self, method, url):
        return subprocess.run(["bash", str(HELPER), method, url, "--header", "X-Api-Key: test"],
                              capture_output=True, text=True, timeout=30)

    def test_success_prints_body(self):
        r = self.run_helper("GET", f"{self.base}/ok")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('"mocks"', r.stdout)

    def test_auth_failure_on_list_fails(self):
        """The old cleanup read this as 'No mock servers found in workspace'."""
        r = self.run_helper("GET", f"{self.base}/denied")
        self.assertEqual(r.returncode, 1)
        self.assertIn("HTTP 401", r.stderr)
        self.assertEqual(r.stdout, "")

    def test_bad_request_fails(self):
        """postman-api-clean-trash got this on every build and reported 'No trashed specs'."""
        r = self.run_helper("GET", f"{self.base}/bad?status=trashed")
        self.assertEqual(r.returncode, 1)
        self.assertIn("HTTP 400", r.stderr)

    def test_refused_delete_fails(self):
        r = self.run_helper("DELETE", f"{self.base}/denied")
        self.assertEqual(r.returncode, 1)

    def test_delete_of_missing_resource_succeeds(self):
        r = self.run_helper("DELETE", f"{self.base}/missing")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_get_of_missing_resource_fails(self):
        r = self.run_helper("GET", f"{self.base}/missing")
        self.assertEqual(r.returncode, 1)

    def test_connection_failure_fails(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        r = self.run_helper("GET", f"http://127.0.0.1:{port}/ok")
        self.assertEqual(r.returncode, 1)
        self.assertIn("request failed", r.stderr)


if __name__ == "__main__":
    unittest.main()

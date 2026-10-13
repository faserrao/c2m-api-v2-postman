#!/usr/bin/env python3
"""
Golden tests for scripts/active/postman_api_request.sh — the helper the Makefile cleanup
targets use for every Postman API call — and for how the Makefile hands the spec to the
Postman API. Before 2026-10-13 those targets called
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


FLAKY_SEEN = set()


class _Handler(http.server.BaseHTTPRequestHandler):
    def _reply(self):
        if self.path.startswith("/flaky-") and self.path not in FLAKY_SEEN:
            FLAKY_SEEN.add(self.path)          # first request: drop the connection, no response
            self.close_connection = True
            self.connection.shutdown(socket.SHUT_RDWR)
            return
        if self.path.startswith("/flaky-"):
            self.path = "/ok"
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

    def test_transient_transport_failure_is_retried(self):
        """2026-10-13: a cleanup DELETE failed with curl exit 16 (HTTP/2 framing error),
        a momentary network error, and stopped the whole build."""
        r = self.run_helper("DELETE", f"{self.base}/flaky-delete")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_connection_failure_fails(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        r = self.run_helper("GET", f"http://127.0.0.1:{port}/ok")
        self.assertEqual(r.returncode, 1)
        self.assertIn("request failed", r.stderr)


class TestMakefileSpecPayloads(unittest.TestCase):
    """Linux caps one command-line argument at 128 KB (MAX_ARG_STRLEN). The spec passed
    that on 2026-10-13 and `jq --arg content "$$(cat spec)"` failed in CI with
    'Argument list too long' (macOS has no such cap, so local builds passed).
    Spec content must reach jq/curl from the file (--rawfile, --data @file, a pipe)."""

    def test_no_recipe_passes_a_spec_file_as_one_argument(self):
        offenders = []
        for n, line in enumerate((REPO_ROOT / "Makefile").read_text().splitlines(), 1):
            code = line.split("#", 1)[0] if line.lstrip().startswith("#") else line
            if "$$(cat" in code and "SPEC" in code and "CONTENT=" in code:
                offenders.append(f"{n}: {line.strip()}")
            if '--arg content "$$' in code or ('--data "$$(jq' in code):
                offenders.append(f"{n}: {line.strip()}")
        self.assertEqual(offenders, [])


class TestMakefileSecurityRepoPath(unittest.TestCase):
    """Local builds take the JWT auth script from the security repo cloned beside this one.
    Until 2026-10-13 the Makefile looked for ../c2m-api-v2-security (the folder name CI
    checks it out into), not the repo's own name, so a plain clone was never found and
    local builds silently used the older fallback script."""

    def test_local_path_is_the_security_repo_name_ci_checks_out(self):
        import re
        makefile = (REPO_ROOT / "Makefile").read_text()
        workflow = (REPO_ROOT / ".github" / "workflows" / "api-ci-cd.yml").read_text()
        repo = re.search(r"repository: \$\{\{ github\.repository_owner \}\}/(\S*security\S*)", workflow).group(1)
        local = re.search(r"^else\nSECURITY_POSTMAN_SCRIPTS_DIR\s*:=\s*(\S+)", makefile, re.M).group(1)
        self.assertEqual(local, f"../{repo}/postman/scripts")


class TestCredentialFilesAreIgnored(unittest.TestCase):
    """postman-env-create writes real clientId/clientSecret into the environment files.
    Until 2026-10-13 postman/environments/c2m-aws-dev.postman_environment.json was
    tracked, so a local build followed by `git add -A` would commit the credentials."""

    def test_every_generated_environment_file_is_ignored_and_untracked(self):
        import re
        makefile = (REPO_ROOT / "Makefile").read_text()
        variables = dict(re.findall(r"^([A-Z_]+)\s*:=\s*(\S+)", makefile, re.M))

        def expand(value):
            for _ in range(5):
                value = re.sub(r"\$\((\w+)\)", lambda m: variables.get(m.group(1), m.group(0)), value)
            return value
        outputs = [expand(p) for p in re.findall(r'generate_postman_env\.sh\s+""\s+(\S+)', makefile)]
        self.assertGreaterEqual(len(outputs), 2)
        for path in outputs:
            ignored = subprocess.run(["git", "check-ignore", "-q", path], cwd=REPO_ROOT).returncode == 0
            tracked = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=REPO_ROOT,
                                     capture_output=True).returncode == 0
            self.assertTrue(ignored, f"{path} is not git-ignored")
            self.assertFalse(tracked, f"{path} is tracked by git")


class TestMakefileWorkspace(unittest.TestCase):
    """The Postman workspace ID must never be empty: with ?workspace= empty the Postman API
    lists every workspace the key can see, so postman-cleanup-all would delete all of it.
    On 2026-10-13 a .env made as the Getting Started guide says (cp .env.example .env)
    produced exactly that: the Makefile exported every word of .env, comments included, and
    "# C2M_WS=..." became an empty C2M_WS that blocked the default."""

    def make(self, *args, env_text=None, extra=""):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for name in ("Makefile", ".git-context"):
                (Path(d) / name).write_text((REPO_ROOT / name).read_text())
            if env_text is not None:
                (Path(d) / ".env").write_text(env_text)
            (Path(d) / "probe.mk").write_text(extra or "probe: ; @echo WS=[$(POSTMAN_WS)]\n")
            return subprocess.run(["make", "--no-print-directory", "-f", "Makefile", "-f", "probe.mk", *args],
                                  cwd=d, capture_output=True, text=True, timeout=60,
                                  env={k: v for k, v in __import__("os").environ.items()
                                       if not k.startswith(("POSTMAN_", "C2M_", "SERRAO_"))})

    def default_ws(self):
        import re
        return re.search(r"^C2M_WS\s*\?=\s*(\S+)", (REPO_ROOT / "Makefile").read_text(), re.M).group(1)

    def test_env_copied_from_example_keeps_the_default_workspace(self):
        r = self.make("probe", env_text=(REPO_ROOT / ".env.example").read_text())
        self.assertIn(f"WS=[{self.default_ws()}]", r.stdout, r.stderr)

    def test_cleanup_stops_before_any_call_when_workspace_is_empty(self):
        for target in ("postman-delete-collections", "postman-delete-mock-servers",
                       "postman-delete-environments", "postman-collections-clean", "postman-workspace-debug"):
            r = self.make(target, "C2M_WS=", env_text="")
            self.assertNotEqual(r.returncode, 0, target)
            self.assertIn("POSTMAN_WS (Postman workspace ID) is empty", r.stderr, target)
            self.assertNotIn("Deleting", r.stdout, target)

    def test_targets_without_postman_calls_still_run_when_workspace_is_empty(self):
        r = self.make("empty-test", "C2M_WS=", env_text="")
        self.assertEqual(r.returncode, 0, r.stderr)


class TestDependencies(unittest.TestCase):
    """Found by the Getting Started test on 2026-10-13: requirements.txt pinned 91 packages
    (a whole TensorFlow environment) of which the pipeline imports 8, and two of the unused
    ones (h5py, pydantic_core) cannot be installed on Python 3.14, so a new developer's first
    build failed. And `make install` ran `npm install <names>`, which upgraded every tool and
    rewrote package.json / package-lock.json in a fresh clone."""

    # import name -> distribution name, where they differ
    DIST = {"yaml": "pyyaml", "dotenv": "python-dotenv", "faker": "faker"}
    DIRS = ("scripts/active", "scripts/validation", "scripts/utilities",
            "scripts/test_data_generator_for_collections", "tests")

    def test_requirements_are_exactly_the_imported_packages(self):
        import re
        import sys
        local = {p.stem for d in self.DIRS for p in (REPO_ROOT / d).rglob("*.py")} | {"utilities"}
        imported = set()
        for d in self.DIRS:
            for p in (REPO_ROOT / d).rglob("*.py"):
                if "archive" in p.parts:
                    continue
                for m in re.finditer(r"^\s*(?:import|from)\s+([A-Za-z_]\w*)", p.read_text(errors="ignore"), re.M):
                    name = m.group(1)
                    if name not in sys.stdlib_module_names and name not in local:
                        imported.add(self.DIST.get(name, name).lower())
        imported.add("pytest")  # the golden tests run under pytest
        lines = (REPO_ROOT / "scripts" / "python_env" / "requirements.txt").read_text().splitlines()
        pinned = {l.split("==")[0].strip().lower() for l in lines if l.strip() and not l.startswith("#")}
        self.assertTrue(all("==" in l for l in lines if l.strip() and not l.startswith("#")), "unpinned requirement")
        # code-sample strings in add-sdk-samples-to-spec.py look like imports (Java/Kotlin)
        imported -= {"com", "okhttp3", "the"}
        self.assertEqual(sorted(pinned - imported), [], "pinned but never imported")
        self.assertEqual(sorted(imported - pinned), [], "imported but not pinned")

    def test_venv_is_ignored_by_the_repo_gitignore(self):
        """CI's Getting Started smoke test (2026-10-13): the rule was */e2o.venv/, one level
        deep, so scripts/python_env/e2o.venv/ showed as untracked under Python 3.11/3.12.
        (3.13+ writes its own .gitignore inside every venv, which hid it locally.)"""
        r = subprocess.run(["git", "-c", "core.excludesfile=/dev/null", "check-ignore", "--no-index", "-v",
                            "scripts/python_env/e2o.venv/bin/python"], cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, "venv not ignored")
        self.assertTrue(r.stdout.startswith(".gitignore:"), r.stdout)   # the repo's root file, not the venv's own

    def test_make_install_uses_the_lockfile(self):
        import re
        recipe = re.search(r"^install:\n((?:\t.*\n)+)", (REPO_ROOT / "Makefile").read_text(), re.M).group(1)
        body = "\n".join(l for l in recipe.splitlines() if not l.strip().startswith("#"))
        self.assertIn("npm ci", body)
        self.assertNotRegex(body, r"npm install\b")


class TestLocalMakeBehaviour(unittest.TestCase):
    """Found by the Getting Started test on 2026-10-13 (fresh clone, GNU Make 4 as the
    guide now requires): prism-start stopped silently under -eu when nothing listened on
    the port; postman-instance-build-with-tests never finished (it ended by serving docs in
    the foreground, so validate-pipeline never ran and Prism kept running); every make
    command in a fresh clone printed 'cat: ... No such file' and '❌ Mock server URL not
    found'; and Make 3.81 (macOS) ignored .ONESHELL/.SHELLFLAGS without a word."""

    MAKEFILE = (REPO_ROOT / "Makefile").read_text()

    def target(self, name):
        import re
        return re.search(rf"^{re.escape(name)}:.*\n((?:\t.*\n|#.*\n)+)", self.MAKEFILE, re.M).group(1)

    def run_make(self, make, *args):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for name in ("Makefile", ".git-context"):
                (Path(d) / name).write_text((REPO_ROOT / name).read_text())
            return subprocess.run([make, "--no-print-directory", *args], cwd=d, capture_output=True,
                                  text=True, timeout=60)

    def test_fresh_clone_make_prints_no_errors(self):
        r = self.run_make("make", "empty-test")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("No such file", r.stderr)
        self.assertNotIn("Mock server URL not found", r.stderr)

    def test_make_3_81_is_refused(self):
        old = "/usr/bin/make"
        if not Path(old).exists() or "3.81" not in subprocess.run([old, "--version"], capture_output=True, text=True).stdout:
            self.skipTest("Make 3.81 not available here")
        r = self.run_make(old, "empty-test")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("GNU Make 3.82 or later is required", r.stderr)

    def test_build_with_tests_finishes_and_stops_prism(self):
        body = self.target("postman-instance-build-with-tests")
        self.assertNotIn("postman-docs-build-and-serve-up", body)   # served docs in the foreground
        self.assertIn("docs-serve-bg", body)
        self.assertLess(body.index("postman-mock"), body.index("prism-stop"))
        self.assertLess(body.index("docs-serve-bg"), body.index("validate-pipeline"))

    def test_prism_start_tolerates_a_free_port(self):
        self.assertIn("lsof -ti :$(PRISM_PORT) || true", self.target("prism-start"))


if __name__ == "__main__":
    unittest.main()

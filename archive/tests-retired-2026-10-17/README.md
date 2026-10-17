# tests/ retired 2026-10-17

The repo-root `tests/` directory was dissolved in the scripts cleanup:

- `validate-secrets.sh`, `validate-pipeline-outputs.sh` — the only files any build used — moved to
  `scripts/validate/post-build/` (called by `ci_verify.sh`, `generate_report.py`, and the
  `validate-secrets` / `validate-pipeline` targets). The golden suites live in `scripts/validate/tests/`.
- Everything here was used by nothing: `jwt-auth-tests.js` (only caller was the retired `jwt-test`
  target), `pipeline-test-suite.sh`, `smoke-test.sh`, `test-github-actions.sh`, `python-cli/`,
  `typescript-cli/`, and the old `README.md`. `click`, `python-dotenv` and `requests` were dropped
  from `scripts/python_env/requirements.txt` with them (nothing else imports them).

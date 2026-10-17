# Scripts

| Directory | What it holds | CI trigger |
|---|---|---|
| `build-spec/` | DD → OpenAPI: `ebnf_to_openapi_dynamic_v3.py` (translator), `merge_openapi_overlays.py`, `add-sdk-samples-to-spec.py` | yes |
| `build-collections/` | OpenAPI → Postman: post-processors, `addRandomDataToRaw.js` (Test collection data), the Real-World and Getting Started generators, `jq/` filters | yes |
| `lib/` | Python helpers shared by generators and validators (`oneof_resolver.py`) | yes |
| `build-docs-sdk/` | DD tables, artifacts index, docs banner fix, SDK generation | yes |
| `publish-postman/` | Postman API calls and environment files | yes |
| `validate/` | validators and gates; `tests/` (golden suites), `migrations/` (change declarations + baselines), `post-build/` (CI checks after publishing: `ci_verify.sh`, Newman, report) | yes |
| `dev-tools/` | local developer helpers (context switch, push helpers, Prism probe, EBNF preview, one-off extractors); not used by the build | no |
| `python_env/` | `requirements.txt` (pinned) and the `e2o.venv` virtual environment | `requirements.txt` only |

The Makefile refers to these only through `SPEC_SCRIPTS_DIR`, `COLLECTION_SCRIPTS_DIR`, `DOCS_SDK_SCRIPTS_DIR`,
`PUBLISH_SCRIPTS_DIR`, `VALIDATE_SCRIPTS_DIR` and `DEV_TOOLS_DIR`. Retired scripts are in
`archive/scripts/retired-2026-10-17/`.

Full reference: [c2m-api-v2-manuals: development/SCRIPTS_REFERENCE.md](https://github.com/click2mail/c2m-api-v2-manuals/blob/master/development/SCRIPTS_REFERENCE.md)
and `development/DD_OpenAPI_Postman_System_Manual.md`.

# Scripts Directory

Build automation, validation tooling, and utility scripts for the C2M API v2 project.

## Directory Structure

```
scripts/
├── active/          # Scripts called directly by Makefile / CI pipeline
├── utilities/       # Manual operations, one-off tools, diagnostic helpers
├── validation/      # Collection and config validators, golden test suite
├── test_data_generator_for_collections/  # Test data injection for Postman collections
├── python_env/      # Python virtual environment (e2o.venv — git-ignored)
├── jq/              # JQ scripts for JSON processing
└── archive/         # Archived / superseded scripts (kept for reference)
    └── scripts/most-recent/
```

---

## `scripts/active/` — Pipeline scripts

Called by Makefile targets or CI. Do not run manually unless you understand the full pipeline.

| Script | Purpose | Called by |
|---|---|---|
| `ebnf_to_openapi_dynamic_v3.py` | EBNF → OpenAPI spec; also emits `config/faker_hints.yaml` and `config/c2m_provider_mappings.yaml` as derived artifacts | `make openapi-build` |
| `add_response_examples.py` | Injects success + error examples into the OpenAPI spec | `make openapi-build` |
| `fix_oneOf_placeholders.js` | Resolves `<oneOf>` placeholders in generated Postman collections; discovers job array fields from spec | `make postman-linked-collection-fix-oneof` |
| `add_auth_examples.js` | Injects auth request bodies from the OpenAPI auth overlay | `make postman-linked-collection-add-auth-examples` |
| `add_error_responses_to_collection.js` | Injects error response examples into Postman collections | `make postman-linked-collection-add-error-responses` |
| `add_tests_jwt.js` | Adds JWT/auth pre-request and test scripts; fields read from auth overlay | `make add-tests-to-test-collection` |
| `add_tests.js` | Adds test scripts to job endpoints in Postman collections | `make add-tests-to-test-collection` |
| `add_pre_request_script.js` | Injects pre-request auth script into collections | various Makefile targets |
| `generate_curated_collections_v4.py` | Generates Real-World use-cases collection from `config/curated-examples-catalog.yaml` | `make postman-generate-real-world-collection` |
| `generate_artifacts_index.py` | Generates `reports/artifacts-index.md` table linking all CI artifacts | `make generate-artifacts-index` |
| `generate_dd_table.py` | Generates Data Dictionary CSV from EBNF; derives `_ENDPOINT_MAP` from the OpenAPI spec at runtime | `make generate-data-dictionary-table` |
| `fix_collection_urls_v2.py` | Replaces hardcoded URLs with `{{baseUrl}}` placeholders | `make postman-fix-urls` |
| `inject_documentation_link.js` | Injects GitHub Pages / Postman-native documentation links into collection descriptions | `make inject-documentation-link` |
| `merge_openapi_overlays.py` | Merges OpenAPI overlay files (auth overlay, etc.) into base spec | `make openapi-build` |
| `fix_openapi_oneOf_schemas.py` | Post-processes oneOf schemas in the generated spec | `make openapi-build` |
| `validate_collection.js` | Validates Postman collection structure (Postman schema) | `make postman-test-collection-validate` |
| `fix-template-banner.sh` | Fixes the Redoc template banner in generated docs | `make docs-build` |
| `fetch_aws_credentials.sh` | Fetches temporary AWS credentials for upload steps | CI |
| `generate_postman_env.sh` | Generates Postman environment JSON from config | `make postman-env-generate` |

---

## `scripts/utilities/` — Manual / diagnostic scripts

Not called by the CI pipeline. Run manually for one-off operations or investigation.

| Script | Purpose |
|---|---|
| `generate_getting_started_collections.py` | Generates Getting Started collections from `config/getting-started-template.yaml` + `config/curated-examples-catalog.yaml`; reads `config/faker_hints.yaml` for realistic values |
| `oneof_resolver.py` | Shared oneOf variant resolver — no hardcoded schema maps; used by the Getting Started generator |
| `generate-sdk-v2.sh` | Generates client SDKs in 11 languages using OpenAPI Generator |
| `add-sdk-samples-to-spec.py` | Adds cURL/Python/JavaScript code samples to the OpenAPI spec |
| `git-push.sh` | Context-aware push helper (routes to click2mail or origin based on `git ctx-push`) |
| `set-context.sh` | Sets git push context (corporate/personal) |
| `git-pull-rebase.sh` | Pull with rebase + autostash |
| `deploy-docs.sh` | Deploys documentation to GitHub Pages or local preview |
| `prism_test.sh` | Tests endpoints against a running Prism mock server |
| `fix_document_source_identifier.py` | One-off migration helper for document source field renames |
| `test_oneof_formats.sh` | Diagnostic: tests primitive vs tagged-union oneOf acceptance by Prism (investigation tool, not CI) |
| `verify_mocks.py` | Diagnostic: verifies mock server responses against the spec. NOTE: does not work against this all-POST API — Prism returns 422 on empty bodies before schema validation runs. Kept as reference only. |
| `extract_yaml_from_postman.py` | Extracts YAML structures from Postman collection exports |
| `debug_v10_api.py` | Diagnostic for Postman API v10 response shapes |

---

## `scripts/validation/` — Validators and test suite

See [`scripts/validation/README.md`](validation/README.md) for full documentation.

| Script | Purpose | Run via |
|---|---|---|
| `validate_configs_against_dd.py` | **V1–V8 config validators** — checks all config files against the DD and spec | `make validate-configs` |
| `validate_collections_against_spec.py` | Spec-driven collection conformance validator (V3/V4 aware) | `make validate-collections-conformance` |
| `validate_all_collections_against_spec.py` | Batch runner for all 4 canonical collections | `make validate-collections-conformance-gate-all` |
| `validate_catalog_against_spec.py` | Validates `curated-examples-catalog.yaml` `select:` entries against spec oneOf | `make validate-catalog-against-spec` |
| `diff_collections.py` | Structural before/after collection diff; `--require-coverage` guards endpoint count | manual |
| `generate_report.py` | Generates markdown conformance report | manual |
| `ci_verify.sh` | CI orchestration script — calls `run_newman.sh` | CI |
| `run_newman.sh` | Standardized Newman test runner with timestamped HTML/JSON reports | CI via `ci_verify.sh` |
| `tests/` | Golden test suite — `test_dd_constraints.py` (28 tests) + `test_validate_collections.py` | `make validate-collections-conformance-test` |

---

## `scripts/test_data_generator_for_collections/` — Test data injection

See [`README-addRandomDataToRaw.md`](test_data_generator_for_collections/README-addRandomDataToRaw.md).

| Script | Purpose |
|---|---|
| `addRandomDataToRaw.js` | Replaces `<String>`/`<Integer>`/`<Boolean>` placeholders in Postman collection request bodies with randomised Faker.js data; also resolves `ph<val1\|val2\|...>` enum placeholders using `faker_hints.yaml` |

---

## Python Environment

Scripts use a Python virtual environment at `scripts/python_env/e2o.venv/`.

```bash
source scripts/python_env/e2o.venv/bin/activate
# or use the $VENV alias:
VENV=scripts/python_env/e2o.venv/bin/python
$VENV scripts/validation/validate_configs_against_dd.py
```

Dependencies: `scripts/python_env/requirements.txt`

---

## Archived Scripts

Scripts moved to `scripts/archive/scripts/most-recent/` are kept for reference but are no longer called by any pipeline step:

| Script | Superseded by |
|---|---|
| `add_auth_to_test_collection.js` | `add_pre_request_script.js` |
| `generate-sdk.sh` | `generate-sdk-v2.sh` |
| `generate_test_data.py` | `addRandomDataToRaw.js` + `faker_hints.yaml` |
| `verify_urls.py` | `fix_collection_urls_v2.py` |

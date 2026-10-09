# C2M API v2 — Postman Pipeline

Primary repository for the Click2Mail API v2 Postman collection pipeline.

See top-level `CLAUDE.md` (`C2M_API_v2/CLAUDE.md`) for full project context and session history.

---

# Key Pipeline Components

| Script | Purpose |
|---|---|
| `scripts/active/ebnf_to_openapi_dynamic_v3.py` | EBNF DD → OpenAPI spec translator; writes every success/error example from the DD (`@error_examples`, `standardResponse` `@hint`s) |
| `scripts/active/fix_oneOf_placeholders.js` | Resolves oneOf placeholders; normalises jobOptions enums |
| `scripts/test_data_generator_for_collections/addRandomDataToRaw.js` | Resolves `<Type>` placeholders for test collection |
| `scripts/active/add_error_responses_to_collection.js` | Copies each operation's spec examples (success + errors; auth via the overlay) into the saved responses of the Test, Linked and Real-World collections |
| `scripts/active/add_auth_examples.js` | Injects auth request examples |
| `scripts/active/add_tests_jwt.js` | Adds JWT test scripts to test collection |
| `scripts/validation/validate_configs_against_dd.py` | V1–V8 build-time config validators |
| `scripts/validation/validate_collections_against_spec.py` | Spec-driven conformance gate (K-V3…K-V6) |
| `scripts/validation/validate_pipeline_consistency.py` | End-to-end DD → spec → Postman consistency gate (saved examples, error map, spec examples); `KNOWN_OPEN` table lists tracked open findings |

---

# Important Patterns

- **Constants over inline strings**: every reused string literal (schema names, content types, field names, enum fallbacks) lives behind a module-level constant.
- **`@doc` annotations**: rule descriptions live in `data_dictionary/c2mapiv2-dd.ebnf` as `(* @doc Description. *)` preceding-line annotations, read at parse time by `generate_dd_table.py`.
- **`ph<>` format is defensive only**: `fix_oneOf_placeholders.js` now writes the first canonical enum value (`propDef.enum[0]`) directly for `jobOptions` fields. The `ph<val1|val2|...>` handler in `addRandomDataToRaw.js` is a fallback for manually-constructed collections only.
- **Repeatable spec builds (M4)**: spec examples use `_EXAMPLE_NOW` and sha256-seeded IDs — two builds from the same DD are byte-identical. Never reintroduce `random`/`datetime.now()` into spec examples (`test_spec_generation_is_repeatable` fails).
- **No silent no-ops**: pipeline scripts exit 1 when they process nothing; Makefile no longer masks guarded steps with `|| echo "Skipping"`.
- **Error map is the authority**: job-endpoint responses and Postman error examples are built from the DD `@http_error_map` per `(status, errorCode)` pair.
- **Derived artifacts**: `config/faker_hints.yaml`, `config/c2m_provider_mappings.yaml`, `openapi/c2mapiv2-openapi-spec-*.yaml` — all generated. Do not edit directly.

---

# Recent Changes

## 2026-10-02 → 2026-10-07 — DD→Spec→Postman audits, H1–H5 / M4 / X3 / N1 / N2 / N5 fixes, consistency gate

**Commits:** `61bef3a`, `ecbdc95`, `5969464`, `d4f05d9`, `64cec53`, `4ee6f50` (all CI-green on click2mail + origin). Full detail: `c2m-api-v2-manuals/audit-reports/PIPELINE_CHANGES_2026-10-05.md`; findings and open decisions: `DD_SPEC_POSTMAN_CONSISTENCY_AUDIT_2026-10-05.md` and `..._REAUDIT_2026-10-05.md`.

| ID | Change |
|---|---|
| H1 | `@numeric_constraints` applied to inline request properties (`_get_field_type()`); orphan constraints rejected; `quantity` removed from DD |
| H2 | `fix_oneOf_placeholders.js` enforces spec `x-mutual-exclusion` (Linked sent jobTemplate+jobOptions on 6/9); K-V6 in conformance gate |
| H3 | DD 400 error map += `INVALID_FORMAT` (decision: allow 400 and 422); V6 checks status placement |
| H4 | `_generate_responses()` derives job responses from the DD map — 429 on all 7 job endpoints |
| H5 | 403 examples use auth-system scopes `jobs:submit` / `templates:read`; unused `postman/custom/auth-*.json` deleted |
| M4 | Deterministic spec examples (`_EXAMPLE_NOW`, seeded IDs) |
| X3 | `add_response_examples.py` `/jobs/` filter (dead since rename) → `_job_operations()`; 200 examples restored |
| guards | 6 scripts fail on zero work; 17 Makefile masks removed |
| gate | `validate_pipeline_consistency.py` + `validate-dd-gates`; both in CI; fixture build ends with `postman-test-collection-add-auth-examples` (matches publish) |
| N1/N2 | `add_error_responses_to_collection.js`: tokens resolved before building; examples keyed by (status, code) from the DD map — 18 pairs per job request |
| N5 | Translator error examples name real body paths via `_find_body_path()` (`zip`, `jobOptions.documentClass`); `postalCode` removed |

**Correction:** earlier finding M1 ("PRs not validated") was wrong — `api-ci-cd.yml` already runs every gate on `pull_request`.

## 2026-09-21 (Session 2) — Hardcoded-Values Audit Passes 3–6 + Comprehensive System Audit

**Commits:** `8655c1e`, `73e6468`, `d98b114`, `d62b48f`

Four additional iterative audit passes fixing 14 items across 9 files (all LOW/MEDIUM). Completed with a 187-check comprehensive end-to-end system audit confirming 0 failures across all 7 layers.

| Pass | Commit | Items Fixed |
|---|---|---|
| Pass 3 | `8655c1e` | M-2 BUG (`recipientAddressSource.zip` in addRandomDataToRaw.js), M-1 (`_load_sdk_langs()` for add-sdk-samples-to-spec.py), L-1/L-2/L-3 (constants + cross-ref comments) |
| Pass 4 | `73e6468` | J1 (bearerAuth cross-ref), J2 (`_FALLBACK_SERVER_URL`), J3 (`CONTENT_TYPE_JSON` in validator), J5/J12 (`_DEFAULT_API_TITLE`/`_DEFAULT_ARTIFACTS_REPO` in artifacts index); J4 confirmed already wired |
| Pass 5 | `d98b114` | K1 (CONTENT_TYPE_JSON usage in add_auth_examples.js), K3 (mappingId fallback 1→5001), K4 (`_SPLIT_JOB_ARRAY_FIELDS_FALLBACK`), K5 (diff_collections.py path-prefix default→"/"), K6/K7 (cross-ref comments + shell variable) |
| Pass 6 | `d62b48f` | G1 (`CONTENT_TYPE_JSON` constant in add_tests_jwt.js), G2/G3 (cross-ref comments in add_response_examples.py + addRandomDataToRaw.js) |

**Comprehensive system audit:** 181/187 checks pass; 6 warnings all documented intentional design decisions.

**Open recommendations (none blocking):**
1. ~~Extend V8 to validate inline discriminator keys in template `values:` blocks against spec~~ **Done 2026-09-23** — V8 now covers both template (7 usages) and catalog (2 usages)
2. Add `@hint` annotations for `addressId`/`addressName` in EBNF DD
3. Add comment to real-world catalog for intentional 2-item `multiZipJobs`

---

## 2026-09-21 — Deep Hardcoded-Values Audit (Two Passes) + Collection-vs-DD Structural Fix

**Commits:** `774e925`, `0413e3f`

### Pass 1 fixes (commit `774e925`)

| ID | Change |
|---|---|
| A1 BUG | `"INTERNAL_SERVER_ERROR"` → `"SERVER_ERROR"` in `addRandomDataToRaw.js:332` |
| D1 | `_RESPONSE_SCHEMA_NAME = "standardResponse"`, `_ERROR_SCHEMA_NAME = "errorResponse"` constants; 7 inline `$ref` strings in `_generate_paths()` replaced |
| F1 | `_ERROR_POSTAL_FIELD = "postalCode"` constant; used in INVALID_FORMAT error-detail f-string |
| F2 | INVALID_ENUM_VALUE fallback `'documentType'` → `'documentClass'` |
| I5 | `fix-template-banner.sh` reads `${DOCS_PORT:-8080}` from environment |
| A2 | Comment: `errorType` fixture values must stay in sync with spec enum |
| C2 | Comment: `_fallback401/403` are OAuth2 RFC 6749/6750 codes, not DD `errorCode` enum |

### Pass 2 fixes (commit `0413e3f`)

| ID | Change |
|---|---|
| A-new-1 | `_ERROR_DOCUMENT_CLASS_FALLBACK = ["letter", "postcard", "brochure", "flat"]` constant |
| B-new-1 | `error-response-examples.yaml` 400/invalid_oneof: `"document"` → `"docSourceAll"` |
| B-new-2 | `error-response-examples.yaml` 422/validation_failed: `"recipientAddress.zip"` → `"recipientAddressSource.zip"` |
| **Collection FAIL** | Linked collection had unresolved `ph<>` in all 6 `jobOptions` blocks. Fixed in `fix_oneOf_placeholders.js` by writing `propDef.enum[0]` directly instead of `ph<>` format. Verified: 0 `ph<>` remaining in linked collection. |

**Verification:** 31/31 golden tests, V1–V8 clean, all 5 conformance gates FAIL=0.

## 2026-09-20 — P1–P6 Fixes + M3 @doc Annotation Migration

**Commits:** `b618031` (P1–P6), `bdda799` (M3)

- **P1 BUG**: `_ERROR_EXTERNAL_SERVICE` corrected `"payment-gateway"` → `"address-validation"`
- **P2**: HC3 in `fix_oneOf_placeholders.js` extended to discover `$ref`-alias array schemas
- **P3**: endpoint-expanded table functions accept explicit `endpoint_map` param
- **P4**: `CONTENT_TYPE_JSON` constant added to `add_auth_examples.js`
- **P5**: Makefile mock names use `$(POSTMAN_MOCK_NAME)` / `$(POSTMAN_LINKED_MOCK_NAME)`
- **P6**: docblock added to `error-response-examples.yaml` for intentionally hardcoded values
- **M3**: 102 `(* @doc Description. *)` annotations added to EBNF DD; `_DESC` shrunk from 73 to 16 entries; `generate_dd_table.py` reads `@doc` annotations at parse time via `_extract_doc_annotations()` pre-pass

---

# Validation Quick Reference

```bash
make openapi-build && make postman-build-golden-test-fixtures   # build spec + all 5 collections (no API keys)
make validate-configs                           # V1–V8 config validators
make validate-collections-conformance-test      # Golden tests: validator script + resolver 20 + DD constraints 37 + consistency 24
make validate-collections-conformance-gate-all  # All 5 collections conform to spec
make validate-dd-gates                          # spec vs DD, all 5 collections vs DD, catalog vs spec
make validate-pipeline-consistency              # end-to-end DD → spec → Postman gate
```

Expected outputs (all clean):
- `✅ All config field names are valid DD rule names`
- `20 passed` / `37 passed, 43 subtests passed` / `24 passed`
- `PASS=9 FAIL=0 SKIP=1` (linked/test), `PASS=17 FAIL=0` (GS), `PASS=8 FAIL=0` (real-world)
- `✅ TOTAL — PASS=191 FAIL=0` (spec vs DD); `0 finding(s) across 5 collection(s)`
- `ERROR categories: 0 · known-open WARN categories: 30`

---

# Known Gaps

Config field names: none — V1–V8 cover them.

Open DD → spec → Postman findings are tracked in the `KNOWN_OPEN` table of `scripts/validation/validate_pipeline_consistency.py` (each entry cites its audit/decision ID; the gate flags entries that stop occurring). Main open items: X1/X2 (Linked/Real-World saved responses synthesised by the converter), X4 (`@doc` not emitted to spec), C1 (no request examples), N3/D9 (Getting Started collections have no saved responses), N4/N5/D10 (spec vs YAML error-example content), decisions D1–D8 (see the 2026-10-05 audit reports).

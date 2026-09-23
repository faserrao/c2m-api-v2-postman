# C2M API v2 — Postman Pipeline

Primary repository for the Click2Mail API v2 Postman collection pipeline.

See top-level `CLAUDE.md` (`C2M_API_v2/CLAUDE.md`) for full project context and session history.

---

# Key Pipeline Components

| Script | Purpose |
|---|---|
| `scripts/active/ebnf_to_openapi_dynamic_v3.py` | EBNF DD → OpenAPI spec translator |
| `scripts/active/fix_oneOf_placeholders.js` | Resolves oneOf placeholders; normalises jobOptions enums |
| `scripts/test_data_generator_for_collections/addRandomDataToRaw.js` | Resolves `<Type>` placeholders for test collection |
| `scripts/active/add_response_examples.py` | Injects success/error response examples into spec |
| `scripts/active/add_error_responses_to_collection.js` | Injects error response examples into Postman collection |
| `scripts/active/add_auth_examples.js` | Injects auth request examples |
| `scripts/active/add_tests_jwt.js` | Adds JWT test scripts to test collection |
| `scripts/validation/validate_configs_against_dd.py` | V1–V8 build-time config validators |
| `scripts/validation/validate_collections_against_spec.py` | Spec-driven conformance gate |

---

# Important Patterns

- **Constants over inline strings**: every reused string literal (schema names, content types, field names, enum fallbacks) lives behind a module-level constant.
- **`@doc` annotations**: rule descriptions live in `data_dictionary/c2mapiv2-dd.ebnf` as `(* @doc Description. *)` preceding-line annotations, read at parse time by `generate_dd_table.py`.
- **`ph<>` format is defensive only**: `fix_oneOf_placeholders.js` now writes the first canonical enum value (`propDef.enum[0]`) directly for `jobOptions` fields. The `ph<val1|val2|...>` handler in `addRandomDataToRaw.js` is a fallback for manually-constructed collections only.
- **Derived artifacts**: `config/faker_hints.yaml`, `config/c2m_provider_mappings.yaml`, `openapi/c2mapiv2-openapi-spec-*.yaml` — all generated. Do not edit directly.

---

# Recent Changes

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
make validate-configs                        # V1–V8 config validators
make validate-collections-conformance-test  # Golden tests (31/31)
make validate-collections-conformance-gate-all  # All 5 conformance gates
```

Expected outputs (all clean):
- `✅ All config field names are valid DD rule names`
- `31 passed, 43 subtests passed`
- `PASS=9 FAIL=0 SKIP=1` (linked/test), `PASS=17 FAIL=0` (GS), `PASS=8 FAIL=0` (real-world)

---

# Known Gaps

None. All hardcoded DD-derived values are validated at `make validate-configs` time by V1–V8. V8 (`validate_template_inline_discriminators`) covers inline branch discriminator keys in template `values:` blocks (e.g. `mergeByRequestId:`, `docSourceZipFileRef:`). The conformance gate (`make validate-collections-conformance-gate-all`) provides a second backstop.

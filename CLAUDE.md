# C2M API v2 — Postman Pipeline

Primary repository for the Click2Mail API v2 Postman collection pipeline.

See top-level `CLAUDE.md` (`C2M_API_v2/CLAUDE.md`) for full project context and session history.

---

# Key Pipeline Components

| Script | Purpose |
|---|---|
| `scripts/active/ebnf_to_openapi_dynamic_v3.py` | EBNF DD → OpenAPI spec translator; writes every success/error example from the DD (`@error_examples`, `standardResponse` `@hint`s) and each job endpoint's request example (schema + `@hint`s, C1) |
| `scripts/active/postman_api_request.sh` | One Postman API call that exits 1 on a non-2xx status (404 on DELETE accepted); used by every cleanup list/delete call |
| `scripts/active/fix_oneOf_placeholders.js` | Resolves oneOf placeholders; normalises jobOptions enums |
| `scripts/test_data_generator_for_collections/addRandomDataToRaw.js` | Resolves `<Type>` placeholders for test collection |
| `scripts/active/add_error_responses_to_collection.js` | Copies each operation's spec examples (success + errors; auth via the overlay) into the saved responses of all five collections (Getting Started since D9) |
| `scripts/active/add_auth_examples.js` | Injects auth request examples from the overlay; sets saved responses' `originalRequest` to the request and URL path variables from overlay parameter examples (L6) |
| `scripts/active/declared_statuses.js` | Each spec operation's declared statuses; `add_tests.js` (build) and `add_tests_jwt.js` (manual) assert exactly those per request (D7) |
| `scripts/active/add_tests_jwt.js` | Adds JWT test scripts to the test collection (`make postman-add-jwt-tests`; not part of the build) |
| `scripts/validation/validate_configs_against_dd.py` | V1–V8 build-time config validators |
| `scripts/validation/validate_collections_against_spec.py` | Spec-driven conformance gate (K-V3…K-V6) |
| `scripts/validation/validate_pipeline_consistency.py` | End-to-end DD → spec → Postman consistency gate (saved examples, error map, spec examples, `@doc` descriptions); `KNOWN_OPEN` table lists tracked open findings (empty since L6, 2026-10-16) |
| `scripts/validation/validate_migration.py` | Migration check: `snapshot` the whole system, then `compare` a rebuild under a declared migration (`scripts/validation/migrations/*.yaml`) — UNEXPECTED / INCOMPLETE / LOST; `retired` scans for removed names. Make: `migration-snapshot`, `validate-migration`, `validate-migration-retired` (`MIGRATION=<name>`) |

---

# Important Patterns

- **Constants over inline strings**: every reused string literal (schema names, content types, field names, enum fallbacks) lives behind a module-level constant.
- **`@doc` annotations**: rule descriptions live in `data_dictionary/c2mapiv2-dd.ebnf` as `(* @doc Description. *)` preceding-line annotations. They feed the DD table (`generate_dd_table.py`) and, since X4, every spec `description` (component + inline properties). The gate fails on a missing or different description. OpenAPI 3.0 forbids siblings beside `$ref`: scalar alias rules are written out as the target schema plus a description; array aliases stay `$ref`.
- **Error examples come from the DD (D10)**: the `@error_examples` block holds every example's summary/message/details; the translator renders them per endpoint; `add_error_responses_to_collection.js` copies the spec's examples into Test, Linked and Real-World. `config/error-response-examples.yaml`, V6 and `add_response_examples.py` are retired.
- **Prove a contract change with a migration**: snapshot before, declare the change in `scripts/validation/migrations/<name>.yaml`, rebuild, compare — zero findings required (used for D2 and X4).
- **`ph<>` format is defensive only**: `fix_oneOf_placeholders.js` now writes the first canonical enum value (`propDef.enum[0]`) directly for `jobOptions` fields. The `ph<val1|val2|...>` handler in `addRandomDataToRaw.js` is a fallback for manually-constructed collections only.
- **Repeatable spec builds (M4)**: spec examples use `_EXAMPLE_NOW` and sha256-seeded IDs — two builds from the same DD are byte-identical. Never reintroduce `random`/`datetime.now()` into spec examples (`test_spec_generation_is_repeatable` fails).
- **No silent no-ops**: pipeline scripts exit 1 when they process nothing; Makefile no longer masks guarded steps with `|| echo "Skipping"`.
- **Error map is the authority**: job-endpoint responses and Postman error examples are built from the DD `@http_error_map` per `(status, errorCode)` pair (an example that cannot occur on an endpoint is omitted; since D3 every job endpoint has all 18).
- **Request examples (C1)**: built by the translator from the schema and the DD `@hint`s (first oneOf branch, one item per array unless `minItems`, top-level mutual exclusion keeps `jobOptions`). A request field with no `@hint` and no enum stops the build. A hint on an array field (`tags`) gives the value of each item; every generator applies it that way. The Postman converter ignores request examples (bodies come from the schema).
- **Hint types**: `HINT_TYPES` in the translator (`faker`, `static`, `random_int`, `aba_routing_number`); the gate imports it. An intentionally empty static hint is written `""`.
- **`@reserved`**: `rule = … ; (* @reserved POST /path *)` marks a rule kept for a planned endpoint (`multiDocJobs` → `/static/multi`). The gate accepts it as unreachable and fails once the rule is used or the endpoint is defined.
- **Never pass a spec file as one argument**: Linux caps a single argument at 128 KB (the final spec is ~136 KB). Use `jq --rawfile`, `--data @file` or a pipe; a golden test checks the Makefile.
- **Local builds**: the security repo is cloned beside this one as `c2m-api-v2-postman-security`; `postman/mock-env.json` and `postman/environments/` receive the `C2M_CLIENT_*` values (empty unless set, since L12) and are git-ignored (a test enforces it). Environment uploads create a new environment when the saved UID's environment is gone.
- **GNU Make 3.82+ only**: the Makefile stops under macOS Make 3.81 (it ignores `.ONESHELL`/`.SHELLFLAGS`). Locally use Homebrew's (`gnubin` first on PATH); recipes run with `-eu -o pipefail`, so a command substitution that can legitimately fail needs `|| true`.
- **Never an empty workspace ID**: Postman URLs take it through `POSTMAN_WS_Q`, which stops make when empty (an empty `?workspace=` lists every workspace the key can see). `.env` exports only `NAME=value` lines.
- **Dependencies**: `requirements.txt` = exactly the 8 imported packages (a test enforces it); `make install` = `npm ci`.
- **CI smoke test**: replays the Getting Started setup in a fresh clone and requires a clean tree — commit regenerated base spec / faker_hints with the DD.
- **DD primitive `object` (D6)**: a free-form JSON object (`type: object, additionalProperties: true`); `errorDetails = object`, so every error example's `errorDetails` is an object. `@error_examples` details must be a JSON object.
- **Newman runs the published Test collection**: `ci_verify.sh` (CI, against the published Postman mock) and `prism-mock-test` / `postman-mock` run `c2mapiv2-test-collection-flat.json`, never the intermediate `-fixed` file (L6). Each request asserts its operation's declared statuses (D7) — a hung mock that returns 500 now fails the build (rerun; to-do in the manuals).
- **Every collection carries saved responses** (gate `B-NO-SAVED-RESPONSES`, D9), and each saved `originalRequest` is its request (`B-EXAMPLE-ORIGINAL-REQUEST-DIFFERS`, L6). Getting Started and Real-World cover the job endpoints only, by design (`JOB_ENDPOINTS_ONLY`).
- **No built-in client credentials (L12)**: `fetch_aws_credentials.sh` / `generate_postman_env.sh` leave `clientId`/`clientSecret` empty unless `C2M_CLIENT_*` is set; the pre-request scripts then skip token fetching. CI copies only `.txt` metadata to the artifacts repo, wipes `openapi/ postman/ docs/ sdks/` there first, and fails if an environment file would be published.
- **Migration declarations** (`scripts/validation/migrations/*.yaml`): besides rules/schemas/paths, `value_changes`, `added_examples`, `json_decoded_fields` (D6), `added_requests` (L10), `saved_responses_added` (D9), `nondeterministic`, `path_rewrites` (also applied to string values).
- **Pushes**: until the user lifts it (2026-10-16), push to the `click2mail` remote only, not `origin`.
- **Derived artifacts**: `config/faker_hints.yaml`, `config/c2m_provider_mappings.yaml`, `openapi/c2mapiv2-openapi-spec-*.yaml` — all generated. Do not edit directly.

---

# Recent Changes

## 2026-10-16 — D6–D9, L4/L6/L8–L13, M3, L12: all audit decisions closed; consistency gate has nothing tracked as open

Pushed to click2mail only from `3cf5901` on (user instruction). Detail: manuals `audit-reports/PIPELINE_CHANGES_2026-10-12.md` §20–§27.

| Commit | Item | Change |
|---|---|---|
| `2772977` | D6 (user) | DD `object` primitive; `errorDetails` an object; `cvv` string; `checkDigit` removed |
| `601d4bc` | D7 (user) | Per-operation Newman status assertions from the spec (`declared_statuses.js`); `POSTMAN_ALLOWED_CODES` retired |
| `3769bfe` | L4 (D8) | Recipient ID variants are wrapper objects (breaking, pre-release); spec-vs-DD wrapper list derived from the DD (PASS 185) |
| `2f565ee` | L9 (D8) | One lowercase placeholder style |
| `1a5fe00` | L10/L8 (D8) | Real-World covers every job endpoint (3 scenarios) + JWT pre-request; `JOB_ENDPOINTS_ONLY` |
| `3cf5901` | D9 (user) | Getting Started collections carry saved responses |
| `8aa25fe`, `a69bc3f` | L6 | Auth `originalRequest` = request; `tokenId` example; Newman runs the published (flat) Test collection |
| `292d7d8` | L11/L13 | Stale DD prose; `/static` description no longer calls payment required; prose/marker/description tests |
| `421147e`, `f2d2fbc` | M3 | Duplicate validator retired; Makefile script/target reference tests (another session) |
| `09c97e8` | L12 | No placeholder credential defaults; CI wipes generated artifact dirs; environment files never published |

## 2026-10-14 — D4 list minimums (`cdd73d7`), D5 envelope=none (`c1c5d63`)

- D4 (user): DD ARRAY CONSTRAINTS block → `minItems` (job/recipient lists ≥1, `documentsToMerge` ≥2, `tags` may be empty); `fix_oneOf_placeholders.js` trims to `minItems`.
- D5 (user): `envelope=none: documentClass must be one of (postcard|brochure|flat)`; the build stops on a combination rule that allows every value, names an unknown field/value or can't be read; the enforcer intersects rules per field and runs after `jobOptions` normalisation.

## 2026-10-13 — D3: /batch/zip request-level options (`f890d21`)

User decision (option A): `/batch/zip` accepts optional `jobTemplate`, `returnAddress`, `jobOptions` like `/batch/split`. Job-item precedence defined once in the DD (JOB LISTS): an item's `jobTemplate` replaces the request-level settings for that item. Migration `D3_batch_zip_top_level` clean; validator gained `added_examples`.

## 2026-10-13 — Getting Started guide tested from a fresh clone (`a501d81` … `cae3da3`)

Empty-workspace guard (a guide-made `.env` emptied the workspace ID; cleanup would have hit every workspace); 8 pinned Python packages (91 before; 3.14 could not build); `npm ci`; GNU Make required, with `prism-start`, the with-tests build and fresh-clone noise fixed; helper retries transport failures; CI smoke test of the guide's setup; venv ignored at any depth. Detail: manuals change report §16.

## 2026-10-13 — X6 / L1 / L7 DD cleanup (`d609421`, CI-green click2mail 38455508600 + origin 38455513217)

Unused `HTTP_*` aliases removed (spec −7 schemas); `@reserved` for `multiDocJobs`; gate reachability follows `discriminated_oneof`; `HINT_TYPES` shared; `address3` `""`, `invoiceNumber` and `tags` hints; `addRandomDataToRaw.js` applies hints per array item; catalog `country` USA. Migration validator `value_changes`. `KNOWN_OPEN` 18 → 13 entries. Detail: manuals change report §14.

## 2026-10-13 — C1 request examples; Postman cleanup fails on API errors

**Commits:** `2bfb236` (CI failed at the spec upload: argument limit), `4f1a60d` (fix; CI-green on click2mail 38452195085 + origin 38452199336). Full detail: `c2m-api-v2-manuals/audit-reports/PIPELINE_CHANGES_2026-10-12.md` §12–13.

| ID | Change |
|---|---|
| C1 | Request example on each job endpoint; gate ERROR on missing; checks for schema, mutual exclusion, valid combinations, filler, `@hint` contradictions; merge-minimum finding tracked under D4; migration validator records request examples |
| cleanup | `postman_api_request.sh` for every list/delete in the cleanup targets; spec-delete loops capped (`POSTMAN_DELETE_MAX_PASSES`); `postman-api-clean-trash` removed (HTTP 400 on every build) |
| spec upload | `jq --rawfile` instead of passing the spec as an argument; spec-create targets exit 1 on failure |

## 2026-10-08 → 2026-10-12 — D10, X1/X2, D1, migration validator, D2, X4, Makefile masks

**Commits:** `64389ff`, `461275c`, `7b919cf`, `a8e22d4`, `d836ce5`, `e85c1cb`, `e16705b`, `6453386` (all CI-green on click2mail + origin). Full detail: `c2m-api-v2-manuals/audit-reports/PIPELINE_CHANGES_2026-10-12.md`.

| ID | Change |
|---|---|
| D10 (user) | DD `@error_examples` block is the single source of example content; Postman saved responses copy the spec's examples; YAML / V6 / `add_response_examples.py` retired |
| X1/X2 | Linked and Real-World saved responses are the spec's examples (auth endpoints included) |
| D1 (user) | `paymentType` field (creditCard/invoice/ach/userCredit) + OpenAPI discriminator on `paymentDetails` |
| migration | `validate_migration.py` + golden tests; required before D2 by the user |
| D2 (user) | `singleAddress` removed — `recipientAddressSource` = ByList / ByListId / ByAddressId; address-list minimum deferred to D4 |
| X4 | `@doc` → spec descriptions; gate requires them |
| masks | `postman-auth-setup` (×3 + inside), auth examples, docs-link injection, AWS Dev env upload and `npm install` now fail instead of continuing |

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
make validate-collections-conformance-test      # Golden tests: validator script + resolver 20 + DD constraints 73 + consistency 68 + migration 36 + Postman API helper 30
make validate-collections-conformance-gate-all  # All 5 collections conform to spec
make validate-dd-gates                          # spec vs DD, all 5 collections vs DD, catalog vs spec
make validate-pipeline-consistency              # end-to-end DD → spec → Postman gate
make validate-migration MIGRATION=<name>        # compare a rebuild against a migration's baseline
```

Expected outputs (all clean):
- `✅ All config field names are valid DD rule names`
- `20 passed` / `73 passed` / `68 passed` / `36 passed` / `30 passed` (resolver / DD constraints / consistency / migration validator / Postman API helper; 230 in all)
- `PASS=9 FAIL=0 SKIP=1` (linked/test), `PASS=17 FAIL=0` (GS), `PASS=11 FAIL=0` (real-world)
- `✅ TOTAL — PASS=185 FAIL=0` (spec vs DD); `0 finding(s) across 5 collection(s)`
- `ERROR categories: 0 · known-open WARN categories: 0 · stale allowances: 0`

---

# Known Gaps

Config field names: none — V1–V8 cover them.

The consistency gate's `KNOWN_OPEN` table is empty: every finding is an ERROR. All audit decisions (D1–D10) are made. Open: L5 (the auth overlay disagrees with the security repo's service — revoke statuses, token-ID format, short-token request; deferred by the user, see the manuals `PROJECT_TODO.md`). Business rules resting on our reasoning (D3–D6, ZIP sources / address capture) await Click2Mail's confirmation (`PROJECT_TODO.md`).

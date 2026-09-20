# Validation Scripts

Build-time and post-build validators for the C2M API v2 pipeline.

## Scripts

### `validate_configs_against_dd.py` — V1–V8 config validators

Validates every manually-maintained config file against the EBNF Data Dictionary and
the generated OpenAPI spec. Run as part of every CI build.

**Validators (V1–V8):**

| ID | Function | What it checks |
|---|---|---|
| V1 | `validate_catalog_jobtemplates()` | Reports `jobTemplate:` values in catalog (no enum in spec — informational only) |
| V2 | `validate_catalog_select_fields()` | Catalog `select:` entries vs spec oneOf variants |
| V3a | `validate_template_values()` | Template `values:` key names vs DD rule names |
| V3b | `validate_template_select_fields()` | Template `select:` entries vs spec oneOf variants |
| V5 | `validate_catalog_joboptions_enums()` | Catalog `jobOptions` field values vs spec enum |
| V6 | `validate_error_response_codes()` | `error-response-examples.yaml` `errorCode:` values vs spec enum |
| V7 | `validate_example_paths()` | Catalog + template `path:`/`method:` vs spec operations |
| V8 | `validate_template_inline_discriminators()` | Template inline oneOf discriminator keys vs correct parent schema context |

**Run:**
```bash
make validate-configs
# or directly:
$VENV scripts/validation/validate_configs_against_dd.py \
    --dd data_dictionary/c2mapiv2-dd.ebnf \
    --catalog config/curated-examples-catalog.yaml \
    --template config/getting-started-template.yaml \
    --spec openapi/c2mapiv2-openapi-spec-final.yaml \
    --error-examples config/error-response-examples.yaml
```

Exits 1 on any error. All validators clean on current codebase.

---

### `validate_collections_against_spec.py` — Spec-driven conformance validator

Validates Postman collection request bodies against the generated OpenAPI spec.
Checks structural requirements, oneOf branch selection (V3), and scalar type/enum
values (V4). Placeholder strings (`<String>`, `<Integer>`) are skipped.

See [`SPEC_DRIVEN_VALIDATOR.md`](SPEC_DRIVEN_VALIDATOR.md) for full documentation.

**Run:**
```bash
$VENV scripts/validation/validate_collections_against_spec.py
$VENV scripts/validation/validate_collections_against_spec.py --exit-status  # CI gate
$VENV scripts/validation/validate_collections_against_spec.py --json         # machine-readable
$VENV scripts/validation/validate_collections_against_spec.py --report reports/conformance.md
```

**Current state:** Linked/Test `PASS=9 FAIL=0 SKIP=1` · Getting Started `PASS=17 FAIL=0` · Real-World `PASS=8 FAIL=0`

---

### `validate_all_collections_against_spec.py`

Batch runner: validates all 4 canonical collections in `postman/generated/` and
reports aggregate results. Used by `make validate-collections-conformance-gate-all`
(CI gate, fails build on FAIL > 0).

---

### `validate_catalog_against_spec.py`

Validates `select:` entries in `config/curated-examples-catalog.yaml` against the
spec's oneOf variants. Overlaps with V2 in `validate_configs_against_dd.py`; provides
a more detailed standalone report.

---

### `diff_collections.py` — Structural diff

Compares two Postman collections structurally (field paths + kinds; values ignored).
Useful before/after a regeneration to confirm no endpoints were dropped or structure
changed unexpectedly.

```bash
$VENV scripts/validation/diff_collections.py \
    --before postman/generated/c2mapiv2-linked-collection-flat.json \
    --after  /tmp/regenerated-collection.json

# Enforce that no endpoint was dropped:
$VENV scripts/validation/diff_collections.py \
    --before postman/generated/c2mapiv2-linked-collection-flat.json \
    --after  /tmp/regenerated-collection.json \
    --require-coverage
```

---

### `run_newman.sh` — Newman test runner

Standardized wrapper for Newman with timestamped HTML/JSON reports. Called by
`ci_verify.sh` which is called by CI.

```bash
./scripts/validation/run_newman.sh \
    -c postman/generated/c2mapiv2-test-collection-flat.json \
    -e postman/mock-env.json

# Custom output directory and reporters:
./scripts/validation/run_newman.sh \
    -c collection.json -e environment.json \
    -o /tmp/reports -r cli,html,junit
```

**Output:** `reports/newman-{collection}-{timestamp}.html` and `.json`

---

### `verify_mocks.py` (diagnostic — moved to `scripts/utilities/`)

Originally designed to verify mock server responses. **Does not work against this
all-POST API**: sending an empty `{}` body triggers a 422 validation error before
schema validation runs, so mock correctness is never checked. Kept in
`scripts/utilities/` as a diagnostic reference only. Not called by CI or Makefile.

---

## Tests (`tests/`)

Golden test suite proving the validators themselves are correct.

| File | Tests | What it covers |
|---|---|---|
| `test_dd_constraints.py` | 28 | EBNF translator output, faker_hints.yaml, provider_mappings.yaml, golden collection structure |
| `test_validate_collections.py` | varies | Spec-driven validator: positive controls, negative controls, synthetic fault injection, placeholder handling, oneOf discrimination, scalar type/enum |

**Run:**
```bash
make validate-collections-conformance-test
# or directly:
$VENV scripts/validation/tests/test_dd_constraints.py
$VENV scripts/validation/tests/test_validate_collections.py
```

All 28 golden assertions pass in CI. The test suite is built before running in CI
by `make postman-build-golden-test-fixtures` (no API keys required).

---

## Makefile targets

| Target | What it runs |
|---|---|
| `make validate-configs` | V1–V8 config validators |
| `make validate-collections-conformance` | Spec-driven validator on existing generated collections (report-only) |
| `make validate-collections-conformance-gate` | CI gate: regenerates Linked fresh, validates with `--exit-status` |
| `make validate-collections-conformance-gate-all` | CI gate: validates all 4 canonical collections with `--exit-status` |
| `make validate-collections-conformance-test` | Runs both golden test files |

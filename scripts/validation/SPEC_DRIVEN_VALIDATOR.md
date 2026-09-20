# Spec-driven collection validator

Non-hardcoded replacement for the legacy `c2m-api-v2-manuals/validate_collections.py`.
Validates Postman collection request bodies against the **generated OpenAPI spec**
(the single source of truth, itself generated from the EBNF). No per-endpoint rules
are hardcoded — expectations are read live from the spec, so changing the EBNF and
regenerating the spec automatically changes what the validator enforces.

## Files
- `validate_collections_against_spec.py` — the validator (structural + oneOf + scalar).
- `tests/test_validate_collections.py` — the golden test suite that proves it.
- `diff_collections.py` — before/after structural diff (companion acceptance check).

## Two acceptance checks for a merge / regeneration
The validator and the diff answer different questions; use both:

| Check | Question it answers | Covers |
|---|---|---|
| `validate_collections_against_spec.py` | Do the request bodies conform to the spec? | Required fields, field names, oneOf branch selection, scalar type/enum |
| `diff_collections.py` | What *changed* between two collections? | EVERY structural change incl. oneOf interiors + flattening |

`diff_collections.py` is **structural, not value-level**: it compares the set of
field paths + kinds (array indices normalized, scalar values ignored), so random
example data creates no noise — identical structure diffs to nothing. It surfaces
`jobs`->`multiDocJobs`, wrapper add/removal, object-vs-array flips, and
nesting/flattening. Two views: an endpoint rollup (name-independent, works even
when example names differ across the two template systems) and a request-level
diff (matched by method+path+name, lists unmatched requests).

```bash
# During the dual-template merge dry-run: current vs regenerated
$VENV scripts/validation/diff_collections.py \
    --before postman/generated/c2mapiv2-getting-started-test-collection.json \
    --after  <regenerated-collection>.json
```
Report-only (exit 0). Read it and decide — this is the check that makes the
merge's interior/flattening changes and example-preservation VISIBLE before
anything is published, closing the validator's structural-interior coverage gap.

## Run

> **Spec choice:** validates against `openapi/c2mapiv2-openapi-spec-final.yaml`
> (the source-of-truth contract; identical to `-base` for the job endpoints).
> Do NOT use `openapi/bundled.yaml` — bundling flattens single-alias `oneOf`
> chains (`documentIdSource -> documentId -> id` collapses to a bare `id`, and
> `recipientAddressSource` collapses to `[…, id, id]`). That is a derived-artifact
> distortion, not the real contract, and not what generates the Postman collections.

```bash
VENV=scripts/python_env/e2o.venv/bin/python   # has yaml + jsonschema

# Validate the 4 canonical collections against the final spec
$VENV scripts/validation/validate_collections_against_spec.py

# Machine-readable / CI-gating / report
$VENV scripts/validation/validate_collections_against_spec.py --json
$VENV scripts/validation/validate_collections_against_spec.py --exit-status
$VENV scripts/validation/validate_collections_against_spec.py --report reports/spec-conformance.md

# Prove the validator itself (golden suite — 28 assertions)
$VENV scripts/validation/tests/test_validate_collections.py
```

## What the validator checks

### Structural (Phase 1)
- Required fields present (recursively, following `$ref`)
- No unexpected fields (where `additionalProperties` is not allowed)
- Object/array shape

### oneOf branch discrimination (V3)
`_best_branch()` scores each oneOf/anyOf branch by counting how many of its `required`
keys are present in the value, then recurses into the highest-scoring branch. Placeholder
strings (`<...>`) skip the check entirely. This was added in commit `76a036f`.

### Scalar type/enum checks (V4)
`_type_matches()` checks JSON Schema type compatibility. After the structural and oneOf
passes, scalar values are checked against `type` and `enum` constraints. Values matching
`<[^>]+>` (placeholders) are skipped. This was added in commit `76a036f`.

## Why a golden test suite
The legacy validator was hardcoded and silently drifted from the EBNF (it forbade a
field the EBNF allows). To prevent that here, the validator is proven against inputs
whose correct verdict is already known — **before** it is trusted to measure anything:

1. **Positive controls** — Linked/Test collections (EBNF-driven) MUST pass with zero
   failures (guards against false positives).
2. **Negative controls** — synthetic bodies with known defects (wrong field name,
   missing required, unexpected field, wrong enum value) MUST produce the expected
   failures (guards against false negatives).
3. **Placeholder bodies** — fields containing `<String>` / `<Integer>` MUST be skipped,
   not flagged.

Current golden suite state: **28/28 assertions pass** in CI.

## CI gate status

The validator is wired into CI in two places:

1. **Per-build gate** (`validate-collections-conformance-gate`, commit `2a4bddc`):
   Regenerates the Linked collection fresh into a temp dir, validates with
   `--exit-status`, fails the build on any `FAIL > 0`. Runs before the Publish step.

2. **All-4-collections gate** (`validate-collections-conformance-gate-all`, commit
   `2a4bddc`): Validates all 4 canonical collections in `postman/generated/` with
   `--exit-status`. Runs after `postman-build-golden-test-fixtures` in CI.

Current conformance state (all 4 collections):
- **Linked + Test:** `PASS=9 FAIL=0 SKIP=1` (SKIP=1 = `/auth/tokens/revoke`, no body — permanent)
- **Getting Started (linked + test):** `PASS=17 FAIL=0 SKIP=0`
- **Real-World:** `PASS=8 FAIL=0 SKIP=0`

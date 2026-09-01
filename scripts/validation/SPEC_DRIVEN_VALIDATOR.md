# Spec-driven collection validator

Non-hardcoded replacement for the legacy `c2m-api-v2-manuals/validate_collections.py`.
Validates Postman collection request bodies against the **generated OpenAPI spec**
(the single source of truth, itself generated from the EBNF). No per-endpoint rules
are hardcoded — expectations are read live from the spec, so changing the EBNF and
regenerating the spec automatically changes what the validator enforces.

## Files
- `validate_collections_against_spec.py` — the validator (Phase 1: structural).
- `tests/test_validate_collections.py` — the golden test suite that proves it.

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

# Prove the validator itself (golden suite)
$VENV scripts/validation/tests/test_validate_collections.py
```

## What Phase 1 checks (structural, placeholder-safe)
- required fields present (recursively, following `$ref`)
- no unexpected fields (where `additionalProperties` is not allowed)
- object/array shape

Scalar **type/enum/format** and **oneOf/anyOf branch selection** are intentionally
NOT validated in Phase 1: reliable branch discrimination needs type/discriminator
awareness, which collides with placeholder values (`<Integer>`) and produces false
positives. Every known divergence (see the §5a table in
`c2m-api-v2-manuals/audit-reports/DUAL_TEMPLATE_SYSTEM_FINDINGS_2026-08-30.md`) is a
top-level required/field-name issue, all caught here. Deep type + discriminator-aware
oneOf validation is a documented Phase 2 (`--deep`).

## Why a golden test suite
The legacy validator was hardcoded and silently drifted from the EBNF (it forbade a
field the EBNF allows). To prevent that here, the validator is proven against inputs
whose correct verdict is already known — **before** it is trusted to measure anything:

1. **Positive controls** — System A (EBNF-driven Linked/Test) MUST pass with zero
   failures (guards against false positives).
2. **Negative controls / golden §5a** — System B (Getting Started) MUST fail on
   exactly the documented divergent endpoints and pass the known-good ones
   (guards against false negatives).
3. **Synthetic faults** — hand-crafted bodies with known defects (wrong field name,
   missing required, unexpected field) + known-clean bodies + placeholder bodies.

Current state: **all golden assertions pass**, and the validator independently
reproduces the §5a divergence table (System A clean; System B fails 9 examples across
6 endpoints, `multi/zip` + the 8 conforming `single/doc` examples pass).

## Sequencing / CI
Report-only today. It is NOT yet wired into `make`/CI as a gate. Do not gate before
the dual-template merge — the Getting Started collections fail 6/8 endpoints now, so a
gate would turn the build red. Sequence: (1) trust the validator [done], (2) use it as
the merge acceptance test, (3) then add it to CI as a gate once System B is clean.
Retire the legacy `c2m-api-v2-manuals/validate_collections.py` at that point.

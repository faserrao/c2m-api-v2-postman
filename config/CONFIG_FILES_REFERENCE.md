# Config Files Reference

This document describes each active file in `config/`. All five files feed into the
build pipeline; none are edited manually at runtime. The EBNF Data Dictionary
(`data_dictionary/c2mapiv2-dd.ebnf`) is the ultimate source of truth — config files
either derive from it or must stay in sync with it.

---

## 1. `curated-examples-catalog.yaml`

**Purpose:** Single source of truth for every curated example that appears in the
Real World Use Cases and Getting Started Postman collections.

**Used by:**
- `scripts/utilities/generate_getting_started_collections.py` — builds the two Getting
  Started collections (linked + test)
- `Makefile` targets `postman-generate-real-world-collection`,
  `postman-generate-getting-started-linked-collection`
- `scripts/validation/validate_configs_against_dd.py` — validates all field names
  against DD rule names at build time (`make validate-configs`)
- `scripts/validation/validate_catalog_against_spec.py` — validates `select:` keys and
  variant names against the live OpenAPI spec (`make validate-catalog-against-spec`)

**Structure:**

```
groups:          # Folder layout for Getting Started collections
  - logical_name: most-frequently-used
    display_name: Most Frequently Used
    order: 1

examples:        # One entry per curated request
  - name: Legal Firm - Court Notices
    method: POST
    path: /static
    group: most-frequently-used   # links to a group above (getting-started only)
    tags:
      - real-world                # "real-world" → Real World collection
      - getting-started           # "getting-started" → Getting Started collections
    select:
      docSourceStandard: documentId   # which oneOf branch to materialise
      paymentDetails: ach
    values:                       # FLAT leaf values only
      documentId: 2001
      routingNumber: "111000025"
```

**Key rules:**
- `values:` must contain **flat leaf primitives only** — no nested objects. The
  generator reads nesting from the Linked Collection.
- All keys in `values:` must be valid EBNF DD rule names (enforced by
  `validate_configs_against_dd.py`).
- `select:` keys are oneOf branch selectors validated against the OpenAPI spec.
- `jobTemplate:` values are customer-defined template names (no enum in the spec);
  the values here are illustrative only and are not spec-validated.
- The `group:` field is only meaningful for entries tagged `getting-started`.

**How to add a new example:** Add an entry under `examples:`, set `tags` to control
which collections it appears in, set `select:` to choose oneOf branches, and set
`values:` to provide leaf data. Run `make validate-configs` before committing.

---

## 2. `getting-started-template.yaml`

**Purpose:** Defines the folder structure, endpoint list, and per-request field
overrides for the Getting Started collections. It is the structural complement to
`curated-examples-catalog.yaml` — the catalog provides realistic values for curated
scenarios; this template defines which endpoints appear and their placeholder layout.

**Used by:**
- `scripts/utilities/generate_getting_started_collections.py` via `--template`
- `scripts/validation/validate_configs_against_dd.py` (`make validate-configs`)
- `Makefile` target `postman-generate-getting-started-with-examples`

**Structure:**

```
collection:
  name: C2M API v2 - Getting Started
  version: 1.0.0

schema_references:
  openapi_spec: openapi/c2mapiv2-openapi-spec-base.yaml
  linked_collection: postman/generated/c2mapiv2-linked-collection-flat.json

groups:                          # Postman folder definitions
  - logical_name: most-frequently-used
    display_name: Most Frequently Used
    order: 1

examples:                        # One entry per Getting Started request
  - name: /static - single or list of recipient
    method: POST
    path: /static
    group: most-frequently-used
    select:
      docSourceAll: requestId
      recipientAddressSource: recipientAddressByList
    values:
      jobTemplate: <String>      # placeholder; faker_hints fills real value
      pdfSplitJobsNoAddress:
        - startPage: <Integer>
          endPage: <Integer>
```

**Key rules:**
- Placeholder values (`<String>`, `<Integer>`) are replaced at collection-generation
  time using `faker_hints.yaml` (for the linked collection) or
  `addRandomDataToRaw.js` (for the test collection).
- The `faker_hints:` section was removed from this file in September 2026; hints now
  live in the EBNF DD as `@hint` annotations and are derived into `faker_hints.yaml`.
- The `groups:` list here controls the Getting Started folder layout. The catalog's
  `groups:` list controls the Real World / Getting Started (catalog) layout —
  they are separate.

**Relationship to catalog:** Both files serve the Getting Started generator but cover
different concerns. The template defines which endpoints appear and their structural
shape; the catalog provides realistic business-scenario values for curated examples.

---

## 3. `faker_hints.yaml`

**Purpose:** Derived artifact providing realistic placeholder values for every field
used in the Getting Started collections. **Do not edit this file directly** — it is
regenerated from the EBNF Data Dictionary on every build.

**Generated by:**
- `scripts/active/ebnf_to_openapi_dynamic_v3.py` via `--faker-hints-output
  config/faker_hints.yaml` (part of `make generate-openapi-spec-from-ebnf-dd`)

**Used by:**
- `scripts/utilities/generate_getting_started_collections.py` via `--faker-hints`
- `scripts/validation/validate_configs_against_dd.py` (`make validate-configs`)

**Structure:**

```yaml
# DO NOT EDIT — update the @hint annotation in the EBNF Data Dictionary instead.
faker_hints:
  firstName:
    type: faker          # call Faker.js method
    method: first_name
  cardNumber:
    type: static         # use this exact value
    value: 4111111111111111
  documentId:
    type: random_int     # pick a random integer in range
    min: 10000
    max: 99999
  layout:
    type: static
    value: address_on_first_page
```

**Three hint types:**

| Type | Meaning | Fields used |
|------|---------|-------------|
| `faker` | Call a Faker.js method by name | `firstName`, `lastName`, `city`, `state`, `zip`, `address1`, `company` |
| `static` | Always emit this exact value | `cardNumber`, `cardType`, `cvv`, `month`, `year`, `layout`, `mailClass`, etc. |
| `random_int` | Random integer between `min`/`max` | `documentId`, `requestId`, `zipDocumentId`, `addressListId` |

**How to change a hint:** Edit the `@hint` annotation on the relevant rule line in
`data_dictionary/c2mapiv2-dd.ebnf`, then run `make generate-openapi-spec-from-ebnf-dd`
to regenerate this file. Commit both the DD and this file together.

---

## 4. `error-response-examples.yaml`

**Purpose:** Single source of truth for all HTTP error response examples injected into
the OpenAPI spec and Postman collections. Defines one or more named examples per HTTP
status code, each with a fixed `errorCode`, human-readable `errorMessage`, and
`errorDetails` JSON string.

**Used by:**
- `scripts/active/add_response_examples.py` — injects examples into the OpenAPI spec
- `scripts/active/add_error_responses_to_collection.js` — injects examples into
  Postman collection responses

**Structure:**

```yaml
400:
  missing_field:
    summary: "Missing required field"
    errorMessage: "Required field is missing from request body"
    errorCode: MISSING_REQUIRED_FIELD
    errorDetails: '{"field": "documentId", "location": "requestBody"}'
  invalid_json:
    summary: "Invalid JSON"
    ...

401:
  missing_token: ...
  invalid_token: ...
  expired_token: ...
```

**Key rules:**
- `errorCode` values **must** match the `errorCode` enum in the EBNF DD. The
  injection scripts validate this at runtime.
- `errorType` is **not** included here — it is derived from `x-http-error-map` in the
  spec at injection time and must not be hardcoded.
- `errorTrackingId` is **not** included — generated dynamically per invocation.
- Two template tokens are supported in `errorDetails`:
  - `{timestamp}` — replaced with the current UTC time
  - `{expired}` — replaced with one hour ago (token-expiry context)
- HTTP status codes covered: 400, 401, 403, 404, 422, 429, 500.

**How to add a new error example:** Add a named entry under the relevant status code.
Ensure `errorCode` matches an existing value in the DD `errorCode` enum. Do not add
`errorType` or `errorTrackingId`.

---

## 5. `c2m_provider_mappings.yaml`

**Purpose:** Maps Click2Mail canonical `jobOptions` field values (as defined in the
EBNF DD) to the literal strings accepted by each provider or legacy system. Acts as a
translation layer between the canonical API surface and provider-specific terminology.

**Used by:**
- `scripts/validation/tests/test_dd_constraints.py` — the golden test suite verifies
  that every EBNF enum value is covered by a mapping entry, and that legacy aliases
  resolve to canonical values.

**Not used** directly in the production build pipeline — it is a reference/test-support
file, not called by any Makefile target at collection-generation time.

**Structure:**

```yaml
mailClass:
  first_class: "first_class"     # canonical == provider (pass-through)
  standard:    "standard"
  non_profit:  "non_profit"
  _aliases:                      # legacy/variant names → canonical
    firstClass:    first_class
    "First Class": first_class

envelope:
  standard:      "standard"
  double_window: "double_window"
  _aliases:
    windowed:            double_window   # old name → canonical
    "#10 double window": double_window
```

**Fields covered:** `mailClass`, `color`, `paperType`, `printOption`,
`productionTime`, `envelope`, `documentClass`, `layout`.

**Key rules:**
- Every canonical value in the EBNF DD enum **must** have an entry here (enforced by
  `test_provider_mappings_covers_all_enum_fields` in the golden test suite).
- Legacy aliases go under `_aliases:` keyed by the old name, value is the canonical
  name. The test suite verifies that `address_on_top` aliases to
  `address_on_first_page`.
- A `null` provider literal means the canonical value is passed through unchanged.

**How to update:** When the EBNF DD gains a new enum value, add a corresponding entry
here. When a provider changes its accepted literal, update the mapping value. Run
`make validate-collections-conformance-test` to confirm the golden tests still pass.

---

## Summary Table

| File | Edited by humans? | Validated by | Generated by |
|------|-------------------|--------------|--------------|
| `curated-examples-catalog.yaml` | Yes | `validate_configs_against_dd.py`, `validate_catalog_against_spec.py` | — |
| `getting-started-template.yaml` | Yes | `validate_configs_against_dd.py` | — |
| `faker_hints.yaml` | **No — DO NOT EDIT** | `validate_configs_against_dd.py` | `ebnf_to_openapi_dynamic_v3.py` |
| `error-response-examples.yaml` | Yes | Runtime check in `add_response_examples.py` | — |
| `c2m_provider_mappings.yaml` | Yes | `test_dd_constraints.py` (golden tests) | — |

## Archived Files

Files previously in `config/` that have been moved to `config/archive/`:

| File | Reason archived |
|------|-----------------|
| `collection-template-blank.yaml` | Zero references anywhere in the repo |
| `getting-started-curated-test.yaml` | Only ever written to by `extract_yaml_from_postman.py`; never read as input by any pipeline step |
| `curated-examples-from-collection.yaml` | Superseded by `curated-examples-catalog.yaml` |
| `getting-started-patterns-from-collection.yaml` | Superseded by `getting-started-template.yaml` |
| `getting-started-patterns.yaml` | Superseded by `getting-started-template.yaml` |

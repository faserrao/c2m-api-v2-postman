# Test Data Generation Architecture

## Current Architecture (PROBLEMATIC)

```
┌─────────────────────────────────────────────────────────────────┐
│                      THREE SEPARATE SYSTEMS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. generate_use_case_collection.py                              │
│     └── Hardcoded static payloads                                │
│     └── Hardcoded dynamic variants                               │
│     └── NO reference to OpenAPI spec                             │
│                                                                   │
│  2. addRandomDataToRaw.js                                        │
│     └── Hardcoded oneOf fixtures                                 │
│     └── Random value generation                                  │
│     └── NO schema validation                                     │
│                                                                   │
│  3. add_examples_to_spec.py                                      │
│     └── Type-based generation only                               │
│     └── Doesn't understand oneOf                                 │
│     └── No business rule awareness                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ⬇️
                     INCONSISTENT DATA
                     VALIDATION ERRORS  
                     400 RESPONSES
```

## Proposed Architecture (CORRECT)

```
┌─────────────────────────────────────────────────────────────────┐
│                    SINGLE SOURCE OF TRUTH                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  EBNF Data Dictionary                                            │
│     ↓                                                            │
│  OpenAPI Spec (c2mapiv2-openapi-spec-final.yaml)               │
│     ↓                                                            │
│  Schema-Aware Example Generator                                  │
│     ├── Understands oneOf schemas                                │
│     ├── Knows discriminator fields                               │
│     ├── Applies business rules                                   │
│     └── Generates coverage matrix                                │
│     ↓                                                            │
│  OpenAPI Spec with Validated Examples                           │
│     ↓                                                            │
│  ┌─────────────────────────────────────┐                        │
│  │  ALL Collections Use Same Examples   │                        │
│  ├─────────────────────────────────────┤                        │
│  │  • Linked Collection                 │                        │
│  │  • Test Collection                   │                        │
│  │  • Use Case Collection               │                        │
│  └─────────────────────────────────────┘                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ⬇️
                     CONSISTENT DATA
                     VALID REQUESTS
                     200 RESPONSES
```

## Example Generation Flow

```
Input: OneOf Schema
{
  "oneOf": [
    {"type": "object", "properties": {"documentId": {"type": "integer"}}},
    {"type": "object", "properties": {"externalUrl": {"type": "string", "format": "uri"}}},
    {"type": "object", "properties": {
      "uploadRequestId": {"type": "integer"},
      "documentName": {"type": "string"}
    }}
  ]
}

                    ⬇️

Schema-Aware Generator Process:
1. Detect oneOf pattern
2. Generate example for EACH variant
3. Validate each example against schema
4. Track coverage

                    ⬇️

Output: Complete Example Set
[
  {"documentId": 1234},
  {"externalUrl": "https://api.example.com/v1/doc/5678"},
  {"uploadRequestId": 100, "documentName": "invoice.pdf"},
  {"uploadRequestId": 200, "zipId": 10, "documentName": "report.pdf"},
  {"zipId": 20, "documentName": "summary.pdf"}
]
```

## Validation Matrix

| Endpoint | OneOf Fields | Variants | Coverage | Status |
|----------|-------------|----------|----------|---------|
| /jobs/single-doc-job-template | documentSourceIdentifier | 5 | 100% | ✅ |
| /jobs/single-doc-job-template | paymentDetails | 6 | 100% | ✅ |
| /jobs/single-doc-job-template | recipientAddressSource | 3 | 100% | ✅ |
| /jobs/multi-doc-merge | documentsToMerge items | 5 | 100% | ✅ |
| ... | ... | ... | ... | ... |

## Next Steps

1. **Immediate**: Fix static payloads in generate_use_case_collection.py
2. **Short-term**: Implement basic schema validation 
3. **Long-term**: Build schema-aware example generator
4. **Future**: Automated coverage reporting and validation
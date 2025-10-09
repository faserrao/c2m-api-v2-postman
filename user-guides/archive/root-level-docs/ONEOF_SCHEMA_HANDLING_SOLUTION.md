# OneOf Schema Handling Solution

## Overview

This document describes the comprehensive solution implemented to handle oneOf schemas in the C2M API pipeline, addressing limitations in openapi-to-postmanv2.

## Problem Statement

1. **EBNF Source**: The data dictionary defines union types like `documentSourceIdentifier` using alternation (`|`)
2. **OpenAPI Generation**: The EBNF-to-OpenAPI converter was creating anonymous inline schemas for concatenations
3. **Tool Limitation**: openapi-to-postmanv2 simplifies oneOf to the first variant's type (e.g., `<integer>`)
4. **Developer Confusion**: Linked collections showed `<integer>` for fields that actually accept multiple types

## Implemented Solution

### 1. Fixed at the Source (EBNF → OpenAPI)

Modified `scripts/active/ebnf_to_openapi_dynamic_v3.py` to generate named schemas for all oneOf variants:

```python
# Before: Anonymous inline schema
"oneOf": [
  { "$ref": "#/components/schemas/documentId" },
  { "type": "object", "properties": {...} }  # Anonymous!
]

# After: All named schemas
"oneOf": [
  { "$ref": "#/components/schemas/documentId" },
  { "$ref": "#/components/schemas/DocumentSourceWithUpload" }
]
```

New named schemas created:
- `DocumentSourceWithUpload` - for `uploadRequestId + documentName`
- `DocumentSourceWithUploadAndZip` - for `uploadRequestId + zipId + documentName`
- `DocumentSourceFromZip` - for `zipId + documentName`

### 2. Post-Processing for Linked Collections

Created `scripts/active/fix_oneOf_placeholders.js` to replace type placeholders with `<oneOf>`:

- Runs immediately after Postman collection generation
- Identifies known oneOf fields (documentSourceIdentifier, paymentDetails, recipientAddressSource)
- Replaces `<integer>`, `<string>`, etc. with `<oneOf>`
- Provides clear indication that the field accepts multiple types

### 3. Test Collection Examples

The existing `addRandomDataToRaw_oneOf.js` script handles test collections by:
- Rotating through all oneOf variants
- Generating proper complex objects for each variant
- Ensuring comprehensive test coverage

## Pipeline Integration

```makefile
postman-api-linked-collection-generate:
    # 1. Generate collection from OpenAPI
    $(GENERATOR_OFFICIAL) -s $(OPENAPI_SPEC) -o $(COLLECTION_RAW)
    
    # 2. Add info block
    $(call jqf,$(JQ_ADD_INFO_FILE),$(COLLECTION_RAW))
    
    # 3. Fix oneOf placeholders (NEW!)
    @node scripts/active/fix_oneOf_placeholders.js $(COLLECTION_RAW) $(COLLECTION_RAW)
```

## Results

### Linked Collection (Schema View)
- **Before**: `"documentSourceIdentifier": "<integer>"`
- **After**: `"documentSourceIdentifier": "<oneOf>"`

### Test Collection (Example Data)
- Rotates through all variants:
  - `1234` (integer)
  - `"https://api.example.com/v1/documents/5678"` (URL)
  - `{ "uploadRequestId": 100, "documentName": "invoice.pdf" }` (object)
  - etc.

## Why Not Use Discriminators?

While OpenAPI supports discriminators for oneOf handling, they require:
1. Adding a type property to all data (e.g., `{ "type": "documentId", "value": 1234 }`)
2. Modifying the API contract to satisfy tooling
3. Adding unnecessary complexity to the data model

Our solution preserves the clean API design while working around tool limitations.

## Maintenance

When adding new oneOf fields:
1. Ensure they follow the EBNF alternation pattern
2. Add the field name to `oneOfFields` in `fix_oneOf_placeholders.js`
3. The EBNF-to-OpenAPI converter will automatically create named schemas for concatenations

## Testing

To verify oneOf handling:
```bash
# Generate and check OpenAPI spec
make generate-openapi-spec-from-dd
grep -A 10 "oneOf:" openapi/c2mapiv2-openapi-spec-final.yaml

# Generate and check Postman collection
make postman-api-linked-collection-generate
grep "<oneOf>" postman/generated/c2mapiv2-collection.json
```
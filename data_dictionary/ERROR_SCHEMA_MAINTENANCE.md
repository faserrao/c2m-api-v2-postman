# Error Schema Maintenance Guide

**Purpose**: Instructions for adding, removing, or modifying error structures in the C2M API v2.

**Last Updated**: 2026-02-17

---

## Overview

Error handling requires updates in **three locations**:
1. EBNF Data Dictionary (schema definitions)
2. OpenAPI Example Script (response examples for specs)
3. Postman Collection Script (response examples for mock server)

**Automatic validation** will catch mismatches between EBNF and scripts.

---

## Adding a New Error Code

### Step 1: Update EBNF Data Dictionary

**File**: `data_dictionary/c2mapiv2-dd.ebnf`

**Location**: Lines 933-949 (errorCode enum)

**Action**: Add new error code to enum

**Example**:
```ebnf
errorCode =
      "MISSING_REQUIRED_FIELD"
    | "INVALID_ONEOF"
    | "INVALID_JSON"
    | "MALFORMED_REQUEST"
    | "MISSING_AUTH_HEADER"
    | "INVALID_TOKEN"
    | "EXPIRED_TOKEN"
    | "INSUFFICIENT_PERMISSIONS"
    | "ACCOUNT_SUSPENDED"
    | "RESOURCE_NOT_FOUND"
    | "JOB_NOT_FOUND"
    | "INVALID_FORMAT"
    | "BUSINESS_RULE_VIOLATION"
    | "INVALID_ENUM_VALUE"
    | "SERVER_ERROR"
    | "DATABASE_ERROR"
    | "EXTERNAL_SERVICE_ERROR"
    | "NEW_ERROR_CODE"           (* NEW: Add description here *)
    ;
```

### Step 2: Add Example to OpenAPI Script

**File**: `scripts/active/add_response_examples.py`

**Location**: Lines 90-173 (ERROR_EXAMPLES dictionary)

**Action**: Add example to appropriate HTTP status code section

**Example** (adding to 400 Bad Request):
```python
'400': {
    'missing_field': { ... },
    'invalid_oneOf': { ... },
    'malformed_json': { ... },
    'new_error_example': {                              # NEW
        'summary': 'Brief description',
        'value': {
            'errorType': 'ValidationError',
            'errorMessage': 'Human-readable message',
            'errorCode': 'NEW_ERROR_CODE',
            'errorDetails': '{"context": "additional info"}',
            'errorTrackingId': 'TRK-20260217-ABC123'
        }
    }
}
```

### Step 3: Add Example to Postman Script

**File**: `scripts/active/add_error_responses_to_collection.js`

**Location**: Lines 16-120 (ERROR_RESPONSES object)

**Action**: Add example to appropriate HTTP status code array

**Example** (adding to 400 errors):
```javascript
'400': [
  { /* existing examples */ },
  {
    name: 'Brief description',
    code: 400,
    _postman_previewlanguage: 'json',
    header: [{ key: 'Content-Type', value: 'application/json' }],
    body: JSON.stringify({
      errorType: 'ValidationError',
      errorMessage: 'Human-readable message',
      errorCode: 'NEW_ERROR_CODE',
      errorDetails: '{"context": "additional info"}',
      errorTrackingId: 'TRK-20260217-ABC123'
    }, null, 2)
  }
]
```

### Step 4: Regenerate and Test

```bash
# Regenerate OpenAPI spec
make generate-openapi-spec-from-ebnf-dd

# Validation will automatically check errorCode values
# Script will exit with error if NEW_ERROR_CODE not in examples

# Full rebuild
make postman-instance-build-without-tests
```

**Expected Output**:
```
Found 18 valid errorCode values in EBNF enum  # Was 17, now 18
All errorCode values in ERROR_EXAMPLES are valid
```

---

## Removing an Error Code

### Step 1: Remove from EBNF

**File**: `data_dictionary/c2mapiv2-dd.ebnf`

**Action**: Delete line from errorCode enum (lines 933-949)

### Step 2: Remove from OpenAPI Script

**File**: `scripts/active/add_response_examples.py`

**Action**: Delete example dictionary from ERROR_EXAMPLES (lines 90-173)

### Step 3: Remove from Postman Script

**File**: `scripts/active/add_error_responses_to_collection.js`

**Action**: Delete example object from ERROR_RESPONSES (lines 16-120)

### Step 4: Regenerate and Test

```bash
make generate-openapi-spec-from-ebnf-dd
make postman-instance-build-without-tests
```

**Note**: Removing errors is rare - consider marking as deprecated instead.

---

## Modifying Error Messages

**To change error message text only** (no errorCode changes):

### Update OpenAPI Script

**File**: `scripts/active/add_response_examples.py`

**Location**: Lines 90-173

**Change**: Update `errorMessage` field in appropriate example

**Example**:
```python
'value': {
    'errorType': 'ValidationError',
    'errorMessage': 'New improved message text',  # CHANGED
    'errorCode': 'MISSING_REQUIRED_FIELD',
    'errorDetails': '{"field": "documentId", "location": "requestBody"}',
    'errorTrackingId': 'TRK-20260217-ABC123'
}
```

### Update Postman Script

**File**: `scripts/active/add_error_responses_to_collection.js`

**Location**: Lines 16-120

**Change**: Update errorMessage in JSON.stringify

**Example**:
```javascript
body: JSON.stringify({
  errorType: 'ValidationError',
  errorMessage: 'New improved message text',  // CHANGED
  errorCode: 'MISSING_REQUIRED_FIELD',
  errorDetails: '{"field": "documentId", "location": "requestBody"}',
  errorTrackingId: 'TRK-20260217-ABC123'
}, null, 2)
```

### Rebuild

```bash
make postman-instance-build-without-tests
```

**Note**: No EBNF changes needed for message-only updates.

---

## Adding a New HTTP Error Status Code

**Current supported codes**: 400, 401, 403, 404, 422, 500

**To add new code** (e.g., 429 Rate Limit Exceeded):

### Step 1: Update Translator

**File**: `scripts/active/ebnf_to_openapi_dynamic_v3.py`

**Location**: Lines 427-468 (hardcoded error response references)

**Action**: Add new status code block

**Example**:
```python
# Add after line 468
'429': {
    'description': 'Too many requests - rate limit exceeded',
    'content': {
        'application/json': {
            'schema': {'$ref': '#/components/schemas/HTTP_429_TOO_MANY_REQUESTS'}
        }
    }
}
```

### Step 2: Update EBNF (HTTP error alias)

**File**: `data_dictionary/c2mapiv2-dd.ebnf`

**Location**: After line 972 (after HTTP_500_INTERNAL_SERVER_ERROR)

**Action**: Add alias definition

**Example**:
```ebnf
HTTP_429_TOO_MANY_REQUESTS = errorResponse ;
```

### Step 3: Add Examples (Both Scripts)

Follow "Adding a New Error Code" steps 2-4 above, using '429' as the key.

### Step 4: Regenerate and Test

```bash
make generate-openapi-spec-from-ebnf-dd
make postman-instance-build-without-tests
```

---

## Validation Workflow

**Automatic Validation** runs during `make openapi-build`:

1. Script reads errorCode enum from OpenAPI spec
2. Compares all ERROR_EXAMPLES errorCode values against EBNF enum
3. **Exits with error** if mismatch found

**Example Validation Output**:
```
Found 17 valid errorCode values in EBNF enum
All errorCode values in ERROR_EXAMPLES are valid
```

**Example Validation Failure**:
```
ERROR: Found errorCode values that don't match EBNF enum:
   - HTTP 400 (invalid_format): 'VALIDATION_FAILED'

Valid errorCode values from EBNF:
   - MISSING_REQUIRED_FIELD
   - INVALID_ONEOF
   - INVALID_FORMAT
   ...

Fix: Update ERROR_EXAMPLES dictionary to use valid EBNF errorCode values
```

---

## File Summary

| File | Purpose | Lines | Update Frequency |
|------|---------|-------|------------------|
| `data_dictionary/c2mapiv2-dd.ebnf` | Error schema definitions | 925-972 | When adding/removing errors |
| `scripts/active/add_response_examples.py` | OpenAPI spec examples | 90-173 | When adding/removing/changing examples |
| `scripts/active/add_error_responses_to_collection.js` | Postman collection examples | 16-120 | When adding/removing/changing examples |
| `scripts/active/ebnf_to_openapi_dynamic_v3.py` | HTTP error code mapping | 427-468 | When adding new HTTP status codes |

---

## Quick Reference Commands

```bash
# Regenerate OpenAPI spec (triggers validation)
make generate-openapi-spec-from-ebnf-dd

# Full rebuild with validation
make postman-instance-build-without-tests

# Check validation output
# Look for: "Found N valid errorCode values in EBNF enum"
#           "All errorCode values in ERROR_EXAMPLES are valid"
```

---

## Common Mistakes

1. **Adding errorCode to EBNF but forgetting examples**
   - Result: Validation passes, but no examples generated
   - Fix: Always update both scripts when adding errorCode

2. **Typo in errorCode value**
   - Result: Validation fails with clear error message
   - Fix: Check spelling matches EBNF exactly (case-sensitive)

3. **Updating only one script**
   - Result: OpenAPI spec has examples, but Postman collection doesn't (or vice versa)
   - Fix: Always update BOTH scripts (OpenAPI + Postman)

4. **Changing EBNF without regenerating**
   - Result: Old spec still in use
   - Fix: Always run `make generate-openapi-spec-from-ebnf-dd` after EBNF changes

---

## Best Practices

1. **Use descriptive errorCode names**: ALL_CAPS_WITH_UNDERSCORES
2. **Keep errorMessage human-readable**: Users see these messages
3. **Include context in errorDetails**: Help developers debug issues
4. **Use consistent errorType values**: ValidationError, AuthenticationError, etc.
5. **Add tracking IDs**: Format TRK-YYYYMMDD-XXXXXX for support correlation
6. **Test after changes**: Run full rebuild to verify everything works

---

## Support

For questions or issues with error schema maintenance:
- Review validation output for specific error messages
- Check `ERROR_SCHEMA_CHANGES_LOG.md` for implementation history
- Consult `CLAUDE.md` session history for troubleshooting guidance

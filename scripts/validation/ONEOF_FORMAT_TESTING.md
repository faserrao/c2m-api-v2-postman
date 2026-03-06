# oneOf Format Validation Testing

**Date Created**: March 5, 2026
**Purpose**: Determine whether Prism strict validation accepts primitive or tagged union formats for oneOf fields
**Issue**: ChatGPT raised concerns about potential mismatch between OpenAPI schema and Postman collection formats

---

## Background

### The Question

Our OpenAPI spec defines oneOf unions like:

```yaml
docSourceAll:
  oneOf:
    - $ref: '#/components/schemas/docSourceStandard'
    - $ref: '#/components/schemas/docSourceZipFile'
```

Where leaf types resolve to primitives through reference chains:

```yaml
documentIdSource:
  $ref: '#/components/schemas/documentId'

documentId:
  $ref: '#/components/schemas/id'

id:
  type: integer
```

### The Formats

**Primitive Format** (bare values):
```json
{
  "docSourceAll": 12345
}
```

**Tagged Union Format** (object wrappers):
```json
{
  "docSourceAll": {
    "documentId": 12345
  }
}
```

### The Issue

- Our `addRandomDataToRaw.js` script generates **tagged union format**
- OpenAPI schema uses **reference chains to primitives**
- ChatGPT suggested Prism strict validation might reject tagged format
- **We need to test which format(s) Prism actually accepts**

---

## Test Script

### Location

```
scripts/validation/test_oneof_formats.sh
```

### What It Tests

**14 comprehensive tests across 4 test suites:**

1. **docSourceAll (Document Source)** - 5 tests
   - Test 1: Primitive documentId (bare integer)
   - Test 2: Tagged documentId (object wrapper)
   - Test 3: Primitive url (bare string)
   - Test 4: Tagged url (object wrapper)
   - Test 5: Object requestId + filename (naturally an object)

2. **recipientAddressSource** - 3 tests
   - Test 6: Object format (single address)
   - Test 7: Primitive addressListId (bare string)
   - Test 8: Tagged addressListId (object wrapper)

3. **paymentDetails** - 3 tests
   - Test 9: Object format (credit card details)
   - Test 10: Primitive paymentMethodId (bare string)
   - Test 11: Tagged paymentMethodId (object wrapper)

4. **Invalid Formats** - 3 tests (expected to fail)
   - Test 12: Wrong primitive type
   - Test 13: Missing required field
   - Test 14: Empty object for oneOf

### Prerequisites

1. **Prism CLI** installed:
   ```bash
   npm install -g @stoplight/prism-cli
   ```

2. **OpenAPI spec** generated:
   ```bash
   make generate-openapi-spec-from-ebnf-dd
   ```

3. **jq** installed (JSON parsing):
   ```bash
   brew install jq
   ```

---

## Running The Tests

### Quick Run

```bash
./scripts/validation/test_oneof_formats.sh
```

### What It Does

1. **Checks prerequisites** (Prism, OpenAPI spec, curl, jq)
2. **Starts Prism** mock server on port 4010 in strict validation mode
3. **Runs 14 tests** sending different JSON formats
4. **Reports results** with color-coded pass/fail
5. **Prints conclusions** with recommendations
6. **Cleans up** (stops Prism) on exit

### Expected Output

```
========================================
  oneOf Format Validation Test Suite
========================================

=== Checking Prerequisites ===

✓ Prism CLI installed: 5.x.x
✓ OpenAPI spec found: openapi/c2mapiv2-openapi-spec-base.yaml
✓ curl available
✓ jq available

=== Starting Prism Mock Server ===

Starting Prism with strict validation...
Waiting for Prism to start...
✓ Prism started successfully (PID: 12345)

=== Test Suite 1: docSourceAll (Document Source) ===

[TEST 1] Primitive format: documentId as bare integer
✓ PASS - HTTP 200 (expected 200)
  Response: {"jobId":"12345","status":"submitted"}...

[TEST 2] Tagged union format: documentId in object wrapper
✓ PASS - HTTP 200 (expected 200)
  Response: {"jobId":"67890","status":"submitted"}...

...

=== Test Summary ===

Total Tests Run:    14
Tests Passed:       12
Tests Failed:       2

✓ ALL TESTS PASSED (or ✗ SOME TESTS FAILED)

=== Conclusions ===

Based on test results:

1. docSourceAll (Document Source):
   - Tests 1-5 show which formats Prism accepts
   - If both primitive and tagged pass: Schema allows both
   - If only tagged passes: Schema requires object wrapper
   - If only primitive passes: Schema expects bare values

2. recipientAddressSource:
   - Tests 6-8 compare object vs primitive formats
   - addressListId test shows if primitives are accepted

3. paymentDetails:
   - Tests 9-11 show payment variant handling
   - paymentMethodId test validates primitive vs tagged

4. Recommendations:
   - Review failed tests to understand Prism's expectations
   - Update oneOfFixtures in addRandomDataToRaw.js if needed
   - Document the official wire format based on results
   - Consider updating COLLECTION_GENERATION_ARCHITECTURE.md
```

---

## Interpreting Results

### Scenario A: Both Formats Pass

**If both primitive AND tagged formats pass all tests:**

- OpenAPI schema is flexible (accepts both formats)
- Our tagged union format is valid
- No changes needed to `addRandomDataToRaw.js`
- **Conclusion**: Current implementation is correct

### Scenario B: Only Tagged Format Passes

**If only tagged format passes (primitives fail):**

- OpenAPI schema requires object wrappers
- Our current implementation is correct
- Prism strict validation enforces object format
- **Conclusion**: Keep current `oneOfFixtures` as-is

### Scenario C: Only Primitive Format Passes

**If only primitive format passes (tagged fails):**

- OpenAPI schema expects bare values
- Our `addRandomDataToRaw.js` is generating WRONG format
- Need to update `oneOfFixtures` dictionary
- **Action Required**: Refactor oneOfFixtures to use primitives

**Changes needed** (if Scenario C):

```javascript
// OLD (tagged union format - lines 83-100)
const oneOfFixtures = {
    docSourceAll: [
        { "documentId": "<integer>" },  // ❌ Object wrapper
        { "url": "<string>" }           // ❌ Object wrapper
    ]
};

// NEW (primitive format)
const oneOfFixtures = {
    docSourceAll: [
        "<integer>",  // ✅ Bare integer (for documentId)
        "<string>"    // ✅ Bare string (for url)
    ]
};
```

### Scenario D: Mixed Results

**If some oneOf fields accept primitives and others require objects:**

- Schema is inconsistent (unlikely but possible)
- Need field-specific handling in `addRandomDataToRaw.js`
- **Action Required**: Create separate fixtures per field type

---

## Next Steps After Testing

### 1. Document Results

Create a findings document:

```bash
# Copy test output to file
./scripts/validation/test_oneof_formats.sh > test_results_$(date +%Y%m%d).txt 2>&1
```

### 2. Update Architecture Documentation

Add findings to `COLLECTION_GENERATION_ARCHITECTURE.md`:

```markdown
## oneOf Format Decision (March 5, 2026)

**Test Results**: [Scenario A/B/C/D from above]

**Prism Validation**:
- Primitive format: [PASS/FAIL]
- Tagged union format: [PASS/FAIL]

**Decision**: [Keep current format / Refactor to primitives / Mixed approach]

**Rationale**: [Explain why based on test results]
```

### 3. Update Generator Scripts (If Needed)

If Scenario C (primitives only):

```bash
# Backup current script
cp scripts/test_data_generator_for_collections/addRandomDataToRaw.js \
   scripts/test_data_generator_for_collections/addRandomDataToRaw.js.backup-$(date +%Y%m%d)

# Edit oneOfFixtures dictionary (lines 83-100)
# Change from tagged format to primitive format
```

### 4. Re-run Full Pipeline

After any changes:

```bash
make postman-cleanup-all
make postman-instance-build-without-tests
```

### 5. Test Against Real API

If Click2Mail API V2 backend exists:

```bash
# Test primitive format
curl -X POST https://api.click2mail.com/v2/jobs/submit/single/doc \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"docSourceAll": 12345, "recipientAddressSource": {...}}'

# Test tagged format
curl -X POST https://api.click2mail.com/v2/jobs/submit/single/doc \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"docSourceAll": {"documentId": 12345}, "recipientAddressSource": {...}}'
```

---

## Troubleshooting

### Prism Won't Start

```bash
# Check if port 4010 is in use
lsof -i :4010

# Kill process using port
lsof -ti:4010 | xargs kill -9

# Try again
./scripts/validation/test_oneof_formats.sh
```

### All Tests Fail with Connection Error

```bash
# Check Prism is running
ps aux | grep prism

# Check Prism log
tail -f /tmp/prism_test_oneof.log

# Verify OpenAPI spec is valid
prism mock openapi/c2mapiv2-openapi-spec-base.yaml --errors
```

### Tests Pass But Real API Fails

**Prism mock server is NOT the same as real API**

- Prism validates against OpenAPI schema
- Real API may have additional business logic
- Real API may have different validation rules
- **Always test against real API before final decision**

---

## Related Files

### Generator Scripts
- `scripts/test_data_generator_for_collections/addRandomDataToRaw.js` - Generates tagged union format
- `scripts/active/generate_getting_started_with_examples_from_test.py` - Uses faker-generated data

### oneOf Fixtures
```javascript
// Location: addRandomDataToRaw.js lines 83-100
const oneOfFixtures = {
    docSourceAll: [
        { "documentId": "<integer>" },
        { "url": "<string>" },
        { "requestId": "<integer>", "filename": "<string>" }
    ],
    recipientAddressSource: [
        // 4 variants
    ],
    paymentDetails: [
        // 6 variants
    ]
};
```

### OpenAPI Schema
```yaml
# Location: openapi/c2mapiv2-openapi-spec-base.yaml
docSourceAll:
  oneOf:
    - $ref: '#/components/schemas/docSourceStandard'
    - $ref: '#/components/schemas/docSourceZipFile'

docSourceStandard:
  oneOf:
    - $ref: '#/components/schemas/documentIdSource'
    - $ref: '#/components/schemas/requestIdSource'
    - $ref: '#/components/schemas/urlSource'
```

---

## References

- **ChatGPT Analysis**: Session from March 5, 2026 raising Prism strict validation concern
- **COLLECTION_GENERATION_ARCHITECTURE.md**: Lines 450-556 document oneOf processing
- **Commit 2cffe5d**: February 28 → March 2, 2026 - Refactored oneOf fixtures to use placeholders
- **March 2, 2026 Bug Fix**: Added `processBodyObject(value, fieldName);` at line 405 of addRandomDataToRaw.js

---

## Conclusion

This test suite provides **definitive answers** about which oneOf format(s) Prism strict validation accepts. Run the tests, interpret the results, and update the codebase accordingly.

**The goal**: Ensure our Postman collections use a format that:
1. ✅ Passes Prism strict validation
2. ✅ Matches OpenAPI schema expectations
3. ✅ Works with the real Click2Mail API V2 backend

**After testing**, document the decision in COLLECTION_GENERATION_ARCHITECTURE.md so future developers understand the rationale.

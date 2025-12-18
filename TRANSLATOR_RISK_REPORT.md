# Translator Risk Report
## C2M Jobs Submit API - EBNF → OpenAPI Translation Analysis

**Date**: 2025-12-17
**Analyst**: Claude Code
**EBNF Source**: `data_dictionary/c2mapiv2-dd.ebnf`
**Generated Spec**: `openapi/c2mapiv2-openapi-spec-base.yaml` (707 lines)
**Translator**: `scripts/active/ebnf_to_openapi_dynamic_v3.py`

---

## Executive Summary

Translation completed with **1 CRITICAL FAILURE** and **3 KNOWN RISKS** requiring mitigation.

- **Overall Status**: FAILED (broken schema reference)
- **Endpoint Schemas**: 8/8 generated successfully
- **Job List Specificity**: 3/4 correct (multiDocJobItem missing)
- **Document Source Scoping**: PASS (with nested oneOf caveat)
- **Payment Details**: PASS (Apple/Google Pay excluded as intended)
- **Tags Shape**: PASS (array of strings)

**Action Required**: Fix EBNF definition for `multiDocJobItem` before deployment.

---

## 1. CRITICAL FAILURE: Missing multiDocJobItem Schema

### What Failed
The OpenAPI spec contains a **broken reference** to `multiDocJobItem`:

```yaml
multiDocJobs:
  type: array
  items:
    $ref: '#/components/schemas/multiDocJobItem'  # BROKEN - schema doesn't exist
```

The schema `multiDocJobItem` is **referenced but not defined** anywhere in the generated spec.

### Why It Failed

**Root Cause**: EBNF inconsistency between commented and active sections

In `data_dictionary/c2mapiv2-dd.ebnf`:

**COMMENTED OUT** (lines 676-692):
```ebnf
(*
multiDocJobItem =
      [ jobTemplate ]
    + docSourceAll
    + recipientAddressSource ;
*)
```

**ACTIVE** (line 694):
```ebnf
multiDocJobs = { multiDocJobItem } ;  (* References undefined symbol *)
```

The old shared job item definitions were commented out during the refactor, but `multiDocJobs` still references the commented-out `multiDocJobItem`. The translator can't find the definition, so it creates a `$ref` to a non-existent schema.

### Impact

- **Severity**: CRITICAL (blocker for deployment)
- **Affected Endpoints**:
  - `POST /jobs/submit/multi/doc` - completely broken
  - OpenAPI validation will FAIL
  - Postman collection generation will FAIL or produce invalid requests
  - Mock server will reject requests to this endpoint

### What Refactor Fixed It

**Option A: Add Missing Definition** (Recommended)

Add the missing definition after line 693:

```ebnf
multiDocJobs = { multiDocJobItem } ;

multiDocJobItem =
      [ jobTemplate ]
    + docSourceAll
    + recipientAddressSource ;
```

This matches the pattern used for `multiZipJobItem` (line 710).

**Option B: Use Inline Definition**

Replace line 694 with:

```ebnf
multiDocJobs = { ([ jobTemplate ] + docSourceAll + recipientAddressSource) } ;
```

However, this is less readable and doesn't match the project's EBNF style.

**Recommendation**: Use Option A for consistency with existing patterns.

---

## 2. KNOWN RISK: Array minItems Constraint (Expected)

### Current Behavior

All job arrays translate to `type: array` with **no minItems constraint**:

```yaml
multiDocJobs:
  type: array
  items:
    $ref: '#/components/schemas/multiDocJobItem'
  # minItems: 1 is missing
```

Same issue for:
- `pdfSplitJobsWithAddress`
- `pdfSplitJobsNoAddress`
- `multiZipJobs`
- `documentsToMerge` (merge endpoint)
- `addressList` (inline address lists)

### Why This Occurs

EBNF grammar uses `{ item }` which means "zero or more" in standard EBNF. The translator correctly generates `type: array` but cannot infer `minItems: 1` from the grammar alone.

### Mitigation Status

**As Documented in Handoff Spec**: This is expected behavior.

**Mitigations**:
1. Endpoint-level comments document the "jobs[] must be non-empty" requirement
2. Server-side validation must enforce this
3. (Optional) Post-generation patching can add `minItems: 1` to specific arrays

**Risk Level**: LOW (documented, known limitation)

---

## 3. KNOWN RISK: Nested oneOf in docSourceAll

### Current Behavior

`docSourceAll` uses a **two-level oneOf structure**:

```yaml
docSourceAll:
  oneOf:
  - $ref: '#/components/schemas/docSourceStandard'
  - $ref: '#/components/schemas/docSourceZipFile'

docSourceStandard:
  oneOf:
  - $ref: '#/components/schemas/documentIdSource'
  - $ref: '#/components/schemas/requestIdSource'
  - $ref: '#/components/schemas/urlSource'

docSourceZipFile:
  oneOf:
  - $ref: '#/components/schemas/zipDocumentIdSource'
  - $ref: '#/components/schemas/zipRequestIdSource'
```

### Expected Behavior (Ideally)

Flat oneOf with all 5 primitives:

```yaml
docSourceAll:
  oneOf:
  - $ref: '#/components/schemas/documentIdSource'
  - $ref: '#/components/schemas/requestIdSource'
  - $ref: '#/components/schemas/urlSource'
  - $ref: '#/components/schemas/zipDocumentIdSource'
  - $ref: '#/components/schemas/zipRequestIdSource'
```

### Why This Occurs

The EBNF defines:

```ebnf
docSourceStandard = documentIdSource | requestIdSource | urlSource ;
docSourceZipFile  = zipDocumentIdSource | zipRequestIdSource ;
docSourceAll      = docSourceStandard | docSourceZipFile ;
```

The translator **correctly** follows the EBNF structure, creating intermediate schemas for `docSourceStandard` and `docSourceZipFile`.

### Impact

**Functional**: The nested oneOf is **semantically correct** and will work.

**Potential Issues**:
- Some OpenAPI validators may not handle nested oneOf well
- Some code generators might produce suboptimal types
- Request validation is slightly slower (two-level check vs flat)

### Mitigation

**Current State**: Acceptable for MVP.

**If Flattening Required**:

Refactor EBNF to eliminate intermediate scoping:

```ebnf
(* Scoped variants removed - direct primitive references only *)
docSourceAll =
      documentIdSource
    | requestIdSource
    | urlSource
    | zipDocumentIdSource
    | zipRequestIdSource ;
```

**Trade-off**: Loses semantic grouping (Standard vs Zip distinction in grammar).

**Risk Level**: LOW (functional, may need refinement for edge cases)

---

## 4. KNOWN RISK: tags Shape (Verified Correct)

### Current Behavior

```yaml
tags:
  type: array
  items:
    type: string
```

This generates JSON:

```json
{
  "tags": ["tag1", "tag2", "tag3"]
}
```

### Handoff Spec Concern

"Current model may generate `"tags": [ "a", "b" ]`. If API requires `"tags": { "tags": [...] }` then EBNF must be refactored."

### Verification

**EBNF Definition** (line 574-575):
```ebnf
tags = tagsList ;
tagsList = { string } ;
```

This correctly produces an array of strings, **NOT** a wrapper object.

If the API requires a wrapper object, the EBNF would need:

```ebnf
tags = tagsWrapper ;
tagsWrapper = tagsList ;
tagsList = { string } ;
```

### Risk Level

NO RISK - Current shape is correct per EBNF. Only refactor if API requirements change.

---

## 5. VALIDATION RESULTS: What Translated Correctly

### Endpoint Schemas (8/8)

All 8 endpoint request schemas generated successfully:

1. `submitSingleDocParams` - uses `docSourceAll` + `recipientAddressSource` ✓
2. `submitSinglePdfAddressCaptureParams` - uses `docSourceStandard`, no addresses ✓
3. `submitSinglePdfSplitParams` - uses `pdfSplitJobsWithAddress` ✓
4. `submitSinglePdfSplitAddressCaptureParams` - uses `pdfSplitJobsNoAddress` ✓
5. `submitMultiDocParams` - uses `multiDocJobs` (BROKEN ref) ✗
6. `submitMultiDocMergeParams` - uses `mergeDocumentSource` ✓
7. `submitMultiZipParams` - uses `multiZipJobs` ✓
8. `submitMultiZipAddressCaptureParams` - uses `zipDocumentSource` ✓

### Job List Specificity (3/4)

Job arrays are correctly differentiated:

- `pdfSplitJobsWithAddress` → array of `pdfSplitJobItemWithAddress` ✓
- `pdfSplitJobsNoAddress` → array of `pdfSplitJobItemNoAddress` ✓
- `multiZipJobs` → array of `multiZipJobItem` ✓
- `multiDocJobs` → array of `multiDocJobItem` (MISSING schema) ✗

**Job Item Schemas Generated**:

```yaml
pdfSplitJobItemWithAddress:
  type: object
  properties:
    startPage:
      $ref: '#/components/schemas/startPage'
    endPage:
      $ref: '#/components/schemas/endPage'
    recipientAddressSource:
      $ref: '#/components/schemas/recipientAddressSource'
  required:
  - startPage
  - endPage
  - recipientAddressSource

pdfSplitJobItemNoAddress:
  type: object
  properties:
    startPage:
      $ref: '#/components/schemas/startPage'
    endPage:
      $ref: '#/components/schemas/endPage'
  required:
  - startPage
  - endPage

multiZipJobItem:
  type: object
  properties:
    jobTemplate:
      $ref: '#/components/schemas/jobTemplate'
    docSourceZipFile:
      $ref: '#/components/schemas/docSourceZipFile'
    recipientAddressSource:
      $ref: '#/components/schemas/recipientAddressSource'
  required:
  - docSourceZipFile
  - recipientAddressSource
```

### Document Source Scoping

All 3 scoped variants generated successfully:

```yaml
docSourceStandard:
  oneOf:
  - $ref: '#/components/schemas/documentIdSource'
  - $ref: '#/components/schemas/requestIdSource'
  - $ref: '#/components/schemas/urlSource'

docSourceZipFile:
  oneOf:
  - $ref: '#/components/schemas/zipDocumentIdSource'
  - $ref: '#/components/schemas/zipRequestIdSource'

docSourceAll:
  oneOf:
  - $ref: '#/components/schemas/docSourceStandard'  # Nested oneOf
  - $ref: '#/components/schemas/docSourceZipFile'   # Nested oneOf
```

**Endpoints Using Scoped Variants**:
- `submitSingleDocParams` → `docSourceAll` (all 5 modes allowed) ✓
- `submitSinglePdfAddressCaptureParams` → `docSourceStandard` (3 modes only) ✓
- `submitSinglePdfSplitParams` → `docSourceStandard` (3 modes only) ✓
- `submitSinglePdfSplitAddressCaptureParams` → `docSourceStandard` (3 modes only) ✓
- `submitMultiZipAddressCaptureParams` → `zipDocumentSource` (2 modes only) ✓
- `multiZipJobItem` → `docSourceZipFile` (2 modes only) ✓

### Payment Details (Apple/Google Pay Excluded)

`paymentDetails` correctly excludes Apple Pay and Google Pay:

```yaml
paymentDetails:
  oneOf:
  - $ref: '#/components/schemas/creditCardPayment'
  - $ref: '#/components/schemas/invoicePayment'
  - $ref: '#/components/schemas/achPayment'
  - $ref: '#/components/schemas/userCreditPayment'
  # No applePay or googlePay variants
```

This matches the EBNF where Apple Pay and Google Pay are commented out (lines 727-728, 747-755, 856-902).

### Tags Shape

Correctly generates array of strings:

```yaml
tags:
  type: array
  items:
    type: string
```

---

## 6. Translator Behavior Analysis

### What the Translator Does Well

1. **Endpoint-Specific Job Arrays**: Correctly creates separate array types
2. **Document Source Scoping**: Preserves EBNF scoping structure
3. **Payment Variants**: Correctly handles oneOf with commented variants excluded
4. **Optional Fields**: Properly translates `[ field ]` to non-required properties
5. **Primitive Types**: Correctly maps string, integer, number
6. **oneOf Handling**: Creates named schemas for alternatives (after fix_openapi_oneOf_schemas.py)

### What the Translator Cannot Do

1. **Undefined Symbol Detection**: Does not fail when referencing undefined EBNF symbols
   - Creates broken $ref instead of erroring
2. **minItems Constraints**: Cannot infer "at least one" from grammar
3. **Flatten Nested Alternatives**: Preserves EBNF hierarchy (docSourceAll → docSourceStandard → primitives)
4. **Runtime Constraints**: Cannot encode "filename required only if..." logic

---

## 7. Required Actions

### IMMEDIATE (Blocker)

**Fix EBNF for multiDocJobItem**

Add definition after line 694 in `data_dictionary/c2mapiv2-dd.ebnf`:

```ebnf
multiDocJobs = { multiDocJobItem } ;

multiDocJobItem =
      [ jobTemplate ]
    + docSourceAll
    + recipientAddressSource ;

pdfSplitJobsWithAddress = { pdfSplitJobItemWithAddress } ;
```

### VERIFICATION STEPS

After fixing EBNF:

1. Regenerate OpenAPI spec:
   ```bash
   make generate-openapi-spec-from-ebnf-dd
   ```

2. Verify `multiDocJobItem` schema exists:
   ```bash
   grep "^    multiDocJobItem:" openapi/c2mapiv2-openapi-spec-base.yaml
   ```

3. Validate OpenAPI spec:
   ```bash
   make openapi-spec-lint
   ```

4. Check for broken references:
   ```bash
   grep -o '\$ref.*' openapi/c2mapiv2-openapi-spec-base.yaml | sort -u > refs.txt
   grep "^    [a-zA-Z].*:$" openapi/c2mapiv2-openapi-spec-base.yaml | sed 's/:$//' | sed 's/^    //' | sort -u > schemas.txt
   comm -23 <(cat refs.txt | sed "s/.*#\/components\/schemas\///" | sed "s/'$//" | sort -u) schemas.txt
   ```

### RECOMMENDED (Non-Blocking)

1. **Add minItems constraints** (post-generation patching or server validation)
2. **Consider flattening docSourceAll** (if nested oneOf causes issues)
3. **Add EBNF validation script** to CI/CD to catch undefined symbols

---

## 8. Summary

### Translation Quality: B- (Passing with Critical Fix Required)

**Strengths**:
- Endpoint schemas correctly structured
- Job list specificity preserved (3/4)
- Document source scoping working as designed
- Payment details correctly excludes Apple/Google Pay
- Tags shape correct

**Critical Weakness**:
- Missing `multiDocJobItem` schema definition (EBNF bug, not translator bug)

**Known Limitations** (As Expected):
- No minItems constraints (documented limitation)
- Nested oneOf for docSourceAll (faithful to EBNF structure)

### Recommendation

**DO NOT DEPLOY** until `multiDocJobItem` EBNF definition is added and spec regenerated.

After fix: **SAFE TO PROCEED** with standard mitigation strategies (server-side validation for minItems).

---

## Appendix: Files Analyzed

- **EBNF Source**: `data_dictionary/c2mapiv2-dd.ebnf` (904 lines)
- **Generated OpenAPI**: `openapi/c2mapiv2-openapi-spec-base.yaml` (707 lines)
- **Translator Script**: `scripts/active/ebnf_to_openapi_dynamic_v3.py`
- **Post-Processor**: `scripts/active/fix_openapi_oneOf_schemas.py`

## Appendix: Verification Commands Used

```bash
# Translation
make generate-openapi-spec-from-ebnf-dd

# Inspection
grep -E "^  submit.*Params:" openapi/c2mapiv2-openapi-spec-base.yaml
grep -n "multiDocJobs\|pdfSplitJobs\|docSource\|paymentDetails:" openapi/c2mapiv2-openapi-spec-base.yaml
grep -A 20 "^    paymentDetails:" openapi/c2mapiv2-openapi-spec-base.yaml
grep "^    multiDocJobItem:" openapi/c2mapiv2-openapi-spec-base.yaml
grep "\\$ref.*multiDocJobItem" openapi/c2mapiv2-openapi-spec-base.yaml

# EBNF verification
grep -n "multiDocJobItem" data_dictionary/c2mapiv2-dd.ebnf
```

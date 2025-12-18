# EBNF Data Dictionary Review Report
**Date**: 2025-12-18
**File**: `data_dictionary/c2mapiv2-dd.ebnf`
**Reviewer**: Claude Code

## Executive Summary

This report identifies inconsistencies between:
1. Comment descriptions of endpoint parameters
2. Actual EBNF parameter names used in endpoint definitions
3. If-then-else validation rules

**Critical Finding**: Parameter names in comments and validation rules frequently do NOT match the actual EBNF parameter names used in endpoint definitions. This creates confusion and potential implementation errors.

**Total Issues Found**: 47 issues across 8 endpoints

---

## Issue Categories

### Category 1: Parameter Name Mismatches (28 issues)
Comments and rules reference generic names (like `documentSource`, `jobs`) instead of the specific EBNF parameter names actually used (like `docSourceAll`, `multiDocJobs`).

### Category 2: Missing Data Type Descriptions (8 issues)
Comments don't explain WHAT each variant contains (e.g., "stored document ID" vs "uploaded file reference").

### Category 3: Incorrect Rule References (9 issues)
Validation rules reference wrong parameter names or wrong item types.

### Category 4: Unanswered Questions (1 issue)
Comment contains an unanswered technical question from team member.

### Category 5: Documentation Errors (1 issue)
Wrong technology name in comment (Apple Pay instead of Google Pay).

---

## Detailed Findings by Endpoint

---

## ENDPOINT 1: POST /jobs/submit/single/doc

**Lines**: 177-241

### Issues Found: 8

#### Issue 1.1: Parameter name mismatch in comment
- **Line**: 182
- **Current**: "Body MUST include documentSource"
- **EBNF uses**: `docSourceAll` (line 236)
- **Problem**: Comment uses generic name `documentSource`, EBNF uses specific name `docSourceAll`
- **Recommendation**: Change to "Body MUST include `docSourceAll` (document source)"

#### Issue 1.2: Missing data type descriptions
- **Lines**: 184-190
- **Current**: Lists variant names only (documentId, requestIdSource, etc.)
- **Problem**: Doesn't explain WHAT each variant represents
- **Recommendation**: Add descriptions:
  ```
  docSourceAll can be:
    - documentIdSource (documentId): References a stored document by ID
    - requestIdSource (requestId + [filename]): References an uploaded file from a previous upload request
    - urlSource (url): URL to fetch document from external source
    - zipDocumentIdSource (zipDocumentId + filename): References a file within a stored zip archive
    - zipRequestIdSource (requestId + zipFilename + filename): References a file within an uploaded zip archive
  ```

#### Issue 1.3: Unanswered technical question
- **Line**: 191
- **Current**: "*** Mahesh: Can this endpoint be called with zipDocumentIdSource and zipRequestIdSource??"
- **Problem**: Question left unanswered
- **Analysis**: YES, endpoint CAN accept zip sources because:
  - Line 236: Uses `docSourceAll`
  - Line 656: `docSourceAll = docSourceStandard | docSourceZipFile`
  - Line 655: `docSourceZipFile = zipDocumentIdSource | zipRequestIdSource`
- **Recommendation**: Answer question with: "Yes. docSourceAll includes docSourceZipFile which contains both zip variants."

#### Issue 1.4-1.8: Validation rules use wrong parameter name (5 instances)
- **Lines**: 198, 200, 206, 207, 212
- **Current**: "IF documentSource is documentIdSource", "ELSE IF documentSource is requestIdSource", etc.
- **EBNF uses**: `docSourceAll` (line 236)
- **Problem**: Rules reference `documentSource` instead of `docSourceAll`
- **Recommendation**: Change all instances to "IF docSourceAll is documentIdSource", "ELSE IF docSourceAll is requestIdSource", etc.

---

## ENDPOINT 2: POST /jobs/submit/single/pdf/addressCapture

**Lines**: 243-277

### Issues Found: 4

#### Issue 2.1: Parameter name mismatch in comment
- **Line**: 248
- **Current**: "Body MUST include documentSource"
- **EBNF uses**: `docSourceStandard` (line 273)
- **Problem**: Comment uses generic name, EBNF uses restricted variant
- **Recommendation**: Change to "Body MUST include `docSourceStandard` (document source - non-zip variants only)"

#### Issue 2.2: Missing data type description
- **Line**: 248
- **Current**: No explanation of what docSourceStandard contains
- **Recommendation**: Add: "docSourceStandard can be: documentIdSource, requestIdSource, or urlSource (zip sources not allowed for this endpoint)"

#### Issue 2.3: Rule uses wrong parameter name
- **Line**: 259
- **Current**: "Apply the same documentSource resolution rules"
- **EBNF uses**: `docSourceStandard` (line 273)
- **Recommendation**: Change to "Apply the same docSourceStandard resolution rules"

#### Issue 2.4: Missing negative constraint explanation
- **Lines**: 254-256
- **Current**: Comments say "does NOT include recipientAddressSource"
- **Problem**: Doesn't explain WHY or what the alternative is
- **Recommendation**: Add: "Addresses are captured via OCR/address extraction workflow after document upload, not provided in request body"

---

## ENDPOINT 3: POST /jobs/submit/single/pdf/split

**Lines**: 279-320

### Issues Found: 10

#### Issue 3.1: Parameter name mismatch in comment
- **Line**: 284
- **Current**: "Body MUST include documentSource (the PDF to split)"
- **EBNF uses**: `docSourceStandard` (line 315)
- **Recommendation**: Change to "Body MUST include `docSourceStandard` (the PDF to split)"

#### Issue 3.2: Parameter name mismatch in comment
- **Line**: 285
- **Current**: "Body MUST include jobs (list of split instructions)"
- **EBNF uses**: `pdfSplitJobsWithAddress` (line 316)
- **Problem**: Comment uses generic name `jobs`, EBNF uses specific name
- **Recommendation**: Change to "Body MUST include `pdfSplitJobsWithAddress` (list of page ranges with recipient addresses)"

#### Issue 3.3: Missing data type description
- **Lines**: 286-287
- **Current**: "each jobs[] entry SHOULD include: startPage + endPage + recipientAddressSource"
- **Problem**: Uses wrong array name and doesn't explain item type
- **Recommendation**: Change to "each `pdfSplitJobsWithAddress[]` entry is a `pdfSplitJobItemWithAddress` containing: startPage (integer) + endPage (integer) + recipientAddressSource (address reference)"

#### Issue 3.4: Rule uses wrong parameter name
- **Line**: 292
- **Current**: "Resolve documentSource."
- **EBNF uses**: `docSourceStandard`
- **Recommendation**: Change to "Resolve docSourceStandard."

#### Issue 3.5-3.8: Validation rules use wrong array name (4 instances)
- **Lines**: 297, 298, 301, 302
- **Current**: "IF jobs missing", "jobs has 0 entries", "FOR EACH jobs[i]", "IF jobs[i]..."
- **EBNF uses**: `pdfSplitJobsWithAddress`
- **Recommendation**: Change all to "pdfSplitJobsWithAddress"

#### Issue 3.9: Rule uses wrong item type name
- **Line**: 302
- **Current**: "IF jobs[i] is not a pdfSplitJobItem shape"
- **EBNF uses**: `pdfSplitJobItemWithAddress` (line 704)
- **Problem**: Generic type name instead of specific variant
- **Recommendation**: Change to "IF pdfSplitJobsWithAddress[i] is not a pdfSplitJobItemWithAddress shape"

#### Issue 3.10: Incorrect rejection message
- **Line**: 303
- **Current**: "THEN reject (multiDocJobItem not allowed on this endpoint)."
- **Problem**: Should explain what IS allowed, not just what isn't
- **Recommendation**: Change to "THEN reject (only pdfSplitJobItemWithAddress allowed; multiDocJobItem and pdfSplitJobItemNoAddress not allowed)."

---

## ENDPOINT 4: POST /jobs/submit/single/pdf/split/addressCapture

**Lines**: 322-364

### Issues Found: 8

#### Issue 4.1: Parameter name mismatch in comment
- **Line**: 328
- **Current**: "Body MUST include documentSource"
- **EBNF uses**: `docSourceStandard` (line 359)
- **Recommendation**: Change to "Body MUST include `docSourceStandard`"

#### Issue 4.2: Parameter name mismatch in comment
- **Line**: 329
- **Current**: "Body MUST include jobs (list of page ranges)"
- **EBNF uses**: `pdfSplitJobsNoAddress` (line 360)
- **Recommendation**: Change to "Body MUST include `pdfSplitJobsNoAddress` (list of page ranges without addresses)"

#### Issue 4.3: Wrong array name in comment
- **Lines**: 330-332
- **Current**: "each jobs[] entry SHOULD include: startPage + endPage"
- **EBNF uses**: `pdfSplitJobsNoAddress`
- **Recommendation**: Change to "each `pdfSplitJobsNoAddress[]` entry is a `pdfSplitJobItemNoAddress` containing: startPage (integer) + endPage (integer)"

#### Issue 4.4: Rule uses wrong parameter name
- **Line**: 341
- **Current**: "Resolve documentSource."
- **Recommendation**: Change to "Resolve docSourceStandard."

#### Issue 4.5-4.7: Validation rules use wrong array name (3 instances)
- **Lines**: 346, 347, 350
- **Current**: "IF jobs missing", "jobs has 0 entries", "FOR EACH jobs[i]"
- **Recommendation**: Change all to "pdfSplitJobsNoAddress"

#### Issue 4.8: Rule uses wrong item type name
- **Line**: 351
- **Current**: "IF jobs[i] is not a pdfSplitJobItem shape"
- **EBNF uses**: `pdfSplitJobItemNoAddress` (line 705)
- **Recommendation**: Change to "IF pdfSplitJobsNoAddress[i] is not a pdfSplitJobItemNoAddress shape"

---

## ENDPOINT 5: POST /jobs/submit/multi/doc

**Lines**: 367-406

### Issues Found: 5

#### Issue 5.1: Parameter name mismatch in comment
- **Line**: 373
- **Current**: "Body MUST include jobs (list of job items)"
- **EBNF uses**: `multiDocJobs` (line 404)
- **Recommendation**: Change to "Body MUST include `multiDocJobs` (list of job items)"

#### Issue 5.2: Wrong array name in comment
- **Lines**: 374-376
- **Current**: "Each jobs[] item SHOULD include..."
- **Recommendation**: Change to "Each `multiDocJobs[]` item is a `multiDocJobItem` containing..."

#### Issue 5.3-5.5: Validation rules use wrong array name (3 instances)
- **Lines**: 381, 382, 385, 398, 399
- **Current**: "IF jobs missing", "jobs has 0 entries", "FOR EACH jobs[i]"
- **Recommendation**: Change all to "multiDocJobs"

---

## ENDPOINT 6: POST /jobs/submit/multi/doc/merge

**Lines**: 409-448

### Issues Found: 0

**Status**: ✅ CORRECT

**Comments**: This endpoint correctly references parameter names and explains the relationship between `mergeDocumentSource` (the param name) and `documentsToMerge` (the array field within it). Good example to follow.

---

## ENDPOINT 7: POST /jobs/submit/multi/zip

**Lines**: 450-492

### Issues Found: 6

#### Issue 7.1: Parameter name mismatch in comment
- **Line**: 456
- **Current**: "Body MUST include jobs (list of job items)"
- **EBNF uses**: `multiZipJobs` (line 490)
- **Recommendation**: Change to "Body MUST include `multiZipJobs` (list of zip-sourced job items)"

#### Issue 7.2: Wrong array name in comment
- **Lines**: 457-458
- **Current**: "Each jobs[] item SHOULD include..."
- **Recommendation**: Change to "Each `multiZipJobs[]` item is a `multiZipJobItem` containing..."

#### Issue 7.3-7.5: Validation rules use wrong array name (3 instances)
- **Lines**: 463, 464, 467
- **Current**: "IF jobs missing", "jobs has 0 entries", "FOR EACH jobs[i]"
- **Recommendation**: Change all to "multiZipJobs"

#### Issue 7.6: Rule uses wrong item type name
- **Line**: 468
- **Current**: "IF jobs[i] is not a multiDocJobItem shape"
- **EBNF uses**: `multiZipJobItem` (line 715)
- **Problem**: References wrong item type - multiZipJobItem is NOT the same as multiDocJobItem
- **Recommendation**: Change to "IF multiZipJobs[i] is not a multiZipJobItem shape"

---

## ENDPOINT 8: POST /jobs/submit/multi/zip/addressCapture

**Lines**: 495-540

### Issues Found: 1

#### Issue 8.1: Ambiguous validation rule
- **Line**: 528
- **Current**: "IF request body includes jobs"
- **Problem**: Not specific enough - which jobs array?
- **Context**: This endpoint should NOT have ANY jobs array (single zip, not multi-job)
- **Recommendation**: Change to "IF request body includes multiDocJobs OR multiZipJobs OR pdfSplitJobsWithAddress OR pdfSplitJobsNoAddress (i.e., any jobs array)"

---

## Additional Issues Not Tied to Specific Endpoints

### Issue A.1: Obsolete commented code should be removed
- **Lines**: 676-692
- **Current**: Old commented definitions of `jobs`, `job`, `multiDocJobItem`, `pdfSplitJobItem`
- **Problem**: These are superseded by the new separate definitions (lines 694-715). Keeping both creates confusion.
- **Recommendation**: Remove lines 676-692 or add clear deprecation notice:
  ```
  (* DEPRECATED - DO NOT USE
     Old unified jobs definitions below have been replaced by endpoint-specific arrays:
     - multiDocJobs (line 694)
     - pdfSplitJobsWithAddress (line 701)
     - pdfSplitJobsNoAddress (line 702)
     - multiZipJobs (line 714)
  *)
  ```

### Issue A.2: Wrong technology name in comment
- **Line**: 858
- **Current**: "(* Apple Pay definitions intentionally commented out for initial testing *)"
- **Problem**: This is the GOOGLE PAY section, not Apple Pay
- **Recommendation**: Change to "(* Google Pay definitions intentionally commented out for initial testing *)"

---

## Summary of Recommendations by Priority

### Priority 1: CRITICAL - Fix parameter name mismatches
**Impact**: Implementation teams will use wrong field names
**Count**: 28 instances
**Action**: Replace generic names (`documentSource`, `jobs`) with specific EBNF names (`docSourceAll`, `multiDocJobs`, etc.)

### Priority 2: HIGH - Add data type descriptions
**Impact**: Developers won't understand what each variant contains
**Count**: 8 instances
**Action**: Add explanations of what each variant represents (stored doc, uploaded file, URL, zip file, etc.)

### Priority 3: MEDIUM - Fix validation rule references
**Impact**: Implementation code may check wrong fields
**Count**: 9 instances
**Action**: Update validation rules to reference correct parameter and item type names

### Priority 4: MEDIUM - Answer technical questions
**Impact**: Unclear requirements lead to implementation delays
**Count**: 1 instance
**Action**: Answer Mahesh's question about zip sources (yes, allowed via docSourceAll)

### Priority 5: LOW - Fix documentation errors
**Impact**: Minor confusion
**Count**: 2 instances
**Action**: Fix wrong technology name, remove obsolete code

---

## Recommended Process for Fixes

1. **Review this report** with the team to confirm recommendations
2. **Fix Priority 1 issues** first (parameter name consistency)
3. **Add Priority 2 descriptions** to help developers understand data types
4. **Update Priority 3 validation rules** to match corrected names
5. **Address Priority 4** by answering technical question
6. **Clean up Priority 5** documentation issues
7. **Regenerate OpenAPI spec** after fixes to ensure consistency
8. **Update any implementation code** that may have been written using incorrect field names

---

## Proposed Comment Template

For future endpoint additions, use this template to ensure consistency:

```ebnf
(* ------------------------------------------------------------------------- *)
(* Endpoint: POST /jobs/submit/[endpoint-path]                              *)
(* ------------------------------------------------------------------------- *)
(* English meaning:
   - Body MUST include `parameterName` (description).
     `parameterName` can be:
       - variantName1 (field1 + field2): Explanation of what this variant represents
       - variantName2 (field1): Explanation of what this variant represents
   - Body MAY include `optionalParam` (description).
*)
(* Decision / validation rules (implementation-required):
   Parameter validation (parameterName):
     IF parameterName is variantName1
       THEN [validation logic using correct field names from EBNF].
     ELSE IF parameterName is variantName2
       THEN [validation logic using correct field names from EBNF].
     ELSE reject (no supported parameterName variant).
*)
submitEndpointParams =
      [ optionalParam ]
    + parameterName
    + ... ;
```

---

## End of Report

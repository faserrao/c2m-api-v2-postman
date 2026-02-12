# documentSource Comment Replacements

**Analysis Date**: 2026-02-11
**Purpose**: Replace references to unused `documentSource` definition in EBNF comments

---

## Summary

`documentSource` is defined (line 659) but **never actually used** by any endpoint. All endpoints use specialized variants:
- `docSourceAll` - Used by multiDocJobItem (allows all 5 source types)
- `docSourceStandard` - Used by most single endpoints (non-zip only: documentId, requestId, url)
- `docSourceZipFile` - Used by multiZipJobItem (zip only: zipDocumentId, zipRequestId)

---

## Replacement Recommendations

### Line 88-90: EBNF Primer Example (Section 6: Alternatives)

**Current:**
```
   The vertical bar means "one of these alternatives".

     documentSource = documentIdSource | requestIdSource | urlSource ;

   Read as: documentSource can be provided in exactly one of these modes.
```

**Replace with:**
```
   The vertical bar means "one of these alternatives".

     docSourceStandard = documentIdSource | requestIdSource | urlSource ;

   Read as: docSourceStandard can be provided in exactly one of these modes.
```

**Reason**: This is just a teaching example for the "|" syntax. Use `docSourceStandard` since it's simpler (3 variants vs 5) and actually used in the endpoint definitions.

---

### Lines 122, 127: Primer Example (Section 8: Endpoint request bodies)

**Current:**
```
   This rule defines the JSON body shape for that endpoint. It is built from the
   shared building blocks (documentSource, recipientAddressSource, etc.).

   Example:
     submitSingleDocParams =
           [ jobTemplate ]
         + documentSource
         + recipientAddressSource
```

**Replace with:**
```
   This rule defines the JSON body shape for that endpoint. It is built from the
   shared building blocks (docSourceAll, recipientAddressSource, etc.).

   Example:
     submitSingleDocParams =
           [ jobTemplate ]
         + docSourceAll
         + recipientAddressSource
```

**Reason**: This matches the actual `submitSingleDocParams` definition (line 248-255). The real definition uses `docSourceAll`, not `documentSource`.

---

### Line 168: Conventions Section

**Current:**
```
   Conventions:
     - Endpoint param sets (submit...Params) represent the JSON request body shape for that endpoint.
     - Each 'Params' rule is composed from reusable building blocks (documentSource, recipientAddressSource, etc.).
```

**Replace with (Option A - Generic):**
```
   Conventions:
     - Endpoint param sets (submit...Params) represent the JSON request body shape for that endpoint.
     - Each 'Params' rule is composed from reusable building blocks (document source variants, recipientAddressSource, etc.).
```

**Replace with (Option B - Specific):**
```
   Conventions:
     - Endpoint param sets (submit...Params) represent the JSON request body shape for that endpoint.
     - Each 'Params' rule is composed from reusable building blocks (docSourceAll/docSourceStandard/docSourceZipFile, recipientAddressSource, etc.).
```

**Reason**: This is a general conventions statement. Option A is cleaner if you want to be generic. Option B is more precise about what's actually available.

**Recommendation**: Use Option A (simpler).

---

### Line 402: Multi-Doc Jobs Description

**Current:**
```
   - Body MAY include a top-level jobTemplate.
   - Body MUST include `multiDocJobs` (list of job items).
   - Each `multiDocJobs[]` item is a `multiDocJobItem` containing:
       [ jobTemplate ] + documentSource + recipientAddressSource
```

**Replace with:**
```
   - Body MAY include a top-level jobTemplate.
   - Body MUST include `multiDocJobs` (list of job items).
   - Each `multiDocJobs[]` item is a `multiDocJobItem` containing:
       [ jobTemplate ] + docSourceAll + recipientAddressSource
```

**Reason**: `multiDocJobItem` definition (line 696-699) actually uses `docSourceAll`, not `documentSource`.

---

### Line 427: Multi-Doc Decision Rules

**Current:**
```
   Document and recipient rules:
     FOR EACH multiDocJobs[i]:
       Resolve multiDocJobs[i].documentSource using the same rules as /single/doc.
```

**Replace with:**
```
   Document and recipient rules:
     FOR EACH multiDocJobs[i]:
       Resolve multiDocJobs[i].docSourceAll using the same rules as /single/doc.
```

**Reason**: `multiDocJobItem` uses `docSourceAll`, so the field will be named `docSourceAll` in the JSON, not `documentSource`.

---

### Line 492: Multi-Zip Jobs Description

**Current:**
```
   - Body MAY include jobTemplate.
   - Body MUST include `multiZipJobs` (list of zip-sourced job items).
   - Each `multiZipJobs[]` item is a `multiZipJobItem` containing:
       [ jobTemplate ] + documentSource + recipientAddressSource
```

**Replace with:**
```
   - Body MAY include jobTemplate.
   - Body MUST include `multiZipJobs` (list of zip-sourced job items).
   - Each `multiZipJobs[]` item is a `multiZipJobItem` containing:
       [ jobTemplate ] + docSourceZipFile + recipientAddressSource
```

**Reason**: `multiZipJobItem` definition (line 736) actually uses `docSourceZipFile`, not `documentSource`. This endpoint only accepts ZIP sources, not all document sources.

---

### Line 687: Translator Note

**Current:**
```
(* Translator note:
   - docSourceStandard/docSourceZipFile/docSourceAll are "scoped" documentSource variants used to keep
     endpoint schemas tight.
```

**Replace with:**
```
(* Translator note:
   - docSourceStandard/docSourceZipFile/docSourceAll are specialized document source variants used to keep
     endpoint schemas tight (only accepting the source types each endpoint supports).
```

**Reason**: This comment already correctly explains the relationship. Just clarify that these are the ACTUAL definitions used (not variants of something else). The unused `documentSource` definition can be deleted entirely.

---

## Optional: Update Definition Comment (Line 659)

If you decide to **keep** `documentSource` for documentation purposes:

**Add comment:**
```ebnf
(* documentSource: Base definition showing all 5 source types.
   NOTE: This is NOT used directly by any endpoint.
   Endpoints use specialized variants: docSourceStandard, docSourceZipFile, or docSourceAll *)
documentSource =
      documentIdSource
    | requestIdSource
    | urlSource
    | zipDocumentIdSource
    | zipRequestIdSource ;
```

If you decide to **delete** `documentSource`, no comment needed (just remove lines 659-664).

---

## Recommended Changes Summary

1. ✅ **Line 88**: Change `documentSource` → `docSourceStandard` (teaching example)
2. ✅ **Line 90**: Change `documentSource` → `docSourceStandard` (teaching example)
3. ✅ **Line 122**: Change `documentSource` → `docSourceAll` (matches actual definition)
4. ✅ **Line 127**: Change `documentSource` → `docSourceAll` (matches actual definition)
5. ✅ **Line 168**: Change `documentSource` → `document source variants` (generic statement)
6. ✅ **Line 402**: Change `documentSource` → `docSourceAll` (matches multiDocJobItem)
7. ✅ **Line 427**: Change `documentSource` → `docSourceAll` (matches multiDocJobItem)
8. ✅ **Line 492**: Change `documentSource` → `docSourceZipFile` (matches multiZipJobItem)
9. ✅ **Line 687**: Clarify as "specialized document source variants" (already mostly correct)

---

## Verification

After making these changes, verify:

```bash
# Should return 0 results (only the definition itself, if you keep it)
grep -n "documentSource[^A-Za-z]" data_dictionary/c2mapiv2-dd.ebnf | grep -v "^659:"

# Should show the definition is never used in any rule
grep "= .*documentSource" data_dictionary/c2mapiv2-dd.ebnf
```

---

## Decision Required

**Should we delete the `documentSource` definition entirely?**

**Option A: Delete it**
- Pros: Removes unused code, prevents confusion
- Cons: Loses documentation value (showing all 5 types in one place)

**Option B: Keep it with clear comment**
- Pros: Useful reference, shows complete picture
- Cons: Extra definition that serves no functional purpose

**My Recommendation**: Keep it with the clarifying comment (Option B), since it helps explain the concept before introducing the specialized variants.

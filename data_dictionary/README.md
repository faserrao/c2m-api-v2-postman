# C2M API V2 Data Dictionary & Permutation Generator

This directory contains the EBNF data dictionary (source of truth for the API) and tools for generating test data permutations.

## Files

### Core Data Dictionary
- **c2mapiv2-dd.ebnf** - EBNF data dictionary defining all 8 /jobs/submit/... endpoints
  - Source of truth for the entire API
  - Used by `ebnf_to_openapi_dynamic_v3.py` to generate OpenAPI spec
  - 930 lines defining request body structures

### Permutation Generator (Updated 2025-12-18)
- **generate_endpoint_permutations.py** - Interactive permutation generator
  - Generates all possible request body combinations for an endpoint
  - Uses itertools.product() for cartesian product
  - Prompts you to choose which endpoint to generate
  - Output: `permutations/<endpoint>.json`

- **generate_all_permutations.sh** - Batch script for all endpoints
  - Generates permutations for all 8 endpoints automatically
  - Creates summary with counts and file sizes
  - Faster than running interactive script 8 times

### Generated Permutations
- **permutations/** - Directory containing all generated test data
  - 8 JSON files (one per endpoint)
  - Total: 3,456 permutations across all endpoints
  - Used by `generate_use_case_collection_v2.py` for diverse examples

## Endpoint Structure

The EBNF defines 8 endpoints under POST /jobs/submit/...:

1. **submitSingleDocParams** - `/jobs/submit/single/doc`
   - 1,296 permutations
   - Components: docSourceAll, recipientAddressSource, jobTemplate, paymentDetails, returnAddress, jobOptions, tags

2. **submitSinglePdfAddressCaptureParams** - `/jobs/submit/single/pdf/addressCapture`
   - 288 permutations
   - Components: docSourceStandard, jobTemplate, paymentDetails, returnAddress, jobOptions, tags

3. **submitSinglePdfSplitParams** - `/jobs/submit/single/pdf/split`
   - 576 permutations
   - Components: docSourceStandard, pdfSplitJobsWithAddress, jobTemplate, paymentDetails, returnAddress, jobOptions, tags

4. **submitSinglePdfSplitAddressCaptureParams** - `/jobs/submit/single/pdf/split/addressCapture`
   - 576 permutations
   - Components: docSourceStandard, pdfSplitJobsNoAddress, jobTemplate, paymentDetails, returnAddress, jobOptions, tags

5. **submitMultiDocParams** - `/jobs/submit/multi/doc`
   - 72 permutations
   - Components: multiDocJobs, jobTemplate, paymentDetails, tags

6. **submitMultiDocMergeParams** - `/jobs/submit/multi/doc/merge`
   - 432 permutations
   - Components: mergeDocumentSource, recipientAddressSource, jobTemplate, paymentDetails, returnAddress, jobOptions, tags

7. **submitMultiZipParams** - `/jobs/submit/multi/zip`
   - 72 permutations
   - Components: multiZipJobs, jobTemplate, paymentDetails, tags

8. **submitMultiZipAddressCaptureParams** - `/jobs/submit/multi/zip/addressCapture`
   - 144 permutations
   - Components: zipDocumentSource, jobTemplate, paymentDetails, returnAddress, jobOptions, tags

## Usage

### Generate Permutations for One Endpoint
```bash
cd data_dictionary
python3 generate_endpoint_permutations.py
# Then select endpoint number (1-8)
```

### Generate Permutations for All Endpoints
```bash
cd data_dictionary
./generate_all_permutations.sh
```

### Use Permutations in Pipeline
The generated permutation files are used by:
- `scripts/active/generate_use_case_collection_v2.py` - Randomly selects 5 diverse examples per use case
- Makefile target: `generate-use-case-collection` - Incorporates permutations into build pipeline

## Component Variants

The permutation generator creates combinations from these component options:

### Document Sources (6 variants)
- documentId (stored document)
- url (external URL)
- requestId (uploaded file)
- requestId + filename (multi-file upload)
- zipDocumentId + filename (stored zip)
- requestId + zipFilename + filename (uploaded zip)

### Recipient Address Sources (3 variants)
- singleAddress (inline address object)
- addressList (array of addresses)
- addressListId (reference to stored list)

### Job Templates (3 variants)
- "legal_certified_mail"
- "invoice_batch"
- "newsletter_monthly"

### Payment Details (4 variants)
- creditCard (Visa, card number, CVV, expiration)
- invoice (invoice number, amount due)
- ach (routing number, account number, check digit)
- userCredit (amount, currency)

Note: Apple Pay and Google Pay are defined in EBNF but commented out for initial testing.

### Job Options (2 variants)
- Letter (First Class, B&W, Next Day)
- Postcard (Standard, Color, Same Day)

### Tags (3 variants)
- ["legal", "certified"]
- ["batch", "invoice"]
- ["campaign", "newsletter"]

## Permutation Math

Example calculation for submitSingleDocParams:
- 6 document sources × 3 recipient sources × 3 job templates × 4 payment methods × 2 job options × 3 tag sets = 1,296 permutations

The cartesian product creates all possible valid combinations, ensuring comprehensive test coverage.

## Archive

Old permutation generator and data dictionary versions are in:
- **ARCHIVE/data_dictionary.original-endpoints/** - Original endpoint structure (pre-refactor)
  - Old endpoint names: submitSingleDocWithTemplateParams, submitMultiDocWithTemplateParams, etc.
  - Kept for historical reference only

## Pipeline Integration

```
EBNF Data Dictionary (c2mapiv2-dd.ebnf)
    ↓
OpenAPI Spec Generation (ebnf_to_openapi_dynamic_v3.py)
    ↓
Permutation Generation (generate_endpoint_permutations.py)
    ↓
Use Case Collection (generate_use_case_collection_v2.py)
    ↓
Postman Collections with Diverse Examples
```

## Key Learnings

1. **Permutation explosion**: Small increases in component options create large increases in permutations
2. **Diversity selection**: Random sampling from permutations creates more varied examples than consecutive selection
3. **Component reuse**: Document sources, payment methods, and addresses are reused across endpoints
4. **Business rules**: Some combinations are mutually exclusive (e.g., jobTemplate + jobOptions) - enforced in test data generator

## Maintenance

When adding new endpoints:
1. Update `c2mapiv2-dd.ebnf` with new endpoint definition
2. Add endpoint to `get_endpoint_components()` in `generate_endpoint_permutations.py`
3. Add component options to `parse_component_options()` if new components introduced
4. Update `generate_all_permutations.sh` with new endpoint number and name
5. Run `./generate_all_permutations.sh` to regenerate all permutations
6. Commit both EBNF and permutation files to version control

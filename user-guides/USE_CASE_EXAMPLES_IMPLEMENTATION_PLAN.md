# Implementation Plan: Use Case Examples for Postman Collections

## Executive Summary

This implementation plan outlines the approach to enhance Postman's handling of oneOf schemas and create a developer-friendly use case collection. The goal is to enable Postman to display ALL oneOf variants as named examples and provide ready-to-run scenarios for each real-world use case.

## 1. Goals of This Task

### Primary Goals:
- Enable Postman to display ALL oneOf variants as named examples (not just one random variant)
- Create a curated "Use Case Collection" that maps natural language scenarios to specific endpoints
- Improve developer onboarding by providing ready-to-run examples for each real-world use case
- Maintain automation - no manual steps in the pipeline

### Secondary Goals:
- Preserve existing pipeline functionality
- Keep the raw OpenAPI-generated collection as technical reference
- Make it easy to add new use cases in the future

## 2. How It Will Be Accomplished

### Two-Pronged Approach:

1. **Enhanced Pipeline (Transformer Script)**
   - Create `extract_all_oneof_examples.py` script
   - Reads OpenAPI spec and Postman collection JSON
   - Extracts ALL examples from oneOf branches
   - Patches Postman collection to include multiple named examples per request
   - Integrates into Makefile after collection generation

2. **Curated Use Case Collection**
   - Create `generate_use_case_collection.py` script
   - Generates a separate collection organized by use cases
   - Each use case maps to specific endpoint + pre-populated payload
   - Includes follow-up requests (Get Job Details, Get Job Status)

## 3. Codebase Impact

### New Files:
```
scripts/active/
├── extract_all_oneof_examples.py    # Transformer for oneOf examples
├── generate_use_case_collection.py   # Curated collection generator
└── use_case_mappings.yaml           # Configuration file for use cases

postman/templates/
├── use_case_collection_template.json # Template for curated collection
└── example_payloads/                # Folder with JSON payload examples
    ├── legal_firm.json
    ├── company_invoice_batch.json
    ├── company_split_invoices.json
    ├── real_estate_agent.json
    ├── medical_agency.json
    ├── monthly_newsletters.json
    ├── reseller_merge_pdfs.json
    └── reseller_zip_pdfs.json
```

### Modified Files:
- `Makefile` - New targets and pipeline integration
- `postman/generated/` - Will contain both enhanced and curated collections
- Documentation files to explain the new approach

## 4. Risks and Mitigations

### Risk 1: Breaking Existing Pipeline
- **Mitigation**: Add new steps AFTER existing pipeline, don't modify current flow
- Keep transformer as optional enhancement (can be skipped if issues)

### Risk 2: Postman Import Limitations
- **Risk**: Postman might reject collections with too many examples
- **Mitigation**: Test with subset first, add pagination if needed

### Risk 3: Maintenance Burden
- **Risk**: Two collections to maintain (raw + curated)
- **Mitigation**: Generate curated collection from configuration file, not hardcoded

### Risk 4: OneOf Complexity
- **Risk**: Deeply nested oneOf schemas might not map cleanly
- **Mitigation**: Start with simple cases, add complexity incrementally

## 5. Potential Issues and Resolutions

### Issue 1: Postman Collection Format Changes
- **Resolution**: Version-lock openapi-to-postmanv2, test with multiple Postman versions

### Issue 2: Example Data Quality
- **Issue**: Generated examples might not be realistic
- **Resolution**: Use template system with realistic placeholder data

### Issue 3: Variable Handling
- **Issue**: {{jobId}} might not propagate between requests
- **Resolution**: Add collection-level variables and pre-request scripts

### Issue 4: Authentication in Examples
- **Issue**: JWT tokens in examples will expire
- **Resolution**: Use {{authToken}} variable, document token refresh process

## 6. Potential Deal Breakers

### Critical Checks:
1. ❓ **Postman API Limits**: Does Postman limit number of examples per request?
2. ❓ **Collection Size**: Is there a size limit for imported collections?
3. ❓ **Performance**: Will 100+ examples slow down Postman UI?
4. ❓ **Compatibility**: Does this work with both Postman desktop and web?

**Need to verify these before full implementation**

## 7. Code to Be Written

### 1. Extract All OneOf Examples Script (`extract_all_oneof_examples.py`):
```python
# Main functions needed:
- load_openapi_spec()
- load_postman_collection()
- extract_oneof_examples()
- map_use_cases_to_examples()
- patch_collection_with_examples()
- save_enhanced_collection()
```

### 2. Generate Use Case Collection Script (`generate_use_case_collection.py`):
```python
# Main functions needed:
- load_use_case_config()
- create_collection_structure()
- generate_submit_job_request()
- generate_follow_up_requests()
- add_pre_request_scripts()
- save_curated_collection()
```

### 3. Use Case Mappings Configuration (`use_case_mappings.yaml`):
```yaml
use_cases:
  legal_firm:
    name: "Legal Firm – Certified Letters"
    endpoint: "POST /jobs/single-doc"
    description: "Sending certified letters with copy to lawyer"
    payload_template: "legal_firm.json"
    oneOf_variant: "documentSourceWithUpload"
    
  company_invoice_batch:
    name: "Company #1 – Invoice Batch"
    endpoint: "POST /jobs/multi-doc"
    description: "Batch processing monthly invoices"
    payload_template: "company_invoice_batch.json"
    oneOf_variant: "documentSourceWithUploadAndZip"
    
  company_split_invoices:
    name: "Company #2 – Split Invoices"
    endpoint: "POST /jobs/single-pdf-split"
    description: "Split PDF with address capture"
    payload_template: "company_split_invoices.json"
    oneOf_variant: "documentId"
```

## 8. Makefile Changes

### New Targets:
```makefile
# Extract all oneOf examples into Postman collection
postman-extract-oneof-examples:
	@echo "📊 Extracting all oneOf examples..."
	$(VENV_PYTHON) scripts/active/extract_all_oneof_examples.py \
		$(C2MAPIV2_OPENAPI_SPEC) \
		$(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_CC)-test-collection.json \
		$(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_CC)-test-collection-enhanced.json

# Generate curated use case collection
postman-generate-use-case-collection:
	@echo "📚 Generating curated use case collection..."
	$(VENV_PYTHON) scripts/active/generate_use_case_collection.py \
		scripts/active/use_case_mappings.yaml \
		$(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_CC)-use-case-collection.json

# Upload both collections
postman-upload-all-collections: postman-upload-enhanced postman-upload-use-cases
```

### Pipeline Integration:
```makefile
# Modify existing target
postman-instance-build-and-test: \
	postman-collection-build-and-test \
	postman-extract-oneof-examples \
	postman-generate-use-case-collection \
	postman-upload-all-collections
```

## 9. Testing Plan

### Unit Tests:
- Test oneOf extraction logic
- Test use case mapping
- Test collection JSON generation

### Integration Tests:
- Import enhanced collection into Postman
- Verify all examples appear in UI
- Test variable propagation

### End-to-End Tests:
- Developer runs through each use case
- Verify mock responses work
- Test with real API endpoints

## 10. Documentation Updates

- Update `POSTMAN_USER_TESTING_GUIDE.md` with new collections
- Add section on choosing between raw vs curated collections
- Document how to add new use cases
- Update pipeline documentation

## 11. Implementation Phases

### Phase 1: Research & Prototype (1-2 days)
- Verify Postman limitations
- Build minimal POC with 1-2 use cases
- Test import/export cycle

### Phase 2: Core Implementation (3-5 days)
- Build transformer script
- Create curated collection generator
- Add Makefile integration

### Phase 3: Full Rollout (2-3 days)
- Generate all 8 use cases
- Test thoroughly
- Update documentation

### Phase 4: Future Enhancements (Ongoing)
- Add more use cases
- Build UI for use case selection
- Create automated tests

## 12. Use Case Details

### Complete List of Use Cases:
1. **Legal Firm – Certified Letters**
   - Endpoint: POST /jobs/single-doc
   - Features: Certified mail, copy to lawyer

2. **Company #1 – Invoice Batch**
   - Endpoint: POST /jobs/multi-doc
   - Features: Batch processing, monthly invoices

3. **Company #2 – Split Invoices**
   - Endpoint: POST /jobs/single-pdf-split
   - Features: PDF splitting, address capture

4. **Real Estate Agent – Postcards**
   - Endpoint: POST /jobs/single-doc
   - Features: Marketing postcards, bulk mailing

5. **Medical Agency – Reports + Boilerplate**
   - Endpoint: POST /jobs/multi-doc-merge
   - Features: Document merging, compliance

6. **Monthly Newsletters**
   - Endpoint: POST /jobs/single-doc
   - Features: Newsletter distribution

7. **Reseller #1 – Merge PDFs**
   - Endpoint: POST /jobs/multi-doc-merge
   - Features: PDF merging service

8. **Reseller #2 – Zip PDFs**
   - Endpoint: POST /jobs/multi-doc
   - Features: Zip file processing

## 13. Success Criteria

- [ ] All oneOf variants appear as named examples in Postman
- [ ] Curated collection has all 8 use cases with proper payloads
- [ ] Pipeline runs without manual intervention
- [ ] Documentation is clear for new developers
- [ ] Mock server returns appropriate responses for each use case
- [ ] Variables propagate correctly between requests
- [ ] Performance is acceptable (< 3s to load collection)

## 14. Next Steps

1. Verify Postman limitations (examples per request, collection size)
2. Build proof of concept with Legal Firm use case
3. Get approval on approach
4. Proceed with full implementation

---

*Created: December 2024*
*Author: C2M API Team*
*Status: Planning*
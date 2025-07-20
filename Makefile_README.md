
# 📘 Makefile Documentation for C2M API Automation

This Makefile automates key steps in the OpenAPI → Postman pipeline, including:
- Generating Postman collections from OpenAPI specs
- Uploading environments, collections, and mocks to Postman
- Linking collections to APIs
- Running tests via Newman

---

## 🔧 Variable Overview

### OpenAPI Variables
- `OPENAPI_SPEC`: Path to OpenAPI spec to use in operations
- `OPENAPI_FINAL_SPEC`: Current working OpenAPI file
- `OPENAPI_V2_SPEC`: Exported spec from EBNF
- `PREVIOUS_SPEC`: Temp file used for comparing spec versions

### Postman Variables
- `POSTMAN_API_KEY`: Your Postman API key
- `POSTMAN_WS`: Workspace ID
- `POSTMAN_API_UID_FILE`: File storing the API UID
- `COLLECTION_UID_FILE`: File storing the main collection UID
- `TEST_COLLECTION_UID_FILE`: File storing a test-only collection UID
- `ENV_UID_FILE`: File storing environment UID
- `MOCK_UID_FILE`: File storing mock server UID
- `MOCK_ENV_FILE`: Environment JSON file for upload
- `COLLECTION_RAW`: Generated collection JSON from OpenAPI
- `COLLECTION_FINAL`: Merged/enhanced collection JSON
- `OVERRIDE_JSON`: Overrides used in merging Postman collections
- `REPORT_HTML`: Newman test report path
- `MOCK_PAYLOAD_FILE`, `LINK_PAYLOAD_FILE`: Payloads for POST requests
- `MOCK_DEBUG_FILE`, `LINK_DEBUG_FILE`, `IMPORT_DEBUG_FILE`, `ENV_UPLOAD_DEBUG_FILE`: Response logs for debugging

### Scripts
- `EBNF_FILE`: Source EBNF definition file
- `EBNF_SCRIPT`: Script to convert EBNF to OpenAPI
- `MERGER`: Script used to merge Postman collections

### Misc
- `SPEC`: Alias for `OPENAPI_FINAL_SPEC`
- `BASE_URL`, `TOKEN`: Extracted from uploaded environment
- `DOCS_DIR`, `TEMPLATES_DIR`: Swagger or Redoc template directories

---

## 🚀 Common Targets

### 1. Generate and Upload for Testing
```bash
make postman-collection-upload-test
```

### 2. Upload Environment
```bash
make postman-env-create
make postman-env-upload
```

### 3. Create a Mock Server
```bash
make postman-mock-create
```

### 4. Full API Sync (Spec → Collection → Upload → Link)
```bash
make postman-sync
```

---

## 🧪 Testing & Debugging
- Newman tests: included in `test`, `mock-test`
- Mock server logs: `$(MOCK_DEBUG_FILE)`
- Collection link logs: `$(LINK_DEBUG_FILE)`

---

## 📝 Notes
- All temporary and persistent identifiers (UIDs) are saved in `postman/*.txt`
- Variables are centralized to simplify maintenance and path updates
- Works seamlessly with Postman v10 API structure

---

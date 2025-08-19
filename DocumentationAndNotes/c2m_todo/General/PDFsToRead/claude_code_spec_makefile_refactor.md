
# Claude Code Spec: Makefile Refactoring for Postman Automation

## Goal
Refactor the existing Makefile for Postman automation while ensuring that:
- Existing functionality remains intact.
- Repetitive patterns (e.g., headers, URLs, jq commands) are consolidated into variables.
- Debugging and error handling are improved.
- `jq` commands handle missing/null fields gracefully.

---

## Key Refactoring Rules

### 1. Standardize Header Variables
Define header variables in one place:
```makefile
POSTMAN_HEADER_API_KEY       := --header "X-Api-Key: $(POSTMAN_API_KEY)"
POSTMAN_HEADER_ACCEPT        := --header "Accept: application/vnd.api.v10+json"
POSTMAN_HEADER_CONTENT_TYPE  := --header "Content-Type: application/json"
POSTMAN_CURL_HEADERS         := $(POSTMAN_HEADER_API_KEY) $(POSTMAN_HEADER_ACCEPT) $(POSTMAN_HEADER_CONTENT_TYPE)
```
Replace repeated inline headers with `$(POSTMAN_CURL_HEADERS)` wherever possible.

---

### 2. URL Variables
Use a single base URL:
```makefile
POSTMAN_API_BASE_URL := https://api.getpostman.com
```
Define endpoint variables:
```makefile
POSTMAN_MOCKS_URL        := $(POSTMAN_API_BASE_URL)/mocks?workspace=$(POSTMAN_WS)
POSTMAN_COLLECTIONS_URL  := $(POSTMAN_API_BASE_URL)/collections?workspaceId=$(POSTMAN_WS)
POSTMAN_APIS_URL         := $(POSTMAN_API_BASE_URL)/apis?workspace=$(POSTMAN_WS)
POSTMAN_ENVIRONMENTS_URL := $(POSTMAN_API_BASE_URL)/environments?workspace=$(POSTMAN_WS)
POSTMAN_SPECS_URL        := $(POSTMAN_API_BASE_URL)/specs?workspaceId=$(POSTMAN_WS)
```
Use these variables instead of hardcoding URLs.

---

### 3. Add Safe jq Filters
When parsing lists:
```bash
jq -r '.mocks // [] | .[].id'
```
Replace all `.something[].id` with `.something // [] | .[].id` to avoid null iteration errors.

---

### 4. Debugging
For each resource type (mocks, collections, APIs, environments, specs), save the raw JSON to a debug file, e.g.:
```makefile
$(POSTMAN_DIR)/mocks-debug.json
$(POSTMAN_DIR)/collections-debug.json
```
Print debug variables such as `DEBUG: MOCKS=$(MOCKS)` after fetching resources.

---

### 5. Consistent Temporary Files
Use variables for temporary paths:
```makefile
COLLECTION_TMP_FILE := $(POSTMAN_GEN_DIR)/c2m.collection.tmp.json
```
Avoid hardcoding `.tmp` paths in multiple places.

---

### 6. Validation and Exit Codes
Ensure each target checks if the required files (e.g., `$(COLLECTION_RAW)`) exist.
Exit gracefully with a clear message if a required file or ID is missing.

---

### 7. Targets to Refactor
Refactor the following targets to use the new variables and patterns:
- `postman-cleanup-all`
- `postman-api-clean-trash`
- `postman-collections-clean`
- `postman-collection-upload`
- `postman-env-upload`
- `postman-mock-create`
- `postman-collection-link`
- `postman-api-import`
- `postman-api-full-publish`
- `postman-api-update`
- `postman-api-debug-*`

---

### 8. Additional Recommendations
- Add `.PHONY` declarations for all targets.
- Consider adding a **`postman-debug-all`** target:
  - Lists mocks, collections, APIs, environments, and specs with names and IDs.
  - Saves all raw responses for easy inspection.
- Keep refactoring incremental. Start with variables and `jq // []` safety, then move to more advanced cleanup.

---

## Deliverable Example
After refactoring, a target might look like this:
```makefile
.PHONY: postman-collections-clean
postman-collections-clean:
	@echo "🗑️ Fetching collections in workspace $(POSTMAN_WS)..."
	@COLLECTIONS=$$(curl --silent --location "$(POSTMAN_COLLECTIONS_URL)" 		$(POSTMAN_HEADER_API_KEY) | tee $(POSTMAN_DIR)/collections-debug.json | jq -r '.collections // [] | .[].uid'); 	echo "DEBUG: COLLECTIONS=$$COLLECTIONS"; 	if [ -z "$$COLLECTIONS" ]; then 		echo "   No collections found."; 	else 		for COL in $$COLLECTIONS; do 			echo "   🚮 Deleting collection $$COL..."; 			curl --silent --location --request DELETE "$(POSTMAN_API_BASE_URL)/collections/$$COL" 				$(POSTMAN_HEADER_API_KEY) || echo "⚠️ Failed to delete collection $$COL"; 		done; 	fi
```

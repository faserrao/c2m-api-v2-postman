# === VARIABLES ===

ENV_FILE        			:= postman/mock-env.json
OVERRIDE_JSON   			:= postman/custom/overrides.json
MOCK_URL_FILE   			:= postman/mock_url.txt
POSTMAN_API_UID_FILE 	:= postman/postman_api_uid.txt
REPORT_HTML 	 				:= postman/newman-report.html
DOCS_DIR 			 				:= docs
TEMPLATES_DIR  				:= docs/templates
COLLECTION_UID_FILE   := 
ENV_UID_FILE					:= postman/env_uid.txt

# Extract token from ENV_FILE
TOKEN_RAW       := $(shell jq -r '.values[] | select(.key=="token") | .value' $(ENV_FILE) 2>/dev/null)
TOKEN           := $(if $(TOKEN_RAW),$(TOKEN_RAW),dummy-token)

# Extract baseUrl from ENV_FILE or use fallback/mock default
BASE_URL_RAW    := $(shell jq -r '.values[] | select(.key=="baseUrl") | .value' $(ENV_FILE) 2>/dev/null)
BASE_URL        := $(if $(BASE_URL_RAW),$(BASE_URL_RAW),https://mock.api)
MOCK_URL 				:= $(shell cat $(MOCK_URL_FILE) 2>/dev/null || echo "https://mock.api")

#C2M_OPENAPI_SPEC := openapi/c2m-api-v2-openapi-spec.yaml
#SPEC := $(C2M_OPENAPI_SPEC)
SPEC 					 := openapi/c2m_openapi_spec_final.yaml
PREVIOUS_SPEC := openapi/tmp_previous_spec.yaml
MAIN_SPEC_PATH := origin/main:$(SPEC)

COLL_RAW       := postman/generated/c2m.collection.json
# COLL_FINAL     :=
COLLECTION_FINAL := postman/generated/c2m.collection.merged.json
COLLECTION_RAW := postman/generated/c2m.collection.json
COLLECTION_MERGED := postman/generated/c2m.collection.merged.json
COLLECTION_FIXED := postman/generated/c2m.collection.fixed.json
COLLECTION_WITH_EXAMPLES := postman/generated/c2m.collection.with.examples.json
COLLECTION_WITH_TESTS    := postman/generated/c2m.collection.with.tests.json

PRISM_PORT     := 4010

POSTMAN 			 			:= postman
GENERATOR_OFFICIAL 	:= npx openapi-to-postmanv2
MERGER         			:= node scripts/merge-postman.js
PRISM          			:= npx @stoplight/prism-cli
NEWMAN         			:= npx newman
REDOCLY 			 			:= npx @redocly/cli
SPECTRAL 			 			:= npx @stoplight/spectral-cli
SWAGGER 			 			:= npx swagger-cli
WIDDERSHINS 	 			:= npx widdershins

POSTMAN_API_KEY 			:= PMAK-68778f2760d869000141987d-201b86a94c0d51d6159052abb42875a0b1
POSTMAN_API_NAME 			:= C2M API
MONITOR_NAME 					:= C2M API Hourly Monitor


# ============================
#         INSTALLATION
# ============================

.PHONY: install
install:
	brew install openapi-diff || echo "✅ openapi-diff already installed or handled"
	npm install \
	openapi-to-postmanv2 \
	@redocly/cli \
	@stoplight/spectral-cli \
	@stoplight/prism-cli \
	newman newman-reporter-html \
	swagger-ui-dist \
	swagger-cli widdershins lodash || echo "✅ npm packages installed or already available"


# --- Make sure to use constants for all hardcoded file and dir names. ---
# --- Generate Docs. ---
# --- Modify Collection to include Examples/Test Data ---
# --- Generate SDKs ---
# --- Naming Conventions ---
# --- Check the diff command for naming and constant names ---
# --- --data-binary @- | jq -r '.collection.uid'); \ ????


.PHONY: generate-openapi-spec-from-dd
generate-openapi-spec-from-dd:
	@echo "📤 Converting the EBNF Data Dictionary to an OpenAPI YAML Specifiction." 
	@echo "📤 Setting the Python Environemnt necessary to run the conversion utility." 
	source $(SCRIPTS_DIR)/python_env/e2o.venv/bin/activate
	@echo "📤 Installing required Python modules." 
	pip install -r $(SCRIPTS_DIR)/python_env/requirements.txt
	@echo "📤 Runnning Conversion Script: $(EBNF_SCRIPT_SHORT) on c2m-api-v2-dd.ebnf outputting: $(OPENAPI_V2_SPEC)" 
	python $(SCRIPTS_DIR)/$(EBNF_SCRIPT_SHORT) ./$(EBNF_FILE) ../$(OPENAPI_SPEC)


#============================
#         OPENAPI
# ============================

.PHONY: lint
lint:
	$(REDOCLY) lint $(SPEC)
	$(SPECTRAL) lint $(SPEC)


.PHONY: diff
diff:
	@echo "📤 Fetching latest from origin/main…"
	git fetch origin
	@echo "🧾 Checking out previous version of spec for diff comparison…"
	git show $(MAIN_SPEC_PATH) > $(PREVIOUS_SPEC)
	@echo "🔍 Running openapi-diff…"
	openapi-diff $(PREVIOUS_SPEC) $(SPEC) --fail-on-incompatible


.PHONY: clean-diff
clean-diff:
	rm -f $(PREVIOUS_SPEC)

# ============================
#        POSTMAN TASKS
# ============================


# === POSTMAN TARGETS ===

# --- LOGIN ---
.PHONY: postman-login postman-mock postman-env-create
.PHONY: postman-login
postman-login:
	@echo "🔐 Logging in to Postman..."
	@postman login --with-api-key $(POSTMAN_API_KEY)


# --- Import OpenAPI definition into Postman ---
.PHONY: postman-api-import
postman-api-import:
	@echo "📥 Importing OpenAPI definition $(SPEC) into Postman workspace $(POSTMAN_WS)..."
	@API_RESPONSE=$$(curl --location --request POST "https://api.getpostman.com/apis?workspaceId=$(POSTMAN_WS)" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Authorization: Bearer $(POSTMAN_API_KEY)" \
		--header "Accept: application/vnd.api.v10+json" \
		--header "Content-Type: application/json" \
		--data "$$(jq -Rs --arg name '$(POSTMAN_API_NAME)' '{ name: $$name, schema: { type: "openapi3", language: "yaml", schema: . }}' $(SPEC))"); \
		echo "$$API_RESPONSE" | jq . > postman/import-debug.json || echo "$$API_RESPONSE" > postman/import-debug.json; \
		API_ID=$$(echo "$$API_RESPONSE" | jq -r '.id // empty'); \
		if [ -z "$$API_ID" ]; then \
			echo "❌ Failed to import API. Check postman/import-debug.json for details."; \
			exit 1; \
		else \
			echo "✅ Imported API with ID: $$API_ID"; \
			echo "$$API_ID" > $(POSTMAN_API_UID_FILE); \
			echo "📄 API ID saved to $(POSTMAN_API_UID_FILE)"; \
		fi


# --- Generate Postman collection from OpenAPI spec ---
.PHONY: postman-collection-generate
postman-collection-generate:
	@echo "📦 Generating Postman collection from $(SPEC)..."
	$(GENERATOR_OFFICIAL) -s $(SPEC) -o $(COLL_RAW) -p
	@echo "✅ Collection written to $(COLL_RAW)"


.PHONY: postman-collection-fix
postman-collection-fix:
	@echo "🛠 Fixing collection to add 'info' block..."
	@jq '. as $$c | {info: {name: "C2M Test Collection", schema: "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"}, item: $$c.item}' \
		$(COLL_RAW) > postman/generated/c2m.collection.fixed.json
	@mv postman/generated/c2m.collection.fixed.json $(COLL_RAW)
	@echo "✅ Collection fixed and updated at $(COLL_RAW)"


# --- Upload Postman collection ---
.PHONY: postman-collection-upload
postman-collection-upload:
	@echo "📤 Uploading Postman collection $(COLL_RAW) to workspace $(POSTMAN_WS)..."
	@COLL_UID=$$(jq -c '{collection: .}' $(COLL_RAW) | \
		curl --silent --location --request POST "https://api.getpostman.com/collections?workspace=$(POSTMAN_WS)" \
			--header "X-Api-Key: $(POSTMAN_API_KEY)" \
			--header "Accept: application/vnd.api.v10+json" \
			--header "Content-Type: application/json" \
			--data-binary @- | jq -r '.collection.uid'); \
	if [ "$$COLL_UID" = "null" ] || [ -z "$$COLL_UID" ]; then \
		echo "❌ Failed to upload collection"; exit 1; \
	else \
		echo "✅ Collection uploaded with UID: $$COLL_UID"; \
		echo $$COLL_UID > postman/postman_collection_uid.txt; \
	fi


# --- Link collection to API version ---
.PHONY: postman-collection-link
postman-collection-link:
	@echo "🔗 Linking collection to API $(POSTMAN_API_NAME)..."
	@if [ ! -f $(POSTMAN_API_UID_FILE) ]; then \
		echo "❌ Missing API UID file: $(POSTMAN_API_UID_FILE). Run postman-api-import first."; exit 1; \
	fi
	@if [ ! -f postman/postman_collection_uid.txt ]; then \
		echo "❌ Missing collection UID file. Run postman-collection-upload first."; exit 1; \
	fi
	@API_ID=$$(cat $(POSTMAN_API_UID_FILE)); \
	COLL_UID=$$(cat postman/postman_collection_uid.txt); \
	echo "🔗 Copying and linking collection $$COLL_UID to API $$API_ID..."; \
	jq -n --arg coll "$$COLL_UID" '{operationType: "COPY_COLLECTION", data: {collectionId: $$coll}}' > postman/link-payload.json; \
	curl --location --request POST "https://api.getpostman.com/apis/$$API_ID/collections" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Authorization: Bearer $(POSTMAN_API_KEY)" \
		--header "Accept: application/vnd.api.v10+json" \
		--header "Content-Type: application/json" \
		--data-binary @postman/link-payload.json | tee postman/link-debug.json


# --- Merge Overrides (Safe Deep Merge) ---
.PHONY: postman-collection-merge-overrides
postman-collection-merge-overrides:
	@echo "🔀 Safely merging overrides from $(OVERRIDE_JSON) into $(COLLECTION_RAW)..."
	@if [ ! -f $(COLLECTION_RAW) ]; then \
		echo "❌ Base collection $(COLLECTION_RAW) not found. Run postman-collection-generate first."; \
		exit 1; \
	fi
	@if [ ! -f $(OVERRIDE_JSON) ]; then \
		echo "⚠️  No override file found at $(OVERRIDE_JSON). Skipping overrides."; \
		cp $(COLLECTION_RAW) $(COLLECTION_FINAL); \
		echo "✅ No overrides applied. Copied $(COLLECTION_RAW) to $(COLLECTION_FINAL)"; \
		exit 0; \
	fi
	@jq -s -f scripts/merge.jq $(COLLECTION_RAW) $(OVERRIDE_JSON) > $(COLLECTION_FINAL)
	@echo "✅ Safe deep merge completed. Output written to $(COLLECTION_FINAL)"


.PHONY: postman-collection-fix-merged
postman-collection-fix-merged:
	@echo "🛠 Fixing collection to add 'info' block..."
	@jq '. as $$c | {info: {name: "C2M Test Collection", schema: "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"}, item: $$c.item}' \
		$(COLLECTION_FINAL) > postman/generated/c2m.collection.fixed.json
	@mv postman/generated/c2m.collection.fixed.json $(COLLECTION_FINAL)
	@echo "✅ Collection fixed and updated at $(COLL)"


# --- Add Examples/Test Data ---
# --- Add Examples/Test Data ---
.PHONY: postman-collection-add-examples
postman-collection-add-examples:
	@echo "🧩 Adding smart example data to Postman collection..."
	@if [ ! -f $(COLLECTION_FINAL) ]; then \
		echo "⚠️  $(COLLECTION_FINAL) not found. Run postman-collection-merge-overrides first."; exit 1; \
	fi
	@python3 scripts/generate_test_data.py $(COLLECTION_FINAL) $(COLLECTION_WITH_EXAMPLES)
	@echo "✅ Examples added and saved to $(COLLECTION_WITH_EXAMPLES)"


.PHONY: postman-collection-validate
postman-collection-validate:
	@echo "🔍 Validating Postman collection $(COLLECTION_FINAL)..."
	@node -e "const { Collection } = require('postman-collection'); \
	const fs = require('fs'); \
	const file = '$(COLLECTION_FINAL)'; \
	const data = JSON.parse(fs.readFileSync(file, 'utf8')); \
	new Collection(data); \
	console.log('✅ Collection', file, 'is valid.');"


# --- Auto-fix invalid collection items ---
.PHONY: postman-collection-auto-fix
postman-collection-auto-fix:
	@echo "🛠 Auto-fixing invalid items in $(COLLECTION_WITH_EXAMPLES)..."
	@if [ ! -f $(COLLECTION_WITH_EXAMPLES) ]; then \
		echo "❌ Collection file not found: $(COLLECTION_WITH_EXAMPLES)"; \
		exit 1; \
	fi
	@jq 'walk( \
		if type == "object" and (has("name") and (has("request") | not) and (has("item") | not)) \
		then . + { "item": [] } \
		else . \
		end \
	)' $(COLLECTION_WITH_EXAMPLES) > $(COLLECTION_FIXED)
	@echo "✅ Auto-fix complete. Fixed collection saved to $(COLLECTION_FIXED)"
	@echo "🔍 Validating fixed collection..."
	@node -e "const {Collection}=require('postman-collection'); \
		const fs=require('fs'); \
		const data=JSON.parse(fs.readFileSync('$(COLLECTION_FIXED)','utf8')); \
		try { new Collection(data); console.log('✅ Collection is valid.'); } \
		catch(e) { console.error('❌ Validation failed:', e.message); process.exit(1); }"


# --- Add default Postman tests to every request ---
# --- Add default Postman tests to every request ---
.PHONY: postman-collection-add-tests
postman-collection-add-tests:
	@echo "🧪 Adding default Postman tests to collection with examples..."
	@if [ ! -f $(COLLECTION_WITH_EXAMPLES) ]; then \
		echo "⚠️  $(COLLECTION_WITH_EXAMPLES) not found. Run postman-collection-add-examples first."; exit 1; \
	fi
	jq --arg test1 'pm.test("Status code is 200", function () { pm.response.to.have.status(200); });' \
	   --arg test2 'pm.test("Response time < 1s", function () { pm.expect(pm.response.responseTime).to.be.below(1000); });' \
	   'def add_tests:
	    {
	        "event": [
	            {
	                "listen": "test",
	                "script": {
	                    "type": "text/javascript",
	                    "exec": [$$test1, $$test2]
	                }
	            }
	        ]
	    };
	    (.item[] | select(has("request")) | . += add_tests) |
	    (.item[] | select(has("item")) | .item[] | select(has("request")) | . += add_tests)
	   ' $(COLLECTION_WITH_EXAMPLES) > $(COLLECTION_WITH_TESTS)
	@echo "✅ Tests added to $(COLLECTION_WITH_TESTS)"


# --- Upload a collection for testing (unlinked) ---
.PHONY: postman-collection-upload-test
postman-collection-upload-test:
	@echo "===== DEBUG: Postman Collection Upload Test Variables ====="
	@echo "POSTMAN_API_KEY: $(POSTMAN_API_KEY)"
	@echo "POSTMAN_WS: $(POSTMAN_WS)"
	@echo "COLLECTION_FIXED: $(COLLECTION_FIXED)"
	@echo "==========================================================="
	@if [ ! -f $(COLLECTION_FIXED) ]; then \
		echo "⚠️  $(COLLECTION_FIXED) not found. Run postman-collection-auto-fix first."; exit 1; \
	fi
	@echo "📦 Using collection: $(COLLECTION_FIXED)"
	@RESPONSE=$$(jq -c '{collection: .}' $(COLLECTION_FIXED) | \
		curl --silent --location --request POST "https://api.getpostman.com/collections?workspace=$(POSTMAN_WS)" \
			--header "X-Api-Key: $(POSTMAN_API_KEY)" \
			--header "Accept: application/vnd.api.v10+json" \
			--header "Content-Type: application/json" \
			--data-binary @-); \
		echo "$$RESPONSE" | jq . > postman/upload-test-debug.json || echo "$$RESPONSE" > postman/upload-test-debug.json; \
		COLL_UID=$$(echo "$$RESPONSE" | jq -r '.collection.uid // empty'); \
		if [ -z "$$COLL_UID" ] || [ "$$COLL_UID" = "null" ]; then \
			echo "❌ Failed to upload test collection. Check postman/upload-test-debug.json for details."; \
			exit 1; \
		else \
			echo "✅ TEST Collection uploaded with UID: $$COLL_UID"; \
			echo $$COLL_UID > postman/postman_test_collection_uid.txt; \
			echo "📄 UID saved to postman/postman_test_collection_uid.txt"; \
		fi

# === Full Collection Build & Upload Test Pipeline ===
# === Full Collection Build & Upload Test Pipeline ===
.PHONY: postman-collection-build-test
postman-collection-build-test:
	@echo "🚀 Starting full collection build and upload pipeline with examples..."
	$(MAKE) postman-collection-generate
	$(MAKE) postman-collection-fix
	$(MAKE) postman-collection-merge-overrides
	$(MAKE) postman-collection-add-examples
	$(MAKE) postman-collection-auto-fix
	$(MAKE) postman-collection-upload-test
	@echo "✅ Postman test collection pipeline complete."


	# === Full Debug Pipeline: Generate → Fix → Merge → Auto-Fix → Upload Test ===
.PHONY: postman-collection-build-debug
postman-collection-build-debug:
	@echo "🚀 Starting full collection build and upload pipeline (DEBUG MODE)..."

	# Step 1: Generate collection
	$(MAKE) postman-collection-generate

	@echo "\n===== CONTENTS OF RAW COLLECTION ($(COLL_RAW)) ====="
	@cat $(COLL_RAW) | jq '.' | head -n 100 || true
	@echo "===================================================="

	# Step 2: Fix base collection (ensure 'info' block)
	$(MAKE) postman-collection-fix
	@echo "\n===== CONTENTS OF FIXED BASE COLLECTION ($(COLLECTION_FIXED_BASE)) ====="
	@cat $(COLLECTION_FIXED_BASE) | jq '.' | head -n 100 || true
	@echo "===================================================="

	# Step 3: Merge overrides
	$(MAKE) postman-collection-merge-overrides
	@echo "\n===== CONTENTS OF MERGED COLLECTION ($(COLLECTION_MERGED)) ====="
	@cat $(COLLECTION_MERGED) | jq '.' | head -n 100 || true
	@echo "===================================================="

	# Step 4: Auto-fix merged collection
	$(MAKE) postman-collection-auto-fix
	@echo "\n===== CONTENTS OF FIXED MERGED COLLECTION ($(COLLECTION_FIXED)) ====="
	@cat $(COLLECTION_FIXED) | jq '.' | head -n 100 || true
	@echo "===================================================="

	# Step 5: Diff between merged and fixed
	@echo "\n===== DIFF: Merged vs Fixed ====="
	@diff -u <(jq -S . $(COLLECTION_MERGED)) <(jq -S . $(COLLECTION_FIXED)) || true
	@echo "===================================================="

	# Step 6: Upload test collection
	$(MAKE) postman-collection-upload-test
	@echo "# === Combined Debug Pipeline Complete ==="






# === MOCK & TEST ===


# --- Create a Postman Mock Server (with optional environment) ---
.PHONY: postman-mock-create
postman-mock-create:
	@echo "🛠 Creating Postman mock server for collection..."
	@if [ ! -f postman/postman_test_collection_uid.txt ]; then \
		echo "❌ Missing test collection UID file: postman/postman_test_collection_uid.txt. Run postman-collection-upload-test first."; \
		exit 1; \
	fi; \
	COLL_UID=$$(cat postman/postman_test_collection_uid.txt); \
	MOCK_NAME="C2M API Mock - Test Collection"; \
	jq -n --arg coll "$$COLL_UID" --arg name "$$MOCK_NAME" \
		'{ mock: { collection: $$coll, name: $$name, private: false } }' \
		> postman/mock-payload.json; \
	curl --silent --location --request POST "https://api.getpostman.com/mocks" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Accept: application/vnd.api.v10+json" \
		--header "Content-Type: application/json" \
		--data-binary @postman/mock-payload.json \
		-o postman/mock-debug.json; \
	if ! jq -e '.mock.mockUrl' postman/mock-debug.json >/dev/null; then \
		echo "❌ Failed to find mockUrl in response. See postman/mock-debug.json"; \
		exit 1; \
	fi; \
	MOCK_URL=$$(jq -r '.mock.mockUrl' postman/mock-debug.json); \
	MOCK_UID=$$(jq -r '.mock.uid' postman/mock-debug.json | sed 's/^46321051-//'); \
	echo "✅ Mock server created at: $$MOCK_URL"; \
	echo "📄 Saving mock URL and UID..."; \
	echo "$$MOCK_URL" > $(MOCK_URL_FILE); \
	echo "$$MOCK_UID" > postman/postman_mock_uid.txt; \
	echo "📄 Mock server URL saved to $(MOCK_URL_FILE)"; \
	echo "📄 Mock UID saved to postman/postman_mock_uid.txt"




MOCK_UID_FILE   := postman/postman_mock_uid.txt
ENV_UID_FILE    := postman/postman_env_uid.txt
COLL_UID_FILE   := postman/postman_collection_uid.txt

API_KEY         := $(POSTMAN_API_KEY)
MOCK_UID        := $(shell cat $(MOCK_UID_FILE) 2>/dev/null || echo "")
ENV_UID         := $(shell cat $(ENV_UID_FILE))
COLL_UID        := $(shell cat $(COLL_UID_FILE))

sync-mock:
	@echo "🔍 Checking for existing mock UID..."
	@if [ -z "$(MOCK_UID)" ]; then \
		echo "⚠️  No mock UID found. Creating a new mock..."; \
		curl --silent --location --request POST "https://api.getpostman.com/mocks" \
			--header "x-api-key: $(API_KEY)" \
			--header "Content-Type: application/json" \
			--data-raw '{"mock": { "name": "Auto Mock", "collection": "$(COLL_UID)", "environment": "$(ENV_UID)", "private": false }}' \
			| jq -r '.mock.uid' > $(MOCK_UID_FILE); \
		echo "✅ Mock created. UID saved to $(MOCK_UID_FILE)."; \
	else \
		echo "✅ Found existing mock UID: $(MOCK_UID)."; \
	fi

	@echo "🔄 Updating Postman mock server environment..."
	curl --location --request PUT "https://api.getpostman.com/mocks/$(shell cat $(MOCK_UID_FILE))" \
		--header "x-api-key: $(API_KEY)" \
		--header "Content-Type: application/json" \
		--data-raw "{\"mock\": { \
			\"name\": \"Auto Mock\", \
			\"collection\": \"$(COLL_UID)\", \
			\"environment\": \"$(ENV_UID)\", \
			\"description\": \"Mock server updated via Makefile sync-mock.\", \
			\"private\": false \
		}}"

	@echo "\n📜 Retrieving final mock configuration..."
	curl --silent --location --request GET "https://api.getpostman.com/mocks/$(shell cat $(MOCK_UID_FILE))" \
		--header "x-api-key: $(API_KEY)" | jq '.mock'



# --- Generate Postman environment file from mock-url.txt ---
.PHONY: postman-env-create
postman-env-create:
	@echo "🧪 Generating Postman environment file …"
	@if [ ! -f $(MOCK_URL_FILE) ]; then \
	    echo '⚠️  mock_url.txt missing. Using fallback URL: $(MOCK_URL)'; fi
	@jq -n \
    --arg baseUrl "$(MOCK_URL)" \
    --arg token "$(TOKEN)" \
    '{ \
        "environment": { \
            "id": "c2m-env-id", \
            "name": "C2M Local Dev", \
            "values": [ \
                { "key": "baseUrl", "value": $$baseUrl, "enabled": true }, \
                { "key": "token", "value": $$token, "enabled": true } \
            ], \
            "_type": "environment" \
        } \
    }' > $(ENV_FILE)
	@echo "✅ Wrote $(ENV_FILE) with baseUrl=$(MOCK_URL)"


# --- Upload environment file to Postman ---
.PHONY: postman-env-upload
postman-env-upload:
	@echo "📤 Uploading Postman environment file to workspace $(POSTMAN_WS)..."
	@RESPONSE=$$(curl --silent --location --request POST "https://api.getpostman.com/environments?workspace=$(POSTMAN_WS)" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header 'Content-Type: application/json' \
		--data-binary '@$(ENV_FILE)'); \
	echo "$$RESPONSE" | jq . > postman/env-upload-debug.json || echo "$$RESPONSE" > postman/env-upload-debug.json; \
	ENV_UID=$$(echo "$$RESPONSE" | jq -r '.environment.uid // empty'); \
	if [ -z "$$ENV_UID" ]; then \
		echo "❌ Failed to upload environment. Check postman/env-upload-debug.json for details."; \
		exit 1; \
	else \
		echo "✅ Environment uploaded with UID: $$ENV_UID"; \
		echo $$ENV_UID > postman/postman_env_uid.txt; \
	fi


MOCK_ID        := $(shell cat postman/postman_mock_uid.txt)
ENV_UID        := $(shell cat postman/postman_env_uid.txt)
COLL_UID       := $(shell cat postman/postman_collection_uid.txt)
API_KEY        := $(POSTMAN_API_KEY)

update-mock-env:
	@echo "🔄 Updating Postman mock server environment..."
	curl --location --request PUT "https://api.getpostman.com/mocks/$(MOCK_ID)" \
		--header "x-api-key: $(API_KEY)" \
		--header "Content-Type: application/json" \
		--data-raw "{\"mock\": { \
			\"name\": \"Updated Mock Server\", \
			\"collection\": \"$(COLL_UID)\", \
			\"environment\": \"$(ENV_UID)\", \
			\"description\": \"Mock server environment updated via Makefile.\", \
			\"private\": false \
		}}"
	@echo "✅ Mock server environment updated."


MOCK_UID_FILE  := postman/postman_mock_uid.txt
API_KEY        := $(POSTMAN_API_KEY)
MOCK_UID       := $(shell cat $(MOCK_UID_FILE))

.PHONY: verify-mock
verify-mock:
	@echo "🔍 Fetching mock server details..."
	@curl --silent --location --request GET "https://api.getpostman.com/mocks/$(MOCK_UID)" \
		--header "x-api-key: $(API_KEY)" \
		| jq '{ \
			mockUrl: .mock.mockUrl, \
			name: .mock.name, \
			collection: .mock.collection, \
			environment: .mock.environment, \
			private: .mock.private, \
			updatedAt: .mock.updatedAt \
		}'


POSTMAN_API_UID_FILE := postman/postman_api_uid.txt
POSTMAN_API_VER_FILE := postman/postman_api_version.txt
POSTMAN_API_VERSION  := v1.0.0

.PHONY: postman-api-version
postman-api-version:
	@echo "📦 Setting version $(POSTMAN_API_VERSION) for Postman API..."
	@if [ ! -f $(POSTMAN_API_UID_FILE) ]; then \
		echo "❌ API UID not found: $(POSTMAN_API_UID_FILE). Run postman-api-create first."; \
		exit 1; \
	fi; \
	API_UID=$$(cat $(POSTMAN_API_UID_FILE)); \
	jq -n --arg ver "$(POSTMAN_API_VERSION)" \
		'{ version: { name: $$ver } }' > postman/postman-api-version-payload.json; \
	curl --silent --location --request POST "https://api.getpostman.com/apis/$$API_UID/versions" \
		--header "x-api-key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data-binary @postman/postman-api-version-payload.json \
		-o postman/postman-api-version-response.json; \
	if ! jq -e '.version.name' postman/postman-api-version-response.json >/dev/null; then \
		echo "❌ Failed to set API version. See postman/postman-api-version-response.json"; \
		exit 1; \
	fi; \
	VER_NAME=$$(jq -r '.version.name' postman/postman-api-version-response.json); \
	echo "$$VER_NAME" > $(POSTMAN_API_VER_FILE); \
	echo "✅ Version $$VER_NAME set for API $$API_UID"





POSTMAN_API_UID_FILE := postman/postman_api_uid.txt
POSTMAN_API_VER_FILE := postman/postman_api_version.txt
OPENAPI_SPEC_FILE    := openapi/c2m_openapi_spec_final.yaml

.PHONY: postman-api-spec
postman-api-spec:
	@echo "🚀 Uploading OpenAPI spec to existing Postman API..."
	@if [ ! -f $(OPENAPI_SPEC_FILE) ]; then \
		echo "❌ OpenAPI spec file not found: $(OPENAPI_SPEC_FILE)"; \
		exit 1; \
	fi; \
	if [ ! -f $(POSTMAN_API_UID_FILE) ]; then \
		echo "❌ API UID not found: $(POSTMAN_API_UID_FILE)"; \
		exit 1; \
	fi; \
	if [ ! -f $(POSTMAN_API_VER_FILE) ]; then \
		echo "❌ API version not found: $(POSTMAN_API_VER_FILE)"; \
		exit 1; \
	fi; \
	API_UID=$$(cat $(POSTMAN_API_UID_FILE)); \
	VER_NAME=$$(cat $(POSTMAN_API_VER_FILE)); \
	jq -n --arg lang "yaml" --rawfile spec $(OPENAPI_SPEC_FILE) \
		'{ spec: { language: $$lang, schema: $$spec } }' \
		> postman/postman-api-spec-payload.json; \
	curl --silent --location --request POST "https://api.getpostman.com/apis/$$API_UID/versions/$$VER_NAME/spec" \
		--header "x-api-key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data-binary @postman/postman-api-spec-payload.json \
		-o postman/postman-api-spec-response.json; \
	if ! jq -e '.spec' postman/postman-api-spec-response.json >/dev/null; then \
		echo "❌ Failed to upload spec. See postman/postman-api-spec-response.json"; \
		exit 1; \
	fi; \
	echo "✅ OpenAPI spec uploaded to Postman API $$API_UID (version $$VER_NAME)"










## Start Prism mock server
.PHONY: prism prism-stop postman-mock mock-test test
.PHONY: prism
prism:
	@echo "🚀 Starting Prism mock server on port $(PRISM_PORT)..."
	$(PRISM) mock $(SPEC) -p $(PRISM_PORT) &


## Kill Prism server if needed
.PHONY: prism-stop
prism-stop:
	@echo "🛑 Killing Prism on port $(PRISM_PORT)..."
	@lsof -ti tcp:$(PRISM_PORT) | xargs -r kill -9


## Run tests against Postman mock server
.PHONY: postman-mock
postman-mock:
	@echo "📤 Getting Postman mock URL from $(MOCK_URL_FILE)..."
	@echo "🔗 Using mock URL: $(MOCK_URL)"
	$(NEWMAN) run $(COLL_FINAL) \
		--env-var baseUrl=$(MOCK_URL) \
		--env-var token=$(TOKEN) \
		--reporters cli,html \
		--reporter-html-export $(REPORT_HTML)


## Run tests against Prism mock server
.PHONY: mock-test
mock-test: 
	@echo "🔬 Running Newman tests against Prism mock on port $(PRISM_PORT)..."
	@nc -z localhost $(PRISM_PORT) || (echo "❌ Prism not running on port $(PRISM_PORT)" && exit 1)
	$(NEWMAN) run $(COLL_FINAL) \
		--env-var baseUrl=http://localhost:$(PRISM_PORT) \
		--env-var token=$(TOKEN) \
		--reporters cli,html \
		--reporter-html-export $(REPORT_HTML)


# === DOCUMENTATION TARGETS ===
.PHONY: docs-build
docs-build:
	@echo "📚 Building API documentation with Redoc..."
	npx @redocly/cli build-docs $(SPEC) -o $(DOCS_DIR)/index.html
	npx swagger-cli bundle $(OPENAPI_FINAL_SPEC) --outfile openapi/bundled.yaml --type yaml



.PHONY: docs-serve
docs-serve:
	@echo "🌐 Serving API documentation locally on http://localhost:8080..."
	python3 -m http.server 8080 --directory $(DOCS_DIR)


.PHONY: postman-full-pipeline
postman-full-pipeline:
	@echo "🚀 Starting FULL Postman pipeline: Generate → Fix → Merge → Examples → Auto-Fix → Tests → Upload → Mock → Env..."
	$(MAKE) install
	$(MAKE) generate-openapi-spec-from-dd
	$(MAKE) lint
	$(MAKE) diff
	$(MAKE) postman-login
	$(MAKE) postman-api-import
#
#	$(MAKE) postman-api-version
#	$(MAKE) postman-api-spec
#
	$(MAKE) postman-collection-generate
	$(MAKE) postman-collection-fix
	$(MAKE) postman-collection-upload
	$(MAKE) postman-collection-link
#
	$(MAKE) postman-collection-generate
	$(MAKE) postman-collection-merge-overrides
	$(MAKE) postman-collection-add-examples
	$(MAKE) postman-collection-auto-fix
	$(MAKE) postman-collection-add-tests
	$(MAKE) postman-collection-upload-test
#
	$(MAKE) postman-mock-create
	$(MAKE) postman-env-create
	$(MAKE) postman-env-upload
	$(MAKE) update-mock-env 
#
	$(MAKE) prism
	$(MAKE) postman-mock
	$(MAKE) mock-test
#
	$(MAKE) docs-build
	$(MAKE) docs-serve
#
	@echo "✅ FULL Postman pipeline complete. Mock URL: $$(cat $(MOCK_URL_FILE))"



## Alias: default test target
test: mock-test

# ---------- DEFAULT -----------------------------------
.PHONY: all
all: install lint diff generate merge docs postman-env-create postman-mock


# ---------- HELP --------------------------------------
.PHONY: help
help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


.PHONY: postman-cleanup
postman-cleanup:
	@echo "🧹 Starting cleanup of Postman resources..."

	# --- Delete Mock Server ---
	@if [ -f postman/postman_mock_uid.txt ]; then \
		MOCK_UID=$$(cat postman/postman_mock_uid.txt); \
		echo "🗑 Deleting Mock Server: $$MOCK_UID..."; \
		curl --silent --location --request DELETE "https://api.getpostman.com/mocks/$$MOCK_UID" \
			--header "X-Api-Key: $(POSTMAN_API_KEY)" \
			--header "Accept: application/vnd.api.v10+json" \
			| tee postman/mock-delete-debug.json; \
		echo "✅ Mock server deleted."; \
	else \
		echo "⚠️  No mock UID found at postman/postman_mock_uid.txt"; \
	fi

	# --- Delete Environment ---
	@if [ -f postman/postman_env_uid.txt ]; then \
		ENV_UID=$$(cat postman/postman_env_uid.txt); \
		echo "🗑 Deleting Environment: $$ENV_UID..."; \
		curl --silent --location --request DELETE "https://api.getpostman.com/environments/$$ENV_UID" \
			--header "X-Api-Key: $(POSTMAN_API_KEY)" \
			--header "Accept: application/vnd.api.v10+json" \
			| tee postman/env-delete-debug.json; \
		echo "✅ Environment deleted."; \
	else \
		echo "⚠️  No environment UID found at postman/postman_env_uid.txt"; \
	fi

	# --- Delete Collection ---
	@if [ -f postman/postman_test_collection_uid.txt ]; then \
		COLL_UID=$$(cat postman/postman_test_collection_uid.txt); \
		echo "🗑 Deleting Collection: $$COLL_UID..."; \
		curl --silent --location --request DELETE "https://api.getpostman.com/collections/$$COLL_UID" \
			--header "X-Api-Key: $(POSTMAN_API_KEY)" \
			--header "Accept: application/vnd.api.v10+json" \
			| tee postman/collection-delete-debug.json; \
		echo "✅ Collection deleted."; \
	else \
		echo "⚠️  No collection UID found at postman/postman_test_collection_uid.txt"; \
	fi

	@echo "🎉 Cleanup complete."




.PHONY: postman-api-debug
postman-api-debug:
	@echo "🐞 Debugging Postman API import..."
	curl --verbose --location --request POST "https://api.getpostman.com/apis?workspace=$(POSTMAN_WS)" \
	--header "X-Api-Key: $(POSTMAN_API_KEY)" \
	--header "Authorization: Bearer $(POSTMAN_API_KEY)" \
	--header "Accept: application/vnd.api.v10+json" \
	--header "Content-Type: application/json" \
	--data "$$(jq -Rs --arg name '$(POSTMAN_API_NAME)' '{ api: { name: $$name, schema: { type: "openapi3", language: "yaml", schema: . }}}' $(SPEC))" \
	| tee postman/import-debug.json


.PHONY: postman-workspace-debug
postman-workspace-debug:
    @echo "🔍 Current Postman workspace ID: $(POSTMAN_WS)"



debug: postman-api-debug


all: postman-login postman-api-import postman-collection-generate postman-collection-upload postman-collection-link

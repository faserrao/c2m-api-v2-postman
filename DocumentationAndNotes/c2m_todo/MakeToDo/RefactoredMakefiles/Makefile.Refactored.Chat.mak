# === CONFIG ===

# Load local environment variables from .env if present
ifneq (,$(wildcard .env))
    include .env
    export $(shell sed 's/=.*//' .env)
endif


POSTMAN_API_NAME     			:= C2mApi

# === DIRECTORIES ===
SCRIPTS_DIR          			:= scripts
DOCS_DIR             			:= docs
OPENAPI_DIR          			:= openapi
DATA_DICT_DIR        			:= DataDictionary
POSTMAN_DIR          			:= postman
POSTMAN_GEN_DIR      			:= $(POSTMAN_DIR)/generated
POSTMAN_CUSTOM_DIR   			:= $(POSTMAN_DIR)/custom
TEMPLATES_DIR        			:= $(DOCS_DIR)/templates
PYTHON_ENV_DIR       			:= $(SCRIPTS_DIR)/python_env

# --- Files ---
EBNF_FILE            			:= $(DATA_DICT_DIR)/c2m-api-v2-dd.ebnf
MOCK_UID_FILE   					:= $(POSTMAN_DIR)/postman_mock_uid.txt
ENV_UID_FILE    					:= $(POSTMAN_DIR)/postman_env_uid.txt
COLL_UID_FILE   					:= $(POSTMAN_DIR)/postman_collection_uid.txt
POSTMAN_API_UID_FILE 			:= $(POSTMAN_DIR)/postman_api_uid.txt
POSTMAN_API_VER_FILE 			:= $(POSTMAN_DIR)/postman_api_version.txt
POSTMAN_SPEC_ID_FILE 			:= $(POSTMAN_DIR)/postman_spec_uid.txt
MOCK_URL_FILE_PRISM 			:= $(POSTMAN_DIR)/postman/mock-url-prism.txt
ENV_FILE             			:= $(POSTMAN_DIR)/mock-env.json
OVERRIDES_FILE						:= $(POSTMAN_CUSTOM_DIR)/overrides.json
POSTMAN_COLLECTION_UID_FILE := $(POSTMAN_DIR)/postman_collection_uid.txt

REPORT_HTML          			:= $(POSTMAN_DIR)/newman-report.html
PRISM_MOCK_URL      			:= $(shell cat $(MOCK_URL_FILE_PRISM) 2>/dev/null || echo "http://127.0.0.1t:$(PRISM_PORT)")

MOCK_UID        					:= $(shell cat $(MOCK_UID_FILE) 2>/dev/null || echo "")
ENV_UID         					:= $(shell cat $(ENV_UID_FILE))
COLL_UID									:= $(shell cat $(COLL_UID_FILE))


# === OPENAPI SPECS ===
MAIN_SPEC_PATH       			:= origin/main:$(OPENAPI_SPEC)
OPENAPI_SPEC         			:= $(OPENAPI_DIR)/c2m_openapi_spec_final.yaml
OPENAPI_SPEC_WITH_EXAMPLES		:= $(OPENAPI_DIR)/c2m_openapi_spec_final-with-examples.yaml
PREVIOUS_SPEC        			:= $(OPENAPI_DIR)/tmp_previous_spec.yaml

COLLECTION_RAW       			:= $(POSTMAN_GEN_DIR)/c2mapiv2-c2m-collection.json
COLLECTION_FIXED     			:= $(POSTMAN_GEN_DIR)/c2mapiv2-collection-fixed.json
COLLECTION_MERGED    			:= $(POSTMAN_GEN_DIR)/c2mapiv2-collection-merged.json
COLLECTION_TMP       			:= $(POSTMAN_GEN_DIR)/c2mapiv2-collection-tmp.json
COLLECTION_WITH_EXAMPLES 	:= $(POSTMAN_GEN_DIR)/c2mapiv2-collection-with-examples.json
COLLECTION_WITH_TESTS    	:= $(POSTMAN_GEN_DIR)/c2mapiv2-collection-with-tests.json

POSTMAN_IMPORT_DEBUG 			:= $(POSTMAN_DIR)/import-debug.json
POSTMAN_LINK_PAYLOAD 			:= $(POSTMAN_DIR)/link-payload.json
POSTMAN_LINK_DEBUG   			:= $(POSTMAN_DIR)/link-debug.json
POSTMAN_VERSION_PAYLOAD 	:= $(POSTMAN_DIR)/version-payload.json
POSTMAN_VERSION_DEBUG   	:= $(POSTMAN_DIR)/version-debug.json
POSTMAN_SCHEMA_UID_FILE 	:= $(POSTMAN_DIR)/schema_uid.txt

# === SCRIPTS ===
ADD_EXAMPLES_TO_OPENAPI_SPEC := $(SCRIPTS_DIR)/test_data_genertor_for_openapi_specs/add_examples_to_spec.py $(OPEN_API_SPEC)
MERGER               			:= node $(SCRIPTS_DIR)/merge-postman.js
FIX_PATHS_SCRIPT     			:= $(SCRIPTS_DIR)/fix_paths.jq
MERGE_SCRIPT         			:= $(SCRIPTS_DIR)/merge.jq
ADD_TESTS_SCRIPT     			:= $(SCRIPTS_DIR)/add_tests.jq
URL_HARDFIX_SCRIPT   			:= $(SCRIPTS_DIR)/url_hardfix.jq
EBNF_TO_OPENAPI_SCRIPT    := $(SCRIPTS_DIR)/ebnf_to_openapi_class_based.py

# === PYTHON VIRTUAL ENVIRONMENT ===
VENV_DIR             								:= $(PYTHON_ENV_DIR)/e2o.venv
VENV_PIP             								:= $(VENV_DIR)/bin/pip
VENV_PYTHON          								:= $(VENV_DIR)/bin/python
PYTHON3              								:= python3
INSTAALL_PYTHON_MODULES							:= install -r $(SCRIPTS_DIR)/python_env/requirements.txt
ADD_EXAMPLES_TO_COLLECTION_SCRIPT 	:= node $(SCRIPTS_DIR)/test_data_generator_for_collections/addRandomDataToRaw.js
ADD_EXAMPLES_TO_COLLECTION_ARGS 		:= --input  $(COLLECTION_RAW) --output $(COLLECTION_WITH_EXAMPLES) 
ADD_EXAMPLES_TO_COLLECTION					:= $(ADD_EXAMPLES_TO_COLLECTION_SCRIPT) $(ADD_EXAMPLES_TO_COLLECTION_ARGS)

PRISM_PORT   := 4010
BASE_URL_RAW 				 			:= $(shell [ -f $(ENV_FILE) ] && jq -r '.environment.values[] | select(.key=="baseUrl") | .value' $(ENV_FILE))
BASE_URL             			:= $(if $(BASE_URL_RAW),$(BASE_URL_RAW),https://mock.api)
MOCK_URL_FILE_POSTMAN 		:= $(POSTMAN_DIR)/mock_url.txt
MOCK_URL_FILE_PRISM  			:= $(POSTMAN_DIR)/prism_mock_url.txt
POSTMAN_MOCK_URL     			:= $(shell cat $(MOCK_URL_FILE_POSTMAN) 2>/dev/null || echo "https://mock.api")
PRISM_MOCK_URL       			:= $(shell cat $(MOCK_URL_FILE_PRISM)   2>/dev/null || echo "http://127.0.0.1:$(PRISM_PORT)")

# === TOOLS ===
GENERATOR_OFFICIAL   			:= npx openapi-to-postmanv2
PRISM                			:= npx @stoplight/prism-cli
NEWMAN               			:= npx newman
REDOCLY              			:= npx @redocly/cli
SPECTRAL             			:= npx @stoplight/spectral-cli
SWAGGER              			:= npx swagger-cli
WIDDERSHINS          			:= npx widdershins

# === Postman Workspaces ===
SERRAO_WS           			:= d8a1f479-a2aa-4471-869e-b12feea0a98c
C2M_WS										:= c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1
POSTMAN_WS           			:= $(SERRAO_WS)

# Postman API Keys
POSTMAN_API_KEY      			:= $(POSTMAN_SERRAO_API_KEY)
# POSTMAN_API_KEY      		:= $(POSTMAN_C2M_API_KEY)

# === TOKENS ===
TOKEN_RAW 					 			:= $(shell [ -f $(ENV_FILE) ] && jq -r '.environment.values[] | select(.key=="token") | .value' $(ENV_FILE))
TOKEN                			:= $(if $(TOKEN_RAW),$(TOKEN_RAW),dummy-token)
TOKEN               			:= dummy-token

PRISM_LOG_FILE        := $(POSTMAN_DIR)/prism.log
PRISM_HOST            := http://127.0.0.1
PRISM_PID_FILE        := $(POSTMAN_DIR)/prism.pid

# === Postman API Base ===
POSTMAN_API_BASE_URL := https://api.getpostman.com
POSTMAN_SPECS_URL    := $(POSTMAN_API_BASE_URL)/specs?workspaceId=$(POSTMAN_WS)
POSTMAN_APIS_URL     := $(POSTMAN_API_BASE_URL)/apis?workspaceId=$(POSTMAN_WS)
POSTMAN_COLLECTIONS_URL := $(POSTMAN_API_BASE_URL)/collections?workspace=$(POSTMAN_WS)
POSTMAN_SPEC_DELETE  := $(POSTMAN_API_BASE_URL)/specs

# === Headers ===
POSTMAN_HEADERS_JSON := \
	--header "X-Api-Key: $(POSTMAN_API_KEY)" \
	--header "Accept: application/vnd.api.v10+json" \
	--header "Content-Type: application/json"

POSTMAN_HEADERS_DEFAULT := \
	--header "X-Api-Key: $(POSTMAN_API_KEY)" \
	--header "Accept: application/vnd.api.v10+json"

# === Postman Payload & Response Files ===
POSTMAN_PAYLOAD_FULL_PUBLISH  := $(POSTMAN_DIR)/full-publish-payload.json
POSTMAN_RESPONSE_FULL_PUBLISH := $(POSTMAN_DIR)/api-full-publish-response.json
POSTMAN_PAYLOAD_UPDATE        := $(POSTMAN_DIR)/update-payload.json
POSTMAN_RESPONSE_UPDATE       := $(POSTMAN_DIR)/api-update-response.json
POSTMAN_COLLECTION_UID_FILE   := $(POSTMAN_DIR)/postman_collection_uid.txt

# === JQ Helpers ===
JQ_GET_ID     := jq -r '.id // empty'
JQ_GET_IDS    := jq -r '.data[].id'
JQ_COLLECTION_UPLOAD := jq -c '{collection: .}'

# Payload Generators (using external JQ files)
JQ_IMPORT_PAYLOAD = jq -Rs --arg name '$(POSTMAN_API_NAME)' -f $(SCRIPTS_DIR)/postman_import_payload.jq
JQ_FULL_PUBLISH_PAYLOAD = jq -n \
	--arg name "C2M Document Submission API" \
	--arg type "OPENAPI:3.0" \
	--arg path "index.yaml" \
	--arg content "$$(jq -Rs . < $(OPENAPI_SPEC))" \
	-f $(SCRIPTS_DIR)/full_publish_payload.jq

JQ_UPDATE_PAYLOAD = jq -n \
	--arg path "index.yaml" \
	--arg content "$$(jq -Rs . < $(OPENAPI_SPEC))" \
	-f $(SCRIPTS_DIR)/update_payload.jq

# === Temporary Files ===
COLLECTION_TMP_FILE := $(POSTMAN_GEN_DIR)/c2m.collection.tmp.json

POSTMAN_COLLECTION_LINK_URL     := $(POSTMAN_API_BASE_URL)/apis
POSTMAN_LINK_PAYLOAD            := $(POSTMAN_DIR)/link-payload.json
POSTMAN_LINK_DEBUG              := $(POSTMAN_DIR)/link-debug.json
JQ_LINK_PAYLOAD                 := jq -n --arg coll "$$COLL_UID" \
	'{operationType: "COPY_COLLECTION", data: {collectionId: $$coll}}'

# --- Postman Collection Linking ---
POSTMAN_LINK_PAYLOAD := $(POSTMAN_DIR)/link-payload.json
POSTMAN_LINK_DEBUG   := $(POSTMAN_DIR)/link-debug.json

# JQ payload for linking a collection to an API
JQ_LINK_PAYLOAD = jq -n --arg coll "$$COLL_UID" -f $(SCRIPTS_DIR)/link_payload.jq

COLLECTION_TESTING_TMP := $(POSTMAN_GEN_DIR)/c2m.testing.collection.tmp.json
JQ_ADD_TESTING_INFO    := jq -f $(SCRIPTS_DIR)/add_testing_info_block.jq

ADD_EXAMPLES_TO_COLLECTION_SCRIPT  := node $(SCRIPTS_DIR)/test_data_generator_for_collections/addRandomDataToRaw.js
ADD_EXAMPLES_TO_COLLECTION_ARGS    := --input $(COLLECTION_RAW) --output $(COLLECTION_WITH_EXAMPLES)
ADD_EXAMPLES_TO_COLLECTION         := $(ADD_EXAMPLES_TO_COLLECTION_SCRIPT) $(ADD_EXAMPLES_TO_COLLECTION_ARGS)

OVERRIDES_FILE       := $(POSTMAN_CUSTOM_DIR)/overrides.json
MERGE_SCRIPT         := $(SCRIPTS_DIR)/merge.jq

ADD_TESTS_SCRIPT := $(SCRIPTS_DIR)/add_tests.jq

AUTO_FIX_SCRIPT := $(SCRIPTS_DIR)/auto_fix_collection.jq

VALIDATE_COLLECTION_SCRIPT := $(SCRIPTS_DIR)/validate_collection.js

COLLECTION_FIXED_TMP := $(COLLECTION_FIXED).tmp


# --- Install and Validate ---
.PHONEY: postman-dd-to-openapi
postman-dd-to-openapi:
	$(MAKE) install
	$(MAKE) generate-openapi-spec-from-dd
	$(MAKE) lint


# --- Full Build Pipeline for Postman Collection and Testing ---
.PHONY: postman-collection-build-and-test
postman-collection-build-and-test:
	@echo "🚀 Starting Postman build and test..."

# --- Generate and Upload Collection (A) ---
	$(MAKE) postman-login
	$(MAKE) postman-api-import
	$(MAKE) postman-api-linked-collection-generate
	$(MAKE) postman-collection-upload
	$(MAKE) postman-collection-link

# ---	First-time publish (clean slate)
	$(MAKE) postman-api-full-publish

# --- Prepare Testing Collection (B) ---
	$(MAKE) postman-testing-collection-generate
	$(MAKE) postman-collection-add-examples || echo "⚠️  Skipping examples (optional step)."
	$(MAKE) postman-collection-merge-overrides
	$(MAKE) postman-collection-add-tests || echo "⚠️  Skipping adding tests (optional step)."


#	$(MAKE) postman-collection-url-hardfix
#	$(MAKE) postman-collection-repair-urls
#	$(MAKE) postman-collection-patch


	$(MAKE) postman-collection-auto-fix
	$(MAKE) postman-collection-fix-v2
	$(MAKE) postman-collection-validate

	$(MAKE) verify-urls
	$(MAKE) fix-urls
	$(MAKE) postman-collection-validate

	$(MAKE) postman-collection-upload-test

# --- Mock Server Creation and Environment (C) ---
	$(MAKE) postman-mock-create
	$(MAKE) postman-env-create
	$(MAKE) postman-env-upload
	$(MAKE) update-mock-env 
#	$(MAKE) postman-link-env-to-collection

# --- Run Tests (D) ---
	$(MAKE) prism-start
	$(MAKE) postman-mock

# --- Documentation Build ---
	$(MAKE) docs-build
	$(MAKE) docs

env-and-mock:
	$(MAKE) postman-mock-create
	$(MAKE) postman-env-create
	$(MAKE) postman-env-upload
	$(MAKE) update-mock-env 

	@echo "✅ Postman collection build and test completed: $(COLLECTION_MERGED)"


# --- Run Postman and Prism Tests ---
.PHONY: run-postman-and-prism-tests
run-postman-and-prism-tests:
	$(MAKE) prism-start
	$(MAKE) prism-mock-test
	$(MAKE) postman-mock


# Update existing spec with latest c2m_openapi_spec_final.yaml:
#	$(MAKE) postman-api-update

# List specs (for debugging)
# $(make) postman-api-list-specs

# Delete all but the most recent spec:
# $(MAKE) postman-api-delete-old-specs

# Debug workspace & API key:
# $(MAKE) postman-api-debug-B


# ============================
#         INSTALLATION
# ============================

.PHONY: postman-apis
postman-apis: ## List all Postman APIs
	@echo "Fetching APIs using POSTMAN_API_KEY..."
	curl --silent --location \
	--header "X-Api-Key: $(POSTMAN_API_KEY)" \
	"https://api.getpostman.com/apis" | jq .


check-mock:
	echo $(PRISM_MOCK_URL)


NPM_TOOLS := \
	openapi-to-postmanv2 \
	@redocly/cli \
	@stoplight/spectral-cli \
	@stoplight/prism-cli \
	newman newman-reporter-html \
	swagger-ui-dist \
	swagger-cli \
	widdershins \
	lodash


.PHONY: install
install:
	brew install openapi-diff || echo "✅ openapi-diff already installed or handled"
	npm install $(NPM_TOOLS) || echo "✅ npm packages installed or already available"


# --- Make sure to use constants for all hardcoded file and dir names. ---
# --- Generate Docs. ---
# --- Modify Collection to include Examples/Test Data ---
# --- Generate SDKs ---
# --- Naming Conventions ---
# --- Check the diff command for naming and constant names ---
# --- --data-binary @- | jq -r '.collection.uid'); \ ????


.PHONY: generate-openapi-spec-from-dd
generate-openapi-spec-from-dd:
	@echo "📤 Converting the EBNF Data Dictionary to an OpenAPI YAML Specification."

	# --- Validate required files and script ---
	@if [ ! -f $(EBNF_TO_OPENAPI_SCRIPT) ]; then \
		echo "❌ Script not found: $(EBNF_TO_OPENAPI_SCRIPT)"; exit 1; \
	fi
	@if [ ! -f $(EBNF_FILE) ]; then \
		echo "❌ EBNF Data Dictionary not found: $(EBNF_FILE)"; exit 1; \
	fi

	# --- Install Python dependencies ---
	@echo "📤 Installing required Python modules..."
	$(VENV_PIP) $(INSTAALL_PYTHON_MODULES)

	# --- Run the conversion script ---
	@echo "📤 Running Conversion Script: $(EBNF_TO_OPENAPI_SCRIPT) on $(EBNF_FILE) outputting: $(OPENAPI_SPEC)"
	$(VENV_PYTHON) $(EBNF_TO_OPENAPI_SCRIPT) -o $(OPENAPI_SPEC) $(EBNF_FILE) 


#============================
#         OPENAPI
# ============================

.PHONY: lint
lint:
	$(REDOCLY) lint $(OPENAPI_SPEC)
	$(SPECTRAL) lint $(OPENAPI_SPEC)


.PHONY: diff
diff:
	@echo "📤 Fetching latest from origin/main…"
	git fetch origin
	@echo "🧾 Checking out previous version of spec for diff comparison…"
	git show $(MAIN_SPEC_PATH) > $(PREVIOUS_SPEC)
	@echo "🔍 Running openapi-diff…"
	openapi-diff $(PREVIOUS_SPEC) $(OPENAPI_SPEC) --fail-on-incompatible


.PHONY: clean-diff
clean-diff:
	rm -f $(PREVIOUS_SPEC)

# ============================
#        POSTMAN TASKS
# ============================


# --- LOGIN ---
.PHONY: postman-login
postman-login:
	@echo "🔐 Logging in to Postman..."
	@postman login --with-api-key $(POSTMAN_API_KEY)


# Add this near other constants
PY_YAML_PACKAGE := PyYAML


# --- Fix PyYAML installation ---
.PHONY: fix-yaml
fix-yaml:
	@echo "🔧 Fixing PyYAML installation..."
	@echo "🧹 Removing any rogue 'yaml' package..."
	@$(VENV_PIP) uninstall -y yaml || true
	@echo "📦 Force reinstalling PyYAML..."
	@$(VENV_PIP) install --force-reinstall PyYAML
	@echo "🔍 Verifying PyYAML installation..."
	@$(VENV_PYTHON) -c "import yaml; print('✅ PyYAML import successful:', yaml.__version__)"


.PHONY: postman-api-import
postman-api-import:
	@echo "📥 Importing OpenAPI definition $(OPENAPI_SPEC) into Postman workspace $(POSTMAN_WS)..."
	@API_RESPONSE=$$(curl --location --request POST "$(POSTMAN_APIS_URL)" \
		$(POSTMAN_CURL_HEADERS) \
		--data "$$($(JQ_IMPORT_PAYLOAD) $(OPENAPI_SPEC))"); \
		echo "$$API_RESPONSE" | jq . > $(POSTMAN_IMPORT_DEBUG) || echo "$$API_RESPONSE" > $(POSTMAN_IMPORT_DEBUG); \
		API_ID=$$(echo "$$API_RESPONSE" | $(JQ_GET_ID)); \
		if [ -z "$$API_ID" ]; then \
			echo "❌ Failed to import API. Check $(POSTMAN_IMPORT_DEBUG) for details."; \
			exit 1; \
		else \
			echo "✅ Imported API with ID: $$API_ID"; \
			echo "$$API_ID" > $(POSTMAN_API_UID_FILE); \
			echo "📄 API ID saved to $(POSTMAN_API_UID_FILE)"; \


.PHONY: postman-api-full-publish
postman-api-full-publish:
	@echo "🚀 Starting full Postman Spec publish..."
	@SPECS=$$(curl --silent \
		$(POSTMAN_HEADER_API_KEY) \
		"$(POSTMAN_SPECS_URL)" \
		| $(JQ_GET_SPEC_IDS)); \
	if [ -n "$$SPECS" ]; then \
		echo "🧹 Deleting all existing specs in workspace $(POSTMAN_WS)..."; \
		for ID in $$SPECS; do \
			echo "   ➡️ Deleting spec $$ID..."; \
			curl --silent --location \
				--request DELETE \
				"$(POSTMAN_SPEC_DELETE)/$$ID" \
				$(POSTMAN_HEADER_API_KEY) \
				--header "Content-Type: application/json" | jq .; \
		done; \
	else \
		echo "ℹ️ No existing specs found. Skipping deletion."; \
	fi; \
	echo "🆕 Creating a fresh Postman Spec with $(OPENAPI_SPEC)..."; \
	$$( $(JQ_FULL_PUBLISH_PAYLOAD) ) > $(POSTMAN_FULL_PUBLISH_PAYLOAD); \
	curl --silent \
		--location \
		--request POST \
		"$(POSTMAN_SPECS_URL)" \
		$(POSTMAN_HEADER_API_KEY) \
		--header "Content-Type: application/json" \
		--data @$(POSTMAN_FULL_PUBLISH_PAYLOAD) \
		| tee $(POSTMAN_FULL_PUBLISH_RESPONSE) | jq .; \
	SPEC_ID=$$(jq -r '.id // empty' $(POSTMAN_FULL_PUBLISH_RESPONSE)); \
	if [ -z "$$SPEC_ID" ]; then \
		echo "❌ Failed to create a fresh spec. See $(POSTMAN_FULL_PUBLISH_RESPONSE)."; \
		exit 1; \
	else \
		echo "✅ Fresh spec created with ID: $$SPEC_ID"; \
		echo "$$SPEC_ID" > $(POSTMAN_SPEC_ID_FILE); \
	fi


.PHONY: postman-api-update
postman-api-update:
	@echo "🔄 Updating existing Postman Spec with latest $(OPENAPI_SPEC)..."
	@if [ ! -f $(POSTMAN_SPEC_ID_FILE) ]; then \
		echo "❌ Spec ID file ($(POSTMAN_SPEC_ID_FILE)) not found. Run make postman-api-full-publish first."; \
		exit 1; \
	fi; \
	SPEC_ID=$$(cat $(POSTMAN_SPEC_ID_FILE)); \
	echo "📄 Using Spec ID: $$SPEC_ID"; \
	$$( $(JQ_UPDATE_PAYLOAD) ) > $(POSTMAN_UPDATE_PAYLOAD); \
	curl --silent \
		--location \
		--request POST \
		"$(POSTMAN_API_BASE_URL)/specs/$$SPEC_ID/files" \
		$(POSTMAN_HEADER_API_KEY) \
		--header "Content-Type: application/json" \
		--data @$(POSTMAN_UPDATE_PAYLOAD) \
		| tee $(POSTMAN_UPDATE_RESPONSE) | jq .


.PHONY: postman-api-linked-collection-generate
postman-api-linked-collection-generate:
	@echo "📦 Generating Postman collection from $(OPENAPI_SPEC)..."
	$(GENERATOR_OFFICIAL) -s $(OPENAPI_SPEC) -o $(COLLECTION_RAW) -p
	@echo "🛠 Adding 'info' block to collection..."
	@jq '. as $$c | {info: {name: "C2M Collection Linked To API", schema: "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"}, item: $$c.item}' \
		$(COLLECTION_RAW) > $(COLLECTION_TMP_FILE)
	@mv $(COLLECTION_TMP_FILE) $(COLLECTION_RAW)
	@echo "✅ Collection generated with 'info' block at $(COLLECTION_RAW)"




# --- Upload Postman collection ---
.PHONY: postman-collection-upload
postman-collection-upload:
	@echo "📤 Uploading Postman collection $(COLLECTION_RAW) to workspace $(POSTMAN_WS)..."
	@COLL_UID=$$($(JQ_COLLECTION_UPLOAD) $(COLLECTION_RAW) | \
		curl --silent --location --request POST "$(POSTMAN_COLLECTIONS_URL)" \
			$(POSTMAN_HEADERS_JSON) \
			--data-binary @- | jq -r '.collection.uid'); \
	if [ "$$COLL_UID" = "null" ] || [ -z "$$COLL_UID" ]; then \
		echo "❌ Failed to upload collection"; \
		exit 1; \
	else \
		echo "✅ Collection uploaded with UID: $$COLL_UID"; \
		echo $$COLL_UID > $(POSTMAN_COLLECTION_UID_FILE); \
	fi


# --- Link collection to API version ---
.PHONY: postman-collection-link
postman-collection-link:
	@echo "🔗 Linking collection to API $(POSTMAN_API_NAME)..."
	@if [ ! -f $(POSTMAN_API_UID_FILE) ]; then \
		echo "❌ Missing API UID file: $(POSTMAN_API_UID_FILE). Run postman-api-import first."; \
		exit 1; \
	fi
	@if [ ! -f $(POSTMAN_COLLECTION_UID_FILE) ]; then \
		echo "❌ Missing collection UID file: $(POSTMAN_COLLECTION_UID_FILE). Run postman-collection-upload first."; \
		exit 1; \
	fi
	@API_ID=$$(cat $(POSTMAN_API_UID_FILE)); \
	COLL_UID=$$(cat $(POSTMAN_COLLECTION_UID_FILE)); \
	echo "🔗 Copying and linking collection $$COLL_UID to API $$API_ID..."; \
	$(JQ_LINK_PAYLOAD) > $(POSTMAN_LINK_PAYLOAD); \
	curl --location --request POST "$(POSTMAN_API_BASE_URL)/apis/$$API_ID/collections" \
		$(POSTMAN_CURL_HEADERS) \
		--data-binary @$(POSTMAN_LINK_PAYLOAD) | tee $(POSTMAN_LINK_DEBUG)


.PHONY: postman-testing-collection-generate
postman-testing-collection-generate:
	@echo "📦 Generating Postman testing collection from $(OPENAPI_SPEC)..."
	@echo "🛠 Adding 'info' block to collection..."
	@$(JQ_ADD_TESTING_INFO) $(COLLECTION_RAW) > $(COLLECTION_TESTING_TMP)
	@mv $(COLLECTION_TESTING_TMP) $(COLLECTION_RAW)
	@echo "✅ Collection generated with 'info' block at $(COLLECTION_RAW)"


.PHONY: postman-collection-add-examples
postman-collection-add-examples:
	@echo "📤 Installing required Python modules..."
	@echo "🧩 Adding smart example data to Postman collection..."
	@if [ ! -f $(COLLECTION_RAW) ]; then \
		echo "⚠️  $(COLLECTION_RAW) not found. Run postman-collection-merge-overrides first."; \
		exit 1; \
	fi
	$(ADD_EXAMPLES_TO_COLLECTION)
	@echo "✅ Examples added and saved to $(COLLECTION_WITH_EXAMPLES)"


# --- Merge Overrides (Safe Deep Merge) ---
.PHONY: postman-collection-merge-overrides
postman-collection-merge-overrides:
	@echo "🔀 Safely merging overrides from $(OVERRIDES_FILE) into $(COLLECTION_WITH_EXAMPLES)..."
	@if [ ! -f $(COLLECTION_WITH_EXAMPLES) ]; then \
		echo "❌ Base collection $(COLLECTION_WITH_EXAMPLES) not found. Run postman-collection-generate first."; \
		exit 1; \
	fi
	@if [ ! -f $(OVERRIDES_FILE) ]; then \
		echo "⚠️  No override file found at $(OVERRIDES_FILE). Skipping overrides."; \
		cp $(COLLECTION_RAW) $(COLLECTION_MERGED); \
		echo "✅ No overrides applied. Copied $(COLLECTION_RAW) to $(COLLECTION_MERGED)"; \
		exit 0; \
	fi
	@jq -s -f $(MERGE_SCRIPT) $(COLLECTION_WITH_EXAMPLES) $(OVERRIDES_FILE) > $(COLLECTION_MERGED)
	@echo "✅ Safe deep merge completed. Output written to $(COLLECTION_MERGED)"


.PHONY: postman-collection-add-tests
postman-collection-add-tests:
	@echo "🧪 Adding default Postman tests to collection with examples..."
	@if [ ! -f $(COLLECTION_MERGED) ]; then \
		echo "⚠️  $(COLLECTION_MERGED) not found. Run postman-collection-add-examples first."; \
		exit 1; \
	fi
	@jq \
	    --arg test1 'pm.test("Status code is 200", function () { pm.response.to.have.status(200); });' \
	    --arg test2 'pm.test("Response time < 1s", function () { pm.expect(pm.response.responseTime).to.be.below(1000); });' \
	    -f $(ADD_TESTS_SCRIPT) \
	    $(COLLECTION_MERGED) > $(COLLECTION_WITH_TESTS)
	@echo "✅ Tests added to $(COLLECTION_WITH_TESTS)"


# --- Auto-fix invalid collection items ---
.PHONY: postman-collection-auto-fix
postman-collection-auto-fix:
	@echo "🛠 Auto-fixing invalid items in $(COLLECTION_WITH_TESTS)..."
	@if [ ! -f $(COLLECTION_WITH_TESTS) ]; then \
		echo "❌ Collection file not found: $(COLLECTION_WITH_TESTS)"; \
		exit 1; \
	fi
	@jq -f $(AUTO_FIX_SCRIPT) $(COLLECTION_WITH_TESTS) > $(COLLECTION_FIXED)
	@echo "✅ Auto-fix complete. Fixed collection saved to $(COLLECTION_FIXED)"
	@echo "🔍 Validating fixed collection..."
	@node $(VALIDATE_COLLECTION_SCRIPT) $(COLLECTION_FIXED)


# Add this to your variables section
FIX_COLLECTION_URLS_SCRIPT := $(SCRIPTS_DIR)/fix_collection_urls.py

.PHONY: postman-collection-fix
postman-collection-fix:
	@echo "🔧 Fixing Postman collection URLs..."
	@$(PYTHON3) $(FIX_COLLECTION_URLS_SCRIPT) $(COLLECTION_FIXED) $(COLLECTION_FIXED)
	@echo "🎉 Collection fixed: $(COLLECTION_FIXED)"


# Add this in your variables section
FIX_COLLECTION_URLS_V2_SCRIPT := $(SCRIPTS_DIR)/fix_collection_urls_v2.py

.PHONY: postman-collection-fix-v2
postman-collection-fix-v2:
	@echo "🔧 Fixing collection URLs (v2) in $(COLLECTION_FIXED)..."
	@$(PYTHON3) $(FIX_COLLECTION_URLS_V2_SCRIPT) $(COLLECTION_FIXED) $(COLLECTION_FIXED)
	@echo "✅ Collection URLs fixed: $(COLLECTION_FIXED)"


# Add this to your variables section
URL_HARDFIX_WITH_PATHS_SCRIPT := $(SCRIPTS_DIR)/url_hardfix_with_paths.jq
COLLECTION_FIXED_TMP          := $(COLLECTION_FIXED).tmp


.PHONY: postman-collection-url-hardfix
postman-collection-url-hardfix:
	@echo "🔧 Applying combined path + URL hard fix..."
	@jq -f $(URL_HARDFIX_WITH_PATHS_SCRIPT) $(COLLECTION_FIXED) > $(COLLECTION_FIXED).tmp \
		&& mv $(COLLECTION_FIXED).tmp $(COLLECTION_FIXED)
	@echo "✅ Combined path and URL hard fix applied: $(COLLECTION_FIXED)"


REPAIR_URLS_SCRIPT := $(SCRIPTS_DIR)/repair_urls.py

.PHONY: postman-collection-repair-urls
postman-collection-repair-urls:
	@echo "🔧 Repairing URLs based on folder hierarchy..."
	@$(PYTHON3) $(REPAIR_URLS_SCRIPT) $(COLLECTION_FIXED)
	@echo "✅ Folder-based URL repair complete: $(COLLECTION_FIXED)"


VERIFY_URLS_SCRIPT := $(SCRIPTS_DIR)/verify_urls.jq

.PHONY: verify-urls
verify-urls:
	@echo "🔍 Verifying URLs in $(COLLECTION_FIXED)..."
	@jq -r -f $(VERIFY_URLS_SCRIPT) $(COLLECTION_FIXED)


FIX_URLS_SCRIPT       := $(SCRIPTS_DIR)/fix_urls.jq
COLLECTION_FIXED_TMP  := $(COLLECTION_FIXED).tmp

.PHONY: fix-urls
fix-urls:
	@echo "🔧 Fixing URLs in $(COLLECTION_FIXED)..."
	@jq -f $(FIX_URLS_SCRIPT) $(COLLECTION_FIXED) > $(COLLECTION_FIXED_TMP)
	@mv $(COLLECTION_FIXED_TMP) $(COLLECTION_FIXED)
	@echo "✅ URLs fixed in $(COLLECTION_FIXED)"


VALIDATE_COLLECTION_SCRIPT := $(SCRIPTS_DIR)/validate_collection.js

.PHONY: postman-collection-validate
postman-collection-validate:
	@echo "🔍 Validating Postman collection $(COLLECTION_FIXED)..."
	@node $(VALIDATE_COLLECTION_SCRIPT) $(COLLECTION_FIXED)


POSTMAN_COLLECTIONS_URL          := $(POSTMAN_API_BASE_URL)/collections?workspace=$(POSTMAN_WS)
POSTMAN_UPLOAD_TEST_DEBUG        := $(POSTMAN_DIR)/upload-test-debug.json
POSTMAN_TEST_COLLECTION_UID_FILE := $(POSTMAN_DIR)/postman_test_collection_uid.txt
JQ_COLLECTION_UPLOAD_FIXED       := jq -c '{collection: .}' $(COLLECTION_FIXED)

.PHONY: postman-collection-upload-test
postman-collection-upload-test:
	@echo "===== DEBUG: Postman Collection Upload Test Variables ====="
	@echo "POSTMAN_API_KEY: $(POSTMAN_API_KEY)"
	@echo "POSTMAN_WS: $(POSTMAN_WS)"
	@echo "COLLECTION_FIXED: $(COLLECTION_FIXED)"
	@echo "==========================================================="
	@if [ ! -f $(COLLECTION_FIXED) ]; then \
		echo "⚠️  $(COLLECTION_FIXED) not found. Run postman-collection-auto-fix first."; \
		exit 1; \
	fi
	@echo "📦 Using collection: $(COLLECTION_FIXED)"
	@RESPONSE=$$($(JQ_COLLECTION_UPLOAD_FIXED) | \
		curl --silent --location --request POST "$(POSTMAN_COLLECTIONS_URL)" \
			$(POSTMAN_HEADERS_JSON) \
			--data-binary @-); \
		echo "$$RESPONSE" | jq . > $(POSTMAN_UPLOAD_TEST_DEBUG) || echo "$$RESPONSE" > $(POSTMAN_UPLOAD_TEST_DEBUG); \
		COLL_UID=$$(echo "$$RESPONSE" | jq -r '.collection.uid // empty'); \
		if [ -z "$$COLL_UID" ] || [ "$$COLL_UID" = "null" ]; then \
			echo "❌ Failed to upload test collection. Check $(POSTMAN_UPLOAD_TEST_DEBUG) for details."; \
			exit 1; \
		else \
			echo "✅ TEST Collection uploaded with UID: $$COLL_UID"; \
			echo $$COLL_UID > $(POSTMAN_TEST_COLLECTION_UID_FILE); \
			echo "📄 UID saved to $(POSTMAN_TEST_COLLECTION_UID_FILE)"; \
		fi


# Postman Mocks
POSTMAN_MOCKS_URL            := $(POSTMAN_API_BASE_URL)/mocks
POSTMAN_MOCK_URL             := $(POSTMAN_MOCKS_URL)/$(shell cat $(MOCK_UID_FILE))
POSTMAN_MOCK_PAYLOAD         := $(POSTMAN_DIR)/mock-payload.json
POSTMAN_MOCK_UPDATE_PAYLOAD  := $(POSTMAN_DIR)/mock-update-payload.json

# JQ templates
JQ_CREATE_MOCK_PAYLOAD       = jq -n \
	--arg coll "$(COLL_UID)" \
	--arg env "$(ENV_UID)" \
	-f $(SCRIPTS_DIR)/create_mock_payload.jq

JQ_UPDATE_MOCK_PAYLOAD       = jq -n \
	--arg coll "$(COLL_UID)" \
	--arg env "$(ENV_UID)" \
	-f $(SCRIPTS_DIR)/update_mock_payload.jq

# Headers
POSTMAN_MOCK_HEADERS         := \
	--header "x-api-key: $(POSTMAN_API_KEY)" \
	--header "Content-Type: application/json"


.PHONY: sync-mock
sync-mock:
	@echo "🔍 Checking for existing mock UID..."
	@if [ -z "$(MOCK_UID)" ]; then \
		echo "⚠️  No mock UID found. Creating a new mock..."; \
		$(JQ_CREATE_MOCK_PAYLOAD) > $(POSTMAN_MOCK_PAYLOAD); \
		curl --silent --location --request POST "$(POSTMAN_MOCKS_URL)" \
			$(POSTMAN_MOCK_HEADERS) \
			--data-binary @$(POSTMAN_MOCK_PAYLOAD) \
			| jq -r '.mock.uid' > $(MOCK_UID_FILE); \
		echo "✅ Mock created. UID saved to $(MOCK_UID_FILE)."; \
	else \
		echo "✅ Found existing mock UID: $(MOCK_UID)."; \
	fi
	@echo "🔄 Updating Postman mock server environment..."
	$(JQ_UPDATE_MOCK_PAYLOAD) > $(POSTMAN_MOCK_UPDATE_PAYLOAD)
	@curl --location --request PUT "$(POSTMAN_MOCK_URL)" \
		$(POSTMAN_MOCK_HEADERS) \
		--data-binary @$(POSTMAN_MOCK_UPDATE_PAYLOAD)


CREATE_ENV_PAYLOAD_SCRIPT := $(SCRIPTS_DIR)/create_env_payload.jq

.PHONY: postman-env-create
postman-env-create:
	@echo "🧪 Generating Postman environment file …"
	@if [ ! -f $(MOCK_URL_FILE_POSTMAN) ]; then \
	    echo '⚠️ $(MOCK_URL_FILE_POSTMAN) missing. Cannot proceed.'; \
	    exit 1; \
	fi
	@POSTMAN_MOCK_URL=$$(cat $(MOCK_URL_FILE_POSTMAN)); \
	echo "Using mock URL: $$POSTMAN_MOCK_URL"; \
	jq -n --arg baseUrl "$$POSTMAN_MOCK_URL" \
	      --arg token "$(TOKEN)" \
	      -f $(CREATE_ENV_PAYLOAD_SCRIPT) > $(ENV_FILE); \
	echo "✅ Wrote $(ENV_FILE) with baseUrl=$$POSTMAN_MOCK_URL"


POSTMAN_ENVIRONMENTS_URL     := $(POSTMAN_API_BASE_URL)/environments?workspace=$(POSTMAN_WS)
POSTMAN_ENV_UPLOAD_DEBUG     := $(POSTMAN_DIR)/env-upload-debug.json
POSTMAN_ENV_UID_FILE         := $(POSTMAN_DIR)/postman_env_uid.txt

# --- Upload environment file to Postman ---
.PHONY: postman-env-upload
postman-env-upload:
	@echo "📤 Uploading Postman environment file to workspace $(POSTMAN_WS)..."
	@RESPONSE=$$(curl --silent --location --request POST "$(POSTMAN_ENVIRONMENTS_URL)" \
		$(POSTMAN_HEADERS_JSON) \
		--data-binary '@$(ENV_FILE)'); \
		echo "$$RESPONSE" | jq . > $(POSTMAN_ENV_UPLOAD_DEBUG) || echo "$$RESPONSE" > $(POSTMAN_ENV_UPLOAD_DEBUG); \
		ENV_UID=$$(echo "$$RESPONSE" | jq -r '.environment.uid // empty'); \
		if [ -z "$$ENV_UID" ]; then \
			echo "❌ Failed to upload environment. Check $(POSTMAN_ENV_UPLOAD_DEBUG) for details."; \
			exit 1; \
		else \
			echo "✅ Environment uploaded with UID: $$ENV_UID"; \
			echo $$ENV_UID > $(POSTMAN_ENV_UID_FILE); \
		fi


UPDATE_MOCK_ENV_PAYLOAD := $(POSTMAN_DIR)/update-mock-env-payload.json
JQ_UPDATE_MOCK_ENV      = jq -n \
	--arg coll "$(COLL_UID)" \
	--arg env "$(ENV_UID)" \
	-f $(SCRIPTS_DIR)/update_mock_env_payload.jq

POSTMAN_MOCK_ENV_URL    := $(POSTMAN_API_BASE_URL)/mocks/$(MOCK_ID)


.PHONY: update-mock-env
update-mock-env:
	@echo "🔄 Updating Postman mock server environment..."
	$(JQ_UPDATE_MOCK_ENV) > $(UPDATE_MOCK_ENV_PAYLOAD)
	@curl --location --request PUT "$(POSTMAN_MOCK_ENV_URL)" \
		$(POSTMAN_MOCK_HEADERS) \
		--data-binary @$(UPDATE_MOCK_ENV_PAYLOAD)
	@echo "✅ Mock server environment updated."


VERIFY_MOCK_SCRIPT := $(SCRIPTS_DIR)/verify_mock.jq

.PHONY: verify-mock
verify-mock:
	@echo "🔍 Fetching mock server details..."
	@curl --silent --location --request GET "$(POSTMAN_VERIFY_MOCK_URL)" \
		$(POSTMAN_MOCK_HEADERS) \
		| jq -f $(VERIFY_MOCK_SCRIPT)


# === START PRISM ===
# New variable to add near the other constants
PRISM_PID_FILE        := $(POSTMAN_DIR)/prism.pid

.PHONY: prism-start
prism-start:
	@echo "🚀 Starting Prism mock server on port $(PRISM_PORT)..."
	@echo "$(PRISM_HOST):$(PRISM_PORT)" > $(MOCK_URL_FILE_PRISM)
	@nohup $(PRISM) mock $(OPENAPI_SPEC_WITH_EXAMPLES) -p $(PRISM_PORT) > $(PRISM_LOG_FILE) 2>&1 &
	@echo $$! > $(PRISM_PID_FILE)
	@sleep 2
	@if lsof -i :$(PRISM_PORT) -t >/dev/null; then \
		echo "✅ Prism started at $(PRISM_MOCK_URL)"; \
	else \
		echo "❌ Failed to start Prism."; \
		exit 1; \
	fi


# === STOP PRISM ===
.PHONY: prism-stop
prism-stop:
	@if [ -f $(PRISM_PID_FILE) ]; then \
		kill -9 `cat $(PRISM_PID_FILE)` || true; \
		rm -f $(PRISM_PID_FILE) $(MOCK_URL_FILE_PRISM); \
		echo "🛑 Prism stopped."; \
	else \
		echo "ℹ️  No Prism instance running."; \
	fi


# === RUN TESTS (Requires Prism Already Running) ===
.PHONY: prism-mock-test
prism-mock-test:
	@echo "🔬 Running Newman tests against Prism mock..."
	@if [ ! -f $(COLLECTION_FIXED) ]; then \
		echo "❌ Missing Postman collection: $(COLLECTION_FIXED)"; \
		exit 1; \
	fi
	@if ! lsof -i :$(PRISM_PORT) -t >/dev/null; then \
		echo "❌ Prism is not running on port $(PRISM_PORT). Start it with 'make prism-start'."; \
		exit 1; \
	fi
	$(NEWMAN) run $(COLLECTION_FIXED) \
		--env-var baseUrl=$(PRISM_MOCK_URL) \
		--env-var token=$(TOKEN) \
		--reporters cli,html \
		--reporter-html-export $(REPORT_HTML)
	@echo "📄 Newman test report generated at $(REPORT_HTML)"


SANITIZE_COLLECTION_SCRIPT := $(SCRIPTS_DIR)/sanitize_collection.jq
COLLECTION_WITH_EXAMPLES   := $(POSTMAN_GEN_DIR)/c2m.collection.with.examples.json
COLLECTION_FIXED           := $(POSTMAN_GEN_DIR)/c2m.collection.fixed.json

# --- Sanitize Postman Collection: Replace <string>, <integer>, etc. with valid example values ---
.PHONY: postman-collection-fix-examples
postman-collection-fix-examples:
	@echo "🧹 Sanitizing Postman collection by replacing placeholder values..."
	@if [ ! -f $(COLLECTION_WITH_EXAMPLES) ]; then \
		echo "❌ Collection with examples not found: $(COLLECTION_WITH_EXAMPLES)"; \
		exit 1; \
	fi
	jq -f $(SANITIZE_COLLECTION_SCRIPT) $(COLLECTION_WITH_EXAMPLES) > $(COLLECTION_FIXED)
	@echo "✅ Sanitized collection saved to $(COLLECTION_FIXED)"


JQ_CREATE_MOCK_PAYLOAD = jq -n \
	--arg coll "$$COLL_UID" \
	--arg env "$$ENV_UID" \
	-f $(SCRIPTS_DIR)/create_mock_payload.jq

.PHONY: postman-mock-create
postman-mock-create:
	@echo "🛠 Creating Postman mock server for collection..."
	@if [ ! -f $(POSTMAN_TEST_COLL_UID_FILE) ]; then \
		echo "❌ Missing test collection UID file: $(POSTMAN_TEST_COLL_UID_FILE). Run postman-collection-upload-test first."; \
		exit 1; \
	fi; \
	COLL_UID=$$(cat $(POSTMAN_TEST_COLL_UID_FILE)); \
	$(JQ_CREATE_MOCK_PAYLOAD) > $(POSTMAN_MOCK_PAYLOAD); \
	echo "📤 Creating mock server via Postman API..."; \
	curl --silent --location --request POST "$(POSTMAN_MOCKS_URL)" \
		$(POSTMAN_CURL_HEADERS) \
		--data-binary @$(POSTMAN_MOCK_PAYLOAD) \
		-o $(POSTMAN_MOCK_DEBUG); \
	if ! jq -e '.mock.mockUrl' $(POSTMAN_MOCK_DEBUG) >/dev/null; then \
		echo "❌ Failed to create mock server. See $(POSTMAN_MOCK_DEBUG)"; \
		exit 1; \
	fi; \
	POSTMAN_MOCK_URL=$$(jq -r '.mock.mockUrl' $(POSTMAN_MOCK_DEBUG)); \
	MOCK_UID=$$(jq -r '.mock.uid' $(POSTMAN_MOCK_DEBUG) | sed 's/^[^-]*-//'); \
	echo "✅ Mock server created at: $$POSTMAN_MOCK_URL"; \
	echo "$$POSTMAN_MOCK_URL" > $(MOCK_URL_FILE_POSTMAN); \
	echo "$$MOCK_UID" > $(POSTMAN_MOCK_UID_FILE); \
	echo "📄 Mock server URL saved to $(MOCK_URL_FILE_POSTMAN)"; \
	echo "📄 Mock UID saved to $(POSTMAN_MOCK_UID_FILE)"; \
	echo "🔍 Validating mock configuration..."; \
	curl --silent --location --request GET "$(POSTMAN_MOCKS_URL)/$$MOCK_UID" \
		$(POSTMAN_CURL_HEADERS) \
		-o $(POSTMAN_MOCK_VALIDATE); \
	if jq -e '.error' $(POSTMAN_MOCK_VALIDATE) >/dev/null; then \
		echo "❌ Postman mock validation failed. See $(POSTMAN_MOCK_VALIDATE)"; \
		exit 1; \
	else \
		echo "✅ Postman mock validated successfully."; \
	fi


REPORT_JSON := $(POSTMAN_DIR)/newman-mock-report.json

.PHONY: postman-mock
postman-mock:
	@echo "🔬 Running Newman tests against Postman mock..."
	@if [ ! -f $(MOCK_URL_FILE_POSTMAN) ]; then \
		echo "ℹ️  Postman mock URL not found. Creating Postman mock..."; \
		$(MAKE) postman-mock-create; \
	fi
	@if [ ! -f $(COLLECTION_FIXED) ]; then \
		echo "❌ Missing Postman collection: $(COLLECTION_FIXED)"; \
		exit 1; \
	fi
	$(NEWMAN) run $(COLLECTION_FIXED) \
		--env-var baseUrl=$(POSTMAN_MOCK_URL) \
		--env-var token=$(TOKEN) \
		--reporters cli,html,json \
		--bail \
		--reporter-html-export $(REPORT_HTML) \
		--reporter-json-export $(REPORT_JSON)
	@echo "📄 Newman test reports generated:"
	@echo "   - HTML: $(REPORT_HTML)"
	@echo "   - JSON: $(REPORT_JSON)"


POSTMAN_ENV_UID_FILE        := $(POSTMAN_DIR)/postman_env_uid.txt
POSTMAN_TEST_COLL_UID_FILE  := $(POSTMAN_DIR)/postman_test_collection_uid.txt
POSTMAN_MOCK_UID_FILE       := $(POSTMAN_DIR)/postman_mock_uid.txt
POSTMAN_MOCK_LINK_DEBUG     := $(POSTMAN_DIR)/mock-link-debug.json
POSTMAN_LINK_ENV_URL        := $(POSTMAN_API_BASE_URL)/mocks

JQ_LINK_ENV_TO_MOCK         = jq -n \
	--arg coll "$$COLL_UID" \
	--arg env "$$ENV_UID" \
	-f $(SCRIPTS_DIR)/link_env_to_mock_payload.jq

.PHONY: postman-link-env-to-collection
postman-link-env-to-collection:
	@echo "🔗 Linking environment to collection and mock server..."
	@if [ ! -f $(POSTMAN_ENV_UID_FILE) ]; then \
		echo "❌ Missing environment UID file: $(POSTMAN_ENV_UID_FILE). Run postman-env-upload first."; \
		exit 1; \
	fi
	@if [ ! -f $(POSTMAN_TEST_COLL_UID_FILE) ]; then \
		echo "❌ Missing test collection UID file: $(POSTMAN_TEST_COLL_UID_FILE). Run postman-collection-upload-test first."; \
		exit 1; \
	fi
	@if [ ! -f $(POSTMAN_MOCK_UID_FILE) ]; then \
		echo "❌ Missing mock UID file: $(POSTMAN_MOCK_UID_FILE). Run postman-mock-create first."; \
		exit 1; \
	fi
	ENV_UID=$$(cat $(POSTMAN_ENV_UID_FILE)); \
	COLL_UID=$$(cat $(POSTMAN_TEST_COLL_UID_FILE)); \
	MOCK_UID=$$(cat $(POSTMAN_MOCK_UID_FILE)); \
	echo "📦 Linking Environment $$ENV_UID with Collection $$COLL_UID (Mock $$MOCK_UID)..."; \
	$(JQ_LINK_ENV_TO_MOCK) | \
	curl --silent --location --request PUT "$(POSTMAN_LINK_ENV_URL)/$$MOCK_UID" \
		$(POSTMAN_CURL_HEADERS) \
		--data-binary @- \
		-o $(POSTMAN_MOCK_LINK_DEBUG); \
	if jq -e '.mock' $(POSTMAN_MOCK_LINK_DEBUG) >/dev/null; then \
		echo "✅ Environment linked to mock server successfully."; \
	else \
		echo "❌ Failed to link environment. See $(POSTMAN_MOCK_LINK_DEBUG)"; \
		exit 1; \
	fi



# === DOCUMENTATION TARGETS ===

# New variables to add near other constants
OPENAPI_BUNDLED_SPEC := $(OPENAPI_DIR)/bundled.yaml
DOCS_INDEX_HTML      := $(DOCS_DIR)/index.html

.PHONY: docs-build
docs-build:
	@echo "📚 Building API documentation with Redoc..."
	$(REDOCLY) build-docs $(OPENAPI_SPEC) -o $(DOCS_INDEX_HTML)
	$(SWAGGER) bundle $(OPENAPI_SPEC) --outfile $(OPENAPI_BUNDLED_SPEC) --type yaml


DOCS_HOST := localhost
DOCS_PORT := 8080
DOCS_URL  := http://$(DOCS_HOST):$(DOCS_PORT)

.PHONY: docs-serve
docs-serve:
	@echo "🌐 Serving API documentation locally on $(DOCS_URL)..."
	@$(PYTHON3) -m http.server $(DOCS_PORT) --bind $(DOCS_HOST) --directory $(DOCS_DIR)


POSTMAN_SPECS_URL     := $(POSTMAN_API_BASE_URL)/specs?workspaceId=$(POSTMAN_WS)
JQ_LIST_SPECS         := jq -r '.data[] | "\(.name)\t\(.id)\t\(.type)\t\(.updatedAt)"'

.PHONY: postman-api-list-specs
postman-api-list-specs:
	@echo "📜 Listing all specs in workspace $(POSTMAN_WS)..."
	@curl --silent \
		$(POSTMAN_HEADER_API_KEY) \
		"$(POSTMAN_SPECS_URL)" \
		| $(JQ_LIST_SPECS) \
		| column -t -s$$'\t'


POSTMAN_SPECS_URL        := $(POSTMAN_API_BASE_URL)/specs?workspaceId=$(POSTMAN_WS)
POSTMAN_SPEC_DELETE_URL  := $(POSTMAN_API_BASE_URL)/specs
JQ_DELETE_OLD_SPECS      := jq -r '.data | sort_by(.updatedAt) | reverse | .[1:] | .[].id'

.PHONY: postman-api-delete-old-specs
postman-api-delete-old-specs:
	@echo "🧹 Deleting old specs in workspace $(POSTMAN_WS), keeping the most recent one..."
	@SPECS=$$(curl --silent \
		$(POSTMAN_HEADER_API_KEY) \
		"$(POSTMAN_SPECS_URL)" \
		| jq -r '.data | sort_by(.updatedAt) | reverse | .[1:] | .[].id'); \
	if [ -z "$$SPECS" ]; then \
		echo "   No old specs to delete."; \
	else \
		echo "   Found old specs to delete:"; \
		echo "$$SPECS" | tr ' ' '\n'; \
		for ID in $$SPECS; do \
			echo "   ➡️ Deleting spec $$ID..."; \
			curl --silent --location \
				--request DELETE "$(POSTMAN_SPEC_DELETE_URL)/$$ID" \
				$(POSTMAN_HEADER_API_KEY) \
				$(POSTMAN_HEADER_CONTENT_TYPE) \
				> /dev/null; \
		done; \
		echo "   ✅ Old specs deleted."; \
	fi


POSTMAN_MOCK_DELETE_URL  := $(POSTMAN_API_BASE_URL)/mocks
POSTMAN_MOCK_DELETE_DEBUG := $(POSTMAN_DIR)/mock-delete-debug.json
POSTMAN_MOCK_UID_FILE    := $(POSTMAN_DIR)/postman_mock_uid.txt

.PHONY: postman-cleanup
postman-cleanup:
	@echo "🧹 Starting full cleanup of Postman resources..."

	# --- Delete Mock Server ---
	@if [ -f $(POSTMAN_MOCK_UID_FILE) ]; then \
		MOCK_UID=$$(cat $(POSTMAN_MOCK_UID_FILE)); \
		echo "🗑 Deleting Mock Server: $$MOCK_UID..."; \
		curl --silent --location --request DELETE "$(POSTMAN_MOCK_DELETE_URL)/$$MOCK_UID" \
			$(POSTMAN_CURL_HEADERS) \
			| tee $(POSTMAN_MOCK_DELETE_DEBUG); \
		echo "✅ Mock server deleted."; \
		rm -f $(POSTMAN_MOCK_UID_FILE) $(MOCK_URL_FILE_POSTMAN); \
	else \
		echo "⚠️  No mock UID found at $(POSTMAN_MOCK_UID_FILE)"; \
	fi


POSTMAN_ENV_DELETE_URL   := $(POSTMAN_API_BASE_URL)/environments
POSTMAN_ENV_DELETE_DEBUG := $(POSTMAN_DIR)/env-delete-debug.json
POSTMAN_ENV_UID_FILE     := $(POSTMAN_DIR)/postman_env_uid.txt
POSTMAN_ENV_FILE         := $(POSTMAN_DIR)/mock-env.json

	# --- Delete Environment ---
	@if [ -f $(POSTMAN_ENV_UID_FILE) ]; then \
		ENV_UID=$$(cat $(POSTMAN_ENV_UID_FILE)); \
		echo "🗑 Deleting Environment: $$ENV_UID..."; \
		curl --silent --location --request DELETE "$(POSTMAN_ENV_DELETE_URL)/$$ENV_UID" \
			$(POSTMAN_CURL_HEADERS) \
			| tee $(POSTMAN_ENV_DELETE_DEBUG); \
		echo "✅ Environment deleted."; \
		rm -f $(POSTMAN_ENV_UID_FILE) $(POSTMAN_ENV_FILE); \
	else \
		echo "⚠️  No environment UID found at $(POSTMAN_ENV_UID_FILE)"; \
	fi


POSTMAN_COLLECTION_DELETE_URL   := $(POSTMAN_API_BASE_URL)/collections
POSTMAN_COLLECTION_DELETE_DEBUG := $(POSTMAN_DIR)/collection-delete-debug.json
POSTMAN_TEST_COLL_UID_FILE      := $(POSTMAN_DIR)/postman_test_collection_uid.txt

	# --- Delete Test Collection ---
	@if [ -f $(POSTMAN_TEST_COLL_UID_FILE) ]; then \
		COLL_UID=$$(cat $(POSTMAN_TEST_COLL_UID_FILE)); \
		echo "🗑 Deleting Collection: $$COLL_UID..."; \
		curl --silent --location --request DELETE "$(POSTMAN_COLLECTION_DELETE_URL)/$$COLL_UID" \
			$(POSTMAN_CURL_HEADERS) \
			| tee $(POSTMAN_COLLECTION_DELETE_DEBUG); \
		echo "✅ Test collection deleted."; \
		rm -f $(POSTMAN_TEST_COLL_UID_FILE); \
	else \
		echo "⚠️  No test collection UID found at $(POSTMAN_TEST_COLL_UID_FILE)"; \
	fi


POSTMAN_MAIN_COLL_UID_FILE       := $(POSTMAN_DIR)/postman_collection_uid.txt
POSTMAN_MAIN_COLL_DELETE_DEBUG   := $(POSTMAN_DIR)/collection-main-delete-debug.json

	# --- Delete Main Collection (if exists) ---
	@if [ -f $(POSTMAN_MAIN_COLL_UID_FILE) ]; then \
		COLL_UID=$$(cat $(POSTMAN_MAIN_COLL_UID_FILE)); \
		echo "🗑 Deleting Main Collection: $$COLL_UID..."; \
		curl --silent --location --request DELETE "$(POSTMAN_COLLECTION_DELETE_URL)/$$COLL_UID" \
			$(POSTMAN_CURL_HEADERS) \
			| tee $(POSTMAN_MAIN_COLL_DELETE_DEBUG); \
		echo "✅ Main collection deleted."; \
		rm -f $(POSTMAN_MAIN_COLL_UID_FILE); \
	else \
		echo "⚠️  No main collection UID found at $(POSTMAN_MAIN_COLL_UID_FILE)"; \
	fi

# Endpoints
POSTMAN_MOCKS_URL         := $(POSTMAN_API_BASE_URL)/mocks?workspace=$(POSTMAN_WS)
POSTMAN_COLLECTIONS_URL   := $(POSTMAN_API_BASE_URL)/collections?workspace=$(POSTMAN_WS)
POSTMAN_APIS_URL          := $(POSTMAN_API_BASE_URL)/apis?workspace=$(POSTMAN_WS)
POSTMAN_ENVIRONMENTS_URL  := $(POSTMAN_API_BASE_URL)/environments?workspace=$(POSTMAN_WS)
POSTMAN_SPECS_URL         := $(POSTMAN_API_BASE_URL)/specs?workspaceId=$(POSTMAN_WS)

# Delete endpoints
POSTMAN_DELETE_MOCK_URL       := $(POSTMAN_API_BASE_URL)/mocks
POSTMAN_DELETE_COLLECTION_URL := $(POSTMAN_API_BASE_URL)/collections
POSTMAN_DELETE_API_URL        := $(POSTMAN_API_BASE_URL)/apis
POSTMAN_DELETE_ENV_URL        := $(POSTMAN_API_BASE_URL)/environments
POSTMAN_DELETE_SPEC_URL       := $(POSTMAN_API_BASE_URL)/specs

.PHONY: postman-cleanup-all
postman-cleanup-all:
	@echo "🧹 Starting FULL cleanup of Postman resources for workspace $(POSTMAN_WS)..."

	# --- Delete Mock Servers ---
	@echo "🔍 Fetching mock servers..."
	@MOCKS=$$(curl --silent --location --request GET "$(POSTMAN_API_BASE_URL)/mocks?workspace=$(POSTMAN_WS)" \
		$(POSTMAN_HEADER_API_KEY) | tee $(POSTMAN_DIR)/mocks-debug.json | jq -r '.mocks // [] | .[].id'); \
	echo "DEBUG: MOCKS=$$MOCKS"; \
	if [ -z "$$MOCKS" ]; then \
		echo "   No mock servers found."; \
	else \
		for MOCK in $$MOCKS; do \
			echo "🗑 Deleting mock server $$MOCK..."; \
			curl --silent --location --request DELETE "$(POSTMAN_API_BASE_URL)/mocks/$$MOCK" \
				$(POSTMAN_HEADER_API_KEY) || echo "⚠️ Failed to delete mock server $$MOCK"; \
		done; \
	fi

	# --- Delete Collections ---
	@echo "🔍 Fetching collections..."
	@COLLECTIONS=$$(curl --silent --location --request GET "$(POSTMAN_API_BASE_URL)/collections?workspaceId=$(POSTMAN_WS)" \
		$(POSTMAN_HEADER_API_KEY) | tee $(POSTMAN_DIR)/collections-debug.json | jq -r '.collections // [] | .[].uid'); \
	echo "DEBUG: COLLECTIONS=$$COLLECTIONS"; \
	if [ -z "$$COLLECTIONS" ]; then \
		echo "   No collections found."; \
	else \
		for COL in $$COLLECTIONS; do \
			echo "🗑 Deleting collection $$COL..."; \
			curl --silent --location --request DELETE "$(POSTMAN_API_BASE_URL)/collections/$$COL" \
				$(POSTMAN_HEADER_API_KEY) || echo "⚠️ Failed to delete collection $$COL"; \
		done; \
	fi

	# --- Delete APIs ---
	@echo "🔍 Fetching APIs..."
	@APIS=$$(curl --silent --location --request GET "$(POSTMAN_API_BASE_URL)/apis?workspace=$(POSTMAN_WS)" \
		$(POSTMAN_HEADER_API_KEY) | tee $(POSTMAN_DIR)/apis-debug.json | jq -r '.apis // [] | .[].id'); \
	echo "DEBUG: APIS=$$APIS"; \
	if [ -z "$$APIS" ]; then \
		echo "   No APIs found."; \
	else \
		for API in $$APIS; do \
			echo "🗑 Deleting API $$API..."; \
			curl --silent --location --request DELETE "$(POSTMAN_API_BASE_URL)/apis/$$API" \
				$(POSTMAN_HEADER_API_KEY) || echo "⚠️ Failed to delete API $$API"; \
		done; \
	fi

	# --- Delete Environments ---
	@echo "🔍 Fetching environments..."
	@ENVS=$$(curl --silent --location --request GET "$(POSTMAN_API_BASE_URL)/environments?workspace=$(POSTMAN_WS)" \
		$(POSTMAN_HEADER_API_KEY) | tee $(POSTMAN_DIR)/envs-debug.json | jq -r '.environments // [] | .[].uid'); \
	echo "DEBUG: ENVS=$$ENVS"; \
	if [ -z "$$ENVS" ]; then \
		echo "   No environments found."; \
	else \
		for ENV in $$ENVS; do \
			echo "🗑 Deleting environment $$ENV..."; \
			curl --silent --location --request DELETE "$(POSTMAN_API_BASE_URL)/environments/$$ENV" \
				$(POSTMAN_HEADER_API_KEY) || echo "⚠️ Failed to delete environment $$ENV"; \
		done; \
	fi

	# --- Delete Specs ---
	@echo "🔍 Fetching specs..."
	@SPECS=$$(curl --silent --location --request GET "$(POSTMAN_API_BASE_URL)/specs?workspaceId=$(POSTMAN_WS)" \
		$(POSTMAN_HEADER_API_KEY) | tee $(POSTMAN_DIR)/specs-debug.json | jq -r '.data // [] | .[].id'); \
	echo "DEBUG: SPECS=$$SPECS"; \
	if [ -z "$$SPECS" ]; then \
		echo "   No specs found."; \
	else \
		for SPEC in $$SPECS; do \
			echo "🗑 Deleting spec $$SPEC..."; \
			curl --silent --location --request DELETE "$(POSTMAN_API_BASE_URL)/specs/$$SPEC" \
				$(POSTMAN_HEADER_API_KEY) || echo "⚠️ Failed to delete spec $$SPEC"; \
		done; \
	fi

	@echo "✅ Postman cleanup complete for workspace $(POSTMAN_WS)."



POSTMAN_SPECS_TRASH_URL    := $(POSTMAN_API_BASE_URL)/specs?workspaceId=$(POSTMAN_WS)&status=trashed
POSTMAN_DELETE_SPEC_URL    := $(POSTMAN_API_BASE_URL)/specs
JQ_GET_TRASH_IDS := jq -r '.data // [] | .[].id'


.PHONY: postman-api-clean-trash
postman-api-clean-trash:
	@echo "🗑️ Checking for trashed specs in workspace $(POSTMAN_WS)..."
	@TRASH=$$(curl --silent \
		$(POSTMAN_HEADER_API_KEY) \
		"$(POSTMAN_SPECS_TRASH_URL)" \
		| $(JQ_GET_TRASH_IDS)); \
	if [ -z "$$TRASH" ]; then \
		echo "   No trashed specs found in workspace $(POSTMAN_WS)."; \
	else \
		for ID in $$TRASH; do \
			echo "   🚮 Permanently deleting trashed spec $$ID..."; \
			curl --silent --location \
				--request DELETE \
				"$(POSTMAN_DELETE_SPEC_URL)/$$ID?permanent=true" \
				$(POSTMAN_HEADER_API_KEY) \
				$(POSTMAN_HEADER_CONTENT_TYPE) | jq .; \
		done; \
		echo "   ✅ All trashed specs have been permanently deleted."; \
	fi


POSTMAN_COLLECTIONS_URL      := $(POSTMAN_API_BASE_URL)/collections?workspaceId=$(POSTMAN_WS)
POSTMAN_DELETE_COLLECTION_URL := $(POSTMAN_API_BASE_URL)/collections
JQ_GET_COLLECTION_IDS        := jq -r '.collections[].uid'

# --- Be careful!  This will delete ALL Collections in a Workspace.
.PHONY: postman-collections-clean
postman-collections-clean:
	@echo "🗑️ Listing all collections in workspace $(POSTMAN_WS)..."
	@COLLECTIONS=$$(curl --silent \
		$(POSTMAN_HEADER_API_KEY) \
		"$(POSTMAN_COLLECTIONS_URL)" \
		| $(JQ_GET_COLLECTION_IDS)); \
	if [ -z "$$COLLECTIONS" ]; then \
		echo "   No collections found."; \
	else \
		for ID in $$COLLECTIONS; do \
			echo "   🚮 Deleting collection $$ID..."; \
			curl --silent --location \
				--request DELETE \
				"$(POSTMAN_DELETE_COLLECTION_URL)/$$ID" \
				$(POSTMAN_HEADER_API_KEY) | jq .; \
		done; \
		echo "   ✅ All collections deleted."; \
	fi


POSTMAN_APIS_URL     := $(POSTMAN_API_BASE_URL)/apis?workspace=$(POSTMAN_WS)
POSTMAN_IMPORT_DEBUG := $(POSTMAN_DIR)/import-debug.json
JQ_IMPORT_API_PAYLOAD := jq -Rs --arg name '$(POSTMAN_API_NAME)' \
  '{ api: { name: $$name, schema: { type: "openapi3", language: "yaml", schema: . }}}'

.PHONY: postman-api-debug-A
postman-api-debug-A:
	@echo "🐞 Debugging Postman API import..."
	curl --verbose --location --request POST "$(POSTMAN_APIS_URL)" \
		$(POSTMAN_HEADER_API_KEY) \
		$(POSTMAN_HEADER_AUTH) \
		$(POSTMAN_HEADER_ACCEPT) \
		$(POSTMAN_HEADER_CONTENT_TYPE) \
		--data "$$($(JQ_IMPORT_API_PAYLOAD) $(OPENAPI_SPEC))" \
		| tee $(POSTMAN_IMPORT_DEBUG)


POSTMAN_ME_URL      := $(POSTMAN_API_BASE_URL)/me
POSTMAN_APIS_LIST   := $(POSTMAN_API_BASE_URL)/apis?workspaceId=$(POSTMAN_WS)
POSTMAN_SPECS_LIST  := $(POSTMAN_API_BASE_URL)/specs?workspaceId=$(POSTMAN_WS)

.PHONY: postman-api-debug-B
postman-api-debug-B:
	@echo "🐞 Debugging Postman API key and workspace..."
	@echo "POSTMAN_API_KEY=$(POSTMAN_API_KEY)"
	@echo "POSTMAN_WS=$(POSTMAN_WS)"
	@echo "🔑 Verifying key..."
	@curl --silent \
		$(POSTMAN_HEADER_API_KEY) \
		"$(POSTMAN_ME_URL)" | jq .
	@echo "📂 Listing APIs in workspace $(POSTMAN_WS)..."
	@curl --silent \
		$(POSTMAN_HEADER_API_KEY) \
		"$(POSTMAN_APIS_LIST)" | jq .
	@echo "📜 Listing Specs in workspace $(POSTMAN_WS)..."
	@curl --silent \
		$(POSTMAN_HEADER_API_KEY) \
		"$(POSTMAN_SPECS_LIST)" | jq .


.PHONY: postman-workspace-debug
postman-workspace-debug:
    @echo "🔍 Current Postman workspace ID: $(POSTMAN_WS)"


# ---------- HELP --------------------------------------
.PHONY: help
help:## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

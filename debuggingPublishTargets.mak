






POSTMAN_API_UID_FILE := postman/postman_api_uid.txt
POSTMAN_API_VER_FILE := postman/postman_api_version.txt
POSTMAN_API_VERSION  := v1.0.0

## --- Create API Version ---
.PHONY: postman-api-create-version
postman-api-create-version:
	@echo "t� Creaing  APIversion $and publishing schean.."
	@if [ ! -f postman/schema_uid.txt ]; then \
		echo "❌ Missing schema UID file: postman/schema_uid.txt. Run postman-api-upload-schema first."; exit 1; \
	fi
	@API_ID=$$(cat $(POSTMAN_API_UID_FILE)); \
	SCHEMA_ID=$$(cat postman/schema_uid.txt); \
	jVERSION_NAME="v1"; \
	jjq -n --arg name "$$VERSION_NAME" --arg schemaId "$$SCHEMA_ID" \
 		'{ name: $$name, schemas: [ { id: $$schemaId } ] }' > postman/version-payload.json; \
	curl --silent --location --request POST "https://api.getpostman.com/apis/$$API_ID/versions" \
		header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--header "Accept: application/vnd.api.v10+json" \
		--data-binary @postman/version-payload.json | tee postman/version-debug.json; \
	if grep -q '"id"' postman/version-debug.json; then \
		echo "✅ API version created successfully."; \
	else \
		echo "❌ Failed to create API version. Check postman/version-debug.json for details."; exit 1; \
	fi


.PHONY: postman-api-spec
postman-api-spec:
	@echo "🚀 Uploading OpenAPI spec to existing Postman API..."
	@if [ ! -f $(OPENAPI_SPEC) ]; then \
		echo "❌ OpenAPI spec file not found: $(OPENAPI_SPEC)"; \
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
	jq -n --arg lang "yaml" --rawfile spec $(OPENAPI_SPEC) \
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


.PHONY: postman-api-upload-spec-version
postman-api-upload-spec-version:
	@echo "📤 Uploading new OpenAPI spec version for API in Postman..."
	@if [ ! -f postman/postman_api_uid.txt ]; then \
		echo "❌ No API ID found. Run postman-api-upload-spec to create an API first."; \
		exit 1; \
	fi
	@API_ID=$$(cat postman/postman_api_uid.txt); \
	VERSION="v$$(date +%Y%m%d%H%M)"; \
	echo "🔖 Creating new version: $$VERSION for API $$API_ID..."; \
	VERSION_RESPONSE=$$(curl --silent --location --request POST "https://api.getpostman.com/apis/$$API_ID/versions" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Accept: application/vnd.api.v10+json" \
		--header "Content-Type: application/json" \
		--data-raw "$$(jq -n --arg version "$$VERSION" '{name: $$version}')"); \
	echo "$$VERSION_RESPONSE" | jq . > postman/api-version-debug.json; \
	VERSION_ID=$$(echo "$$VERSION_RESPONSE" | jq -r '.version.id // empty'); \
	if [ -z "$$VERSION_ID" ]; then \
		echo "❌ Failed to create version. Check postman/api-version-debug.json"; \
		exit 1; \
	fi; \
	echo "✅ Created version $$VERSION_ID. Uploading schema..."; \
	curl --silent --location --request POST "https://api.getpostman.com/apis/$$API_ID/versions/$$VERSION_ID/schemas" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Accept: application/vnd.api.v10+json" \
		--header "Content-Type: application/json" \
		--data-raw "$$(jq -Rs '{type: "openapi3", language: "yaml", schema: .}' $(OPENAPI_SPEC))" \
		| tee postman/api-schema-debug.json | jq .


.PHONY: postman-create-spec
postman-create-spec:
	@echo "📤 Creating a Spec in Postman’s Spec Hub using $(OPENAPI_SPEC)..."
	@ESCAPED_SPEC=$$(jq -Rs . $(OPENAPI_SPEC)); \
	PAYLOAD=$$(jq -n \
		--arg name "C2M API Spec" \
		--arg type "OPENAPI:3.0" \
		--arg content "$$ESCAPED_SPEC" \
		'{ name: $$name, type: $$type, files: [ { path: "index.yaml", content: $$content } ] }'); \
	echo "🔍 DEBUG: Payload prepared."; \
	curl --silent --location --request POST "https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data-raw "$$PAYLOAD" \
		| tee postman/create-spec-debug.json



POSTMAN_SPEC_FILE := postman/postman_spec_uid.txt

.PHONY: postman-api-new-spec
postman-api-new-spec:
	@mkdir -p postman
	@echo "🆕 Creating a new Postman Spec in workspace $(POSTMAN_WS)..."
	@RESPONSE=$$(jq -n \
		--arg name "C2M API Spec" \
		--arg type "OPENAPI:3.0" \
		--arg path "$(notdir $(OPENAPI_SPEC))" \
		--arg content "$$(jq -Rs . < $(OPENAPI_SPEC))" \
		'{ name: $$name, type: $$type, files: [ { path: $$path, content: $$content } ] }' \
		| curl --silent --location \
			--request POST "https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
			--header "X-Api-Key: $(POSTMAN_API_KEY)" \
			--header "Content-Type: application/json" \
			--data @-); \
	echo "$$RESPONSE" > postman/api-new-spec-response.json; \
	SPEC_ID=$$(echo "$$RESPONSE" | jq -r '.spec.id // empty'); \
	if [ -z "$$SPEC_ID" ]; then \
		echo "❌ Failed to create spec. See postman/api-new-spec-response.json for details."; \
		exit 1; \
	else \
		echo "$$SPEC_ID" > $(POSTMAN_SPEC_FILE); \
		echo "✅ Created Postman Spec with ID: $$SPEC_ID"; \
	fi


.PHONY: postman-api-set-root
postman-api-set-root:
	@POSTMAN_SPEC_ID=$$(cat $(POSTMAN_SPEC_FILE)); \
	if [ -z "$$POSTMAN_SPEC_ID" ]; then \
		echo "❌ No spec ID found. Run 'make postman-api-new-spec' first."; \
		exit 1; \
	fi; \
	echo "🔗 Setting rootFilePath to $(notdir $(OPENAPI_SPEC))..."; \
	curl --silent \
		--location \
		--request PUT \
		"https://api.getpostman.com/specs/$$POSTMAN_SPEC_ID" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data '{"rootFilePath":"$(notdir $(OPENAPI_SPEC))"}' \
		| jq .


POSTMAN_SPEC_FILE := postman/postman_spec_uid.txt
PLACEHOLDER_FILE  := postman/placeholder.yaml
PAYLOAD_FILE      := postman/payload.json

.PHONY: postman-api-publish-safe
postman-api-publish-safe:
	@mkdir -p postman
	@echo "openapi: 3.0.3" > $(PLACEHOLDER_FILE)
	@echo "info:" >> $(PLACEHOLDER_FILE)
	@echo "  title: Placeholder Spec" >> $(PLACEHOLDER_FILE)
	@echo "  version: 1.0.0" >> $(PLACEHOLDER_FILE)
	@echo "paths: {}" >> $(PLACEHOLDER_FILE)
	@echo "🆕 Creating Postman Spec with placeholder OpenAPI skeleton..."
	@PLACEHOLDER_CONTENT=$$(jq -Rs . < $(PLACEHOLDER_FILE)); \
	jq -n \
		--arg name "C2M Document Submission API" \
		--arg type "OPENAPI:3.0" \
		--arg path "index.yaml" \
		--arg content "$$PLACEHOLDER_CONTENT" \
		'{ name: $$name, type: $$type, files: [ { path: $$path, content: $$content } ] }' > $(PAYLOAD_FILE); \
	curl --silent --location \
		--request POST "https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data @$(PAYLOAD_FILE) > postman/api-publish-response.json; \
	SPEC_ID=$$(jq -r '.spec.id // empty' postman/api-publish-response.json); \
	if [ -z "$$SPEC_ID" ]; then \
		echo "❌ Failed to create spec. See postman/api-publish-response.json for details."; \
		exit 1; \
	else \
		echo "$$SPEC_ID" > $(POSTMAN_SPEC_FILE); \
		echo "✅ Created Postman Spec with ID: $$SPEC_ID"; \
	fi; \
	POSTMAN_SPEC_ID=$$(cat $(POSTMAN_SPEC_FILE)); \
	echo "📤 Uploading root OpenAPI spec: $(notdir $(OPENAPI_SPEC))..."; \
	CONTENT=$$(jq -Rs . < $(OPENAPI_SPEC)); \
	jq -n \
		--arg path "$(notdir $(OPENAPI_SPEC))" \
		--arg content "$$CONTENT" \
		'{ path: $$path, content: $$content }' > $(PAYLOAD_FILE); \
	curl --silent \
		--loc

POSTMAN_SPEC_FILE := postman/postman_spec_uid.txt
PAYLOAD_FILE      := postman/payload.json
OPENAPI_FILENAME  := $(notdir $(OPENAPI_SPEC))

.PHONY: postman-api-reset-spec
postman-api-reset-spec:
	@mkdir -p postman
	@if [ -s $(POSTMAN_SPEC_FILE) ]; then \
		OLD_ID=$$(cat $(POSTMAN_SPEC_FILE)); \
		echo "🗑️ Deleting old Postman Spec: $$OLD_ID..."; \
		curl --silent --location \
			--request DELETE \
			"https://api.getpostman.com/specs/$$OLD_ID" \
			--header "X-Api-Key: $(POSTMAN_API_KEY)" \
			--header "Content-Type: application/json" | jq .; \
	fi
	@echo "🆕 Creating new Postman Spec with root file index.yaml..."
	@CONTENT=$$(jq -Rs . < $(OPENAPI_SPEC)); \
	jq -n \
		--arg name "C2M Document Submission API" \
		--arg type "OPENAPI:3.0" \
		--arg path "index.yaml" \
		--arg content "$$CONTENT" \
		'{ name: $$name, type: $$type, files: [ { path: $$path, content: $$content } ] }' > $(PAYLOAD_FILE); \
	curl --silent --location \
		--request POST "https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
		--


POSTMAN_SPEC_FILE := postman/postman_spec_uid.txt
PAYLOAD_FILE      := postman/upload-root.json
OPENAPI_FILENAME  := $(notdir $(OPENAPI_SPEC))

.PHONY: postman-api-upload-root
postman-api-upload-root:
	@if [ ! -s $(POSTMAN_SPEC_FILE) ]; then \
		echo "❌ No spec ID found. Run 'make postman-api-reset-spec' first."; \
		exit 1; \
	fi
	@POSTMAN_SPEC_ID=$$(cat $(POSTMAN_SPEC_FILE)); \
	echo "📤 Uploading $(OPENAPI_FILENAME) to spec $$POSTMAN_SPEC_ID..."; \
	CONTENT=$$(jq -Rs . < $(OPENAPI_SPEC)); \
	jq -n \
		--arg path "$(OPENAPI_FILENAME)" \
		--arg content "$$CONTENT" \
		'{ path: $$path, content: $$content }' > $(PAYLOAD_FILE); \
	curl --silent \
		--location \
		--request POST \
		"https://api.getpostman.com/specs/$$POSTMAN_SPEC_ID/files" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data @$(PAYLOAD_FILE) | jq .; \
	echo "🔗 Setting rootFilePath to $(OPENAPI_FILENAME)..."; \
	curl --silent \
		--location \
		--request PUT \
		"https://api.getpostman.com/specs/$$POSTMAN_SPEC_ID" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data '{"rootFilePath":"$(OPENAPI_FILENAME)"}' | jq .


.PHONY: postman-api-publish
postman-api-publish: postman-api-delete-old-specs
	@POSTMAN_SPEC_ID=$$(curl --silent \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		"https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
		| jq -r '.data | sort_by(.updatedAt) | reverse | .[0].id'); \
	if [ -z "$$POSTMAN_SPEC_ID" ]; then \
		echo "❌ No spec found. Please create one first."; \
		exit 1; \
	fi; \
	echo "📤 Uploading $(OPENAPI_SPEC) as index.yaml to spec $$POSTMAN_SPEC_ID..."; \
	CONTENT=$$(jq -Rs . < $(OPENAPI_SPEC)); \
	jq -n \
		--arg path "index.yaml" \
		--arg content "$$CONTENT" \
		'{ path: $$path, content: $$content }' > postman/upload-root.json; \
	curl --silent \
		--location \
		--request POST \
		"https://api.getpostman.com/specs/$$POSTMAN_SPEC_ID/files" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data @postman/upload-root.json | jq .; \
	echo "🔗 Setting rootFilePath to index.yaml..."; \
	curl --silent \
		--location \
		--request PUT \
		"https://api.getpostman.com/specs/$$POSTMAN_SPEC_ID" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data '{"rootFilePath":"index.yaml"}' | jq .



.PHONY: postman-api-publish-fresh
postman-api-publish-fresh:
	@echo "🧹 Deleting all existing specs in workspace $(POSTMAN_WS)..."
	@SPECS=$$(curl --silent \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		"https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
		| jq -r '.data[].id'); \
	for ID in $$SPECS; do \
		echo "   ➡️ Deleting spec $$ID..."; \
		curl --silent --location \
			--request DELETE \
			"https://api.getpostman.com/specs/$$ID" \
			--header "X-Api-Key: $(POSTMAN_API_KEY)" \
			--header "Content-Type: application/json" | jq .; \
	done; \
	echo "🆕 Creating a new Postman Spec with $(OPENAPI_SPEC)..."; \
	CONTENT=$$(cat $(OPENAPI_SPEC) | jq -Rs .); \
	jq -n \
		--arg name "C2M Document Submission API" \
		--arg type "OPENAPI:3.0" \
		--arg path "index.yaml" \
		--arg content "$$CONTENT" \
		'{ name: $$name, type: $$type, files: [ { path: $$path, content: $$content | fromjson } ] }' \
		> postman/publish-payload.json; \
	curl --silent \
		--location \
		--request POST \
		"https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data @postman/publish-payload.json \
		| tee postman/api-publish-fresh-response.json | jq .; \
	SPEC_ID=$$(jq -r '.id // empty' postman/api-publish-fresh-response.json); \
	if [ -z "$$SPEC_ID" ]; then \
		echo "❌ Failed to create a fresh spec. See postman/api-publish-fresh-response.json."; \
		exit 1; \
	else \
		echo "✅ Fresh spec created with ID: $$SPEC_ID"; \
		echo "$$SPEC_ID" > postman/postman_spec_uid.txt; \
	fi


.PHONY: postman-api-update
postman-api-update:
	@echo "🔄 Updating existing Postman Spec with latest $(OPENAPI_SPEC)..."
	@if [ ! -f postman/postman_spec_uid.txt ]; then \
		echo "❌ Spec ID file (postman/postman_spec_uid.txt) not found. Run make postman-api-publish-fresh first."; \
		exit 1; \
	fi; \
	SPEC_ID=$$(cat postman/postman_spec_uid.txt); \
	echo "📄 Using Spec ID: $$SPEC_ID"; \
	CONTENT=$$(jq -Rs . < $(OPENAPI_SPEC)); \
	jq -n \
		--arg path "index.yaml" \
		--arg content "$$CONTENT" \
		'{ path: $$path, content: $$content | fromjson }' \
		> postman/update-payload.json; \
	curl --silent \
		--location \
		--request POST \
		"https://api.getpostman.com/specs/$$SPEC_ID/files" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data @postman/update-payload.json \
		| tee postman/api-update-response.json | jq .


.PHONY: postman-api-full-publish
postman-api-full-publish:
	@echo "🚀 Starting full Postman Spec publish..."
	@SPECS=$$(curl --silent \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		"https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
		| jq -r '.data[].id'); \
	if [ -n "$$SPECS" ]; then \
		echo "🧹 Deleting all existing specs in workspace $(POSTMAN_WS)..."; \
		for ID in $$SPECS; do \
			echo "   ➡️ Deleting spec $$ID..."; \
			curl --silent --location \
				--request DELETE \
				"https://api.getpostman.com/specs/$$ID" \
				--header "X-Api-Key: $(POSTMAN_API_KEY)" \
				--header "Content-Type: application/json" | jq .; \
		done; \
	else \
		echo "ℹ️ No existing specs found. Skipping deletion."; \
	fi; \
	echo "🆕 Creating a fresh Postman Spec..."; \
	CONTENT=$$(jq -Rs . < $(OPENAPI_SPEC)); \
	jq -n \
		--arg name "C2M Document Submission API" \
		--arg type "OPENAPI:3.0" \
		--arg path "index.yaml" \
		--arg content "$$CONTENT" \
		'{ name: $$name, type: $$type, files: [ { path: $$path, content: $$content | fromjson } ] }' \
		> postman/full-publish-payload.json; \
	curl --silent \
		--location \
		--request POST \
		"https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--data @postman/full-publish-payload.json \
		| tee postman/api-full-publish-response.json | jq .; \
	SPEC_ID=$$(jq -r '.id // empty' postman/api-full-publish-response.json); \
	if [ -z "$$SPEC_ID" ]; then \
		echo "❌ Failed to create a fresh spec. See postman/api-full-publish-response.json."; \
		exit 1; \
	else \
		echo "✅ Fresh spec created with ID: $$SPEC_ID"; \
		echo "$$SPEC_ID" > postman/postman_spec_uid.txt; \
	fi







.PHONY: postman-api-debug
postman-api-debug:
	@echo "🐞 Debugging Postman API key and workspace..."
	@echo "POSTMAN_API_KEY=$(POSTMAN_API_KEY)"
	@echo "POSTMAN_WS=$(POSTMAN_WS)"
	@echo "🔑 Verifying key..."
	@curl --silent \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		https://api.getpostman.com/me | jq .
	@echo "📂 Listing APIs in workspace $(POSTMAN_WS)..."
	@curl --silent \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		"https://api.getpostman.com/apis?workspaceId=$(POSTMAN_WS)" | jq .
	@echo "📜 Listing Specs in workspace $(POSTMAN_WS)..."
	@curl --silent \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		"https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" | jq .


.PHONY: postman-api-list-specs
postman-api-list-specs:
	@echo "📜 Listing all specs in workspace $(POSTMAN_WS)..."
	@curl --silent \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		"https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
		| jq -r '.data[] | "\(.name)\t\(.id)\t\(.type)\t\(.updatedAt)"' \
		| column -t -s$$'\t'




.PHONY: postman-spec-list
postman-spec-list:
	@echo "📥 Fetching all specs from Postman Spec Hub (workspace: $(POSTMAN_WS))..."
	curl --silent --location \
		--request GET "https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		| jq .




.PHONY: postman-api-delete-old-specs
postman-api-delete-old-specs:
	@echo "🧹 Deleting old specs in workspace $(POSTMAN_WS), keeping the most recent one..."
	@SPECS=$$(curl --silent \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		"https://api.getpostman.com/specs?workspaceId=$(POSTMAN_WS)" \
		| jq -r '.data | sort_by(.updatedAt) | reverse | .[1:] | .[].id'); \
	for ID in $$SPECS; do \
		echo "   ➡️ Deleting spec $$ID..."; \
		curl --silent --location \
			--request DELETE \
			"https://api.getpostman.com/specs/$$ID" \
			--header "X-Api-Key: $(POSTMAN_API_KEY)" \
			--header "Content-Type: application/json" \
			| jq .; \
	done; \
	if [ -z "$$SPECS" ]; then \
		echo "   No old specs to delete."; \
	else \
		echo "   ✅ Old specs deleted."; \
	fi


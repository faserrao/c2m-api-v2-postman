
# postman-api-update is not working and probably not necessary.
POSTMAN_API_URL        := https://api.getpostman.com/apis
POSTMAN_SCHEMA_PAYLOAD := postman/schema-update-payload.json
POSTMAN_SCHEMA_RESP    := postman/schema-update-response.json
POSTMAN_SCHEMA_FILE    := index.yaml

.PHONY: postman-api-update
postman-api-update:
	@echo "🔄 Updating existing Postman API schema with latest $(OPENAPI_SPEC)..."

	@if [ ! -f $(POSTMAN_API_ID_FILE) ] || [ ! -f $(POSTMAN_SCHEMA_ID_FILE) ]; then \
		echo "❌ API or Schema ID missing. Run make postman-api-full-publish first."; \
		exit 1; \
	fi

	@API_ID=$$(cat $(POSTMAN_API_ID_FILE)); \
	SCHEMA_ID=$$(cat $(POSTMAN_SCHEMA_ID_FILE)); \
	echo "📄 Using API ID: $$API_ID, Schema ID: $$SCHEMA_ID"; \

	@echo "📝 Building schema payload from $(OPENAPI_SPEC)..."; \
	CONTENT=$$(jq -Rs . < $(OPENAPI_SPEC)); \
	jq -n \
		--arg content "$$CONTENT" \
		'{ content: $$content | fromjson }' \
		> $(POSTMAN_SCHEMA_PAYLOAD)

	@echo "📤 Uploading updated schema to Postman..."; \
	curl --silent \
	  --request PUT "$(POSTMAN_API_URL)/$$API_ID/schemas/$$SCHEMA_ID" \
	  $(POSTMAN_CURL_HEADERS) \
	  --data @$(POSTMAN_SCHEMA_PAYLOAD) \
	  | tee $(POSTMAN_SCHEMA_RESP) | jq .

# --- Debugging Postman API Update ---
.PHONY: postman-api-debug
postman-api-debug:
	@echo "🐛 Debugging Postman API Update..."
	@if [ ! -f $(POSTMAN_SPEC_ID_FILE) ]; then \
		echo "❌ Spec ID file ($(POSTMAN_SPEC_ID_FILE)) not found. Run make postman-api-full-publish first."; \
		exit 1; \
	fi
	@SPEC_ID=$$(cat $(POSTMAN_SPEC_ID_FILE)); \
	echo "📄 Using Spec ID: $$SPEC_ID"; \
	echo "📤 Sending PATCH request (verbose)..."; \
	curl --verbose \
	  --request PATCH \
	  "https://api.getpostman.com/specs/$$SPEC_ID/files/index.yaml" \
	  --header "X-Api-Key: $(POSTMAN_API_KEY)" \
	  --header "Content-Type: application/json" \
	  --data @postman/update-payload.json
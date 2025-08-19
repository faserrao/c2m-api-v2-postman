# --- Import OpenAPI definition into Postman ---
.PHONY: postman-api-import
postman-api-import:
	@echo "📥 Importing OpenAPI definition $(OPENAPI_SPEC) into Postman workspace $(POSTMAN_WS)..."
	@API_RESPONSE=$$(curl --silent --fail --location --request POST "$(POSTMAN_APIS_URL)" \
		$(POSTMAN_CURL_HEADERS) \
		--data '$(POSTMAN_IMPORT_PAYLOAD)' || echo ""); \
		if [ -z "$$API_RESPONSE" ]; then \
			echo "❌ API request failed."; \
			exit 1; \
		fi; \
		echo "$$API_RESPONSE" | jq . > $(POSTMAN_IMPORT_DEBUG) || echo "$$API_RESPONSE" > $(POSTMAN_IMPORT_DEBUG); \
		API_ID=$$(jq -r '.id // empty' $(POSTMAN_IMPORT_DEBUG)); \
		if [ -z "$$API_ID" ]; then \
			echo "❌ Failed to import API. Check $(POSTMAN_IMPORT_DEBUG) for details."; \
			exit 1; \
		fi; \
		echo "✅ Imported API with ID: $$API_ID"; \
		echo "$$API_ID" > $(POSTMAN_API_UID_FILE); \
		echo "📄 API ID saved to $(POSTMAN_API_UID_FILE)";
.PHONY: prism-mock-test
prism-mock-test:
	@echo "🔬 Running Newman tests against Prism mock..."
	@if [ ! -f $(MOCK_URL_FILE_PRISM) ]; then \
		echo "ℹ️  Prism mock URL not found. Starting Prism..."; \
		$(MAKE) prism-start; \
		sleep 2; \
	fi
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
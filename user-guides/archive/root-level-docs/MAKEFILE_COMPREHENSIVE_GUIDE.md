# C2M API V2 Makefile Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Makefile Structure](#makefile-structure)
3. [Variable Sections](#variable-sections)
4. [Target Categories](#target-categories)
5. [Orchestration Targets](#orchestration-targets)
6. [Logic Targets](#logic-targets)
7. [Utility Targets](#utility-targets)
8. [CI/CD Targets](#cicd-targets)
9. [Advanced Features](#advanced-features)
10. [Best Practices](#best-practices)

## Overview

The C2M API V2 Makefile is a sophisticated build orchestration system that manages the entire pipeline from EBNF data dictionary to deployed API documentation. It follows the principle of composable targets, where complex operations are built from simpler, reusable components.

### Key Design Principles
- **Modularity**: Each target does one thing well
- **Composability**: Complex targets orchestrate simpler ones
- **Idempotency**: Targets can be run multiple times safely
- **Error Handling**: Fails fast with clear error messages
- **CI/CD Ready**: Includes specific targets for automation

## Makefile Structure

### File Organization
```makefile
# ========================================================================
# HEADER: Purpose, version, author
# ========================================================================

# ENVIRONMENT CONFIGURATION
# SHELL CONFIGURATION
# LOGGING HELPERS
# API NAMING CONVENTIONS
# DIRECTORY STRUCTURE
# FILE PATHS
# SCRIPTS
# PYTHON ENVIRONMENT
# EXTERNAL TOOLS

# PRIMARY TARGETS (User-facing)
# ORCHESTRATION TARGETS
# LOGIC TARGETS
# UTILITY TARGETS
# CI/CD ALIASES
# HELP SYSTEM
```

## Variable Sections

### 1. Environment Configuration
```makefile
# Load .env file if exists
-include .env

# Expected variables in .env:
#   POSTMAN_SERRAO_API_KEY=your-api-key
#   POSTMAN_C2M_API_KEY=alternate-api-key
```

### 2. Shell Configuration
```makefile
SHELL := bash
.ONESHELL:                    # Run all lines in recipe in single shell
.SHELLFLAGS := -eu -o pipefail -c  # Strict error handling
.DELETE_ON_ERROR:             # Delete target on recipe failure
V ?= 0                        # Verbosity level
Q := $(if $(filter 1,$(V)),,@)     # Quiet prefix
```

### 3. Logging and Validation Helpers
```makefile
# Color output helpers
say = @printf "%b\n" "$(1)"
ok  = $(call say,✅ $(1))
err = $(call say,❌ $(1))

# Guard helpers
guard-file = test -f "$(1)" || { echo "❌ Missing file: $(1)"; exit 1; }
guard-var  = test -n "$$($(1))" || { echo "❌ Missing var: $(1)"; exit 1; }
```

### 4. API Naming Conventions
```makefile
# Different case conventions for various contexts
C2MAPIV2_POSTMAN_API_NAME_PC := C2mApiV2      # PascalCase
C2MAPIV2_POSTMAN_API_NAME_CC := c2mApiV2      # camelCase
C2MAPIV2_POSTMAN_API_NAME_SC := c2mapiv2      # snake_case
C2MAPIV2_POSTMAN_API_NAME_KC := c2mapiv2      # kebab-case
POSTMAN_API_NAME := $(C2MAPIV2_POSTMAN_API_NAME_PC)
```

### 5. Directory Structure
```makefile
# Base directories
POSTMAN_DIR         := postman
OPENAPI_DIR         := openapi
SCRIPTS_DIR         := scripts
DOCS_DIR            := docs
DATA_DICT_DIR       := data_dictionary

# Subdirectories
POSTMAN_CUSTOM_DIR     := $(POSTMAN_DIR)/custom
POSTMAN_GENERATED_DIR  := $(POSTMAN_DIR)/generated
POSTMAN_ENV_DIR        := $(POSTMAN_DIR)/environments
SCRIPTS_ACTIVE_DIR     := $(SCRIPTS_DIR)/active
PYTHON_ENV_DIR         := $(SCRIPTS_DIR)/python_env
```

### 6. File Path Variables
```makefile
# OpenAPI specifications
C2MAPIV2_OPENAPI_SPEC := $(OPENAPI_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-openapi-spec-final.yaml
C2MAPIV2_OPENAPI_SPEC_BASE := $(OPENAPI_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-openapi-spec-base.yaml
C2MAPIV2_OPENAPI_SPEC_WITH_EXAMPLES := $(basename $(C2MAPIV2_OPENAPI_SPEC))-with-examples$(suffix $(C2MAPIV2_OPENAPI_SPEC))

# Postman collections
POSTMAN_COLLECTION_RAW := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-collection.json
POSTMAN_LINKED_COLLECTION := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-linked-collection-flat.json
POSTMAN_TEST_COLLECTION := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-test-collection-flat.json

# Tracking files
POSTMAN_COLLECTION_UID_FILE := $(POSTMAN_DIR)/postman_collection_uid.txt
POSTMAN_MOCK_URL_FILE := $(POSTMAN_DIR)/postman_mock_url.txt
POSTMAN_MOCK_ID_FILE := $(POSTMAN_DIR)/postman_mock_id.txt
```

### 7. Script Definitions

#### Core Pipeline Scripts
```makefile
EBNF_TO_OPENAPI_SCRIPT := $(SCRIPTS_DIR)/active/ebnf_to_openapi_dynamic_v3.py
FIX_COLLECTION_URLS    := $(SCRIPTS_DIR)/active/fix_collection_urls_v2.py
ADD_TESTS_SCRIPT       := $(SCRIPTS_DIR)/active/add_tests.js
MERGE_OPENAPI_OVERLAYS := $(SCRIPTS_DIR)/active/merge_openapi_overlays.py
```

#### OneOf Fix Scripts
```makefile
FIX_ONEOF_SCHEMAS      := $(SCRIPTS_DIR)/active/fix_openapi_oneOf_schemas.py
FIX_ONEOF_PLACEHOLDERS := $(SCRIPTS_DIR)/active/fix_oneOf_placeholders.js
```

#### Test Data Generation Scripts
```makefile
ADD_EXAMPLES_SCRIPT    := $(SCRIPTS_DIR)/test_data_generator_for_collections/addRandomDataToRaw.js
MERGE_CUSTOM_SCRIPT    := $(SCRIPTS_DIR)/utilities/merge_custom_into_generated.py
ADD_AUTH_PROVIDER      := $(SCRIPTS_DIR)/utilities/add-auth-provider-to-test-collection.js
```

#### JQ Transformations
```makefile
# Add info block to collection
JQ_ADD_INFO := --arg name "$$(POSTMAN_LINKED_COLLECTION_NAME)" \
               '. as $$c | {info: {name: $$name, schema: "$$(POSTMAN_SCHEMA_V2)"}, item: $$c.item}'

# Auto-fix empty folders
JQ_AUTO_FIX := jq 'walk(if type == "object" and (has("name") and (has("request") | not) and (has("item") | not)) then . + { "item": [] } else . end)'

# Fix URLs to use baseUrl variable
JQ_FIX_URLS := jq 'walk(if type == "object" and has("url") and (.url | type) == "object" and .url.raw then .url.raw |= sub("http://localhost"; "{{baseUrl}}") else . end)'

# Verify URLs
JQ_VERIFY_URLS := jq -r '.. | objects | select(has("url")) | .url.raw? // empty'
```

### 8. Python Environment
```makefile
PYTHON3 := python3
VENV_DIR := $(PYTHON_ENV_DIR)/e2o.venv
VENV_PIP := $(VENV_DIR)/bin/pip
VENV_PYTHON := $(VENV_DIR)/bin/python
INSTALL_PYTHON_MODULES := install -r $(PYTHON_ENV_DIR)/requirements.txt
```

### 9. External Tools

#### Node.js Tools
```makefile
GENERATOR_OFFICIAL := npx openapi-to-postmanv2
SPECTRAL           := npx @stoplight/spectral-cli
REDOCLY           := npx @redocly/cli
SWAGGER           := npx @apidevtools/swagger-cli
NEWMAN            := npx newman
```

#### Postman CLI
```makefile
POSTMAN_CLI   := postman
POSTMAN_LOGIN := $(POSTMAN_CLI) login --with-api-key
```

#### HTTP and Processing Tools
```makefile
CURL := curl -s
JQ   := jq
GREP := grep
SED  := sed
```

## Target Categories

### Primary User-Facing Targets

These are the main entry points for developers:

```makefile
.PHONY: help
help: ## Show this help message
	@echo "C2M API V2 - Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install all dependencies (npm and Python)

.PHONY: postman-instance-build-and-test
postman-instance-build-and-test: ## Complete pipeline build and test

.PHONY: postman-cleanup-all
postman-cleanup-all: ## Delete all Postman resources
```

## Orchestration Targets

These targets compose multiple operations into workflows:

### 1. Complete Pipeline Orchestration
```makefile
.PHONY: postman-instance-build-and-test
postman-instance-build-and-test:
	@echo "🚀 Starting Postman build and test..."
	$(MAKE) postman-login
	$(MAKE) postman-import-openapi-spec
	$(MAKE) postman-create-linked-collection
	$(MAKE) postman-create-test-collection  
	$(MAKE) postman-create-mock-and-env
	$(MAKE) postman-mock
	$(MAKE) postman-docs-build-and-serve-up
```

### 2. OpenAPI Build Orchestration
```makefile
.PHONY: ebnf-dd-to-openapi-spec
ebnf-dd-to-openapi-spec: venv
	$(MAKE) install
	$(MAKE) generate-openapi-spec-from-ebnf-dd
	$(MAKE) openapi-merge-overlays
	$(MAKE) openapi-spec-lint
```

### 3. Collection Build Orchestration
```makefile
.PHONY: postman-create-linked-collection
postman-create-linked-collection:
	$(MAKE) postman-api-linked-collection-generate
	$(MAKE) postman-linked-collection-flatten
	$(MAKE) postman-linked-collection-upload
```

### 4. Test Collection Orchestration
```makefile
.PHONY: postman-create-test-collection
postman-create-test-collection:
	$(MAKE) postman-test-collection-generate
	$(MAKE) postman-test-collection-add-examples || echo "⚠️  Skipping examples"
	$(MAKE) postman-test-collection-merge
	$(MAKE) postman-test-collection-add-tests
	$(MAKE) postman-test-collection-add-auth-provider
	$(MAKE) postman-test-collection-fix-urls
	$(MAKE) postman-test-collection-validate
	$(MAKE) postman-test-collection-flatten  
	$(MAKE) postman-test-collection-upload
```

### 5. Cleanup Orchestration
```makefile
.PHONY: postman-cleanup-all
postman-cleanup-all:
	@echo "🧹 Starting FULL cleanup..."
	$(MAKE) postman-delete-mock-servers
	$(MAKE) postman-delete-collections
	$(MAKE) postman-delete-apis
	$(MAKE) postman-delete-environments
	$(MAKE) postman-api-clean-trash
	$(MAKE) postman-delete-specs
	@echo "✅ Postman cleanup complete"
```

## Logic Targets

These perform the actual work:

### 1. EBNF to OpenAPI Conversion
```makefile
.PHONY: generate-openapi-spec-from-ebnf-dd
generate-openapi-spec-from-ebnf-dd:
	@echo "📤 Converting EBNF to OpenAPI..."
	@$(call guard-file,$(EBNF_TO_OPENAPI_SCRIPT))
	@$(call guard-file,$(DD_EBNF_FILE))
	# Create venv if needed
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON3) -m venv "$(VENV_DIR)"; \
	fi
	# Run conversion
	$(VENV_PYTHON) $(EBNF_TO_OPENAPI_SCRIPT) -o $(C2MAPIV2_OPENAPI_SPEC_BASE) $(DD_EBNF_FILE)
	# Fix anonymous oneOf schemas
	$(VENV_PYTHON) $(FIX_ONEOF_SCHEMAS) $(C2MAPIV2_OPENAPI_SPEC_BASE) $(C2MAPIV2_OPENAPI_SPEC_BASE)
	@echo "✅ OneOf schemas fixed"
```

### 2. Collection Generation
```makefile
.PHONY: postman-api-linked-collection-generate
postman-api-linked-collection-generate: | $(POSTMAN_DIR)
	@mkdir -p $(POSTMAN_GENERATED_DIR)
	@echo "📦 Generating Postman collection..."
	$(GENERATOR_OFFICIAL) -s $(C2MAPIV2_OPENAPI_SPEC_WITH_EXAMPLES) -o $(POSTMAN_COLLECTION_RAW) -p
	# Add metadata
	@jq $(JQ_ADD_INFO) $(POSTMAN_COLLECTION_RAW) > $(POSTMAN_COLLECTION_RAW).tmp
	@mv $(POSTMAN_COLLECTION_RAW).tmp $(POSTMAN_COLLECTION_RAW)
	# Fix oneOf placeholders
	@node $(FIX_ONEOF_PLACEHOLDERS) $(POSTMAN_COLLECTION_RAW) $(POSTMAN_COLLECTION_RAW)
	@echo "✅ OneOf placeholders fixed"
```

### 3. Mock Server Creation
```makefile
.PHONY: postman-mock-create
postman-mock-create:
	@echo "🎭 Creating mock server..."
	$(call guard-var,POSTMAN_API_KEY)
	$(call guard-var,POSTMAN_WORKSPACE_ID)
	@COLLECTION_UID=$$(cat $(POSTMAN_TEST_UID_FILE) 2>/dev/null || echo "") && \
	test -n "$$COLLECTION_UID" || { echo "❌ No test collection UID"; exit 1; } && \
	RESPONSE=$$($(CURL) -X POST "$(POSTMAN_BASE_URL)/mocks?workspace=$(POSTMAN_WORKSPACE_ID)" \
		-H "X-Api-Key: $(POSTMAN_API_KEY)" \
		-H "Content-Type: application/json" \
		-d '{"mock": {"collection": "'$$COLLECTION_UID'", "name": "$(MOCK_SERVER_NAME)", "private": false}}') && \
	MOCK_ID=$$(echo "$$RESPONSE" | jq -r '.mock.id') && \
	MOCK_URL=$$(echo "$$RESPONSE" | jq -r '.mock.mockUrl') && \
	echo "$$MOCK_ID" > $(POSTMAN_MOCK_ID_FILE) && \
	echo "$$MOCK_URL" > $(POSTMAN_MOCK_URL_FILE) && \
	echo "✅ Mock server created. URL=$$MOCK_URL"
```

### 4. Test Execution
```makefile
.PHONY: postman-mock
postman-mock: $(NEWMAN) guard-postman-test-collection guard-postman-mock-env
	@echo "🧪 Running tests against Postman mock server..."
	@MOCK_URL=$$(cat $(POSTMAN_MOCK_URL_FILE) 2>/dev/null) && \
	test -n "$$MOCK_URL" || { echo "❌ No mock URL found"; exit 1; } && \
	$(NEWMAN) run $(POSTMAN_TEST_COLLECTION) \
		-e $(POSTMAN_ENV_FILE) \
		--env-var "baseUrl=$$MOCK_URL" \
		--reporters cli,html \
		--reporter-html-export $(POSTMAN_DIR)/newman-report.html && \
	echo "📄 Newman test report generated at $(POSTMAN_DIR)/newman-report.html"
```

## Utility Targets

### 1. Validation Utilities
```makefile
.PHONY: postman-test-collection-validate
postman-test-collection-validate:
	@echo "🔍 Validating collection structure..."
	@$(call guard-file,$(TEST_COLLECTION_FILE))
	@node -e "JSON.parse(require('fs').readFileSync('$(TEST_COLLECTION_FILE)'))" && \
	echo "✅ Collection is valid."

.PHONY: openapi-spec-lint
openapi-spec-lint:
	$(REDOCLY) lint $(C2MAPIV2_OPENAPI_SPEC)
	$(SPECTRAL) lint $(C2MAPIV2_OPENAPI_SPEC)
```

### 2. Debug Utilities
```makefile
.PHONY: print-openapi-vars
print-openapi-vars:
	@echo "OPENAPI_DIR = $(OPENAPI_DIR)"
	@echo "C2MAPIV2_OPENAPI_SPEC = $(C2MAPIV2_OPENAPI_SPEC)"
	@echo "C2MAPIV2_OPENAPI_SPEC_BASE = $(C2MAPIV2_OPENAPI_SPEC_BASE)"

.PHONY: postman-workspace-debug
postman-workspace-debug:
	@echo "🔍 Debugging workspace $(POSTMAN_WORKSPACE_ID)..."
	@$(CURL) "$(POSTMAN_BASE_URL)/workspaces/$(POSTMAN_WORKSPACE_ID)" \
		-H "X-Api-Key: $(POSTMAN_API_KEY)" | jq '.'
```

### 3. URL Verification
```makefile
.PHONY: verify-urls
verify-urls:
	@echo "🔍 Verifying collection URLs..."
	@cat $(POSTMAN_TEST_COLLECTION) | $(JQ_VERIFY_URLS) | sort | uniq | \
	while read url; do \
		if echo "$$url" | grep -q "{{baseUrl}}"; then \
			echo "✅ $$url"; \
		else \
			echo "❌ $$url (missing variable)"; \
		fi \
	done
```

### 4. Python Environment
```makefile
.PHONY: venv
venv: $(VENV_DIR)/bin/activate

$(VENV_DIR)/bin/activate:
	@echo "🐍 Creating Python virtual environment..."
	@test -d $(VENV_DIR) || $(PYTHON3) -m venv $(VENV_DIR)
	@test -x "$(VENV_PIP)" || { echo "🐍 Creating venv"; $(PYTHON3) -m venv "$(VENV_DIR)"; }
	@$(VENV_PIP) install --upgrade pip setuptools wheel
	@touch $(VENV_DIR)/bin/activate

.PHONY: fix-yaml
fix-yaml: venv
	@echo "🔧 Fixing PyYAML..."
	@$(VENV_PIP) uninstall -y pyyaml
	@$(VENV_PIP) --no-cache-dir install pyyaml
```

## CI/CD Targets

These are aliases optimized for GitHub Actions:

### 1. Build Targets
```makefile
.PHONY: openapi-build
openapi-build: generate-openapi-spec-from-ebnf-dd ## Build OpenAPI from EBNF [CI alias]
	$(MAKE) openapi-merge-overlays
	$(MAKE) openapi-spec-lint

.PHONY: postman-collection-build
postman-collection-build: ## Generate collections [CI alias]
	$(MAKE) postman-api-linked-collection-generate
	$(MAKE) postman-linked-collection-flatten

.PHONY: docs
docs: docs-build ## Build API documentation [CI alias]
```

### 2. Publish Targets
```makefile
.PHONY: postman-publish
postman-publish: ## Publish to workspace based on .postman-target
	@if [ -f .postman-target ]; then \
		TARGET=$$(cat .postman-target); \
		echo "📍 Publishing to $$TARGET workspace..."; \
		$(MAKE) postman-publish-$$TARGET; \
	else \
		echo "📍 No .postman-target found, using personal"; \
		$(MAKE) postman-publish-personal; \
	fi

.PHONY: postman-publish-personal
postman-publish-personal: ## Publish to personal workspace
	$(MAKE) POSTMAN_API_KEY=$(POSTMAN_SERRAO_API_KEY) \
		POSTMAN_WORKSPACE_ID=$(SERRAO_WORKSPACE_ID) \
		_postman-publish-impl

.PHONY: postman-publish-corporate  
postman-publish-corporate: ## Publish to corporate workspace
	$(MAKE) POSTMAN_API_KEY=$(POSTMAN_C2M_API_KEY) \
		POSTMAN_WORKSPACE_ID=$(C2M_WORKSPACE_ID) \
		_postman-publish-impl
```

## Advanced Features

### 1. Smart Rebuild System
```makefile
.PHONY: smart-rebuild
smart-rebuild: ## Intelligently rebuild only changed components
	@echo "🔍 Checking for changes..."
	@bash $(SCRIPTS_DIR)/utilities/smart-rebuild.sh

.PHONY: smart-rebuild-status
smart-rebuild-status: ## Show build state and hashes
	@bash $(SCRIPTS_DIR)/utilities/smart-rebuild.sh status

.PHONY: smart-rebuild-clean
smart-rebuild-clean: ## Clear hash cache
	@rm -rf .build-cache/
	@echo "✅ Build cache cleared"
```

### 2. Guard Functions
```makefile
# File guards
guard-postman-collection-raw:
	@$(call guard-file,$(POSTMAN_COLLECTION_RAW))

guard-postman-test-collection:
	@$(call guard-file,$(POSTMAN_TEST_COLLECTION))

# Variable guards
guard-postman-api-key:
	@$(call guard-var,POSTMAN_API_KEY)

guard-postman-workspace:
	@$(call guard-var,POSTMAN_WORKSPACE_ID)
```

### 3. Conditional Logic
```makefile
# Skip test data if script missing
postman-test-collection-add-examples:
	@if [ -f "$(ADD_EXAMPLES_SCRIPT)" ]; then \
		node $(ADD_EXAMPLES_SCRIPT) --input $(INPUT) --output $(OUTPUT); \
	else \
		echo "⚠️  Examples script not found, skipping"; \
	fi
```

### 4. Error Recovery
```makefile
# Continue on optional failures
postman-create-test-collection:
	$(MAKE) postman-test-collection-generate
	$(MAKE) postman-test-collection-add-examples || echo "⚠️  Skipping examples (optional)"
	$(MAKE) postman-test-collection-merge
```

## Best Practices

### 1. Target Naming
- Use descriptive names with namespace prefixes
- `postman-*` for Postman operations
- `openapi-*` for OpenAPI operations
- `docs-*` for documentation

### 2. Dependencies
- Use prerequisites for file dependencies
- Use order-only prerequisites for directories
- Guard functions for runtime checks

### 3. Output Management
- Prefix output with emojis for clarity
- Use `@echo` for user messages
- Redirect verbose output to `/dev/null`

### 4. Variable Usage
- Define at top of Makefile
- Use descriptive names
- Group related variables

### 5. Error Handling
- Fail fast with clear messages
- Use guards for preconditions
- Provide recovery suggestions

### 6. Composition
- Build complex targets from simple ones
- Keep each target focused
- Use orchestration targets for workflows

### 7. Documentation
- Add `## Description` comments for help
- Document complex logic inline
- Keep README synchronized

## Common Patterns

### 1. API Key Selection
```makefile
# Dynamic API key selection
POSTMAN_API_KEY ?= $(POSTMAN_SERRAO_API_KEY)
ifeq ($(WORKSPACE_TYPE),corporate)
	POSTMAN_API_KEY := $(POSTMAN_C2M_API_KEY)
endif
```

### 2. File Tracking
```makefile
# Save IDs for later reference
echo "$$COLLECTION_UID" > $(POSTMAN_COLLECTION_UID_FILE)
# Read saved IDs
COLLECTION_UID=$$(cat $(POSTMAN_COLLECTION_UID_FILE) 2>/dev/null || echo "")
```

### 3. JSON Processing
```makefile
# Extract value with jq
MOCK_ID=$$(echo "$$RESPONSE" | jq -r '.mock.id')
# Transform structure
jq '.info.name = "NewName"' input.json > output.json
```

### 4. Conditional Execution
```makefile
# Check file existence
@if [ -f "$(FILE)" ]; then \
	echo "Processing $(FILE)"; \
	process_command $(FILE); \
fi
```

## Debugging Tips

### 1. Verbose Mode
```bash
make V=1 target  # Show all commands
```

### 2. Dry Run
```bash
make -n target  # Show commands without executing
```

### 3. Debug Variables
```bash
make print-openapi-vars
make print-postman-vars
```

### 4. Trace Execution
```bash
make -d target  # Full debug output
```

### 5. Check Prerequisites
```bash
make -p | grep "^target:"  # Show target dependencies
```

## Maintenance Guide

### Adding New Targets
1. Choose appropriate namespace
2. Add to correct section
3. Include help comment
4. Test in isolation
5. Add to orchestration if needed

### Updating Dependencies
1. Check `requirements.txt` for Python
2. Update tool versions in variables
3. Test full pipeline after changes
4. Update CI/CD if needed

### Refactoring
1. Extract common patterns to functions
2. Create orchestration for complex flows
3. Keep backwards compatibility
4. Document breaking changes
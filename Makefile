# ========================================================================
# C2M API V2 - Postman Integration Makefile
# ========================================================================
# Purpose: Automates the complete workflow from EBNF data dictionary to
#          OpenAPI specification, Postman collections, mock servers, and
#          API documentation.
#
# Author: [Your Name]
# Version: 2.1.0
# Last Updated: 2024-11-19
#
# Architecture Flow:
#   EBNF Data Dictionary → OpenAPI Spec → Postman Collection → Mock Server → Documentation
#
# Usage:
#   make help                          # Show all available targets
#   make postman-instance-build-and-test  # Run complete pipeline
#   make postman-cleanup-all           # Clean all Postman resources
#
# Load environment variables from .env file if it exists
-include .env

# Prerequisites:
#   - Node.js and npm
#   - Python 3
#   - Postman API key (set in .env file)
#   - curl, jq, and basic Unix tools
# ========================================================================

# Place this line at the top of your Makefile
VARS_OLD := $(.VARIABLES)

# ========================================================================
# ENVIRONMENT CONFIGURATION
# ========================================================================
# Load local environment variables from .env if present
# Expected variables in .env:
#   POSTMAN_SERRAO_API_KEY=your-api-key
#   POSTMAN_C2M_API_KEY=alternate-api-key
ifneq (,$(wildcard .env))
    include .env
    export $(shell sed 's/=.*//' .env)
endif

# ========================================================================
# SHELL CONFIGURATION
# ========================================================================
# Set strict shell options for safety:
# -e: Exit on error
# -u: Error on undefined variables
# -o pipefail: Fail on pipe errors
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
V ?= 0
Q := $(if $(filter 1,$(V)),,@)

# ========================================================================
# LOGGING AND VALIDATION HELPERS
# ========================================================================
# Simple log helpers for consistent output formatting
say = @printf "%b\n" "$(1)"
ok    = $(call say,✅ $(1))
err = $(call say,❌ $(1))

# Guard helpers to ensure files and variables exist before use
guard-file    = test -f "$(1)" || { echo "❌ Missing file: $(1)"; exit 1; }
guard-var        = test -n "$$($(1))" || { echo "❌ Missing var: $(1)"; exit 1; }

# ========================================================================
# API NAMING CONVENTIONS
# ========================================================================
# Different case conventions for various contexts:
# PascalCase
C2MAPIV2_POSTMAN_API_NAME_PC    := C2mApiV2
# camelCase
C2MAPIV2_POSTMAN_API_NAME_CC    := c2mApiV2
# snake_case
C2MAPIV2_POSTMAN_API_NAME_SC    := c2mapiv2
# kebab-case
C2MAPIV2_POSTMAN_API_NAME_KC    := c2mapiv2
POSTMAN_API_NAME                 := $(C2MAPIV2_POSTMAN_API_NAME_PC)

# ========================================================================
# DIRECTORY STRUCTURE
# ========================================================================
# All paths are relative to the Makefile location
POSTMAN_DIR                      := postman
POSTMAN_ENV_FILE                 := $(POSTMAN_DIR)/mock-env.json
POSTMAN_BASE_URL                 := https://api.getpostman.com
LOCALHOST_URL                    := http://127.0.0.1

#--- Directories ---
# User customizations
POSTMAN_CUSTOM_DIR               := $(POSTMAN_DIR)/custom
# Auto-generated files
POSTMAN_GENERATED_DIR            := $(POSTMAN_DIR)/generated
# Generated SDKs
SDKS_DIR                         := sdks
# Helper scripts
SCRIPTS_DIR                      := scripts
# Documentation output
DOCS_DIR                         := docs
# EBNF source files
DATA_DICT_DIR                    := data_dictionary
# Doc templates
TEMPLATES_DIR                    := $(DOCS_DIR)/templates

# --- Files ---
DD_EBNF_FILE                     := $(DATA_DICT_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_SC)-dd.ebnf
REDOC_HTML_OUTPUT                := $(DOCS_DIR)/index.html
DOCS_PID_FILE                    := $(DOCS_DIR)/http_pid.txt

# ========================================================================
# POSTMAN API CONFIGURATION
# ========================================================================
#--- Postman API Variables ---
POSTMAN_API_UID_FILE             := $(POSTMAN_DIR)/postman_api_uid.txt
POSTMAN_API_VERSION_FILE         := $(POSTMAN_DIR)/postman_api_version.txt
POSTMAN_APIS_URL                 := $(POSTMAN_BASE_URL)/apis

#--- OpenAPI Specification Variables ---
OPENAPI_DIR                      := openapi
C2MAPIV2_OPENAPI_SPEC            := $(OPENAPI_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-openapi-spec-final.yaml
C2MAPIV2_MAIN_SPEC_PATH          := origin/main:$(C2MAPIV2_OPENAPI_SPEC)
POSTMAN_SPEC_ID_FILE             := $(POSTMAN_DIR)/postman_spec_uid.txt
C2MAPIV2_OPENAPI_SPEC_WITH_EXAMPLES := $(basename $(C2MAPIV2_OPENAPI_SPEC))-with-examples$(suffix $(C2MAPIV2_OPENAPI_SPEC))
PREVIOUS_C2MAPIV2_OPENAPI_SPEC   := $(OPENAPI_DIR)/tmp-previous-spec.yaml
POSTMAN_SPECS_URL                := $(POSTMAN_BASE_URL)/specs
POSTMAN_SCHEMA_V2                := https://schema.getpostman.com/json/collection/v2.1.0/collection.json
POSTMAN_SCHEMA_UID_FILE          := $(POSTMAN_DIR)/schema_uid.txt

#--- OpenAPI Overlays ---
OPENAPI_OVERLAYS_DIR             := $(OPENAPI_DIR)/overlays
OPENAPI_AUTH_OVERLAY             := $(OPENAPI_OVERLAYS_DIR)/auth.tokens.yaml
C2MAPIV2_OPENAPI_SPEC_BASE       := $(OPENAPI_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-openapi-spec-base.yaml
OPENAPI_BUNDLED_FILE             := $(OPENAPI_DIR)/bundled.yaml

# ========================================================================
# POSTMAN COLLECTION CONFIGURATION
# ========================================================================
# Same collection file is used to create both the linked collection and the test collection
POSTMAN_COLLECTION_RAW           := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-collection.json

#--- Postman Testing Collection Variables ---
POSTMAN_TEST_COLLECTION_NAME     := $(C2MAPIV2_POSTMAN_API_NAME_PC)TestCollection
POSTMAN_TEST_COLLECTION_TMP      := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-test-collection-tmp.json
POSTMAN_TEST_COLLECTION_FIXED    := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-test-collection-fixed.json
POSTMAN_TEST_COLLECTION_MERGED   := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-test-collection-merged.json
POSTMAN_TEST_COLLECTION_FINAL    := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-test-collection-final.json
POSTMAN_TEST_COLLECTION_UID_FILE := $(POSTMAN_DIR)/test_collection_uid.txt
POSTMAN_TEST_COLLECTION_UID      := $(shell cat $(POSTMAN_TEST_COLLECTION_UID_FILE) 2>/dev/null || echo "")
POSTMAN_TEST_COLLECTION_WITH_EXAMPLES := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-test-collection-with-examples.json
POSTMAN_TEST_COLLECTION_WITH_TESTS := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-test-collection-with-tests.json
POSTMAN_TEST_COLLECTION_FIXED_WITH_TESTS := $(basename $(POSTMAN_TEST_COLLECTION_FIXED))-with-tests.json

#--- Linked Collection Variables ---
POSTMAN_LINKED_COLLECTION_UID_FILE := $(POSTMAN_DIR)/postman_linked_collection_uid.txt
POSTMAN_LINKED_COLLECTION_UID    := $(shell cat $(POSTMAN_LINKED_COLLECTION_UID_FILE))
POSTMAN_LINKED_COLLECTION_TMP    := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-linked-collection-tmp.json
# TODO: Base collection name api name like we did for the test collection
POSTMAN_LINKED_COLLECTION_NAME   := C2mApiCollectionLinked
POSTMAN_COLLECTIONS_URL          := $(POSTMAN_BASE_URL)/collections

# ========================================================================
# POSTMAN DEBUG AND PAYLOAD FILES
# ========================================================================
# Files used for debugging API interactions and storing payloads
POSTMAN_IMPORT_DEBUG             := $(POSTMAN_DIR)/import-debug.json
POSTMAN_LINK_PAYLOAD             := $(POSTMAN_DIR)/link-payload.json
POSTMAN_LINK_DEBUG               := $(POSTMAN_DIR)/link-debug.json
POSTMAN_VERSION_PAYLOAD          := $(POSTMAN_DIR)/version-payload.json
POSTMAN_VERSION_DEBUG            := $(POSTMAN_DIR)/version-debug.json
POSTMAN_IMPORT_PAYLOAD           := $(POSTMAN_DIR)/import-payload.json
POSTMAN_FULL_PAYLOAD             := $(POSTMAN_DIR)/full-publish-payload.json
POSTMAN_FULL_RESPONSE            := $(POSTMAN_DIR)/api-full-publish-response.json

# ========================================================================
# POSTMAN ENVIRONMENT CONFIGURATION
# ========================================================================
#--- Postman Environment Variables ---
POSTMAN_ENV_NAME                 := $(C2MAPIV2_POSTMAN_API_NAME_PC)Env
POSTMAN_ENV_FILE_TEMP            := $(POSTMAN_DIR)/mock-env-temp.json
POSTMAN_ENV_FILE_NEW             := $(POSTMAN_DIR)/mock-env-new.json
POSTMAN_ENV_UID_FILE             := $(POSTMAN_DIR)/postman_env_uid.txt
POSTMAN_ENV_UID                  := $(shell cat $(POSTMAN_ENV_UID_FILE))
POSTMAN_ENV_UPLOAD_DEBUG         := $(POSTMAN_DIR)/env-upload-debug.json
POSTMAN_ENVIRONMENTS_URL         := $(POSTMAN_BASE_URL)/environments

# ========================================================================
# POSTMAN MOCK SERVER CONFIGURATION
# ========================================================================
#--- Postman Mock Variables ---
POSTMAN_MOCK_NAME                := $(POSTMAN_API_NAME)MockServer
POSTMAN_MOCK_PAYLOAD             := $(POSTMAN_DIR)/mock-payload.json
POSTMAN_MOCK_DEBUG               := $(POSTMAN_DIR)/mock-debug.json
POSTMAN_MOCK_VALIDATE            := $(POSTMAN_DIR)/mock-validate.json
POSTMAN_MOCK_UID_FILE            := $(POSTMAN_DIR)/postman_mock_uid.txt
POSTMAN_MOCK_LINK_DEBUG_FILE     := $(POSTMAN_DIR)/postman-mock-link-debug.json
POSTMAN_MOCK_UID                 := $(shell cat $(POSTMAN_MOCK_UID_FILE) 2>/dev/null || echo "")
POSTMAN_MOCK_URL_FILE            := $(POSTMAN_DIR)/postman_mock_url.txt
POSTMAN_MOCKS_URL                := $(POSTMAN_BASE_URL)/mocks
POSTMAN_MOCK_URL                 := $(shell cat $(POSTMAN_MOCK_URL_FILE) 2>/dev/null || echo "https://mock.api")
POSTMAN_MOCK_ID_FILE             := $(POSTMAN_DIR)/postman_mock_id.txt
POSTMAN_MOCK_ID                  := $(shell cat $(POSTMAN_MOCK_ID_FILE) 2>/dev/null || echo "")

# ========================================================================
# PRISM MOCK SERVER CONFIGURATION
# ========================================================================
# Prism is a local mock server that runs on your machine
PRISM_LOG                        ?= $(POSTMAN_DIR)/prism.log
PRISM_PID_FILE                   ?= $(POSTMAN_DIR)/prism_pid.txt
PRISM_MOCK_TEST                  ?= $(POSTMAN_DIR)/prism-mock-test-results.json
PRISM_MOCK_TEST_REPORT           ?= $(POSTMAN_DIR)/prism-mock-test-report.html
PRISM_PORT                       ?= 4010
PRISM_HOST                       ?= 127.0.0.1
PRISM_MOCK_URL_FILE              ?= $(POSTMAN_DIR)/prism_mock_url.txt
PRISM_MOCK_URL                   ?= $(shell cat $(PRISM_MOCK_URL_FILE) 2>/dev/null || echo "$(LOCALHOST_URL):$(PRISM_PORT)")

# Spec file path (override if needed)
PRISM_SPEC                       ?= $(C2MAPIV2_OPENAPI_SPEC_WITH_EXAMPLES)

# ========================================================================
# TESTING CONFIGURATION
# ========================================================================
#--- Postman Testing Variables ---
POSTMAN_OVERRIDES_FILE           := $(POSTMAN_CUSTOM_DIR)/overrides.json
POSTMAN_UPLOAD_TEST_DEBUG        := $(POSTMAN_DIR)/upload-test-debug.json
TEST_DATA_DIR                    := test-data
REPORT_HTML                      := $(POSTMAN_DIR)/newman-report.html

# Security scripts (for auth provider)
# Check if running in CI (GitHub Actions sets CI environment variable)
ifdef CI
SECURITY_POSTMAN_SCRIPTS_DIR     := c2m-api-v2-security/postman/scripts
else
SECURITY_POSTMAN_SCRIPTS_DIR     := ../c2m-api-v2-security/postman/scripts
endif
# Token updated 2025-09-09

# Default allowed status codes (comma-separated)
POSTMAN_ALLOWED_CODES            ?= 200,201,204,400,401,403,404,429
# JWT test collection output
TEST_COLLECTION_WITH_JWT_TESTS   := $(POSTMAN_DIR)/generated/c2mapiv2-test-collection-jwt.json

# ========================================================================
# JQ FILTERS AND SCRIPTS
# ========================================================================
# ---- jq filters (centralized) ----
# These filters manipulate JSON data throughout the pipeline
JQ_DIR                           := scripts/jq
JQ_ADD_INFO_FILE                 := $(JQ_DIR)/add_info.jq
JQ_FIX_URLS_FILE                 := $(JQ_DIR)/fix_urls.jq
JQ_AUTO_FIX_FILE                 := $(JQ_DIR)/auto_fix.jq
JQ_VERIFY_URLS_FILE              := $(JQ_DIR)/verify_urls.jq
JQ_SANITIZE_COLLECTION_FILE      := $(JQ_DIR)/sanitize_collection.jq

# tiny runners for jq operations
jqf = jq -f $(1) $(2)
jqx = jq $(1) $(2)

# ========================================================================
# CURL HELPERS
# ========================================================================
# ---- curl helpers ----
# Basic JSON POST/PUT/GET with our canonical headers
define curl_json
curl --silent --show-error --fail --location \
    $(POSTMAN_CURL_HEADERS_XC) $(1) $(2)
endef

# Same but also adds Accept+Auth (some Postman endpoints expect them)
define curl_json_xcaa
curl --silent --show-error --fail --location \
    $(POSTMAN_CURL_HEADERS_XC) $(POSTMAN_CURL_HEADERS_AA) $(1) $(2)
endef

# ========================================================================
# SCRIPT PATHS
# ========================================================================
#--- SCRIPTS ---
ADD_EXAMPLES_TO_OPENAPI_SPEC     := $(SCRIPTS_DIR)/test_data_genertor_for_openapi_specs/add_examples_to_spec.py $(C2MAPIV2_OPENAPI_SPEC)
ADD_TESTS_SCRIPT                 := $(SCRIPTS_DIR)/active/add_tests.js
EBNF_TO_OPENAPI_SCRIPT           := $(SCRIPTS_DIR)/active/ebnf_to_openapi_dynamic_v3.py
FIX_COLLECTION_URLS              := $(SCRIPTS_DIR)/active/fix_collection_urls_v2.py
FIX_PATHS_SCRIPT                 := $(SCRIPTS_DIR)/jq/fix_paths.jq
JQ_ADD_INFO                      := --arg name "$$(POSTMAN_LINKED_COLLECTION_NAME)" '. as $$c | {info: {name: $$name, schema: "$$(POSTMAN_SCHEMA_V2)"}, item: $$c.item}'
JQ_AUTO_FIX                      := jq 'walk(if type == "object" and (has("name") and (has("request") | not) and (has("item") | not)) then . + { "item": [] } else . end)'
JQ_FIX_URLS                      := jq 'walk(if type == "object" and has("url") and (.url | type) == "object" and .url.raw then .url.raw |= sub("http://localhost"; "{{baseUrl}}") else . end)'
JQ_VERIFY_URLS                   := jq -r '.. | objects | select(has("url")) | .url.raw? // empty'
MERGE_POSTMAN_OVERRIDES          := $(SCRIPTS_DIR)/jq/merge_overrides.jq
MERGE_SCRIPT                     := $(SCRIPTS_DIR)/jq/merge.jq
NODE_COLLECTION_VALIDATE         := node -e "const {Collection}=require('postman-collection'); const fs=require('fs'); const data=JSON.parse(fs.readFileSync('$(POSTMAN_TEST_COLLECTION_FIXED)','utf8')); try { new Collection(data); console.log('✅ Collection is valid.'); } catch(e) { console.error('❌ Validation failed:', e.message); process.exit(1); }"
POSTMAN_VALIDATOR                := $(SCRIPTS_DIR)/active/validate_collection.js
INSTALL_PYTHON_MODULES           := install -r $(SCRIPTS_DIR)/python_env/requirements.txt

ADD_EXAMPLES_TO_COLLECTION_SCRIPT := node $(SCRIPTS_DIR)/test_data_generator_for_collections/addRandomDataToRaw.js
ADD_EXAMPLES_TO_COLLECTION_ARGS  := --input  $(POSTMAN_COLLECTION_RAW) --output $(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES)
ADD_EXAMPLES_TO_COLLECTION       := $(ADD_EXAMPLES_TO_COLLECTION_SCRIPT) $(ADD_EXAMPLES_TO_COLLECTION_ARGS)

# ========================================================================
# PYTHON VIRTUAL ENVIRONMENT
# ========================================================================
# --- Python Virtual Environment ---
# Isolated Python environment for conversion scripts
PYTHON_ENV_DIR                   := $(SCRIPTS_DIR)/python_env
VENV_DIR                         := $(PYTHON_ENV_DIR)/e2o.venv
VENV_PIP                         := $(VENV_DIR)/bin/pip
VENV_PYTHON                      := $(VENV_DIR)/bin/python
PYTHON3                          := python3
PYTHON                           := $(PYTHON3)

# ========================================================================
# EXTERNAL TOOLS
# ========================================================================
#--- Tools ---
# These tools are installed via npm in the install target
GENERATOR_OFFICIAL               := npx openapi-to-postmanv2
PRISM                            := npx @stoplight/prism-cli
NEWMAN                           := npx newman
REDOCLY                          := npx @redocly/cli
SPECTRAL                         := npx @stoplight/spectral-cli
SWAGGER                          := npx swagger-cli
WIDDERSHINS                      := npx widdershins
OPENAPI_DIFF                     := npx openapi-diff

# ========================================================================
# POSTMAN WORKSPACE AND AUTHENTICATION
# ========================================================================
#--- Postman Workspaces ---
SERRAO_WS                        := d8a1f479-a2aa-4471-869e-b12feea0a98c
C2M_WS                           := c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1

#--- Default workspace configuration ---
# Default to personal workspace, allow override
POSTMAN_WS                       := $(or $(POSTMAN_WORKSPACE_OVERRIDE),$(SERRAO_WS))
# Check for API key in environment first (for GitHub Actions), then fall back to override
POSTMAN_API_KEY                  := $(or $(POSTMAN_API_KEY_OVERRIDE),$(POSTMAN_SERRAO_API_KEY),$(POSTMAN_C2M_API_KEY))

#--- TOKENS ---
# Extract token from environment file if it exists
TOKEN_RAW                        := $(shell [ -f $(POSTMAN_ENV_FILE) ] && jq -r '.environment.values[] | select(.key=="token") | .value' $(POSTMAN_ENV_FILE) 2>/dev/null || echo "")
TOKEN                            := $(if $(TOKEN_RAW),$(TOKEN_RAW),dummy-token)

# ========================================================================
# HTTP HEADERS
# ========================================================================
#--- Postman HTTP Headers ---
POSTMAN_HEADER_API_KEY           := --header "X-Api-Key: $(POSTMAN_API_KEY)"
POSTMAN_HEADER_CONTENT_TYPE      := --header "Content-Type: application/json"
POSTMAN_HEADER_ACCEPT            := --header "Accept: application/vnd.api.v10+json"
POSTMAN_HEADER_AUTH              := --header "Authorization: Bearer $(POSTMAN_API_KEY)"

# Header combinations for different endpoints
POSTMAN_CURL_HEADERS_XC          := $(POSTMAN_HEADER_API_KEY) $(POSTMAN_HEADER_CONTENT_TYPE)
POSTMAN_CURL_HEADERS_AA          := $(POSTMAN_HEADER_ACCEPT) $(POSTMAN_HEADER_AUTH)
POSTMAN_CURL_HEADERS_ACA         := $(POSTMAN_HEADER_ACCEPT) $(POSTMAN_HEADER_CONTENT_TYPE) $(POSTMAN_HEADER_AUTH)

# ========================================================================
# QUERY PARAMETERS
# ========================================================================
# NOTE: specs API uses workspaceId=, collections & mocks often use workspace=
# for /apis and /specs
POSTMAN_Q_ID    := ?workspaceId=$(POSTMAN_WS)
# for /collections, /mocks, /environments
POSTMAN_Q            := ?workspace=$(POSTMAN_WS)

# ========================================================================
# DEFAULT TARGET
# ========================================================================
# First target is the default when running 'make' with no arguments
.PHONY: empty-test
empty-test:
	@echo "Empty target."

# ========================================================================
# TEST TARGETS
# ========================================================================
# Test target to verify mock environment update calls work correctly
.PHONY: test-update-mock-env-call
test-update-mock-env-call:
	curl -s --location "$$(POSTMAN_MOCKS_URL)?workspace=$$(POSTMAN_WS)" \
		$(POSTMAN_HEADER_API_KEY) | jq '.mocks[] | {id, uid, name, mockUrl}'

# ========================================================================
# COMPOSITE TARGETS
# ========================================================================

###### NEED ########

#
# 1) A complete build starting from delete all and starting from dd conversion
# 2) Delete all but dd conversion but rebuild as well.
# 3) Just test collection?  If adding examples becomes part of this.
# 4) Have to look into Install in detail
# 	a) All the node_modules and what dir they are in.
# 	b) All the venvs and what dir they are in.
# 	c) Where the requirements.txt for each venv is.
# 	d) Do we need multiple node_modules
# 	e) Do we need multiple venvs.
# 5) Echo start and stop of all composite targets.
# 6) Clean up naming (e.g. postman prefix)
# 

# ========================================================================
# DATA DICTIONARY TO OPENAPI CONVERSION
# ========================================================================
# Convert EBNF data dictionary to OpenAPI specification
.PHONY: ebnf-dd-to-openapi-spec
ebnf-dd-to-openapi-spec: venv
	$(MAKE) install
	$(MAKE) generate-openapi-spec-from-ebnf-dd
	$(MAKE) openapi-merge-overlays
	$(MAKE) openapi-spec-lint

# Generate and Upload the Postman Linked Collection
# Using post-process flattening approach
.PHONY: postman-create-linked-collection
postman-create-linked-collection:
	$(MAKE) postman-api-linked-collection-generate
	$(MAKE) postman-linked-collection-flatten
	$(MAKE) postman-linked-collection-upload
	$(MAKE) postman-linked-collection-link

# Legacy workflow with post-process flattening (if needed)
.PHONY: postman-create-linked-collection-legacy
postman-create-linked-collection-legacy:
	$(MAKE) postman-api-linked-collection-generate
	$(MAKE) postman-linked-collection-flatten
	$(MAKE) postman-linked-collection-upload
	$(MAKE) postman-linked-collection-link

# Generate, Add Tests, Validate, Fix, and Upload the Test Collection
# Using post-process flattening
.PHONY: postman-create-test-collection
postman-create-test-collection:
	$(MAKE) postman-test-collection-generate
	$(MAKE) postman-test-collection-add-examples || echo "⚠️  Skipping examples (optional step)."
	$(MAKE) postman-test-collection-merge-overrides
	$(MAKE) postman-test-collection-add-tests || echo "⚠️  Skipping adding tests (optional step)."
	$(MAKE) postman-auth-setup || echo "⚠️  Skipping auth setup (provider not available)."
	$(MAKE) postman-test-collection-diff-tests
	$(MAKE) postman-test-collection-auto-fix
	$(MAKE) postman-test-collection-fix-v2
	$(MAKE) postman-test-collection-validate
	$(MAKE) verify-urls
	$(MAKE) fix-urls
	$(MAKE) postman-test-collection-validate
	$(MAKE) postman-test-collection-flatten-rename
	$(MAKE) postman-test-collection-add-auth-examples || echo "⚠️  Skipping auth examples (optional step)."
	$(MAKE) postman-test-collection-upload

# Legacy test collection workflow with post-process flattening
.PHONY: postman-create-test-collection-legacy
postman-create-test-collection-legacy:
	$(MAKE) postman-test-collection-generate
	$(MAKE) postman-test-collection-add-examples || echo "⚠️  Skipping examples (optional step)."
	$(MAKE) postman-test-collection-merge-overrides
	$(MAKE) postman-test-collection-add-tests || echo "⚠️  Skipping adding tests (optional step)."
	$(MAKE) postman-test-collection-diff-tests
	$(MAKE) postman-test-collection-auto-fix
	$(MAKE) postman-test-collection-fix-v2
	$(MAKE) postman-test-collection-validate
	$(MAKE) verify-urls
	$(MAKE) fix-urls
	$(MAKE) postman-test-collection-validate
	$(MAKE) postman-test-collection-flatten-rename
	$(MAKE) postman-test-collection-upload

# TODO: Ask Claude if this makes sense without install and venv like below.
.PHONY: generate-and-validate-openapi-spec
generate-and-validate-openapi-spec:
	$(MAKE) generate-openapi-spec-from-ebnf-dd
	$(MAKE) openapi-spec-lint
	$(MAKE) openapi-spec-diff
	$(MAKE) clean-openapi-spec-diff

# Create both environment and mock server in sequence
.PHONY: postman-create-mock-and-env
postman-create-mock-and-env:
	$(MAKE) postman-mock-create
	$(MAKE) postman-env-create
	$(MAKE) postman-env-upload
	$(MAKE) update-mock-env

# Run all mock server tests (both Postman and Prism)
.PHONY: run-postman-and-prism-tests
run-postman-and-prism-tests:
	$(MAKE) prism-start
	$(MAKE) prism-mock-test
	$(MAKE) postman-mock

.PHONY: postman-docs-build-and serve-up
postman-docs-build-and-serve-up:
	# Generate and serve documentation
	$(MAKE) docs-build
	# use docs-serve-bg if you don't want blocking here
	$(MAKE) docs-serve

# ========================================================================
# MAIN BUILD AND TEST PIPELINE
# Complete pipeline from OpenAPI spec to
#	deployed mock server and documentation.
# Note that the data dictionary to OpenAPI conversion is done separately.
# This is because it is not done every time we recreate the Postman
#	instance.
# ========================================================================

.PHONY: postman-instance-build-and-test
postman-instance-build-and-test:
	@echo "🚀 Starting Postman build and test..."
	# Authentication
	$(MAKE) postman-login
	# Import OpenAPI spec into Postman
	$(MAKE) postman-import-openapi-spec
	# Create standalone spec in Specs tab
	$(MAKE) postman-spec-create-standalone
	# Generate and link standard collection
	$(MAKE) postman-create-linked-collection
	$(MAKE) postman-create-test-collection
	$(MAKE) postman-create-mock-and-env
	# Start local mock and run tests
	$(MAKE) prism-start
	$(MAKE) postman-mock
	# Generate and serve documentation
	$(MAKE) postman-docs-build-and-serve-up

# CI version - skips local testing
.PHONY: postman-instance-build-only
postman-instance-build-only:
	@echo "🚀 Starting Postman build (CI mode - no local testing)..."
	# Authentication
	$(MAKE) postman-login
	# Import OpenAPI spec into Postman
	$(MAKE) postman-import-openapi-spec
	# Create standalone spec in Specs tab
	$(MAKE) postman-spec-create-standalone
	# Generate and link standard collection
	$(MAKE) postman-create-linked-collection
	$(MAKE) postman-create-test-collection
	$(MAKE) postman-create-mock-and-env
	# Skip local testing in CI

# ---
# TODO: Need to determine if there is a need for this.
# Control variable for optional full publish
# RUN_FULL_PUBLISH ?= 0
# ---
# ---
# TODO: Need to determine if there is a need for this.
# Optional full publish to Postman
#	@if [ "$$(RUN_FULL_PUBLISH)" = "1" ]; then \
#		$(MAKE) postman-api-full-publish; \
#	else \
#		echo "🔕 Skipping postman-api-full-publish (RUN_FULL_PUBLISH=$$(RUN_FULL_PUBLISH))"; \
#	fi
# ---

# Complete cleanup of all Postman resources in the workspace
.PHONY: postman-cleanup-all
postman-cleanup-all:
	@echo "🧹 Starting FULL cleanup of Postman resources for workspace $(POSTMAN_WS)..."
	$(MAKE) postman-delete-mock-servers
	$(MAKE) postman-delete-collections
	$(MAKE) postman-delete-apis
	$(MAKE) postman-delete-environments
	$(MAKE) postman-api-clean-trash
	$(MAKE) postman-delete-specs
	@echo "🔍 Verifying cleanup..."
	@REMAINING_APIS=$$(curl --silent --location \
		--request GET "$(POSTMAN_APIS_URL)$(POSTMAN_Q_ID)" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" | jq -r '.apis | length' || echo 0); \
	if [ "$$REMAINING_APIS" -gt 0 ]; then \
		echo "⚠️  Warning: $$REMAINING_APIS APIs still remain in workspace after cleanup!"; \
		curl --silent --location \
			--request GET "$(POSTMAN_APIS_URL)$(POSTMAN_Q_ID)" \
			--header "X-Api-Key: $(POSTMAN_API_KEY)" | jq -r '.apis[] | "  - \(.id): \(.name)"'; \
		echo "🔄 Attempting cleanup again..."; \
		$(MAKE) postman-delete-apis; \
	else \
		echo "✅ All APIs successfully deleted"; \
	fi
	@echo "✅ Postman cleanup complete for workspace $(POSTMAN_WS)."

# Rebuild everything without deleting existing resources
.PHONY: rebuild-all-no-delete
rebuild-all-no-delete:
	$(MAKE) install
	$(MAKE) generate-and-validate-openapi-spec
	$(MAKE) postman-instance-build-and-test

# Delete existing resources and rebuild everything.
.PHONY: rebuild-all-with-delete
rebuild-all-with-delete:
	$(MAKE) postman-cleanup-all
	$(MAKE) rebuild-all-no-delete

# CI versions - skip local testing
.PHONY: rebuild-all-no-delete-ci
rebuild-all-no-delete-ci:
	$(MAKE) install
	$(MAKE) generate-and-validate-openapi-spec
	$(MAKE) postman-instance-build-only

.PHONY: rebuild-all-with-delete-ci
rebuild-all-with-delete-ci:
	$(MAKE) postman-cleanup-all
	$(MAKE) rebuild-all-no-delete-ci

# ========================================================================
# PYTHON VIRTUAL ENVIRONMENT
# ========================================================================
# Create and configure Python virtual environment for conversion scripts
.PHONY: venv
venv:
	@test -x "$(VENV_PIP)" || { echo "🐍 Creating venv at $(VENV_DIR)"; $(PYTHON3) -m venv "$(VENV_DIR)"; }
	@"$(VENV_PIP)" install -U pip setuptools wheel
	@"$(VENV_PIP)" -q $(INSTALL_PYTHON_MODULES)

# ========================================================================
# DEBUG TARGETS
# ========================================================================
# Print OpenAPI-related variables for debugging
.PHONY: print-openapi-vars
print-openapi-vars:
	@echo "OPENAPI_DIR                         	= $(OPENAPI_DIR)"
	@echo "C2MAPIV2_OPENAPI_SPEC              	= $(C2MAPIV2_OPENAPI_SPEC)"
	@echo "C2MAPIV2_MAIN_SPEC_PATH            	= $(C2MAPIV2_MAIN_SPEC_PATH)"
	@echo "C2MAPIV2_OPENAPI_SPEC_WITH_EXAMPLES	= $(C2MAPIV2_OPENAPI_SPEC_WITH_EXAMPLES)"

# ========================================================================
# INSTALLATION
# ========================================================================
# List all Postman APIs in the workspace
.PHONY: postman-apis
postman-apis: ## List all Postman APIs
	@echo "Fetching APIs using POSTMAN_API_KEY..."
	curl --silent --location \
	--header "X-Api-Key: $(POSTMAN_API_KEY)" \
	"https://api.getpostman.com/apis" | jq .

# Check mock server URL configuration
.PHONY: check-mock
check-mock:
	echo $(PRISM_MOCK_URL)

# Install all required dependencies
.PHONY: install
install:
	npm install \
	openapi-to-postmanv2 \
	@redocly/cli \
	@stoplight/spectral-cli \
	@stoplight/prism-cli \
	newman newman-reporter-html \
	swagger-ui-dist \
	swagger-cli widdershins lodash || echo "✅ npm packages installed or already available"

# ========================================================================
# OPENAPI SPECIFICATION GENERATION
# ========================================================================
# Convert EBNF data dictionary to OpenAPI specification
.PHONY: generate-openapi-spec-from-ebnf-dd
generate-openapi-spec-from-ebnf-dd:
	@echo "📤 Converting the EBNF Data Dictionary to an OpenAPI YAML Specification."

	# --- Validate required files and script ---
	@if [ ! -f $(EBNF_TO_OPENAPI_SCRIPT) ]; then \
		echo "❌ Script not found: $(EBNF_TO_OPENAPI_SCRIPT)"; exit 1; \
	fi
	@if [ ! -f $(DD_EBNF_FILE) ]; then \
		echo "❌ EBNF Data Dictionary not found: $(DD_EBNF_FILE)"; exit 1; \
	fi

	# --- Create venv if it doesn't exist ---
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "🐍 Creating Python virtual environment..."; \
		$(PYTHON3) -m venv "$(VENV_DIR)"; \
	fi
	
	# --- Install Python dependencies ---
	@echo "📦 Installing required Python modules into venv..."
	@$(VENV_PIP) install -U pip setuptools wheel
	@$(VENV_PIP) $(INSTALL_PYTHON_MODULES)

	# --- Run the conversion script ---
	@echo "🛠  Running: $(EBNF_TO_OPENAPI_SCRIPT) → $(C2MAPIV2_OPENAPI_SPEC_BASE)"
	$(VENV_PYTHON) $(EBNF_TO_OPENAPI_SCRIPT) -o $(C2MAPIV2_OPENAPI_SPEC_BASE) $(DD_EBNF_FILE)

# Merge auth overlay into base OpenAPI spec
.PHONY: openapi-merge-overlays
openapi-merge-overlays: $(C2MAPIV2_OPENAPI_SPEC_BASE) $(OPENAPI_AUTH_OVERLAY)
	@echo "🔗 Merging auth overlay into generated OpenAPI..."
	@$(VENV_PYTHON) scripts/active/merge_openapi_overlays.py \
		$(C2MAPIV2_OPENAPI_SPEC_BASE) $(OPENAPI_AUTH_OVERLAY) $(C2MAPIV2_OPENAPI_SPEC)


# ========================================================================
# OPENAPI VALIDATION AND LINTING
# ========================================================================
# Validate OpenAPI specification with multiple linters
.PHONY: openapi-spec-lint
openapi-spec-lint:
	$(REDOCLY) lint $(C2MAPIV2_OPENAPI_SPEC)
	$(SPECTRAL) lint $(C2MAPIV2_OPENAPI_SPEC)

# Compare current spec with main branch version
.PHONY: openapi-spec-diff
openapi-spec-diff:
	@echo "📤 Fetching latest from origin/main…"
	git fetch origin
	@echo "🧾 Checking out previous version of spec for diff comparison…"
	git show $(C2MAPIV2_MAIN_SPEC_PATH) > $(PREVIOUS_C2MAPIV2_OPENAPI_SPEC)
	@echo "🔍 Running openapi-diff…"
	# TODO: Fix hanging issue with npm version of openapi-diff
	# Was working with brew version, but npm version hangs
	# -$(OPENAPI_DIFF) $(PREVIOUS_C2MAPIV2_OPENAPI_SPEC) $(C2MAPIV2_OPENAPI_SPEC)
	@echo "⚠️  openapi-diff temporarily disabled due to hanging issue"

# Clean up diff temporary files
.PHONY: clean-openapi-spec-diff
clean-openapi-spec-diff:
	rm -f $(PREVIOUS_C2MAPIV2_OPENAPI_SPEC)

# ========================================================================
# POSTMAN AUTHENTICATION
# ========================================================================
# Authenticate with Postman API
.PHONY: postman-login
postman-login:
	@echo "🔐 Logging in to Postman..."
	@postman login --with-api-key $(POSTMAN_API_KEY)

# ========================================================================
# JWT AUTHENTICATION TESTING
# ========================================================================
# Run JWT authentication tests
.PHONY: jwt-test
jwt-test:
	@echo "🔐 Running JWT authentication tests..."
	@cd $(PROJECT_ROOT) && npm test -- tests/jwt-auth-tests.js || \
		node tests/jwt-auth-tests.js

# Add JWT tests to Postman collection
.PHONY: postman-add-jwt-tests
postman-add-jwt-tests:
	@echo "🔧 Adding JWT-specific tests to collection..."
	@if [ -f "$(TEST_COLLECTION_WITH_TESTS)" ]; then \
		node scripts/active/add_tests_jwt.js \
			"$(TEST_COLLECTION_WITH_TESTS)" \
			"$(TEST_COLLECTION_WITH_JWT_TESTS)" \
			--allowed-codes "200,201,204,400,401,403,404,429"; \
		echo "✅ JWT tests added to collection"; \
	else \
		echo "⚠️  Test collection not found. Run 'make postman-create-test-collection' first."; \
	fi

# ========================================================================
# PYTHON ENVIRONMENT FIXES
# ========================================================================
# Fix common PyYAML installation issues
.PHONY: fix-yaml
fix-yaml:
	@echo "🔧 Fixing PyYAML installation..."
	@echo "🧹 Removing any rogue 'yaml' package..."
	@$(VENV_PIP) uninstall -y yaml || true
	@echo "📦 Force reinstalling PyYAML..."
	@$(VENV_PIP) install --force-reinstall PyYAML
	@echo "🔍 Verifying PyYAML installation..."
	@$(VENV_PYTHON) -c "import yaml; print('✅ PyYAML import successful:', yaml.__version__)"

# ========================================================================
# POSTMAN API IMPORT OPTIONS
# ========================================================================

# OPTION A1: Import OpenAPI with folderStrategy=none (native Postman flattening)
.PHONY: postman-import-openapi-flat-native
postman-import-openapi-flat-native:
	@echo "📥 Importing OpenAPI from file $(C2MAPIV2_OPENAPI_SPEC) with native flattening (folderStrategy=none)..."
	@mkdir -p $(POSTMAN_DIR)
	@curl --silent --location --request POST "$(POSTMAN_BASE_URL)/import/openapi?workspace=$(POSTMAN_WS)" \
		-H "X-Api-Key: $(POSTMAN_API_KEY)" \
		--form "type=file" \
		--form "input=@$(C2MAPIV2_OPENAPI_SPEC)" \
		--form 'parameters={"folderStrategy":"none"}' \
	| tee $(POSTMAN_DIR)/import-flat-native.json >/dev/null
	@COLLECTION_UID=$$(jq -r '.collections[0].uid // empty' $(POSTMAN_DIR)/import-flat-native.json); \
	if [ -z "$$COLLECTION_UID" ]; then \
		echo "❌ Import failed. Response:"; \
		cat $(POSTMAN_DIR)/import-flat-native.json | jq . || cat $(POSTMAN_DIR)/import-flat-native.json; \
		exit 1; \
	else \
		echo "✅ Imported flat collection UID: $$COLLECTION_UID"; \
		echo $$COLLECTION_UID > $(POSTMAN_DIR)/native-flat-collection-uid.txt; \
	fi

# OPTION A2: Import and create API definition (shows under APIs, not Specs)
.PHONY: postman-import-openapi-as-api
postman-import-openapi-as-api:
	@echo "📥 Importing OpenAPI as API definition (shows under APIs)..."
	@if [ -z "$(POSTMAN_API_KEY)" ]; then \
		echo "❌ Error: POSTMAN_API_KEY is not set"; \
		exit 1; \
	fi
	@echo "🧹 Pre-import cleanup: Deleting existing APIs with same name..."
	@$(MAKE) postman-delete-apis
	@echo "🔑 Using API Key: $$(echo $(POSTMAN_API_KEY) | head -c 8)..."
	@echo "📍 Target Workspace: $(POSTMAN_WS)"
	@echo "🌐 API URL: $(POSTMAN_APIS_URL)?workspaceId=$(POSTMAN_WS)"
	@CONTENT=$$(jq -Rs . < "$(C2MAPIV2_OPENAPI_SPEC)"); \
	PAYLOAD=$$(jq -n \
		--arg name "$(POSTMAN_API_NAME)" \
		--arg schema "$$CONTENT" \
		'{ name: $$name, schema: { type: "openapi3", language: "yaml", schema: $$schema } }'); \
	echo "🔧 Headers: X-Api-Key: $$(echo $(POSTMAN_API_KEY) | head -c 8)..."; \
	echo "📤 Sending request to Postman API..."; \
	HTTP_CODE=$$(curl --silent --show-error --write-out "%{http_code}" --output postman/import-api-response.json \
		--location --request POST "$(POSTMAN_APIS_URL)?workspaceId=$(POSTMAN_WS)" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		--header "Content-Type: application/json" \
		--header "Accept: application/vnd.api.v10+json" \
		--header "Authorization: Bearer $(POSTMAN_API_KEY)" \
		--data "$$PAYLOAD"); \
	echo "📡 HTTP Response Code: $$HTTP_CODE"; \
	if [ "$$HTTP_CODE" != "200" ] && [ "$$HTTP_CODE" != "201" ]; then \
		echo "❌ API request failed with HTTP code: $$HTTP_CODE"; \
		echo "📄 Response body:"; \
		cat postman/import-api-response.json 2>/dev/null || echo "No response body"; \
		exit 1; \
	fi; \
	API_RESPONSE=$$(cat postman/import-api-response.json); \
	echo "$$API_RESPONSE" | jq . > postman/import-api-debug.json || echo "$$API_RESPONSE" > postman/import-api-debug.json; \
	API_ID=$$(echo "$$API_RESPONSE" | jq -r '.id // empty'); \
	if [ -z "$$API_ID" ]; then \
		echo "❌ Failed to import API. Check postman/import-api-debug.json for details."; \
		echo "📄 Response:"; \
		cat postman/import-api-debug.json 2>/dev/null || echo "No response"; \
		exit 1; \
	else \
		echo "✅ Imported API with ID: $$API_ID"; \
		echo $$API_ID > $(POSTMAN_API_UID_FILE); \
	fi

# OPTION B: Current implementation - post-process flattening
.PHONY: postman-import-openapi-then-flatten
postman-import-openapi-then-flatten:
	@echo "📥 Using current implementation: Generate collection then flatten (Option B)..."
	$(MAKE) postman-api-linked-collection-generate
	$(MAKE) postman-linked-collection-flatten
	$(MAKE) postman-linked-collection-upload

# Show all import options
.PHONY: postman-import-help
postman-import-help:
	@echo "=========================================="
	@echo "POSTMAN IMPORT OPTIONS:"
	@echo "=========================================="
	@echo ""
	@echo "🔸 postman-import-openapi-flat-native"
	@echo "   Import OpenAPI with native Postman flattening (folderStrategy=none)"
	@echo "   Creates a flat collection directly from OpenAPI"
	@echo ""
	@echo "🔸 postman-import-openapi-as-api"
	@echo "   Import OpenAPI as API definition (shows under APIs tab)"
	@echo "   This is the current default behavior"
	@echo ""
	@echo "🔸 postman-import-openapi-then-flatten"
	@echo "   Generate collection then flatten using jq (Option B)"
	@echo "   Current implementation for test collections"
	@echo ""
	@echo "🔸 postman-spec-create"
	@echo "   Create/update spec that shows under Specs tab"
	@echo "   Requires API to exist first"
	@echo ""
	@echo "🔸 postman-api-full-publish"
	@echo "   Full publish that deletes existing specs first"
	@echo "   Creates fresh spec under Specs tab"
	@echo "==========================================="

# Default import - create API and use post-process flattening for now
.PHONY: postman-import-openapi-spec
postman-import-openapi-spec:
	@echo "📥 Importing OpenAPI and creating API definition..."
	# Create the API definition
	$(MAKE) postman-import-openapi-as-api

# ========================================================================
# POSTMAN SPEC MANAGEMENT (Shows under "Specs" tab)
# ========================================================================

# Create or update spec (shows under Specs tab, not APIs tab)
.PHONY: postman-spec-create
postman-spec-create:
	@echo "📄 Creating/updating OpenAPI spec under Specs tab..."
	@CONTENT=$$(jq -Rs . < "$(C2MAPIV2_OPENAPI_SPEC)"); \
	jq -n \
		--arg name "$(C2MAPIV2_POSTMAN_API_NAME_PC)" \
		--arg type "openapi3" \
		--arg path "openapi.yaml" \
		--arg content "$$CONTENT" \
		'{ type: $$type, files: [{ path: $$path, content: $$content }] }' \
		> "$(POSTMAN_DIR)/spec-payload.json"
	@RESPONSE=$$(curl --silent --location --request POST "$(POSTMAN_BASE_URL)/apis/$(shell cat $(POSTMAN_API_UID_FILE))/versions/1.0.0/schemas" \
		$(POSTMAN_CURL_HEADERS_XC) \
		--data-binary "@$(POSTMAN_DIR)/spec-payload.json"); \
	echo "$$RESPONSE" | jq . > $(POSTMAN_DIR)/spec-create-response.json || echo "$$RESPONSE" > $(POSTMAN_DIR)/spec-create-response.json; \
	SPEC_ID=$$(echo "$$RESPONSE" | jq -r '.id // empty'); \
	if [ -n "$$SPEC_ID" ]; then \
		echo "✅ Spec created/updated with ID: $$SPEC_ID"; \
		echo $$SPEC_ID > $(POSTMAN_DIR)/spec-id.txt; \
	else \
		echo "❌ Failed to create spec. Check $(POSTMAN_DIR)/spec-create-response.json"; \
	fi

# Create standalone spec in Specs tab (without deleting existing)
.PHONY: postman-spec-create-standalone
postman-spec-create-standalone:
	@echo "🧹 Deleting existing specs with the same name before creating new one..."
	$(MAKE) postman-delete-specs-by-name NAME="$(C2MAPIV2_POSTMAN_API_NAME_PC)"
	@echo "📄 Creating standalone spec in Specs tab..."
	@CONTENT=$$(cat "$(C2MAPIV2_OPENAPI_SPEC)"); \
	jq -n \
		--arg name "$(C2MAPIV2_POSTMAN_API_NAME_PC)" \
		--arg type "OPENAPI:3.0" \
		--arg content "$$CONTENT" \
		'{ name: $$name, type: $$type, files: [{ path: "openapi.yaml", content: $$content }] }' > "$(POSTMAN_DIR)/spec-standalone-payload.json"
	@RESPONSE=$$(curl --silent --location --request POST "$(POSTMAN_SPECS_URL)?workspaceId=$(POSTMAN_WS)" \
		$(POSTMAN_CURL_HEADERS_XC) \
		--data-binary "@$(POSTMAN_DIR)/spec-standalone-payload.json"); \
	echo "$$RESPONSE" | jq . > $(POSTMAN_DIR)/spec-standalone-response.json || echo "$$RESPONSE" > $(POSTMAN_DIR)/spec-standalone-response.json; \
	SPEC_ID=$$(echo "$$RESPONSE" | jq -r '.id // empty'); \
	if [ -n "$$SPEC_ID" ]; then \
		echo "✅ Standalone spec created with ID: $$SPEC_ID"; \
		echo "📍 View in Postman: Specs tab → $(C2MAPIV2_POSTMAN_API_NAME_PC)"; \
		echo $$SPEC_ID > $(POSTMAN_DIR)/spec-standalone-id.txt; \
	else \
		echo "❌ Failed to create standalone spec. Check $(POSTMAN_DIR)/spec-standalone-response.json"; \
		cat $(POSTMAN_DIR)/spec-standalone-response.json | jq . || cat $(POSTMAN_DIR)/spec-standalone-response.json; \
	fi

# List all specs in workspace
.PHONY: postman-spec-list
postman-spec-list:
	@echo "📋 Listing all specs in workspace..."
	@curl --silent --location "$(POSTMAN_SPECS_URL)?workspaceId=$(POSTMAN_WS)" \
		$(POSTMAN_CURL_HEADERS_XC) | jq '.specs // [] | .[] | {id: .id, name: .name, type: .type}'

# ========================================================================
# POSTMAN FULL PUBLISH
# ========================================================================
# Publish complete specification to Postman (deletes existing specs first)
.PHONY: postman-api-full-publish
postman-api-full-publish:
	@echo "🚀 Starting full Postman Spec publish..."

	# Fetch all existing specs in the workspace
	@SPECS=$$( $(call curl_json,"$(POSTMAN_SPECS_URL)$(POSTMAN_Q_ID)","") | jq -r '.specs[].id' ); \
	if [ -n "$$SPECS" ]; then \
		echo "🧹 Deleting all existing specs in workspace $(POSTMAN_WS)..."; \
		for ID in $$SPECS; do \
			echo "   ➡️ Deleting spec $$ID..."; \
			$(call curl_json,--request DELETE "$(POSTMAN_SPECS_URL)/$$ID","") | jq .; \
		done; \
	else \
		echo "ℹ️ No existing specs found. Skipping deletion."; \
	fi

	# Build payload JSON for new spec (YAML as raw string; no fromjson)
	@echo "🆕 Creating a fresh Postman Spec with $(C2MAPIV2_OPENAPI_SPEC)..."
	@CONTENT=$$(jq -Rs . < "$(C2MAPIV2_OPENAPI_SPEC)"); \
	jq -n \
		--arg name "$(C2MAPIV2_POSTMAN_API_NAME_PC)" \
		--arg type "OPENAPI:3.0" \
		--arg path "index.yaml" \
		--arg content "$$CONTENT" \
		'{ name: $$name, type: $$type, files: [ { path: $$path, content: $$content } ] }' \
		> "$(POSTMAN_FULL_PAYLOAD)"

	# Create a new spec
	@$(call curl_json,--request POST "$(POSTMAN_SPECS_URL)$(POSTMAN_Q_ID)",--data @$(POSTMAN_FULL_PAYLOAD)) \
		| tee "$(POSTMAN_FULL_RESPONSE)" > /dev/null

	# Extract and save SPEC_ID
	@SPEC_ID=$$(jq -r '.id // empty' "$(POSTMAN_FULL_RESPONSE)"); \
	if [ -z "$$SPEC_ID" ]; then \
		echo "❌ Failed to create a fresh spec. See $(POSTMAN_FULL_RESPONSE)."; \
		exit 1; \
	else \
		echo "✅ Fresh spec created with ID: $$SPEC_ID"; \
		echo "$$SPEC_ID" > "$(POSTMAN_SPEC_ID_FILE)"; \
	fi

# ========================================================================
# POSTMAN COLLECTION GENERATION
# ========================================================================

# Generate Postman collection from OpenAPI spec and add metadata
.PHONY: postman-api-linked-collection-generate
postman-api-linked-collection-generate: | $(POSTMAN_DIR) $(POSTMAN_GENERATED_DIR)
	@echo "📦 Generating Postman collection from $(C2MAPIV2_OPENAPI_SPEC)..."
	$(GENERATOR_OFFICIAL) -s $(C2MAPIV2_OPENAPI_SPEC) -o $(POSTMAN_COLLECTION_RAW) -p
	@echo "🛠 Adding 'info' block to collection..."
	@JQ_INFO_NAME="$(POSTMAN_LINKED_COLLECTION_NAME)" \
	 JQ_INFO_SCHEMA="$(POSTMAN_SCHEMA_V2)" \
	 $(call jqf,$(JQ_ADD_INFO_FILE),$(POSTMAN_COLLECTION_RAW)) > $(POSTMAN_COLLECTION_RAW).tmp
	@mv $(POSTMAN_COLLECTION_RAW).tmp $(POSTMAN_COLLECTION_RAW)
	@echo "✅ Collection generated with 'info' block at $(POSTMAN_COLLECTION_RAW)"

# ========================================================================
# LINKED COLLECTION FLATTENING
# ========================================================================
# Flatten linked collection structure
POSTMAN_LINKED_COLLECTION_FLAT := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-linked-collection-flat.json

.PHONY: postman-linked-collection-flatten
postman-linked-collection-flatten:
	@echo "🧹 Flattening linked collection from $(POSTMAN_COLLECTION_RAW)..."
	@$(call guard-file,$(POSTMAN_COLLECTION_RAW))
	@jq 'def all_items(i): (i // []) as $$a | [ $$a[] | if has("item") then all_items(.item)[] else . end ]; def req_name(r): (r.request.method // "REQ") as $$m | (r.request.url.path // []) as $$p | ($$p | join("/")) as $$path | if $$path == "" then $$m else ($$m + " /" + $$path) end; .item = (all_items(.item) | map( .name = req_name(.) ))' $(POSTMAN_COLLECTION_RAW) > $(POSTMAN_LINKED_COLLECTION_FLAT)
	@echo "✅ Linked collection flattened with renamed requests"
	@echo "🔐 Adding auth examples to linked collection..."
	@node scripts/active/add_auth_examples.js $(POSTMAN_LINKED_COLLECTION_FLAT) $(POSTMAN_LINKED_COLLECTION_FLAT) || echo "⚠️  Skipping auth examples"
	@echo "✅ Auth examples added"
	@echo "📝 Adding pre-request script to collection..."
	@node scripts/active/add_pre_request_script.js $(POSTMAN_LINKED_COLLECTION_FLAT) postman/scripts/jwt-pre-request.js $(POSTMAN_LINKED_COLLECTION_FLAT)
	@echo "✅ Pre-request script added"

# ========================================================================
# POSTMAN COLLECTION UPLOAD
# ========================================================================
# Upload generated collection to Postman workspace (with optional flattening)
.PHONY: postman-linked-collection-upload
postman-linked-collection-upload:
	@# Check if we should use flattened version
	@if [ -f "$(POSTMAN_LINKED_COLLECTION_FLAT)" ]; then \
		UPLOAD_FILE="$(POSTMAN_LINKED_COLLECTION_FLAT)"; \
		echo "📤 Uploading FLATTENED linked collection $$UPLOAD_FILE to workspace $(POSTMAN_WS)..."; \
	else \
		UPLOAD_FILE="$(POSTMAN_COLLECTION_RAW)"; \
		echo "📤 Uploading Postman collection $$UPLOAD_FILE to workspace $(POSTMAN_WS)..."; \
	fi; \
	COLLECTION_UID=$$(jq -c '{collection: .}' "$$UPLOAD_FILE" | \
		curl --silent --location --request POST "$(POSTMAN_COLLECTIONS_URL)?workspace=$(POSTMAN_WS)" \
			$(POSTMAN_CURL_HEADERS_XC) \
			--data-binary @- | jq -r '.collection.uid'); \
	if [ "$$COLLECTION_UID" = "null" ] || [ -z "$$COLLECTION_UID" ]; then \
		echo "❌ Failed to upload collection"; exit 1; \
	else \
		echo "✅ Collection uploaded with UID: $$COLLECTION_UID"; \
		echo $$COLLECTION_UID > $(POSTMAN_LINKED_COLLECTION_UID_FILE); \
	fi
	@echo " "
	@echo " "
	@echo " "
	@echo " "

# ========================================================================
# POSTMAN COLLECTION LINKING
# ========================================================================
# Link uploaded collection to API definition
.PHONY: postman-linked-collection-link
postman-linked-collection-link:
	@echo "🔗 Linking collection to API $(POSTMAN_API_NAME)..."
	@if [ ! -f $(POSTMAN_API_UID_FILE) ]; then \
		echo "❌ Missing API UID file: $(POSTMAN_API_UID_FILE). Run postman-import-openapi-spec first."; exit 1; \
	fi
	@if [ ! -f $(POSTMAN_LINKED_COLLECTION_UID_FILE) ]; then \
		echo "❌ Missing collection UID file: $(POSTMAN_LINKED_COLLECTION_UID_FILE). Run postman-collection-upload first."; exit 1; \
	fi
	@API_ID=$$(cat $(POSTMAN_API_UID_FILE)); \
	COLLECTION_UID=$$(cat $(POSTMAN_LINKED_COLLECTION_UID_FILE)); \
	echo "🔗 Copying and linking collection $$COLLECTION_UID to API $$API_ID..."; \
	jq -n --arg coll "$$COLLECTION_UID" '{operationType: "COPY_COLLECTION", data: {collectionId: $$coll}}' > $(POSTMAN_LINK_PAYLOAD); \
	curl --silent --location --request POST "$(POSTMAN_APIS_URL)/$$API_ID/collections" \
		$(POSTMAN_CURL_HEADERS_XC) \
		$(POSTMAN_CURL_HEADERS_AA) \
		--data-binary "@$(POSTMAN_LINK_PAYLOAD)" | tee $(POSTMAN_LINK_DEBUG)
	@echo " "
	@echo " "
	@echo " "
	@echo " "

# ========================================================================
# TEST COLLECTION GENERATION
# ========================================================================

# Generate test collection from native flattened import
.PHONY: postman-test-collection-generate-from-flat
postman-test-collection-generate-from-flat: | $(POSTMAN_GENERATED_DIR)
	@echo "📦 Preparing test collection from native flattened import..."
	@if [ ! -f $(POSTMAN_DIR)/import-flat-native.json ]; then \
		echo "❌ Native flat import not found. Run postman-import-openapi-spec first."; \
		exit 1; \
	fi
	# Extract the collection from import response and update metadata
	@jq '.collections[0]' $(POSTMAN_DIR)/import-flat-native.json | \
	JQ_INFO_NAME="$(POSTMAN_TEST_COLLECTION_NAME)" \
	JQ_INFO_SCHEMA="$(POSTMAN_SCHEMA_V2)" \
	$(call jqf,$(JQ_ADD_INFO_FILE),.) > $(POSTMAN_COLLECTION_RAW)
	@echo "✅ Test collection prepared from native flat import at $(POSTMAN_COLLECTION_RAW)"

# Legacy: Generate test collection with appropriate metadata
.PHONY: postman-test-collection-generate
postman-test-collection-generate: | $(POSTMAN_GENERATED_DIR)
	@echo "📦 Preparing testing collection from $(POSTMAN_COLLECTION_RAW)..."
	@JQ_INFO_NAME="$(POSTMAN_TEST_COLLECTION_NAME)" \
	 JQ_INFO_SCHEMA="$(POSTMAN_SCHEMA_V2)" \
	 $(call jqf,$(JQ_ADD_INFO_FILE),$(POSTMAN_COLLECTION_RAW)) > $(POSTMAN_TEST_COLLECTION_TMP)
	@mv $(POSTMAN_TEST_COLLECTION_TMP) $(POSTMAN_COLLECTION_RAW)
	@echo "✅ Test collection info set at $(POSTMAN_COLLECTION_RAW)"

# ========================================================================
# TEST DATA GENERATION
# ========================================================================
# Add example data to collection requests
.PHONY: postman-test-collection-add-examples
postman-test-collection-add-examples:
	@echo "📤 Installing required Python modules..."
	@echo "🧩 Adding smart example data to Postman collection..."
	@if [ ! -f $(POSTMAN_COLLECTION_RAW) ]; then \
		echo "⚠️  $(POSTMAN_COLLECTION_RAW) not found. Run postman-collection-merge-overrides first."; exit 1; \
	fi
	$(ADD_EXAMPLES_TO_COLLECTION)
	@echo "✅ Examples added and saved to $(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES)"
	@echo " "
	@echo " "
	@echo " "
	@echo " "

# ========================================================================
# OVERRIDE MERGING
# ========================================================================
# Merge custom overrides into collection (safe deep merge)
.PHONY: postman-test-collection-merge-overrides
postman-test-collection-merge-overrides:
	@echo "🔀 Safely merging overrides from $(POSTMAN_OVERRIDES_FILE) into $(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES)..."
	@if [ ! -f $(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES) ]; then \
		echo "❌ Base collection $(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES) not found. Run postman-collection-generate first."; \
		exit 1; \
	fi
	@if [ ! -f $(POSTMAN_OVERRIDES_FILE) ]; then \
		echo "⚠️  No override file found at $(POSTMAN_OVERRIDES_FILE). Skipping overrides."; \
		cp $(POSTMAN_COLLECTION_RAW) $(POSTMAN_TEST_COLLECTION_MERGED); \
		echo "✅ No overrides applied. Copied $(POSTMAN_COLLECTION_RAW) to $(POSTMAN_TEST_COLLECTION_MERGED)"; \
		exit 0; \
	fi
	@jq -s -f $(MERGE_POSTMAN_OVERRIDES) $(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES) $(POSTMAN_OVERRIDES_FILE) > $(POSTMAN_TEST_COLLECTION_MERGED)
	@echo "✅ Safe deep merge completed. Output written to $(POSTMAN_TEST_COLLECTION_MERGED)"
	@echo " "
	@echo " "
	@echo " "
	@echo " "

# ========================================================================
# TEST ADDITION
# ========================================================================
# Add automated tests to collection endpoints
.PHONY: postman-test-collection-add-tests
postman-test-collection-add-tests:
	@echo "🧪 Adding default Postman tests to $(POSTMAN_TEST_COLLECTION_MERGED) with allowed codes: $(POSTMAN_ALLOWED_CODES)..."
	@if [ ! -f $(POSTMAN_TEST_COLLECTION_MERGED) ]; then \
		echo "⚠️  $(POSTMAN_TEST_COLLECTION_MERGED) not found. Run postman-collection-add-examples first."; \
		exit 1; \
	fi
	@node $(ADD_TESTS_SCRIPT) $(POSTMAN_TEST_COLLECTION_MERGED) $(POSTMAN_TEST_COLLECTION_WITH_TESTS) --allowed-codes "$(POSTMAN_ALLOWED_CODES)"
	@echo "✅ Tests added to $(POSTMAN_TEST_COLLECTION_WITH_TESTS)"
	@echo " "
	@echo " "
	@echo " "
	@echo " "

# ========================================================================
# DIFF VIEWING
# ========================================================================
# Show differences between collection versions
.PHONY: postman-test-collection-diff-tests
postman-test-collection-diff-tests:
	@if [ ! -f $(POSTMAN_TEST_COLLECTION_MERGED) ] || [ ! -f $(POSTMAN_TEST_COLLECTION_WITH_TESTS) ]; then \
		echo "❌ One or both files not found: $(POSTMAN_TEST_COLLECTION_MERGED), $(POSTMAN_TEST_COLLECTION_WITH_TESTS)"; \
		exit 1; \
	fi
	@echo "🔍 Showing diff between original and test-augmented collections..."
	@diff --unified $(POSTMAN_TEST_COLLECTION_MERGED) $(POSTMAN_TEST_COLLECTION_WITH_TESTS) || true
	@echo " "
	@echo " "
	@echo " "
	@echo " "

# Open diff in VS Code
.PHONY: postman-test-collection-diff-tests-vscode
postman-test-collection-diff-tests-vscode:
	@code --diff $(POSTMAN_TEST_COLLECTION_MERGED) $(POSTMAN_TEST_COLLECTION_WITH_TESTS)
	@echo " "
	@echo " "
	@echo " "
	@echo " "

# ========================================================================
# COLLECTION AUTO-FIX
# ========================================================================
# Fix invalid collection items automatically
.PHONY: postman-test-collection-auto-fix
postman-test-collection-auto-fix: | $(POSTMAN_GENERATED_DIR)
	@echo "🛠 Auto-fixing invalid items in $(POSTMAN_TEST_COLLECTION_WITH_TESTS)..."
	$(call guard-file,$(POSTMAN_TEST_COLLECTION_WITH_TESTS))
	$(call jqf,$(JQ_AUTO_FIX_FILE),$(POSTMAN_TEST_COLLECTION_WITH_TESTS)) > $(POSTMAN_TEST_COLLECTION_FIXED)
	@echo "✅ Auto-fix complete -> $(POSTMAN_TEST_COLLECTION_FIXED)"
	@echo "🔍 Validating fixed collection..."
	@$(NODE_COLLECTION_VALIDATE)

# Show auto-fix differences
.PHONY: postman-test-collection-diff-auto-fix
postman-test-collection-diff-auto-fix:
	@if [ ! -f $(POSTMAN_TEST_COLLECTION_WITH_TESTS) ] || [ ! -f $(POSTMAN_TEST_COLLECTION_FIXED) ]; then \
		echo "❌ One or both files not found: $(POSTMAN_TEST_COLLECTION_WITH_TESTS), $(POSTMAN_TEST_COLLECTION_FIXED)"; \
		exit 1; \
	fi
	@echo "🔍 Showing diff between original and test-augmented collections..."
	@diff --unified $(POSTMAN_TEST_COLLECTION_WITH_TESTS) $(POSTMAN_TEST_COLLECTION_FIXED) || true

# Open auto-fix diff in VS Code
.PHONY: postman-test-collection-diff-auto-fix-vscode
postman-test-collection-diff-auto-fix-vscode:
	@code --diff $(POSTMAN_TEST_COLLECTION_WITH_TESTS) $(POSTMAN_TEST_COLLECTION_FIXED)

# ========================================================================
# URL FIXING
# ========================================================================
# Fix collection URLs using Python script
.PHONY: postman-test-collection-fix-v2
postman-test-collection-fix-v2:
	@echo "🔧 Fixing collection URLs (v2) in $(POSTMAN_TEST_COLLECTION_FIXED)..."
	@$(PYTHON) $(FIX_COLLECTION_URLS) $(POSTMAN_TEST_COLLECTION_FIXED) $(POSTMAN_TEST_COLLECTION_FIXED)
	@echo "✅ Collection URLs fixed: $(POSTMAN_TEST_COLLECTION_FIXED)"

# Verify URLs in collection
.PHONY: verify-urls
verify-urls:
	@echo "🔍 Verifying URLs in $(POSTMAN_TEST_COLLECTION_FIXED)..."
	$(call jqf,$(JQ_VERIFY_URLS_FILE),$(POSTMAN_TEST_COLLECTION_FIXED))

# Fix URLs using jq filter
.PHONY: fix-urls
fix-urls:
	@echo "🔧 Fixing URLs in $(POSTMAN_TEST_COLLECTION_FIXED)..."
	$(call jqf,$(JQ_FIX_URLS_FILE),$(POSTMAN_TEST_COLLECTION_FIXED)) > $(POSTMAN_TEST_COLLECTION_FIXED).tmp
	@mv $(POSTMAN_TEST_COLLECTION_FIXED).tmp $(POSTMAN_TEST_COLLECTION_FIXED)
	@echo "✅ URL fix complete: $(POSTMAN_TEST_COLLECTION_FIXED)"

# ========================================================================
# COLLECTION VALIDATION
# ========================================================================
# Validate Postman collection structure
.PHONY: postman-test-collection-validate
postman-test-collection-validate:
	@echo "🔍 Validating Postman collection $(POSTMAN_TEST_COLLECTION_FIXED)..."
	@node $(POSTMAN_VALIDATOR) "$(POSTMAN_TEST_COLLECTION_FIXED)"

# ========================================================================
# COLLECTION FLATTENING
# ========================================================================
# Flatten collection structure (remove folder hierarchy)
POSTMAN_TEST_COLLECTION_FLAT := $(POSTMAN_GENERATED_DIR)/$(C2MAPIV2_POSTMAN_API_NAME_KC)-test-collection-flat.json

.PHONY: postman-test-collection-flatten
postman-test-collection-flatten:
	@echo "🧹 Flattening collection (removing folder hierarchy) from $(POSTMAN_TEST_COLLECTION_FIXED)..."
	@$(call guard-file,$(POSTMAN_TEST_COLLECTION_FIXED))
	@jq 'def all_items(i): (i // []) as $$a | [ $$a[] | if has("item") then all_items(.item)[] else . end ]; .item = all_items(.item)' $(POSTMAN_TEST_COLLECTION_FIXED) > $(POSTMAN_TEST_COLLECTION_FLAT)
	@echo "✅ Collection flattened to $(POSTMAN_TEST_COLLECTION_FLAT)"
	@echo "📊 Original items: $$(jq '[.. | .item? // empty] | add | length' $(POSTMAN_TEST_COLLECTION_FIXED))"
	@echo "📊 Flattened items: $$(jq '.item | length' $(POSTMAN_TEST_COLLECTION_FLAT))"

# Flatten with renamed requests (METHOD /path format)
.PHONY: postman-test-collection-flatten-rename
postman-test-collection-flatten-rename:
	@echo "🧹 Flattening and renaming requests to 'METHOD /path' format..."
	@$(call guard-file,$(POSTMAN_TEST_COLLECTION_FIXED))
	@jq 'def all_items(i): (i // []) as $$a | [ $$a[] | if has("item") then all_items(.item)[] else . end ]; def req_name(r): (r.request.method // "REQ") as $$m | (r.request.url.path // []) as $$p | ($$p | join("/")) as $$path | if $$path == "" then $$m else ($$m + " /" + $$path) end; .item = (all_items(.item) | map( .name = req_name(.) ))' $(POSTMAN_TEST_COLLECTION_FIXED) > $(POSTMAN_TEST_COLLECTION_FLAT)
	@echo "✅ Collection flattened with renamed requests"

# Apply auth examples to test collection (after flattening)
.PHONY: postman-test-collection-add-auth-examples
postman-test-collection-add-auth-examples:
	@echo "🔐 Adding auth examples to test collection..."
	@if [ ! -f "$(POSTMAN_TEST_COLLECTION_FLAT)" ]; then \
		echo "⚠️  Flattened test collection not found. Skipping auth examples."; \
		exit 0; \
	fi
	@if [ -f "$(SCRIPTS_DIR)/active/add_auth_examples.js" ]; then \
		node $(SCRIPTS_DIR)/active/add_auth_examples.js $(POSTMAN_TEST_COLLECTION_FLAT) $(POSTMAN_TEST_COLLECTION_FLAT) || echo "⚠️  Failed to add auth examples"; \
		echo "✅ Auth examples added to test collection"; \
	else \
		echo "⚠️  Auth examples script not found"; \
	fi

# ========================================================================
# TEST COLLECTION UPLOAD
# ========================================================================
# Upload test collection to Postman (with optional flattening)
.PHONY: postman-test-collection-upload
postman-test-collection-upload:
	@echo "===== DEBUG: Postman Collection Upload Test Variables ====="
	@echo "POSTMAN_API_KEY: $(POSTMAN_API_KEY)"
	@echo "POSTMAN_WS: $(POSTMAN_WS)"
	@echo "(POSTMAN_TEST_COLLECTION_FIXED): $(POSTMAN_TEST_COLLECTION_FIXED)"
	@echo "==========================================================="
	@# Check if we should use flattened version
	@if [ -f "$(POSTMAN_TEST_COLLECTION_FLAT)" ]; then \
		UPLOAD_FILE="$(POSTMAN_TEST_COLLECTION_FLAT)"; \
		echo "📦 Using FLATTENED collection: $$UPLOAD_FILE"; \
	else \
		UPLOAD_FILE="$(POSTMAN_TEST_COLLECTION_FIXED)"; \
		echo "📦 Using collection: $$UPLOAD_FILE"; \
	fi; \
	$(call guard-file,$$UPLOAD_FILE); \
	RESPONSE=$$(jq -c '{collection: .}' "$$UPLOAD_FILE" | \
		curl --silent --location --request POST "$(POSTMAN_COLLECTIONS_URL)?workspace=$(POSTMAN_WS)" \
			$(POSTMAN_CURL_HEADERS_XC) \
			--data-binary @-); \
	echo "$$RESPONSE" | jq . > "$(POSTMAN_UPLOAD_TEST_DEBUG)" || echo "$$RESPONSE" > "$(POSTMAN_UPLOAD_TEST_DEBUG)"; \
	COLLECTION_UID=$$(echo "$$RESPONSE" | jq -r '.collection.uid // empty'); \
	if [ -z "$$COLLECTION_UID" ] || [ "$$COLLECTION_UID" = "null" ]; then \
		echo "❌ Failed to upload test collection. See $(POSTMAN_UPLOAD_TEST_DEBUG)."; \
		exit 1; \
	else \
		echo "✅ TEST Collection uploaded with UID: $$COLLECTION_UID"; \
		echo "$$COLLECTION_UID" > "$(POSTMAN_TEST_COLLECTION_UID_FILE)"; \
		echo "📄 UID saved to $(POSTMAN_TEST_COLLECTION_UID_FILE)"; \
	fi

# ========================================================================
# ENVIRONMENT CREATION
# ========================================================================
# Generate Postman environment file with mock URL and auth fields
# Auth flow: When clientId/clientSecret are populated, the pre-request script
# will automatically fetch tokens from AWS and add them to API requests
.PHONY: postman-env-create
postman-env-create:
	@echo "🧪 Generating Postman environment file with auth fields..."

	@if [ ! -f $(POSTMAN_MOCK_URL_FILE) ]; then \
			echo "⚠️  Missing mock URL file: $(POSTMAN_MOCK_URL_FILE)"; \
			exit 1; \
	fi
	@echo "🔐 Fetching AWS credentials..."
	@# Source credentials from AWS Secrets Manager (or use defaults)
	@eval $$(USE_LOCAL_CREDS=true ./scripts/active/fetch_aws_credentials.sh) && \
	export C2M_BASE_URL=$$(cat $(POSTMAN_MOCK_URL_FILE)) && \
	export ENV_NAME="C2M API - Mock Server" && \
	./scripts/active/generate_postman_env.sh "" $(POSTMAN_ENV_FILE)
	@echo "✅ Mock environment file written to $(POSTMAN_ENV_FILE) with auth credentials"
	
	@echo "🌐 Creating AWS Dev environment for token testing..."
	@mkdir -p postman/environments
	@eval $$(USE_LOCAL_CREDS=true ./scripts/active/fetch_aws_credentials.sh) && \
	export C2M_BASE_URL="$$C2M_BASE_URL" && \
	export ENV_NAME="C2M API - AWS Dev" && \
	./scripts/active/generate_postman_env.sh "" postman/environments/c2m-aws-dev.postman_environment.json
	@echo "✅ AWS Dev environment file written to postman/environments/c2m-aws-dev.postman_environment.json"

# ========================================================================
# ENVIRONMENT UPLOAD
# ========================================================================
# Upload environment to Postman workspace
.PHONY: postman-env-upload
postman-env-upload:
	@echo "📤 Uploading Mock environment file to workspace $(POSTMAN_WS)..."
	@$(call guard-file,$(POSTMAN_ENV_FILE))
	@RESPONSE=$$(curl --silent --show-error --fail --location \
		--request POST "$(POSTMAN_ENVIRONMENTS_URL)$(POSTMAN_Q)" \
		$(POSTMAN_CURL_HEADERS_XC) \
		--data-binary '@$(POSTMAN_ENV_FILE)' || true); \
	echo "$$RESPONSE" | jq . > $(POSTMAN_ENV_UPLOAD_DEBUG) || echo "$$RESPONSE" > $(POSTMAN_ENV_UPLOAD_DEBUG); \
	POSTMAN_ENV_UID=$$(echo "$$RESPONSE" | jq -r '.environment.uid // empty'); \
	if [ -z "$$POSTMAN_ENV_UID" ]; then \
		echo "❌ Failed to upload environment. See $(POSTMAN_ENV_UPLOAD_DEBUG)."; \
		exit 1; \
	else \
		echo "✅ Mock environment uploaded with UID: $$POSTMAN_ENV_UID"; \
		echo $$POSTMAN_ENV_UID > $(POSTMAN_ENV_UID_FILE); \
	fi
	
	@echo "📤 Uploading AWS Dev environment file to workspace $(POSTMAN_WS)..."
	@AWS_ENV_FILE="postman/environments/c2m-aws-dev.postman_environment.json"; \
	if [ -f "$$AWS_ENV_FILE" ]; then \
		RESPONSE=$$(curl --silent --show-error --fail --location \
			--request POST "$(POSTMAN_ENVIRONMENTS_URL)$(POSTMAN_Q)" \
			$(POSTMAN_CURL_HEADERS_XC) \
			--data-binary "@$$AWS_ENV_FILE" || true); \
		AWS_ENV_UID=$$(echo "$$RESPONSE" | jq -r '.environment.uid // empty'); \
		if [ -z "$$AWS_ENV_UID" ]; then \
			echo "⚠️  Failed to upload AWS Dev environment"; \
		else \
			echo "✅ AWS Dev environment uploaded with UID: $$AWS_ENV_UID"; \
		fi \
	else \
		echo "⚠️  AWS Dev environment file not found: $$AWS_ENV_FILE"; \
	fi

# ========================================================================
# MOCK SERVER CREATION
# ========================================================================
# Create Postman mock server with collection and environment
.PHONY: postman-mock-create
postman-mock-create:
	@echo "🆕 Creating Postman mock server..."
	@if [ -z "$(POSTMAN_WS)" ]; then echo "❌ POSTMAN_WS (workspace ID) is not set. Aborting."; exit 1; fi
	@if [ -z "$(POSTMAN_TEST_COLLECTION_UID)" ]; then echo "❌ POSTMAN_TEST_COLLECTION_UID not set. Aborting."; exit 1; fi
	@PAYLOAD=$$(jq -n --arg coll "$(POSTMAN_TEST_COLLECTION_UID)" --arg name "$(POSTMAN_MOCK_NAME)" \
	  '{ mock: { collection: $$coll, name: $$name, private: false } }'); \
	echo "Debug: Creating mock with payload: $$PAYLOAD" >&2; \
	echo "Debug: URL: $(POSTMAN_MOCKS_URL)$(POSTMAN_Q)" >&2; \
	RESP=$$(curl --silent --show-error --location \
	  --request POST "$(POSTMAN_MOCKS_URL)$(POSTMAN_Q)" \
	  $(POSTMAN_CURL_HEADERS_XC) \
	  --data-raw "$$PAYLOAD"); \
	echo "$$RESP" | jq . > $(POSTMAN_DIR)/postman_mock_create.json || echo "$$RESP" > $(POSTMAN_DIR)/postman_mock_create.json; \
	jq -r '.mock.uid // empty' $(POSTMAN_DIR)/postman_mock_create.json > "$(POSTMAN_MOCK_UID_FILE)"; \
	jq -r '.mock.id  // empty' $(POSTMAN_DIR)/postman_mock_create.json > "$(POSTMAN_MOCK_ID_FILE)"; \
	jq -r '.mock.mockUrl // empty' $(POSTMAN_DIR)/postman_mock_create.json > "$(POSTMAN_MOCK_URL_FILE)"; \
	if [ ! -s "$(POSTMAN_MOCK_UID_FILE)" ] || [ ! -s "$(POSTMAN_MOCK_ID_FILE)" ]; then \
		echo "❌ Failed to create mock server. See $(POSTMAN_DIR)/postman_mock_create.json"; exit 1; \
	fi; \
	echo "✅ Mock server created. UID=$$(cat $(POSTMAN_MOCK_UID_FILE))  ID=$$(cat $(POSTMAN_MOCK_ID_FILE))"

# ========================================================================
# MOCK SERVER UPDATE
# ========================================================================
# Update mock server with new environment configuration
.PHONY: update-mock-env
update-mock-env:
	@echo "🔄 Updating Postman mock server environment..."
	@if [ -z "$(POSTMAN_MOCK_ID)" ]; then \
		echo "❌ POSTMAN_MOCK_ID not found in $(POSTMAN_MOCK_ID_FILE). Aborting."; \
		exit 1; \
	fi
	@curl --silent --show-error --fail --location \
		--request PUT "$(POSTMAN_MOCKS_URL)/$(POSTMAN_MOCK_ID)" \
		$(POSTMAN_CURL_HEADERS_XC) \
		--data-raw '{ "mock": { "name": "C2mApiV2MockServer", "collection": "$(POSTMAN_TEST_COLLECTION_UID)", "environment": "$(POSTMAN_ENV_UID)", "description": "Mock server environment updated via Makefile.", "private": false } }' \
		--output /dev/null \
		&& echo "✅ Mock server environment updated." \
		|| (echo "❌ Failed to update mock server. Check UID/ID values and API key." && exit 1)

# Verify mock server configuration
.PHONY: verify-mock
verify-mock:
	@echo "🔍 Fetching mock server details..."
	@curl --silent --location --request GET "$(POSTMAN_MOCKS_URL)/$(POSTMAN_MOCK_ID)" \
		--header "x-api-key: $(POSTMAN_API_KEY)" \
		| jq '{ mockUrl: .mock.mockUrl, name: .mock.name, collection: .mock.collection, environment: .mock.environment, private: .mock.private, updatedAt: .mock.updatedAt }'

# ========================================================================
# PRISM MOCK SERVER
# ========================================================================
# Start local Prism mock server
.PHONY: prism-start
prism-start:
	@echo "🚀 Starting Prism mock server on port $(PRISM_PORT)..."
	@mkdir -p $(POSTMAN_DIR)
	# Preflight: npx present?
	@command -v npx >/dev/null 2>&1 || { echo "❌ npx not found. Install Node.js/npm."; exit 1; }
	# Preflight: spec exists?
	@test -f "$(PRISM_SPEC)" || { echo "❌ Spec not found: $(PRISM_SPEC)"; exit 1; }
	# If something is already on the port, stop it first
	@EXISTING=$$(lsof -ti :$(PRISM_PORT)) ; \
	if [ -n "$$EXISTING" ]; then \
		echo "ℹ️ Port $(PRISM_PORT) is in use (PID $$EXISTING). Stopping it..."; \
		kill $$EXISTING || true; sleep 1; \
	fi
	# Start Prism
	@echo "$(PRISM_HOST):$(PRISM_PORT)" > "$(PRISM_MOCK_URL_FILE)"
	@echo "=== $$(date) ===" >> "$(PRISM_LOG)"
	@nohup npx @stoplight/prism-cli mock "$(PRISM_SPEC)" -p $(PRISM_PORT) >> "$(PRISM_LOG)" 2>&1 &
	# Wait up to 15s for the port to bind
	@i=0; \
	while [ $$i -lt 30 ]; do \
		if lsof -ti :$(PRISM_PORT) >/dev/null; then break; fi; \
		sleep 0.5; i=$$((i+1)); \
	done; \
	if lsof -ti :$(PRISM_PORT) >/dev/null; then \
		PID=$$(lsof -ti :$(PRISM_PORT) | head -n1); \
		echo "$$PID" > "$(PRISM_PID_FILE)"; \
		echo "✅ Prism started at $(PRISM_MOCK_URL) (PID: $$PID)"; \
	else \
		echo "❌ Failed to start Prism."; \
		echo "─── Last 60 log lines ───"; \
		tail -n 60 "$(PRISM_LOG)" || true; \
		exit 1; \
	fi

# Stop Prism mock server
.PHONY: prism-stop
prism-stop:
	@if [ -f $(PRISM_PID_FILE) ]; then \
		PID=$$(cat $(PRISM_PID_FILE) | xargs); \
		if [ -n "$$PID" ]; then \
			echo "🔪 Killing Prism PID: $$PID"; \
			kill -9 "$$PID" 2>/dev/null && echo "🛑 Prism stopped." || echo "⚠️  Failed to kill Prism (PID $$PID)"; \
			rm -f $(PRISM_PID_FILE) $(PRISM_MOCK_URL_FILE); \
		else \
			echo "⚠️  PID file is empty. Skipping kill."; \
		fi \
	else \
		echo "ℹ️  No Prism instance running."; \
	fi

# Check Prism status
.PHONY: prism-status
prism-status:
	@echo "🔍 Checking Prism mock server status on port $(PRISM_PORT)..."
	@if lsof -i :$(PRISM_PORT) -t >/dev/null; then \
		echo "✅ Prism is running on port $(PRISM_PORT) (PID: $$(lsof -ti :$(PRISM_PORT)))"; \
	else \
		echo "❌ Prism is not running."; \
	fi

# ========================================================================
# TESTING WITH NEWMAN
# ========================================================================
# Run tests against Prism mock server
.PHONY: prism-mock-test
prism-mock-test:
	@echo "🔬 Running Newman tests against Prism mock with allowed codes: $(POSTMAN_ALLOWED_CODES)..."
	@if [ ! -f $(POSTMAN_TEST_COLLECTION_FIXED) ]; then \
		echo "❌ Missing Postman collection: $(POSTMAN_TEST_COLLECTION_FIXED)"; \
		exit 1; \
	fi
	@if ! lsof -i :$(PRISM_PORT) -t >/dev/null; then \
		echo "❌ Prism is not running on port $(PRISM_PORT). Start it with 'make prism-start'."; \
		exit 1; \
	fi
	@echo "📦 Using test-ready collection: $(POSTMAN_TEST_COLLECTION_FIXED)"
	NODE_OPTIONS=--no-deprecation $(NEWMAN) run $(POSTMAN_TEST_COLLECTION_FIXED) \
		--env-var baseUrl=$(PRISM_MOCK_URL) \
		--env-var token=$(TOKEN) \
		--reporters cli,html \
		--reporter-html-export $(REPORT_HTML)
	@echo "✅ Newman test report generated at $(REPORT_HTML)"

# Sanitize collection placeholders
.PHONY: postman-test-collection-fix-examples
postman-test-collection-fix-examples:
	@echo "🧹 Sanitizing Postman collection placeholders..."
	$(call guard-file,$(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES))
	$(call jqf,$(JQ_SANITIZE_COLLECTION_FILE),$(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES)) > $(POSTMAN_GENERATED_DIR)/c2m.collection.fixed.json
	@echo "✅ Sanitized collection saved to $(POSTMAN_GENERATED_DIR)/c2m.collection.fixed.json"

# Run tests against Postman mock server
.PHONY: postman-mock
postman-mock:
	@echo "🔬 Running Newman tests against Postman mock..."
	@if [ ! -f $(POSTMAN_MOCK_URL_FILE) ]; then \
		echo "ℹ️  Postman mock URL not found. Creating Postman mock..."; \
		$(MAKE) postman-mock-create; \
	fi
	@if [ ! -f $(POSTMAN_TEST_COLLECTION_FIXED) ]; then \
		echo "❌ Missing Postman collection: $(POSTMAN_TEST_COLLECTION_FIXED)"; \
		exit 1; \
	fi
	NODE_OPTIONS=--no-deprecation $(NEWMAN) run $(POSTMAN_TEST_COLLECTION_FIXED) \
		--env-var baseUrl=$(POSTMAN_MOCK_URL) \
		--env-var token=$(TOKEN) \
		--reporters cli,html \
		--reporter-html-export $(REPORT_HTML)
	@echo "📄 Newman test report generated at $(REPORT_HTML)"

# Link environment to mock server
.PHONY: postman-link-env-to-mock-server
postman-link-env-to-mock-server:
	@echo "🔗 Linking environment to mock server..."
	@if [ ! -f $(POSTMAN_ENV_UID_FILE) ]; then echo "❌ Missing environment UID file: $(POSTMAN_ENV_UID_FILE). Run postman-env-upload first."; exit 1; fi
	@if [ ! -f $(POSTMAN_MOCK_UID_FILE) ]; then echo "❌ Missing mock UID file: $(POSTMAN_MOCK_UID_FILE). Run postman-mock-create first."; exit 1; fi
	@if [ ! -f $(POSTMAN_TEST_COLLECTION_UID_FILE) ]; then echo "❌ Missing collection UID file: $(POSTMAN_TEST_COLLECTION_UID_FILE). Run postman-collection-upload-test first."; exit 1; fi
	@POSTMAN_ENV_UID=$$(cat $(POSTMAN_ENV_UID_FILE)); \
	POSTMAN_MOCK_UID=$$(cat $(POSTMAN_MOCK_UID_FILE)); \
	COLLECTION_UID=$$(cat $(POSTMAN_TEST_COLLECTION_UID_FILE)); \
	LINK_DEBUG="$(POSTMAN_MOCK_LINK_DEBUG_FILE)"; \
	echo "📦 Linking Environment $$POSTMAN_ENV_UID with Collection $$COLLECTION_UID (Mock $$POSTMAN_MOCK_UID)..."; \
	curl --silent --location --request PUT "$(POSTMAN_MOCKS_URL)/$$POSTMAN_MOCK_UID" \
		$(POSTMAN_CURL_HEADERS_XC) \
		--data-raw "$$(jq -n --arg coll $$COLLECTION_UID --arg env $$POSTMAN_ENV_UID \
			'{ mock: { name: "Linked Mock Server", collection: $$coll, environment: $$env, private: false } }')" \
		-o "$$LINK_DEBUG"; \
	if jq -e '.mock' "$$LINK_DEBUG" >/dev/null; then \
		echo "✅ Environment linked to mock server successfully."; \
	else \
		echo "❌ Failed to link environment. See $$LINK_DEBUG"; \
		exit 1; \
	fi

# ========================================================================
# DOCUMENTATION GENERATION
# ========================================================================
# Build API documentation with Redoc
.PHONY: docs-build
docs-build:
	@echo "📚 Building API documentation with Redoc..."
	$(REDOCLY) build-docs $(C2MAPIV2_OPENAPI_SPEC) -o $(REDOC_HTML_OUTPUT) -t $(DOCS_DIR)/custom-redoc-template.hbs
	$(SWAGGER) bundle $(C2MAPIV2_OPENAPI_SPEC) --outfile $(OPENAPI_BUNDLED_FILE) --type yaml

# Serve documentation in background
.PHONY: docs-serve-bg
docs-serve-bg:
	@mkdir -p "$(DOCS_DIR)"
	@nohup python3 -m http.server 8080 --directory "$(DOCS_DIR)" >/dev/null 2>&1 & echo $$! > "$(DOCS_PID_FILE)"
	@echo "🌐 Docs served in background on http://localhost:8080 (PID: $$(cat $(DOCS_PID_FILE)))"

# Fix template banner if it disappears
.PHONY: fix-template-banner
fix-template-banner:
	@$(SCRIPTS_DIR)/active/fix-template-banner.sh

# Stop documentation server
.PHONY: docs-stop
docs-stop:
	@if [ -f "$(DOCS_PID_FILE)" ]; then \
		kill $$(cat "$(DOCS_PID_FILE)") 2>/dev/null || true; \
		rm -f "$(DOCS_PID_FILE)"; \
		echo "🛑 Docs server stopped."; \
	else \
		echo "ℹ️ No docs server PID file."; \
	fi

# Serve documentation (blocking)
.PHONY: docs-serve
docs-serve:
	@echo "🌐 Serving API documentation locally on http://localhost:8080..."
	@python3 -m http.server 8080 --directory $(DOCS_DIR)

# ========================================================================
# POSTMAN API MANAGEMENT
# ========================================================================
# List all specs in workspace
.PHONY: postman-api-list-specs
postman-api-list-specs:
	@echo "📜 Listing all specs in workspace $(POSTMAN_WS)..."
	curl --silent \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" \
		"$(POSTMAN_SPECS_URL)?workspaceId=$(POSTMAN_WS)" \
		| jq -r '.specs[] | "\(.name)\t\(.id)\t\(.type)\t\(.updatedAt)"' \
		| column -t -s\t'

# ========================================================================
# CLEANUP OPERATIONS
# ========================================================================
# Delete all mock servers in workspace
.PHONY: postman-delete-mock-servers
postman-delete-mock-servers:
	@echo "🔍 Fetching mock servers from workspace $(POSTMAN_WS)..."
	@MOCKS=$$(curl --silent --location \
		--request GET "$(POSTMAN_MOCKS_URL)$(POSTMAN_Q)" \
		$(POSTMAN_CURL_HEADERS_XC) | jq -r '.mocks[]?.id' 2>/dev/null | grep -v '^null$$' || true); \
	if [ -z "$$MOCKS" ]; then \
		echo "ℹ️  No mock servers found in workspace"; \
	else \
		for MOCK in $$MOCKS; do \
			if [ -n "$$MOCK" ]; then \
				echo "🗑 Deleting mock server $$MOCK..."; \
		curl --silent --location \
			--request DELETE "$(POSTMAN_MOCKS_URL)/$$MOCK" \
			$(POSTMAN_CURL_HEADERS_XC) || echo "⚠️ Failed to delete mock server $$MOCK"; \
		fi; \
		done; \
	fi

# Delete all collections in workspace
.PHONY: postman-delete-collections
postman-delete-collections:
	@echo "🔍 Fetching collections from workspace $(POSTMAN_WS)..."
	@COLLECTIONS=$$(curl --silent --location \
		--request GET "$(POSTMAN_COLLECTIONS_URL)$(POSTMAN_Q)" \
		$(POSTMAN_CURL_HEADERS_XC) | jq -r '.collections[]?.uid' 2>/dev/null | grep -v '^null$$' || true); \
	if [ -z "$$COLLECTIONS" ]; then \
		echo "ℹ️  No collections found in workspace"; \
	else \
		for COL in $$COLLECTIONS; do \
			if [ -n "$$COL" ]; then \
				echo "🗑 Deleting collection $$COL..."; \
		curl --silent --location \
			--request DELETE "$(POSTMAN_COLLECTIONS_URL)/$$COL" \
			$(POSTMAN_CURL_HEADERS_XC) || echo "⚠️ Failed to delete collection $$COL"; \
		fi; \
		done; \
	fi

# Delete all APIs in workspace
.PHONY: postman-delete-apis
postman-delete-apis:
	@echo "🔍 Fetching APIs from workspace $(POSTMAN_WS)..."
	@RESPONSE=$$(curl --silent --location \
		--request GET "$(POSTMAN_APIS_URL)$(POSTMAN_Q_ID)" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)"); \
	echo "$$RESPONSE" | jq -r '.apis[] | "\(.id) - \(.name)"' 2>/dev/null || echo "📊 Checking for APIs..."; \
	APIS=$$(echo "$$RESPONSE" | jq -r '.apis[]?.id' 2>/dev/null | grep -v '^null$$' || true); \
	API_COUNT=$$(echo "$$APIS" | grep -c . || echo 0); \
	echo "📊 Found $$API_COUNT APIs to delete"; \
	if [ -z "$$APIS" ]; then \
		echo "ℹ️  No APIs found in workspace"; \
	else \
		echo "📋 API IDs to delete:"; \
		echo "$$APIS" | sed 's/^/  - /'; \
		echo "$$APIS" | while IFS= read -r API; do \
			if [ -n "$$API" ]; then \
				echo "🗑 Deleting API $$API..."; \
			DELETE_RESPONSE=$$(curl --silent --location --write-out "\n%{http_code}" \
				--request DELETE "$(POSTMAN_APIS_URL)/$$API" \
				--header "X-Api-Key: $(POSTMAN_API_KEY)"); \
			HTTP_CODE=$$(echo "$$DELETE_RESPONSE" | tail -n1); \
			BODY=$$(echo "$$DELETE_RESPONSE" | sed '$$d'); \
			if [ "$$HTTP_CODE" = "200" ] || [ "$$HTTP_CODE" = "204" ]; then \
				echo "✅ Successfully deleted API $$API"; \
			else \
				echo "⚠️  Failed to delete API $$API (HTTP $$HTTP_CODE)"; \
				echo "$$BODY" | jq . 2>/dev/null || echo "$$BODY"; \
			fi; \
		fi; \
		done; \
	fi

# Delete all environments in workspace
.PHONY: postman-delete-environments
postman-delete-environments:
	@echo "🔍 Fetching environments from workspace $(POSTMAN_WS)..."
	@ENVS=$$(curl --silent --location \
		--request GET "$(POSTMAN_ENVIRONMENTS_URL)$(POSTMAN_Q)" \
		--header "X-Api-Key: $(POSTMAN_API_KEY)" | jq -r '.environments[]?.uid' 2>/dev/null | grep -v '^null$$' || true); \
	if [ -z "$$ENVS" ]; then \
		echo "ℹ️  No environments found in workspace"; \
	else \
		for ENV in $$ENVS; do \
			if [ -n "$$ENV" ]; then \
				echo "🗑 Deleting environment $$ENV..."; \
		curl --silent --location \
			--request DELETE "$(POSTMAN_ENVIRONMENTS_URL)/$$ENV" \
			--header "X-Api-Key: $(POSTMAN_API_KEY)" || echo "⚠️ Failed to delete environment $$ENV"; \
		fi; \
		done; \
	fi

# Clean trash in workspace
.PHONY: postman-api-clean-trash
postman-api-clean-trash:
	@echo "🗑️ Checking for trashed specs in workspace $(POSTMAN_WS)..."
	@TRASH=$$(curl --silent \
		$(POSTMAN_CURL_HEADERS_XC) \
		"$(POSTMAN_SPECS_URL)$(POSTMAN_Q_ID)&status=trashed" \
		| jq -r '.specs // [] | .[].id'); \
	if [ -z "$$TRASH" ]; then \
		echo "   No trashed specs found in workspace $(POSTMAN_WS)."; \
	else \
		for ID in $$TRASH; do \
			echo "   🚮 Permanently deleting trashed spec $$ID..."; \
			curl --silent --location \
				--request DELETE "$(POSTMAN_SPECS_URL)/$$ID?permanent=true" \
				$(POSTMAN_CURL_HEADERS_XC) | jq .; \
		done; \
		echo "   ✅ All trashed specs have been permanently deleted."; \
	fi

# Delete old specs keeping the most recent
.PHONY: postman-api-delete-old-specs
postman-api-delete-old-specs:
	@echo "🧹 Deleting old specs in workspace: $(POSTMAN_WS), keeping the most recent one..."
	@RESPONSE=$$(curl --silent $(POSTMAN_CURL_HEADERS_XC) "$(POSTMAN_SPECS_URL)$(POSTMAN_Q_ID)"); \
	echo "$$RESPONSE" > $(POSTMAN_DIR)/specs-debug.json; \
	SPECS=$$(echo "$$RESPONSE" | jq -r 'select(.specs != null) | .specs | sort_by(.updatedAt) | reverse | .[1:] | .[].id'); \
	if [ -z "$$SPECS" ]; then \
		echo "ℹ️  No old specs to delete."; \
	else \
		for ID in $$SPECS; do \
			echo "   ➡️ Deleting spec $$ID..."; \
			curl --silent --location \
				--request DELETE "$(POSTMAN_SPECS_URL)/$$ID" \
				$(POSTMAN_CURL_HEADERS_XC) | jq .; \
		done; \
		echo "✅ Old specs deleted."; \
	fi

# Delete specs by name
.PHONY: postman-delete-specs-by-name
postman-delete-specs-by-name:
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Error: NAME parameter required"; \
		exit 1; \
	fi
	@echo "🔍 Looking for specs named '$(NAME)' in workspace $(POSTMAN_WS)..."
	@SPECS=$$(curl --silent --location \
		--request GET "$(POSTMAN_SPECS_URL)?workspaceId=$(POSTMAN_WS)" \
		$(POSTMAN_CURL_HEADERS_XC) | jq -r --arg name "$(NAME)" '.specs // [] | .[] | select(.name == $$name) | .id'); \
	if [ -z "$$SPECS" ]; then \
		echo "ℹ️  No specs found with name '$(NAME)'"; \
	else \
		for SPEC in $$SPECS; do \
			echo "🗑  Deleting spec $$SPEC..."; \
			curl --silent --location \
				--request DELETE "$(POSTMAN_SPECS_URL)/$$SPEC" \
				$(POSTMAN_CURL_HEADERS_XC) || echo "⚠️ Failed to delete spec $$SPEC"; \
		done; \
		echo "✅ Deleted all specs named '$(NAME)'"; \
	fi

# Delete all specs in workspace
.PHONY: postman-delete-specs
postman-delete-specs:
	@echo "🔍 Fetching specs in workspace $(POSTMAN_WS)..."
	@SPECS=$$(curl --silent --location \
		--request GET "$(POSTMAN_SPECS_URL)?workspaceId=$(POSTMAN_WS)" \
		$(POSTMAN_CURL_HEADERS_XC) | jq -r '.specs // [] | .[].id'); \
	for SPEC in $$SPECS; do \
		echo "🗑 Deleting spec $$SPEC..."; \
		curl --silent --location \
			--request DELETE "$(POSTMAN_SPECS_URL)/$$SPEC" \
			$(POSTMAN_CURL_HEADERS_XC) || echo "⚠️ Failed to delete spec $$SPEC"; \
	done

# Clean all collections in workspace (careful!)
.PHONY: postman-collections-clean
postman-collections-clean:
	@echo "🗑️ Fetching all collections in workspace $(POSTMAN_WS)..."
	@RESPONSE=$$(curl --silent --location \
		--request GET "$(POSTMAN_COLLECTIONS_URL)$(POSTMAN_Q)" \
		$(POSTMAN_CURL_HEADERS_XC); \
	echo "$$RESPONSE" > $(POSTMAN_DIR)/collections-clean-debug.json; \
	COLLECTIONS=$$(echo "$$RESPONSE" | jq -r '.collections[]?.uid'); \
	if [ -z "$$COLLECTIONS" ]; then \
		echo "   ℹ️ No collections found."; \
	else \
		for ID in $$COLLECTIONS; do \
			echo "   🚮 Deleting collection $$ID..."; \
			curl --silent --location \
				--request DELETE "$(POSTMAN_COLLECTIONS_URL)/$$ID" \
				$(POSTMAN_CURL_HEADERS_XC) | jq .; \
		done; \
		echo "   ✅ All collections deleted."; \
	fi

# ========================================================================
# DEBUG OPERATIONS
# ========================================================================
# Debug API import with verbose output
.PHONY: postman-api-debug-A
postman-api-debug-A:
	@echo "🐞 Debugging Postman API import..."

	@curl --verbose --location --request POST "$(POSTMAN_APIS_URL)$(POSTMAN_Q_ID)" \
		$(POSTMAN_CURL_HEADERS_XC) \
		$(POSTMAN_CURL_HEADERS_AA) \
		--data "$$(jq -Rs --arg name '$(POSTMAN_API_NAME)' \
			'{ api: { name: $$name, schema: { type: "openapi3", language: "yaml", schema: . }}}' \
			$(C2MAPIV2_OPENAPI_SPEC)" \
	| tee $(POSTMAN_IMPORT_DEBUG)

# Debug API credentials and workspace
.PHONY: postman-api-debug-B
postman-api-debug-B:
	@echo "🐞 Debugging Postman API credentials and workspace..."

	@echo "🔑 API Key: $(POSTMAN_API_KEY)"
	@echo "🗂️ Workspace: $(POSTMAN_WS)"

	@echo "📡 Verifying API key with /me endpoint..."
	@curl --silent --location \
		$(POSTMAN_CURL_HEADERS_XC) \
		"$(POSTMAN_BASE_URL)/me" \
		| jq . > $(POSTMAN_DIR)/debug-me.json || cat $(POSTMAN_DIR)/debug-me.json
	@echo "✅ Saved to $(POSTMAN_DIR)/debug-me.json"

	@echo "📂 Listing APIs in workspace $(POSTMAN_WS)..."
	@curl --silent --location \
		$(POSTMAN_CURL_HEADERS_XC) \
		"$(POSTMAN_APIS_URL)$(POSTMAN_Q_ID)" \
		| jq . > $(POSTMAN_DIR)/debug-apis.json || cat $(POSTMAN_DIR)/debug-apis.json
	@echo "✅ Saved to $(POSTMAN_DIR)/debug-apis.json"

	@echo "📜 Listing specs in workspace $(POSTMAN_WS)..."
	@curl --silent --location \
		$(POSTMAN_CURL_HEADERS_XC) \
		"$(POSTMAN_SPECS_URL)?workspaceId=$(POSTMAN_WS)" \
		| jq . > $(POSTMAN_DIR)/debug-specs.json || cat $(POSTMAN_DIR)/debug-specs.json
	@echo "✅ Saved to $(POSTMAN_DIR)/debug-specs.json"

# Debug workspace configuration
.PHONY: postman-workspace-debug
postman-workspace-debug:
	@echo "🔍 Current Postman workspace ID: $(POSTMAN_WS)"

# ========================================================================
# ADVANCED TESTING UTILITIES
# ========================================================================
# Test specific endpoint with Prism using request body from Postman collection
.PHONY: prism-test-endpoint
prism-test-endpoint: ## Test specific endpoint with Prism mock server
	@if [ -z "$(PRISM_TEST_ENDPOINT)" ]; then \
		echo "❌ Please specify PRISM_TEST_ENDPOINT. Example: make prism-test-endpoint PRISM_TEST_ENDPOINT=/jobs/single-doc"; \
		exit 1; \
	fi
	@if ! lsof -i :$(PRISM_PORT) -t >/dev/null; then \
		echo "❌ Prism is not running. Start it with 'make prism-start'"; \
		exit 1; \
	fi
	@echo "🧪 Testing endpoint: $(PRISM_TEST_ENDPOINT)"
	@$(SCRIPTS_DIR)/utilities/prism_test.sh "$(PRISM_TEST_ENDPOINT)"

# List available test bodies for an endpoint
.PHONY: prism-test-list
prism-test-list: ## List available test bodies for endpoint
	@if [ -z "$(PRISM_TEST_ENDPOINT)" ]; then \
		echo "❌ Please specify PRISM_TEST_ENDPOINT. Example: make prism-test-list PRISM_TEST_ENDPOINT=/jobs/single-doc"; \
		exit 1; \
	fi
	@$(SCRIPTS_DIR)/utilities/prism_test.sh "$(PRISM_TEST_ENDPOINT)" --list

# Test specific endpoint with selected test body
.PHONY: prism-test-select
prism-test-select: ## Test endpoint with specific test body index
	@if [ -z "$(PRISM_TEST_ENDPOINT)" ]; then \
		echo "❌ Please specify PRISM_TEST_ENDPOINT"; \
		exit 1; \
	fi
	@if [ -z "$(PRISM_TEST_INDEX)" ]; then \
		echo "❌ Please specify PRISM_TEST_INDEX (e.g., PRISM_TEST_INDEX=2)"; \
		exit 1; \
	fi
	@$(SCRIPTS_DIR)/utilities/prism_test.sh "$(PRISM_TEST_ENDPOINT)" --select "$(PRISM_TEST_INDEX)"

# ========================================================================
# SDK GENERATION
# ========================================================================
# Generate SDK from OpenAPI specification
.PHONY: generate-sdk
generate-sdk: ## Generate SDK from OpenAPI specification
	@echo "🔧 Generating SDK from OpenAPI specification..."
	@if [ ! -f "$(C2MAPIV2_OPENAPI_SPEC)" ]; then \
		echo "❌ OpenAPI spec not found: $(C2MAPIV2_OPENAPI_SPEC)"; \
		echo "   Run 'make openapi-build' first"; \
		exit 1; \
	fi
	@if [ -x "$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh" ]; then \
		if [ -n "$(LANG)" ]; then \
			$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh $(LANG); \
		else \
			$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh; \
		fi \
	else \
		echo "⚠️  SDK generation script not implemented yet"; \
		echo "   TODO: Implement $(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh"; \
		echo "   Consider using OpenAPI Generator or similar tool"; \
	fi

# Generate Python SDK
.PHONY: generate-sdk-python
generate-sdk-python: ## Generate Python SDK
	@echo "🐍 Generating Python SDK..."
	@$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh python sdk/python

# Generate JavaScript/Node.js SDK
.PHONY: generate-sdk-javascript
generate-sdk-javascript: ## Generate JavaScript SDK
	@echo "🟨 Generating JavaScript SDK..."
	@$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh javascript sdk/javascript

# Generate TypeScript SDK
.PHONY: generate-sdk-typescript
generate-sdk-typescript: ## Generate TypeScript SDK
	@echo "🔷 Generating TypeScript SDK..."
	@$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh typescript sdk/typescript

# Generate Java SDK
.PHONY: generate-sdk-java
generate-sdk-java: ## Generate Java SDK
	@echo "☕ Generating Java SDK..."
	@$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh java sdk/java

# Generate Go SDK
.PHONY: generate-sdk-go
generate-sdk-go: ## Generate Go SDK
	@echo "🐹 Generating Go SDK..."
	@$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh go sdk/go

# Generate Ruby SDK
.PHONY: generate-sdk-ruby
generate-sdk-ruby: ## Generate Ruby SDK
	@echo "💎 Generating Ruby SDK..."
	@$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh ruby sdk/ruby

# Generate PHP SDK
.PHONY: generate-sdk-php
generate-sdk-php: ## Generate PHP SDK
	@echo "🐘 Generating PHP SDK..."
	@$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh php sdk/php

# Generate C# SDK
.PHONY: generate-sdk-csharp
generate-sdk-csharp: ## Generate C# SDK
	@echo "🔷 Generating C# SDK..."
	@$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh csharp sdk/csharp

# Generate Swift SDK (iOS)
.PHONY: generate-sdk-swift
generate-sdk-swift: ## Generate Swift SDK
	@echo "🦉 Generating Swift SDK..."
	@$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh swift sdk/swift

# Generate Kotlin SDK (Android)
.PHONY: generate-sdk-kotlin
generate-sdk-kotlin: ## Generate Kotlin SDK
	@echo "🤖 Generating Kotlin SDK..."
	@$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh kotlin sdk/kotlin

# Generate Rust SDK
.PHONY: generate-sdk-rust
generate-sdk-rust: ## Generate Rust SDK
	@echo "🦀 Generating Rust SDK..."
	@$(SCRIPTS_DIR)/utilities/generate-sdk-v2.sh rust sdk/rust

# Generate all SDKs
.PHONY: generate-sdk-all
generate-sdk-all: ## Generate SDKs for all supported languages
	@echo "🌐 Generating SDKs for all languages..."
	@$(MAKE) generate-sdk-python
	@$(MAKE) generate-sdk-javascript
	@$(MAKE) generate-sdk-typescript
	@$(MAKE) generate-sdk-java
	@$(MAKE) generate-sdk-go
	@$(MAKE) generate-sdk-ruby
	@$(MAKE) generate-sdk-php
	@$(MAKE) generate-sdk-csharp
	@$(MAKE) generate-sdk-swift
	@$(MAKE) generate-sdk-kotlin
	@$(MAKE) generate-sdk-rust
	@echo "✅ All SDKs generated successfully!"

# Clean generated SDKs
.PHONY: clean-sdk
clean-sdk: ## Clean all generated SDKs
	@echo "🧹 Cleaning generated SDKs..."
	@rm -rf sdk/
	@echo "✅ SDKs cleaned"

# ========================================================================
# DOCUMENTATION DEPLOYMENT
# ========================================================================
# Deploy documentation to hosting service
.PHONY: deploy-docs
deploy-docs: docs-build ## Deploy API documentation
	@echo "🚀 Deploying API documentation..."
	@if [ -x "$(SCRIPTS_DIR)/utilities/deploy-docs.sh" ]; then \
		$(SCRIPTS_DIR)/utilities/deploy-docs.sh; \
	else \
		echo "⚠️  Documentation deployment not implemented yet"; \
		echo "   TODO: Implement $(SCRIPTS_DIR)/utilities/deploy-docs.sh"; \
		echo "   Consider deploying to GitHub Pages, S3, or similar"; \
	fi

# ========================================================================
# MAINTENANCE UTILITIES
# ========================================================================
# Clean up scripts directory
.PHONY: cleanup-scripts
cleanup-scripts: ## Clean up obsolete scripts
	@echo "🧹 Cleaning up scripts directory..."
	@$(SCRIPTS_DIR)/utilities/cleanup-scripts-directory.sh

# Clean up OpenAPI directory
.PHONY: cleanup-openapi
cleanup-openapi: ## Clean up old OpenAPI files
	@echo "🧹 Cleaning up OpenAPI directory..."
	@$(SCRIPTS_DIR)/utilities/cleanup-openapi-directory.sh

# Clean up docs directory
.PHONY: cleanup-docs
cleanup-docs: ## Clean up temporary documentation files
	@echo "🧹 Cleaning up docs directory..."
	@$(SCRIPTS_DIR)/utilities/cleanup-docs-directory.sh

# Clean all directories
.PHONY: cleanup-all
cleanup-all: cleanup-scripts cleanup-openapi cleanup-docs ## Clean all temporary and obsolete files

# ========================================================================
# GIT WORKFLOW HELPERS
# ========================================================================
# Git pull with rebase
.PHONY: git-pull-rebase
git-pull-rebase: ## Pull latest changes with rebase
	@echo "🔄 Pulling latest changes with rebase..."
	@$(SCRIPTS_DIR)/utilities/git-pull-rebase.sh

# Quick save (add, commit, push)
.PHONY: git-save
git-save: ## Quick git save (requires MSG="commit message")
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Please provide a commit message: make git-save MSG=\"your message\""; \
		exit 1; \
	fi
	@echo "💾 Saving changes: $(MSG)"
	@$(SCRIPTS_DIR)/utilities/git-push.sh "$(MSG)"

# ========================================================================
# AUTHENTICATION CONFIGURATION
# ========================================================================
# Setup authentication configuration for collections
.PHONY: postman-auth-setup
postman-auth-setup: ## Configure authentication for Postman collection
	@echo "🔐 Setting up authentication configuration..."
	@if [ -f "$(SECURITY_POSTMAN_SCRIPTS_DIR)/jwt-auth-provider.js" ]; then \
		echo "📋 Using JWT auth provider script from security repo..."; \
		node scripts/active/add_pre_request_script.js "$(POSTMAN_TEST_COLLECTION_WITH_TESTS)" "$(SECURITY_POSTMAN_SCRIPTS_DIR)/jwt-auth-provider.js" "$(POSTMAN_TEST_COLLECTION_WITH_TESTS)" && \
		echo "✅ Auth provider script added to test collection" || \
		echo "❌ Failed to add auth provider script"; \
	else \
		echo "📋 Auth provider script not found in security repo, using local script..."; \
		if [ -f "$(POSTMAN_DIR)/scripts/jwt-pre-request.js" ]; then \
			node scripts/active/add_pre_request_script.js "$(POSTMAN_TEST_COLLECTION_WITH_TESTS)" "$(POSTMAN_DIR)/scripts/jwt-pre-request.js" "$(POSTMAN_TEST_COLLECTION_WITH_TESTS)" && \
			echo "✅ Local auth provider script added to test collection" || \
			echo "❌ Failed to add local auth provider script"; \
		else \
			echo "⚠️  No auth provider script found"; \
		fi; \
	fi

# ========================================================================
# HELP
# ========================================================================
# ========================================================================
# CI/CD ALIASES
# ========================================================================
# These aliases provide stable targets for GitHub Actions CI/CD workflow
# They delegate to existing rich targets maintaining single source of truth

.PHONY: openapi-build
openapi-build: generate-openapi-spec-from-ebnf-dd ## Build OpenAPI from EBNF + overlays + lint [CI alias]
	$(MAKE) openapi-merge-overlays
	$(MAKE) openapi-spec-lint

.PHONY: postman-collection-build
postman-collection-build: ## Generate and flatten the primary collection [CI alias]
	$(MAKE) postman-api-linked-collection-generate
	$(MAKE) postman-linked-collection-flatten

.PHONY: docs
docs: docs-build ## Build API documentation [CI alias]

.PHONY: lint
lint: openapi-spec-lint ## Lint OpenAPI spec [CI alias]

.PHONY: diff
diff: openapi-spec-diff ## Diff OpenAPI spec vs origin/main [CI alias]

.PHONY: postman-publish
postman-publish: ## Push API + collection to current workspace (use POSTMAN_TARGET to control)
	@if [ "$(POSTMAN_TARGET)" = "both" ]; then \
		$(MAKE) postman-publish-both; \
	elif [ "$(POSTMAN_TARGET)" = "team" ]; then \
		$(MAKE) postman-publish-team; \
	elif [ "$(POSTMAN_TARGET)" = "personal" ]; then \
		$(MAKE) postman-publish-personal; \
	else \
		echo "📍 Publishing to default workspace (personal)..."; \
		$(MAKE) postman-import-openapi-as-api; \
		$(MAKE) postman-linked-collection-upload; \
		$(MAKE) postman-linked-collection-link; \
	fi

.PHONY: postman-publish-personal
postman-publish-personal: ## Push complete suite to personal workspace
	@echo "🏠 Publishing to PERSONAL workspace..."
	@if [ -z "$(SKIP_TARGET_SAVE)" ]; then \
		echo "personal" > .postman-target; \
		echo "📝 Saved target 'personal' to .postman-target for CI/CD"; \
	fi
	@echo "🔧 Setting workspace to: $(SERRAO_WS)"
	@echo "🔑 Using API key: POSTMAN_SERRAO_API_KEY"
	@echo ""
	@POSTMAN_WORKSPACE_OVERRIDE=$(SERRAO_WS) POSTMAN_API_KEY_OVERRIDE="$${POSTMAN_SERRAO_API_KEY}" \
		$(MAKE) rebuild-all-with-delete-ci

.PHONY: postman-publish-team
postman-publish-team: ## Push complete suite to team workspace
	@echo "👥 Publishing to TEAM workspace..."
	@if [ -z "$(SKIP_TARGET_SAVE)" ]; then \
		echo "team" > .postman-target; \
		echo "📝 Saved target 'team' to .postman-target for CI/CD"; \
	fi
	@echo "🔧 Setting workspace to: $(C2M_WS)"
	@echo "🔑 Using API key: POSTMAN_C2M_API_KEY"
	@echo ""
	@POSTMAN_WORKSPACE_OVERRIDE=$(C2M_WS) POSTMAN_API_KEY_OVERRIDE="$${POSTMAN_C2M_API_KEY}" \
		$(MAKE) rebuild-all-with-delete-ci

.PHONY: postman-publish-both
postman-publish-both: ## Push API + collection to BOTH workspaces
	@echo "🚀 Publishing to BOTH workspaces..."
	@if [ -z "$(SKIP_TARGET_SAVE)" ]; then \
		echo "both" > .postman-target; \
		echo "📝 Saved target 'both' to .postman-target for CI/CD"; \
	fi
	@echo ""
	@echo "──── Publishing to PERSONAL workspace ────"
	@SKIP_TARGET_SAVE=1 $(MAKE) postman-publish-personal
	@echo ""
	@echo "──── Publishing to TEAM workspace ────"
	@SKIP_TARGET_SAVE=1 $(MAKE) postman-publish-team
	@echo ""
	@echo "🎉 Both workspaces updated successfully!"

# Show all available targets with descriptions
.PHONY: help
help:## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ========================================================================
# WORKSPACE INFORMATION AND SWITCHING
# ========================================================================
.PHONY: workspace-info
workspace-info: ## Show current Postman workspace configuration
	@echo "🔍 Postman Workspace Configuration:"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Current Workspace: $(if $(findstring $(POSTMAN_WS),$(C2M_WS)),C2M Team,Personal/Serrao)"
	@echo "Workspace ID: $(POSTMAN_WS)"
	@echo "API Key: $(if $(findstring $(POSTMAN_API_KEY),$(POSTMAN_C2M_API_KEY)),C2M Team Key,Personal Key)"
	@if [ -f .postman-target ]; then \
		echo "CI/CD Target: $$(cat .postman-target) (from .postman-target file)"; \
	else \
		echo "CI/CD Target: personal (default - no .postman-target file)"; \
	fi
	@echo ""
	@echo "📚 Available Publishing Options:"
	@echo "  • make postman-publish-personal → Publish to personal workspace"
	@echo "  • make postman-publish-team     → Publish to team workspace"
	@echo "  • make postman-publish-both     → Publish to BOTH workspaces"
	@echo ""
	@echo "💡 These commands also save the target for CI/CD in .postman-target"

.PHONY: use-team-workspace
use-team-workspace: ## Force use of C2M team workspace
	@echo "🔄 Forcing C2M team workspace..."
	POSTMAN_WORKSPACE_OVERRIDE=$(C2M_WS) POSTMAN_API_KEY_OVERRIDE=$(POSTMAN_C2M_API_KEY) $(MAKE) workspace-info

.PHONY: use-personal-workspace
use-personal-workspace: ## Force use of personal workspace
	@echo "🔄 Forcing personal workspace..."
	POSTMAN_WORKSPACE_OVERRIDE=$(SERRAO_WS) POSTMAN_API_KEY_OVERRIDE=$(POSTMAN_SERRAO_API_KEY) $(MAKE) workspace-info

# ========================================================================
# LOGGING
# ========================================================================
CUR-DIR := $(shell pwd)
LOG-DIR := $(CUR-DIR)/make-logs

# ========================================================================
# VARIABLE DEBUGGING
# ========================================================================
# Print all variables defined after VARS_OLD
.PHONY: print-vars
print-vars:
	$(foreach v,                                        \
		$(filter-out $(VARS_OLD) VARS_OLD,$$(.VARIABLES)), \
		$(info $(v) = $($(v))))

# ========================================================================
# END OF MAKEFILE
# ========================================================================
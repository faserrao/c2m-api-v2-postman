# C2M API V3 - Comprehensive Documentation

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Directory Structure](#directory-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Directory Documentation](#detailed-directory-documentation)
- [Core Workflows](#core-workflows)
- [Configuration](#configuration)
- [Development Guide](#development-guide)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Deployment](#deployment)
- [Makefile Documentation](#makefile-documentation)
- [Script Usage Analysis](#script-usage-analysis)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Overview

The C2M API V3 is a comprehensive document submission and mail processing API that automates the workflow from data modeling to deployment. The project uses an innovative pipeline that converts EBNF data dictionaries to OpenAPI specifications, generates Postman collections for testing, and provides both cloud and local mock servers for development.

### Key Features

- **Automated API Specification Generation**: Converts EBNF data models to OpenAPI 3.0 specifications
- **Comprehensive Testing Framework**: Automated testing with Newman and Postman collections
- **Mock Server Support**: Both Postman cloud mock and local Prism mock servers
- **Interactive Documentation**: Auto-generated documentation using Redoc and Swagger UI
- **SDK Generation Support**: Framework for generating client SDKs in multiple languages
- **Complete DevOps Pipeline**: Single Makefile orchestrates the entire workflow

### Architecture Flow

```
EBNF Data Dictionary → OpenAPI Spec → Postman Collection → Mock Server → Documentation
         ↓                    ↓              ↓                  ↓              ↓
   Data Modeling        API Design      Testing          Development    Deployment
```

---

## Architecture

The C2M API follows a document submission architecture supporting multiple input sources and processing options:

### Document Sources
- **File Uploads**: Direct file uploads to the API
- **URLs**: Documents fetched from external URLs
- **Document IDs**: References to pre-uploaded documents

### Processing Options
- **Printing**: Various print options including color, duplex, paper types
- **Mailing**: Address validation, return addresses, mail classes
- **Payment**: Multiple payment methods including credit cards and invoicing

### API Design Principles
- RESTful architecture with JSON payloads
- JWT-based authentication
- Comprehensive validation and error handling
- Idempotent operations where applicable

---

## Directory Structure

```
c2m-api-repo/
├── data_dictionary/           # EBNF data model definitions
├── docs/                      # Generated API documentation
├── gen/                       # Generated files (gitignored)
├── node_modules/              # Node.js dependencies
├── Old/                       # Legacy files and backups
├── openapi/                   # OpenAPI specifications
├── postman/                   # Postman collections and tests
├── project_management/        # Project documentation
├── resources/                 # Example requests/responses
├── scripts/                   # Build and utility scripts
├── sdk-clients/               # Generated SDK clients
├── tests/                     # Test suites
├── vscode-setup/              # VS Code configuration
├── Makefile                   # Build orchestration
├── package.json               # Node.js configuration
└── README.md                  # This file
```

---

## Prerequisites

### Required Software
- **macOS/Linux** with bash and make
- **Node.js** (v14+) and npm
- **Python 3** (3.8+)
- **Homebrew** (for macOS users)
- **Postman API Key** (free account required)

### Required Tools
- `jq` - JSON processor
- `curl` - HTTP client
- `git` - Version control
- `diff` - File comparison
- `openapi-diff` - OpenAPI comparison tool

### Installation

```bash
# Install system dependencies (macOS)
brew install jq openapi-diff

# Install Node.js dependencies
make install

# Create Python virtual environment
make venv
```

---

## Quick Start

### 1. Environment Setup

Create a `.env` file in the repository root:

```ini
# Postman API Configuration
POSTMAN_SERRAO_API_KEY=your-postman-api-key-here
# Alternative key (optional)
# POSTMAN_C2M_API_KEY=alternate-key

# Workspace ID (default provided)
POSTMAN_WS=d8a1f479-a2aa-4471-869e-b12feea0a98c

# API Token for testing
TOKEN=dummy-token
```

### 2. Generate OpenAPI from Data Dictionary

```bash
# Convert EBNF to OpenAPI and validate
make postman-dd-to-openapi
```

### 3. Run Complete Pipeline

```bash
# Build, test, and deploy everything
make postman-collection-build-and-test
```

This command will:
1. Authenticate with Postman
2. Import OpenAPI specification
3. Generate and upload collections
4. Create mock servers
5. Run automated tests
6. Build and serve documentation

### 4. Access Documentation

Once complete, access the interactive API documentation at:
- http://localhost:8080 - Redoc documentation

---

## Detailed Directory Documentation

### `/data_dictionary` - Data Model Definitions

This directory contains the formal data model definitions in EBNF (Extended Backus-Naur Form) notation.

#### Key Files:
- **`c2mapiv2-dd.ebnf`** - Main data dictionary defining:
  - Document source structures (upload, URL, ID)
  - Recipient address formats
  - Job options (printing, mailing)
  - Payment method definitions
  
- **`paymentDataUpdate.ebnf`** - Payment-specific definitions:
  - Credit card structures
  - Invoice options
  - Payment validation rules

- **`DataDictionaryQuestions071132025.txt`** - Important clarifications:
  - Business rule documentation
  - Data model decisions
  - Integration requirements

#### Purpose:
The EBNF files serve as the single source of truth for the API's data structures. They are automatically converted to OpenAPI schemas, ensuring consistency across documentation, validation, and client generation.

### `/docs` - API Documentation

Contains the generated API documentation and Swagger UI distribution.

#### Key Files:
- **`swagger.yaml`** - OpenAPI specification file
- **`api.md`** - Markdown API documentation
- **`index.html`** - Main documentation entry point
- **`swagger.html`** - Swagger UI interface
- **`redoc.html`** - Redoc documentation interface
- **`apiTestingReadme.md`** - API testing guidelines

#### Swagger UI Files:
- `swagger-ui-bundle.js` - Core Swagger UI functionality
- `swagger-ui-standalone-preset.js` - Standalone configuration
- `swagger-ui.css` - UI styling
- `oauth2-redirect.html` - OAuth flow handler

#### Purpose:
Provides interactive API documentation for developers, allowing them to explore endpoints, view schemas, and test API calls directly from the browser.

### `/openapi` - OpenAPI Specifications

Contains the OpenAPI 3.0 specifications that define the API contract.

#### Key Files:
- **`c2mapiv2-openapi-spec-final.yaml`** - Production API specification
- **`c2mapiv2-openapi-spec-final-with-examples.yaml`** - Specification with request/response examples
- **`bundled.yaml`** - Single-file bundled specification
- **`tmp-previous-spec.yaml`** - Previous version for diff comparison

#### Subdirectories:
- **`Backups/`** - Historical specification versions
- **`Old/`** - Legacy specification files

#### Purpose:
The OpenAPI specifications are the source of truth for the API contract. They define:
- All API endpoints and operations
- Request/response schemas
- Authentication requirements
- Validation rules
- Example payloads

### `/postman` - Postman Integration

Central hub for Postman collections, environments, and test configurations.

#### Subdirectories:
- **`generated/`** - Auto-generated Postman collections:
  - Raw collections from OpenAPI
  - Test collections with examples
  - Fixed and validated collections
  
- **`custom/`** - User customizations:
  - `overrides.json` - Custom test overrides

#### Key Files:
- **`*_uid.txt`** - Postman resource identifiers
- **`mock-env.json`** - Mock server environment
- **`*-debug.json`** - API response debugging
- **`newman-report.html`** - Test execution reports
- **`prism.log`** - Local mock server logs

#### Purpose:
Facilitates API testing through:
- Automated collection generation
- Mock server configuration
- Environment management
- Test execution and reporting

### `/project_management` - Project Documentation

Contains project planning, documentation, and management resources.

#### Key Files:
- **`Makefile-Documentation.md`** - Comprehensive build system documentation
- **`IssuesQuestionsRisksAndToDo.xlsx`** - Project tracking spreadsheet
- **`c2mApiWorkFlow.drawio`** - Visual workflow diagrams
- **`DocumentedMakefile`** - Annotated Makefile reference

#### Subdirectories:
- **`c2m_todo/`** - Task tracking and todo items
- **`PostmanNotesAndIssues/`** - Postman-specific documentation
- **`ShowAndTell/`** - Demo materials
- **`Github/`** - GitHub integration scripts

#### Purpose:
Provides comprehensive project documentation including:
- Technical architecture decisions
- Workflow documentation
- Issue tracking
- Meeting notes and decisions

### `/resources` - Example Data

Contains sample requests and responses for testing and documentation.

#### Structure:
```
resources/
├── example_requests/
│   └── example_request.json
└── example_responses/
    └── example_response.json
```

#### Purpose:
Provides reference examples for:
- API request formatting
- Expected response structures
- Test data templates
- Integration examples

### `/scripts` - Build and Utility Scripts

Contains all automation scripts used by the build system.

#### Subdirectories:

##### `/scripts/jq/` - JSON Query Filters
- `add_info.jq` - Adds collection metadata
- `auto_fix.jq` - Auto-repairs collections
- `fix_urls.jq` - Corrects URL placeholders
- `sanitize_collection.jq` - Cleans collections
- `verify_urls.jq` - Validates URLs

##### `/scripts/makefile-scripts/` - Makefile Utilities
- Various backup and modification scripts
- Refactoring tools
- Variable management

##### `/scripts/test_data_generator_for_collections/` - Collection Test Data
- `addRandomDataToRaw.js` - Generates random test data
- `README-addRandomDataToRaw.md` - Generator documentation

##### `/scripts/test_data_generator_for_openapi_specs/` - Spec Test Data
- `add_examples_to_spec.py` - Adds examples to OpenAPI
- `test_data_generator.venv/` - Python environment

#### Key Scripts in Use:
1. **Python Scripts**:
   - `ebnf_to_openapi_class_based.py` - EBNF to OpenAPI converter
   - `fix_collection_urls_v2.py` - URL correction utility
   - `generate_test_data.py` - Test data generator

2. **JavaScript Scripts**:
   - `add_tests.js` - Test injection
   - `validate_collection.js` - Collection validator
   - `merge-postman.js` - Collection merger

3. **Shell Scripts**:
   - `deploy-docs.sh` - Documentation deployment
   - `generate-postman.sh` - Collection generation
   - `git-*.sh` - Git automation

#### Purpose:
Provides modular, reusable components for:
- Data transformation
- Validation
- Test generation
- Build automation

### `/sdk-clients` - Client SDKs

Framework for auto-generated client libraries.

#### Structure:
```
sdk-clients/
├── README.md
├── javascript/
│   └── README.md
└── python/
    └── README.md
```

#### Purpose:
Placeholder structure for:
- Auto-generated client SDKs
- Language-specific implementations
- SDK documentation
- Usage examples

### `/tests` - Test Suites

Comprehensive testing infrastructure for the API.

#### Components:

##### `/tests/contract/` - Contract Testing
- `validate_against_spec.js` - Validates API responses against OpenAPI spec

##### `/tests/integration/` - Integration Tests
- `postman_tests.json` - Postman test collections

##### `/tests/python-cli/` - Python CLI Testing
- `cli.py` - Command-line testing tool
- `requirements.txt` - Python dependencies
- Features:
  - JWT authentication
  - All HTTP methods
  - File upload support
  - Response validation

##### `/tests/typescript-cli/` - TypeScript CLI
- `src/index.ts` - TypeScript implementation
- `tsconfig.json` - TypeScript configuration
- `package.json` - Node.js dependencies

#### Purpose:
Ensures API quality through:
- Contract validation
- Integration testing
- Manual testing tools
- Automated test execution

### `/vscode-setup` - VS Code Configuration

Contains Visual Studio Code workspace settings.

#### Files:
- `extensions.json` - Recommended VS Code extensions

#### Recommended Extensions:
- API development tools
- YAML/JSON validators
- Markdown editors
- Git integration

---

## Core Workflows

### 1. Data Dictionary to OpenAPI

```bash
# Generate OpenAPI from EBNF
make generate-openapi-spec-from-dd

# Validate the generated spec
make lint

# Compare with previous version
make diff
```

### 2. Postman Collection Generation

```bash
# Generate collection from OpenAPI
make postman-api-linked-collection-generate

# Add test data
make postman-test-collection-add-examples

# Add automated tests
make postman-test-collection-add-tests

# Validate collection
make postman-test-collection-validate
```

### 3. Mock Server Setup

```bash
# Start local Prism mock
make prism-start

# Create Postman cloud mock
make postman-mock-create

# Update mock environment
make update-mock-env
```

### 4. Testing

```bash
# Test against local mock
make prism-mock-test

# Test against Postman mock
make postman-mock

# View test results
open postman/newman-report.html
```

### 5. Documentation

```bash
# Build documentation
make docs-build

# Serve documentation
make docs-serve

# Or serve in background
make docs-serve-bg
```

---

## Configuration

### Environment Variables

Create a `.env` file with:

```ini
# Required: Postman API Key
POSTMAN_SERRAO_API_KEY=PMAK-xxxxxxxxxxxxx

# Optional: Alternative API Key
POSTMAN_C2M_API_KEY=PMAK-yyyyyyyyyyyyy

# Workspace Configuration
POSTMAN_WS=d8a1f479-a2aa-4471-869e-b12feea0a98c

# Testing Token
TOKEN=your-test-token

# Mock Server Ports (optional)
PRISM_PORT=4010
DOCS_PORT=8080
```

### Makefile Variables

Key configuration variables in the Makefile:

```makefile
# API Naming Conventions
C2MAPIV2_POSTMAN_API_NAME_PC := C2mApiV2      # PascalCase
C2MAPIV2_POSTMAN_API_NAME_CC := c2mApiV2      # camelCase
C2MAPIV2_POSTMAN_API_NAME_SC := c2mapiv2      # snake_case

# Directories
POSTMAN_DIR := postman
OPENAPI_DIR := openapi
SCRIPTS_DIR := scripts
DOCS_DIR := docs

# Testing Configuration
POSTMAN_ALLOWED_CODES := 200,400,401
```

---

## Development Guide

### Adding New Endpoints

1. **Update Data Dictionary**:
   ```ebnf
   # In data_dictionary/c2mapiv2-dd.ebnf
   newEndpoint ::= {
     "field1": string,
     "field2": integer
   }
   ```

2. **Regenerate OpenAPI**:
   ```bash
   make generate-openapi-spec-from-dd
   ```

3. **Rebuild Collections**:
   ```bash
   make postman-collection-build-and-test
   ```

### Custom Test Overrides

Add custom tests in `postman/custom/overrides.json`:

```json
{
  "item": [
    {
      "name": "Custom Test",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Custom validation', function() {",
              "  pm.response.to.have.status(200);",
              "});"
            ]
          }
        }
      ]
    }
  ]
}
```

### Running Specific Tests

```bash
# Test single endpoint
make prism-test-select PRISM_TEST_ENDPOINT=/api/v1/endpoint

# Run with specific Newman options
NODE_OPTIONS=--no-deprecation newman run postman/generated/collection.json
```

---

## API Endpoints

### Document Submission

**POST** `/api/v1/documents`

Submit documents for processing with various source options:

```json
{
  "documentSource": {
    "type": "upload",
    "fileData": "base64-encoded-content"
  },
  "recipients": [
    {
      "name": "John Doe",
      "address": {
        "line1": "123 Main St",
        "city": "Boston",
        "state": "MA",
        "zip": "02101"
      }
    }
  ],
  "jobOptions": {
    "print": {
      "color": true,
      "duplex": "DUPLEX_LONG_EDGE"
    },
    "mail": {
      "mailClass": "FIRST_CLASS"
    }
  }
}
```

### Status Check

**GET** `/api/v1/jobs/{jobId}`

Check the status of a submitted job:

```json
{
  "jobId": "12345",
  "status": "COMPLETED",
  "createdAt": "2024-01-01T00:00:00Z",
  "completedAt": "2024-01-01T00:15:00Z"
}
```

---

## Testing

### Unit Tests

```bash
# Run JavaScript tests
npm test

# Run Python tests
cd tests/python-cli
python -m pytest
```

### Integration Tests

```bash
# Full integration test suite
make postman-collection-build-and-test

# Quick smoke test
make prism-start
make prism-mock-test
```

### Manual Testing

Using the Python CLI:

```bash
cd tests/python-cli
python cli.py --base-url http://localhost:4010 \
              --auth your-jwt-token \
              --method POST \
              --endpoint /api/v1/documents \
              --body '{"test": "data"}'
```

---

## Deployment

### Local Development

```bash
# Start all services
make prism-start
make docs-serve-bg

# Your services are now available at:
# - API Mock: http://localhost:4010
# - Documentation: http://localhost:8080
```

### Production Deployment

1. **Generate Production Spec**:
   ```bash
   make postman-api-full-publish RUN_FULL_PUBLISH=1
   ```

2. **Deploy Documentation**:
   ```bash
   make docs-build
   # Upload docs/ directory to your web server
   ```

3. **Generate SDKs**:
   ```bash
   # Use OpenAPI Generator or similar tool
   openapi-generator generate -i openapi/c2mapiv2-openapi-spec-final.yaml
   ```

---

## Makefile Documentation

The Makefile is the heart of the build system, orchestrating the entire workflow from data dictionary to deployed API.

### Architecture

The Makefile implements a sophisticated build pipeline with the following characteristics:

#### Shell Configuration
```makefile
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
```
- Uses bash with strict error handling
- Exits on errors (-e)
- Errors on undefined variables (-u)
- Fails on pipe errors (-o pipefail)
- Deletes output files on error

#### Logging System
```makefile
say = @printf "%b\n" "$(1)"
ok  = $(call say,✅ $(1))
err = $(call say,❌ $(1))
```
Provides consistent, emoji-enhanced logging throughout the build process.

#### Guard Functions
```makefile
guard-file = test -f "$(1)" || { echo "❌ Missing file: $(1)"; exit 1; }
guard-var  = test -n "$($(1))" || { echo "❌ Missing var: $(1)"; exit 1; }
```
Ensures required files and variables exist before proceeding.

### Core Components

#### 1. Environment Management
The Makefile automatically loads `.env` files and manages environment variables:
- Postman API keys
- Workspace IDs
- Authentication tokens
- Service URLs and ports

#### 2. Path Management
Centralizes all file paths and directories:
```makefile
POSTMAN_DIR := postman
OPENAPI_DIR := openapi
SCRIPTS_DIR := scripts
DOCS_DIR := docs
```

#### 3. HTTP Communication
Provides standardized curl wrappers for API calls:
```makefile
define curl_json
curl --silent --show-error --fail --location \
    $(POSTMAN_CURL_HEADERS_XC) $(1) $(2)
endef
```

#### 4. JSON Processing
Integrates jq for JSON manipulation:
```makefile
jqf = jq -f $(1) $(2)
jqx = jq $(1) $(2)
```

### Primary Targets

#### Installation and Setup
- **`make install`** - Installs all required dependencies
- **`make venv`** - Creates Python virtual environment
- **`make fix-yaml`** - Fixes common PyYAML issues

#### OpenAPI Generation
- **`make postman-dd-to-openapi`** - Complete EBNF to OpenAPI conversion
- **`make generate-openapi-spec-from-dd`** - Core conversion process
- **`make lint`** - Validates OpenAPI with multiple linters
- **`make diff`** - Compares with previous version

#### Postman Integration
- **`make postman-collection-build-and-test`** - Main pipeline
- **`make postman-login`** - Authenticates with Postman
- **`make postman-api-import`** - Imports OpenAPI to Postman
- **`make postman-linked-collection-generate`** - Creates collection
- **`make postman-linked-collection-upload`** - Uploads collection

#### Testing Collections
- **`make postman-test-collection-generate`** - Prepares test collection
- **`make postman-test-collection-add-examples`** - Adds test data
- **`make postman-test-collection-add-tests`** - Injects test scripts
- **`make postman-test-collection-validate`** - Validates structure

#### Mock Servers
- **`make prism-start`** - Starts local mock (port 4010)
- **`make prism-stop`** - Stops local mock
- **`make prism-status`** - Checks mock status
- **`make postman-mock-create`** - Creates cloud mock
- **`make update-mock-env`** - Updates mock configuration

#### Testing Execution
- **`make prism-mock-test`** - Tests against local mock
- **`make postman-mock`** - Tests against cloud mock
- **`make run-postman-and-prism-tests`** - Runs all tests

#### Documentation
- **`make docs-build`** - Generates HTML documentation
- **`make docs-serve`** - Serves docs (blocking)
- **`make docs-serve-bg`** - Serves docs (background)
- **`make docs-stop`** - Stops doc server

#### Cleanup
- **`make postman-cleanup-all`** - Removes all Postman resources
- **`make postman-delete-mock-servers`** - Deletes mocks
- **`make postman-delete-collections`** - Deletes collections
- **`make postman-delete-apis`** - Deletes APIs
- **`make postman-delete-environments`** - Deletes environments

#### Debugging
- **`make postman-api-debug-B`** - Comprehensive API debugging
- **`make print-vars`** - Displays all Makefile variables
- **`make help`** - Shows available targets

### Advanced Features

#### Conditional Execution
```makefile
RUN_FULL_PUBLISH ?= 0
@if [ "$(RUN_FULL_PUBLISH)" = "1" ]; then \
    $(MAKE) postman-api-full-publish; \
fi
```

#### State Management
The Makefile maintains state through various files:
- `postman_api_uid.txt` - API identifier
- `postman_mock_uid.txt` - Mock server ID
- `postman_env_uid.txt` - Environment ID
- `prism_pid.txt` - Local mock process ID

#### Error Recovery
- Automatic retry logic for network operations
- Graceful fallbacks for optional steps
- Comprehensive error messages with debugging hints

#### Parallel Execution
Where possible, independent targets can be run in parallel:
```bash
make -j4 target1 target2 target3 target4
```

### Best Practices

1. **Always run `make venv` before Python operations**
2. **Use `make postman-cleanup-all` to reset state**
3. **Check `.env` for required API keys**
4. **Run `make postman-api-debug-B` when encountering issues**
5. **Use `make print-vars` to inspect variable values**

### Troubleshooting Common Issues

#### PyYAML Import Errors
```bash
make fix-yaml
```

#### Postman Authentication Failures
```bash
# Verify API key
make postman-api-debug-B

# Check workspace access
curl -s "https://api.getpostman.com/me" -H "X-Api-Key: $POSTMAN_API_KEY" | jq .
```

#### Port Conflicts
```makefile
# Change in Makefile or environment
PRISM_PORT ?= 4011  # Different port
```

#### Missing Dependencies
```bash
make install
make venv
```

---

## Script Usage Analysis

### Scripts Currently in Use (17 total)

#### Essential Python Scripts
1. **`ebnf_to_openapi_class_based.py`** - Core EBNF to OpenAPI converter
2. **`fix_collection_urls_v2.py`** - URL correction for collections
3. **`add_examples_to_spec.py`** - Adds examples to OpenAPI specs

#### Critical JavaScript Scripts
1. **`add_tests.js`** - Injects automated tests into collections
2. **`addRandomDataToRaw.js`** - Generates realistic test data
3. **`validate_collection.js`** - Validates Postman collection structure

#### Active JQ Filters
1. **`env_template.jq`** - Environment template generator
2. **`add_info.jq`** - Adds metadata to collections
3. **`auto_fix.jq`** - Auto-repairs invalid collections
4. **`fix_urls.jq`** - Corrects URL placeholders
5. **`sanitize_collection.jq`** - Cleans collection data
6. **`verify_urls.jq`** - Validates all URLs
7. **`merge_overrides.jq`** - Merges custom configurations

### Unused Scripts Analysis (43 total)

A detailed analysis has been performed on all unused scripts. See `UNUSED_SCRIPTS_ANALYSIS.md` for complete recommendations.

#### High-Value Scripts to Integrate (8 scripts)
These provide valuable functionality that should be added to the Makefile:
- **`deploy-docs.sh`** - Documentation deployment automation
- **`generate-sdk.sh`** - SDK generation for multiple languages
- **`git-pull-rebase.sh`** - Standardized git workflow
- **`init-directory-structure.sh`** - Project initialization
- **`generate_test_data.py`** - Enhanced test data generation
- **`verify_urls.py`** - Advanced URL validation
- **`merge-postman.js`** - Complex collection merging

#### Utility Scripts for Manual Use (7 scripts)
Useful for debugging and special operations:
- **`git-push.sh`** - CI/CD pipeline integration
- **`prism_test.sh`** - Advanced Prism testing
- **`makefile-scripts/backup-makefile.sh`** - Makefile version control
- **`makefile-scripts/check_and_create_makefile_files.sh`** - Makefile validation

#### Scripts to Archive or Remove (28 scripts)
- **15 Legacy Scripts**: Replaced by newer versions (e.g., `fix_collection_urls.py` → `fix_collection_urls_v2.py`)
- **13 Experimental Scripts**: Unclear purpose or temporary fixes
- **Duplicates**: JQ scripts existing in multiple locations

### Recommended Actions

1. **Immediate**: Create structured directories:
   ```
   scripts/
   ├── active/      # Currently used scripts
   ├── utilities/   # Manual-use scripts
   ├── archived/    # Legacy reference scripts
   └── README.md    # Script documentation
   ```

2. **Integration**: Add high-value scripts as Makefile targets:
   ```makefile
   make docs-deploy      # Deploy documentation
   make generate-sdks    # Generate client SDKs
   make git-sync        # Sync with upstream
   ```

3. **Cleanup**: Remove duplicates and corrupted files (e.g., files with "Unicode Encoding Conflict")

4. **Documentation**: Add headers to all active scripts with purpose, usage, and dependencies

For complete details and implementation plan, see `UNUSED_SCRIPTS_ANALYSIS.md`.

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "URL rejected: Malformed input"
**Cause**: Trailing spaces in environment variables
**Solution**: 
```bash
# Check for trailing spaces in .env
cat -A .env  # Shows all special characters

# Remove trailing spaces
sed -i '' 's/[[:space:]]*$//' .env
```

#### 2. "Missing file" errors
**Cause**: Build dependencies not met
**Solution**:
```bash
# Ensure all directories exist
mkdir -p postman/generated postman/custom

# Run the full pipeline
make postman-collection-build-and-test
```

#### 3. Prism won't start
**Cause**: Port already in use or missing dependencies
**Solution**:
```bash
# Check what's using the port
lsof -i :4010

# Kill existing process
make prism-stop

# Use different port
PRISM_PORT=4011 make prism-start
```

#### 4. Newman tests fail
**Cause**: Mock server not running or wrong URL
**Solution**:
```bash
# Verify mock is running
make prism-status

# Check mock URL
cat postman/prism_mock_url.txt

# Restart mock
make prism-stop
make prism-start
```

#### 5. Postman API errors
**Cause**: Invalid API key or workspace permissions
**Solution**:
```bash
# Debug API access
make postman-api-debug-B

# Verify workspace membership
curl -s "https://api.getpostman.com/workspaces" \
  -H "X-Api-Key: $POSTMAN_API_KEY" | jq '.workspaces[] | {id, name}'
```

### Debug Workflow

When encountering issues:

1. **Enable verbose output**:
   ```bash
   V=1 make target-name
   ```

2. **Check debug files**:
   ```bash
   ls -la postman/*debug*.json
   cat postman/import-debug.json | jq .
   ```

3. **Verify environment**:
   ```bash
   make print-vars | grep POSTMAN
   ```

4. **Clean and retry**:
   ```bash
   make postman-cleanup-all
   make postman-collection-build-and-test
   ```

---

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Set up development environment:
   ```bash
   make install
   make venv
   cp .env.example .env  # Edit with your API key
   ```

### Making Changes

#### Adding New Endpoints
1. Update EBNF in `data_dictionary/`
2. Regenerate OpenAPI: `make generate-openapi-spec-from-dd`
3. Test changes: `make postman-collection-build-and-test`

#### Improving Scripts
1. Add script to appropriate directory
2. Update Makefile to use the script
3. Document usage in script header
4. Add to this README if significant

#### Updating Documentation
1. Edit relevant markdown files
2. Regenerate docs: `make docs-build`
3. Preview locally: `make docs-serve`

### Testing Your Changes

```bash
# Run full test suite
make postman-collection-build-and-test

# Test specific components
make lint                    # Validate OpenAPI
make postman-test-collection-validate  # Validate collections
make prism-mock-test        # Test with local mock
```

### Submitting Changes

1. Ensure all tests pass
2. Update documentation
3. Create descriptive commit messages
4. Submit pull request with:
   - Description of changes
   - Testing performed
   - Any breaking changes

### Code Style

- **Shell Scripts**: Follow Google Shell Style Guide
- **Python**: PEP 8 compliance
- **JavaScript**: Standard.js style
- **YAML**: 2-space indentation
- **Makefile**: Tabs for recipes, spaces for continuation

---

## License

See LICENSE file in the repository root.

---

## Support

For issues and questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review debug output files in `postman/`
3. Run `make postman-api-debug-B` for diagnostics
4. Create an issue with debug output attached

---

## Changelog

See CHANGELOG.md for version history and migration guides.
# Makefile Documentation - C2M API V2 Postman Integration

## Overview

This Makefile automates the workflow for converting an EBNF data dictionary to an OpenAPI specification, then integrating it with Postman for API testing and documentation. It manages the complete lifecycle from specification generation to mock server deployment.

## Architecture Flow

```
EBNF Data Dictionary → OpenAPI Spec → Postman Collection → Mock Server → Documentation
```

## Key Features

- **Data Dictionary to OpenAPI Conversion**: Converts EBNF format to OpenAPI 3.0 specification
- **Postman Integration**: Automated creation and management of Postman collections, environments, and mock servers
- **Mock Server Support**: Both Postman cloud mock and local Prism mock server
- **API Documentation**: Generates interactive documentation using Redoc
- **Testing Framework**: Newman-based testing with HTML reports
- **Python Virtual Environment**: Isolated Python dependencies for conversion scripts

## Prerequisites

- Node.js and npm
- Python 3
- Postman API key
- Homebrew (for macOS)
- curl, jq, and basic Unix tools

## Environment Variables

The Makefile loads variables from `.env` file if present:

```bash
# .env example
POSTMAN_SERRAO_API_KEY=your-api-key
POSTMAN_C2M_API_KEY=alternate-api-key
```

## Core Variables

### API Naming Convention
- `C2MAPIV2_POSTMAN_API_NAME_PC`: PascalCase (C2mApiV2)
- `C2MAPIV2_POSTMAN_API_NAME_CC`: camelCase (c2mApiV2)
- `C2MAPIV2_POSTMAN_API_NAME_SC`: snake_case (c2mapiv2)
- `C2MAPIV2_POSTMAN_API_NAME_KC`: kebab-case (c2mapiv2)

### Directory Structure
```
.
├── postman/
│   ├── custom/           # User overrides and customizations
│   ├── generated/        # Auto-generated files
│   └── *.json           # Various debug and state files
├── openapi/             # OpenAPI specifications
├── sdks/                # Generated SDKs
├── scripts/             # Helper scripts
├── docs/                # Generated documentation
├── data_dictionary/     # EBNF source files
└── test-data/          # Test data files
```

## Primary Workflows

### 1. Complete Build and Test Pipeline
```bash
make postman-collection-build-and-test
```
This runs the entire pipeline:
- Postman login
- API import
- Collection generation and upload
- Mock server creation
- Environment setup
- Documentation build

### 2. Generate OpenAPI from Data Dictionary
```bash
make postman-dd-to-openapi
```
Converts EBNF data dictionary to OpenAPI specification with linting.

### 3. Quick Rebuild (No Deletion)
```bash
make rebuild-all-no-delete
```
Rebuilds everything without cleaning existing resources.

### 4. Full Cleanup
```bash
make postman-cleanup-all
```
Removes all Postman resources from the workspace.

## Key Targets

### Installation and Setup
- `make install` - Install all required npm packages and tools
- `make venv` - Create Python virtual environment
- `make fix-yaml` - Fix PyYAML installation issues

### OpenAPI Management
- `make generate-openapi-spec-from-dd` - Convert EBNF to OpenAPI
- `make lint` - Lint OpenAPI spec with Redocly and Spectral
- `make diff` - Compare current spec with origin/main

### Postman Operations
- `make postman-login` - Authenticate with Postman API
- `make postman-api-import` - Import OpenAPI spec to Postman
- `make postman-linked-collection-generate` - Generate Postman collection
- `make postman-test-collection-upload` - Upload test collection

### Mock Servers
- `make prism-start` - Start local Prism mock server (port 4010)
- `make prism-stop` - Stop Prism mock server
- `make postman-mock-create` - Create Postman cloud mock server

### Testing
- `make postman-mock` - Run Newman tests against Postman mock
- `make prism-mock-test` - Run Newman tests against Prism mock

### Documentation
- `make docs-build` - Build HTML documentation with Redoc
- `make docs-serve` - Serve documentation locally (port 8080)
- `make docs-serve-bg` - Serve documentation in background

### Debugging
- `make postman-api-debug-B` - Debug API credentials and workspace
- `make print-vars` - Print all Makefile variables
- `make help` - Show available targets

## Advanced Features

### Shell Safety
The Makefile uses strict shell options:
```makefile
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
```

### Logging Helpers
- `say` - Print formatted messages
- `ok` - Print success messages with ✅
- `err` - Print error messages with ❌

### Guard Functions
- `guard-file` - Ensure file exists before proceeding
- `guard-var` - Ensure variable is set

### JSON Processing
Centralized jq filters for consistent JSON manipulation:
- `jq_add_info.jq` - Add collection info
- `jq_fix_urls.jq` - Fix URL placeholders
- `jq_auto_fix.jq` - Auto-fix collection structure
- `jq_sanitize_collection.jq` - Clean up placeholders

### HTTP Headers
Predefined header combinations for Postman API:
- `POSTMAN_CURL_HEADERS_XC` - X-Api-Key + Content-Type
- `POSTMAN_CURL_HEADERS_AA` - Accept + Authorization
- `POSTMAN_CURL_HEADERS_ACA` - All headers combined

## Workflow Examples

### Initial Setup
```bash
# Install dependencies
make install

# Create Python environment
make venv

# Generate OpenAPI from data dictionary
make generate-openapi-spec-from-dd
```

### Development Workflow
```bash
# Start local mock server
make prism-start

# Run tests against local mock
make prism-mock-test

# View test report
open postman/newman-report.html
```

### Production Deployment
```bash
# Full pipeline with Postman cloud
make postman-collection-build-and-test

# Optionally publish to Postman
make postman-collection-build-and-test RUN_FULL_PUBLISH=1
```

### Cleanup
```bash
# Remove all Postman resources
make postman-cleanup-all

# Stop local services
make prism-stop
make docs-stop
```

## State Management

The Makefile maintains state through various files:
- `postman_api_uid.txt` - Current API ID
- `postman_mock_uid.txt` - Mock server ID
- `postman_env_uid.txt` - Environment ID
- `test_collection_uid.txt` - Test collection ID
- `prism_pid.txt` - Prism process ID

## Troubleshooting

### Common Issues

1. **PyYAML Import Error**
   ```bash
   make fix-yaml
   ```

2. **Postman API Authentication**
   - Verify API key in `.env`
   - Check workspace ID in variables

3. **Port Conflicts**
   - Prism: Change `PRISM_PORT` (default 4010)
   - Docs: Change port in `docs-serve` target

4. **Missing Dependencies**
   ```bash
   make install
   make venv
   ```

### Debug Commands
```bash
# Check Postman credentials
make postman-api-debug-B

# View all variables
make print-vars

# Check specific workflow state
cat postman/*.txt
```

## Best Practices

1. **Always run `make venv` before Python operations**
2. **Use `make postman-cleanup-all` to reset state**
3. **Check `.env` file for API keys before running**
4. **Review generated files in `postman/generated/`**
5. **Use dry-run options when available**
6. **Monitor `postman/*.json` files for API responses**

## Notes

- The Makefile supports multiple Postman workspaces (SERRAO_WS, C2M_WS)
- Spec API endpoints use `workspaceId=` while others use `workspace=`
- All HTTP operations include proper error handling and debug output
- The system maintains backward compatibility with v2.1.0 Postman collections

---

This Makefile represents a complete DevOps pipeline for API development, testing, and documentation, with robust error handling and state management throughout the workflow.
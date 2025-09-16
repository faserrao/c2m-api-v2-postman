# C2M API v2 Build System Technical Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Flow](#architecture-flow)
3. [Core Components](#core-components)
4. [Build Pipeline Stages](#build-pipeline-stages)
5. [Makefile Target Categories](#makefile-target-categories)
6. [Dynamic Resource Management](#dynamic-resource-management)
7. [Test Generation and Execution](#test-generation-and-execution)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Environment Management](#environment-management)
10. [Build System Operations](#build-system-operations)

## System Overview

The C2M API v2 build system is a sophisticated orchestration framework that transforms EBNF data dictionary definitions into a complete API ecosystem. It leverages Make as the primary orchestration tool, coordinating Python scripts, Node.js tools, and various API services to create a fully automated development pipeline.

### Key Design Principles
- **Single Source of Truth**: EBNF data dictionary drives all API specifications
- **Dynamic Generation**: No hardcoded endpoints or schemas
- **Idempotent Operations**: All operations can be safely re-run
- **Environment Isolation**: Python virtual environments and npm local installations
- **CI/CD Integration**: Seamless GitHub Actions workflow support

## Architecture Flow

The build system follows this transformation pipeline:

```
EBNF Data Dictionary
    ↓ (Python: ebnf_to_openapi_dynamic_v3.py)
OpenAPI Base Specification
    ↓ (Python: merge_openapi_overlays.py)
OpenAPI Final Specification
    ↓ (npm: openapi-to-postmanv2)
Postman Collection (Raw)
    ↓ (Multiple transformation steps)
Test Collection + Linked Collection
    ↓ (Postman API)
Mock Server + Environment
    ↓ (Newman/Prism)
Test Execution + Documentation
```

## Core Components

### 1. Makefile Structure
The Makefile serves as the orchestration layer with several key sections:

- **Environment Configuration** (lines 30-60): Shell setup, logging helpers, and validation guards
- **Directory Structure** (lines 87-108): Defines all working directories
- **File Definitions** (lines 110-207): Declares input/output files for each stage
- **Tool Configuration** (lines 316-327): External tool definitions
- **Target Definitions** (lines 400+): Build targets and dependencies

### 2. Script Categories

#### Active Scripts (`scripts/active/`)
- `ebnf_to_openapi_dynamic_v3.py`: Core EBNF→OpenAPI converter using Lark parser
- `merge_openapi_overlays.py`: Merges authentication and other overlays
- `add_tests.js`: Injects Postman test scripts into collections
- `fix_collection_urls_v2.py`: Normalizes URLs to use {{baseUrl}} variable
- `validate_collection.js`: Validates Postman collection structure

#### JQ Filters (`scripts/jq/`)
- `add_info.jq`: Adds collection metadata
- `fix_urls.jq`: URL normalization transformations
- `merge_overrides.jq`: Merges custom test overrides
- `sanitize_collection.jq`: Cleans collection structure

### 3. Configuration Files
- `package.json`: Node.js dependencies for Postman tools, linting, and documentation
- `openapitools.json`: OpenAPI generator configuration
- `.env`: Local environment variables (API keys, workspace IDs)

## Build Pipeline Stages

### Stage 1: EBNF to OpenAPI Conversion

**Target**: `generate-openapi-spec-from-ebnf-dd`

**Process**:
1. Python virtual environment activation
2. Parse EBNF file with Lark grammar parser
3. Extract endpoint definitions from EBNF comments
4. Generate OpenAPI schemas from EBNF productions
5. Resolve type chains (e.g., `documentId → id → integer`)
6. Output base OpenAPI specification

**Key Features**:
- Dynamic endpoint discovery from comments like `(* GET /jobs *)`
- Automatic schema generation from EBNF productions
- Type inference and resolution
- Comprehensive error reporting

### Stage 2: OpenAPI Overlay Merging

**Target**: `openapi-merge-overlays`

**Process**:
1. Load base OpenAPI specification
2. Load authentication overlay (`auth.tokens.yaml`)
3. Deep merge overlays preserving base definitions
4. Special handling for paths to avoid overrides
5. Output final OpenAPI specification

### Stage 3: Postman Collection Generation

**Target**: `postman-api-linked-collection-generate`

**Process**:
1. Use `openapi-to-postmanv2` to convert OpenAPI→Postman
2. Apply collection metadata and schema
3. Generate raw collection JSON
4. Store collection structure for further processing

### Stage 4: Test Collection Enhancement

**Targets**: Multiple sequential targets
- `postman-test-collection-add-examples`: Inject random test data
- `postman-test-collection-merge-overrides`: Apply custom overrides
- `postman-test-collection-add-tests`: Add test scripts
- `postman-test-collection-fix-v2`: Fix URL structures
- `postman-test-collection-flatten-rename`: Flatten nested structures

**Process**:
1. Load raw collection
2. Use Faker.js to generate realistic test data
3. Merge custom test configurations from `postman/custom/overrides.json`
4. Inject test scripts for response validation
5. Normalize all URLs to use `{{baseUrl}}` variable
6. Flatten collection hierarchy for better usability

### Stage 5: Postman API Integration

**Targets**: Various `postman-*-upload` targets

**Process**:
1. Authenticate with Postman API using workspace-specific key
2. Create/update API definition
3. Upload collections (linked and test versions)
4. Create mock server
5. Generate and upload environment with mock URL
6. Link environment to mock server

### Stage 6: Documentation Generation

**Target**: `docs-build`

**Process**:
1. Use Redocly to generate static HTML documentation
2. Apply custom templates and styling
3. Generate both Redoc and Swagger UI versions
4. Prepare for GitHub Pages deployment

## Makefile Target Categories

### 1. Primary Workflow Targets

#### `postman-instance-build-and-test`
Complete pipeline execution including local testing:
```make
postman-login
postman-import-openapi-spec
postman-spec-create-standalone
postman-create-linked-collection
postman-create-test-collection
postman-create-mock-and-env
prism-start
postman-mock
postman-docs-build-and-serve-up
```

#### `postman-instance-build-only`
CI-optimized version without local testing

### 2. Cleanup Targets

#### `postman-cleanup-all`
Removes all Postman resources:
- Mock servers
- Collections
- APIs
- Environments
- Specifications

### 3. Utility Targets

- `workspace-info`: Display current workspace configuration
- `print-vars`: Debug variable values
- `help`: Show available targets

### 4. CI/CD Aliases

- `openapi-build`: Build OpenAPI from EBNF
- `postman-collection-build`: Generate collections
- `docs`: Build documentation
- `lint`: Lint OpenAPI specification
- `diff`: Compare against main branch

## Dynamic Resource Management

### Resource Discovery
The system dynamically discovers resources through:

1. **EBNF Comment Parsing**: Endpoints defined as `(* METHOD /path *)`
2. **Production Analysis**: Schema generation from EBNF rules
3. **Type Resolution**: Following type chains to base types

### Resource Tracking
Resources are tracked using UID files:
- `postman_api_uid.txt`: API definition ID
- `test_collection_uid.txt`: Test collection ID
- `postman_env_uid.txt`: Environment ID
- `postman_mock_uid.txt`: Mock server ID

### Workspace Management
The system supports multiple workspaces:
- Personal workspace (default): `SERRAO_WS`
- Team workspace: `C2M_WS`
- Selection via `POSTMAN_TARGET` variable

## Test Generation and Execution

### Test Data Generation

**Script**: `addRandomDataToRaw.js`

Generates realistic test data using Faker.js:
- Names, addresses, emails
- Dates and timestamps
- UUIDs and identifiers
- Custom domain-specific data

### Test Script Injection

**Script**: `add_tests.js`

Injects Postman test scripts:
- Status code validation
- Response schema validation
- Response time checks
- Custom business logic tests

### Test Execution

#### Newman (Postman CLI)
```bash
newman run collection.json \
  -e environment.json \
  --reporters cli,html \
  --allowed-codes 200,201,204,400,401,403,404,429
```

#### Prism Mock Server
Local OpenAPI mock server for development:
```bash
prism mock -p 4010 openapi-spec.yaml
```

## CI/CD Pipeline

### GitHub Actions Workflow (`api-ci-cd.yml`)

#### Triggers
- Push to main branch
- Pull requests
- Manual workflow dispatch

#### Job Stages

1. **Setup**
   - Checkout repositories (main + security)
   - Install Node.js and Python
   - Install dependencies

2. **Build**
   - Generate OpenAPI from EBNF
   - Build Postman collections
   - Lint OpenAPI specification
   - Generate documentation

3. **Validation**
   - Check for uncommitted changes
   - Run drift detection
   - Validate generated artifacts

4. **Publish** (main branch only)
   - Upload to Postman workspaces
   - Deploy to GitHub Pages
   - Commit generated artifacts

### PR Drift Check (`pr-drift-check.yml`)

Ensures generated files are committed:
1. Regenerates all artifacts
2. Checks for git differences
3. Comments on PR with instructions if drift detected

## Environment Management

### Local Development
- `.env` file for API keys and configuration
- Python virtual environment in `scripts/python_env/e2o.venv`
- Node modules in local `node_modules`

### CI/CD Environment
- Secrets stored in GitHub repository settings
- Environment variables passed to Make targets
- Conditional logic for CI vs local execution

### Postman Environments
Dynamic environment generation includes:
- Base URL configuration
- Mock server URL
- Authentication tokens
- Custom variables

## Build System Operations

### Incremental Builds
The system supports incremental operations:
- Skip EBNF conversion if OpenAPI exists
- Reuse existing collections if unchanged
- Update only modified resources

### Error Handling
Comprehensive error handling throughout:
- File existence guards
- API call error checking
- Validation at each stage
- Graceful degradation for optional steps

### Parallel Execution
Where possible, operations run in parallel:
- Multiple file transformations
- API resource queries
- Test executions

### Logging and Debugging
- Structured logging with emoji indicators
- Debug files for API interactions
- Verbose mode support (`V=1`)
- Step-by-step execution tracking

## Advanced Features

### 1. Multi-Format Documentation
Generates documentation in multiple formats:
- Redoc (primary)
- Swagger UI (alternative)
- Markdown (for GitHub)

### 2. SDK Generation
Supports SDK generation for multiple languages:
- Python, JavaScript, TypeScript
- Java, Go, Ruby
- PHP, C#, Swift
- Kotlin, Rust

### 3. Authentication Integration
Seamlessly integrates with external auth system:
- JWT token management
- Pre-request scripts
- Token refresh logic

### 4. Example Data Injection
Sophisticated example generation:
- Context-aware data
- Referential integrity
- Realistic values
- Multiple scenarios

## Troubleshooting Guide

### Common Issues

1. **Missing Dependencies**
   - Run `make install` to install all dependencies
   - Check Python virtual environment activation

2. **API Key Issues**
   - Verify `.env` file exists and contains keys
   - Check workspace permissions

3. **Generation Failures**
   - Validate EBNF syntax
   - Check for circular type references
   - Review error logs

4. **CI/CD Failures**
   - Ensure secrets are configured
   - Check branch protection rules
   - Verify artifact paths

### Debug Commands
```bash
# Show all variables
make print-vars

# Test specific endpoint
make prism-test-endpoint ENDPOINT=/jobs METHOD=GET

# Validate collection
make postman-test-collection-validate

# Check workspace
make workspace-info
```

## Best Practices

1. **Always run `make install` first** - Ensures all dependencies are available
2. **Use incremental builds** - Faster development cycles
3. **Commit generated files** - Prevents CI/CD drift
4. **Test locally first** - Use `postman-instance-build-and-test`
5. **Clean periodically** - Use `postman-cleanup-all` to reset
6. **Monitor API limits** - Postman has rate limits
7. **Version control overlays** - Keep auth overlays in sync

## Conclusion

The C2M API v2 build system represents a sophisticated approach to API development, treating the EBNF data dictionary as the single source of truth and automating the entire pipeline from specification to deployment. Its modular design, comprehensive error handling, and CI/CD integration make it a robust foundation for API development and maintenance.
# C2M API v2 Build Processes Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture Flow](#architecture-flow)
3. [Build Environment](#build-environment)
4. [Local Build Process](#local-build-process)
5. [GitHub Actions CI/CD](#github-actions-cicd)
6. [Configuration Files](#configuration-files)
7. [Build Tools and Dependencies](#build-tools-and-dependencies)
8. [Build Targets and Commands](#build-targets-and-commands)
9. [Artifacts Generated](#artifacts-generated)
10. [Key Differences: Local vs GitHub](#key-differences-local-vs-github)

## Overview

The C2M API v2 build system is a comprehensive pipeline that transforms an EBNF (Extended Backus-Naur Form) data dictionary into a fully functional API ecosystem including:
- OpenAPI 3.0.3 specification
- Postman collections and tests
- Mock servers (Postman and Prism)
- SDK generation for multiple languages
- API documentation (Swagger UI and Redoc)

## Architecture Flow

```
EBNF Data Dictionary
    ↓
OpenAPI Spec Generation (Python)
    ↓
Auth Overlay Merge
    ↓
OpenAPI Validation & Linting
    ↓
Postman Collection Generation
    ↓
Test Addition & Validation
    ↓
Mock Server Creation
    ↓
SDK Generation
    ↓
Documentation Build
```

## Build Environment

### Directory Structure
```
c2m-api-repo/
├── data_dictionary/          # EBNF source files
│   └── c2mapiv2-dd.ebnf     # Main data dictionary
├── openapi/                  # OpenAPI specifications
│   ├── overlays/            # Auth and other overlays
│   └── *.yaml               # Generated specs
├── postman/                  # Postman collections
│   ├── custom/              # Custom overrides
│   ├── generated/           # Auto-generated files
│   └── scripts/             # Pre-request scripts
├── scripts/                  # Build scripts
│   ├── active/              # Current scripts
│   ├── jq/                  # JQ filters
│   └── archived/            # Legacy scripts
├── sdk/                      # Generated SDKs
├── docs/                     # API documentation
└── tests/                    # Test suites
```

### Environment Variables

#### Required for Postman Operations
- `POSTMAN_SERRAO_API_KEY`: Personal workspace API key
- `POSTMAN_C2M_API_KEY`: Organization workspace API key
- `POSTMAN_WS`: Workspace ID (auto-detected based on branch)

#### Python Environment
- `VENV_DIR`: Virtual environment directory (default: `venv`)
- `PYTHON3`: Python executable (default: `python3`)

## Local Build Process

### 1. EBNF to OpenAPI Conversion

**Script**: `scripts/active/ebnf_to_openapi_dynamic_v3.py`

**Process**:
1. Parse EBNF data dictionary using Lark parser
2. Extract endpoint definitions from comments
3. Generate OpenAPI schemas from EBNF productions
4. Resolve type chains dynamically
5. Output base OpenAPI spec

**Key Features**:
- Fully dynamic - no hardcoded endpoints
- Comprehensive type resolution
- Issue reporting and validation

### 2. OpenAPI Overlay Merge

**Script**: `scripts/active/merge_openapi_overlays.py`

**Process**:
1. Load base OpenAPI spec
2. Load auth overlay (`openapi/overlays/auth.tokens.yaml`)
3. Deep merge preserving complex structures
4. Add authentication endpoints and schemas

### 3. OpenAPI Validation

**Tools**: 
- Redocly CLI
- Spectral CLI

**Validations**:
- Schema validity
- Reference resolution
- Best practices compliance
- Security definitions

### 4. Postman Collection Generation

**Process**:
1. Convert OpenAPI to Postman using `openapi-to-postmanv2`
2. Generate linked collection (references API definition)
3. Generate test collection (standalone)
4. Add examples using Faker.js
5. Merge custom overrides
6. Add test scripts
7. Fix URLs and validate structure

### 5. Mock Server Setup

**Prism (Local)**:
- Runs on `http://127.0.0.1:4010`
- Uses OpenAPI spec with examples
- Provides realistic responses

**Postman Mock**:
- Cloud-based mock server
- Syncs with test collection
- Available for external testing

### 6. Documentation Generation

**Tools**:
- Swagger UI
- Redoc
- Custom templates

**Output**:
- Interactive API documentation
- Try-it-out functionality
- Code examples

## GitHub Actions CI/CD

### Main Workflow: `api-ci-cd.yml`

**Triggers**:
- Push to main branch
- Pull requests
- Manual dispatch

**Jobs**:

#### 1. Build Job
```yaml
steps:
  - Checkout repository
  - Checkout security repository
  - Setup Node.js and Python
  - Install dependencies
  - Build OpenAPI from EBNF
  - Build Postman collection
  - Lint OpenAPI spec
  - Diff OpenAPI spec (PRs only)
  - Build documentation
  - Check for uncommitted changes
  - Publish to Postman (main only)
  - Commit generated artifacts
  - Upload artifacts
```

#### 2. Deploy Pages Job
- Deploys documentation to GitHub Pages
- Only runs on main branch
- Uses GitHub Pages action

### Supporting Workflows

**`openapi-ci.yml`**: Validates OpenAPI spec
**`deploy-docs.yml`**: Deploys documentation
**`lint-openapi.yaml`**: Runs linting checks
**`pr-drift-check.yml`**: Ensures generated files are committed

## Configuration Files

### 1. `Makefile`
- Primary orchestration tool
- 600+ lines of targets and dependencies
- Handles entire build pipeline
- Environment-aware (local vs CI)

### 2. `package.json`
- Node.js dependencies
- Scripts for linting and docs
- Dev dependencies for build tools

### 3. `openapitools.json`
- OpenAPI Generator configuration
- Version specification

### 4. `sdk-config.yaml`
- SDK generation settings
- Language-specific configurations
- Template customizations

### 5. `.env` (Local only)
- API keys
- Environment-specific settings

## Build Tools and Dependencies

### Core Tools

#### Python (3.11+)
- Lark parser for EBNF
- PyYAML for YAML processing
- Custom conversion scripts

#### Node.js (20+)
- Postman collection tools
- OpenAPI validators
- Documentation generators
- Test frameworks

#### System Tools
- `jq`: JSON processing
- `curl`: API interactions
- `make`: Build orchestration
- `git`: Version control

### Key NPM Packages
```json
{
  "@redocly/cli": "^1.34.5",
  "@stoplight/spectral-cli": "^6.15.0",
  "@stoplight/prism-cli": "^5.14.2",
  "openapi-to-postmanv2": "^5.1.0",
  "postman-collection": "^5.0.2",
  "newman": "^4.6.1",
  "swagger-ui-dist": "^5.29.0",
  "@faker-js/faker": "^9.9.0"
}
```

### Python Dependencies
```
lark==1.1.5
PyYAML==6.0
requests==2.31.0
jsonschema==4.17.3
```

## Build Targets and Commands

### Primary Targets

#### Complete Pipeline
```bash
make postman-instance-build-and-test  # Full build with testing
make postman-instance-build-only      # Build without local testing (CI)
```

#### OpenAPI Generation
```bash
make ebnf-dd-to-openapi-spec          # Convert EBNF to OpenAPI
make openapi-merge-overlays           # Merge auth overlay
make openapi-spec-lint                # Validate spec
```

#### Postman Operations
```bash
make postman-create-linked-collection # Generate linked collection
make postman-create-test-collection   # Generate test collection
make postman-create-mock-and-env      # Create mock server
```

#### Documentation
```bash
make docs-build                       # Build documentation
make docs-serve                       # Serve locally
```

#### Cleanup
```bash
make postman-cleanup-all              # Remove all Postman resources
make clean                            # Clean local files
```

### CI-Specific Targets
```bash
make rebuild-all-no-delete-ci         # CI build without cleanup
make rebuild-all-with-delete-ci       # CI build with cleanup
```

## Artifacts Generated

### OpenAPI Specifications
- `c2mapiv2-openapi-spec-base.yaml`: Base spec from EBNF
- `c2mapiv2-openapi-spec-final.yaml`: Merged with overlays
- `c2mapiv2-openapi-spec-final-with-examples.yaml`: With test data

### Postman Collections
- `c2mapiv2-collection.json`: Raw collection
- `c2mapiv2-linked-collection-flat.json`: Flattened linked
- `c2mapiv2-test-collection-final.json`: Test collection
- `c2mapiv2-test-collection-jwt.json`: With JWT tests

### Documentation
- `docs/index.html`: Redoc documentation
- `docs/swagger.html`: Swagger UI
- `docs/api.md`: Markdown documentation

### SDKs (Multiple Languages)
- Python: `sdk/python/`
- JavaScript: `sdk/javascript/`
- TypeScript: `sdk/typescript/`
- Java: `sdk/java/`
- Go: `sdk/go/`
- Ruby: `sdk/ruby/`
- PHP: `sdk/php/`
- C#: `sdk/csharp/`
- Kotlin: `sdk/kotlin/`
- Swift: `sdk/swift/`
- Rust: `sdk/rust/`

### Mock Server Files
- `postman_mock_url.txt`: Postman mock URL
- `prism_mock_url.txt`: Local Prism URL
- `mock-env.json`: Environment configuration

## Key Differences: Local vs GitHub

### Local Build
- Uses `.env` file for API keys
- Can run Prism mock server
- Interactive documentation serving
- Full test execution with Newman
- Direct Postman API access

### GitHub Actions Build
- Uses GitHub Secrets for API keys
- Skips local mock server testing
- Automated artifact uploads
- Parallel job execution
- Deployment to GitHub Pages
- Security repository integration
- Postman CLI pre-installed

### Environment Detection
```makefile
ifdef CI
    # GitHub Actions specific
    SECURITY_POSTMAN_SCRIPTS_DIR := c2m-api-v2-security/postman/scripts
else
    # Local development
    SECURITY_POSTMAN_SCRIPTS_DIR := ../c2m-api-v2-security/postman/scripts
endif
```

## Build Process Chain

### Complete Build Flow

1. **Data Dictionary Processing**
   - Read EBNF file
   - Parse with Lark
   - Extract endpoints from comments
   - Generate type definitions

2. **OpenAPI Generation**
   - Convert EBNF to OpenAPI schemas
   - Add standard responses
   - Include security definitions
   - Merge auth overlay

3. **Validation Phase**
   - Lint with Spectral
   - Validate with Redocly
   - Check references
   - Verify examples

4. **Postman Collection Creation**
   - Convert OpenAPI to Postman
   - Add pre-request scripts
   - Include test assertions
   - Apply custom overrides

5. **Mock Server Setup**
   - Start Prism locally
   - Create Postman mock
   - Configure environments
   - Test endpoints

6. **SDK Generation**
   - Use OpenAPI Generator
   - Apply language configs
   - Generate documentation
   - Create examples

7. **Documentation Build**
   - Generate Swagger UI
   - Build Redoc site
   - Create markdown docs
   - Deploy to GitHub Pages

## Troubleshooting

### Common Issues

1. **PyYAML Import Errors**
   ```bash
   make fix-yaml
   ```

2. **Postman API Failures**
   - Check API key validity
   - Verify workspace permissions
   - Ensure collection UIDs exist

3. **OpenAPI Validation Errors**
   - Run individual linters
   - Check $ref resolutions
   - Validate schema syntax

4. **Build Dependency Issues**
   ```bash
   make install
   npm ci
   ```

### Debug Commands
```bash
make print-vars              # Show Makefile variables
make print-openapi-vars      # OpenAPI-specific vars
make postman-apis            # List workspace APIs
make check-mock              # Verify mock URLs
```

## Security Considerations

1. **API Keys**: Never commit to repository
2. **Secrets Management**: Use GitHub Secrets for CI
3. **Token Handling**: JWT tokens expire appropriately
4. **Mock Data**: No sensitive data in examples
5. **Access Control**: Workspace-based isolation

## Future Enhancements

1. **Incremental Builds**: Only rebuild changed components
2. **Parallel Processing**: Speed up SDK generation
3. **Cache Optimization**: Better dependency caching
4. **Test Coverage**: Expand automated testing
5. **Performance Metrics**: Build time tracking
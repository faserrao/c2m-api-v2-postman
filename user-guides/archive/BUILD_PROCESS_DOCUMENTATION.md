# C2M API v2 Build Process Documentation

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
11. [Security and Secrets](#security-and-secrets)
12. [Troubleshooting](#troubleshooting)

## Overview

The C2M API v2 build system transforms an EBNF data dictionary into a complete API ecosystem including OpenAPI specifications, Postman collections, mock servers, documentation, and SDKs for multiple programming languages.

### Key Components:
- **Input**: EBNF data dictionary (`ebnf/c2m_api_v2_dd.txt`)
- **Primary Output**: OpenAPI 3.0 specification
- **Secondary Outputs**: Postman collections, documentation, SDKs, mock servers
- **Orchestration**: GNU Make with 600+ lines of targets
- **CI/CD**: GitHub Actions workflows

## Architecture Flow

```
EBNF Data Dictionary
     ↓
Python Parser (Lark)
     ↓
Initial OpenAPI Spec
     ↓
Overlay Merge (Authentication)
     ↓
Final OpenAPI Spec
     ↓
   ╱ │ ╲
  ╱  │  ╲
 ╱   │   ╲
Postman  Docs  SDKs
Collection │    (11 langs)
    │      │
Mock Server│
    │      │
  Tests  Redocly
```

## Build Environment

### Directory Structure
```
c2m-api-repo/
├── .github/workflows/     # GitHub Actions workflows
├── ebnf/                  # EBNF data dictionary
├── openapi/               # OpenAPI specifications
│   ├── paths/            # Path definitions
│   ├── schemas/          # Schema definitions
│   └── overlays/         # Authentication overlays
├── postman/              # Postman collections
├── scripts/              # Build scripts
├── docs/                 # Documentation
├── dist/                 # Build outputs
├── tests/                # Test suites
└── Makefile              # Build orchestration
```

### Environment Variables

#### Required for Postman Operations:
- `POSTMAN_API_KEY`: API key for Postman
- `POSTMAN_WORKSPACE_ID`: Target workspace (Private or Team)
- `POSTMAN_COLLECTION_UID`: Collection identifier
- `POSTMAN_MOCK_SERVER_ID`: Mock server ID

#### Optional:
- `CI`: Set to "true" in GitHub Actions
- `POSTMAN_INSTANCE_TYPE`: "private" or "team" (default: "private")

### Key Configuration Files
1. `config.mk` - Make variables and paths
2. `package.json` - Node.js dependencies
3. `.spectral.json` - OpenAPI linting rules
4. `redocly.yaml` - Documentation configuration
5. `openapitools.json` - SDK generator config

## Local Build Process

### Phase 1: EBNF to OpenAPI Conversion

**Command**: `make ebnf-yaml-convert`

**Process**:
1. Reads `ebnf/c2m_api_v2_dd.txt`
2. Executes `scripts/c2mapiv2_dd_data_obj_convert_ebnf_dd_to_yaml_w_lark.py`
3. Uses Lark parser to transform EBNF grammar
4. Generates `openapi/schemas/c2mapiv2_schemas_only_from_dd.yaml`

**Dependencies**:
- Python 3.x
- Lark parser library
- PyYAML

### Phase 2: OpenAPI Assembly

**Command**: `make openapi-build`

**Process**:
1. Combines schemas with paths
2. Adds API metadata (title, version, servers)
3. Creates `openapi/c2mapiv2-openapi-spec-draft.yaml`

**Files Used**:
- `openapi/schemas/*.yaml`
- `openapi/paths/*.yaml`
- `openapi/info.yaml`

### Phase 3: Authentication Overlay

**Command**: `make openapi-merge-auth-overlay`

**Process**:
1. Reads draft OpenAPI spec
2. Applies `openapi/overlays/add-auth-overlay.yaml`
3. Adds Bearer authentication to all endpoints
4. Outputs `openapi/c2mapiv2-openapi-spec-with-auth.yaml`

**Tool**: `redocly bundle` with overlay support

### Phase 4: Validation

**Command**: `make openapi-validate`

**Validators**:
1. **Redocly**: `redocly lint`
   - Uses `.redocly.yaml` configuration
   - Checks for OpenAPI best practices
   
2. **Spectral**: `spectral lint`
   - Uses `.spectral.json` ruleset
   - Additional custom rules

3. **OpenAPI Generator**: `openapi-generator-cli validate`
   - Ensures spec can generate SDKs

### Phase 5: Postman Integration

**Command**: `make postman-build`

**Sub-processes**:

1. **Create/Update Collection**:
   ```bash
   make postman-instance-create-or-update
   ```
   - Converts OpenAPI to Postman format
   - Uploads to Postman cloud
   - Updates with authentication scripts

2. **Mock Server Setup**:
   ```bash
   make postman-mock-server-create
   ```
   - Creates mock server from collection
   - Configures example responses

3. **Test Configuration**:
   ```bash
   make postman-instance-build-and-test
   ```
   - Runs Newman tests
   - Validates all endpoints

### Phase 6: Documentation Generation

**Command**: `make docs-build`

**Process**:
1. Uses Redocly CLI
2. Applies custom template: `docs/custom-redoc-template.hbs`
3. Generates `docs/index.html`
4. Includes custom banner via JavaScript injection

**Template Features**:
- Custom CSS styling
- "Start with Template Endpoints!" banner
- JavaScript for dynamic content
- Analytics integration

### Phase 7: SDK Generation

**Command**: `make sdks-generate`

**Languages Generated**:
1. Python
2. JavaScript
3. TypeScript
4. Java
5. C#
6. Go
7. Ruby
8. PHP
9. Swift
10. Kotlin
11. Rust

**Process**:
- Uses `openapi-generator-cli`
- Config in `openapitools.json`
- Outputs to `dist/sdks/[language]/`

## GitHub Actions CI/CD

### Main Workflow: `api-ci-cd.yml`

**Trigger**: Push to `main` branch

**Jobs**:

1. **Setup**:
   - Checkout code (including security repo)
   - Setup Node.js and Python
   - Install dependencies

2. **Build**:
   ```yaml
   - make ci-ebnf-yaml-convert
   - make ci-openapi-build-and-validate
   - make ci-postman-instance-build-and-update
   - make ci-postman-instance-build-and-test
   - make ci-docs-build
   ```

3. **Deploy**:
   - Commits generated files
   - Pushes to repository

**Key Differences from Local**:
- Uses `ci-` prefixed targets
- Skips local-only operations (Prism server)
- Requires secrets for Postman
- Cannot run interactive tests

### Documentation Workflow: `deploy-docs.yml`

**Purpose**: Build and deploy Redocly docs to GitHub Pages

**Process**:
1. Install Redocly CLI
2. Build docs with custom template:
   ```bash
   redocly build-docs openapi/c2mapiv2-openapi-spec-final.yaml \
     -o docs/index.html \
     -t docs/custom-redoc-template.hbs
   ```
3. Commit and push to trigger Pages deployment

### Supporting Workflows

1. **`lint-openapi.yaml`**: Validates OpenAPI on PRs
2. **`pr-drift-check.yml`**: Ensures PRs are up-to-date
3. **`openapi-ci.yml`**: Additional validation checks

## Configuration Files

### Makefile Structure

**Sections**:
1. **Variables** (lines 1-50): Paths, tools, IDs
2. **Primary Targets** (lines 51-150): Main pipeline
3. **EBNF Operations** (lines 151-200): Parsing logic
4. **OpenAPI Operations** (lines 201-350): Spec building
5. **Postman Operations** (lines 351-500): Collection management
6. **Documentation** (lines 501-550): Docs generation
7. **Utilities** (lines 551-650): Helpers and cleanup

**Key Variables**:
```makefile
OPENAPI_INPUT_DIR        := openapi
POSTMAN_DIR              := postman
DOCS_DIR                 := docs
DIST_DIR                 := dist
C2MAPIV2_OPENAPI_SPEC    := $(OPENAPI_INPUT_DIR)/c2mapiv2-openapi-spec-final.yaml
```

### package.json Dependencies

**Key Packages**:
```json
{
  "@redocly/cli": "^1.5.0",
  "@stoplight/spectral-cli": "^6.11.1",
  "@apidevtools/swagger-cli": "^4.0.4",
  "newman": "^6.1.1",
  "@openapitools/openapi-generator-cli": "^2.13.4"
}
```

**Total**: 40+ dependencies for various build operations

### Custom Redoc Template

**File**: `docs/custom-redoc-template.hbs`

**Features**:
1. Custom CSS for branding
2. JavaScript banner injection
3. Analytics tracking
4. Responsive design
5. Search functionality

**Banner Code**:
```javascript
const banner = document.createElement('div');
banner.className = 'custom-banner';
banner.innerHTML = `
  <div class="banner-content">
    <h2>🚀 Start with Template Endpoints!</h2>
    <p>Simplify your integration with pre-configured job templates</p>
    <div class="banner-links">
      <a href="#tag/templates">Explore Templates</a>
      <a href="/quickstart">Quick Start Guide</a>
    </div>
  </div>
`;
```

## Build Tools and Dependencies

### System Requirements

**Required Software**:
- GNU Make 4.0+
- Python 3.8+
- Node.js 18+
- Git
- curl
- jq

### Python Dependencies

```
lark==1.1.9
PyYAML==6.0.1
jsonschema==4.20.0
requests==2.31.0
```

### Node.js Dependencies

**Build Tools**:
- `@redocly/cli`: OpenAPI bundling and docs
- `@stoplight/spectral-cli`: Linting
- `newman`: API testing
- `@openapitools/openapi-generator-cli`: SDK generation

**Utilities**:
- `json-dereference`: Resolves $ref pointers
- `glob-parent`: File system operations
- `marked`: Markdown processing
- `yargs`: CLI argument parsing

### External Services

1. **Postman Cloud**: Collection and mock server hosting
2. **GitHub Pages**: Documentation hosting
3. **npm Registry**: Package management
4. **Docker Hub**: Generator images

## Build Targets and Commands

### Primary Pipeline

```bash
# Complete build
make pipeline

# Components
make ebnf-yaml-convert
make openapi-build
make openapi-validate
make postman-build
make docs-build
make sdks-generate
```

### CI-Specific Targets

```bash
# Used in GitHub Actions
make ci-pipeline
make ci-postman-instance-build-and-test
make ci-docs-build
```

### Utility Targets

```bash
# Development
make dev-server          # Start local API server
make watch              # Watch for changes
make lint               # Run all linters

# Cleanup
make clean              # Remove build artifacts
make clean-all          # Deep clean including node_modules
make reset-postman      # Remove Postman artifacts
```

### Testing Targets

```bash
# Local testing
make test               # Run all tests
make test-openapi       # Validate OpenAPI only
make test-postman       # Run Postman/Newman tests

# Mock servers
make prism-server       # Start Prism mock (local only)
make postman-mock-test  # Test Postman mock
```

## Artifacts Generated

### OpenAPI Specifications

1. `openapi/schemas/c2mapiv2_schemas_only_from_dd.yaml` - Generated schemas
2. `openapi/c2mapiv2-openapi-spec-draft.yaml` - Initial spec
3. `openapi/c2mapiv2-openapi-spec-with-auth.yaml` - With authentication
4. `openapi/c2mapiv2-openapi-spec-final.yaml` - Production ready

### Postman Artifacts

1. `postman/C2M-API-V2.postman_collection.json` - Collection file
2. `postman/generated-from-openapi-*.json` - Intermediate files
3. `postman/mock-server-config.json` - Mock configuration
4. `postman/test-results/` - Newman test reports

### Documentation

1. `docs/index.html` - Main documentation
2. `docs/assets/` - CSS, JS, images
3. `docs/search-index.json` - Search functionality

### SDKs

Directory structure:
```
dist/sdks/
├── python/
├── javascript/
├── typescript/
├── java/
├── csharp/
├── go/
├── ruby/
├── php/
├── swift/
├── kotlin/
└── rust/
```

Each contains:
- Source code
- README
- Examples
- Tests
- Package configuration

### Logs and Reports

1. `dist/validation-report.json` - OpenAPI validation
2. `postman/test-results/*.xml` - JUnit format test results
3. `logs/build.log` - Build process logs

## Key Differences: Local vs GitHub

### 1. Environment Detection

**Local**:
```makefile
ifdef CI
    @echo "Running in CI environment"
else
    @echo "Running locally"
endif
```

**GitHub**: Sets `CI=true` automatically

### 2. Secret Management

**Local**:
- Uses `.env` file
- Manual export of variables
- Can use personal API keys

**GitHub**:
- Uses repository secrets
- Accessed via `${{ secrets.NAME }}`
- Shared team credentials

### 3. Testing Capabilities

**Local**:
- Can run Prism mock server
- Interactive debugging
- Direct API testing

**GitHub**:
- Newman tests only
- No local servers
- Relies on Postman cloud mock

### 4. Build Outputs

**Local**:
- Artifacts stay on machine
- Can inspect intermediate files
- Manual deployment needed

**GitHub**:
- Commits back to repo
- Automatic deployment
- Artifacts in workflow logs

### 5. Authentication

**Local**:
- Personal Postman account
- Local AWS credentials
- Direct token access

**GitHub**:
- Service account for Postman
- IAM roles for AWS
- Secrets for tokens

## Security and Secrets

### Required Secrets (GitHub)

1. `POSTMAN_API_KEY` - Postman authentication
2. `POSTMAN_WORKSPACE_ID` - Target workspace
3. `POSTMAN_COLLECTION_UID` - Collection ID
4. `POSTMAN_MOCK_SERVER_ID` - Mock server
5. `SECURITY_REPO_TOKEN` - Access security repo

### Security Best Practices

1. Never commit `.env` files
2. Use least-privilege API keys
3. Rotate secrets regularly
4. Audit secret usage
5. Use separate keys for CI/CD

### Sensitive Files

**Never commit**:
- `.env`
- `*.pem` or `*.key`
- `credentials.json`
- `aws-config`

**Use `.gitignore`**:
```
.env
.env.*
*.pem
*.key
credentials/
secrets/
```

## Troubleshooting

### Common Issues

1. **EBNF Parse Errors**:
   - Check EBNF syntax
   - Validate with `make ebnf-validate`
   - Review parser logs

2. **OpenAPI Validation Fails**:
   - Run individual validators
   - Check for schema conflicts
   - Validate JSON syntax

3. **Postman Sync Issues**:
   - Verify API key
   - Check workspace permissions
   - Ensure collection exists

4. **Documentation Build Fails**:
   - Verify template file exists
   - Check Redocly version
   - Validate OpenAPI spec first

5. **SDK Generation Errors**:
   - Update generator version
   - Check language-specific configs
   - Validate OpenAPI 3.0 compliance

### Debug Commands

```bash
# Verbose output
make VERBOSE=1 pipeline

# Dry run
make -n target

# Debug specific phase
make DEBUG=1 openapi-build

# Check environment
make check-env
```

### Logs and Debugging

1. **Build Logs**: `logs/build.log`
2. **Validation Reports**: `dist/validation-report.json`
3. **Test Results**: `postman/test-results/`
4. **GitHub Actions**: Check workflow run logs

## Ensuring Build Reproducibility

### Version Pinning

1. **package.json**: Exact versions with lockfile
2. **requirements.txt**: Pinned Python packages
3. **Makefile**: Tool version checks
4. **Docker images**: Tagged versions

### Consistency Checks

```bash
# Verify builds match
make verify-build-consistency

# Compare artifacts
diff local-build/openapi.yaml ci-build/openapi.yaml

# Checksum validation
make checksum-artifacts
```

### Best Practices

1. Always run `make clean` before full builds
2. Use same Node/Python versions as CI
3. Keep dependencies updated together
4. Test changes in both environments
5. Document any platform-specific code

## Conclusion

The C2M API v2 build system provides a complete pipeline from EBNF data dictionary to production-ready API artifacts. By following this documentation, you can:

1. Understand the complete build flow
2. Reproduce builds consistently
3. Troubleshoot issues effectively
4. Extend the system safely
5. Maintain parity between local and CI builds

For questions or improvements, refer to the inline documentation in the Makefile and individual script files.
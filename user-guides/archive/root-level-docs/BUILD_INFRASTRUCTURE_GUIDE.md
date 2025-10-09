# C2M API v2 Build Infrastructure Guide

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Build Pipeline](#build-pipeline)
4. [Makefile Reference](#makefile-reference)
5. [GitHub Actions Workflows](#github-actions-workflows)
6. [Postman Resource Management](#postman-resource-management)
7. [Test Generation and Execution](#test-generation-and-execution)
8. [Documentation Generation](#documentation-generation)
9. [SDK Generation](#sdk-generation)
10. [Environment Differences](#environment-differences)

## Overview

The C2M API v2 build system is a sophisticated pipeline that transforms an EBNF (Extended Backus-Naur Form) data dictionary into a complete API ecosystem. The system is designed to be fully automated, idempotent, and capable of running both locally and in CI/CD environments.

### Core Design Principles

1. **Single Source of Truth**: The EBNF data dictionary defines all data structures
2. **Automated Transformation**: Each stage automatically transforms artifacts from the previous stage
3. **Dynamic Resource Management**: All cloud resources (Postman collections, mock servers) are created and tracked dynamically
4. **Environment Agnostic**: The same build process works locally and in CI/CD
5. **Idempotent Operations**: Running the build multiple times produces consistent results

## System Architecture

### Build Pipeline Flow

```
EBNF Data Dictionary (c2m_api_v2_dd.txt)
         |
         v
    Python Parser (Lark)
         |
         v
    OpenAPI Schema
         |
         v
    Path Definitions (manual)
         |
         v
    Combined OpenAPI Spec
         |
         v
    Authentication Overlay
         |
         v
    Final OpenAPI Spec
         |
    +----+----+----+
    |    |    |    |
    v    v    v    v
Postman Docs SDKs Tests
```

### Key Components

1. **EBNF Parser**: Python script using Lark grammar parser
2. **OpenAPI Builder**: Combines schemas with paths and metadata
3. **Overlay Processor**: Merges authentication requirements
4. **Postman Manager**: Creates and updates collections dynamically
5. **Test Generator**: Injects examples and test scripts
6. **Documentation Builder**: Generates Redocly documentation
7. **SDK Generator**: Creates client libraries for 11 languages

## Build Pipeline

### Stage 1: EBNF to OpenAPI Schema

The build begins with parsing the EBNF data dictionary:

```bash
make ebnf-yaml-convert
```

**Process**:
1. Reads `ebnf/c2m_api_v2_dd.txt`
2. Executes `scripts/c2mapiv2_dd_data_obj_convert_ebnf_dd_to_yaml_w_lark.py`
3. Uses Lark parser with custom grammar rules
4. Extracts JSON comments for endpoint discovery
5. Generates `openapi/schemas/c2mapiv2_schemas_only_from_dd.yaml`

**Key Features**:
- Preserves EBNF structure as OpenAPI schemas
- Maps EBNF types to OpenAPI types
- Extracts endpoint hints from comments

### Stage 2: OpenAPI Assembly

Combines generated schemas with manually defined paths:

```bash
make openapi-build
```

**Components Combined**:
1. Generated schemas from EBNF
2. Path definitions from `openapi/paths/*.yaml`
3. API metadata (title, version, servers)
4. Security schemes

**Output**: `openapi/c2mapiv2-openapi-spec-draft.yaml`

### Stage 3: Authentication Overlay

Applies authentication requirements to all endpoints:

```bash
make openapi-merge-auth-overlay
```

**Process**:
1. Uses Redocly's overlay feature
2. Applies `openapi/overlays/add-auth-overlay.yaml`
3. Adds Bearer authentication to each operation
4. Handles exceptions (auth endpoints themselves)

**Output**: `openapi/c2mapiv2-openapi-spec-final.yaml`

### Stage 4: Postman Collection Generation

Creates or updates Postman collection:

```bash
make postman-build
```

**Sub-processes**:

1. **Convert OpenAPI to Postman**:
   - Uses `openapi2postmanv2` converter
   - Preserves folder structure
   - Maintains request/response examples

2. **Enhance Collection**:
   - Runs `scripts/c2mapiv2_inject_examples_faker.js`
   - Adds Faker.js-generated test data
   - Injects response validation tests
   - Creates pre-request scripts

3. **Upload to Postman**:
   - Uses Postman API
   - Creates new or updates existing collection
   - Tracks collection UID in `postman_collection_uid.txt`

### Stage 5: Mock Server Creation

Establishes mock servers for testing:

```bash
make postman-mock-server-create
```

**Creates Two Mock Servers**:

1. **Postman Cloud Mock**:
   - Hosted on Postman infrastructure
   - Accessible via internet
   - URL saved to `postman_mock_url.txt`

2. **Local Prism Mock** (local only):
   - Runs on localhost:4010
   - Uses Stoplight Prism
   - PID saved to `prism_pid.txt`

### Stage 6: Test Execution

Runs comprehensive test suite:

```bash
make postman-test
```

**Test Types**:

1. **Schema Validation**: Response structure matches OpenAPI
2. **Status Code Checks**: Correct HTTP codes returned
3. **Data Type Validation**: Fields have correct types
4. **Business Logic Tests**: Custom validations

**Execution Methods**:
- **Local**: Uses Newman CLI
- **CI/CD**: Newman with JUnit reporter
- **Results**: Saved to `postman/test-results/`

## Makefile Reference

### Primary Targets

#### `postman-instance-build-and-test`
The main target that orchestrates the complete build:
1. Converts EBNF to OpenAPI
2. Builds final OpenAPI spec
3. Creates/updates Postman collection
4. Generates mock servers
5. Runs tests

#### `pipeline`
Alias for `postman-instance-build-and-test` - runs complete build

#### `ci-pipeline`
CI/CD version that skips local-only operations

### EBNF Operations

#### `ebnf-yaml-convert`
- Parses EBNF data dictionary
- Generates OpenAPI schemas
- Discovers endpoint information

#### `ebnf-clean`
- Removes generated schema files
- Preserves manual path definitions

### OpenAPI Operations

#### `openapi-build`
- Combines schemas and paths
- Adds API metadata
- Creates draft specification

#### `openapi-validate`
- Runs multiple validators:
  - Redocly lint
  - Spectral lint
  - OpenAPI Generator validate

#### `openapi-merge-auth-overlay`
- Applies authentication overlay
- Creates final specification

### Postman Operations

#### `postman-instance-create-or-update`
- Dynamically creates or updates collection
- Handles workspace selection
- Tracks resource UIDs

#### `postman-inject-examples`
- Adds Faker.js test data
- Creates response validators
- Injects helper scripts

#### `postman-mock-server-create`
- Creates cloud mock server
- Configures example responses
- Saves mock URL

#### `postman-test`
- Executes Newman tests
- Generates reports
- Validates endpoints

### Utility Targets

#### `check-env`
- Validates environment setup
- Checks required tools
- Verifies API keys

#### `clean`
- Removes build artifacts
- Preserves source files
- Resets to clean state

#### `clean-all`
- Deep clean including dependencies
- Removes node_modules
- Clears all generated files

### CI-Specific Targets

All CI targets have `ci-` prefix and:
- Skip local-only operations
- Use appropriate reporters
- Handle missing interactive features

## GitHub Actions Workflows

### Main CI/CD Workflow: `api-ci-cd.yml`

**Trigger**: Push to main branch or manual dispatch

**Jobs**:

1. **Setup**:
   ```yaml
   - Checkout main repository
   - Checkout security repository
   - Setup Node.js and Python
   - Install dependencies
   ```

2. **Build**:
   ```yaml
   - Generate OpenAPI from EBNF
   - Build and validate specification
   - Create Postman collection
   - Run API tests
   ```

3. **Deploy**:
   ```yaml
   - Generate documentation
   - Create SDKs
   - Commit artifacts
   - Push to repository
   ```

**Key Features**:
- Uses repository secrets for API keys
- Commits generated files back
- Runs in Ubuntu environment
- Handles multi-repository setup

### Documentation Workflow: `deploy-docs.yml`

**Purpose**: Build and deploy Redocly documentation

**Process**:
1. Install Redocly CLI
2. Build documentation with custom template
3. Commit to docs folder
4. Trigger GitHub Pages deployment

**Custom Template**: Includes banner and styling

### PR Validation Workflow: `pr-drift-check.yml`

**Purpose**: Ensure PR branches are current

**Checks**:
- Detects commits to main during PR review
- Fails if PR is behind main
- Requires rebase/merge

## Postman Resource Management

### Dynamic Resource Creation

The system dynamically manages Postman resources:

1. **Collections**: Created on first run, updated subsequently
2. **Mock Servers**: Created fresh each build
3. **Environments**: Generated from OpenAPI servers
4. **Tests**: Injected based on endpoint analysis

### UID Tracking

Resource identifiers are saved to files:
- `postman_collection_uid.txt`: Main collection ID
- `postman_mock_url.txt`: Mock server endpoint
- `postman_env_uid.txt`: Environment ID

These files are:
- Generated during build
- Committed to repository
- Used for subsequent updates

### Workspace Management

Supports multiple workspaces:
```makefile
POSTMAN_WORKSPACE_ID = $(if $(filter team,$(POSTMAN_INSTANCE_TYPE)),$(TEAM_WORKSPACE_ID),$(PERSONAL_WORKSPACE_ID))
```

## Test Generation and Execution

### Test Data Generation

The `inject_examples_faker.js` script:

1. **Analyzes Each Endpoint**:
   - Reads request/response schemas
   - Identifies data types
   - Generates appropriate fake data

2. **Creates Examples**:
   ```javascript
   requestBody: {
     name: faker.person.fullName(),
     email: faker.internet.email(),
     phone: faker.phone.number()
   }
   ```

3. **Adds Validation Tests**:
   ```javascript
   pm.test("Status code is 200", () => {
     pm.response.to.have.status(200);
   });
   
   pm.test("Response has required fields", () => {
     const json = pm.response.json();
     pm.expect(json).to.have.property('id');
   });
   ```

### Pre-request Scripts

Automatically injected for:
- Authentication token management
- Dynamic variable substitution
- Request ID generation
- Timestamp handling

### Test Execution

**Local Testing**:
```bash
newman run collection.json \
  --environment postman/environments/local.json \
  --reporters cli,json
```

**CI/CD Testing**:
```bash
newman run collection.json \
  --environment postman/environments/ci.json \
  --reporters cli,junit \
  --reporter-junit-export results.xml
```

## Documentation Generation

### Redocly Documentation

**Process**:
```bash
make docs-build
```

**Steps**:
1. Uses `@redocly/cli`
2. Applies custom template (`docs/custom-redoc-template.hbs`)
3. Generates static HTML
4. Includes:
   - Interactive API explorer
   - Code samples
   - Authentication guide
   - Custom banner

### Custom Template Features

The template adds:
- Marketing banner for template endpoints
- Custom CSS styling
- Analytics integration
- Search functionality
- Responsive design

## SDK Generation

### Supported Languages

The system generates SDKs for:
1. Python
2. JavaScript/TypeScript
3. Java
4. C#
5. Go
6. Ruby
7. PHP
8. Swift
9. Kotlin
10. Rust

### Generation Process

```bash
make sdks-generate
```

**For Each Language**:
1. Uses OpenAPI Generator
2. Applies language-specific config
3. Generates to `dist/sdks/[language]/`
4. Includes:
   - Client library code
   - Documentation
   - Examples
   - Tests

### Configuration

Defined in `openapitools.json`:
```json
{
  "generator-cli": {
    "version": "7.0.1",
    "generators": {
      "python": {
        "generatorName": "python",
        "output": "dist/sdks/python",
        "additionalProperties": {
          "packageName": "c2m_api_client"
        }
      }
    }
  }
}
```

## Environment Differences

### Local Development

**Characteristics**:
- Full access to file system
- Can run local servers (Prism)
- Interactive debugging available
- Personal Postman workspace
- Direct tool execution

**Additional Capabilities**:
- Hot reload with `make watch`
- Verbose logging options
- Step-by-step execution
- Local mock server

### CI/CD Environment

**Characteristics**:
- Ubuntu runner environment
- Secrets from GitHub
- No interactive features
- Team Postman workspace
- Automated commits

**Limitations**:
- No local servers
- No interactive prompts
- Limited debugging output
- Requires all secrets configured

### Key Differences

| Feature | Local | CI/CD |
|---------|-------|-------|
| Prism Mock | ✓ | ✗ |
| Interactive Debug | ✓ | ✗ |
| Auto-commit | ✗ | ✓ |
| Secret Management | .env | GitHub Secrets |
| Workspace | Personal | Team |
| Error Display | Verbose | Summary |

## Advanced Features

### Incremental Builds

The Makefile uses timestamp comparisons:
```makefile
$(OUTPUT): $(INPUT)
	@if [ $(INPUT) -nt $(OUTPUT) ]; then \
		echo "Rebuilding..."; \
		$(BUILD_COMMAND); \
	fi
```

### Parallel Execution

Supports parallel builds:
```bash
make -j4 all-targets
```

### Error Recovery

Graceful handling of failures:
- Cleans partial outputs
- Logs errors to files
- Returns meaningful exit codes

### Debugging

Enable verbose output:
```bash
make VERBOSE=1 target
DEBUG=1 make target
```

## Best Practices

1. **Always Run Clean Build**: `make clean && make pipeline`
2. **Check Environment First**: `make check-env`
3. **Use CI Targets in CI**: `make ci-pipeline`
4. **Commit Generated Files**: Required for CI continuity
5. **Monitor UID Files**: Track resource creation

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   - Run `npm install`
   - Check Python packages

2. **API Key Problems**:
   - Verify in `.env` (local)
   - Check GitHub secrets (CI)

3. **Build Failures**:
   - Check logs in `dist/`
   - Validate OpenAPI first
   - Ensure clean state

4. **Test Failures**:
   - Review Newman output
   - Check mock server status
   - Validate test data

### Debug Commands

```bash
# Verbose Makefile execution
make -d target

# Dry run (show commands)
make -n target

# Force rebuild
make -B target

# Check specific stage
make openapi-validate
```

## Conclusion

The C2M API v2 build infrastructure provides a complete, automated pipeline from data definition to deployed API. By understanding how each component works and how they integrate, developers can effectively use, modify, and extend the system for their own projects. The key is recognizing that all resources are dynamically managed - the system creates what it needs when it needs it, tracking everything through UID files for subsequent operations.
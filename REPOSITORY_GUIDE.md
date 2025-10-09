# c2m-api-repo - Complete Repository Guide

**Repository**: c2m-api-repo (Main Source Repository)
**Purpose**: Single source of truth for C2M API V2 definitions, build processes, and orchestration
**Last Updated**: 2025-10-08

---

## 📖 Cliff Notes - Quick Reference

**If you need to...**

| Task | Command | Location |
|------|---------|----------|
| **Run complete build** | `make postman-instance-build-and-test` | Root |
| **Generate OpenAPI from EBNF** | `make generate-openapi-spec-from-ebnf-dd` | Root |
| **Test with local mock** | `make prism-start && make prism-mock-test` | Root |
| **Publish to Postman** | `make postman-publish` | Root |
| **Clean everything** | `make postman-cleanup-all` | Root |
| **View all commands** | `make help` | Root |
| **Edit API definitions** | Edit `data_dictionary/c2mapiv2-dd.ebnf` | data_dictionary/ |
| **Add custom tests** | Edit `postman/custom/overrides.json` | postman/custom/ |
| **View documentation** | Open `docs/index.html` or visit GitHub Pages | docs/ |

**Key Files**:
- `data_dictionary/c2mapiv2-dd.ebnf` - **Source of truth** for all API definitions
- `Makefile` - Build orchestration (~3000 lines)
- `openapi/c2mapiv2-openapi-spec-final.yaml` - Generated OpenAPI spec
- `.postman-target` - Controls which Postman workspace to publish to

**Core Pipeline**: `EBNF → OpenAPI → Postman → Mock → Tests → Docs`

**Related Repositories**:
- `c2m-api-artifacts` - Generated artifacts (auto-populated by CI/CD)
- `c2m-api-v2-security` - Authentication service (JWT tokens)
- `click2endpoint-aws` - Developer wizard tool

**Common Issues**:
- OpenAPI not updating? Run `make generate-openapi-spec-from-ebnf-dd`
- Postman errors? Check `.env` file has correct API keys
- Tests failing? Ensure mock server running: `make prism-start`
- CI/CD failing? Verify GitHub secrets configured

---

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Architecture & Design](#architecture--design)
3. [Directory Structure](#directory-structure)
4. [Build System](#build-system)
5. [Pipeline Stages](#pipeline-stages)
6. [Makefile Reference](#makefile-reference)
7. [EBNF Data Dictionary](#ebnf-data-dictionary)
8. [OpenAPI Specification](#openapi-specification)
9. [Postman Integration](#postman-integration)
10. [Testing](#testing)
11. [Documentation](#documentation)
12. [CI/CD & GitHub Actions](#cicd--github-actions)
13. [Local Development](#local-development)
14. [Troubleshooting](#troubleshooting)
15. [Best Practices](#best-practices)

---

## Repository Overview

### Purpose

The **c2m-api-repo** is the main source repository for the C2M API V2 project. It contains:
- **No generated artifacts** (those go to c2m-api-artifacts)
- **Only source files**: EBNF, scripts, configurations, overlays
- **Build orchestration**: Makefile and CI/CD workflows
- **Documentation**: User guides and technical docs

### What This Repo DOES NOT Contain

After the two-repo migration (completed 2025-09-18):
- ❌ Generated OpenAPI specifications (in artifacts repo)
- ❌ Generated Postman collections (in artifacts repo)
- ❌ Built documentation (in artifacts repo)
- ❌ Generated SDKs (in artifacts repo)

These are all **generated** and stored in `c2m-api-artifacts`.

### Repository Status

✅ **Production Ready**
- All 24 tests passing
- CI/CD fully automated
- Documentation complete
- Two-repo architecture implemented

### Key Characteristics

**Data-Driven**: EBNF data dictionary is single source of truth
**API-First**: Mock servers enable development before implementation
**Fully Automated**: Complete pipeline from EBNF to deployed API
**Security Isolated**: Authentication in separate repository
**CI/CD Native**: GitHub Actions workflows for all automation

---

## Architecture & Design

### Core Design Principles

#### 1. Single Source of Truth
**The EBNF data dictionary defines everything**:
- All data structures
- All endpoints
- Request/response schemas
- Validation rules

**Why**: Prevents drift between documentation and implementation.

#### 2. Data-Driven Pipeline
**Linear transformation flow**:
```
EBNF Data Dictionary
    ↓ (Python script)
OpenAPI Base Specification
    ↓ (Overlay merge)
OpenAPI Final Specification
    ↓ (openapi-to-postmanv2)
Postman Collections
    ↓ (Test enhancement)
Test Collections + Mock Servers
    ↓ (Newman/Prism)
Test Results + Documentation
```

**Why**: Each stage validates previous stage, catches errors early.

#### 3. API-First Development
**Mock servers created before implementation**:
- Local Prism mock (port 4010)
- Postman cloud mock (public URL)
- Test collections validate contract

**Why**: Enables parallel frontend/backend development.

#### 4. Separation of Concerns

**Source vs Artifacts**:
- Source repo: Human-authored files only
- Artifacts repo: Machine-generated files only

**Main API vs Security**:
- Main repo: API definitions and orchestration
- Security repo: Authentication infrastructure

**Why**: Prevents git conflicts, enables independent deployment.

#### 5. Automation-First

**Everything automated**:
- EBNF → OpenAPI conversion
- Test data generation
- Collection enhancement
- Documentation building
- Deployment to cloud

**Why**: Consistency, repeatability, reduced errors.

### Architecture Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       c2m-api-repo                              │
│  (Source Files Only - No Generated Artifacts)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ GitHub Actions CI/CD
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      BUILD PIPELINE                             │
│                                                                 │
│  [1] EBNF Parsing → Python Script                              │
│  [2] OpenAPI Generation → YAML Output                          │
│  [3] Overlay Merge → Auth + Customizations                     │
│  [4] Collection Generation → Postman JSON                      │
│  [5] Test Enhancement → Faker.js Data                          │
│  [6] Mock Creation → Prism + Postman Cloud                     │
│  [7] Documentation → Redoc + Swagger UI                        │
│  [8] SDK Generation → 12 Languages                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Auto-commit & Push
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    c2m-api-artifacts                            │
│  (Generated Files - Updated Every Build)                        │
│                                                                 │
│  • OpenAPI specs (base, final, bundled)                        │
│  • Postman collections (7 variants)                            │
│  • Documentation (GitHub Pages)                                │
│  • SDKs (Python, JS, Java, Go, etc.)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ├──→ GitHub Pages Deployment
                              └──→ Postman Workspace Updates
```

### Two-Repository Pattern

**Why separate source and artifacts?**

**Before (Single Repo Problems)**:
- Git conflicts between CI/CD and developers
- Large repo with generated files
- Unclear what's human vs machine authored
- Every build = massive commit with 100s of file changes

**After (Two Repo Benefits)**:
- No git conflicts (CI is only writer to artifacts)
- Small source repo (~5MB)
- Clear ownership boundaries
- Atomic artifact updates

**How they integrate**:
1. Developer pushes to c2m-api-repo
2. GitHub Actions runs build pipeline
3. Artifacts copied to c2m-api-artifacts
4. Single commit with all generated files
5. GitHub Pages auto-deploys documentation

---

## Directory Structure

```
c2m-api-repo/
├── .github/
│   └── workflows/              # GitHub Actions CI/CD
│       ├── api-ci-cd.yml      # Main build pipeline
│       ├── pr-drift-check.yml # Validates generated files committed
│       └── deploy-docs.yml    # Documentation deployment
│
├── data_dictionary/
│   ├── c2mapiv2-dd.ebnf       # ⭐ SOURCE OF TRUTH - All API definitions
│   └── examples/              # Example request/response data
│
├── openapi/
│   └── overlays/              # Human-authored customizations
│       └── auth.tokens.yaml   # Authentication endpoints overlay
│
├── postman/
│   ├── custom/                # Custom test overrides
│   │   └── overrides.json    # Merge into generated collections
│   └── scripts/               # Pre-request/test scripts
│       └── jwt-pre-request.js # JWT authentication handler
│
├── scripts/
│   ├── active/                # Current production scripts
│   │   ├── ebnf_to_openapi_class_based.py  # Core converter
│   │   ├── add_tests.js                     # Test injection
│   │   ├── fix_collection_urls_v2.py        # URL normalization
│   │   └── generate_use_case_collection_v2.py  # Use case examples
│   ├── utilities/             # Helper scripts
│   └── archived/              # Legacy scripts (reference only)
│
├── user-guides/               # Documentation (this guide lives here)
│   ├── getting-started/
│   ├── architecture/
│   ├── authentication/
│   ├── development/
│   ├── testing/
│   └── project-reports/
│
├── Makefile                   # ⭐ BUILD ORCHESTRATOR (~3000 lines)
├── .env                       # Local environment (API keys)
├── .postman-target            # Workspace selector (personal/team)
├── package.json               # Node.js dependencies
└── README.md                  # Repository overview
```

### Key Directories Explained

#### data_dictionary/
**Purpose**: Single source of truth for all API definitions
**Format**: EBNF (Extended Backus-Naur Form)
**Files**:
- `c2mapiv2-dd.ebnf` - Complete API definition (2000+ lines)
- `examples/` - Sample request/response payloads

**Why EBNF?**
- Formal, unambiguous syntax
- Easier to write than OpenAPI YAML
- Supports complex type definitions
- Can include endpoint hints in comments

#### scripts/active/
**Purpose**: Production conversion and enhancement scripts
**Key Scripts**:
- **ebnf_to_openapi_class_based.py** (1200 lines)
  - Parses EBNF using Lark grammar
  - Generates OpenAPI 3.0.3 schemas
  - Discovers endpoints from comments
  - Handles complex type resolution
- **add_tests.js** (800 lines)
  - Injects Postman test scripts
  - Adds status code validations
  - Creates response time checks
- **fix_collection_urls_v2.py** (400 lines)
  - Normalizes URLs to use `{{baseUrl}}`
  - Fixes endpoint references
  - Validates request structures

#### postman/
**Purpose**: Postman-specific customizations
**Structure**:
- `custom/` - Human-authored overrides
- `scripts/` - Pre-request and test scripts
- *(generated files go to artifacts repo)*

**Key Files**:
- `custom/overrides.json` - Merge into collections
- `scripts/jwt-pre-request.js` - Auto-authentication

#### user-guides/
**Purpose**: Comprehensive documentation
**Organization**:
- By audience (getting-started, development)
- By topic (architecture, testing, authentication)
- By type (guides, reports, references)

---

## Build System

### Makefile: The Orchestrator

The Makefile is the central command interface (~3000 lines).

**Design Philosophy**:
- **Modularity**: Each target does one thing
- **Composability**: Complex targets call simpler ones
- **Idempotency**: Safe to run multiple times
- **Error Handling**: Fail fast with clear messages

**Structure**:
```makefile
# [Lines 1-100] Environment configuration
# [Lines 101-300] Variable definitions
# [Lines 301-500] Helper functions
# [Lines 501-1500] Primary targets
# [Lines 1501-2500] Logic targets
# [Lines 2501-3000] Utility and CI/CD targets
```

### Target Categories

#### Primary Targets (User-Facing)

**Most Common**:
```bash
make postman-instance-build-and-test  # Complete pipeline with testing
make postman-instance-build-only      # Build without local testing (CI)
make postman-cleanup-all              # Clean all Postman resources
make prism-mock-test                  # Test against local mock
```

**Publishing**:
```bash
make postman-publish                  # Publish to workspace in .postman-target
make postman-publish-personal         # Explicitly publish to personal
make postman-publish-team            # Explicitly publish to team
```

#### Orchestration Targets

These coordinate multiple logic targets:

```bash
make rebuild-all-with-delete          # Full rebuild (cleanup first)
make rebuild-all-no-delete            # Full rebuild (keep existing)
make smart-rebuild                    # Only rebuild what changed
```

#### Logic Targets

Low-level targets for specific operations:

```bash
make generate-openapi-spec-from-ebnf-dd   # EBNF → OpenAPI
make openapi-spec-lint                    # Validate OpenAPI
make postman-create-linked-collection     # Generate linked collection
make postman-create-mock-and-env          # Create mock server
```

### Environment Variables

**Required in `.env`**:
```bash
POSTMAN_SERRAO_API_KEY=your-personal-key
POSTMAN_C2M_API_KEY=your-team-key
```

**Optional**:
```bash
V=1                 # Verbose output
DEBUG=1             # Debug mode
POSTMAN_TARGET=team # Override .postman-target file
```

### Workspace Management

**Two workspaces supported**:
- **Personal (Serrao)**: Development and testing
- **Team (C2M)**: Production and collaboration

**Controlled by**: `.postman-target` file
```bash
# Set target
echo "personal" > .postman-target
# Or
echo "team" > .postman-target
```

CI/CD reads this file to determine publish destination.

---

## Pipeline Stages

### Stage 1: EBNF to OpenAPI Conversion

**Target**: `generate-openapi-spec-from-ebnf-dd`
**Script**: `scripts/active/ebnf_to_openapi_class_based.py`
**Input**: `data_dictionary/c2mapiv2-dd.ebnf`
**Output**: `openapi/c2mapiv2-openapi-spec-base.yaml` (in artifacts repo)

**Process**:
1. Parse EBNF using Lark grammar
2. Extract endpoint hints from comments `(* POST /jobs/single-doc *)`
3. Generate OpenAPI schemas from EBNF productions
4. Resolve type chains (e.g., `documentId → id → integer`)
5. Add standard responses and metadata
6. Validate generated spec

**Key Features**:
- Fully dynamic (no hardcoded endpoints)
- Supports complex type definitions
- Handles oneOf/anyOf constructs
- Comprehensive error reporting

**Example EBNF → OpenAPI**:
```ebnf
documentId := id ;
id := integer ;

(* POST /jobs/single-doc *)
singleDocJob := {
    documentId: documentId,
    recipientName: string
} ;
```

Becomes:
```yaml
paths:
  /jobs/single-doc:
    post:
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                documentId:
                  type: integer
                recipientName:
                  type: string
```

### Stage 2: OpenAPI Overlay Merging

**Target**: `openapi-merge-overlays`
**Script**: `scripts/active/merge_openapi_overlays.py`
**Inputs**:
- Base spec (from Stage 1)
- `openapi/overlays/auth.tokens.yaml`
**Output**: `openapi/c2mapiv2-openapi-spec-final.yaml`

**Process**:
1. Load base OpenAPI spec
2. Load overlay files
3. Deep merge preserving structure
4. Add authentication requirements
5. Validate merged spec

**Why Overlays?**
- Separate auth from core API
- Easy to swap authentication providers
- Keeps EBNF focused on business logic

### Stage 3: OpenAPI Validation

**Target**: `openapi-spec-lint`
**Tools**: Spectral, Redocly

**Validations**:
- Schema validity (OpenAPI 3.0.3 compliance)
- Reference resolution ($ref links)
- Security definitions
- Best practices
- Naming conventions

**Example Issues Caught**:
- Duplicate operation IDs
- Missing response schemas
- Invalid $ref paths
- Inconsistent naming

### Stage 4: Postman Collection Generation

**Target**: `postman-api-linked-collection-generate`
**Tool**: `openapi-to-postmanv2`
**Input**: Final OpenAPI spec
**Output**: Postman collection JSON

**Process**:
1. Convert OpenAPI to Postman format
2. Preserve folder structure
3. Add request/response examples
4. Generate variable placeholders

**Two Collection Types**:
- **Linked Collection**: References API definition (stays in sync)
- **Test Collection**: Standalone (for testing)

### Stage 5: Test Collection Enhancement

**Multiple Sequential Targets**:
1. `postman-test-collection-add-examples` - Add Faker.js data
2. `postman-test-collection-merge-overrides` - Merge custom tests
3. `postman-test-collection-add-tests` - Add validation scripts
4. `postman-test-collection-fix-v2` - Fix URLs
5. `postman-test-collection-flatten-rename` - Flatten structure

**Test Data Generation**:
- Uses Faker.js for realistic data
- Context-aware (email, phone, address)
- Referential integrity
- Multiple scenarios

**Test Scripts Added**:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response time is acceptable", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});

pm.test("Response has required fields", function () {
    var json = pm.response.json();
    pm.expect(json).to.have.property('jobId');
});
```

### Stage 6: Mock Server Creation

**Target**: `postman-create-mock-and-env`
**Creates**:
- Postman cloud mock server
- Environment with mock URL
- (Local Prism mock for testing)

**Mock Server Benefits**:
- Test before API implementation
- Consistent responses
- No backend required
- Shareable URL for teams

### Stage 7: Test Execution

**Target**: `postman-mock`
**Tool**: Newman CLI
**Process**:
1. Run collection against mock
2. Validate responses
3. Generate reports
4. Check status codes

**Allowed Status Codes**:
- 200, 201, 204 (success)
- 400, 401, 403, 404 (expected errors)
- 429 (rate limiting)

### Stage 8: Documentation Generation

**Target**: `docs-build`
**Tools**: Redocly, Swagger UI
**Outputs**:
- Interactive API explorer (Redocly)
- Try-it-out interface (Swagger)
- Static HTML
- GitHub Pages deployment

**Documentation Features**:
- Searchable
- Code samples (multiple languages)
- Request/response examples
- Authentication guide

---

## Makefile Reference

### Essential Commands

#### Development Workflow

```bash
# Complete build and test
make postman-instance-build-and-test

# Quick build (no local testing)
make postman-instance-build-only

# Smart rebuild (only changed components)
make smart-rebuild

# Preview what smart-rebuild would do
make smart-rebuild-dry-run
```

#### EBNF & OpenAPI

```bash
# Generate OpenAPI from EBNF
make generate-openapi-spec-from-ebnf-dd

# Merge overlays (auth, etc.)
make openapi-merge-overlays

# Validate OpenAPI spec
make openapi-spec-lint

# Show OpenAPI variables
make print-openapi-vars
```

#### Postman Operations

```bash
# Generate collections
make postman-create-linked-collection
make postman-create-test-collection

# Create mock server
make postman-create-mock-and-env

# Publish to Postman
make postman-publish                # Use .postman-target
make postman-publish-personal       # Force personal
make postman-publish-team          # Force team

# Clean up
make postman-cleanup-all           # Delete ALL resources
make postman-cleanup-mocks         # Just mocks
make postman-cleanup-collections   # Just collections
```

#### Testing

```bash
# Start local mock server
make prism-start                   # Runs on port 4010

# Test against mock
make prism-mock-test

# Test specific endpoint
make prism-test-endpoint PRISM_TEST_ENDPOINT=/jobs/single-doc

# Run Newman tests
make postman-mock
```

#### Documentation

```bash
# Build documentation
make docs-build

# Serve locally
make docs-serve                    # Opens on port 8080
```

#### Utilities

```bash
# Show all targets
make help

# Show variables
make print-vars

# Workspace information
make workspace-info

# Validate collection
make postman-test-collection-validate
```

### CI/CD-Specific Targets

These targets are optimized for GitHub Actions:

```bash
# CI aliases (skip local operations)
make openapi-build                 # EBNF → OpenAPI
make postman-collection-build      # Generate collections
make docs                         # Build docs
make lint                         # Lint spec
make diff                         # Compare to main

# CI rebuild targets
make rebuild-all-no-delete-ci
make rebuild-all-with-delete-ci
```

### Smart Rebuild System

**Tracks file changes and only rebuilds what's needed**:

```bash
# Check status
make smart-rebuild-status          # Show what would rebuild

# Dry run
make smart-rebuild-dry-run         # Preview changes

# Execute
make smart-rebuild                 # Rebuild changed components

# Force full rebuild
make smart-rebuild-clean           # Clear cache
make smart-rebuild                 # Rebuild everything
```

**How it works**:
1. Stores SHA256 hashes of key files
2. Compares current vs last build
3. Only rebuilds affected stages
4. Shows diffs of changes

---

## EBNF Data Dictionary

### What is EBNF?

**Extended Backus-Naur Form** - A formal notation for defining syntax.

**Why use EBNF instead of writing OpenAPI directly?**
- More concise (2000 lines vs 8000+ in OpenAPI)
- Easier to read and maintain
- Supports complex type definitions
- Can include endpoint metadata in comments
- Less error-prone than YAML

### File Location

`data_dictionary/c2mapiv2-dd.ebnf`

### EBNF Syntax Basics

```ebnf
(* Comment *)
production := definition ;
alternation := option1 | option2 | option3 ;
sequence := part1, part2, part3 ;
optional := [ maybe ] ;
repetition := { many }* ;
```

### Example: Document Source Identifier

```ebnf
(* Document can come from upload, zip, or both *)
documentSourceIdentifier :=
    documentSourceWithUpload |
    documentSourceFromZip |
    documentSourceWithUploadAndZip ;

documentSourceWithUpload := {
    uploadRequestId: uploadRequestId,
    documentName: documentName
} ;

documentSourceFromZip := {
    zipId: zipId,
    documentName: documentName
} ;

documentSourceWithUploadAndZip := {
    uploadRequestId: uploadRequestId,
    zipId: zipId,
    documentName: documentName
} ;
```

### Endpoint Hints

**Endpoints defined in comments**:
```ebnf
(* POST /jobs/single-doc-job-template *)
singleDocJobTemplate := {
    jobTemplate: jobTemplate,
    documentSourceIdentifier: documentSourceIdentifier,
    recipientAddressSource: recipientAddressSource,
    paymentDetails: paymentDetails
} ;
```

The converter extracts:
- Method: POST
- Path: /jobs/single-doc-job-template
- Request body: singleDocJobTemplate schema

### Type Resolution

**EBNF supports type chains**:
```ebnf
documentId := id ;
id := integer ;
```

Converts to:
```yaml
documentId:
  type: integer
```

### Best Practices

1. **Keep productions focused**: One concept per production
2. **Use meaningful names**: `singleDocJob` not `job1`
3. **Document with comments**: Explain business rules
4. **Group related definitions**: Keep related types together
5. **Use consistent naming**: camelCase for all productions

### Common Patterns

**Required Fields**:
```ebnf
job := {
    jobId: jobId,        (* Required *)
    status: status       (* Required *)
} ;
```

**Optional Fields**:
```ebnf
job := {
    jobId: jobId,
    description: [ description ]  (* Optional *)
} ;
```

**Lists/Arrays**:
```ebnf
jobs := { job }* ;  (* Zero or more jobs *)
```

**Enums**:
```ebnf
status := "pending" | "processing" | "completed" | "failed" ;
```

---

## OpenAPI Specification

### Generation Process

**From EBNF to OpenAPI**:
1. Parse EBNF grammar
2. Build type dependency graph
3. Generate schemas from productions
4. Extract endpoint definitions from comments
5. Add standard responses
6. Merge overlays (auth, etc.)
7. Validate final spec

### File Locations

**All in artifacts repo** (generated, not committed here):
- `c2mapiv2-openapi-spec-base.yaml` - From EBNF conversion
- `c2mapiv2-openapi-spec-final.yaml` - With overlays merged
- `c2mapiv2-openapi-spec-final-with-examples.yaml` - With test data

### Overlay System

**Why overlays?**
- Separate concerns (auth vs API logic)
- Easy to swap providers
- Keep EBNF focused on business domain

**Auth Overlay** (`openapi/overlays/auth.tokens.yaml`):
```yaml
paths:
  /auth/tokens/long:
    post:
      summary: Issue long-term token
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LongTokenRequest'
      responses:
        '200':
          description: Token issued
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LongTokenResponse'
```

### OneOf Schema Handling

**Problem**: `openapi-to-postmanv2` simplifies anonymous oneOf to first type only.

**Solution**: Convert anonymous oneOf to named schemas.

**Before**:
```yaml
documentSourceIdentifier:
  oneOf:
    - type: object
      properties:
        uploadRequestId: ...
    - type: object
      properties:
        zipId: ...
```

**After**:
```yaml
documentSourceIdentifier:
  oneOf:
    - $ref: '#/components/schemas/DocumentSourceWithUpload'
    - $ref: '#/components/schemas/DocumentSourceFromZip'
```

**Script**: `scripts/active/fix_openapi_oneOf_schemas.py`

---

## Postman Integration

### Collection Types

#### 1. Linked Collection
- References API definition
- Stays in sync automatically
- Postman schema validation
- Used for development

#### 2. Test Collection
- Standalone (no API reference)
- Includes test scripts
- Has example data
- Used for testing

#### 3. Use Case Collection
- Real-world scenarios
- Pre-filled requests
- Business context
- Used for documentation

### Workspace Strategy

**Two workspaces**:
- **Personal (Serrao)**: Development, experimentation
- **Team (C2M)**: Production, collaboration

**Controlled by**: `.postman-target` file

**Switching workspaces**:
```bash
# Set to personal
echo "personal" > .postman-target
make postman-publish

# Set to team
echo "team" > .postman-target
make postman-publish
```

### JWT Authentication

**Pre-request Script**: `postman/scripts/jwt-pre-request.js`

**Automatically**:
1. Checks for existing token
2. Validates token expiry
3. Refreshes if needed
4. Adds Authorization header

**Configuration**:
```javascript
// In collection variables
pm.collectionVariables.set("authBaseUrl", "https://...");
pm.collectionVariables.set("clientId", "your-client-id");
pm.collectionVariables.set("clientSecret", "your-secret");
```

**Mock Server Detection**:
```javascript
// Skip auth for mock servers
if (pm.request.url.host.includes('mock.pstmn.io')) {
    return; // No auth header
}
```

### Custom Test Overrides

**File**: `postman/custom/overrides.json`

**Format**:
```json
{
  "/jobs/single-doc": {
    "tests": [
      "pm.test('Custom validation', function() { ... });"
    ],
    "preRequest": "// Custom pre-request logic"
  }
}
```

**Applied during**: `postman-test-collection-merge-overrides` target

### Mock Servers

**Two types**:

#### Local (Prism)
- Runs on localhost:4010
- Uses OpenAPI spec
- Fast, local testing
- Command: `make prism-start`

#### Cloud (Postman)
- Public URL
- Based on collection examples
- Shareable with team
- Created by: `postman-create-mock-and-env`

### URL Normalization

**Problem**: Collections have hardcoded URLs

**Solution**: Replace with `{{baseUrl}}` variable

**Script**: `scripts/active/fix_collection_urls_v2.py`

**Before**:
```json
"url": {
  "raw": "https://api.example.com/jobs/single-doc",
  "protocol": "https",
  "host": ["api", "example", "com"],
  "path": ["jobs", "single-doc"]
}
```

**After**:
```json
"url": {
  "raw": "{{baseUrl}}/jobs/single-doc",
  "host": ["{{baseUrl}}"],
  "path": ["jobs", "single-doc"]
}
```

---

## Testing

### Test Strategy

#### Contract Testing
**Validates**: Request/response match OpenAPI spec
**Tool**: Postman JSON schema validation
**Coverage**: 100% of endpoints

#### Integration Testing
**Validates**: Full authentication flow
**Tool**: Newman with environment
**Coverage**: Auth endpoints + protected endpoints

#### Mock Testing
**Validates**: Mock responses match spec
**Tool**: Prism + Newman
**Coverage**: All documented examples

### Test Data Generation

**Script**: `scripts/active/addRandomDataToRaw.js`
**Library**: Faker.js

**Generates**:
- Names, addresses, emails
- Phone numbers
- Dates and timestamps
- UUIDs
- Document names
- Amounts and currencies

**Example**:
```javascript
{
  "recipientName": "John Smith",
  "recipientAddress": {
    "street": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "zip": "62701"
  },
  "amount": "45.99"
}
```

### Test Scripts

**Auto-generated for every request**:
```javascript
// Status code validation
pm.test("Status code is 200 or 201", function () {
    pm.expect(pm.response.code).to.be.oneOf([200, 201]);
});

// Response time check
pm.test("Response time is acceptable", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});

// Schema validation
pm.test("Response matches schema", function () {
    var schema = {...};
    pm.response.to.have.jsonSchema(schema);
});

// Business logic validation
pm.test("JobId is present", function () {
    var json = pm.response.json();
    pm.expect(json).to.have.property('jobId');
    pm.expect(json.jobId).to.be.a('string');
});
```

### Running Tests Locally

```bash
# Start local mock
make prism-start

# Run tests
make prism-mock-test

# Test specific endpoint
make prism-test-endpoint PRISM_TEST_ENDPOINT=/jobs/single-doc

# View results
open postman/test-results/newman-report.html
```

### CI/CD Testing

**GitHub Actions runs**:
```bash
make postman-instance-build-only    # Build
make postman-mock                   # Test against cloud mock
```

**Results**:
- Uploaded as artifacts
- Available in Actions tab
- Fail fast on errors

### Test Configuration

**Allowed status codes** (in Makefile):
```makefile
ALLOWED_CODES := 200,201,204,400,401,403,404,429
```

**Timeouts**:
- Request timeout: 10 seconds
- Response time assertion: 2 seconds

**Retries**:
- Failed requests: 0 (fail fast)
- Network errors: 1 retry

---

## Documentation

### Documentation Types

#### 1. API Documentation (Auto-Generated)
- **Redoc**: Interactive, searchable
- **Swagger UI**: Try-it-out functionality
- **Markdown**: Offline reference

#### 2. User Guides (Human-Authored)
- Getting started guides
- Architecture documentation
- Development guides
- Testing documentation

#### 3. Project Reports
- Accomplishments summaries
- Status reports
- Migration logs

### API Documentation Generation

**Target**: `docs-build`
**Tool**: Redocly CLI
**Input**: Final OpenAPI spec
**Output**: Static HTML

**Features**:
- Three-panel layout
- Search functionality
- Code samples (curl, JavaScript, Python)
- Request/response examples
- Authentication guide
- Downloadable spec

**Deployment**:
```bash
# Build locally
make docs-build

# Serve locally (port 8080)
make docs-serve

# Deploy to GitHub Pages (via CI/CD)
# Automatic on push to main
```

**Live URL**: https://faserrao.github.io/c2m-api-artifacts/

### User Guide Organization

**Structure** (in `user-guides/`):
```
getting-started/      # Quick starts, onboarding
architecture/         # Design docs, PROJECT_MEMORY
authentication/       # Auth guides (links to security repo)
development/          # Dev guides, READMEs
testing/              # Test strategies, data generation
api-reference/        # Template endpoints, guides
project-reports/      # Accomplishments, status
```

**Key Documents**:
- `getting-started/QUICKSTART.md` - 5-minute start
- `architecture/PROJECT_MEMORY.md` - Comprehensive knowledge base
- `development/POSTMAN_COMPLETE_GUIDE.md` - Postman workflows
- This document (`REPOSITORY_GUIDE.md`) - Complete reference

---

## CI/CD & GitHub Actions

### Workflows

#### 1. Main Pipeline (`api-ci-cd.yml`)

**Triggers**:
- Push to main branch
- Pull requests
- Manual dispatch

**Jobs**:
1. **Checkout** - Main + security repos
2. **Setup** - Node.js, Python
3. **Install** - Dependencies
4. **Build** - OpenAPI from EBNF
5. **Generate** - Postman collections
6. **Lint** - Validate spec
7. **Diff** - Compare to main (PRs only)
8. **Docs** - Build documentation
9. **Validate** - Check for uncommitted changes
10. **Publish** - Upload to Postman (main only)
11. **Commit** - Push artifacts to artifacts repo
12. **Deploy** - GitHub Pages

**Duration**: ~5-8 minutes

#### 2. PR Drift Check (`pr-drift-check.yml`)

**Purpose**: Ensure generated files are committed

**Process**:
1. Checkout PR branch
2. Run full build
3. Check for git differences
4. Comment on PR if drift detected
5. Fail PR if changes found

**Why**: Prevents "works on my machine" issues

#### 3. Documentation Deployment (`deploy-docs.yml`)

**Triggers**: Push to main (after artifacts committed)

**Process**:
1. Checkout artifacts repo
2. Configure GitHub Pages
3. Deploy from `docs/` directory

**Result**: Live documentation at GitHub Pages URL

### GitHub Secrets Required

**Configure in repo settings**:
```
POSTMAN_SERRAO_API_KEY     # Personal workspace key
POSTMAN_C2M_API_KEY        # Team workspace key
SECURITY_REPO_TOKEN        # PAT for security repo access
```

### CI/CD vs Local Differences

| Feature | Local | CI/CD |
|---------|-------|-------|
| Prism mock | ✅ Runs | ❌ Skipped |
| Local docs serve | ✅ Available | ❌ Skipped |
| Auto-commit | ❌ Manual | ✅ Automatic |
| Workspace | Personal | From .postman-target |
| Error detail | Verbose | Summary |
| Artifacts | Local files | Uploaded |

### Environment Detection

```makefile
ifdef CI
    # GitHub Actions specific
    SECURITY_DIR := c2m-api-v2-security
else
    # Local development
    SECURITY_DIR := ../c2m-api-v2-security
endif
```

### Artifact Storage

**GitHub Actions artifacts**:
- OpenAPI specifications
- Postman collections
- Test results
- Documentation

**Retention**: 90 days

**Download**: Actions tab → Select run → Artifacts section

---

## Local Development

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/faserrao/c2m-api-repo.git
cd c2m-api-repo

# 2. Install dependencies
npm install
pip install -r scripts/python_env/requirements.txt

# 3. Create .env file
cat > .env << EOF
POSTMAN_SERRAO_API_KEY=your-api-key
POSTMAN_C2M_API_KEY=your-team-key
EOF

# 4. Set workspace target
echo "personal" > .postman-target

# 5. Test the setup
make check-env
```

### Common Development Workflows

#### Workflow 1: Edit API Definition

```bash
# 1. Edit EBNF
vim data_dictionary/c2mapiv2-dd.ebnf

# 2. Generate OpenAPI
make generate-openapi-spec-from-ebnf-dd

# 3. Validate
make openapi-spec-lint

# 4. Build collections
make postman-create-linked-collection
make postman-create-test-collection

# 5. Test locally
make prism-start
make prism-mock-test

# 6. Publish when ready
make postman-publish
```

#### Workflow 2: Add Custom Tests

```bash
# 1. Edit override file
vim postman/custom/overrides.json

# 2. Rebuild test collection
make postman-create-test-collection

# 3. Test
make prism-mock-test
```

#### Workflow 3: Update Documentation

```bash
# 1. Edit user guide
vim user-guides/getting-started/QUICKSTART.md

# 2. Commit changes
git add user-guides/
git commit -m "Update quickstart guide"
git push
```

#### Workflow 4: Full Rebuild

```bash
# Clean everything
make postman-cleanup-all

# Full rebuild with testing
make postman-instance-build-and-test

# Or just build (no local testing)
make postman-instance-build-only
```

### Development Tools

#### Prism Mock Server

```bash
# Start server (port 4010)
make prism-start

# Check status
make prism-status

# Stop server
make prism-stop

# Test endpoint
curl http://localhost:4010/jobs/single-doc
```

#### Newman CLI Testing

```bash
# Run collection
newman run postman/generated/collection.json \
  -e postman/generated/environment.json \
  --reporters cli,html

# With specific options
newman run collection.json \
  --timeout-request 10000 \
  --delay-request 100 \
  --reporters cli,json,html \
  --reporter-html-export results.html
```

### IDE Configuration

#### VS Code

**Recommended extensions**:
- YAML (Red Hat)
- Postman (for collections)
- REST Client
- Makefile Tools

**Settings** (.vscode/settings.json):
```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/schemas/v3.0/schema.json": "openapi/*.yaml"
  },
  "files.associations": {
    "*.ebnf": "plaintext"
  }
}
```

---

## Troubleshooting

### Common Issues

#### Issue: OpenAPI not updating

**Symptoms**: Changes to EBNF not reflected in spec

**Cause**: Cached or not regenerated

**Solution**:
```bash
# Force regeneration
rm -f openapi/c2mapiv2-openapi-spec-base.yaml
make generate-openapi-spec-from-ebnf-dd
```

#### Issue: Postman publish fails

**Symptoms**: 401 or 403 errors

**Cause**: Invalid or expired API key

**Solution**:
```bash
# Check .env file
cat .env

# Verify key is valid
curl -X GET https://api.getpostman.com/me \
  -H "X-Api-Key: YOUR_KEY"

# Update key if needed
vim .env
```

#### Issue: Tests failing

**Symptoms**: Newman reports failures

**Possible Causes**:
1. Mock server not running
2. Wrong environment selected
3. Invalid test data
4. Schema mismatch

**Solutions**:
```bash
# 1. Check mock server
make prism-status

# 2. Restart mock
make prism-stop
make prism-start

# 3. Regenerate test data
make postman-test-collection-add-examples

# 4. Validate collection
make postman-test-collection-validate
```

#### Issue: CI/CD failing

**Symptoms**: GitHub Actions build fails

**Common Causes**:
1. Missing secrets
2. Generated files not committed
3. Lint errors
4. Workspace access denied

**Solutions**:
```bash
# 1. Check secrets (in GitHub settings)
# 2. Commit generated files locally first
make postman-instance-build-only
git add openapi/ postman/
git commit -m "Update generated files"
git push

# 3. Run lint locally
make openapi-spec-lint

# 4. Verify workspace access
make workspace-info
```

#### Issue: Wrong workspace published

**Symptoms**: Changes appear in wrong Postman workspace

**Cause**: `.postman-target` file incorrect

**Solution**:
```bash
# Check current target
cat .postman-target

# Set to personal
echo "personal" > .postman-target

# Or set to team
echo "team" > .postman-target
```

### Debug Commands

```bash
# Show all variables
make print-vars

# Show OpenAPI-specific variables
make print-openapi-vars

# Show workspace info
make workspace-info

# List Postman resources
make postman-apis
make postman-collections
make postman-mocks

# Validate files
make openapi-spec-lint
make postman-test-collection-validate

# Check environment
make check-env
```

### Error Messages

#### "Missing file: data_dictionary/c2mapiv2-dd.ebnf"

**Cause**: EBNF file not found

**Solution**: Ensure you're in repository root
```bash
pwd  # Should end in /c2m-api-repo
ls data_dictionary/c2mapiv2-dd.ebnf  # Should exist
```

#### "POSTMAN_API_KEY not set"

**Cause**: Environment variable not loaded

**Solution**: Create or update `.env` file
```bash
cat > .env << EOF
POSTMAN_SERRAO_API_KEY=your-key
EOF
```

#### "401 Unauthorized from Postman API"

**Cause**: Invalid API key

**Solution**: Generate new key in Postman
1. Go to Postman web app
2. Settings → API Keys
3. Generate API key
4. Update `.env` file

---

## Best Practices

### EBNF Development

1. **Start with simple definitions**
   ```ebnf
   jobId := string ;
   ```

2. **Build up complexity gradually**
   ```ebnf
   job := {
       jobId: jobId,
       status: status
   } ;
   ```

3. **Test frequently**
   ```bash
   make generate-openapi-spec-from-ebnf-dd
   make openapi-spec-lint
   ```

4. **Use meaningful names**
   - ✅ `singleDocJobTemplate`
   - ❌ `job1`, `req`, `payload`

5. **Document complex rules**
   ```ebnf
   (* Template content constraint: address list and document list are mutually exclusive *)
   templateContent := addressListOnly | documentListOnly ;
   ```

### Build System

1. **Use smart rebuild** when possible
   ```bash
   make smart-rebuild  # Faster than full rebuild
   ```

2. **Clean before major changes**
   ```bash
   make postman-cleanup-all
   make rebuild-all-with-delete
   ```

3. **Test locally before pushing**
   ```bash
   make postman-instance-build-and-test
   ```

4. **Commit generated files** (if CI/CD will publish)
   ```bash
   make postman-instance-build-only
   git add openapi/ postman/
   git commit -m "Update API"
   ```

### Postman Integration

1. **Use workspace targets consistently**
   ```bash
   # Development
   echo "personal" > .postman-target

   # Production
   echo "team" > .postman-target
   ```

2. **Keep custom overrides minimal**
   - Only add tests for business logic
   - Let auto-generation handle standard tests

3. **Test mock servers before publishing**
   ```bash
   make prism-start
   make prism-mock-test
   # Only publish if tests pass
   make postman-publish
   ```

### Documentation

1. **Update user guides when changing workflows**

2. **Keep PROJECT_MEMORY.md current**
   - Add lessons learned
   - Document workarounds
   - Update architecture decisions

3. **Use consistent formatting**
   - Markdown for all docs
   - Code blocks with language tags
   - Headings hierarchy (# → ## → ###)

### Git Workflow

1. **Create feature branches**
   ```bash
   git checkout -b feature/add-endpoint
   ```

2. **Commit generated files separately**
   ```bash
   git add data_dictionary/
   git commit -m "Add new endpoint definition"

   make generate-openapi-spec-from-ebnf-dd
   git add openapi/
   git commit -m "Regenerate OpenAPI spec"
   ```

3. **Write descriptive commit messages**
   - ✅ "Add multi-doc-merge endpoint with template support"
   - ❌ "Update files"

### CI/CD

1. **Test PR checks locally first**
   ```bash
   make openapi-build
   make postman-collection-build
   make lint
   ```

2. **Monitor GitHub Actions**
   - Check build status after push
   - Review logs if failures occur

3. **Keep secrets updated**
   - Rotate API keys periodically
   - Update GitHub secrets when keys change

---

## Appendix: Quick Command Reference

### Most Used Commands

```bash
# Complete pipeline
make postman-instance-build-and-test

# EBNF → OpenAPI
make generate-openapi-spec-from-ebnf-dd

# Validate
make openapi-spec-lint

# Start mock
make prism-start

# Test
make prism-mock-test

# Publish
make postman-publish

# Clean
make postman-cleanup-all

# Help
make help
```

### File Locations

```
⭐ SOURCE OF TRUTH
data_dictionary/c2mapiv2-dd.ebnf

📝 OVERLAYS
openapi/overlays/auth.tokens.yaml

🔧 BUILD ORCHESTRATOR
Makefile

⚙️ CONFIGURATION
.env
.postman-target

📚 THIS GUIDE
user-guides/REPOSITORY_GUIDE.md
```

### External Links

- **GitHub Repository**: https://github.com/faserrao/c2m-api-repo
- **Artifacts Repository**: https://github.com/faserrao/c2m-api-artifacts
- **Security Repository**: https://github.com/faserrao/c2m-api-v2-security
- **API Documentation**: https://faserrao.github.io/c2m-api-artifacts/
- **System Architecture**: ../C2M_API_V2_SYSTEM_ARCHITECTURE.md

---

**Document Version**: 1.0
**Last Updated**: 2025-10-08
**Maintained By**: C2M API Development Team

For questions or corrections, please create an issue in the GitHub repository.

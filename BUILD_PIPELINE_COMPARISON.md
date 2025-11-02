# Build Pipeline Comparison: CI/CD vs Local

**Document Version**: 1.0
**Date**: 2025-10-29
**Purpose**: High-level comparison of what gets built/tested in CI/CD vs local development

## Executive Summary

There are **two build pipelines**:

1. **CI/CD Pipeline** (GitHub Actions): Triggered on push to `main` branch
   - Builds everything (OpenAPI, Postman, Docs, SDKs)
   - **DOES NOT run tests** (Prism or Postman)
   - Publishes to Postman workspace
   - Deploys docs to GitHub Pages
   - Copies artifacts to artifacts repository

2. **Local Development Pipeline**: Run manually via `make postman-instance-build-and-test`
   - Builds everything (same as CI/CD)
   - **RUNS TESTS** (Prism local mock + Postman collection tests)
   - Serves docs locally
   - Does not publish/deploy (stays local)

## Detailed Comparison

### CI/CD Pipeline (GitHub Actions)

**Trigger**: Push to `main` branch (or manual workflow dispatch)

**What Runs** (in order):

#### Phase 1: Setup (Lines 66-139)
```
1. Checkout main repository
2. Checkout security repository
3. Checkout artifacts repository
4. Setup Node.js (v20)
5. Setup Python (v3.11)
6. Install dependencies (npm, pip, Postman CLI)
7. Print environment info
```

#### Phase 2: Build (Lines 142-169)
```
8. Build OpenAPI from EBNF
   - Runs: make openapi-build
   - Creates: openapi/c2mapiv2-openapi-spec-base.yaml
   - Creates: openapi/c2mapiv2-openapi-spec-final.yaml

9. Lint OpenAPI Spec
   - Runs: make lint
   - Validates: OpenAPI spec against OpenAPI 3.1.0 spec

10. Diff OpenAPI Spec (PRs only)
    - Runs: make diff
    - Compares: Changes between branches

11. Build Documentation (Redocly)
    - Runs: make docs
    - Creates: docs/index.html
    - Creates: docs/site/** (static site)

12. Generate SDKs
    - Runs: make generate-sdk-all
    - Creates: sdk/python/**
    - Creates: sdk/javascript/**
    - Status: Currently fails (continue-on-error: true)
```

#### Phase 3: Drift Detection (Lines 172-193, PRs only)
```
13. Check for uncommitted changes
    - Verifies: Generated files match committed files
    - Fails PR if: Generated artifacts out of sync
```

#### Phase 4: Postman Publish (Lines 195-234, main only)
```
14. Determine target workspace
    - Reads: .postman-target file
    - Fallback: POSTMAN_TARGET secret or "personal"

15. FULL CLEANUP of Postman workspace
    - Runs: make postman-cleanup-all
    - Deletes: ALL APIs
    - Deletes: ALL Collections
    - Deletes: ALL Mock Servers
    - Deletes: ALL Environments
    - Deletes: ALL Standalone Specs
    - Empties: Trash

16. FULL REBUILD of Postman workspace
    - Runs: make postman-instance-build-only
    - Creates: API Definition (from OpenAPI)
    - Creates: Standalone Spec (in Specs tab)
    - Creates: Linked Collection
    - Creates: Use Case Collection
    - Creates: Test Collection
    - Creates: Mock Server (from Use Case Collection)
    - Creates: 2 Environments (Mock Server + AWS Dev)

WARNING: DOES NOT RUN TESTS
```

#### Phase 5: Artifacts Management (Lines 237-298, main only)
```
17. Copy artifacts to artifacts repository
    - Copies: openapi/*.yaml
    - Copies: postman/generated/*.json
    - Copies: postman/*.txt (UIDs)
    - Copies: postman/*.json (metadata)
    - Copies: docs/**
    - Copies: sdk/** (if exists)

18. Commit and push artifacts
    - Commits: All artifacts with build info
    - Pushes: To click2mail/c2m-api-v2-postman-artifacts
```

#### Phase 6: GitHub Pages Deploy (Lines 308-343, main only)
```
19. Setup Pages
    - Configures: GitHub Pages environment

20. Upload Pages artifact
    - Uploads: docs/** directory

21. Deploy to GitHub Pages
    - Deploys: Redocly documentation
    - URL: https://click2mail.github.io/c2m-api-v2-postman/
```

#### Phase 7: Summary (Lines 346-383)
```
22. Generate workflow summary
    - Shows: Build status
    - Shows: Deployment status
    - Shows: Quick links
```

**What Gets Created in Postman** (via `postman-instance-build-only`):
- API Definition: C2M API V2
- Standalone Spec: C2M API V2 OpenAPI Spec
- Collection: C2mApiV2LinkedCollection
- Collection: C2mApiV2RealWorldUseCases
- Collection: C2mApiV2TestCollection
- Mock Server: (random URL assigned by Postman)
- Environment: Mock Server Environment
- Environment: AWS Dev Environment

**What Does NOT Happen**:
- NO Prism local mock server
- NO Postman collection tests
- NO local documentation serving
- NO oneOf examples extraction

**Total Time**: ~3-5 minutes (depending on Postman API responsiveness)

---

### Local Development Pipeline

**Trigger**: Manual - `make postman-instance-build-and-test`

**What Runs** (in order):

#### Phase 1: Prerequisites (assumed already done)
```
1. EBNF data dictionary updated
2. OpenAPI spec generated
   - Run: make generate-openapi-spec-from-ebnf-dd
   - Creates: openapi/c2mapiv2-openapi-spec-base.yaml
   - Creates: openapi/c2mapiv2-openapi-spec-final.yaml
```

#### Phase 2: Postman Build (Lines 513-526)
```
3. Authenticate with Postman
   - Runs: make postman-login
   - Uses: POSTMAN_API_KEY (from .env)

4. Import OpenAPI as API Definition
   - Runs: make postman-import-openapi-spec
   - Creates: API Definition in Postman workspace

5. Create Standalone Spec
   - Runs: make postman-spec-create-standalone
   - Creates: Standalone spec in Specs tab

6. Create Linked Collection
   - Runs: make postman-create-linked-collection
   - Creates: Collection linked to API Definition

7. Create Test Collection
   - Runs: make postman-create-test-collection
   - Creates: Test collection with automated tests

8. Extract oneOf Examples
   - Runs: make postman-extract-oneof-examples
   - Creates: Examples for all oneOf variants
   - Status: LOCAL ONLY (not in CI/CD)

9. Generate Use Case Collection
   - Runs: make postman-generate-use-case-collection
   - Creates: Real-world use case scenarios

10. Upload All Enhanced Collections
    - Runs: make postman-upload-all-enhanced-collections
    - Uploads: All collections to Postman

11. Create Mock Server and Environments
    - Runs: make postman-create-mock-and-env
    - Creates: Mock Server
    - Creates: Mock Server Environment
    - Creates: AWS Dev Environment
```

#### Phase 3: Local Testing (Lines 527-529)
```
12. Start Prism Local Mock Server
    - Runs: make prism-start
    - Port: 4010
    - Mock: OpenAPI spec via Prism
    - Status: LOCAL ONLY (not in CI/CD)

13. Run Postman Collection Tests
    - Runs: make postman-mock
    - Tests: All collections against Prism mock
    - Validates: Request/response schemas
    - Checks: Authentication flows
    - Status: LOCAL ONLY (not in CI/CD)
```

#### Phase 4: Documentation (Line 531)
```
14. Build and Serve Documentation
    - Runs: make postman-docs-build-and-serve-up
    - Builds: Redocly docs
    - Serves: http://localhost:8080
    - Status: LOCAL ONLY (not in CI/CD)
```

**What Gets Created in Postman** (same as CI/CD):
- API Definition: C2M API V2
- Standalone Spec: C2M API V2 OpenAPI Spec
- Collection: C2mApiV2LinkedCollection
- Collection: C2mApiV2RealWorldUseCases
- Collection: C2mApiV2TestCollection
- Mock Server: (random URL assigned by Postman)
- Environment: Mock Server Environment
- Environment: AWS Dev Environment

**What Also Happens Locally**:
- Prism mock server running (port 4010)
- Postman tests executed and results shown
- Redocly docs served locally (port 8080)
- oneOf examples extracted and included

**What Does NOT Happen**:
- NO artifacts repository push
- NO GitHub Pages deployment
- NO workflow summary

**Total Time**: ~5-8 minutes (including test execution)

---

## Side-by-Side Comparison Table

| Step | CI/CD (GitHub Actions) | Local Development | Notes |
|------|----------------------|-------------------|-------|
| **Setup** | Auto (Node, Python, deps) | Manual (one-time) | Local: requires initial setup |
| **Build OpenAPI** | `make openapi-build` | `make generate-openapi-spec-from-ebnf-dd` | Same result, different target names |
| **Lint OpenAPI** | Yes | Optional | CI always lints |
| **Build Docs** | Yes (Redocly) | Yes (Redocly) | Same output |
| **Generate SDKs** | Yes (fails, ignored) | Optional | Not fully implemented |
| **Postman Cleanup** | FULL cleanup | Manual (if desired) | CI always cleans first |
| **Postman API Definition** | Created | Created | Identical |
| **Postman Standalone Spec** | Created | Created | Identical |
| **Postman Linked Collection** | Created | Created | Identical |
| **Postman Use Case Collection** | Created | Created | Identical |
| **Postman Test Collection** | Created | Created | Identical |
| **Postman Mock Server** | Created | Created | Identical |
| **Postman Environments** | Created (2) | Created (2) | Identical |
| **Extract oneOf Examples** | NO | YES | **LOCAL ONLY** |
| **Prism Mock Server** | NO | YES (port 4010) | **LOCAL ONLY** |
| **Run Postman Tests** | NO | YES | **LOCAL ONLY** |
| **Serve Docs Locally** | NO | YES (port 8080) | **LOCAL ONLY** |
| **Copy to Artifacts Repo** | YES | NO | **CI/CD ONLY** |
| **Deploy GitHub Pages** | YES | NO | **CI/CD ONLY** |

## Key Differences

### 1. Testing

**CI/CD**: **NO TESTS RUN**
- Builds everything
- Publishes to Postman
- Does NOT validate endpoints work
- Does NOT run Prism mock tests
- Does NOT run Postman collection tests

**Local**: **FULL TESTING**
- Builds everything
- Starts Prism mock server (port 4010)
- Runs Postman collection tests against Prism
- Validates request/response schemas
- Reports test results

**Rationale**: CI/CD focuses on deployment speed. Testing happens locally before pushing.

### 2. oneOf Examples

**CI/CD**: **SKIPPED**
- Use Case Collection created without oneOf variants
- Only includes main example per endpoint

**Local**: **INCLUDED**
- Extracts all oneOf examples
- Creates comprehensive test coverage
- More examples = better testing

**Rationale**: oneOf extraction adds time; not needed for deployment.

### 3. Documentation

**CI/CD**: **DEPLOYED TO GITHUB PAGES**
- Builds Redocly docs
- Uploads to GitHub Pages
- Public URL: https://click2mail.github.io/c2m-api-v2-postman/

**Local**: **SERVED LOCALLY**
- Builds Redocly docs
- Serves on http://localhost:8080
- Preview before deploying

**Rationale**: Different audiences (public vs developer preview).

### 4. Artifacts

**CI/CD**: **PUSHED TO ARTIFACTS REPO**
- Copies all generated files
- Commits to c2m-api-v2-postman-artifacts
- Auto-versioned with build number

**Local**: **STAYS LOCAL**
- Generated files stay in local workspace
- No auto-commit
- Manual git operations

**Rationale**: CI/CD maintains audit trail; local is for development.

### 5. oneOf Examples Extraction

**What is oneOf?**

In OpenAPI/JSON Schema, `oneOf` allows a field to accept **one of several different types**. For example:

```yaml
paymentDetails:
  oneOf:
    - $ref: '#/components/schemas/CreditCardPayment'
    - $ref: '#/components/schemas/ACHPayment'
    - $ref: '#/components/schemas/InvoicePayment'
```

This means `paymentDetails` can be:
- Credit card payment (with cardNumber, cvv, expiry)
- OR ACH payment (with routingNumber, accountNumber)
- OR Invoice payment (with invoiceId)

**Only ONE** at a time, but any of the three.

**What Does "Extract oneOf Examples" Mean?**

The `make postman-extract-oneof-examples` target:
1. Scans the OpenAPI spec for all `oneOf` constructs
2. Generates separate examples for each variant
3. Creates multiple Postman requests - one per variant

**Example**: One endpoint `/jobs/submit` becomes:
- `POST /jobs/submit` - Example 1: Credit Card Payment
- `POST /jobs/submit` - Example 2: ACH Payment
- `POST /jobs/submit` - Example 3: Invoice Payment
- `POST /jobs/submit` - Example 4: Single Document
- `POST /jobs/submit` - Example 5: Multiple Documents
- `POST /jobs/submit` - Example 6: Embedded Addresses
- `POST /jobs/submit` - Example 7: External Addresses

**CI/CD**: **SKIPPED**
- Use Case Collection created without oneOf variants
- Only includes main example per endpoint
- Result: ~12 examples total

**Local**: **INCLUDED**
- Extracts all oneOf examples
- Creates comprehensive test coverage
- Result: 100+ examples total
- Time cost: +2-3 minutes

**Why Skip in CI/CD?**

1. **Speed**: oneOf extraction is slow (analyzes entire spec, generates many examples)
2. **Overkill**: Production doesn't need 100 variants tested - just needs valid spec deployed
3. **Mock Server**: Works fine with basic examples
4. **Documentation**: Users see main example, not every possible variant
5. **Testing Happens Locally**: Developers test all variants before pushing

**Real-World Impact**

Without oneOf extraction (CI/CD):
```json
POST /jobs/submit
{
  "paymentDetails": {
    "creditCard": {
      "cardNumber": "4111111111111111",
      "cvv": "123"
    }
  }
}
```
One example. Good enough for deployment.

With oneOf extraction (Local):
- Dozens of examples covering all code paths
- Credit Card, ACH, Invoice variants
- Single doc, multi-doc variants
- Embedded addresses, external addresses variants
- All combinations tested locally

**Rationale**: Exhaustive local testing, efficient CI/CD deployment.

## What Gets Built/Deployed: Complete List

### Generated Files (Both CI/CD and Local)

#### OpenAPI Specs
```
openapi/c2mapiv2-openapi-spec-base.yaml         (30KB) - Generated from EBNF
openapi/c2mapiv2-openapi-spec-final.yaml        (30KB) - Copy of base
openapi/c2mapiv2-openapi-spec-final-with-examples.yaml (64KB) - With code examples
```

#### Postman Collections
```
postman/generated/C2mApiV2LinkedCollection.json          - Linked to API Definition
postman/generated/C2mApiV2RealWorldUseCases.json         - Real-world scenarios
postman/generated/C2mApiV2TestCollection.json            - Automated tests
```

#### Postman Metadata Files
```
postman/api-uid.txt                    - API Definition UID
postman/test_collection_uid.txt        - Test Collection UID
postman/use_case_collection_uid.txt    - Use Case Collection UID
postman/native-flat-collection-uid.txt - Linked Collection UID
postman/mock_server_uid.txt            - Mock Server UID
postman/mock_env_uid.txt               - Mock Environment UID
postman/aws_dev_env_uid.txt            - AWS Dev Environment UID
postman/spec-standalone-payload.json   - Standalone spec payload
```

#### Documentation
```
docs/index.html                        - Redocly main page
docs/site/**                           - Static site files
docs/swagger/**                        - Swagger UI files (if generated)
```

#### SDKs (if generation succeeds)
```
sdk/python/**                          - Python SDK
sdk/javascript/**                      - JavaScript SDK
```

### Postman Resources Created (Both CI/CD and Local)

#### In Postman Workspace
```
APIs Tab:
  - C2M API V2 (API Definition with linked spec)

Specs Tab:
  - C2M API V2 OpenAPI Spec (Standalone spec)

Collections Tab:
  - C2mApiV2LinkedCollection (linked to API Definition)
  - C2mApiV2RealWorldUseCases (use case scenarios)
  - C2mApiV2TestCollection (automated tests)

Mock Servers Tab:
  - Mock Server (backed by Use Case Collection)
    URL: https://[random-id].mock.pstmn.io

Environments Tab:
  - Mock Server Environment (baseUrl = mock server URL)
  - AWS Dev Environment (baseUrl = AWS API Gateway URL)
```

### External Deployments (CI/CD Only)

#### Artifacts Repository
```
Repository: click2mail/c2m-api-v2-postman-artifacts
Branch: main
Files:
  - openapi/*.yaml (all OpenAPI specs)
  - postman/collections/*.json (all collections)
  - postman/metadata/*.txt (UIDs)
  - postman/metadata/*.json (payloads)
  - docs/** (full documentation site)
  - sdks/** (generated SDKs)
```

#### GitHub Pages
```
URL: https://click2mail.github.io/c2m-api-v2-postman/
Content: Redocly API documentation
Updated: On every push to main
```

## Common Commands

### CI/CD (Automatic)
```bash
# Trigger automatically
git push origin main

# OR manually trigger
# GitHub UI: Actions → API Spec, Docs, and Postman CI/CD → Run workflow
```

### Local Development

#### Full Build and Test
```bash
# Complete local build with testing
make postman-instance-build-and-test

# What this does:
# 1. Builds OpenAPI spec
# 2. Creates all Postman resources
# 3. Starts Prism mock (port 4010)
# 4. Runs Postman tests
# 5. Serves docs (port 8080)
```

#### Full Cleanup and Rebuild (matches CI/CD)
```bash
# Delete all Postman resources
make postman-cleanup-all

# Rebuild all Postman resources (no tests)
make postman-instance-build-only

# This is EXACTLY what CI/CD does
```

#### Individual Steps
```bash
# Build OpenAPI from EBNF
make generate-openapi-spec-from-ebnf-dd

# Lint OpenAPI
make lint

# Build docs
make docs

# Generate SDKs
make generate-sdk-all

# Start Prism mock
make prism-start

# Run Postman tests
make postman-mock

# Serve docs locally
make docs-serve
```

## Verification Checklist

After CI/CD run or local build, verify:

### Postman Workspace
- [ ] API Definition exists in APIs tab
- [ ] Standalone Spec exists in Specs tab
- [ ] 3 Collections exist in Collections tab
- [ ] 1 Mock Server exists and returns 200 OK
- [ ] 2 Environments exist (Mock + AWS Dev)
- [ ] Mock Server Environment has correct mock URL

### Local Files
- [ ] `openapi/c2mapiv2-openapi-spec-final.yaml` exists (30KB)
- [ ] `postman/generated/` has 3 JSON files
- [ ] `postman/` has 7+ UID/metadata files
- [ ] `docs/index.html` exists
- [ ] `docs/site/` directory has content

### External (CI/CD Only)
- [ ] Artifacts repo has new commit
- [ ] GitHub Pages updated
- [ ] Workflow shows green checkmark
- [ ] Workflow summary shows all steps passed

### Local Testing Only
- [ ] Prism running on port 4010
- [ ] Postman tests show PASS results
- [ ] Docs accessible at http://localhost:8080
- [ ] No test failures reported

## Troubleshooting

### CI/CD Issues

**Workflow fails at "Publish to Postman"**:
- Check: POSTMAN_SERRAO_API_KEY or POSTMAN_C2M_API_KEY secret exists
- Check: .postman-target file committed (should be "personal" or "team")
- Check: Postman API is responding (https://status.postman.com/)

**Artifacts not copied**:
- Check: SECURITY_REPO_TOKEN secret has repo scope
- Check: artifacts-repo directory exists in workflow
- Check: Files actually generated in previous steps

**GitHub Pages not updated**:
- Check: DEPLOY_GH_PAGES=true (default)
- Check: docs/ directory has content
- Check: Pages enabled in repo settings

### Local Issues

**Prism won't start**:
- Check: Port 4010 not already in use (`lsof -i :4010`)
- Check: OpenAPI spec exists at `openapi/c2mapiv2-openapi-spec-final.yaml`
- Check: Prism installed (`which prism`)

**Postman tests fail**:
- Check: Mock server created successfully
- Check: Environment variables set correctly
- Check: Collections uploaded to workspace
- Check: Prism mock responding on port 4010

**Docs won't serve**:
- Check: Port 8080 not already in use (`lsof -i :8080`)
- Check: docs/ directory exists and has index.html
- Check: Node dependencies installed (`npm ci`)

## Recommendations

### For Daily Development
```bash
# Use local build with testing
make postman-instance-build-and-test

# Verify tests pass before pushing to GitHub
```

### For Quick Iterations
```bash
# Build OpenAPI only
make generate-openapi-spec-from-ebnf-dd

# Upload to Postman (no cleanup)
make postman-import-openapi-spec
```

### For Production Deployment
```bash
# Let CI/CD handle it
git add .
git commit -m "Your changes"
git push origin main

# CI/CD will:
# - Build everything
# - Clean and rebuild Postman workspace
# - Deploy docs to GitHub Pages
# - Push artifacts to artifacts repo
```

### Before Merging PR
```bash
# Run full local build to ensure everything works
make postman-cleanup-all
make postman-instance-build-and-test

# Verify all tests pass
# Then create PR
```

## Summary

**CI/CD Pipeline**:
- **Purpose**: Automated deployment on push to main
- **Scope**: Build all artifacts, publish to Postman, deploy docs
- **Testing**: NONE (assumes local testing already done)
- **Speed**: Fast (~3-5 minutes)
- **Audience**: Production consumers

**Local Pipeline**:
- **Purpose**: Development and validation
- **Scope**: Build all artifacts, run comprehensive tests
- **Testing**: FULL (Prism mock + Postman collection tests)
- **Speed**: Slower (~5-8 minutes)
- **Audience**: Developers

**Key Takeaway**: Local build tests everything before pushing. CI/CD deploys what was already validated locally. This separation keeps CI/CD fast while ensuring quality through local testing.

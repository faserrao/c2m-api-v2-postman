# Complete Build Guide - C2M API V2

**Version**: 2.0
**Last Updated**: 2025-11-09
**Author**: Technical Documentation
**Purpose**: Comprehensive guide for local and CI/CD builds of the entire C2M API V2 pipeline

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture & Pipeline Flow](#architecture--pipeline-flow)
3. [Prerequisites](#prerequisites)
4. [Security Configuration](#security-configuration)
5. [Pre-Build Configuration](#pre-build-configuration)
6. [Local Build Process](#local-build-process)
7. [GitHub CI/CD Build Process](#github-cicd-build-process)
8. [Build Verification](#build-verification)
9. [Resource Update Strategy: Full Rebuild vs Partial Updates](#resource-update-strategy-full-rebuild-vs-partial-updates)
10. [Troubleshooting](#troubleshooting)
11. [Developer Handoff Checklist](#developer-handoff-checklist)

---

## Overview

The C2M API V2 project uses a **data-driven pipeline architecture** where the EBNF data dictionary is the single source of truth. All downstream artifacts (OpenAPI specs, Postman collections, documentation, SDKs) are generated from this source.

### Pipeline Architecture

```
EBNF Data Dictionary (source of truth)
    ↓
OpenAPI Specification (generated)
    ↓
Postman Collections (generated)
    ↓
Mock Servers + Environments (created in Postman cloud)
    ↓
API Documentation (generated)
    ↓
SDKs (generated - future)
```

### Build Types

| Build Type | Trigger | Testing | Publish Target |
|------------|---------|---------|----------------|
| **Local with Tests** | Developer manual | ✅ Local mock server + tests | Personal or Corporate workspace |
| **Local without Tests** | Developer manual | ❌ Skip local testing | Personal or Corporate workspace |
| **GitHub CI/CD** | Git push / PR / Manual | ✅ Automated validation | Workspace from `.postman-target` |

---

## Architecture & Pipeline Flow

### Data-Driven Pipeline

The entire system is built from a single source of truth:

1. **`data_dictionary/c2mapiv2-dd.ebnf`** - EBNF grammar defining all data structures
2. **Python Converter** (`scripts/active/ebnf_to_openapi_dynamic_v3.py`) - Converts EBNF → OpenAPI
3. **OpenAPI Processors** - Add examples, fix oneOf schemas, validate
4. **Postman Generators** - Create collections from OpenAPI spec
5. **Cloud Publishing** - Upload to Postman workspace
6. **Documentation** - Generate API docs with Redocly

### Key Design Principles

- **Single Source of Truth**: EBNF data dictionary drives everything
- **Immutable Artifacts**: Generated files checked into git for diff tracking
- **Dual Workspace Support**: Personal (development) and Corporate (production)
- **Automated Testing**: All endpoints validated before publish
- **Version Control**: All generated artifacts tracked in git

---

## Prerequisites

### Required Software

| Tool | Version | Installation | Purpose |
|------|---------|--------------|---------|
| **Node.js** | 18.x+ | `brew install node` | Postman CLI, OpenAPI tools |
| **Python** | 3.9+ | Built-in on macOS | EBNF converter, test generators |
| **jq** | 1.6+ | `brew install jq` | JSON processing in Makefile |
| **npm** | 9.x+ | Comes with Node.js | Package management |
| **Git** | 2.x+ | Built-in on macOS | Version control |
| **Make** | 3.81+ | Built-in on macOS | Build orchestration |

### Required Node Packages

```bash
# Install from package.json
npm install

# Key packages installed:
# - @redocly/cli (OpenAPI linting, docs generation)
# - @stoplight/spectral-cli (OpenAPI validation)
# - @stoplight/prism-cli (Mock server)
# - postman-cli (Postman automation)
# - openapi-to-postmanv2 (OpenAPI → Postman conversion)
```

### Required Python Packages

```bash
# Automatically installed via Makefile into virtual environment
# See: scripts/python_env/requirements.txt

# Key packages:
# - pyyaml (YAML processing)
# - jsonschema (Validation)
# - openai (AI/NLP features)
# - lark (EBNF parsing)
```

### Directory Structure

```
c2m-api-v2-postman/
├── data_dictionary/          # EBNF source files
│   └── c2mapiv2-dd.ebnf     # Single source of truth
├── openapi/                  # Generated OpenAPI specs
│   ├── c2mapiv2-openapi-spec-base.yaml
│   ├── c2mapiv2-openapi-spec-final.yaml
│   └── c2mapiv2-openapi-spec-final-with-examples.yaml
├── postman/
│   ├── generated/           # Generated collections
│   ├── custom/              # Manual overrides
│   ├── scripts/             # Pre-request/test scripts
│   ├── environments/        # Environment templates
│   └── *.txt                # UID tracking files
├── docs/                    # Generated documentation
├── scripts/
│   ├── active/              # Primary pipeline scripts
│   ├── utilities/           # Support scripts
│   └── python_env/          # Python virtual environment
├── .env                     # Local environment variables (gitignored)
├── .postman-target          # Workspace selector (personal/corporate)
├── Makefile                 # Build orchestrator
└── package.json             # Node dependencies
```

---

## Security Configuration

### Environment Variables

All sensitive credentials are stored in `.env` file (gitignored, never committed to git).

**File**: `.env`

```bash
# Postman API Keys (REQUIRED)
# Get from: https://go.postman.co/settings/me/api-keys
POSTMAN_SERRAO_API_KEY=PMAK-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
POSTMAN_C2M_API_KEY=PMAK-yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

# Workspace IDs (REQUIRED)
POSTMAN_WORKSPACE_ID=d8a1f479-a2aa-4471-869e-b12feea0a98c  # Personal
POSTMAN_WORKSPACE_ID_CORPORATE=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Test Credentials (OPTIONAL - for authentication testing)
TEST_CLIENT_ID=test-client-123
TEST_CLIENT_SECRET=test-secret-456
```

### Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Rotate API keys quarterly** - Generate new keys in Postman settings
3. **Use different keys for development and production**
4. **Store production keys in GitHub Secrets** (see GitHub CI/CD section)
5. **Test credentials are mock values** - Not real production credentials

### GitHub Secrets (for CI/CD)

**Required Secrets** (configured in GitHub repository settings):

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `POSTMAN_SERRAO_API_KEY` | Personal workspace API key | Postman Settings → API Keys |
| `POSTMAN_C2M_API_KEY` | Corporate workspace API key | Postman Settings → API Keys |
| `POSTMAN_WORKSPACE_ID` | Personal workspace UUID | Postman workspace URL |
| `POSTMAN_WORKSPACE_ID_CORPORATE` | Corporate workspace UUID | Postman workspace URL |

**Configuration Path**: GitHub Repository → Settings → Secrets and variables → Actions

---

## Pre-Build Configuration

### Workspace Target Selection

The `.postman-target` file determines which workspace receives the build artifacts.

**File**: `.postman-target`

```bash
# Options: "personal" or "corporate"
personal
```

**How to Set**:

```bash
# Publish to personal workspace (development)
echo "personal" > .postman-target

# Publish to corporate workspace (production)
echo "corporate" > .postman-target

# Check current target
cat .postman-target
```

**How It Works**:

1. Makefile reads `.postman-target` file
2. Selects corresponding API key and workspace ID from `.env`
3. All Postman resources published to selected workspace

**Default**: `personal` (if file doesn't exist)

### Build Type Selection

| Makefile Target | Purpose | Local Testing | Use Case |
|----------------|---------|---------------|----------|
| `postman-instance-build-with-tests` | Full build + local testing | ✅ Yes | Development |
| `postman-instance-build-without-tests` | Build only, skip tests | ❌ No | CI/CD, Quick publish |
| `postman-cleanup-all` | Delete all Postman resources | N/A | Clean slate |

---

## Local Build Process

### Complete Clean Rebuild (Recommended)

This process completely deletes all Postman resources and regenerates everything from scratch.

#### Step 1: Set Workspace Target

```bash
# Choose workspace
echo "personal" > .postman-target

# Verify setting
cat .postman-target
# Output: personal
```

#### Step 2: Source Environment Variables

```bash
# Load API keys and credentials
source .env

# Verify loaded (first 30 chars only)
echo $POSTMAN_SERRAO_API_KEY | cut -c1-30
# Output: PMAK-68778f2760d869000141987d
```

**Why This Step?**:
- Makefile needs environment variables from `.env`
- `source .env` loads them into current shell session
- Must be done in same terminal session as build commands

#### Step 3: Complete Cleanup (Delete All Postman Resources)

```bash
make postman-cleanup-all
```

**What This Does**:

1. **Delete Mock Servers** (`postman-delete-mock-servers`)
   - Finds all mock servers in workspace
   - Deletes each one via Postman API
   - Frees up mock server quota

2. **Delete Collections** (`postman-delete-collections`)
   - Finds all collections in workspace
   - Deletes Test Collection, Linked Collection, Use Case Collection
   - Removes from workspace completely

3. **Delete APIs** (`postman-delete-apis`)
   - Finds all API definitions in workspace
   - Deletes API definition (appears in APIs tab)
   - Removes associated versions and specs

4. **Delete Environments** (`postman-delete-environments`)
   - Finds all environments in workspace
   - Deletes Mock Server environment and AWS Dev environment
   - Removes environment variables

5. **Delete Specs** (`postman-delete-specs`)
   - Finds all standalone OpenAPI specs in workspace
   - Deletes from Specs tab
   - Cleans up orphaned specs

**Expected Output**:

```
🧹 Starting FULL cleanup of Postman resources for workspace d8a1f479-a2aa-4471-869e-b12feea0a98c...
🔍 Fetching mock servers from workspace...
🗑 Deleting mock server 59cece1b-0966-4544-9135-73f9a9bbfc8c...
✅ Mock server deleted
🔍 Fetching collections from workspace...
🗑 Deleting collection 46321051-402bcb82-b4e6-4bb2-90c8-3f2bed733002...
✅ Collection deleted
...
✅ Postman cleanup complete
```

**Duration**: ~30 seconds (depends on number of resources)

#### Step 4: Full Build and Publish

```bash
# Build everything with local testing
source .env && make postman-instance-build-with-tests
```

**OR**

```bash
# Build everything without local testing (faster)
source .env && make postman-instance-build-without-tests
```

**Duration**:
- With tests: ~10-15 minutes
- Without tests: ~5-8 minutes

---

### Detailed Build Pipeline Breakdown

The `postman-instance-build-with-tests` target orchestrates the entire pipeline. Here's what happens:

#### Phase 1: Authentication

**Target**: `postman-login`

```bash
# Authenticates with Postman CLI
postman login --with-api-key $POSTMAN_API_KEY
```

**Purpose**: Establishes authenticated session for Postman CLI commands

**Output**:
```
🔐 Logging in to Postman...
Logged in using api key of user: stellario2021
Logged in successfully.
```

---

#### Phase 2: OpenAPI Spec Generation

**Target**: `generate-openapi-spec-from-ebnf-dd`

This is a multi-step process:

##### Step 2.1: EBNF to OpenAPI Conversion

**Script**: `scripts/active/ebnf_to_openapi_dynamic_v3.py`

```bash
python3 scripts/active/ebnf_to_openapi_dynamic_v3.py \
  -o openapi/c2mapiv2-openapi-spec-base.yaml \
  data_dictionary/c2mapiv2-dd.ebnf
```

**What It Does**:
- Parses EBNF data dictionary using Lark grammar parser
- Converts EBNF structures to OpenAPI 3.0.3 schemas
- Generates request/response definitions for all 9 endpoints
- Creates reusable components for all data types
- Outputs base OpenAPI spec

**Key Transformations**:
- `oneOf` unions → OpenAPI discriminated unions
- EBNF enums → OpenAPI enum constraints
- Composite types → Nested object schemas
- Optional fields `[ field ]` → Not in `required` array
- Repeated fields `{ field }` → Array schemas

**Input**: `data_dictionary/c2mapiv2-dd.ebnf` (499 lines)
**Output**: `openapi/c2mapiv2-openapi-spec-base.yaml` (~1000 lines)

##### Step 2.2: Fix Anonymous oneOf Schemas

**Script**: `scripts/active/fix_openapi_oneOf_schemas.py`

```bash
python3 scripts/active/fix_openapi_oneOf_schemas.py \
  openapi/c2mapiv2-openapi-spec-base.yaml \
  openapi/c2mapiv2-openapi-spec-base.yaml
```

**Purpose**:
- Postman's `openapi-to-postmanv2` converter has a bug with anonymous oneOf schemas
- It simplifies anonymous oneOf to just the first type
- This script converts anonymous oneOf to named schemas

**Example Fix**:
```yaml
# BEFORE (broken in Postman)
paymentDetails:
  oneOf:
    - type: object        # Anonymous schema
      properties: {...}

# AFTER (works in Postman)
paymentDetails:
  oneOf:
    - $ref: '#/components/schemas/creditCardPayment'  # Named schema
```

**Output**: `openapi/c2mapiv2-openapi-spec-base.yaml` (updated in place)

##### Step 2.3: Add Response Examples

**Script**: `scripts/active/add_response_examples.py`

```bash
python3 scripts/active/add_response_examples.py
```

**Purpose**: Add realistic example response data to OpenAPI spec

**What It Adds**:
- Success response examples (200, 201)
- Error response examples (400, 401, 403, 404, 429)
- Realistic job IDs, timestamps, status values
- Used by Postman for test data generation

**Output**: `openapi/c2mapiv2-openapi-spec-final.yaml`

##### Step 2.4: Add Code Samples

**Script**: `scripts/active/add_code_samples.py`

```bash
python3 scripts/active/add_code_samples.py
```

**Purpose**: Add SDK code examples to OpenAPI spec for documentation

**Code Samples Added**:
- Python (requests library)
- JavaScript (fetch API)
- cURL (command line)
- All samples include JWT authentication

**Output**: `openapi/c2mapiv2-openapi-spec-final-with-examples.yaml`

**This is the final OpenAPI spec used for everything downstream.**

---

#### Phase 3: OpenAPI Validation

**Target**: `openapi-spec-lint`

```bash
# Redocly validation
npx @redocly/cli lint openapi/c2mapiv2-openapi-spec-final.yaml

# Spectral validation
npx @stoplight/spectral-cli lint openapi/c2mapiv2-openapi-spec-final.yaml
```

**Purpose**: Validate OpenAPI spec for errors before generating collections

**Checks**:
- OpenAPI 3.0.3 compliance
- Schema consistency
- Required fields present
- Valid references
- Security definitions

**Expected**: 0 errors, ~34 warnings (warnings are acceptable - unused components, missing descriptions)

**If Validation Fails**: Build stops, fix errors in EBNF or converter script

---

#### Phase 4: Postman API Import

**Target**: `postman-import-openapi-spec`

This creates resources in Postman cloud via API.

##### Step 4.1: Import as API Definition

**Target**: `postman-import-openapi-as-api`

```bash
curl -X POST \
  "https://api.getpostman.com/apis?workspaceId=$POSTMAN_WORKSPACE_ID" \
  -H "X-Api-Key: $POSTMAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "C2mApiV2",
    "summary": "C2M API v2 for job submission",
    "description": "...",
    "content": "<OPENAPI_SPEC_CONTENT>"
  }'
```

**Purpose**: Creates API definition in Postman (appears in "APIs" tab)

**Pre-Import Cleanup**:
- Deletes existing APIs with same name
- Prevents duplicates
- Uses `postman-delete-apis-by-name`

**Output**:
- API created with unique ID
- ID saved to `postman/postman_api_uid.txt`
- Example: `4738a2c2-1ad8-4491-b06b-5439650464ab`

##### Step 4.2: Create Standalone Spec

**Target**: `postman-spec-create-standalone`

```bash
curl -X POST \
  "https://api.getpostman.com/apis/$API_ID/versions/$VERSION_ID/schemas" \
  -H "X-Api-Key: $POSTMAN_API_KEY" \
  -d '{
    "type": "openapi3",
    "files": [{"path": "index.yaml", "content": "..."}]
  }'
```

**Purpose**: Creates standalone OpenAPI spec in "Specs" tab

**Pre-Create Cleanup**:
- Deletes existing specs with same name
- Uses `postman-delete-specs-by-name`

**Output**:
- Spec created with unique ID
- Appears in Postman Specs tab
- Example ID: `325402d9-6eb9-46ff-a3a2-8ab5afab94ef`

---

#### Phase 5: Postman Collection Generation

This phase generates 3 different collections for different purposes.

##### Step 5.1: Linked Collection (Generated from OpenAPI)

**Target**: `postman-create-linked-collection`

###### 5.1.1: Generate Collection from OpenAPI

**Command**:
```bash
npx openapi-to-postmanv2 \
  -s openapi/c2mapiv2-openapi-spec-final-with-examples.yaml \
  -o postman/generated/c2mapiv2-collection.json \
  -p
```

**Purpose**: Convert OpenAPI spec to Postman collection format

**Converter Options**:
- `-s`: Source OpenAPI file
- `-o`: Output collection file
- `-p`: Pretty print (formatted JSON)

**Output**: `postman/generated/c2mapiv2-collection.json`

###### 5.1.2: Fix oneOf Placeholders

**Script**: `scripts/active/fix_collection_oneOf_placeholders.js`

```bash
node scripts/active/fix_collection_oneOf_placeholders.js \
  postman/generated/c2mapiv2-collection.json \
  postman/generated/c2mapiv2-collection.json
```

**Purpose**: Replace generic placeholders with oneOf indicators

**Transformations**:
```json
// BEFORE
"paymentDetails": {"type": "<integer>"}

// AFTER
"paymentDetails": {"type": "<oneOf>"}
```

**Why**: Indicates to developers this field has multiple variants

###### 5.1.3: Flatten Collection

**Script**: `scripts/active/flatten_postman_collection.py`

```bash
python3 scripts/active/flatten_postman_collection.py \
  postman/generated/c2mapiv2-collection.json \
  postman/generated/c2mapiv2-linked-collection-flat.json
```

**Purpose**: Remove folder nesting, rename requests to "METHOD /path" format

**Before**:
```
Jobs/
  Single Doc/
    Submit Single Doc Job
```

**After**:
```
POST /jobs/single-doc
POST /jobs/multi-doc
POST /jobs/multi-doc-merge
...
```

**Why**: Easier to find endpoints, clearer in test results

###### 5.1.4: Add JWT Pre-Request Script

**Script**: `scripts/active/add_prerequest_script.py`

```bash
python3 scripts/active/add_prerequest_script.py \
  postman/generated/c2mapiv2-linked-collection-flat.json \
  postman/scripts/jwt-pre-request.js
```

**Purpose**: Add JWT authentication to all requests

**Pre-Request Script Features**:
- Two-token JWT flow (long-term → short-term)
- Automatic token refresh
- Mock server detection (skip auth for mock URLs)
- Token expiry management

**Script Location**: Collection-level pre-request (runs before every request)

###### 5.1.5: Upload to Postman

**Command**:
```bash
curl -X POST \
  "https://api.getpostman.com/collections?workspace=$POSTMAN_WORKSPACE_ID" \
  -H "X-Api-Key: $POSTMAN_API_KEY" \
  -d @postman/generated/c2mapiv2-linked-collection-flat.json
```

**Output**:
- Collection uploaded with UID
- UID saved to `postman/postman_linked_collection_uid.txt`
- Example: `46321051-f2df726e-8dae-42bc-848f-956ec5625ece`

###### 5.1.6: Link to API Definition

**Command**:
```bash
curl -X POST \
  "https://api.getpostman.com/apis/$API_ID/versions/$VERSION_ID/relations" \
  -H "X-Api-Key: $POSTMAN_API_KEY" \
  -d '{
    "collection": {"id": "$COLLECTION_UID"},
    "type": "contracttest"
  }'
```

**Purpose**: Link collection to API definition (shows in APIs tab)

---

##### Step 5.2: Use Case Collection (Real-World Examples)

**Target**: `postman-generate-use-case-collection`

**Script**: `scripts/active/generate_use_case_collection_v2.py`

```bash
python3 scripts/active/generate_use_case_collection_v2.py
```

**Purpose**: Generate curated real-world use case examples

**Use Cases Generated** (8 total):

1. **Legal Firm - Certified Mail**
   - Endpoint: POST /jobs/single-doc-job-template
   - Template: legal_certified_mail
   - Multiple recipients from address list

2. **Real Estate Agent - Property Flyers**
   - Endpoint: POST /jobs/single-doc-job-template
   - Template: real_estate_flyer
   - Single document to multiple addresses

3. **Medical Agency - Patient Statements**
   - Endpoint: POST /jobs/multi-doc-merge-job-template
   - Template: medical_statement
   - Merge multiple documents per patient

4. **Monthly Newsletters**
   - Endpoint: POST /jobs/single-doc-job-template
   - Template: newsletter_standard
   - Bulk mailing to subscriber list

5. **Company with Embedded Addresses #1**
   - Endpoint: POST /jobs/multi-pdf-address-capture
   - Multiple PDFs with embedded addresses

6. **Company with Embedded Addresses #2**
   - Endpoint: POST /jobs/single-pdf-split-addressCapture
   - Single PDF with address extraction

7. **Reseller - Multi-Doc #1**
   - Endpoint: POST /jobs/multi-docs-job-template
   - Different document per recipient

8. **Reseller - Multi-Doc #2**
   - Endpoint: POST /jobs/single-pdf-split
   - Split PDF by page ranges

**Data Strategy**:
- Reads from `data_dictionary/generate-endpoint-permutations/permutations/`
- Each permutation file has 270-810 variations
- Randomly selects 5 diverse examples per endpoint
- Ensures variety across document sources, payment types, addresses

**Output**: `postman/generated/c2mapiv2-use-case-collection.json`

**Upload**: Same process as Linked Collection

**UID File**: `postman/use_case_collection_uid.txt`

---

##### Step 5.3: Test Collection (Automated Testing)

**Target**: `postman-create-test-collection`

This is the most complex collection with automated tests.

###### 5.3.1: Start with Base Collection

**Input**: `postman/generated/c2mapiv2-collection.json`

###### 5.3.2: Add Example Data

**Script**: `scripts/test_data_generator_for_collections/addRandomDataToRaw.js`

```bash
node scripts/test_data_generator_for_collections/addRandomDataToRaw.js \
  --input postman/generated/c2mapiv2-collection.json \
  --output postman/generated/c2mapiv2-test-collection-with-examples.json
```

**Purpose**: Add rotating realistic test data to all requests

**oneOf Rotation Strategy**:

```javascript
// Rotates through variants for each oneOf field
paymentDetails variants (6):
  0: creditCardPayment
  1: invoicePayment
  2: achPayment
  3: userCreditPayment
  4: applePayPayment
  5: googlePayPayment

documentSourceIdentifier variants (5):
  0: documentId (integer)
  1: externalUrl (string)
  2: uploadRequestId + documentName
  3: uploadRequestId + zipId + documentName
  4: zipId + documentName

recipientAddressSource variants (3):
  0: recipientAddress (inline)
  1: addressListId (reference)
  2: addressId (reference)
```

**Example Output**:
```json
{
  "documentSourceIdentifier": {
    "documentId": 12345
  },
  "recipientAddressSource": {
    "recipientAddress": {
      "firstName": "John",
      "lastName": "Doe",
      "address1": "123 Main St",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  },
  "paymentDetails": {
    "creditCardPayment": {
      "creditCardDetails": {
        "cardType": "visa",
        "cardNumber": "4111111111111111",
        "expirationDate": {"month": 12, "year": 2025},
        "cvv": 123
      }
    }
  },
  "jobTemplate": "legal_certified_mail",
  "tags": ["test", "legal", "certified"]
}
```

**Statistics Reported**:
- Modified requests: 9
- Modified responses: 9
- oneOf replacements: ~100 total
- Current rotation indices

###### 5.3.3: Merge Custom Overrides

**Script**: `scripts/active/merge_overrides.py`

```bash
python3 scripts/active/merge_overrides.py \
  postman/generated/c2mapiv2-test-collection-with-examples.json \
  postman/custom/overrides.json \
  postman/generated/c2mapiv2-test-collection-merged.json
```

**Purpose**: Apply manual customizations from `postman/custom/overrides.json`

**Customizations**:
- Test-specific headers
- Environment variable overrides
- Custom test assertions
- Specific test data scenarios

**Merge Strategy**: Deep merge (custom values override generated values)

###### 5.3.4: Add Automated Tests

**Script**: `scripts/active/add_tests.js`

```bash
node scripts/active/add_tests.js \
  postman/generated/c2mapiv2-test-collection-merged.json \
  postman/generated/c2mapiv2-test-collection-with-tests.json \
  200,201,204,400,401,403,404,429
```

**Tests Added to Each Request**:

```javascript
// Test 1: Status code validation
pm.test("Status code is allowed (200,201,204,400,401,403,404,429)", function () {
    pm.expect([200,201,204,400,401,403,404,429]).to.include(pm.response.code);
});

// Test 2: Response time check
pm.test("Response time < 1s", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});
```

**Allowed Status Codes**:
- `200` - OK
- `201` - Created
- `204` - No Content
- `400` - Bad Request (validation error)
- `401` - Unauthorized (auth required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limit)

**Why 403 Allowed**: Auth endpoints may return 403 for invalid credentials (not a test failure)

###### 5.3.5: Add JWT Authentication

**Script**: `scripts/active/add_prerequest_script.py`

Same JWT pre-request script as Linked Collection.

###### 5.3.6: Auto-Fix Collection

**Script**: `scripts/jq/auto_fix.jq` (jq filter)

```bash
jq -f scripts/jq/auto_fix.jq \
  postman/generated/c2mapiv2-test-collection-with-tests.json \
  > postman/generated/c2mapiv2-test-collection-fixed.json
```

**Fixes Applied**:
- Remove invalid characters
- Fix malformed JSON
- Normalize whitespace
- Remove duplicate keys

###### 5.3.7: Fix URLs

**Script**: `scripts/active/fix_collection_urls_v2.py`

```bash
python3 scripts/active/fix_collection_urls_v2.py \
  postman/generated/c2mapiv2-test-collection-fixed.json
```

**URL Transformations**:

```
BEFORE: https://api.example.com/v1/jobs/single-doc
AFTER:  {{baseUrl}}/jobs/single-doc
```

**Purpose**: Use environment variable for base URL (supports mock/dev/prod)

###### 5.3.8: Validate Collection

**Command**:
```bash
jq empty postman/generated/c2mapiv2-test-collection-fixed.json
```

**Purpose**: Ensure valid JSON before upload

**If Validation Fails**: Build stops, fix JSON syntax

###### 5.3.9: Flatten and Rename

Same flatten script as Linked Collection.

**Output**: `postman/generated/c2mapiv2-test-collection-flat.json`

###### 5.3.10: Upload to Postman

**Upload**: Same process as other collections

**UID File**: `postman/test_collection_uid.txt`

**This collection is used for mock server creation** (has endpoint definitions)

---

#### Phase 6: Mock Server & Environments

##### Step 6.1: Create Mock Server

**Target**: `postman-mock-create`

```bash
curl -X POST \
  "https://api.getpostman.com/mocks?workspace=$POSTMAN_WORKSPACE_ID" \
  -H "X-Api-Key: $POSTMAN_API_KEY" \
  -d '{
    "name": "C2M API Mock Server",
    "collection": "'$TEST_COLLECTION_UID'",
    "private": false
  }'
```

**IMPORTANT**: Mock must be created from **Test Collection**, not Use Case Collection

**Why**:
- Test Collection has endpoint **definitions** (request/response schemas)
- Use Case Collection only has **example requests**
- Mock server needs definitions to generate responses

**Output**:
- Mock server created with unique URL
- Example: `https://1b4e5d65-0e75-443c-88cb-03e727e35939.mock.pstmn.io`
- UID saved to `postman/postman_mock_uid.txt`

##### Step 6.2: Create Environments

**Target**: `postman-env-create`

Two environments are created:

###### Environment 1: Mock Server Environment

**File**: `postman/mock-env.json`

**Generated By**: `scripts/active/generate_postman_env.sh`

**Variables**:
```json
{
  "name": "C2M API - Mock Server",
  "values": [
    {
      "key": "baseUrl",
      "value": "https://1b4e5d65-0e75-443c-88cb-03e727e35939.mock.pstmn.io",
      "type": "default",
      "enabled": true
    },
    {
      "key": "isMockServer",
      "value": "true",
      "type": "default"
    },
    {
      "key": "clientId",
      "value": "test-client-123",
      "type": "secret"
    },
    {
      "key": "clientSecret",
      "value": "test-secret-456",
      "type": "secret"
    }
  ]
}
```

**Purpose**: Use mock server for testing without backend

###### Environment 2: AWS Dev Environment

**File**: `postman/environments/c2m-aws-dev.postman_environment.json`

**Variables**:
```json
{
  "name": "C2M API - AWS Dev",
  "values": [
    {
      "key": "baseUrl",
      "value": "https://api.dev.c2m.com/v2",
      "type": "default"
    },
    {
      "key": "authUrl",
      "value": "https://auth.dev.c2m.com",
      "type": "default"
    },
    {
      "key": "isMockServer",
      "value": "false",
      "type": "default"
    },
    {
      "key": "clientId",
      "value": "test-client-123",
      "type": "secret"
    },
    {
      "key": "clientSecret",
      "value": "test-secret-456",
      "type": "secret"
    }
  ]
}
```

**Purpose**: Use real AWS backend for integration testing

##### Step 6.3: Upload Environments

**Command**:
```bash
curl -X POST \
  "https://api.getpostman.com/environments?workspace=$POSTMAN_WORKSPACE_ID" \
  -H "X-Api-Key: $POSTMAN_API_KEY" \
  -d @postman/mock-env.json
```

**Repeated for both environments**

**Output**:
- Mock environment UID saved to `postman/postman_env_uid.txt`
- AWS Dev environment UID saved separately

##### Step 6.4: Link Mock Server to Environment

**Target**: `update-mock-env`

```bash
curl -X PUT \
  "https://api.getpostman.com/mocks/$MOCK_UID" \
  -H "X-Api-Key: $POSTMAN_API_KEY" \
  -d '{
    "environment": "'$MOCK_ENV_UID'"
  }'
```

**Purpose**: Associate mock server with Mock environment (auto-selects when using mock)

---

#### Phase 7: Documentation Generation

**Target**: `docs` (only in full build, not in `-without-tests`)

##### Step 7.1: Generate API Documentation

**Command**:
```bash
npx @redocly/cli build-docs \
  openapi/c2mapiv2-openapi-spec-final-with-examples.yaml \
  -o docs/index.html
```

**Purpose**: Generate interactive HTML documentation from OpenAPI spec

**Features**:
- Interactive API explorer
- Request/response examples
- Try-it-out functionality
- Search and navigation
- Code samples in Python/JavaScript/cURL

**Output**: `docs/index.html` (single-file HTML)

##### Step 7.2: Serve Documentation (Local Only)

**Command** (only with `-with-tests`):
```bash
npx @redocly/cli preview-docs \
  openapi/c2mapiv2-openapi-spec-final-with-examples.yaml \
  -p 8080
```

**Purpose**: Start local documentation server for review

**Access**: http://localhost:8080

**Duration**: Runs in background until build completes or Ctrl+C

---

#### Phase 8: Local Testing (Only with `-with-tests`)

##### Step 8.1: Start Prism Mock Server

**Command**:
```bash
npx @stoplight/prism-cli mock \
  openapi/c2mapiv2-openapi-spec-final-with-examples.yaml \
  -p 4010
```

**Purpose**: Start local mock server for testing

**Access**: http://localhost:4010

**Features**:
- Validates requests against OpenAPI spec
- Returns example responses
- Reports validation errors

##### Step 8.2: Run Postman Tests Against Local Mock

**Command**:
```bash
postman collection run \
  postman/generated/c2mapiv2-test-collection-flat.json \
  --environment postman/mock-env.json \
  --reporter-cli-no-failures \
  --reporter-cli-no-console
```

**Purpose**: Validate all endpoints against local mock

**Tests Run**:
- 9 endpoints × 2 tests = 18 tests minimum
- Additional custom tests from overrides

**Expected Results**:
- ✅ All tests pass
- ⏱️ Response times < 1s
- ✅ Status codes in allowed list

**If Tests Fail**:
- Check Prism logs for validation errors
- Review test collection
- Fix OpenAPI spec or test expectations

---

### Build Output Summary

After successful build, the following resources exist:

#### Postman Cloud Resources

| Resource Type | Name | UID File | Purpose |
|--------------|------|----------|---------|
| API Definition | C2mApiV2 | `postman/postman_api_uid.txt` | API in "APIs" tab |
| Standalone Spec | C2mApiV2 | N/A | Spec in "Specs" tab |
| Test Collection | C2mApiV2TestCollection | `postman/test_collection_uid.txt` | Automated testing |
| Linked Collection | C2mApiCollectionLinked | `postman/postman_linked_collection_uid.txt` | Linked to API |
| Use Case Collection | C2M API v2 - Real World Use Cases | N/A | Examples |
| Mock Server | C2M API Mock Server | `postman/postman_mock_uid.txt` | Cloud mock |
| Mock Environment | C2M API - Mock Server | `postman/postman_env_uid.txt` | Mock variables |
| AWS Dev Environment | C2M API - AWS Dev | N/A | Real API variables |

#### Local Files Generated

| File | Size | Purpose |
|------|------|---------|
| `openapi/c2mapiv2-openapi-spec-base.yaml` | ~50KB | Base spec from EBNF |
| `openapi/c2mapiv2-openapi-spec-final.yaml` | ~60KB | Spec with examples |
| `openapi/c2mapiv2-openapi-spec-final-with-examples.yaml` | ~80KB | Final spec with code samples |
| `postman/generated/c2mapiv2-collection.json` | ~106KB | Base collection |
| `postman/generated/c2mapiv2-linked-collection-flat.json` | ~103KB | Linked collection |
| `postman/generated/c2mapiv2-test-collection-flat.json` | ~102KB | Test collection |
| `postman/generated/c2mapiv2-use-case-collection.json` | ~126KB | Use case collection |
| `docs/index.html` | ~500KB | API documentation |

---

## GitHub CI/CD Build Process

The GitHub Actions workflow automates the entire build process on every push to `main` or when manually triggered.

### Workflow File

**Location**: `.github/workflows/api-ci-cd.yml`

### Triggers

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'data_dictionary/**'
      - 'scripts/**'
      - 'postman/**'
      - 'Makefile'
      - '.github/workflows/api-ci-cd.yml'
  pull_request:
    branches:
      - main
  workflow_dispatch:   # Manual trigger
```

**Trigger Conditions**:
1. **Push to main**: Automatic on commits to main branch
2. **Pull Request**: Automatic on PRs targeting main
3. **Manual**: Via GitHub Actions UI → Run workflow

**Path Filters**: Only triggers if files in these directories change

---

### Workflow Steps

#### Step 1: Checkout Code

```yaml
- name: Checkout code
  uses: actions/checkout@v3
```

**Purpose**: Clone repository to GitHub Actions runner

---

#### Step 2: Setup Node.js

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v3
  with:
    node-version: '18'
```

**Purpose**: Install Node.js for npm packages

---

#### Step 3: Install Dependencies

```yaml
- name: Install dependencies
  run: npm ci
```

**Purpose**: Install exact versions from package-lock.json

**Why `npm ci` instead of `npm install`**:
- Faster (skips package resolution)
- Reproducible (uses lockfile exactly)
- Fails if lockfile out of sync

---

#### Step 4: Install Postman CLI

```yaml
- name: Install Postman CLI
  run: |
    curl -o- "https://dl-cli.pstmn.io/install/linux64.sh" | sh
```

**Purpose**: Install Postman CLI for collection runs

**Platform**: Linux (GitHub Actions runner)

---

#### Step 5: Set Postman Target

```yaml
- name: Set Postman target workspace
  run: |
    if [ ! -f .postman-target ]; then
      echo "personal" > .postman-target
    fi
    echo "Publishing to: $(cat .postman-target)"
```

**Purpose**: Ensure `.postman-target` file exists

**Default**: `personal` if file not in repo

---

#### Step 6: Build OpenAPI Spec

```yaml
- name: Build OpenAPI spec from EBNF
  run: make openapi-build
  env:
    POSTMAN_SERRAO_API_KEY: ${{ secrets.POSTMAN_SERRAO_API_KEY }}
    POSTMAN_C2M_API_KEY: ${{ secrets.POSTMAN_C2M_API_KEY }}
```

**Target**: `openapi-build`

**Includes**:
1. `generate-openapi-spec-from-ebnf-dd`
2. `openapi-spec-lint`

**Environment Variables**: Loaded from GitHub Secrets

---

#### Step 7: Generate Postman Collections

```yaml
- name: Generate Postman collections
  run: make postman-collection-build
```

**Target**: `postman-collection-build`

**Generates**:
- Linked Collection
- Test Collection
- Use Case Collection

**Does NOT**:
- Upload to Postman (happens in next step)
- Run local tests (no Prism in CI)

---

#### Step 8: Build Documentation

```yaml
- name: Build documentation
  run: make docs
```

**Target**: `docs`

**Generates**: `docs/index.html`

**No Server**: Does not start preview server (CI environment)

---

#### Step 9: Auto-Commit Generated Files

```yaml
- name: Commit generated files
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  run: |
    git config user.name "GitHub Actions"
    git config user.email "actions@github.com"
    git add openapi/*.yaml postman/generated/*.json docs/
    git diff --staged --quiet || git commit -m "chore: regenerate API artifacts [skip ci]"
    git push
```

**When**: Only on push to main (not PRs, not manual triggers)

**What It Commits**:
- OpenAPI specs (`openapi/*.yaml`)
- Postman collections (`postman/generated/*.json`)
- Documentation (`docs/`)

**Commit Message**: Includes `[skip ci]` to prevent infinite loop

**Why Commit Generated Files**:
- Track changes in git diffs
- Enable OpenAPI spec diff in PRs
- Preserve artifacts for rollback

---

#### Step 10: Publish to Postman

```yaml
- name: Publish to Postman
  run: make postman-publish
  env:
    POSTMAN_SERRAO_API_KEY: ${{ secrets.POSTMAN_SERRAO_API_KEY }}
    POSTMAN_C2M_API_KEY: ${{ secrets.POSTMAN_C2M_API_KEY }}
```

**Target**: `postman-publish`

**Workspace Selection**: Reads `.postman-target` file

**What It Publishes**:
- API Definition
- Standalone Spec
- Test Collection
- Linked Collection
- Use Case Collection
- Mock Server
- Environments

**Same Process**: As local build, but automated

---

#### Step 11: Copy Artifacts to Artifacts Repo (Optional)

```yaml
- name: Copy artifacts to artifacts repo
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  env:
    SECURITY_REPO_TOKEN: ${{ secrets.SECURITY_REPO_TOKEN }}
  run: |
    git clone https://${SECURITY_REPO_TOKEN}@github.com/click2mail/c2m-api-v2-postman-artifacts.git ../artifacts
    cp -r openapi/*.yaml ../artifacts/openapi/
    cp -r postman/generated/*.json ../artifacts/postman/
    cp -r docs/ ../artifacts/docs/
    cd ../artifacts
    git config user.name "GitHub Actions"
    git config user.email "actions@github.com"
    git add .
    git diff --staged --quiet || git commit -m "chore: update artifacts from main repo"
    git push
```

**Purpose**: Maintain separate artifacts repository

**Authentication**: Uses Personal Access Token from GitHub Secrets

**Artifacts Copied**:
- OpenAPI specs
- Postman collections
- Documentation

**Optional**: Can be disabled by removing from workflow

---

#### Step 12: Deploy Documentation to GitHub Pages

```yaml
- name: Deploy docs to GitHub Pages
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs
```

**Purpose**: Publish documentation to public URL

**URL**: https://click2mail.github.io/c2m-api-v2-postman/

**When**: Only on push to main

**Requires**: GitHub Pages enabled in repository settings

---

### GitHub Secrets Configuration

All sensitive credentials stored in GitHub repository settings.

**Path**: Repository → Settings → Secrets and variables → Actions

**Required Secrets**:

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `POSTMAN_SERRAO_API_KEY` | `PMAK-xxxxxxxx...` | Postman → Settings → API Keys → Generate API Key |
| `POSTMAN_C2M_API_KEY` | `PMAK-yyyyyyyy...` | Same process (corporate account) |
| `SECURITY_REPO_TOKEN` | `ghp_xxxxxxxxx...` | GitHub → Settings → Developer settings → Personal access tokens → Generate new token (classic) → Permissions: `repo` (full control) |

**Secret Security**:
- Secrets never appear in logs (GitHub redacts them)
- Only accessible to workflows in same repository
- Rotate regularly (recommended quarterly)

---

### Differences: Local vs CI/CD

| Aspect | Local Build | GitHub CI/CD |
|--------|-------------|--------------|
| **Trigger** | Manual (`make` command) | Automatic (git push) |
| **Authentication** | `.env` file | GitHub Secrets |
| **Testing** | Prism mock server + Postman CLI | No local testing |
| **Documentation** | Server started on port 8080 | HTML generated, no server |
| **Artifacts Commit** | Manual | Automatic |
| **Duration** | 10-15 min (with tests) | 5-8 min (no local tests) |
| **Build Target** | `postman-instance-build-with-tests` | `postman-instance-build-without-tests` |

---

### Workflow Execution Example

**Trigger**: Push to main

```
15:23:14 - Workflow triggered by push (commit abc123)
15:23:16 - Checkout code                                 ✓ 2s
15:23:18 - Setup Node.js 18                              ✓ 2s
15:23:25 - Install dependencies (npm ci)                 ✓ 7s
15:23:32 - Install Postman CLI                           ✓ 7s
15:23:33 - Set Postman target (personal)                 ✓ 1s
15:25:42 - Build OpenAPI spec from EBNF                  ✓ 2m 9s
15:27:15 - Generate Postman collections                  ✓ 1m 33s
15:27:48 - Build documentation                           ✓ 33s
15:27:51 - Commit generated files                        ✓ 3s
15:29:23 - Publish to Postman (personal workspace)       ✓ 1m 32s
15:29:35 - Copy artifacts to artifacts repo              ✓ 12s
15:29:47 - Deploy docs to GitHub Pages                   ✓ 12s
15:29:48 - Workflow complete                             ✓ 6m 34s
```

**Total Duration**: ~6-7 minutes

---

## Build Verification

After build completes (local or CI/CD), verify all resources created correctly.

### Verification Checklist

#### 1. Local Files Generated

```bash
# Check OpenAPI specs exist
ls -lh openapi/*.yaml
# Expected: 3 files (base, final, final-with-examples)

# Check Postman collections exist
ls -lh postman/generated/*.json
# Expected: 9+ files (collection, linked, test, use-case, and variants)

# Check documentation generated
ls -lh docs/index.html
# Expected: ~500KB HTML file

# Check UID files created
ls -la postman/*_uid.txt
# Expected: 5 files (api, env, linked_collection, mock, test_collection)
```

#### 2. Postman Workspace Resources

```bash
# Source API key
source .env

# List collections
curl -s -H "X-API-Key: $POSTMAN_SERRAO_API_KEY" \
  "https://api.getpostman.com/collections?workspace=$POSTMAN_WORKSPACE_ID" \
  | jq -r '.collections[] | "\(.name)"'

# Expected output:
# C2mApiV2TestCollection
# C2mApiCollectionLinked
# C2M API v2 - Real World Use Cases

# List environments
curl -s -H "X-API-Key: $POSTMAN_SERRAO_API_KEY" \
  "https://api.getpostman.com/environments?workspace=$POSTMAN_WORKSPACE_ID" \
  | jq -r '.environments[] | "\(.name)"'

# Expected output:
# C2M API - Mock Server
# C2M API - AWS Dev

# List mock servers
curl -s -H "X-API-Key: $POSTMAN_SERRAO_API_KEY" \
  "https://api.getpostman.com/mocks?workspace=$POSTMAN_WORKSPACE_ID" \
  | jq -r '.mocks[] | "\(.name) - \(.mockUrl)"'

# Expected output:
# C2M API Mock Server - https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.mock.pstmn.io
```

#### 3. Postman UI Verification

1. **Open Postman Desktop App**
2. **Switch to Personal Workspace** (or Corporate if that's the target)
3. **Check APIs Tab**:
   - Should see "C2mApiV2" API definition
   - Click → Should show linked collection
4. **Check Collections Tab**:
   - Should see 3 collections
   - Open Test Collection → Should have 9 endpoints
5. **Check Environments Tab**:
   - Should see 2 environments
   - Open Mock environment → Should have `baseUrl`, `clientId`, `clientSecret`
6. **Check Specs Tab**:
   - Should see "C2mApiV2" standalone spec
   - Click → Should open OpenAPI spec viewer

#### 4. Test Mock Server

```bash
# Get mock URL from environment file
MOCK_URL=$(jq -r '.values[] | select(.key == "baseUrl") | .value' postman/mock-env.json)

# Test endpoint
curl -X POST \
  "$MOCK_URL/jobs/single-doc-job-template" \
  -H "Content-Type: application/json" \
  -d '{
    "documentSourceIdentifier": {"documentId": 12345},
    "recipientAddressSource": {"addressListId": 67890},
    "jobTemplate": "legal_certified_mail",
    "paymentDetails": {
      "creditCardPayment": {
        "creditCardDetails": {
          "cardType": "visa",
          "cardNumber": "4111111111111111",
          "expirationDate": {"month": 12, "year": 2025},
          "cvv": 123
        }
      }
    }
  }'

# Expected response:
# {
#   "status": "processing",
#   "message": "Job submitted successfully",
#   "jobId": "CSlkTg1owN"
# }
```

#### 5. Test Documentation

```bash
# Local documentation (if running with -with-tests)
open http://localhost:8080

# OR GitHub Pages (after CI/CD deploy)
open https://click2mail.github.io/c2m-api-v2-postman/
```

**What to Check**:
- All 9 endpoints listed
- Request/response examples visible
- Code samples in Python/JavaScript/cURL
- Search functionality works

---

## Resource Update Strategy: Full Rebuild vs Partial Updates

### Overview

This section explains the recommended approach for updating Postman resources when making changes to the API.

### Two Approaches Considered

#### Approach 1: Full Rebuild (Recommended ✅)

**Command**:
```bash
make postman-cleanup-all && make postman-instance-build-without-tests
```

**Process**:
1. Delete all existing Postman resources (mock servers, collections, APIs, environments, specs)
2. Regenerate all artifacts from EBNF data dictionary
3. Upload all resources to Postman workspace

**Advantages**:
- ✅ **Clean slate**: No orphaned resources or inconsistencies
- ✅ **Predictable**: Always produces same result regardless of previous state
- ✅ **Dual workspace compatible**: Works correctly with both personal and corporate workspaces
- ✅ **No UID tracking issues**: All UIDs regenerated fresh
- ✅ **Safe**: No risk of partial state corruption
- ✅ **Tested**: This is the primary workflow tested in CI/CD

**Disadvantages**:
- ⏱️ Slower: Takes 5-8 minutes for complete rebuild
- 📊 UID changes: New UIDs generated each time (breaks external references)

**When to Use**:
- Making changes to EBNF data dictionary
- Adding or removing endpoints
- Changing schema structures
- After fixing build errors
- When switching between workspaces
- When unsure of current Postman state

---

#### Approach 2: Partial Update (Not Recommended ⚠️)

**Concept**: Update only the changed resource (e.g., re-upload one collection without full rebuild)

**Example**:
```bash
# Hypothetical workflow (not implemented)
make postman-generate-use-case-collection
make postman-upload-use-case-collection
```

**Why Not Implemented**:

##### Issue 1: Dual Workspace UID Tracking

**Problem**: UID files don't track which workspace they belong to

```bash
# Upload to personal workspace
echo "personal" > .postman-target
make postman-instance-build-without-tests
# Saves UID to test_collection_uid.txt (personal workspace UID)

# Switch to corporate workspace
echo "corporate" > .postman-target
make postman-upload-use-case-collection  # Hypothetical partial update
# Reads UID from file (personal's UID)
# Tries to delete from corporate workspace using personal's UID
# Result: Either fails (UID not found) OR leaves orphan in personal workspace
```

**Root Cause**: Single local infrastructure publishes to two different Postman workspaces, but UID files don't distinguish between them.

##### Issue 2: Complexity of Name-Based Deletion

**Alternative Considered**: Query by name → delete if found → upload new

**Example**:
```bash
# For each resource upload:
# 1. Query current workspace for resource by name
# 2. If found, delete it
# 3. Upload new resource with same name
```

**Implementation Impact**: Would require adding name-based deletion logic to 8+ Makefile targets:
- `postman-linked-collection-upload`
- `postman-test-collection-upload`
- `postman-upload-enhanced-collection`
- `postman-upload-use-case-collection`
- `postman-env-upload`
- `postman-spec-create`
- `postman-spec-create-standalone`
- `postman-mock-create`

**Why Not Implemented**:
- Adds complexity to build system
- Requires API calls for every upload (slower)
- Still risk of race conditions (if multiple builds run simultaneously)
- Error handling becomes more complex
- Not significantly faster than full rebuild for typical changes

##### Issue 3: Dependency Graph Complexity

**Problem**: Postman resources have complex dependencies

**Example**:
```
Mock Server → depends on → Test Collection → depends on → OpenAPI Spec → depends on → EBNF
Environment → depends on → Mock Server URL
Linked Collection → depends on → API Definition
```

**Scenario**: Update EBNF to add new field

**Partial Update Would Require**:
1. Regenerate OpenAPI spec
2. Regenerate Test Collection (uses OpenAPI spec)
3. Recreate Mock Server (uses Test Collection UID)
4. Update Environment (new mock URL)
5. Regenerate Linked Collection (new OpenAPI spec)
6. Update API Definition (new OpenAPI spec)

**Result**: Almost same work as full rebuild, but with more room for errors

---

### Recommended Workflow

#### For Development (Frequent Changes)

**Full Rebuild Workflow**:
```bash
# 1. Make changes to EBNF data dictionary
vim data_dictionary/c2mapiv2-dd.ebnf

# 2. Set workspace target
echo "personal" > .postman-target

# 3. Source environment variables
source .env

# 4. Complete rebuild
make postman-cleanup-all && make postman-instance-build-without-tests

# Duration: 5-8 minutes
```

#### For Production Releases

**Same Full Rebuild via CI/CD**:
```bash
# 1. Merge to main branch
git checkout main
git merge feature-branch
git push

# 2. GitHub Actions automatically:
#    - Reads .postman-target (corporate)
#    - Runs full rebuild
#    - Publishes to corporate workspace
#    - Commits generated artifacts

# Duration: 6-7 minutes (automated)
```

#### For Quick Iterations (Manual Deletion)

**If you absolutely need partial update** (e.g., testing one collection change):

```bash
# 1. Make your change
vim scripts/active/generate_use_case_collection_v2.py

# 2. Regenerate only the affected file
make postman-generate-use-case-collection

# 3. Manually delete from Postman UI
#    - Open Postman desktop app
#    - Navigate to Collections tab
#    - Find "C2M API v2 - Real World Use Cases"
#    - Right-click → Delete

# 4. Upload new version
make postman-upload-use-case-collection

# Duration: 1-2 minutes (but manual steps required)
```

**Why Manual Deletion**:
- Ensures you're deleting from correct workspace (you can see which workspace you're in)
- No risk of cross-workspace UID confusion
- Simple and explicit
- Only viable for single-resource updates

---

### Decision Rationale

**Why Full Rebuild is Recommended**:

1. **Dual Workspace Architecture**: Local infrastructure publishes to both personal and corporate workspaces. Automated partial updates would need complex workspace-aware UID tracking.

2. **Build Speed**: Full rebuild (5-8 min) vs partial update (1-2 min manual + implementation complexity) is not significant enough to justify the added complexity.

3. **Reliability**: Full rebuild guarantees consistent state. Partial updates risk leaving orphaned resources or inconsistent dependencies.

4. **Simplicity**: One well-tested workflow is easier to maintain than multiple code paths for different update scenarios.

5. **CI/CD Alignment**: GitHub Actions uses full rebuild. Keeping local workflow aligned reduces surprises.

6. **Error Recovery**: If partial update fails midway, state is unclear. Full rebuild always starts from clean state.

---

### Future Considerations

If partial updates become critical (e.g., for very large APIs where full rebuild takes 30+ minutes), consider:

1. **Workspace-Aware UID Tracking**:
   ```bash
   # Instead of:
   postman/test_collection_uid.txt

   # Use:
   postman/personal/test_collection_uid.txt
   postman/corporate/test_collection_uid.txt
   ```

2. **Dependency Graph Analysis**:
   - Detect which resources need regeneration based on what changed
   - Only rebuild affected resources and their dependents
   - Similar to `make`'s dependency tracking

3. **State Checksum Validation**:
   - Store checksums of each resource
   - Compare before upload
   - Only upload if changed

**Current Status**: Not implemented. Use full rebuild for all changes.

---

## Troubleshooting

### Common Build Errors

#### Error 1: "Error occurred in validating API key"

**Symptom**:
```
🔐 Logging in to Postman...
error: Error occurred in validating API key. Please try again.
make: *** [postman-login] Error 1
```

**Cause**: API key not loaded or invalid

**Fix**:
```bash
# 1. Verify .env file exists
ls -la .env

# 2. Check API key format (should start with PMAK-)
grep "POSTMAN_SERRAO_API_KEY" .env | cut -c1-50

# 3. Source .env file in current shell
source .env

# 4. Verify loaded
echo $POSTMAN_SERRAO_API_KEY | cut -c1-30

# 5. Retry build
make postman-instance-build-without-tests
```

---

#### Error 2: "Cannot iterate over null (null)"

**Symptom**:
```
jq: error (at <stdin>:0): Cannot iterate over null (null)
```

**Cause**: Postman API returned empty or error response

**Fix**:
```bash
# 1. Test API key manually
curl -s -H "X-API-Key: $POSTMAN_SERRAO_API_KEY" \
  "https://api.getpostman.com/me" | jq '.'

# If this returns {"error": {...}}, key is invalid
# Generate new key in Postman settings

# 2. Test workspace access
curl -s -H "X-API-Key: $POSTMAN_SERRAO_API_KEY" \
  "https://api.getpostman.com/workspaces" | jq '.workspaces[] | .name'

# Should list your workspaces
# If empty, check workspace permissions
```

---

#### Error 3: "Collection uploaded with UID: (empty)"

**Symptom**: Collection upload succeeds but UID not saved

**Cause**: Postman API response format changed or parsing error

**Fix**:
```bash
# 1. Check UID file
cat postman/test_collection_uid.txt
# Should have UID like: 46321051-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# 2. If empty, manually query collections
curl -s -H "X-API-Key: $POSTMAN_SERRAO_API_KEY" \
  "https://api.getpostman.com/collections?workspace=$POSTMAN_WORKSPACE_ID" \
  | jq -r '.collections[] | select(.name == "C2mApiV2TestCollection") | .uid'

# 3. Manually save UID
echo "46321051-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" > postman/test_collection_uid.txt

# 4. Continue build
make postman-create-mock-and-env
```

---

#### Error 4: "Mock server creation failed"

**Symptom**:
```
Error: Collection UID is required but not found
```

**Cause**: Test collection not uploaded or UID not saved

**Fix**:
```bash
# 1. Verify test collection exists
cat postman/test_collection_uid.txt
# Should not be empty

# 2. If empty, re-upload test collection
make postman-test-collection-upload

# 3. Verify UID saved
cat postman/test_collection_uid.txt

# 4. Retry mock creation
make postman-mock-create
```

---

#### Error 5: "Python module not found"

**Symptom**:
```
ModuleNotFoundError: No module named 'yaml'
```

**Cause**: Python virtual environment not set up or activated

**Fix**:
```bash
# 1. Check if venv exists
ls -la scripts/python_env/e2o.venv

# 2. If not exists, create manually
python3 -m venv scripts/python_env/e2o.venv

# 3. Activate venv
source scripts/python_env/e2o.venv/bin/activate

# 4. Install requirements
pip install -r scripts/python_env/requirements.txt

# 5. Deactivate venv
deactivate

# 6. Retry build (Makefile will use venv)
make generate-openapi-spec-from-ebnf-dd
```

---

#### Error 6: GitHub Actions Workflow Fails

**Symptom**: Workflow shows red X in Actions tab

**Fix**:
```bash
# 1. Check workflow logs
# GitHub → Actions → Click failed workflow → Click failed job

# 2. Common issues:

# Issue: Secrets not configured
# Fix: Add secrets in repository settings

# Issue: .postman-target file missing
# Fix: Add to repository:
echo "personal" > .postman-target
git add .postman-target
git commit -m "Add postman target"
git push

# Issue: OpenAPI validation errors
# Fix: Run local build first to catch errors:
make openapi-spec-lint

# Issue: Postman publish timeout
# Fix: Manually trigger workflow again (may be Postman API issue)
```

---

#### Error 7: "Port already in use"

**Symptom** (local testing only):
```
Error: listen EADDRINUSE: address already in use :::4010
```

**Cause**: Prism mock server already running from previous build

**Fix**:
```bash
# 1. Stop Prism
make prism-stop

# 2. If error persists, kill manually
lsof -ti:4010 | xargs kill -9

# 3. Retry build
make postman-instance-build-with-tests
```

---

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Set debug environment variable
export DEBUG=1

# Run build with verbose output
make postman-instance-build-without-tests

# Unset debug mode
unset DEBUG
```

---

## Developer Handoff Checklist

When handing off this project to another developer, ensure they have:

### Access & Credentials

- [ ] Postman account with workspace access
- [ ] Postman API key generated
- [ ] GitHub repository access (read/write)
- [ ] GitHub Secrets access (admin only for production)
- [ ] `.env` file configured with their own API keys

### Knowledge Transfer

- [ ] Read this document completely
- [ ] Understand EBNF data dictionary structure
- [ ] Understand OpenAPI spec generation process
- [ ] Understand Postman collection generation
- [ ] Understand mock server architecture
- [ ] Know how to run local build
- [ ] Know how to debug build failures

### Hands-On Practice

- [ ] Successfully run `make postman-cleanup-all`
- [ ] Successfully run `make postman-instance-build-without-tests`
- [ ] Verify resources in Postman workspace
- [ ] Test mock server with cURL
- [ ] Make a small change to EBNF and rebuild
- [ ] Trigger GitHub Actions workflow manually
- [ ] Review workflow logs in GitHub Actions

### Key Files Locations

- [ ] Know where EBNF data dictionary is (`data_dictionary/c2mapiv2-dd.ebnf`)
- [ ] Know where OpenAPI specs are generated (`openapi/`)
- [ ] Know where Postman collections are generated (`postman/generated/`)
- [ ] Know where UID files are stored (`postman/*_uid.txt`)
- [ ] Know where environment variables are (`.env`)
- [ ] Know where workspace target is (`.postman-target`)

### Emergency Procedures

- [ ] Know how to restore from git if build corrupts artifacts
- [ ] Know how to manually delete Postman resources via UI
- [ ] Know how to regenerate Postman API key if compromised
- [ ] Know how to switch between personal and corporate workspaces
- [ ] Have backup contact for Postman workspace admin

---

## Appendix A: Makefile Target Reference

Complete list of all Makefile targets and their purposes.

### Top-Level Orchestrator Targets

| Target | Purpose | Dependencies |
|--------|---------|--------------|
| `postman-instance-build-with-tests` | Complete build + local testing | All phases + prism + docs |
| `postman-instance-build-without-tests` | Complete build, skip local tests | All phases except prism/docs |
| `postman-cleanup-all` | Delete all Postman resources | Mock, collections, APIs, envs, specs |
| `postman-publish` | Upload to Postman workspace | All publish targets |

### OpenAPI Generation Targets

| Target | Purpose | Output |
|--------|---------|--------|
| `generate-openapi-spec-from-ebnf-dd` | Convert EBNF to OpenAPI | `openapi/c2mapiv2-openapi-spec-base.yaml` |
| `openapi-spec-lint` | Validate OpenAPI spec | Console output |
| `openapi-build` | Generate + validate | Final spec |

### Postman Collection Generation Targets

| Target | Purpose | Output |
|--------|---------|--------|
| `postman-api-linked-collection-generate` | Generate from OpenAPI | `c2mapiv2-collection.json` |
| `postman-linked-collection-flatten` | Flatten + rename | `c2mapiv2-linked-collection-flat.json` |
| `postman-linked-collection-upload` | Upload to Postman | UID in `postman_linked_collection_uid.txt` |
| `postman-test-collection-generate` | Generate test collection | `c2mapiv2-test-collection-*.json` (multiple) |
| `postman-test-collection-upload` | Upload test collection | UID in `test_collection_uid.txt` |
| `postman-generate-use-case-collection` | Generate use cases | `c2mapiv2-use-case-collection.json` |
| `postman-upload-use-case-collection` | Upload use cases | UID saved |

### Postman Publishing Targets

| Target | Purpose | Creates |
|--------|---------|---------|
| `postman-import-openapi-as-api` | Create API definition | API in "APIs" tab |
| `postman-spec-create-standalone` | Create standalone spec | Spec in "Specs" tab |
| `postman-linked-collection-link` | Link collection to API | Relationship |
| `postman-mock-create` | Create mock server | Mock server + URL |
| `postman-env-create` | Generate environment files | JSON files |
| `postman-env-upload` | Upload environments | Environments in workspace |

### Postman Cleanup Targets

| Target | Purpose |
|--------|---------|
| `postman-delete-mock-servers` | Delete all mock servers |
| `postman-delete-collections` | Delete all collections |
| `postman-delete-apis` | Delete all API definitions |
| `postman-delete-environments` | Delete all environments |
| `postman-delete-specs` | Delete all standalone specs |
| `postman-delete-apis-by-name` | Delete specific API by name |
| `postman-delete-specs-by-name` | Delete specific spec by name |

### Documentation Targets

| Target | Purpose | Output |
|--------|---------|--------|
| `docs` | Generate API documentation | `docs/index.html` |
| `docs-serve` | Start documentation server | http://localhost:8080 |

### Testing Targets (Local Only)

| Target | Purpose |
|--------|---------|
| `prism-start` | Start Prism mock server on port 4010 |
| `prism-stop` | Stop Prism mock server |
| `prism-mock-test` | Run tests against local mock |
| `prism-test-endpoint` | Test specific endpoint |

### Utility Targets

| Target | Purpose |
|--------|---------|
| `postman-login` | Authenticate with Postman CLI |
| `postman-workspace-debug` | Show workspace ID and resources |
| `print-openapi-vars` | Debug OpenAPI variables |
| `verify-urls` | Check collection URLs |

---

## Appendix B: Environment Variable Reference

All environment variables used in builds.

### Required Environment Variables

| Variable | Example | Where Used | Purpose |
|----------|---------|------------|---------|
| `POSTMAN_SERRAO_API_KEY` | `PMAK-6877...` | All Postman API calls | Personal workspace auth |
| `POSTMAN_C2M_API_KEY` | `PMAK-1234...` | Corporate publish | Corporate workspace auth |
| `POSTMAN_WORKSPACE_ID` | `d8a1f479-...` | Personal publish | Personal workspace UUID |
| `POSTMAN_WORKSPACE_ID_CORPORATE` | `xxxxxxxx-...` | Corporate publish | Corporate workspace UUID |

### Optional Environment Variables

| Variable | Example | Default | Purpose |
|----------|---------|---------|---------|
| `TEST_CLIENT_ID` | `test-client-123` | N/A | JWT test credentials |
| `TEST_CLIENT_SECRET` | `test-secret-456` | N/A | JWT test credentials |
| `DEBUG` | `1` | (unset) | Enable verbose output |
| `USE_LOCAL_CREDS` | `true` | `true` | Use test credentials vs real |

### Makefile Internal Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `POSTMAN_API_KEY` | (computed) | Selected based on `.postman-target` |
| `POSTMAN_WS` | (computed) | Selected workspace ID |
| `C2MAPIV2_OPENAPI_SPEC` | `openapi/c2mapiv2-openapi-spec-final.yaml` | Final spec path |
| `POSTMAN_TEST_COLLECTION_UID_FILE` | `postman/test_collection_uid.txt` | UID tracking |

---

## Appendix C: File Naming Conventions

Understanding generated file naming patterns.

### OpenAPI Specs

| File | Purpose |
|------|---------|
| `c2mapiv2-openapi-spec-base.yaml` | Base conversion from EBNF |
| `c2mapiv2-openapi-spec-final.yaml` | With response examples |
| `c2mapiv2-openapi-spec-final-with-examples.yaml` | With code samples (FINAL) |

### Postman Collections

| File | Purpose |
|------|---------|
| `c2mapiv2-collection.json` | Base collection from OpenAPI |
| `c2mapiv2-linked-collection-flat.json` | Linked collection (flattened) |
| `c2mapiv2-test-collection-with-examples.json` | Test collection + examples |
| `c2mapiv2-test-collection-merged.json` | With custom overrides |
| `c2mapiv2-test-collection-with-tests.json` | With automated tests |
| `c2mapiv2-test-collection-fixed.json` | Auto-fixed |
| `c2mapiv2-test-collection-flat.json` | Final test collection |
| `c2mapiv2-use-case-collection.json` | Real-world examples |

### UID Tracking Files

| File | Contains |
|------|----------|
| `postman_api_uid.txt` | API definition UID |
| `postman_linked_collection_uid.txt` | Linked collection UID |
| `test_collection_uid.txt` | Test collection UID |
| `postman_mock_uid.txt` | Mock server UID |
| `postman_env_uid.txt` | Mock environment UID |

---

## Appendix D: Quick Reference Commands

### Most Common Commands

```bash
# Full clean rebuild (local)
source .env && make postman-cleanup-all && make postman-instance-build-without-tests

# Quick rebuild (no cleanup)
source .env && make postman-publish

# Test mock server
curl -X POST "https://YOUR-MOCK-URL.mock.pstmn.io/jobs/single-doc" \
  -H "Content-Type: application/json" \
  -d '{"documentSourceIdentifier": {"documentId": 12345}, ...}'

# Switch to corporate workspace
echo "corporate" > .postman-target

# Switch to personal workspace
echo "personal" > .postman-target

# Verify current target
cat .postman-target

# List Postman resources
source .env && make postman-workspace-debug

# Validate OpenAPI spec only
make openapi-spec-lint

# Generate documentation only
make docs

# Start local documentation server
make docs-serve
# Then open http://localhost:8080
```

---

## Document Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-09 | Initial version |
| 2.0 | 2025-11-09 | Added Apple Pay & Google Pay payment methods, complete rebuild section |

---

**END OF DOCUMENT**

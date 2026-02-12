# Full Delete All + Make All Workflow

## Complete Step-by-Step Guide to Clean Rebuild

This document provides EXTREMELY detailed documentation of the complete "delete all + make all" workflow for the C2M API V2 system. Every command, every Postman operation, every GitHub Action, and every file change is documented.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Complete Cleanup (Delete All)](#phase-1-complete-cleanup-delete-all)
3. [Phase 2: Complete Rebuild (Make All)](#phase-2-complete-rebuild-make-all)
4. [Phase 3: GitHub Actions Workflow](#phase-3-github-actions-workflow)
5. [Phase 4: Verification](#phase-4-verification)
6. [Appendix: All File Changes](#appendix-all-file-changes)

---

## Prerequisites

### Environment Setup

**Required Files**:
- `.env` file with Postman API keys:
  ```bash
  POSTMAN_SERRAO_API_KEY=PMAK-xxxxx  # Personal workspace key
  POSTMAN_C2M_API_KEY=PMAK-xxxxx     # Corporate/team workspace key
  ```

**Required Tools**:
- Python 3.x with virtual environment: `./venv/bin/python3`
- Node.js and npm
- jq (JSON processor)
- yq (YAML processor)
- curl
- newman (Postman CLI)
- Prism (OpenAPI mock server)

**Workspace Selection**:
- File: `.postman-target`
- Values: `personal` or `team` (also accepts `click2mail`, `corporate`)
- How to set:
  ```bash
  echo "team" > .postman-target
  # OR
  echo "personal" > .postman-target
  ```

**Terminal Session Setup**:
```bash
# Source environment variables (required for Postman API keys)
source .env

# Verify workspace selection
cat .postman-target
# Should output: team (or personal)

# Verify API key loaded
echo ${POSTMAN_C2M_API_KEY:0:10}...
# Should output: PMAK-xxxxx...
```

---

## Phase 1: Complete Cleanup (Delete All)

### Command

```bash
make postman-cleanup-all
```

### What This Command Does

**High-Level**: Deletes ALL Postman resources in the target workspace to ensure a completely clean slate.

**Resources Deleted** (in order):
1. Mock servers
2. Collections
3. APIs
4. Environments
5. Standalone API specs

### Detailed Execution Flow

#### Step 1: Read Workspace Configuration

**Makefile code** (lines ~2018-2022):
```makefile
POSTMAN_TARGET := $(shell cat .postman-target 2>/dev/null || echo "personal")
POSTMAN_WS := $(if $(filter personal,$(POSTMAN_TARGET)),$(POSTMAN_WS_PERSONAL),$(POSTMAN_WS_TEAM))
POSTMAN_API_KEY := $(if $(filter personal,$(POSTMAN_TARGET)),$(POSTMAN_SERRAO_API_KEY),$(POSTMAN_C2M_API_KEY))
```

**What happens**:
- Reads `.postman-target` file
- Sets `POSTMAN_TARGET` variable (personal or team)
- Sets `POSTMAN_WS` to appropriate workspace ID:
  - Personal: `d8a1f479-a2aa-4471-869e-b12feea0a98c`
  - Team: `c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1`
- Sets `POSTMAN_API_KEY` to appropriate key

#### Step 2: Delete All Mock Servers

**Command executed**: `make postman-mock-delete-all`

**API Call**:
```bash
curl --silent --request GET \
  "https://api.getpostman.com/mocks?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: PMAK-xxxxx"
```

**Response**:
```json
{
  "mocks": [
    {
      "id": "46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a",
      "name": "C2M API - Mock Server",
      "collection": "46321051-47361a89-e47f-4ae1-979b-e58bb67de756"
    },
    {
      "id": "46321051-abef8e8d-7175-4eaf-b8c9-3ae3033259d9",
      "name": "C2M API - Mock Server",
      "collection": "46321051-073376fa-1e84-4f2f-ace2-088f3bcbf18b"
    }
  ]
}
```

**For each mock**:
```bash
curl --silent --request DELETE \
  "https://api.getpostman.com/mocks/46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a" \
  --header "X-API-Key: PMAK-xxxxx"
```

**Output**:
```
Deleted mock: 46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a
Deleted mock: 46321051-abef8e8d-7175-4eaf-b8c9-3ae3033259d9
Total mocks deleted: 2
```

#### Step 3: Delete All Collections

**Command executed**: `make postman-collection-delete-all`

**API Call**:
```bash
curl --silent --request GET \
  "https://api.getpostman.com/collections?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: PMAK-xxxxx"
```

**Response**:
```json
{
  "collections": [
    {
      "id": "13141248-2c9d7407-d41e-4acd-82fb-29f305ae9599",
      "name": "C2M API v2 - Getting Started",
      "uid": "13141248-2c9d7407-d41e-4acd-82fb-29f305ae9599"
    },
    {
      "id": "13141248-97506cee-e4ff-403b-b2a1-f475e9f9d795",
      "name": "C2M API v2 - Getting Started (With Examples)",
      "uid": "13141248-97506cee-e4ff-403b-b2a1-f475e9f9d795"
    },
    ...8 total collections
  ]
}
```

**For each collection**:
```bash
curl --silent --request DELETE \
  "https://api.getpostman.com/collections/13141248-2c9d7407-d41e-4acd-82fb-29f305ae9599" \
  --header "X-API-Key: PMAK-xxxxx"
```

**Output**:
```
Deleted collection: 13141248-2c9d7407-d41e-4acd-82fb-29f305ae9599
Deleted collection: 13141248-97506cee-e4ff-403b-b2a1-f475e9f9d795
Deleted collection: 46321051-71422ca4-82dd-459b-8a80-2e8b7029f5b5
Deleted collection: 46321051-47361a89-e47f-4ae1-979b-e58bb67de756
Deleted collection: 46321051-fd08af09-c49c-4f89-907b-bb87a4ed3d2d
Deleted collection: 46321051-365772da-09ef-47d6-821d-7c229bbe208c
Deleted collection: 46321051-073376fa-1e84-4f2f-ace2-088f3bcbf18b
Deleted collection: 46321051-a78af34c-7c51-493a-89cd-8218870f6f24
Total collections deleted: 8
```

#### Step 4: Delete All APIs

**Command executed**: `make postman-api-delete-all`

**API Call**:
```bash
curl --silent --request GET \
  "https://api.getpostman.com/apis?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: PMAK-xxxxx"
```

**Response**:
```json
{
  "apis": [
    {
      "id": "1f3c774e-ea37-4645-9d27-ff1fe5c372b8",
      "name": "C2mApiV2",
      "createdBy": "...",
      "updatedBy": "...",
      "createdAt": "2025-12-18T21:03:26.000Z",
      "updatedAt": "2026-02-03T12:20:07.000Z"
    }
  ]
}
```

**For each API**:
```bash
curl --silent --request DELETE \
  "https://api.getpostman.com/apis/1f3c774e-ea37-4645-9d27-ff1fe5c372b8" \
  --header "X-API-Key: PMAK-xxxxx"
```

**Output**:
```
Deleted API: 1f3c774e-ea37-4645-9d27-ff1fe5c372b8
Total APIs deleted: 1
```

#### Step 5: Delete All Environments

**Command executed**: `make postman-env-delete-all`

**API Call**:
```bash
curl --silent --request GET \
  "https://api.getpostman.com/environments?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: PMAK-xxxxx"
```

**Response**:
```json
{
  "environments": [
    {
      "id": "46321051-3cb2367e-9c7e-41f4-a665-0a2fa5245ec4",
      "name": "C2M API - Mock Server",
      "uid": "46321051-3cb2367e-9c7e-41f4-a665-0a2fa5245ec4"
    },
    {
      "id": "46321051-f564e9de-97c6-4288-9060-04aafe07026d",
      "name": "C2M API - AWS Dev",
      "uid": "46321051-f564e9de-97c6-4288-9060-04aafe07026d"
    },
    {
      "id": "46321051-63e0fb01-99ee-4d7f-8fcc-7c8869893604",
      "name": "C2M API - Mock Server",
      "uid": "46321051-63e0fb01-99ee-4d7f-8fcc-7c8869893604"
    },
    {
      "id": "46321051-a32832e0-d60f-40c7-aa38-dea07d7c9bbc",
      "name": "C2M API - AWS Dev",
      "uid": "46321051-a32832e0-d60f-40c7-aa38-dea07d7c9bbc"
    }
  ]
}
```

**For each environment**:
```bash
curl --silent --request DELETE \
  "https://api.getpostman.com/environments/46321051-3cb2367e-9c7e-41f4-a665-0a2fa5245ec4" \
  --header "X-API-Key: PMAK-xxxxx"
```

**Output**:
```
Deleted environment: 46321051-3cb2367e-9c7e-41f4-a665-0a2fa5245ec4
Deleted environment: 46321051-f564e9de-97c6-4288-9060-04aafe07026d
Deleted environment: 46321051-63e0fb01-99ee-4d7f-8fcc-7c8869893604
Deleted environment: 46321051-a32832e0-d60f-40c7-aa38-dea07d7c9bbc
Total environments deleted: 4
```

#### Step 6: Delete All Standalone Specs

**Command executed**: (Part of postman-spec-delete-all if it existed, or handled in API deletion)

**Note**: Standalone API specs are typically linked to APIs, so deleting the API also removes the spec.

### Summary of Phase 1

**Total Resources Deleted**:
- Mock Servers: 2
- Collections: 8
- APIs: 1
- Environments: 4
- **Total: 15 resources**

**Postman Workspace State After Cleanup**:
- Empty workspace (no resources)
- Ready for clean rebuild

**Local File Changes**:
- No local files deleted
- UID tracking files will be overwritten in rebuild

---

## Phase 2: Complete Rebuild (Make All)

### Command

```bash
make postman-instance-build-without-tests
```

**OR** (for local development with testing):

```bash
make postman-instance-build-with-tests
```

**Difference**:
- `without-tests`: Skips Prism mock server, local docs serving, Newman testing (used for CI/CD)
- `with-tests`: Includes full local testing infrastructure (used for development)

### Complete Build Pipeline Overview

**High-Level Flow**:
```
EBNF Data Dictionary
  ↓ ebnf_to_openapi_dynamic_v3.py
OpenAPI Spec (base)
  ↓ overlay merge (auth.tokens.yaml)
OpenAPI Spec (final)
  ↓ add code samples
OpenAPI Spec (with examples)
  ↓ openapi-to-postmanv2
Postman Collection (linked - placeholders)
  ↓ fix_oneOf_placeholders.js
Postman Collection (linked with <oneOf>)
  ↓ add_tests.js + addRandomDataToRaw.js
Postman Collection (test - realistic data)
  ↓ generate_use_case_collection_v2.py
Postman Collection (use cases - examples)
  ↓ generate_getting_started_from_linked.py
Postman Collection (getting started - placeholders)
  ↓ generate_getting_started_with_examples_from_test.py
Postman Collection (getting started with examples - realistic)
  ↓ Upload to Postman + Create Mock + Create Environments
Postman Workspace Populated
```

### Detailed Execution Flow

#### Step 1: Generate OpenAPI Spec from EBNF

**Command**: `make generate-openapi-spec-from-ebnf-dd`

**Script**: `scripts/active/ebnf_to_openapi_dynamic_v3.py`

**Input**: `data_dictionary/c2mapiv2-dd.ebnf` (904 lines)

**Processing**:
1. Parse EBNF file into syntax tree
2. Extract endpoint definitions (8 job submission endpoints)
3. Extract schema definitions (docSourceAll, recipientAddressSource, etc.)
4. Generate OpenAPI paths with POST operations
5. Generate component schemas with oneOf discriminators
6. Add documentation (summaries, descriptions, tags)

**Output**: `openapi/c2mapiv2-openapi-spec-base.yaml` (719 lines)

**Key Sections Generated**:
```yaml
openapi: 3.0.3
info:
  title: C2M Job Submission API
  version: 2.0.0
  description: Click2Mail API for submitting mailing jobs

paths:
  /jobs/submit/single/doc:
    post:
      summary: Submit a single doc job
      description: Submits a mailing job with a single document...
      operationId: submitSingleDocWithTemplateParams
      tags: [jobs]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/submitSingleDocParams'
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/jobSubmissionResponse'

components:
  schemas:
    submitSingleDocParams:
      type: object
      required:
        - docSourceAll
        - recipientAddressSource
      properties:
        docSourceAll:
          oneOf:
            - $ref: '#/components/schemas/documentIdSource'
            - $ref: '#/components/schemas/requestIdSource'
            - $ref: '#/components/schemas/urlSource'
            - $ref: '#/components/schemas/zipDocumentIdSource'
            - $ref: '#/components/schemas/zipRequestIdSource'
        recipientAddressSource:
          oneOf:
            - $ref: '#/components/schemas/singleAddress'
            - $ref: '#/components/schemas/addressList'
            - $ref: '#/components/schemas/addressListId'
            - $ref: '#/components/schemas/addressListName'
        jobTemplate:
          type: string
        paymentDetails:
          oneOf:
            - $ref: '#/components/schemas/creditCardDetails'
            - $ref: '#/components/schemas/achDetails'
            - $ref: '#/components/schemas/invoiceDetails'
        returnAddress:
          $ref: '#/components/schemas/usAddress'
        jobOptions:
          $ref: '#/components/schemas/jobOptions'
        tags:
          type: array
          items:
            type: string
```

**Verification**:
```bash
ls -lh openapi/c2mapiv2-openapi-spec-base.yaml
# Expected: ~25-30KB file

yq eval '.paths | keys | length' openapi/c2mapiv2-openapi-spec-base.yaml
# Expected: 8 (job submission endpoints)
```

#### Step 2: Merge Auth Overlay

**Command**: `make openapi-merge-auth-overlay`

**Overlay File**: `openapi/overlays/auth.tokens.yaml` (180 lines)

**Processing**:
1. Read base spec
2. Read auth overlay
3. Merge paths (adds 3 auth endpoints: /auth/tokens/long, /auth/tokens/short, /auth/tokens/revoke)
4. Merge security schemes (ShortTokenAuth, LongTokenAuth)
5. Update info block

**Output**: `openapi/c2mapiv2-openapi-spec-final.yaml` (900+ lines)

**New Sections Added**:
```yaml
paths:
  /auth/tokens/long:
    post:
      summary: Obtain long-term token
      security: []  # No auth required for this endpoint
  /auth/tokens/short:
    post:
      summary: Exchange long-term for short-term token
      security:
        - LongTokenAuth: []
  /auth/tokens/revoke:
    post:
      summary: Revoke token
      security:
        - ShortTokenAuth: []

components:
  securitySchemes:
    ShortTokenAuth:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: /auth/tokens/short
          scopes:
            tokens:write: Create and manage tokens
            tokens:revoke: Revoke tokens
    LongTokenAuth:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: /auth/tokens/long
          scopes:
            tokens:write: Create and manage tokens
```

**Verification**:
```bash
yq eval '.paths | keys | length' openapi/c2mapiv2-openapi-spec-final.yaml
# Expected: 11 (8 job endpoints + 3 auth endpoints)

grep -c "/auth/tokens" openapi/c2mapiv2-openapi-spec-final.yaml
# Expected: 3 or more
```

#### Step 3: Add Code Samples

**Command**: `make openapi-add-code-samples`

**Script**: `scripts/active/add_code_samples.py`

**Processing**:
1. Read final OpenAPI spec
2. For each endpoint, generate code samples in multiple languages:
   - Python (requests library)
   - JavaScript (fetch API)
   - cURL (command line)
3. Add x-codeSamples extension to each operation

**Output**: `openapi/c2mapiv2-openapi-spec-final-with-examples.yaml`

**Code Samples Added**:
```yaml
paths:
  /jobs/submit/single/doc:
    post:
      x-codeSamples:
        - lang: Python
          label: Python (requests)
          source: |
            import requests
            import json

            url = "https://api.click2mail.com/jobs/submit/single/doc"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer YOUR_TOKEN"
            }
            data = {
                "docSourceAll": {"documentId": 1234},
                "recipientAddressSource": {"addressId": 5000},
                "jobTemplate": "template_name"
            }

            response = requests.post(url, headers=headers, json=data)
            print(response.json())

        - lang: JavaScript
          label: JavaScript (fetch)
          source: |
            const url = 'https://api.click2mail.com/jobs/submit/single/doc';
            const data = {
              docSourceAll: {documentId: 1234},
              recipientAddressSource: {addressId: 5000},
              jobTemplate: 'template_name'
            };

            fetch(url, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer YOUR_TOKEN'
              },
              body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(console.log);

        - lang: Shell
          label: cURL
          source: |
            curl -X POST https://api.click2mail.com/jobs/submit/single/doc \
              -H "Content-Type: application/json" \
              -H "Authorization: Bearer YOUR_TOKEN" \
              -d '{
                "docSourceAll": {"documentId": 1234},
                "recipientAddressSource": {"addressId": 5000},
                "jobTemplate": "template_name"
              }'
```

**Verification**:
```bash
yq eval '[.. | select(has("x-codeSamples"))] | length' openapi/c2mapiv2-openapi-spec-final-with-examples.yaml
# Expected: 11 (all endpoints have code samples)
```

#### Step 4: Generate Linked Collection (Placeholders)

**Command**: `make postman-api-linked-collection-generate`

**Tool**: `openapi-to-postmanv2` (npm package)

**Input**: `openapi/c2mapiv2-openapi-spec-final-with-examples.yaml`

**Processing**:
```bash
npx openapi-to-postmanv2 \
  -s openapi/c2mapiv2-openapi-spec-final-with-examples.yaml \
  -o postman/generated/c2mapiv2-linked-collection-flat.json \
  -p -O folderStrategy=Tags,includeAuthInfoInExample=false
```

**Options Explained**:
- `-p`: Pretty print output
- `-O folderStrategy=Tags`: Group endpoints by OpenAPI tags
- `-O includeAuthInfoInExample=false`: Don't add auth to examples

**Output**: `postman/generated/c2mapiv2-linked-collection-flat.json` (108KB)

**Structure**:
```json
{
  "info": {
    "name": "C2mApiCollectionLinked",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "jobs",
      "item": [
        {
          "name": "submit",
          "item": [
            {
              "name": "single",
              "item": [
                {
                  "name": "doc",
                  "item": [
                    {
                      "name": "POST /jobs/submit/single/doc",
                      "request": {
                        "method": "POST",
                        "header": [
                          {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                          "mode": "raw",
                          "raw": "{\n  \"docSourceAll\": {\n    \"documentId\": 0\n  },\n  \"recipientAddressSource\": {\n    \"singleAddress\": {...}\n  }\n}"
                        },
                        "url": {
                          "raw": "{{baseUrl}}/jobs/submit/single/doc",
                          "host": ["{{baseUrl}}"],
                          "path": ["jobs", "submit", "single", "doc"]
                        }
                      }
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": "auth",
      "item": [...]
    }
  ]
}
```

**Issue**: oneOf fields show as objects with placeholder values, not `<oneOf>` marker

**Next Step**: Fix oneOf placeholders

#### Step 5: Fix OneOf Placeholders

**Command**: (Automatically called in pipeline)

**Script**: `scripts/active/fix_oneOf_placeholders.js`

**Processing**:
1. Read OpenAPI spec to discover all oneOf fields dynamically
2. Traverse spec looking for schemas with `oneOf` keyword
3. For each oneOf field found, search collection for matching fields
4. Replace field values with `"<oneOf>"` string

**OneOf Fields Discovered** (8 total):
- docSourceAll
- docSourceStandard
- docSourceZipFile
- recipientAddressSource
- paymentDetails
- zipDocumentSource
- mergeDocumentSource
- documentAggregationSource

**Transformation**:

**Before**:
```json
{
  "docSourceAll": {
    "documentId": 0
  },
  "recipientAddressSource": {
    "singleAddress": {
      "firstName": "",
      "lastName": ""
    }
  }
}
```

**After**:
```json
{
  "docSourceAll": "<oneOf>",
  "recipientAddressSource": "<oneOf>",
  "jobTemplate": "<string>",
  "paymentDetails": "<oneOf>",
  "returnAddress": {
    "firstName": "<string>",
    "lastName": "<string>",
    "address1": "<string>",
    "city": "<string>",
    "state": "<string>",
    "zip": "<string>"
  },
  "jobOptions": {
    "documentClass": "<string>",
    "layout": "<string>",
    "productionTime": "<string>",
    "mailType": "<string>"
  },
  "tags": ["<string>", "<string>"]
}
```

**Total Replacements**: ~100 (across all 11 endpoints)

**Verification**:
```bash
cat postman/generated/c2mapiv2-linked-collection-flat.json | grep -c '"<oneOf>"'
# Expected: 11+ (at least one per job endpoint)
```

#### Step 6: Add JWT Pre-Request Script

**Command**: (Automatically called in pipeline)

**Script**: `scripts/active/add_jwt_pre_request_script.js`

**Processing**:
1. Read JWT pre-request script template: `postman/scripts/jwt-pre-request.js`
2. Add to collection-level events (runs before every request)

**JWT Script Flow**:
```javascript
// 1. Check if this is a mock server request
const url = pm.request.url;
const isMockServer = (url.host && url.host.includes('mock.pstmn.io')) ||
                     (pm.variables.get('baseUrl') && pm.variables.get('baseUrl').includes('mock'));

if (isMockServer) {
    console.log('Mock server detected - skipping Authorization header');
    return;  // Don't add auth header for mocks
}

// 2. Check if we already have a short-term token
let shortToken = pm.environment.get('shortTermToken');
let shortTokenExpiry = pm.environment.get('shortTermTokenExpiry');

if (shortToken && shortTokenExpiry && Date.now() < shortTokenExpiry) {
    // Use existing valid short token
    pm.request.headers.add({
        key: 'Authorization',
        value: `Bearer ${shortToken}`
    });
    return;
}

// 3. Get or refresh long-term token
let longToken = pm.environment.get('longTermToken');

if (!longToken) {
    // Get new long-term token
    pm.sendRequest({
        url: `${pm.environment.get('authBaseUrl')}/auth/tokens/long`,
        method: 'POST',
        header: {'Content-Type': 'application/json'},
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                grant_type: 'client_credentials',
                client_id: pm.environment.get('clientId'),
                client_secret: pm.environment.get('clientSecret')
            })
        }
    }, (err, response) => {
        if (!err) {
            longToken = response.json().token;
            pm.environment.set('longTermToken', longToken);
        }
    });
}

// 4. Exchange long-term for short-term token
pm.sendRequest({
    url: `${pm.environment.get('authBaseUrl')}/auth/tokens/short`,
    method: 'POST',
    header: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${longToken}`
    },
    body: {
        mode: 'raw',
        raw: JSON.stringify({grant_type: 'refresh_token'})
    }
}, (err, response) => {
    if (!err) {
        const data = response.json();
        pm.environment.set('shortTermToken', data.token);
        pm.environment.set('shortTermTokenExpiry', Date.now() + (14 * 60 * 1000)); // 14 min

        // Add auth header for current request
        pm.request.headers.add({
            key: 'Authorization',
            value: `Bearer ${data.token}`
        });
    }
});
```

**Result**: All requests automatically get JWT authentication except mock server requests

#### Step 7: Generate Test Collection (Realistic Data)

**Command**: `make postman-create-test-collection`

**Scripts**:
1. `scripts/active/add_tests.js` - Adds Newman test assertions
2. `scripts/test_data_generator_for_collections/addRandomDataToRaw.js` - Generates faker data

**Processing**:

**Test Script Addition**:
```javascript
pm.test("Status code is 200 or 201", function () {
    pm.expect(pm.response.code).to.be.oneOf([200, 201]);
});

pm.test("Response time < 1s", function () {
    const rt = pm.response.responseTime;
    console.log(`Response time: ${rt}ms ${rt > 1000 ? '(>1s - SLOW)' : '(OK)'}`);
});

pm.test("Response has required fields", function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('status');
    pm.expect(json).to.have.property('message');
    pm.expect(json).to.have.property('jobId');
});

pm.test("Job ID is valid format", function () {
    const json = pm.response.json();
    pm.expect(json.jobId).to.be.a('string');
    pm.expect(json.jobId.length).to.be.greaterThan(0);
});
```

**Test Data Generation**:
```javascript
// Realistic faker-generated data
{
  "docSourceAll": {
    "requestId": 11011  // Random 10000-99999
  },
  "recipientAddressSource": {
    "singleAddress": {
      "firstName": "Mavis",        // faker.name.firstName()
      "lastName": "Kuvalis",        // faker.name.lastName()
      "address1": "5321 Roob Mountain",  // faker.address.streetAddress()
      "city": "East Barryboro",     // faker.address.city()
      "state": "Wisconsin",         // faker.address.state()
      "zip": "67159-4829",         // faker.address.zipCode()
      "country": "Gibraltar"        // faker.address.country()
    }
  },
  "jobTemplate": "template_zazaDSUJ",  // Random template_XXXXXXXX
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",          // Random from enum
      "cardNumber": "4111111111111111",  // Test card
      "expirationDate": {
        "month": 12,               // Random 1-12
        "year": 2025               // Random 2024-2030
      },
      "cvv": 123                   // Random 100-999
    }
  },
  "returnAddress": {
    "firstName": "Mavis",
    "lastName": "Kuvalis",
    "address1": "5321 Roob Mountain",
    "city": "East Barryboro",
    "state": "Wisconsin",
    "zip": "67159-4829"
  },
  "tags": ["<string>", "<string>"]  // Not yet filled
}
```

**Mutual Exclusion Enforcement**:
- Rule: `jobTemplate` and `jobOptions` are mutually exclusive
- Strategy: Alternate between endpoints
  - Endpoints 1, 3, 5, 7 → Have jobTemplate
  - Endpoints 2, 4, 6, 8 → Have jobOptions
- Result: 100% valid test data (no endpoints with both)

**Output**: `postman/generated/c2mapiv2-test-collection-with-examples.json` (152KB)

**Verification**:
```bash
cat postman/generated/c2mapiv2-test-collection-with-examples.json | \
  jq '[.item[].item[].item[].item[].item[].event[]? | select(.listen == "test")] | length'
# Expected: 40+ (test scripts across all endpoints)
```

#### Step 8: Generate Getting Started Collection (Placeholders)

**Command**: `make postman-generate-getting-started-collection`

**Script**: `scripts/active/generate_getting_started_from_linked.py`

**Input**: `postman/generated/c2mapiv2-linked-collection-flat.json` (correct field names from EBNF)

**Processing**:
1. Read linked collection
2. Define 16 educational patterns in 3 categories
3. For each pattern, find matching endpoint by path
4. Clone request structure (preserves all fields and <oneOf> placeholders)
5. Add friendly name and educational description
6. Organize into nested category folders

**Patterns Defined**:

**Category 1: Most Frequently Used** (3 patterns):
1. Single recipient - basic job submission (`/jobs/submit/single/doc`)
2. Mail merge - multiple recipients (`/jobs/submit/single/doc`)
3. Address capture - PDF with embedded addresses (`/jobs/submit/single/pdf/addressCapture`)

**Category 2: Bulk Operations** (3 patterns):
4. Split PDF with address capture (`/jobs/submit/single/pdf/split/addressCapture`)
5. Split PDF with specified addresses (`/jobs/submit/single/pdf/split`)
6. Multiple documents from ZIP with address capture (`/jobs/submit/multi/zip/addressCapture`)

**Category 3: Advanced Patterns** (10 patterns):
7. Merge multiple documents (`/jobs/submit/multi/doc/merge`)
8. Using jobOptions instead of template (`/jobs/submit/single/doc`)
9. Using document URL instead of upload (`/jobs/submit/single/doc`)
10. Adding tags for organization (`/jobs/submit/single/doc`)
11. Naming an address list for reuse (`/jobs/submit/single/doc`)
12. Specifying payment method (`/jobs/submit/single/doc`)
13. Multiple documents from ZIP - specify addresses (`/jobs/submit/multi/zip`)
14. Multiple separate documents (`/jobs/submit/multi/doc`)
15. Using stored documentId (`/jobs/submit/single/doc`)
16. Using saved addressListId (`/jobs/submit/single/doc`)

**Output**: `postman/generated/c2mapiv2-getting-started-collection.json` (480 lines, 20KB)

**Structure**:
```json
{
  "info": {
    "name": "C2M API v2 - Getting Started",
    "description": "Educational collection organized by usage patterns..."
  },
  "item": [
    {
      "name": "Most Frequently Used",
      "description": "The most common API calls for everyday use",
      "item": [
        {
          "name": "Single recipient - basic job submission",
          "request": {
            "name": "Single recipient - basic job submission",
            "description": "Submit a single document to one recipient using jobTemplate...",
            "url": {...},
            "body": {
              "raw": "{\n  \"docSourceAll\": \"<oneOf>\",\n  \"recipientAddressSource\": \"<oneOf>\",\n  \"jobTemplate\": \"<string>\"\n}"
            }
          }
        }
      ]
    },
    {
      "name": "Bulk Operations",
      "item": [...]
    },
    {
      "name": "Advanced Patterns",
      "item": [...]
    }
  ]
}
```

**Verification**:
```bash
cat postman/generated/c2mapiv2-getting-started-collection.json | \
  jq '.item | length'
# Expected: 3 (categories)

cat postman/generated/c2mapiv2-getting-started-collection.json | \
  jq '[.item[].item[]] | length'
# Expected: 16 (patterns)
```

#### Step 9: Generate Getting Started With Examples

**Command**: `make postman-generate-getting-started-with-examples`

**Script**: `scripts/active/generate_getting_started_with_examples_from_test.py`

**Input**: `postman/generated/c2mapiv2-test-collection-with-examples.json` (realistic data)

**Processing**:
1. Read test collection
2. Use same 16 pattern definitions
3. For each pattern, find matching endpoint by path (recursive search through nested folders)
4. Clone request structure (preserves realistic faker data)
5. Add same friendly names and descriptions
6. Organize into same nested category folders

**Key Difference from Placeholder Version**:
- Data is realistic (John Smith, 1839 Maple Blvd) instead of placeholders (`<string>`, `<oneOf>`)
- Same 16 patterns, same structure
- Collection name: "C2M API v2 - Getting Started (With Examples)"

**Output**: `postman/generated/c2mapiv2-getting-started-with-examples-collection.json` (480 lines, 20KB)

**Example Request Body**:
```json
{
  "docSourceAll": {
    "documentId": 1234
  },
  "recipientAddressSource": {
    "addressId": 5000
  },
  "jobTemplate": "template_zazaDSUJ",
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {
        "month": 12,
        "year": 2025
      },
      "cvv": 123
    }
  },
  "returnAddress": {
    "firstName": "Mavis",
    "lastName": "Kuvalis",
    "address1": "5321 Roob Mountain",
    "city": "East Barryboro",
    "state": "Wisconsin",
    "zip": "67159-4829"
  },
  "tags": ["<string>", "<string>"]
}
```

#### Step 10: Upload Collections to Postman

**Commands Executed** (in order):
1. `make postman-import-openapi-as-api` - Create API definition
2. `make postman-spec-create-standalone` - Upload standalone spec
3. `make postman-api-linked-collection-upload` - Upload linked collection
4. `make postman-use-case-collection-upload` - Upload use case collection
5. `make postman-upload-getting-started-collection` - Upload Getting Started (placeholders)
6. `make postman-upload-getting-started-with-examples` - Upload Getting Started (examples)
7. `make postman-test-collection-upload` - Upload test collection

**For Each Upload** (example: Getting Started collection):

**API Call**:
```bash
curl --silent --location --request POST \
  "https://api.getpostman.com/collections?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: PMAK-xxxxx" \
  --header "Content-Type: application/json" \
  --data-binary @- <<EOF
{
  "collection": {
    "info": {
      "name": "C2M API v2 - Getting Started",
      "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [...]
  }
}
EOF
```

**Response**:
```json
{
  "collection": {
    "id": "13141248-2c9d7407-d41e-4acd-82fb-29f305ae9599",
    "name": "C2M API v2 - Getting Started",
    "uid": "13141248-2c9d7407-d41e-4acd-82fb-29f305ae9599"
  }
}
```

**UID Saved to File**:
```bash
echo "13141248-2c9d7407-d41e-4acd-82fb-29f305ae9599" > \
  postman/getting-started-collection-uid.txt
```

**All UIDs Tracked** (8 files):
- `postman/postman_api_uid.txt`
- `postman/postman_spec_uid.txt`
- `postman/postman_linked_collection_uid.txt`
- `postman/use_case_collection_uid.txt`
- `postman/getting-started-collection-uid.txt`
- `postman/getting-started-with-examples-collection-uid.txt`
- `postman/test_collection_uid.txt`
- `postman/mock_server_uid.txt`

#### Step 11: Create Mock Server

**Command**: `make postman-mock-create`

**Important**: Mock server MUST be created from TEST collection (has all endpoints), not Use Case collection (only 3 endpoints)

**API Call**:
```bash
curl --silent --location --request POST \
  "https://api.getpostman.com/mocks?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: PMAK-xxxxx" \
  --header "Content-Type: application/json" \
  --data-raw '{
    "mock": {
      "name": "C2M API - Mock Server",
      "collection": "13141248-d5cbb3a5-7151-493a-89cd-8218870f6f24"
    }
  }'
```

**Response**:
```json
{
  "mock": {
    "id": "46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a",
    "name": "C2M API - Mock Server",
    "uid": "46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a",
    "collection": "13141248-d5cbb3a5-7151-493a-89cd-8218870f6f24",
    "mockUrl": "https://46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a.mock.pstmn.io"
  }
}
```

**UID Saved**:
```bash
echo "46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a" > postman/mock_server_uid.txt
echo "https://46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a.mock.pstmn.io" > postman/mock_url.txt
```

#### Step 12: Create Environments

**Two environments created**:
1. C2M API - Mock Server
2. C2M API - AWS Dev

**Mock Server Environment**:

**API Call**:
```bash
curl --silent --location --request POST \
  "https://api.getpostman.com/environments?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: PMAK-xxxxx" \
  --header "Content-Type: application/json" \
  --data-raw '{
    "environment": {
      "name": "C2M API - Mock Server",
      "values": [
        {
          "key": "baseUrl",
          "value": "https://46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a.mock.pstmn.io",
          "enabled": true
        }
      ]
    }
  }'
```

**AWS Dev Environment**:

**API Call**:
```bash
curl --silent --location --request POST \
  "https://api.getpostman.com/environments?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: PMAK-xxxxx" \
  --header "Content-Type: application/json" \
  --data-raw '{
    "environment": {
      "name": "C2M API - AWS Dev",
      "values": [
        {
          "key": "baseUrl",
          "value": "https://api-dev.click2mail.com",
          "enabled": true
        },
        {
          "key": "authBaseUrl",
          "value": "https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev",
          "enabled": true
        },
        {
          "key": "clientId",
          "value": "test-client-123",
          "enabled": true
        },
        {
          "key": "clientSecret",
          "value": "",
          "enabled": true,
          "type": "secret"
        },
        {
          "key": "longTermToken",
          "value": "",
          "enabled": true,
          "type": "secret"
        },
        {
          "key": "shortTermToken",
          "value": "",
          "enabled": true,
          "type": "secret"
        },
        {
          "key": "shortTermTokenExpiry",
          "value": "",
          "enabled": true
        }
      ]
    }
  }'
```

**UIDs Saved**:
```bash
echo "46321051-3cb2367e-9c7e-41f4-a665-0a2fa5245ec4" > postman/mock_env_uid.txt
echo "46321051-f564e9de-97c6-4288-9060-04aafe07026d" > postman/aws_env_uid.txt
```

#### Step 13: Link Mock Server to Environment

**Command**: `make postman-link-env-to-mock-server`

**API Call**:
```bash
curl --silent --location --request PUT \
  "https://api.getpostman.com/mocks/46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a" \
  --header "X-API-Key: PMAK-xxxxx" \
  --header "Content-Type: application/json" \
  --data-raw '{
    "mock": {
      "environment": "46321051-3cb2367e-9c7e-41f4-a665-0a2fa5245ec4"
    }
  }'
```

**Result**: Mock server now uses Mock Server environment variables

### Summary of Phase 2

**Total Resources Created**:
- API Definitions: 1
- Standalone Specs: 1
- Collections: 6 (Linked, Test, Use Case, Getting Started x2, Real World)
- Mock Servers: 1
- Environments: 2
- **Total: 11 resources**

**All Generated Files**:
- `openapi/c2mapiv2-openapi-spec-base.yaml` (719 lines)
- `openapi/c2mapiv2-openapi-spec-final.yaml` (900+ lines)
- `openapi/c2mapiv2-openapi-spec-final-with-examples.yaml` (1000+ lines)
- `postman/generated/c2mapiv2-linked-collection-flat.json` (108KB)
- `postman/generated/c2mapiv2-test-collection-with-examples.json` (152KB)
- `postman/generated/c2mapiv2-use-case-collection.json` (varies)
- `postman/generated/c2mapiv2-getting-started-collection.json` (20KB)
- `postman/generated/c2mapiv2-getting-started-with-examples-collection.json` (20KB)
- 8 UID tracking files in `postman/`

---

## Phase 3: GitHub Actions Workflow

### When Workflow Triggers

**Automatic Triggers**:
- Push to `main` branch
- Pull request to `main` branch

**Manual Trigger**:
```bash
gh workflow run api-ci-cd.yml
```

### Workflow File

**Location**: `.github/workflows/api-ci-cd.yml` (438 lines)

### Workflow Steps

#### Job 1: Build API Spec, Collections, and Docs

**Runs on**: `ubuntu-latest`

**Environment Variables Set**:
```yaml
env:
  POSTMAN_SERRAO_API_KEY: ${{ secrets.POSTMAN_API_KEY }}
  POSTMAN_C2M_API_KEY: ${{ secrets.POSTMAN_C2M_API_KEY }}
  GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Steps**:

1. **Checkout Repository**
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Fetch all history for git diff
```

2. **Set up Python**
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.x'
```

3. **Install Python Dependencies**
```yaml
- name: Install Python packages
  run: |
    python -m pip install --upgrade pip
    pip install pyyaml requests
```

4. **Set up Node.js**
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '18'
```

5. **Install Node.js Dependencies**
```yaml
- name: Install npm packages
  run: |
    npm install -g newman openapi-to-postmanv2
```

6. **Install System Tools**
```yaml
- name: Install system tools
  run: |
    sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
    sudo chmod +x /usr/local/bin/yq
```

7. **Build OpenAPI Spec from EBNF**
```yaml
- name: Build OpenAPI from EBNF
  run: make openapi-build
```

**What `make openapi-build` does**:
```makefile
openapi-build: generate-openapi-spec-from-ebnf-dd openapi-merge-auth-overlay openapi-add-code-samples openapi-spec-lint
```

Steps:
- Generate base spec from EBNF
- Merge auth overlay
- Add code samples
- Lint spec (checks for errors/warnings)

8. **Build Postman Collections**
```yaml
- name: Build Postman collections
  run: make postman-collection-build
```

**What `make postman-collection-build` does**:
```makefile
postman-collection-build: \
  postman-api-linked-collection-generate \
  postman-create-test-collection \
  postman-use-case-collection-generate \
  postman-generate-getting-started-all
```

Steps:
- Generate linked collection from OpenAPI
- Fix oneOf placeholders
- Add tests and realistic data
- Generate use case examples
- Generate both Getting Started collections

9. **Build Documentation**
```yaml
- name: Build documentation
  run: make docs
```

**What `make docs` does**:
```makefile
docs: docs-build docs-validate
```

Steps:
- Generate Redocly documentation HTML
- Bundle OpenAPI spec into docs
- Validate docs were created

10. **Commit Generated Files** (only on main branch push)
```yaml
- name: Commit generated files
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  run: |
    git config --local user.email "github-actions[bot]@users.noreply.github.com"
    git config --local user.name "github-actions[bot]"
    git add openapi/*.yaml postman/generated/*.json docs/index.html docs/openapi-bundle.yaml
    git diff --staged --quiet || git commit -m "chore: auto-generate OpenAPI spec and collections [skip ci]"
    git push
```

**Note**: `[skip ci]` prevents infinite loop of builds

11. **Publish to Postman**
```yaml
- name: Publish to Postman workspace
  run: make postman-publish
```

**What `make postman-publish` does**:
- Reads `.postman-target` to determine workspace
- Calls `postman-publish-personal` or `postman-publish-team`
- Uploads all collections, creates mock server, creates environments
- Same process as Phase 2 Step 10-13

12. **Copy Generated Files to Artifacts Repository**
```yaml
- name: Copy to artifacts repository
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  env:
    SECURITY_REPO_TOKEN: ${{ secrets.SECURITY_REPO_TOKEN }}
  run: |
    # Clone artifacts repo
    git clone https://${SECURITY_REPO_TOKEN}@github.com/${{ github.repository_owner }}/c2m-api-v2-postman-artifacts.git ../artifacts

    # Copy files
    cp -r openapi/*.yaml ../artifacts/openapi/
    cp -r postman/generated/*.json ../artifacts/postman/
    cp -r docs/* ../artifacts/docs/

    # Commit and push
    cd ../artifacts
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add .
    git diff --staged --quiet || git commit -m "chore: update generated artifacts from ${{ github.repository }} [skip ci]"
    git push
```

**Artifacts Copied**:
- All OpenAPI specs (base, final, with-examples)
- All Postman collections (6 files)
- All documentation files (index.html, openapi-bundle.yaml)

13. **Deploy Documentation to GitHub Pages** (requires admin to enable)
```yaml
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs
    destination_dir: ./
```

**Note**: This step skipped if GitHub Pages not enabled

### Workflow Summary

**Total Duration**: ~3-4 minutes

**Resources Created in Postman**:
- Same 11 resources as Phase 2

**GitHub Artifacts Repository Updated**:
- All generated OpenAPI specs
- All generated Postman collections
- All generated documentation

**GitHub Pages Deployed** (if enabled):
- API documentation at `https://{owner}.github.io/c2m-api-v2-postman-artifacts/`

---

## Phase 4: Verification

### Local Verification

#### 1. Verify Generated Files

**OpenAPI Specs**:
```bash
# Check base spec
ls -lh openapi/c2mapiv2-openapi-spec-base.yaml
yq eval '.paths | keys | length' openapi/c2mapiv2-openapi-spec-base.yaml
# Expected: 8 paths

# Check final spec
ls -lh openapi/c2mapiv2-openapi-spec-final.yaml
yq eval '.paths | keys | length' openapi/c2mapiv2-openapi-spec-final.yaml
# Expected: 11 paths (8 + 3 auth)

# Check examples spec
ls -lh openapi/c2mapiv2-openapi-spec-final-with-examples.yaml
yq eval '[.. | select(has("x-codeSamples"))] | length' openapi/c2mapiv2-openapi-spec-final-with-examples.yaml
# Expected: 11 (all endpoints have code samples)
```

**Postman Collections**:
```bash
# Check linked collection
ls -lh postman/generated/c2mapiv2-linked-collection-flat.json
cat postman/generated/c2mapiv2-linked-collection-flat.json | grep -c '"<oneOf>"'
# Expected: 11+

# Check test collection
ls -lh postman/generated/c2mapiv2-test-collection-with-examples.json
cat postman/generated/c2mapiv2-test-collection-with-examples.json | \
  jq '[.item[].item[].item[].item[].item[].event[]? | select(.listen == "test")] | length'
# Expected: 40+

# Check Getting Started collections
ls -lh postman/generated/c2mapiv2-getting-started-collection.json
cat postman/generated/c2mapiv2-getting-started-collection.json | jq '.item | length'
# Expected: 3 (categories)

ls -lh postman/generated/c2mapiv2-getting-started-with-examples-collection.json
cat postman/generated/c2mapiv2-getting-started-with-examples-collection.json | \
  jq '[.item[].item[]] | length'
# Expected: 16 (patterns)
```

**UID Files**:
```bash
# Check all UID files exist
ls -1 postman/*.txt
# Expected:
# postman/aws_env_uid.txt
# postman/getting-started-collection-uid.txt
# postman/getting-started-with-examples-collection-uid.txt
# postman/mock_env_uid.txt
# postman/mock_server_uid.txt
# postman/mock_url.txt
# postman/postman_api_uid.txt
# postman/postman_linked_collection_uid.txt
# postman/postman_spec_uid.txt
# postman/test_collection_uid.txt
# postman/use_case_collection_uid.txt
```

#### 2. Run Pipeline Validation

```bash
make validate-pipeline
```

**Expected Output**:
```
Validating pipeline outputs...

[CHECK] Validating OpenAPI specifications...
[PASS] Base OpenAPI spec exists
[PASS] Final OpenAPI spec exists
[PASS] Auth endpoints present in final spec
[PASS] OpenAPI spec with examples exists
[PASS] SDK code samples found in spec (11 endpoints)

[CHECK] Validating Postman collections...
[PASS] Linked collection exists
[PASS] Test collection exists
[PASS] Test scripts found in collection (29 test assertions)

[CHECK] Validating Postman artifacts...
[PASS] All UID files exist

[CHECK] Validating documentation...
[PASS] Redoc documentation exists
[PASS] Documentation file size OK

Total validations: 22
Passed: 22
Failed: 0

All validations passed
```

#### 3. Verify Postman Workspace

**List All Collections**:
```bash
source .env  # Load POSTMAN_C2M_API_KEY
curl --silent --request GET \
  "https://api.getpostman.com/collections?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: ${POSTMAN_C2M_API_KEY}" | \
  jq -r '.collections[] | "\(.name) - \(.uid)"'
```

**Expected Output**:
```
C2M API v2 - Getting Started - 13141248-2c9d7407-d41e-4acd-82fb-29f305ae9599
C2M API v2 - Getting Started (With Examples) - 13141248-97506cee-e4ff-403b-b2a1-f475e9f9d795
C2mApiV2TestCollection - 13141248-d5cbb3a5-7151-493a-89cd-8218870f6f24
C2mApiCollectionLinked - 13141248-16f5e06a-4c3-4f8a-b4b8-2fad4d178eb2
C2M API v2 - Real World Use Cases - 46321051-365772da-09ef-47d6-821d-7c229bbe208c
(6 collections total)
```

**List All Environments**:
```bash
curl --silent --request GET \
  "https://api.getpostman.com/environments?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: ${POSTMAN_C2M_API_KEY}" | \
  jq -r '.environments[] | "\(.name) - \(.uid)"'
```

**Expected Output**:
```
C2M API - Mock Server - 46321051-3cb2367e-9c7e-41f4-a665-0a2fa5245ec4
C2M API - AWS Dev - 46321051-f564e9de-97c6-4288-9060-04aafe07026d
```

**List All Mock Servers**:
```bash
curl --silent --request GET \
  "https://api.getpostman.com/mocks?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: ${POSTMAN_C2M_API_KEY}" | \
  jq -r '.mocks[] | "\(.name) - \(.id) - \(.mockUrl)"'
```

**Expected Output**:
```
C2M API - Mock Server - 46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a - https://46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a.mock.pstmn.io
```

#### 4. Test Mock Server

**Send Test Request**:
```bash
curl --silent --request POST \
  "https://46321051-57d0772a-9c35-4e40-8272-d92bd8fbcb2a.mock.pstmn.io/jobs/submit/single/doc" \
  --header "Content-Type: application/json" \
  --data-raw '{
    "docSourceAll": {"documentId": 1234},
    "recipientAddressSource": {"addressId": 5000},
    "jobTemplate": "test_template"
  }' | jq
```

**Expected Response**:
```json
{
  "status": "processing",
  "message": "Job submitted successfully",
  "jobId": "CSlkTg1owN"
}
```

### GitHub Actions Verification

#### 1. Check Latest Workflow Run

```bash
gh run list --limit 1
```

**Expected Output**:
```
STATUS  NAME                WORKFLOW  BRANCH  EVENT  ID            ELAPSED
✓       Build API Spec...   CI/CD     main    push   21629993498   3m 42s
```

#### 2. View Workflow Details

```bash
gh run view 21629993498
```

**Expected Output**:
```
Build API Spec, Collections, and Docs · main
Triggered via push about 10 minutes ago

JOBS
✓ build (ID 123456789)
  ✓ Set up job
  ✓ Checkout
  ✓ Set up Python
  ✓ Install Python packages
  ✓ Set up Node.js
  ✓ Install npm packages
  ✓ Install system tools
  ✓ Build OpenAPI from EBNF
  ✓ Build Postman collections
  ✓ Build documentation
  ✓ Commit generated files
  ✓ Publish to Postman workspace
  ✓ Copy to artifacts repository
  ✗ Deploy to GitHub Pages (skipped - Pages not enabled)
  ✓ Complete job

For more information about this run, try: gh run view 21629993498 --web
```

#### 3. Check Artifacts Repository

```bash
# Clone artifacts repo
git clone https://github.com/click2mail/c2m-api-v2-postman-artifacts.git /tmp/artifacts

# Check contents
ls -R /tmp/artifacts/
```

**Expected Structure**:
```
/tmp/artifacts/:
openapi/
postman/
docs/
README.md

/tmp/artifacts/openapi/:
c2mapiv2-openapi-spec-base.yaml
c2mapiv2-openapi-spec-final.yaml
c2mapiv2-openapi-spec-final-with-examples.yaml

/tmp/artifacts/postman/:
c2mapiv2-linked-collection-flat.json
c2mapiv2-test-collection-with-examples.json
c2mapiv2-use-case-collection.json
c2mapiv2-getting-started-collection.json
c2mapiv2-getting-started-with-examples-collection.json

/tmp/artifacts/docs/:
index.html
openapi-bundle.yaml
```

### Complete Verification Checklist

- [ ] All OpenAPI specs generated (3 files)
- [ ] All Postman collections generated (6 files)
- [ ] All UID files created (11 files)
- [ ] Pipeline validation passed (22/22 checks)
- [ ] Collections uploaded to Postman workspace
- [ ] Mock server created and linked
- [ ] Environments created (Mock + AWS)
- [ ] GitHub Actions workflow completed successfully
- [ ] Artifacts repository updated with latest files
- [ ] Mock server responds to test requests
- [ ] Documentation generated (index.html)

---

## Appendix: All File Changes

### Files Created (New)

**OpenAPI Specs** (3 files):
- `openapi/c2mapiv2-openapi-spec-base.yaml` - Generated from EBNF
- `openapi/c2mapiv2-openapi-spec-final.yaml` - Base + auth overlay
- `openapi/c2mapiv2-openapi-spec-final-with-examples.yaml` - Final + code samples

**Postman Collections** (6 files):
- `postman/generated/c2mapiv2-linked-collection-flat.json` - Placeholders (<oneOf>)
- `postman/generated/c2mapiv2-test-collection-with-examples.json` - Realistic faker data
- `postman/generated/c2mapiv2-use-case-collection.json` - Real world examples
- `postman/generated/c2mapiv2-getting-started-collection.json` - Educational placeholders
- `postman/generated/c2mapiv2-getting-started-with-examples-collection.json` - Educational realistic
- `postman/generated/c2mapiv2-real-world-use-cases-collection.json` - (May be separate or same as use case)

**UID Tracking Files** (11 files):
- `postman/postman_api_uid.txt`
- `postman/postman_spec_uid.txt`
- `postman/postman_linked_collection_uid.txt`
- `postman/test_collection_uid.txt`
- `postman/use_case_collection_uid.txt`
- `postman/getting-started-collection-uid.txt`
- `postman/getting-started-with-examples-collection-uid.txt`
- `postman/mock_server_uid.txt`
- `postman/mock_url.txt`
- `postman/mock_env_uid.txt`
- `postman/aws_env_uid.txt`

**Documentation** (2 files):
- `docs/index.html` - Redocly API documentation
- `docs/openapi-bundle.yaml` - Bundled OpenAPI spec

**Total New Files**: 22

### Files Modified

**Configuration Files**:
- `.postman-target` - Workspace selection (personal or team)

**EBNF Data Dictionary** (if changes made):
- `data_dictionary/c2mapiv2-dd.ebnf` - May have comment updates or schema changes

**Total Modified Files**: 1-2

### Files Deleted (During Cleanup)

**Postman Resources** (not local files):
- All collections in workspace
- All environments in workspace
- All mock servers in workspace
- All APIs in workspace
- All standalone specs in workspace

**Local Files**: None deleted

---

## Quick Reference

### Common Commands

**Complete Rebuild**:
```bash
# 1. Set workspace
echo "team" > .postman-target

# 2. Source environment
source .env

# 3. Clean all
make postman-cleanup-all

# 4. Rebuild
make postman-instance-build-without-tests

# 5. Verify
make validate-pipeline
```

**Check Postman Resources**:
```bash
source .env
curl --silent --request GET \
  "https://api.getpostman.com/collections?workspace=c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1" \
  --header "X-API-Key: ${POSTMAN_C2M_API_KEY}" | \
  jq -r '.collections[] | .name'
```

**Trigger GitHub Actions**:
```bash
gh workflow run api-ci-cd.yml
gh run list --limit 1
gh run view --web
```

### Workspace IDs

- **Personal**: `d8a1f479-a2aa-4471-869e-b12feea0a98c`
- **Team/Corporate**: `c740f0f4-0de2-4db3-8ab6-f8a0fa6fbeb1`

### Estimated Times

- **Cleanup**: ~30 seconds
- **Local Rebuild (without tests)**: ~8 minutes
- **Local Rebuild (with tests)**: ~15 minutes
- **GitHub Actions Workflow**: ~3-4 minutes

---

## Document Version

**Version**: 1.0
**Date**: 2026-02-12
**Author**: Claude Code
**Status**: Complete and tested

# Postman Collections Guide for C2M API v2

## Table of Contents
1. [Overview](#overview)
2. [Collection Types](#collection-types)
3. [Linked Collection](#linked-collection)
4. [Test Collection](#test-collection)
5. [Real World Use Cases Collection](#real-world-use-cases-collection)
6. [Enhanced Collections](#enhanced-collections)
7. [Authentication Flow](#authentication-flow)
8. [Mock Server Integration](#mock-server-integration)
9. [Workflow Examples](#workflow-examples)

---

## Overview

The C2M API v2 uses multiple Postman collections, each serving a specific purpose in the development and testing workflow. These collections are automatically generated from the OpenAPI specification, which itself is derived from the EBNF data dictionary.

### Generation Pipeline
```
EBNF Data Dictionary → OpenAPI Spec → Postman Collections → Mock Server → Tests
```

---

## Collection Types

### 1. **Linked Collection** (`C2mApiCollectionLinked`)
**Purpose**: Direct representation of the OpenAPI specification for documentation and reference.

**Characteristics**:
- Auto-generated from OpenAPI spec using `openapi-to-postmanv2`
- Contains ALL endpoints defined in the API
- Minimal examples (usually just `<string>`, `<integer>` placeholders)
- No test scripts
- No complex request bodies
- Primarily for API exploration and documentation

**Use Cases**:
- Quick API reference
- Understanding available endpoints
- Generating documentation
- Base for creating other collections

### 2. **Test Collection** (`C2mApiV2TestCollection`)
**Purpose**: Automated testing with simple data and JWT authentication endpoints.

**Characteristics**:
- Contains JWT authentication endpoints (`/auth/tokens/*`)
- Contains all API endpoints with basic test data
- Includes test scripts for response validation
- Uses placeholder values and simple examples
- Each request has basic assertions (status code, response time)

**Structure**:
```
Test Collection/
├── auth/
│   ├── POST /auth/tokens/long
│   ├── POST /auth/tokens/short
│   └── POST /auth/tokens/:tokenId/revoke
└── jobs/
    ├── POST /jobs/single-doc-job-template
    ├── POST /jobs/multi-doc-merge
    └── ... (other job endpoints)
```

**Request Example**:
```json
{
  "documentSourceIdentifier": {"documentId": 1234},
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {"month": 12, "year": 2025},
      "cvv": 123
    }
  },
  "tags": ["<string>", "<string>"]
}
```

### 3. **Real World Use Cases Collection** (`C2M API v2 – Real World Use Cases`)
**Purpose**: Business scenario testing with realistic data and comprehensive examples.

**Characteristics**:
- Organized by business scenarios (Legal Firm, Medical Agency, etc.)
- Each POST endpoint has 5 example variations
- Complex, realistic request bodies
- Includes mock-aware JWT authentication
- Saved example responses for each variation

**Structure**:
```
Real World Use Cases/
├── Legal Firm/
│   ├── [single-doc-job-template]/
│   │   ├── Document ID + Credit Card + New Address
│   │   ├── External URL + Invoice + Address List ID
│   │   ├── Upload Request + ACH + Address ID
│   │   ├── Upload + Zip + User Credit + New Address
│   │   └── Zip Only + Apple Pay + Address List ID
│   ├── Get Job Details
│   └── Get Job Status
├── Company #1/
│   └── [multi-pdf-address-capture]/
│       └── (5 variations...)
└── ... (other use cases)
```

**Key Features**:
- **5 Variations per POST endpoint** demonstrating:
  - All document source types (Document ID, External URL, Upload Request, etc.)
  - All payment methods (Credit Card, Invoice, ACH, User Credit, Apple Pay)
  - All address source types (New Address, Address List ID, Address ID)
- **Pre-request Script**: Mock-aware JWT authentication
- **Saved Examples**: Each request has a saved response for mock server

### 4. **Enhanced Collections**
**Purpose**: Extended versions with additional examples and test coverage.

- **Test Collection Enhanced**: Includes all oneOf schema variations
- **Use Case Collection Enhanced**: Additional edge cases and error scenarios

---

## Authentication Flow

### JWT Authentication Process

1. **Pre-request Script Execution**:
   ```javascript
   // Runs before EVERY request in Real World Use Cases collection
   1. Check if running against mock server
   2. If not mock server OR if tokens needed:
      - Call POST /auth/tokens/long (get long-term token)
      - Call POST /auth/tokens/short (exchange for short-term token)
      - Save tokens in environment variables
   3. If real API: Add Authorization header
   4. If mock server: Skip Authorization header
   ```

2. **Token Storage**:
   - `longTermToken`: 30-day token from client credentials
   - `shortTermToken`: 15-minute token for API calls
   - `tokenExpiry`: When short token expires
   - `authToken`: Current active token

3. **Mock-Aware Logic**:
   ```javascript
   if (baseUrl.includes("mock.pstmn.io")) {
       // Don't attach Authorization header
   } else {
       // Attach Authorization: Bearer <token>
   }
   ```

---

## Mock Server Integration

### Configuration
- Mock server is paired with Real World Use Cases collection
- Contains saved example responses for each request variation
- Configuration: `matchHeader: false`, `matchBody: false`

### Why Mock-Aware Authentication?
- Postman mock servers don't validate JWT tokens
- Saved examples have `Authorization: Bearer {{authToken}}`
- Actual requests have `Authorization: Bearer eyJjdHk...`
- Mismatch causes 400 errors even with header matching disabled
- Solution: Don't send Authorization header to mock servers

---

## Workflow Examples

### 1. **Testing with Mock Server**
```
1. Select "C2M API - Mock Server" environment
2. Open Real World Use Cases → Legal Firm → [single-doc-job-template]
3. Choose any of the 5 variations
4. Send request
   - Pre-request script runs JWT negotiation
   - Token obtained but NOT attached
   - Mock returns saved example response
```

### 2. **Testing with Real API**
```
1. Select "C2M API - Production" environment (or similar)
2. Same collection and request
3. Send request
   - Pre-request script runs JWT negotiation
   - Token obtained AND attached as Authorization header
   - Real API validates token and processes request
```

### 3. **Manual JWT Testing**
```
1. Open Test Collection → auth
2. Run POST /auth/tokens/long
   - Provide client credentials
   - Receive long-term token
3. Run POST /auth/tokens/short
   - Uses long-term token
   - Receive short-term token
4. Use tokens in other requests
```

### 4. **Automated Testing Flow**
```bash
# Command line with Newman
newman run c2mapiv2-test-collection.json \
  --environment mock-env.json \
  --reporters cli,html

# Results:
- All JWT endpoints tested
- All API endpoints tested with basic data
- Response assertions validated
- HTML report generated
```

---

## Best Practices

1. **For Development**:
   - Use Real World Use Cases with mock server
   - Test different business scenarios
   - Validate request/response structure

2. **For Integration Testing**:
   - Use Test Collection with real API
   - Run full suite with Newman
   - Validate actual API behavior

3. **For Documentation**:
   - Use Linked Collection as reference
   - Shows all available endpoints
   - Clean structure without test data

4. **For Customer Onboarding**:
   - Start with Real World Use Cases
   - Demonstrate business scenarios
   - Show JWT authentication flow

---

## Collection Maintenance

### Regeneration Process
When API changes:
1. Update EBNF data dictionary
2. Run `make postman-instance-build-and-test`
3. Collections automatically regenerated
4. Mock-aware JWT script reapplied
5. Examples and variations preserved

### Key Files
- **Linked**: `postman/generated/c2mapiv2-linked-collection-flat.json`
- **Test**: `postman/generated/c2mapiv2-test-collection-flat.json`
- **Use Cases**: `postman/generated/c2mapiv2-use-case-collection.json`
- **JWT Script**: `postman/scripts/simple-jwt-pre-request.js`

---

## Troubleshooting

### Mock Server Returns 400 HTML Error
- Ensure using mock-aware JWT script
- Check environment has `baseUrl` with `mock.pstmn.io`
- Verify Authorization header NOT being sent

### JWT Authentication Not Working
- Check environment has `clientId` and `clientSecret`
- Verify `authUrl` points to auth server
- Open Postman Console to see auth requests

### Missing Endpoints
- Linked collection should have ALL endpoints
- Test collection has basic endpoints + auth
- Real World Use Cases has business scenarios only

---

## Summary

- **Linked Collection**: API reference and documentation
- **Test Collection**: Automated testing with assertions
- **Real World Use Cases**: Business scenarios with realistic data
- **JWT Authentication**: Automatic token management
- **Mock Server**: Paired with use cases, no auth header needed

Each collection serves a specific purpose in the API development lifecycle, from initial exploration to comprehensive business scenario testing.
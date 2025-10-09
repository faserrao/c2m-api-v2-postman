# C2M API V2 Postman Testing Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Postman Components Overview](#postman-components-overview)
4. [Step-by-Step Testing Guide](#step-by-step-testing-guide)
5. [Using the Enhanced Collections](#using-the-enhanced-collections)
6. [Testing with Real-World Use Cases](#testing-with-real-world-use-cases)
7. [Testing the 9 Job Endpoints](#testing-the-9-job-endpoints)
8. [Understanding Request Structure](#understanding-request-structure)
9. [Appendix: Testing Auth Endpoints](#appendix-testing-auth-endpoints)

## Introduction

This guide helps you test the C2M API V2 using Postman. The API enables businesses to submit documents for physical mail delivery with various routing and processing options.

### What You'll Learn
- How to navigate the C2M Postman workspace
- How to select and configure environments
- How to test each of the 9 job submission endpoints
- How to understand request/response structures
- How to test authentication endpoints

## Getting Started

### Prerequisites
- Postman desktop app or web version
- Access to the C2M API workspace
- Basic familiarity with Postman

### Initial Setup

1. **Open Postman**
   - Launch Postman desktop app or go to web.postman.co
   - Sign in with your credentials

2. **Select the Workspace**
   - Click the workspace dropdown (top left)
   - Select: `C2M API V2 - Serrao` 
   - You should see:
     - APIs: C2mApiV2
     - Collections: Multiple test collections
     - Environments: C2M API environments
     - Mock Servers: C2mApiV2MockServer

3. **Select the Environment**
   - Click the environment dropdown (top right)
   - Select: `C2M API - Mock Server` or `C2M API - AWS Dev`
   - This provides:
     - `{{baseUrl}}` → Mock server or API URL
     - `{{authUrl}}` → Authentication server
     - `{{clientId}}` → Pre-configured credential
     - `{{clientSecret}}` → Pre-configured credential
   - **Authentication is ready to use!**

## Postman Components Overview

### 1. API Definition
- **Location**: APIs tab → C2mApiV2
- **Purpose**: Source of truth for API structure
- **Contents**: OpenAPI specification with all endpoints

### 2. Collections
- **C2mApiV2LinkedCollection**: Shows API structure with type placeholders
- **C2mApiV2TestCollection**: Contains example data for testing
  - Pre-configured requests
  - Test scripts
  - Authentication handling
- **C2mApiV2TestCollection (Enhanced)**: Test collection with ALL oneOf examples
  - Every variant shown in Examples tab
  - 73+ pre-configured examples
  - Easier testing of different scenarios
- **C2M API v2 – Real World Use Cases**: Organized by business scenarios
  - 8 real-world use cases
  - Pre-populated requests
  - Follow-up requests included

### 3. Mock Server
- **URL**: Provided in environment as `{{baseUrl}}`
- **Purpose**: Simulates API responses without backend
- **Behavior**: Returns example responses from OpenAPI spec

### 4. Environment
- **C2M API - Mock Server**: Contains:
  - `baseUrl`: Mock server endpoint
  - `authUrl`: Authentication endpoint
  - `clientId`: Test client ID
  - `clientSecret`: Test client secret
  - `accessToken`: Auto-populated by auth flow

## Step-by-Step Testing Guide

### 1. Open the Test Collection
1. Click **Collections** in sidebar
2. Expand **C2mApiV2TestCollection**
3. You'll see folders:
   - auth (3 endpoints)
   - jobs (9 endpoints)

### 2. Check Environment Variables
1. Click the eye icon next to environment dropdown
2. Verify you see:
   - `baseUrl` (should have mock server URL)
   - `clientId` (should have value)
   - `clientSecret` (should have value)

### 3. Understand JWT Authentication

#### How Authentication Works
1. **Automatic Token Management**
   - Each collection has a pre-request script
   - It automatically gets JWT tokens before each request
   - Tokens are cached and reused until expired
   - No manual token copying needed!

2. **View the Authentication Process**
   - **Open Postman Console**: View → Show Postman Console
   - Keep console open while sending requests
   - You'll see:
     ```
     No token found, acquiring new token...
     POST https://auth-server.com/auth/tokens/long
     200 OK
     Authorization header added
     ```

3. **The Pre-request Script**
   - Click on the collection name
   - Go to **Scripts** tab → **Pre-request**
   - This script:
     - Checks if token exists
     - Gets new long-term token if needed
     - Adds Authorization header to every request
     - Skips auth for token endpoints themselves

#### Authentication Setup

**The credentials are already configured in the environment!** The pre-request script automatically uses:

1. **From Environment** (Already Set)
   - `clientId`: Pre-configured in environment
   - `clientSecret`: Pre-configured in environment
   - `authUrl`: Authentication server URL
   - `baseUrl`: Mock server or API URL

2. **How the Script Works**
   ```javascript
   // Checks environment first
   const clientId = pm.environment.get('clientId') || pm.collectionVariables.get('clientId');
   const clientSecret = pm.environment.get('clientSecret') || pm.collectionVariables.get('clientSecret');
   ```

3. **No Setup Needed!**
   - Just select the environment (dropdown in top right)
   - The script finds credentials automatically
   - Open Console to watch it work

#### Monitoring JWT Flow in Console

1. **Enable Console**
   ```
   View → Show Postman Console
   or
   Cmd+Alt+C (Mac) / Ctrl+Alt+C (Windows)
   ```

2. **What You'll See**
   - **First Request** (No Token):
     ```
     No token found, acquiring new token...
     → POST /auth/tokens/long
     ← 200 OK
     Token saved: eyJhbGci...
     Authorization header added
     → POST /jobs/single-doc
     ← 200 OK
     ```
   
   - **Subsequent Requests** (Token Cached):
     ```
     Authorization header added
     → POST /jobs/multi-doc
     ← 200 OK
     ```

3. **Common Console Messages**
   - `"Skipping auth for token endpoint"` - Normal for auth endpoints
   - `"No token found, acquiring new token..."` - Getting fresh token
   - `"Authorization header added"` - Token attached to request
   - `"Client credentials not configured"` - Check your variables
   - `"Failed to get token: 401"` - Invalid credentials

#### Troubleshooting Authentication

1. **No Authorization Header**
   - Check Console for error messages
   - Verify clientId and clientSecret are set
   - Ensure authUrl is correct

2. **401 Unauthorized Errors**
   - Open Console to see token acquisition
   - Check if token request succeeded
   - Verify credentials are correct

3. **Token Expired**
   - Script automatically gets new token
   - Watch Console to confirm renewal

### 4. Send Your First Request
1. Navigate to: **jobs** → **single-doc-job-template**
2. Click to open the request
3. Review the **Body** tab:
   ```json
   {
     "jobTemplate": "legal-certified-mail",
     "documentSourceIdentifier": 123456,
     "recipientAddressSources": [{
       "firstName": "John",
       "lastName": "Doe",
       "address1": "123 Main St",
       "city": "New York",
       "state": "NY",
       "zip": "10001",
       "country": "US"
     }],
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
     }
   }
   ```
4. Click **Send**
5. Check response (should be 200 OK)

## Using the Enhanced Collections

The Enhanced Test Collection provides ALL oneOf variants as examples, making it easier to test different scenarios without guessing the correct format.

### What's Enhanced?

The standard test collection randomly picks one variant of oneOf fields. The enhanced collection shows ALL variants in the Examples dropdown.

### How to Access OneOf Examples

1. **Open Enhanced Test Collection**
   - Look for: **C2mApiV2TestCollection (Enhanced)**
   - Expand to see the same endpoints

2. **Select Any Endpoint**
   - Example: Open **POST /jobs/single-doc**

3. **Click Examples Dropdown**
   - Located next to the Send button
   - You'll see multiple examples like:
     - "Using Document ID"
     - "Using External URL" 
     - "Using Upload Request ID"
     - "Using Upload + Zip"
     - "Using Zip ID Only"

4. **Choose Your Variant**
   - Click any example to load it
   - The request body updates automatically
   - Send the request with that specific variant

### OneOf Fields with Multiple Examples

#### documentSourceIdentifier (5 variants)
- **Using Document ID**: Simple integer ID
- **Using External URL**: URL to document
- **Using Upload Request ID**: Upload reference with document name
- **Using Upload + Zip**: Upload reference with zip and document
- **Using Zip ID Only**: Just zip reference with document

#### recipientAddressSource (3 variants)
- **Using Existing Address ID**: Reference to stored address
- **Using Address List**: Reference to address list
- **Creating New Address**: Full address object

#### paymentDetails (6 variants)
- **Credit Card Payment**: Full card details
- **Invoice Payment**: Invoice number and amount
- **ACH Payment**: Bank routing details
- **User Credit**: Credit amount
- **Apple Pay**: Apple Pay token
- **Google Pay**: Google Pay token

### Benefits of Enhanced Collection

1. **No More Guessing**: See exactly what each variant looks like
2. **Faster Testing**: Switch between variants instantly
3. **Complete Coverage**: Test all possible combinations
4. **Learning Tool**: Understand the API structure better

## Testing with Real-World Use Cases

The **C2M API v2 – Real World Use Cases** collection organizes endpoints by actual business scenarios, making it easier to understand how to implement specific features.

### Collection Structure

```
C2M API v2 – Real World Use Cases
├── Legal Firm – Certified Letters
│   ├── Submit Job
│   ├── Get Job Details
│   └── Get Job Status
├── Company #1 – Invoice Batch
│   ├── Submit Job
│   ├── Get Job Details
│   └── Get Job Status
└── (6 more use cases...)
```

### How to Use the Use Case Collection

1. **Import the Collection**
   - Look for: **C2M API v2 – Real World Use Cases**
   - This is separate from the test collection

2. **Authentication is Ready**
   - Credentials are in the environment already
   - No need to set clientId/clientSecret manually
   - The collection handles JWT automatically
   - Open Console to watch token acquisition

3. **Choose a Business Scenario**
   - Each folder represents a real customer use case
   - Read the folder description for context

4. **Run the Workflow**
   - **Step 1**: Run "Submit Job" first
   - **Step 2**: This saves the jobId automatically
   - **Step 3**: Run "Get Job Details" (uses saved jobId)
   - **Step 4**: Run "Get Job Status" (uses saved jobId)

5. **Monitor in Console**
   - First request will show token acquisition
   - Subsequent requests reuse the token
   - All requests include Authorization header

### Available Use Cases

#### 1. Legal Firm – Certified Letters
- **Scenario**: Law firm sends certified letters with copies
- **Endpoint**: POST /jobs/single-doc
- **Features**: 
  - Certified mail delivery
  - Copy to attorney
  - Credit card payment

#### 2. Company #1 – Invoice Batch  
- **Scenario**: Monthly invoice batch processing
- **Endpoint**: POST /jobs/multi-doc
- **Features**:
  - Multiple documents
  - Individual recipients
  - Invoice payment method

#### 3. Company #2 – Split Invoices
- **Scenario**: Split combined PDF with address capture
- **Endpoint**: POST /jobs/single-pdf-split-addressCapture
- **Features**:
  - PDF splitting
  - Address extraction
  - ACH payment

#### 4. Real Estate Agent – Postcards
- **Scenario**: Marketing postcards to neighborhoods
- **Endpoint**: POST /jobs/single-doc
- **Features**:
  - Bulk mailing lists
  - Postcard format
  - User credit payment

#### 5. Medical Agency – Reports + Boilerplate
- **Scenario**: Merge patient reports with compliance text
- **Endpoint**: POST /jobs/multi-doc-merge
- **Features**:
  - Document merging
  - Compliance pages
  - Invoice billing

#### 6. Monthly Newsletters
- **Scenario**: Newsletter distribution to subscribers
- **Endpoint**: POST /jobs/single-doc
- **Features**:
  - Multiple address lists
  - Color printing
  - Credit card payment

#### 7. Reseller #1 – Merge PDFs
- **Scenario**: PDF merging service for clients
- **Endpoint**: POST /jobs/multi-doc-merge
- **Features**:
  - B2B service
  - Document assembly
  - Apple Pay

#### 8. Reseller #2 – Zip PDFs
- **Scenario**: Process zip files with multiple PDFs
- **Endpoint**: POST /jobs/multi-doc
- **Features**:
  - Zip file processing
  - Batch operations
  - Google Pay

### Working with Use Cases

#### Pre-populated Data
Each use case includes realistic data:
- Actual document references
- Real address formats
- Appropriate payment methods
- Relevant job options

#### Variables and Flow
- The collection uses variables to pass data between requests
- `{{jobId}}` is automatically saved and reused
- `{{baseUrl}}` and `{{authToken}}` are inherited from environment

#### Customization
Feel free to:
- Modify the pre-populated data
- Add your own examples
- Create new use case folders
- Fork the collection for your team

### Choosing the Right Collection

| Collection | Best For | Key Feature |
|------------|----------|-------------|
| **Linked Collection** | API Reference | See structure and schemas |
| **Test Collection** | Basic Testing | Random test data |
| **Enhanced Test Collection** | OneOf Testing | All variants available |
| **Use Case Collection** | Implementation | Real-world scenarios |

## Testing the 9 Job Endpoints

### 1. POST /jobs/single-doc-job-template

**Use Cases:**
- **Legal firm**: Send letters via Certified Mail with copy to legal representative
- **Real estate agent**: Send postcards with specific templates using mail merge
- **Monthly newsletters**: Send static flyer to mailing list

**What it does**: Submits one document to multiple recipients using a predefined template

**Key fields:**
- `jobTemplate`: Predefined mailing configuration
- `documentSourceIdentifier`: Your document (ID, URL, or upload reference)
- `recipientAddressSources`: Array of recipients (addresses or address list IDs)

**Testing steps:**
1. Open the endpoint in collection
2. Review the pre-filled body
3. Note the `documentSourceIdentifier` field shows different variants each run
4. Send the request
5. Verify 200 response with jobId

---

### 2. POST /jobs/multi-docs-job-template

**Use Case:**
- **Reseller #2**: Batch PDFs from customers and send as a zip file

**What it does**: Submits multiple unique documents, each to its own recipient, using a template

**Key fields:**
- `items`: Array of document-recipient pairs
- Each item has:
  - `documentSourceIdentifier`: Individual document
  - `recipientAddressSource`: Specific recipient

**Testing steps:**
1. Open the endpoint
2. Review the array structure in body
3. Each item pairs one document with one recipient
4. Send and verify response

---

### 3. POST /jobs/multi-doc-merge-job-template

**Use Case:**
- **Medical agency**: Send custom medical reports with generic information pages

**What it does**: Merges multiple documents into one and sends to a recipient

**Key fields:**
- `documentsToMerge`: Array of documents to combine
- `recipientAddressSource`: Single recipient
- Documents are merged in array order

**Testing steps:**
1. Open the endpoint
2. Note the `documentsToMerge` array
3. Single recipient receives merged document
4. Send and check response

---

### 4. POST /jobs/single-doc

**What it does**: Submit one document with full job options (no template)

**Key difference**: Requires complete `jobOptions` specification:
- `documentClass`: businessLetter or personalLetter
- `layout`: portrait or landscape
- `mailclass`: firstClassMail, priorityMail, etc.
- `paperType`: letter, legal, postcard
- `printOption`: none, color, grayscale
- `envelope`: flat, windowedFlat, letter, etc.

**Testing steps:**
1. Open the endpoint
2. Review the detailed `jobOptions` object
3. Modify options as needed
4. Send request

---

### 5. POST /jobs/multi-doc

**What it does**: Submit multiple documents without using templates

**Structure**: Similar to multi-docs-job-template but with full `jobOptions`

**Testing steps:**
1. Review the items array
2. Note the `jobOptions` at root level (applies to all)
3. Send and verify

---

### 6. POST /jobs/multi-doc-merge

**What it does**: Merge documents and send without template

**Key fields:**
- `documentsToMerge`: Documents to combine
- `recipientAddressSource`: Target recipient
- `jobOptions`: Full mailing specifications

---

### 7. POST /jobs/single-pdf-split

**Use Case:**
- **Reseller #1**: Split customer PDFs and batch send

**What it does**: Split one PDF into sections, each going to different recipients

**Key fields:**
- `documentSourceIdentifier`: Source PDF
- `items`: Array of:
  - `pageRange`: {startPage, endPage}
  - `recipientAddressSources`: Who gets these pages

**Testing steps:**
1. Note the page range specifications
2. Each range can go to multiple recipients
3. Send and verify

---

### 8. POST /jobs/single-pdf-split-addressCapture

**Use Case:**
- **Company #2**: Split invoice PDF with addresses in the document

**What it does**: Split PDF and extract addresses from specified regions

**Key fields:**
- `embeddedExtractionSpecs`: Array of:
  - `startPage`, `endPage`: Page range
  - `addressRegion`: {x, y, width, height, pageOffset}

**Testing note**: The system extracts addresses from specified coordinates

---

### 9. POST /jobs/multi-pdf-address-capture

**Use Case:**
- **Company #1**: Process multiple invoice PDFs with embedded addresses

**What it does**: Process multiple PDFs, extracting addresses from each

**Key fields:**
- `addressCapturePdfs`: Array of PDFs with extraction regions
- Each PDF specifies where to find addresses

## Understanding Request Structure

### Common Fields Across All Endpoints

#### documentSourceIdentifier (OneOf)
The test collection rotates through these variants:
1. **Document ID** (integer): `12345`
2. **External URL** (string): `"https://example.com/document.pdf"`
3. **Upload reference**: 
   ```json
   {
     "uploadRequestId": 67890,
     "documentName": "invoice.pdf"
   }
   ```
4. **Upload with zip**:
   ```json
   {
     "uploadRequestId": 67890,
     "zipId": 11111,
     "documentName": "report.pdf"
   }
   ```
5. **Zip reference**:
   ```json
   {
     "zipId": 22222,
     "documentName": "letter.pdf"
   }
   ```

#### recipientAddressSource (OneOf)
Can be:
1. **New address** (object with fields)
2. **Address ID** (integer): `54321`
3. **Address list ID** (integer): `99999`

#### paymentDetails (OneOf)
Rotates through:
1. Credit card payment
2. Invoice payment
3. ACH payment
4. User credit
5. Apple Pay
6. Google Pay

### Headers
All requests include:
- `Authorization: Bearer {{accessToken}}` (auto-added)
- `Content-Type: application/json`

### Variables Used
From environment:
- `{{baseUrl}}`: Base API URL
- `{{authUrl}}`: Auth server URL
- `{{accessToken}}`: Current JWT token

## Appendix: Testing Auth Endpoints

### 1. Get Long-Term Token
**POST {{authUrl}}/auth/tokens/long**

Manual test:
1. Open auth → tokens → long
2. Body is pre-filled with test credentials
3. Send request
4. Response includes:
   - `access_token`: JWT token
   - `expires_in`: 7776000 (90 days)

### 2. Get Short-Term Token  
**POST {{authUrl}}/auth/tokens/short**

Process:
1. Requires valid long-term token
2. Returns 15-minute access token
3. This is what the pre-request script does automatically

### 3. Revoke Token
**POST {{authUrl}}/auth/tokens/:tokenId/revoke**

To test:
1. Get the `tokenId` from previous response
2. Replace `:tokenId` in URL
3. Send to revoke the token

### Authentication Flow
1. Collection pre-request script checks for valid token
2. If missing/expired, gets long-term token
3. Exchanges for short-term token
4. Adds to Authorization header
5. All automatic - just send requests!

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check environment is selected
   - Try manually getting new token
   - Verify clientId/clientSecret

2. **404 Not Found**
   - Verify correct workspace
   - Check baseUrl in environment
   - Ensure mock server is active

3. **400 Bad Request**
   - Review request body
   - Check required fields
   - Validate data types

### Tips for Success

1. **Start Simple**: Test single-doc endpoints first
2. **Watch the Console**: View → Show Postman Console
3. **Check Variables**: Hover over {{variables}} to see values
4. **Review Examples**: Each request has example responses
5. **Use Tests Tab**: See what validations run

## Quick Reference: Which Collection to Use?

### "I want to..."

| Goal | Use This Collection | Why |
|------|-------------------|-----|
| See all API endpoints | **Linked Collection** | Complete API reference |
| Test with random data | **Test Collection** | Quick testing with examples |
| Test all oneOf variants | **Enhanced Test Collection** | All variants in Examples dropdown |
| Implement a specific feature | **Use Case Collection** | Real-world scenarios with context |
| Understand business usage | **Use Case Collection** | Named by actual use cases |
| Debug oneOf issues | **Enhanced Test Collection** | See all possible formats |
| Run automated tests | **Test Collection** | Has test scripts |
| Learn the API | **Use Case Collection** | Best for understanding |

### Quick Tips for OneOf Fields

1. **Can't figure out the format?**
   - Use Enhanced Test Collection
   - Click Examples dropdown
   - All variants are listed

2. **Need realistic examples?**
   - Use Use Case Collection
   - Each scenario has appropriate data

3. **Testing different payment methods?**
   - Enhanced Collection has all 6 payment types
   - Just select from Examples

### JWT Authentication Quick Reference

1. **View Token Flow**
   - Open: View → Show Postman Console
   - Watch authentication happen in real-time

2. **Debug Auth Issues**
   - Console shows all token requests
   - Look for error messages
   - Check credentials in Variables tab

3. **Token Management**
   - Automatic - no manual work needed
   - Cached until expiry
   - Pre-request script handles everything

### Common Workflows

#### New Developer Onboarding
1. Select the environment (top right dropdown)
2. Start with **Use Case Collection**
3. Open Console to see JWT flow
4. Find scenario similar to your needs
5. Run the complete workflow
6. Modify for your requirements

#### Testing All Variants
1. Open **Enhanced Test Collection**
2. Select endpoint
3. Use Examples dropdown
4. Test each variant systematically

#### Quick API Testing
1. Use standard **Test Collection**
2. Requests have random test data
3. Just click Send

## Next Steps

1. Try the Enhanced Test Collection to see all oneOf variants
2. Explore the Use Case Collection for your scenario
3. Create your own examples based on these patterns
4. Build a workflow using Collection Runner
5. Export and share with your team

## Support

For issues or questions:
- Check the API documentation in the API tab
- Review the Use Case Collections Guide
- See examples in Enhanced Test Collection
- Contact the API team

Happy testing! 🚀
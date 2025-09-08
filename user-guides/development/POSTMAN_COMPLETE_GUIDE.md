# Complete Postman Guide for C2M API V2

This comprehensive guide consolidates all Postman documentation for the C2M API V2 project. It covers setup, authentication, testing, CI/CD integration, and troubleshooting.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Workspace Setup](#workspace-setup)
- [Authentication Configuration](#authentication-configuration)
- [Collection Management](#collection-management)
- [Mock Server Usage](#mock-server-usage)
- [Testing Workflows](#testing-workflows)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)
- [Reference](#reference)

---

## Overview

The C2M API V2 Postman integration provides:
- **Automated Collection Generation** - Collections generated from OpenAPI specifications
- **JWT Authentication** - Automatic token management with pre-request scripts
- **Mock Servers** - Both cloud (Postman) and local (Prism) mock servers
- **Test Automation** - Comprehensive test suites for all endpoints
- **CI/CD Publishing** - Automated publishing via GitHub Actions

### Architecture Flow
```
EBNF Data Dictionary → OpenAPI Spec → Postman Collection → Mock Server → Tests
                                            ↓
                                      JWT Auth Scripts
```

---

## Quick Start

### 1. Prerequisites
- Postman account (free at [postman.com](https://www.postman.com))
- Postman Desktop app installed
- Access to C2M API repository

### 2. Import Collection and Environment

1. **Download Files**:
   ```bash
   # From the repository
   postman/generated/c2mapiv2-test-collection-fixed.json
   postman/environments/c2m-api-dev.json
   ```

2. **Import to Postman**:
   - Open Postman Desktop
   - Click **Import** button
   - Drag both files into the import window
   - Click **Import**

3. **Select Environment**:
   - Click environment dropdown (top right)
   - Select `c2m-api-dev`

4. **Test Authentication**:
   - Open any request (except `/auth/*` endpoints)
   - Click **Send**
   - Check Console (View → Show Postman Console) for auth success

---

## Workspace Setup

### Current Workspace Configuration

| Component | Value |
|-----------|-------|
| **API ID** | 72171f42-24f4-4436-aeca-ff115bf5f8dd |
| **Linked Collection UID** | 46321051-20f03116-7068-4232-bcc4-e42b82f6e73d |
| **Test Collection UID** | 46321051-ffd1a734-64f0-414f-82cf-3192ad453289 |
| **Mock Server ID** | 6480522b-e3b9-4968-8ed8-4193fd0b58af |
| **Mock URL** | https://6480522b-e3b9-4968-8ed8-4193fd0b58af.mock.pstmn.io |
| **Environment UID** | 46321051-2b02180d-bdb7-479c-a08f-79c0c32c5957 |

### Get Your Postman API Key

1. Log into [Postman](https://www.postman.com)
2. Click your avatar (top right) → **Settings**
3. Click **API Keys** tab
4. Click **Generate API Key**
5. Name it "C2M API Access"
6. Copy the key (starts with `PMAK-`)
7. Save it securely

### Local Development Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/[your-org]/c2m-api-repo.git
   cd c2m-api-repo
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add:
   # POSTMAN_API_KEY=your-postman-api-key-here
   ```

3. **Set Workspace Target**:
   ```bash
   echo "personal" > .postman-target  # or "corporate"
   ```

---

## Authentication Configuration

### JWT Authentication Flow

The C2M API uses a two-token JWT system:
1. **Long-term token** (30-90 days) - Obtained via client credentials
2. **Short-term token** (15 minutes) - Used for API requests

### Setting Up Authentication

#### Step 1: Collection Pre-request Script

The collection includes an automated pre-request script that:
- Checks if a valid token exists
- Automatically obtains new tokens when needed
- Adds `Authorization: Bearer <token>` header
- Skips authentication for `/auth/*` endpoints

#### Step 2: Environment Variables

Configure these in your Postman environment:

```json
{
  "baseUrl": "https://api.c2m.example.com",
  "authUrl": "https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev",
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret",
  "token": "",           // Auto-populated
  "tokenExpiry": "",     // Auto-populated
  "longTermToken": "",   // Auto-populated
  "longTermExpiry": ""   // Auto-populated
}
```

#### Step 3: Test Credentials

For development, test credentials are available:
- **Client ID**: `test-client-123`
- **Client Secret**: Available in AWS Secrets Manager

### Manual Token Management

```javascript
// Force token refresh
await pm.globals.get('refreshCognitoToken')();

// Debug auth status
pm.globals.get('debugCognitoAuth')();

// Clear all tokens
pm.globals.get('clearCognitoTokens')();
```

---

## Collection Management

### Directory Structure

```
postman/
├── generated/                    # Auto-generated collections
│   ├── c2mapiv2-collection.json # Base from OpenAPI
│   ├── c2mapiv2-test-collection-fixed.json # With auth & tests
│   └── c2mapiv2-linked-collection-flat.json # API-linked version
├── environments/                 # Environment configs
│   ├── c2m-api-dev.json        # Development environment
│   └── c2m-api-prod.json       # Production environment
├── scripts/                     # Pre-request & test scripts
│   ├── jwt-pre-request.js      # JWT authentication
│   └── auth-pre-request-abstract.js # Base auth logic
└── custom/                      # User customizations
    ├── auth-body-override.json  # Auth endpoint overrides
    └── auth-examples.json       # Example requests
```

### Building Collections

#### Local Build
```bash
# Complete build and test pipeline
make postman-collection-build-and-test

# Individual steps
make generate-openapi-spec-from-dd    # EBNF to OpenAPI
make postman-import-openapi-spec      # Import to Postman
make postman-collection-add-tests     # Add test scripts
make postman-fix-urls                 # Fix URL variables
```

#### CI/CD Build (GitHub Actions)
```bash
# CI-specific targets (no local servers)
make postman-instance-build-only      # Build without local testing
make rebuild-all-postman-ci          # Full CI rebuild
```

### Collection Features

1. **Pre-request Scripts**:
   - Automatic JWT token management
   - Environment variable validation
   - Request timing headers

2. **Test Scripts**:
   - Status code validation
   - Schema compliance checking
   - Response time assertions
   - Business logic validation

3. **Example Data**:
   - Success scenarios (200/201)
   - Error scenarios (400/401/403)
   - Edge cases and validation

---

## Mock Server Usage

### Postman Cloud Mock

```bash
# Create/update mock server
make postman-mock-create

# Test against mock
make postman-mock

# Get mock URL
cat postman/postman_mock_url.txt
```

### Local Prism Mock

```bash
# Start local mock (port 4010)
make prism-start

# Check status
make prism-status

# Run tests
make prism-mock-test

# Stop mock
make prism-stop
```

### Mock Server URLs

- **Cloud Mock**: `https://[mock-id].mock.pstmn.io`
- **Local Mock**: `http://localhost:4010`

Configure in environment as `{{baseUrl}}`

---

## Testing Workflows

### 1. Manual Testing

1. Select collection in Postman
2. Choose environment (dev/prod/mock)
3. Send individual requests
4. Review responses and console logs

### 2. Collection Runner

1. Click **Runner** button in Postman
2. Select collection and environment
3. Configure:
   - Iterations: 1
   - Delay: 0ms
   - Data file: Optional CSV/JSON
4. Click **Run**

### 3. Newman CLI Testing

```bash
# Install Newman
npm install -g newman

# Run tests
newman run postman/generated/c2mapiv2-test-collection-fixed.json \
  -e postman/environments/c2m-api-dev.json \
  --reporters cli,html \
  --reporter-html-export newman-report.html
```

### 4. Automated Testing

```bash
# Test specific endpoint
make prism-test-endpoint PRISM_TEST_ENDPOINT=/jobs/submit/single

# Test with selection menu
make prism-test-select

# Run all tests
make postman-test-collection
```

---

## CI/CD Integration

### GitHub Actions Workflow

The project includes automated CI/CD that:
1. Builds OpenAPI spec from EBNF
2. Generates Postman collections
3. Publishes to configured workspace
4. Runs automated tests

### Setup GitHub Actions

1. **Add Secrets**:
   - Go to repository Settings → Secrets → Actions
   - Add `POSTMAN_API_KEY` with your API key

2. **Configure Target**:
   ```bash
   # Choose workspace
   echo "personal" > .postman-target  # or "corporate"
   git add .postman-target
   git commit -m "Configure Postman target"
   git push
   ```

3. **Trigger Workflow**:
   - Push to main branch
   - Or manually: Actions → Run workflow

### CI-Specific Targets

These targets skip local server requirements:

```makefile
# Build without local testing
make postman-instance-build-only

# Rebuild for CI environment
make rebuild-all-postman-ci

# Publish to workspace
make postman-publish
```

### Known CI/CD Issues (Fixed)

1. **Postman CLI Installation**:
   ```yaml
   # Added to workflow
   curl -o- "https://dl-cli.pstmn.io/install/linux64.sh" | sh
   ```

2. **Local Server Dependencies**:
   - Created CI-specific targets
   - Skip prism-start and docs-serve

3. **openapi-diff Tool**:
   - npm version hangs
   - Temporarily disabled
   - Use `npx openapi-diff` when needed

---

## Troubleshooting

### Common Issues

#### "No authorization header"
**Cause**: Environment not selected
**Fix**: Select environment from dropdown (top right)

#### "401 Unauthorized"
**Causes**:
- Invalid credentials
- Expired token
- Wrong auth URL

**Fixes**:
1. Verify environment variables
2. Check credentials in AWS Secrets Manager
3. Clear tokens: `pm.globals.get('clearCognitoTokens')()`

#### "403 Forbidden"
**Cause**: Valid token but insufficient permissions
**Fix**: 
- Verify client has correct scopes
- Check API Gateway authorizer configuration
- Note: Auth endpoints return 403 for some operations (expected)

#### "Command not found" (Local)
**Cause**: Missing dependencies
**Fix**:
```bash
make install
npm install -g newman
brew install jq
```

#### GitHub Actions Failures
**Common Causes**:
1. Missing `POSTMAN_API_KEY` secret
2. Wrong `.postman-target` value
3. Network timeout

**Debug Steps**:
1. Check workflow logs
2. Verify secrets configured
3. Try manual workflow run

### Debug Commands

```bash
# Check Postman workspace
make postman-workspace-debug

# Verify collection URLs
make verify-urls

# Test Postman auth
make postman-test-auth

# Print configuration
make print-openapi-vars
```

### Quick Fixes

```bash
# Clean and rebuild everything
make postman-cleanup-all
make postman-collection-build-and-test

# Reset authentication
pm.globals.get('clearCognitoTokens')()

# Force new mock
make postman-mock-delete
make postman-mock-create
```

---

## Reference

### Make Targets

| Target | Description |
|--------|-------------|
| `postman-collection-build-and-test` | Full build and test pipeline |
| `postman-instance-build-only` | CI build without local testing |
| `postman-import-openapi-spec` | Import OpenAPI to Postman |
| `postman-collection-add-tests` | Add test scripts to collection |
| `postman-fix-urls` | Fix hardcoded URLs |
| `postman-mock-create` | Create cloud mock server |
| `prism-start` | Start local mock server |
| `postman-workspace-debug` | Debug workspace contents |
| `postman-cleanup-all` | Remove all Postman resources |

### File Locations

| File | Purpose |
|------|---------|
| `postman/generated/c2mapiv2-test-collection-fixed.json` | Main test collection |
| `postman/environments/c2m-api-dev.json` | Development environment |
| `postman/scripts/jwt-pre-request.js` | JWT authentication script |
| `.postman-target` | Workspace target (personal/corporate) |
| `postman/postman_mock_url.txt` | Current mock server URL |

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `baseUrl` | API base URL | `https://api.c2m.example.com` |
| `authUrl` | Auth endpoint URL | `https://auth.c2m.example.com` |
| `clientId` | OAuth client ID | `test-client-123` |
| `clientSecret` | OAuth client secret | `secret-value` |
| `token` | Current JWT token | Auto-populated |
| `tokenExpiry` | Token expiration | Auto-populated |

### API Resources

- **API Definition**: APIs tab in Postman
- **Collections**: Collections tab
- **Environments**: Environments tab
- **Mock Servers**: Mock Servers tab
- **Documentation**: [GitHub Pages](https://[org].github.io/c2m-api-repo)

---

## Next Steps

1. **Import collection and environment** to Postman
2. **Configure authentication** with your credentials
3. **Test a few endpoints** to verify setup
4. **Run the full test suite** with Newman
5. **Set up CI/CD** for automated updates

For additional help:
- Create a GitHub issue
- Check the [main README](../README.md)
- Review [troubleshooting logs](#debug-commands)

---

*Last Updated: 2025-09-08*
*Consolidates documentation from both c2m-api-repo and c2m-api-v2-security repositories*
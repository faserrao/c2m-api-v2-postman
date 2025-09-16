# Complete Postman Guide for C2M API V2

This comprehensive guide covers Postman integration for the C2M API V2 project, including setup, authentication, testing, CI/CD integration, and troubleshooting.

## Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Workspace Management](#workspace-management)
- [Authentication System](#authentication-system)
- [Collection Generation](#collection-generation)
- [Mock Server Configuration](#mock-server-configuration)
- [Testing Framework](#testing-framework)
- [CI/CD Integration](#cicd-integration)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)

---

## Overview

The C2M API V2 Postman integration provides a complete API testing and documentation ecosystem that automatically synchronizes with the OpenAPI specification.

### Key Features

- **Automated Synchronization**: Collections generated from OpenAPI specs
- **Dynamic Authentication**: JWT token management with automatic refresh
- **Dual Mock Servers**: Cloud (Postman) and local (Prism) options
- **Comprehensive Testing**: Automated test generation and execution
- **CI/CD Publishing**: GitHub Actions integration for continuous updates

### Design Principles

1. **Single Source of Truth**: OpenAPI specification drives all Postman artifacts
2. **Automation First**: Minimize manual configuration
3. **Environment Agnostic**: Works locally and in CI/CD
4. **Dynamic Resource Management**: UIDs tracked automatically

---

## System Architecture

### Integration Flow

```
EBNF Data Dictionary
        ↓
   OpenAPI Spec
        ↓
 Postman Collection
    ↓        ↓
Mock Server  Tests
```

### Component Relationships

1. **OpenAPI to Postman**: Automated conversion via Postman API
2. **Authentication Layer**: Pre-request scripts handle JWT tokens
3. **Mock Servers**: Both cloud and local options available
4. **Test Suites**: Generated from OpenAPI examples

### Resource Management

The system dynamically manages Postman resources:
- Collections created/updated via API
- Mock servers provisioned automatically
- Environment variables synchronized
- UIDs tracked in repository

---

## Workspace Management

### Workspace Types

The system supports two workspace configurations:

1. **Private Workspace**
   - Personal development
   - Individual API keys
   - Isolated testing

2. **Team Workspace**
   - Shared resources
   - Collaborative testing
   - Production synchronization

### Resource Identification

Resources are identified by UIDs that persist across operations:
- Collection UID: Tracks main collection
- Mock Server ID: References cloud mock
- Environment UID: Links configuration

These UIDs are:
- Generated on first creation
- Stored in repository
- Used for updates
- Never manually edited

### API Key Management

Postman API keys enable programmatic access:

1. **Generation**:
   - Login to Postman
   - Navigate to Settings → API Keys
   - Generate new key
   - Store securely

2. **Usage**:
   - Local: `.env` file
   - CI/CD: GitHub secrets
   - Never commit to repository

---

## Authentication System

### JWT Token Architecture

The system implements a two-tier JWT token system:

1. **Long-term Tokens**
   - 30-90 day lifetime
   - Used for token exchange
   - Stored securely

2. **Short-term Tokens**
   - 15-minute lifetime
   - Used for API calls
   - Auto-refreshed

### Pre-request Script

The authentication script runs before each request:

```javascript
// Skip auth for auth endpoints
if (pm.request.url.path.join('/').includes('auth/')) {
    return;
}

// Check token expiration
const tokenExpiry = pm.environment.get('tokenExpiry');
if (tokenExpiry && new Date() < new Date(tokenExpiry)) {
    return; // Token still valid
}

// Refresh token logic...
```

Key features:
- Automatic token refresh
- Expiration monitoring
- Error handling
- Retry logic

### Environment Variables

Authentication requires these environment variables:
- `authUrl`: Authentication endpoint
- `clientId`: Client identifier
- `clientSecret`: Client secret
- `token`: Current short-term token
- `tokenExpiry`: Token expiration time
- `longTermToken`: Long-term token
- `longTermExpiry`: Long-term expiration

---

## Collection Generation

### OpenAPI to Postman Conversion

The build process converts OpenAPI to Postman format:

1. **Parse OpenAPI**: Read specification file
2. **Convert Format**: Transform to Postman schema
3. **Add Authentication**: Inject pre-request scripts
4. **Generate Tests**: Create test assertions
5. **Update Collection**: Push to Postman cloud

### Collection Structure

Generated collections include:
- Folder organization by tags
- Request examples from OpenAPI
- Variable substitution
- Authentication headers
- Test assertions

### Dynamic Updates

Collections update automatically when:
- OpenAPI spec changes
- New endpoints added
- Authentication modified
- Examples updated

The system preserves:
- Custom test scripts
- Manual variable overrides
- Additional headers
- Request descriptions

---

## Mock Server Configuration

### Postman Mock Server

Cloud-based mock server features:
- Automatic provisioning
- Public accessibility
- Example matching
- Variable support

Configuration process:
1. Collection uploaded
2. Mock server created
3. URL generated
4. Environment updated

### Local Mock Server (Prism)

For local development:
- No internet required
- Faster response times
- Dynamic responses
- Request validation

Usage:
```bash
make prism-server
# Server runs at http://localhost:4010
```

### Mock Response Management

Mock responses are defined in:
- OpenAPI examples
- Postman examples
- Response templates
- Dynamic generators

Priority order:
1. Exact match examples
2. Schema-based responses
3. Default responses
4. Error responses

---

## Testing Framework

### Test Generation

Tests are automatically generated for:
- Status code validation
- Schema compliance
- Response time checks
- Business logic rules

Example generated test:
```javascript
pm.test("Status code is 200", () => {
    pm.response.to.have.status(200);
});

pm.test("Response has required fields", () => {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('jobId');
});
```

### Test Organization

Tests are organized by:
- Collection level: Global assertions
- Folder level: Tag-specific tests
- Request level: Endpoint tests
- Example level: Scenario tests

### Newman Integration

Command-line testing via Newman:
- Headless execution
- CI/CD compatible
- Multiple reporters
- Environment support

Execution:
```bash
newman run collection.json \
  -e environment.json \
  --reporters cli,junit \
  --reporter-junit-export results.xml
```

---

## CI/CD Integration

### GitHub Actions Workflow

The CI/CD pipeline automates:
1. OpenAPI validation
2. Collection generation
3. Postman upload
4. Mock server update
5. Test execution

### Workflow Triggers

Updates occur on:
- Push to main branch
- OpenAPI modifications
- Manual workflow dispatch
- Scheduled builds

### Secret Management

Required GitHub secrets:
- `POSTMAN_API_KEY`: API authentication
- `POSTMAN_WORKSPACE_ID`: Target workspace
- Collection UIDs stored in repo

### Build Process

CI-specific make targets:
- `ci-postman-build`: Generate collection
- `ci-postman-update`: Upload to cloud
- `ci-postman-test`: Run test suite

---

## Development Workflow

### Local Development Cycle

1. **Modify OpenAPI**:
   - Edit specification
   - Add examples
   - Update schemas

2. **Generate Collection**:
   ```bash
   make postman-build
   ```

3. **Test Locally**:
   ```bash
   make postman-test
   ```

4. **Update Cloud**:
   ```bash
   make postman-update
   ```

### Best Practices

1. **Always test locally first**
2. **Use environment variables**
3. **Keep examples current**
4. **Document test purposes**
5. **Version control changes**

### Debugging Tools

- Postman Console: Request/response logs
- Newman reporters: Detailed test output
- Environment viewer: Variable inspection
- History tracking: Request comparison

---

## Troubleshooting

### Common Issues

#### Authentication Failures
- Verify client credentials
- Check token expiration
- Confirm environment selection
- Review console logs

#### Collection Sync Issues
- Validate API key
- Check workspace permissions
- Verify collection UID
- Review build logs

#### Mock Server Problems
- Confirm server URL
- Check example matching
- Verify variable substitution
- Test connectivity

#### Test Failures
- Inspect actual vs expected
- Check environment variables
- Verify mock responses
- Review test logic

### Debug Commands

```bash
# Verbose build output
make VERBOSE=1 postman-build

# Test specific folder
newman run collection.json --folder "Authentication"

# Dry run (no uploads)
make -n postman-update

# Check environment
make check-postman-env
```

### Log Locations

- Build logs: `logs/postman-build.log`
- Test results: `postman/test-results/`
- Newman output: Console/CI logs
- Postman Console: In-app logs

---

## Best Practices Summary

1. **Resource Management**
   - Let system manage UIDs
   - Don't edit IDs manually
   - Track changes in git

2. **Authentication**
   - Use environment variables
   - Never hardcode secrets
   - Monitor token expiration

3. **Testing**
   - Write meaningful assertions
   - Test error scenarios
   - Use data-driven tests

4. **Collaboration**
   - Document custom changes
   - Share environment templates
   - Coordinate team updates

---

*This guide represents the complete Postman integration system for C2M API V2, focusing on automated workflows and best practices for API testing and documentation.*
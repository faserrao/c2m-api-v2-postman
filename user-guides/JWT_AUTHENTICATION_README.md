# JWT Authentication Implementation Guide

This guide provides comprehensive documentation for the JWT authentication system implemented in the C2M API v2.

## Quick Start

### 1. Generate OpenAPI Spec with JWT Endpoints
```bash
make generate-openapi-spec-from-dd
make openapi-merge-overlays
```

### 2. Build and Test JWT-enabled Collections
```bash
make postman-collection-build-and-test
make postman-add-jwt-tests
```

### 3. Run JWT Authentication Tests
```bash
make jwt-test
```

## Implementation Overview

The JWT authentication system uses a two-token approach:
- **Long-term tokens** (30-90 days): For server-to-server authentication
- **Short-term tokens** (15 minutes): For API requests

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   EBNF Data     │     │  Auth Overlay    │     │ Merged OpenAPI  │
│   Dictionary    │ + → │ (auth.tokens.yaml)│ → → │ Specification   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           ↓
                                                  ┌─────────────────┐
                                                  │ Postman         │
                                                  │ Collection      │
                                                  └─────────────────┘
```

## JWT Endpoints

### 1. Issue Long-Term Token
**POST** `/auth/tokens/long`

Obtain a long-lived token for server authentication.

**Authentication Methods:**
- Client credentials + secret
- Client credentials + OTP
- Signed JWT assertion

**Example:**
```bash
curl -X POST https://api.example.com/v1/auth/tokens/long \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: c2m_your_client_id" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "c2m_your_client_id",
    "client_secret": "your_secret",
    "scopes": ["jobs:submit", "templates:read"],
    "ttl_seconds": 2592000
  }'
```

### 2. Issue Short-Term Token
**POST** `/auth/tokens/short`

Exchange a long-term token for a short-lived JWT.

**Example:**
```bash
curl -X POST https://api.example.com/v1/auth/tokens/short \
  -H "Authorization: Bearer {long_term_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "scopes": ["jobs:submit"]
  }'
```

### 3. Revoke Token
**POST** `/auth/tokens/{tokenId}/revoke`

Revoke any token by its ID.

**Example:**
```bash
curl -X POST https://api.example.com/v1/auth/tokens/tok_123/revoke \
  -H "Authorization: Bearer {token_with_revoke_permission}"
```

## Client Examples

### JavaScript/Node.js
See [`examples/jwt-authentication-examples.md`](examples/jwt-authentication-examples.md) for complete implementations in:
- JavaScript/Node.js (with automatic token refresh)
- Python (with retry logic)
- cURL commands
- Alternative authentication methods

### Postman Pre-request Script
The [`postman/scripts/jwt-pre-request.js`](postman/scripts/jwt-pre-request.js) script automatically:
- Obtains long-term tokens when needed
- Exchanges for short-term tokens
- Refreshes expired tokens
- Adds Authorization headers

## Testing

### Automated Test Suite
Run comprehensive JWT tests:
```bash
make jwt-test
```

Tests include:
- Token issuance with various authentication methods
- Token exchange and scope narrowing
- Token revocation and idempotency
- Error handling and rate limiting
- Token expiration and refresh

### Postman Collection Tests
Add JWT-specific tests to your collection:
```bash
make postman-add-jwt-tests
```

This adds:
- Response validation for JWT fields
- Token storage in environment variables
- OAuth 2.0 error format validation
- Automatic token management

## Configuration

### Environment Variables
Set these in your `.env` file:
```bash
# API Configuration
API_BASE_URL=http://localhost:4010
TEST_CLIENT_ID=c2m_test_client
TEST_CLIENT_SECRET=test_secret

# Postman Environment
POSTMAN_API_KEY=your_postman_api_key
```

### Postman Environment Setup
Configure these variables in Postman:
- `baseUrl`: API base URL
- `clientId`: Your client ID
- `clientSecret`: Your client secret
- `longTermToken`: (auto-populated)
- `shortTermToken`: (auto-populated)
- `tokenExpiry`: (auto-populated)

## Security Best Practices

1. **Token Storage**
   - Store long-term tokens securely
   - Never expose client secrets in client-side code
   - Use environment variables for sensitive data

2. **Token Lifecycle**
   - Implement automatic token refresh
   - Revoke tokens when no longer needed
   - Monitor token usage patterns

3. **Scope Management**
   - Request minimal required scopes
   - Use scope narrowing for short-term tokens
   - Validate scopes on the server side

4. **Error Handling**
   - Implement retry logic for 401/429 errors
   - Handle token expiration gracefully
   - Log authentication events for auditing

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check token expiration
   - Verify client credentials
   - Ensure proper Authorization header format

2. **403 Forbidden**
   - Verify token has required scopes
   - Check resource permissions

3. **429 Rate Limited**
   - Implement exponential backoff
   - Check Retry-After header

### Debug Commands
```bash
# Check current OpenAPI spec
cat openapi/c2mapiv2-openapi-spec-final.yaml | grep -A20 "/auth/tokens"

# Verify JWT overlay
cat openapi/overlays/auth.tokens.yaml

# Test token endpoint manually
curl -X POST http://localhost:4010/auth/tokens/long \
  -H "Content-Type: application/json" \
  -d '{"grant_type":"client_credentials",...}'
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run JWT Tests
  env:
    TEST_CLIENT_ID: ${{ secrets.TEST_CLIENT_ID }}
    TEST_CLIENT_SECRET: ${{ secrets.TEST_CLIENT_SECRET }}
  run: make jwt-test
```

### Docker Integration
```dockerfile
# Copy JWT test files
COPY tests/jwt-auth-tests.js /app/tests/
COPY postman/scripts/jwt-pre-request.js /app/postman/scripts/

# Run tests
RUN make jwt-test
```

## Next Steps

1. **Production Deployment**
   - Configure production client credentials
   - Set appropriate token TTLs
   - Enable audit logging

2. **Advanced Features**
   - Implement token rotation policies
   - Add multi-factor authentication
   - Configure IP allowlisting

3. **Monitoring**
   - Track token issuance metrics
   - Monitor authentication failures
   - Set up alerts for anomalies
# C2M API V2 Authentication - Consolidated Guide

> **Note**: This document consolidates all authentication documentation previously spread across multiple files. Original documents are archived in `archive/` folder.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Implementation Guide](#implementation-guide)
- [Testing Guide](#testing-guide)
- [Postman Configuration](#postman-configuration)
- [Production vs Development](#production-vs-development)
- [Quick Reference](#quick-reference)
- [Troubleshooting](#troubleshooting)

---

## Overview

The C2M API V2 uses a two-tier JWT authentication system:

1. **Long-term tokens** (30-90 days) - Obtained with client credentials
2. **Short-term tokens** (15 minutes) - Used for actual API calls

### Key Benefits
- Enhanced security through token isolation
- Reduced attack surface with short-lived tokens
- Provider-agnostic design (Cognito today, any provider tomorrow)
- Efficient token management

### Authentication Flow
```
Client Credentials → Long Token (30-90d) → Short Token (15m) → API Calls
                          ↓                      ↓
                    Stored Securely        Used for Requests
```

---

## Architecture

### AWS Services Used

```
┌─────────────────────┐
│   Client Application│
└──────────┬──────────┘
           │ 1. Client Credentials
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│   API Gateway       │────▶│  Lambda Functions   │
│  /auth/tokens/*     │     │  Token Management   │
└─────────────────────┘     └──────────┬──────────┘
                                       │
                            ┌──────────▼──────────────┐
                            │   Backend Services      │
                            ├────────────────────────┤
                            │ • Cognito User Pool     │
                            │ • DynamoDB (metadata)   │
                            │ • Secrets Manager       │
                            │ • CloudWatch Logs       │
                            └────────────────────────┘
```

### Components

1. **API Gateway**
   - REST API endpoints for token management
   - JWT authorizer for validation
   - Request throttling and CORS

2. **Lambda Functions**
   - `issueLongToken` - Client credential validation
   - `issueShortToken` - Token exchange
   - `revokeToken` - Token revocation
   - `jwtAuthorizer` - Request authorization

3. **Cognito User Pool**
   - Service account management
   - No email/SMS features (M2M only)
   - Custom attributes for metadata

4. **DynamoDB**
   - Token metadata storage
   - Revocation tracking
   - TTL-based cleanup

5. **Secrets Manager**
   - Client credentials storage
   - JWT signing keys
   - Automatic rotation support

---

## Implementation Guide

### Authentication Endpoints

#### 1. Get Long-term Token
```http
POST https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev/auth/tokens/long
Content-Type: application/json
X-Client-Id: your-client-id

{
  "grant_type": "client_credentials",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "scopes": ["jobs:submit", "templates:read"],
  "ttl_seconds": 2592000  // 30 days
}
```

Response:
```json
{
  "access_token": "eyJraWQ...",
  "token_type": "Bearer",
  "expires_in": 2592000,
  "expires_at": "2024-02-29T12:00:00Z",
  "token_id": "tok_abc123",
  "scopes": ["jobs:submit", "templates:read"]
}
```

#### 2. Exchange for Short-term Token
```http
POST https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev/auth/tokens/short
Authorization: Bearer {long-term-token}
Content-Type: application/json

{
  "scopes": ["jobs:submit"]  // Optional: narrow scopes
}
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 900,
  "expires_at": "2024-01-29T10:15:00Z",
  "token_id": "stk_xyz789"
}
```

#### 3. Revoke Token
```http
POST https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev/auth/tokens/{tokenId}/revoke
Authorization: Bearer {token-with-revoke-permission}
```

Response: `204 No Content`

### Code Examples

#### JavaScript/Node.js
```javascript
class C2MAuthClient {
  constructor(config) {
    this.clientId = config.clientId;
    this.clientSecret = config.clientSecret;
    this.authUrl = config.authUrl || 'https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev';
    this.longTermToken = null;
    this.shortTermToken = null;
  }

  async getShortTermToken() {
    // Check if we have a valid short-term token
    if (this.shortTermToken && new Date() < new Date(this.shortTermToken.expiresAt)) {
      return this.shortTermToken.accessToken;
    }

    // Get long-term token first
    const longToken = await this.getLongTermToken();

    // Exchange for short-term token
    const response = await fetch(`${this.authUrl}/auth/tokens/short`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${longToken}`,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();
    this.shortTermToken = {
      accessToken: data.access_token,
      expiresAt: data.expires_at
    };

    return this.shortTermToken.accessToken;
  }

  async makeApiCall(endpoint, options = {}) {
    const token = await this.getShortTermToken();
    
    return fetch(endpoint, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    });
  }
}
```

#### Python
```python
import requests
from datetime import datetime, timezone

class C2MAuthClient:
    def __init__(self, client_id, client_secret, auth_url=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url or 'https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev'
        self.long_term_token = None
        self.short_term_token = None
    
    def get_short_term_token(self):
        # Check existing token
        if self.short_term_token and self._token_valid(self.short_term_token):
            return self.short_term_token['access_token']
        
        # Get long-term token
        long_token = self.get_long_term_token()
        
        # Exchange for short-term
        response = requests.post(
            f"{self.auth_url}/auth/tokens/short",
            headers={
                "Authorization": f"Bearer {long_token}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        
        self.short_term_token = response.json()
        return self.short_term_token['access_token']
```

---

## Testing Guide

### Quick Test with cURL

```bash
# Set credentials
AUTH_URL="https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev"
CLIENT_ID="test-client-123"
CLIENT_SECRET="super-secret-password-123"

# Get long-term token
LONG_TOKEN=$(curl -s -X POST "$AUTH_URL/auth/tokens/long" \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: $CLIENT_ID" \
  -d "{
    \"grant_type\": \"client_credentials\",
    \"client_id\": \"$CLIENT_ID\",
    \"client_secret\": \"$CLIENT_SECRET\"
  }" | jq -r '.access_token')

echo "Long token: ${LONG_TOKEN:0:20}..."

# Get short-term token
SHORT_TOKEN=$(curl -s -X POST "$AUTH_URL/auth/tokens/short" \
  -H "Authorization: Bearer $LONG_TOKEN" \
  -H "Content-Type: application/json" | jq -r '.access_token')

echo "Short token: ${SHORT_TOKEN:0:20}..."
```

### Test Credentials

**Development Environment**:
- Client ID: `test-client-123`
- Client Secret: Available in AWS Secrets Manager
- Auth URL: `https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev`

### AWS CLI Testing

```bash
# Get credentials from Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id c2m-api/dev/client-secrets \
  --query 'SecretString' \
  --output text | jq '."test-client-123"'

# Check token in DynamoDB
aws dynamodb get-item \
  --table-name c2m-token-store-dev \
  --key '{"tokenId": {"S": "tok_abc123"}}'
```

---

## Postman Configuration

### Pre-request Script Setup

The Postman collection includes an automatic JWT refresh script:

1. **Environment Variables Required**:
   ```
   authUrl: https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev
   clientId: test-client-123
   clientSecret: [your-secret]
   ```

2. **Script Behavior**:
   - Automatically obtains long-term token
   - Exchanges for short-term token
   - Refreshes before expiry
   - Skips auth for `/auth/*` endpoints

3. **Manual Token Operations**:
   ```javascript
   // Force refresh
   await pm.globals.get('refreshCognitoToken')();
   
   // Debug status
   pm.globals.get('debugCognitoAuth')();
   
   // Clear tokens
   pm.globals.get('clearCognitoTokens')();
   ```

### Postman vs Production Differences

| Aspect | Postman/Development | Production |
|--------|-------------------|------------|
| Token Storage | Environment variables | Secure vault/KMS |
| Token Refresh | Automatic (script) | Application logic |
| Error Handling | Console logging | Structured logging |
| Credentials | Plain text in env | Encrypted storage |
| Network | Direct HTTPS | VPN/Private link |

---

## Production vs Development

### Environment URLs

| Environment | Auth API | Main API | Purpose |
|-------------|----------|----------|---------|
| Development | https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev | TBD | Testing |
| Staging | TBD | TBD | Pre-production |
| Production | TBD | TBD | Live system |

### Security Considerations

**Development**:
- Test credentials in Secrets Manager
- Relaxed CORS for testing
- Detailed error messages
- Lower rate limits

**Production**:
- Customer-specific credentials
- Strict CORS policy
- Generic error messages
- Higher rate limits
- IP whitelisting available
- WAF protection enabled

---

## Quick Reference

### Common Commands

```bash
# Test auth endpoint
curl -I https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev/health

# Decode JWT (for debugging)
echo $TOKEN | cut -d. -f2 | base64 -d | jq .

# Check CloudWatch logs
aws logs tail /aws/lambda/issueLongToken-dev --follow

# List all tokens for a client
aws dynamodb query \
  --table-name c2m-token-store-dev \
  --index-name client-index \
  --key-condition-expression "clientId = :id" \
  --expression-attribute-values '{":id": {"S": "test-client-123"}}'
```

### Token Scopes

| Scope | Description |
|-------|-------------|
| `jobs:submit` | Submit print jobs |
| `jobs:read` | Read job status |
| `templates:read` | Access templates |
| `templates:write` | Modify templates |
| `tokens:revoke` | Revoke tokens |
| `bulk:operations` | Bulk submissions |

### Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 201 | Token created | Store token |
| 204 | Token revoked | Success (no content) |
| 401 | Unauthorized | Check credentials/token |
| 403 | Forbidden | Check scopes/permissions |
| 429 | Rate limited | Retry with backoff |

---

## Troubleshooting

### Common Issues

#### "Invalid client credentials"
- Verify client ID and secret match
- Check you're using correct environment
- Ensure credentials haven't been rotated

#### "Token expired"
- Implement automatic refresh logic
- Check token expiry before use
- Use appropriate TTL values

#### "Insufficient scopes"
- Request required scopes when getting tokens
- Check endpoint documentation
- Verify client has been granted scopes

#### "CORS error" (Browser)
- Use server-side authentication
- Check allowed origins configuration
- Verify preflight requests

### Debug Checklist

1. **Verify Endpoint**:
   ```bash
   curl -I $AUTH_URL/health
   ```

2. **Check Credentials**:
   ```bash
   echo "Client ID: $CLIENT_ID"
   echo "Secret exists: $([ -n "$CLIENT_SECRET" ] && echo "Yes" || echo "No")"
   ```

3. **Validate Token Format**:
   ```bash
   # Should have 3 parts
   echo $TOKEN | awk -F. '{print NF}'
   ```

4. **Review Logs**:
   - CloudWatch Logs for Lambda errors
   - API Gateway logs for request issues
   - DynamoDB for token status

### Getting Help

1. Check CloudWatch logs for detailed errors
2. Include request ID in support tickets
3. Verify with `aws sts get-caller-identity`
4. Test with minimal example first

---

## Migration Notes

This consolidated guide combines content from:
- `AUTHENTICATION_GUIDE.md` - General auth guide
- `JWT_AUTHENTICATION_README.md` - JWT specifics
- `AWS_JWT_AUTHENTICATION_ARCHITECTURE.md` - AWS architecture
- `AWS_AUTH_TESTING_GUIDE.md` - Testing procedures
- `QUICK_TEST_AWS_AUTH.md` - Quick testing
- `TOKEN_AUTH_POSTMAN_VS_PRODUCTION.md` - Environment differences
- `JWT_IMPLEMENTATION_SUMMARY.md` - Implementation details

Original documents are preserved in the `archive/` folder for reference.

---

*Last Updated: 2025-09-08*
*Consolidated by: Claude Code for internal team reference*
# C2M API V2 Authentication Guide

> **📌 Note**: This document has been superseded by **[AUTHENTICATION_CONSOLIDATED.md](./AUTHENTICATION_CONSOLIDATED.md)** which combines all authentication documentation into a single comprehensive guide.
>
> This file is preserved for backward compatibility and will be archived in a future update.

---

*Original content below for reference:*

This guide covers authentication for the C2M API V2, including JWT token management, endpoint usage, and integration with your applications.

## Table of Contents
- [Overview](#overview)
- [Authentication Architecture](#authentication-architecture)
- [Quick Start](#quick-start)
- [Authentication Endpoints](#authentication-endpoints)
- [Integration Guide](#integration-guide)
- [Token Management Best Practices](#token-management-best-practices)
- [Testing Authentication](#testing-authentication)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

---

## Overview

The C2M API V2 uses a two-tier JWT authentication system designed for security and scalability:

1. **Long-term tokens** (30-90 days) - For secure storage and minimal network requests
2. **Short-term tokens** (15 minutes) - For actual API calls with automatic expiration

This approach provides:
- ✅ Enhanced security through token isolation
- ✅ Reduced attack surface with short-lived tokens
- ✅ Efficient token management with minimal overhead
- ✅ Provider-agnostic design (works with any auth backend)

### Key Benefits
- **Security**: Short tokens limit exposure if compromised
- **Performance**: Long tokens reduce authentication requests
- **Flexibility**: Works with Cognito, Auth0, or custom providers
- **Scalability**: Stateless JWT tokens with distributed validation

---

## Authentication Architecture

### Components

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
                            ┌──────────▼──────────┐
                            │   Backend Services  │
                            ├────────────────────┤
                            │ • Cognito User Pool │
                            │ • DynamoDB         │
                            │ • Secrets Manager  │
                            └────────────────────┘
```

### Token Flow

1. **Initial Authentication**: Client credentials → Long-term token
2. **Token Exchange**: Long-term token → Short-term token
3. **API Calls**: Short-term token → Authorized requests
4. **Token Refresh**: Automatic before expiration

---

## Quick Start

### 1. Obtain Client Credentials

Contact your C2M administrator to receive:
- `client_id` - Your unique identifier
- `client_secret` - Your secret key (keep secure!)

### 2. Get Long-term Token

```bash
curl -X POST https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev/auth/tokens/long \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: your-client-id" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "scopes": ["jobs:submit", "templates:read"],
    "ttl_seconds": 2592000
  }'
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

### 3. Exchange for Short-term Token

```bash
curl -X POST https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev/auth/tokens/short \
  -H "Authorization: Bearer YOUR_LONG_TERM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scopes": ["jobs:submit"]
  }'
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

### 4. Make API Calls

```bash
curl -X POST https://api.c2m.example.com/jobs/submit/single/doc \
  -H "Authorization: Bearer YOUR_SHORT_TERM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... your job data ... }'
```

---

## Authentication Endpoints

### POST /auth/tokens/long

Issues a long-term token for API authentication.

**Request:**
```http
POST /auth/tokens/long
Content-Type: application/json
X-Client-Id: {client_id}

{
  "grant_type": "client_credentials",
  "client_id": "string",
  "client_secret": "string",
  "scopes": ["array", "of", "scopes"],
  "ttl_seconds": 2592000  // Optional, default 30 days
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `grant_type` | string | Yes | Must be "client_credentials" |
| `client_id` | string | Yes | Your client identifier |
| `client_secret` | string | Yes | Your secret key |
| `scopes` | array | No | Requested permissions |
| `ttl_seconds` | number | No | Token lifetime (max 7776000/90 days) |

**Response:** `201 Created`
```json
{
  "access_token": "string",
  "token_type": "Bearer",
  "expires_in": 2592000,
  "expires_at": "2024-02-29T12:00:00Z",
  "token_id": "tok_abc123",
  "scopes": ["jobs:submit", "templates:read", "tokens:revoke"]
}
```

### POST /auth/tokens/short

Exchanges a long-term token for a short-term token.

**Request:**
```http
POST /auth/tokens/short
Authorization: Bearer {long_term_token}
Content-Type: application/json

{
  "scopes": ["jobs:submit"]  // Optional scope narrowing
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scopes` | array | No | Narrow permissions (subset of long token) |

**Response:** `201 Created`
```json
{
  "access_token": "string",
  "token_type": "Bearer",
  "expires_in": 900,
  "expires_at": "2024-01-29T10:15:00Z",
  "token_id": "stk_xyz789"
}
```

### POST /auth/tokens/{tokenId}/revoke

Revokes a token (both long-term and short-term).

**Request:**
```http
POST /auth/tokens/{tokenId}/revoke
Authorization: Bearer {token_with_revoke_permission}
```

**Response:** `204 No Content`

**Notes:**
- Revoking a long-term token also revokes all associated short-term tokens
- Requires `tokens:revoke` scope
- Idempotent - revoking already revoked token returns success

---

## Integration Guide

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class C2MAuthClient {
  constructor(config) {
    this.clientId = config.clientId;
    this.clientSecret = config.clientSecret;
    this.authUrl = config.authUrl || 'https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev';
    this.apiUrl = config.apiUrl;
    this.longTermToken = null;
    this.shortTermToken = null;
  }

  async getLongTermToken() {
    // Check if we have a valid long-term token
    if (this.longTermToken && new Date() < new Date(this.longTermToken.expiresAt)) {
      return this.longTermToken.accessToken;
    }

    // Request new long-term token
    const response = await axios.post(`${this.authUrl}/auth/tokens/long`, {
      grant_type: 'client_credentials',
      client_id: this.clientId,
      client_secret: this.clientSecret,
      scopes: ['jobs:submit', 'templates:read', 'tokens:revoke'],
      ttl_seconds: 2592000 // 30 days
    }, {
      headers: {
        'Content-Type': 'application/json',
        'X-Client-Id': this.clientId
      }
    });

    this.longTermToken = {
      accessToken: response.data.access_token,
      expiresAt: response.data.expires_at,
      tokenId: response.data.token_id
    };

    return this.longTermToken.accessToken;
  }

  async getShortTermToken() {
    // Check if we have a valid short-term token
    if (this.shortTermToken && new Date() < new Date(this.shortTermToken.expiresAt)) {
      return this.shortTermToken.accessToken;
    }

    // Get long-term token first
    const longToken = await this.getLongTermToken();

    // Exchange for short-term token
    const response = await axios.post(`${this.authUrl}/auth/tokens/short`, {
      scopes: ['jobs:submit']
    }, {
      headers: {
        'Authorization': `Bearer ${longToken}`,
        'Content-Type': 'application/json'
      }
    });

    this.shortTermToken = {
      accessToken: response.data.access_token,
      expiresAt: response.data.expires_at,
      tokenId: response.data.token_id
    };

    return this.shortTermToken.accessToken;
  }

  async makeApiCall(method, endpoint, data = null) {
    const token = await this.getShortTermToken();
    
    return axios({
      method,
      url: `${this.apiUrl}${endpoint}`,
      data,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
  }
}

// Usage
const client = new C2MAuthClient({
  clientId: 'your-client-id',
  clientSecret: 'your-client-secret',
  apiUrl: 'https://api.c2m.example.com'
});

// Submit a job
const job = await client.makeApiCall('POST', '/jobs/submit/single/doc', {
  documentSource: { url: 'https://example.com/doc.pdf' },
  recipientAddress: { /* ... */ }
});
```

### Python Example

```python
import requests
from datetime import datetime, timezone
import time

class C2MAuthClient:
    def __init__(self, client_id, client_secret, auth_url=None, api_url=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url or 'https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev'
        self.api_url = api_url
        self.long_term_token = None
        self.short_term_token = None
    
    def _token_valid(self, token_data):
        if not token_data:
            return False
        expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
        return datetime.now(timezone.utc) < expires_at
    
    def get_long_term_token(self):
        # Check existing token
        if self.long_term_token and self._token_valid(self.long_term_token):
            return self.long_term_token['access_token']
        
        # Request new token
        response = requests.post(
            f"{self.auth_url}/auth/tokens/long",
            json={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scopes": ["jobs:submit", "templates:read", "tokens:revoke"],
                "ttl_seconds": 2592000
            },
            headers={
                "Content-Type": "application/json",
                "X-Client-Id": self.client_id
            }
        )
        response.raise_for_status()
        
        self.long_term_token = response.json()
        return self.long_term_token['access_token']
    
    def get_short_term_token(self):
        # Check existing token
        if self.short_term_token and self._token_valid(self.short_term_token):
            return self.short_term_token['access_token']
        
        # Get long-term token
        long_token = self.get_long_term_token()
        
        # Exchange for short-term
        response = requests.post(
            f"{self.auth_url}/auth/tokens/short",
            json={"scopes": ["jobs:submit"]},
            headers={
                "Authorization": f"Bearer {long_token}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        
        self.short_term_token = response.json()
        return self.short_term_token['access_token']
    
    def make_api_call(self, method, endpoint, data=None):
        token = self.get_short_term_token()
        
        response = requests.request(
            method=method,
            url=f"{self.api_url}{endpoint}",
            json=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
client = C2MAuthClient(
    client_id='your-client-id',
    client_secret='your-client-secret',
    api_url='https://api.c2m.example.com'
)

# Submit a job
job = client.make_api_call('POST', '/jobs/submit/single/doc', {
    'documentSource': {'url': 'https://example.com/doc.pdf'},
    'recipientAddress': { ... }
})
```

### Postman Pre-request Script

For Postman users, this script automatically manages token refresh:

```javascript
// JWT Token Auto-Refresh Script
const authUrl = pm.environment.get('authUrl') || 'https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev';
const clientId = pm.environment.get('clientId');
const clientSecret = pm.environment.get('clientSecret');

// Skip auth for auth endpoints
if (pm.request.url.path.join('/').includes('auth/')) {
    console.log('Skipping auth for auth endpoint');
    return;
}

// Function to get long-term token
async function getLongTermToken() {
    const longTermExpiry = pm.environment.get('longTermExpiry');
    
    if (longTermExpiry && new Date() < new Date(longTermExpiry)) {
        console.log('Using existing long-term token');
        return pm.environment.get('longTermToken');
    }
    
    console.log('Obtaining new long-term token...');
    
    const response = await pm.sendRequest({
        url: `${authUrl}/auth/tokens/long`,
        method: 'POST',
        header: {
            'Content-Type': 'application/json',
            'X-Client-Id': clientId
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                grant_type: 'client_credentials',
                client_id: clientId,
                client_secret: clientSecret,
                scopes: ['jobs:submit', 'templates:read', 'tokens:revoke'],
                ttl_seconds: 2592000
            })
        }
    });
    
    if (response.code !== 201) {
        throw new Error(`Failed to get long-term token: ${response.status}`);
    }
    
    const data = response.json();
    pm.environment.set('longTermToken', data.access_token);
    pm.environment.set('longTermExpiry', data.expires_at);
    
    return data.access_token;
}

// Function to get short-term token
async function getShortTermToken() {
    const tokenExpiry = pm.environment.get('tokenExpiry');
    
    // Check if we need a new token (5 second buffer)
    if (tokenExpiry && new Date(new Date().getTime() + 5000) < new Date(tokenExpiry)) {
        console.log('Using existing short-term token');
        return;
    }
    
    const longToken = await getLongTermToken();
    
    console.log('Exchanging for short-term token...');
    
    const response = await pm.sendRequest({
        url: `${authUrl}/auth/tokens/short`,
        method: 'POST',
        header: {
            'Authorization': `Bearer ${longToken}`,
            'Content-Type': 'application/json'
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                scopes: ['jobs:submit']
            })
        }
    });
    
    if (response.code !== 201) {
        throw new Error(`Failed to get short-term token: ${response.status}`);
    }
    
    const data = response.json();
    pm.environment.set('token', data.access_token);
    pm.environment.set('tokenExpiry', data.expires_at);
    
    console.log(`Token obtained, expires at ${data.expires_at}`);
}

// Main execution
(async () => {
    try {
        await getShortTermToken();
        pm.request.headers.add({
            key: 'Authorization',
            value: `Bearer ${pm.environment.get('token')}`
        });
        console.log('Authorization header set');
    } catch (error) {
        console.error('Authentication failed:', error);
        throw error;
    }
})();
```

---

## Token Management Best Practices

### Storage

**DO:**
- Store long-term tokens securely (encrypted at rest)
- Use environment variables or secure vaults
- Implement proper access controls

**DON'T:**
- Store tokens in source code
- Log tokens in plain text
- Share tokens between environments

### Refresh Strategy

1. **Proactive Refresh**: Refresh tokens before expiry
   ```javascript
   // Refresh 1 minute before expiry
   const bufferTime = 60 * 1000; // 1 minute
   const shouldRefresh = new Date().getTime() + bufferTime > expiryTime;
   ```

2. **Retry on 401**: Handle token expiration gracefully
   ```javascript
   try {
     response = await makeApiCall();
   } catch (error) {
     if (error.response?.status === 401) {
       await refreshToken();
       response = await makeApiCall(); // Retry
     }
   }
   ```

3. **Token Hierarchy**: Remember the relationship
   - Long token → Multiple short tokens
   - Revoking long token → Revokes all short tokens

### Scopes

Use minimal required scopes:
- `jobs:submit` - Submit print jobs
- `jobs:read` - Read job status
- `templates:read` - Access templates
- `templates:write` - Modify templates
- `tokens:revoke` - Revoke tokens
- `bulk:operations` - Bulk job submission

---

## Testing Authentication

### Using cURL

```bash
# 1. Set variables
AUTH_URL="https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev"
CLIENT_ID="test-client-123"
CLIENT_SECRET="your-secret"

# 2. Get long-term token
LONG_TOKEN=$(curl -s -X POST "$AUTH_URL/auth/tokens/long" \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: $CLIENT_ID" \
  -d "{
    \"grant_type\": \"client_credentials\",
    \"client_id\": \"$CLIENT_ID\",
    \"client_secret\": \"$CLIENT_SECRET\",
    \"scopes\": [\"jobs:submit\", \"templates:read\"],
    \"ttl_seconds\": 3600
  }" | jq -r '.access_token')

echo "Long token: ${LONG_TOKEN:0:20}..."

# 3. Get short-term token
SHORT_TOKEN=$(curl -s -X POST "$AUTH_URL/auth/tokens/short" \
  -H "Authorization: Bearer $LONG_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"scopes": ["jobs:submit"]}' | jq -r '.access_token')

echo "Short token: ${SHORT_TOKEN:0:20}..."

# 4. Test API call (when deployed)
curl -X GET "https://api.c2m.example.com/health" \
  -H "Authorization: Bearer $SHORT_TOKEN"
```

### Using Postman

1. Import the environment file from `postman/environments/c2m-api-dev.json`
2. Set your client credentials in environment variables
3. The pre-request script handles authentication automatically
4. Send any request - tokens are managed transparently

### Test Credentials

For development/testing:
- **Client ID**: `test-client-123`
- **Client Secret**: Available from your administrator
- **Auth URL**: `https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev`

---

## Troubleshooting

### Common Errors

#### 401 Unauthorized
```json
{
  "error": "Invalid credentials",
  "message": "The provided client credentials are invalid"
}
```
**Solutions:**
- Verify client ID and secret
- Check you're using the correct environment
- Ensure credentials haven't been rotated

#### 403 Forbidden
```json
{
  "error": "Insufficient permissions",
  "message": "Token lacks required scopes"
}
```
**Solutions:**
- Request required scopes when getting tokens
- Check endpoint documentation for required scopes
- Ensure your client has been granted the scopes

#### Token Expired
```json
{
  "error": "Token expired",
  "message": "The access token has expired"
}
```
**Solutions:**
- Implement automatic token refresh
- Check token expiry before making calls
- Use appropriate TTL for your use case

### Debug Checklist

1. **Verify Credentials**
   ```bash
   echo "Client ID: $CLIENT_ID"
   echo "Secret length: ${#CLIENT_SECRET}"
   ```

2. **Check Token Format**
   ```bash
   # JWT should have 3 parts separated by dots
   echo $TOKEN | awk -F. '{print NF}' # Should output: 3
   ```

3. **Decode Token** (for debugging only)
   ```bash
   echo $TOKEN | cut -d. -f2 | base64 -d 2>/dev/null | jq .
   ```

4. **Test Auth Endpoint**
   ```bash
   curl -I "$AUTH_URL/health"
   ```

### Getting Help

1. Check CloudWatch logs for detailed errors
2. Verify your client configuration with administrator
3. Review the API documentation for endpoint requirements
4. Contact support with request ID from error responses

---

## Security Considerations

### Best Practices

1. **Credential Security**
   - Never commit credentials to version control
   - Use environment variables or secure vaults
   - Rotate credentials regularly (quarterly)
   - Use different credentials per environment

2. **Token Handling**
   - Transmit tokens only over HTTPS
   - Don't log tokens in application logs
   - Clear tokens from memory after use
   - Implement secure token storage

3. **Network Security**
   - Whitelist IP addresses when possible
   - Use VPN for additional security
   - Monitor for unusual activity patterns
   - Implement request signing for critical operations

4. **Monitoring**
   - Track authentication failures
   - Monitor token usage patterns
   - Set up alerts for anomalies
   - Regular security audits

### Compliance

The authentication system supports:
- SOC 2 compliance
- HIPAA requirements (with BAA)
- PCI DSS standards
- GDPR data protection

For specific compliance questions, contact your security team.

---

## Migration from V1

If migrating from C2M API V1:

1. **Key Differences**:
   - V2 uses JWT tokens (not API keys)
   - Two-tier token system
   - Scoped permissions
   - Token revocation support

2. **Migration Steps**:
   - Obtain V2 client credentials
   - Update authentication logic
   - Test in development environment
   - Gradually migrate endpoints
   - Monitor both versions during transition

3. **Backwards Compatibility**:
   - V1 API keys remain valid during transition
   - Both authentication methods supported temporarily
   - Deprecation notices provided in advance

---

## Next Steps

1. **Get Started**: Obtain client credentials from your administrator
2. **Test Authentication**: Use the quick start examples
3. **Integrate**: Add authentication to your application
4. **Monitor**: Set up logging and monitoring
5. **Optimize**: Implement token caching and refresh strategies

For additional resources:
- [API Documentation](../README.md)
- [Postman Collection](./POSTMAN_COMPLETE_GUIDE.md)
- [SDK Examples](../sdk/)

---

*Last Updated: 2025-09-08*
*Consolidates authentication documentation from c2m-api-repo and c2m-api-v2-security repositories*
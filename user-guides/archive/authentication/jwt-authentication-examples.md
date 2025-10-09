# JWT Authentication Examples

This document provides comprehensive examples of how to authenticate with the C2M API using JWT tokens.

## Overview

The C2M API uses a two-token authentication system:
- **Long-term tokens** (30-90 days): For server-to-server communication
- **Short-term tokens** (15 minutes): For actual API requests

## Authentication Flow

```
1. Obtain long-term token (one-time setup)
   ↓
2. Exchange for short-term token (every 15 minutes)
   ↓
3. Use short-term token for API requests
```

## Client Examples

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class C2MAuthClient {
  constructor(config) {
    this.baseUrl = config.baseUrl || 'https://api.example.com/v1';
    this.clientId = config.clientId;
    this.clientSecret = config.clientSecret;
    this.longTermToken = null;
    this.shortTermToken = null;
    this.tokenExpiry = null;
  }

  // Get long-term token using client credentials
  async getLongTermToken() {
    try {
      const response = await axios.post(`${this.baseUrl}/auth/tokens/long`, {
        grant_type: 'client_credentials',
        client_id: this.clientId,
        client_secret: this.clientSecret,
        scopes: ['jobs:submit', 'templates:read'],
        ttl_seconds: 2592000 // 30 days
      }, {
        headers: {
          'Content-Type': 'application/json',
          'X-Client-Id': this.clientId
        }
      });

      this.longTermToken = response.data.access_token;
      console.log('Long-term token obtained:', response.data.token_id);
      return this.longTermToken;
    } catch (error) {
      console.error('Failed to get long-term token:', error.response?.data);
      throw error;
    }
  }

  // Exchange long-term token for short-term token
  async getShortTermToken() {
    if (!this.longTermToken) {
      await this.getLongTermToken();
    }

    try {
      const response = await axios.post(`${this.baseUrl}/auth/tokens/short`, {
        scopes: ['jobs:submit'] // Optional: narrow the scope
      }, {
        headers: {
          'Authorization': `Bearer ${this.longTermToken}`,
          'Content-Type': 'application/json'
        }
      });

      this.shortTermToken = response.data.access_token;
      this.tokenExpiry = new Date(response.data.expires_at);
      console.log('Short-term token obtained, expires:', this.tokenExpiry);
      return this.shortTermToken;
    } catch (error) {
      console.error('Failed to get short-term token:', error.response?.data);
      throw error;
    }
  }

  // Get valid short-term token (auto-refresh if expired)
  async getValidToken() {
    const now = new Date();
    const bufferTime = 60000; // 1 minute buffer before expiry

    if (!this.shortTermToken || !this.tokenExpiry || 
        (this.tokenExpiry - now) < bufferTime) {
      await this.getShortTermToken();
    }

    return this.shortTermToken;
  }

  // Make authenticated API request
  async makeAuthenticatedRequest(method, endpoint, data = null) {
    const token = await this.getValidToken();

    try {
      const response = await axios({
        method,
        url: `${this.baseUrl}${endpoint}`,
        data,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        // Token might be invalid, try refreshing
        await this.getShortTermToken();
        return this.makeAuthenticatedRequest(method, endpoint, data);
      }
      throw error;
    }
  }

  // Revoke a token
  async revokeToken(tokenId) {
    const token = await this.getValidToken();

    try {
      await axios.post(`${this.baseUrl}/auth/tokens/${tokenId}/revoke`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      console.log(`Token ${tokenId} revoked successfully`);
    } catch (error) {
      console.error('Failed to revoke token:', error.response?.data);
      throw error;
    }
  }
}

// Usage example
async function example() {
  const client = new C2MAuthClient({
    clientId: 'c2m_your_client_id',
    clientSecret: 'your_client_secret'
  });

  try {
    // Submit a job using authenticated request
    const jobData = {
      jobTemplate: 'standard-letter',
      paymentDetails: {
        creditCardDetails: {
          cardType: 'visa',
          cardNumber: '4111111111111111',
          expirationDate: { month: 12, year: 2025 },
          cvv: 123
        }
      }
    };

    const result = await client.makeAuthenticatedRequest(
      'POST', 
      '/jobs/single-doc-job-template', 
      jobData
    );

    console.log('Job submitted:', result.jobId);
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Python Example

```python
import requests
from datetime import datetime, timedelta
import time

class C2MAuthClient:
    def __init__(self, base_url='https://api.example.com/v1', 
                 client_id=None, client_secret=None):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.long_term_token = None
        self.short_term_token = None
        self.token_expiry = None
    
    def get_long_term_token(self):
        """Obtain long-term token using client credentials"""
        response = requests.post(
            f"{self.base_url}/auth/tokens/long",
            json={
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scopes': ['jobs:submit', 'templates:read'],
                'ttl_seconds': 2592000  # 30 days
            },
            headers={
                'Content-Type': 'application/json',
                'X-Client-Id': self.client_id
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            self.long_term_token = data['access_token']
            print(f"Long-term token obtained: {data['token_id']}")
            return self.long_term_token
        else:
            raise Exception(f"Failed to get long-term token: {response.text}")
    
    def get_short_term_token(self):
        """Exchange long-term token for short-term token"""
        if not self.long_term_token:
            self.get_long_term_token()
        
        response = requests.post(
            f"{self.base_url}/auth/tokens/short",
            json={'scopes': ['jobs:submit']},  # Optional scope narrowing
            headers={
                'Authorization': f'Bearer {self.long_term_token}',
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            self.short_term_token = data['access_token']
            self.token_expiry = datetime.fromisoformat(
                data['expires_at'].replace('Z', '+00:00')
            )
            print(f"Short-term token obtained, expires: {self.token_expiry}")
            return self.short_term_token
        else:
            raise Exception(f"Failed to get short-term token: {response.text}")
    
    def get_valid_token(self):
        """Get valid short-term token (auto-refresh if expired)"""
        now = datetime.now(tz=self.token_expiry.tzinfo if self.token_expiry else None)
        buffer_time = timedelta(minutes=1)
        
        if (not self.short_term_token or not self.token_expiry or 
            self.token_expiry - now < buffer_time):
            self.get_short_term_token()
        
        return self.short_term_token
    
    def make_authenticated_request(self, method, endpoint, json_data=None):
        """Make authenticated API request with automatic token refresh"""
        token = self.get_valid_token()
        
        response = requests.request(
            method=method,
            url=f"{self.base_url}{endpoint}",
            json=json_data,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code == 401:
            # Token might be invalid, try refreshing
            self.get_short_term_token()
            token = self.short_term_token
            response = requests.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                json=json_data,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
            )
        
        response.raise_for_status()
        return response.json()
    
    def revoke_token(self, token_id):
        """Revoke a token by ID"""
        token = self.get_valid_token()
        
        response = requests.post(
            f"{self.base_url}/auth/tokens/{token_id}/revoke",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 204:
            print(f"Token {token_id} revoked successfully")
        else:
            raise Exception(f"Failed to revoke token: {response.text}")

# Usage example
def main():
    client = C2MAuthClient(
        client_id='c2m_your_client_id',
        client_secret='your_client_secret'
    )
    
    try:
        # Submit a job
        job_data = {
            'jobTemplate': 'standard-letter',
            'paymentDetails': {
                'creditCardDetails': {
                    'cardType': 'visa',
                    'cardNumber': '4111111111111111',
                    'expirationDate': {'month': 12, 'year': 2025},
                    'cvv': 123
                }
            }
        }
        
        result = client.make_authenticated_request(
            'POST',
            '/jobs/single-doc-job-template',
            job_data
        )
        
        print(f"Job submitted: {result['jobId']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

### cURL Examples

```bash
# 1. Get long-term token with client credentials
curl -X POST https://api.example.com/v1/auth/tokens/long \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: c2m_your_client_id" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "c2m_your_client_id",
    "client_secret": "your_client_secret",
    "scopes": ["jobs:submit", "templates:read"],
    "ttl_seconds": 2592000
  }'

# Response:
# {
#   "token_type": "Bearer",
#   "access_token": "lt_0d51e9bd2f6449cf...",
#   "expires_in": 2592000,
#   "expires_at": "2025-09-25T22:45:00Z",
#   "scopes": ["jobs:submit", "templates:read"],
#   "token_id": "tok_lt_b8e0aa"
# }

# 2. Exchange for short-term token
LONG_TOKEN="lt_0d51e9bd2f6449cf..."

curl -X POST https://api.example.com/v1/auth/tokens/short \
  -H "Authorization: Bearer $LONG_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scopes": ["jobs:submit"]
  }'

# Response:
# {
#   "token_type": "Bearer",
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "expires_in": 900,
#   "expires_at": "2025-08-26T22:45:00Z",
#   "scopes": ["jobs:submit"],
#   "token_id": "tok_st_9f3d2c"
# }

# 3. Use short-term token for API request
SHORT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST https://api.example.com/v1/jobs/single-doc-job-template \
  -H "Authorization: Bearer $SHORT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jobTemplate": "standard-letter",
    "paymentDetails": {
      "creditCardDetails": {
        "cardType": "visa",
        "cardNumber": "4111111111111111",
        "expirationDate": {"month": 12, "year": 2025},
        "cvv": 123
      }
    }
  }'

# 4. Revoke a token
curl -X POST https://api.example.com/v1/auth/tokens/tok_st_9f3d2c/revoke \
  -H "Authorization: Bearer $SHORT_TOKEN"
```

### Alternative Authentication Methods

#### Using OTP (One-Time Password)

```javascript
// Get long-term token with OTP
const response = await axios.post(`${baseUrl}/auth/tokens/long`, {
  grant_type: 'client_credentials',
  client_id: 'c2m_your_client_id',
  otp_code: '123456',  // From authenticator app
  scopes: ['jobs:*'],
  ttl_seconds: 7776000  // 90 days
});
```

#### Using Signed Assertion (JWT Bearer)

```javascript
// Create signed JWT assertion
const jwt = require('jsonwebtoken');

const assertion = jwt.sign({
  iss: 'c2m_your_client_id',
  sub: 'c2m_your_client_id',
  aud: 'https://api.example.com',
  exp: Math.floor(Date.now() / 1000) + 300,
  iat: Math.floor(Date.now() / 1000)
}, privateKey, { algorithm: 'RS256' });

// Exchange assertion for long-term token
const response = await axios.post(`${baseUrl}/auth/tokens/long`, {
  grant_type: 'assertion',
  client_id: 'c2m_your_client_id',
  assertion_type: 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
  assertion: assertion,
  scopes: ['jobs:submit', 'templates:read']
});
```

## Error Handling

### Common Error Responses

```json
// 401 Unauthorized - Invalid or expired token
{
  "code": "invalid_token",
  "message": "The provided token is expired or invalid"
}

// 403 Forbidden - Insufficient scope
{
  "code": "insufficient_scope",
  "message": "The token lacks the required scope for this operation"
}

// 429 Too Many Requests - Rate limited
{
  "code": "rate_limited",
  "message": "Too many requests. Please retry after 60 seconds."
}
```

### Retry Logic Example

```javascript
async function makeRequestWithRetry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.response?.status === 429) {
        // Rate limited - wait and retry
        const retryAfter = error.response.headers['retry-after'] || 60;
        console.log(`Rate limited. Waiting ${retryAfter} seconds...`);
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      } else if (error.response?.status === 401 && i < maxRetries - 1) {
        // Token invalid - refresh and retry
        console.log('Token invalid, refreshing...');
        await this.getShortTermToken();
      } else {
        throw error;
      }
    }
  }
}
```

## Best Practices

1. **Token Storage**: Store long-term tokens securely (e.g., environment variables, secure key storage)
2. **Token Refresh**: Implement automatic token refresh before expiry (with buffer time)
3. **Scope Management**: Request only the scopes you need
4. **Error Handling**: Implement proper retry logic for 401 and 429 errors
5. **Token Lifecycle**: Revoke tokens when no longer needed
6. **Monitoring**: Log token operations for audit trails

## Security Considerations

1. Never expose client secrets in client-side code
2. Use HTTPS for all API communications
3. Rotate long-term tokens periodically
4. Monitor for unusual token usage patterns
5. Implement proper token storage and transmission
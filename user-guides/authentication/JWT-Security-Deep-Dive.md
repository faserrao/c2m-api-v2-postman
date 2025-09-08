# JWT Security Deep Dive - C2M API V2

## Overview

This document provides an in-depth analysis of the JWT (JSON Web Token) implementation in the C2M API V2, identifying potential vulnerabilities and providing specific remediation strategies.

## JWT Architecture Analysis

### Current Implementation

The C2M API uses a two-tier JWT system:

```
Long-term Token (30-90 days) → Short-term Token (15 minutes) → API Access
```

### Token Structure Analysis

#### Expected JWT Structure
```json
{
  "header": {
    "alg": "HS256",  // Symmetric algorithm (potential weakness)
    "typ": "JWT"
  },
  "payload": {
    "sub": "client_id",
    "iss": "c2m-api",
    "exp": 1234567890,
    "iat": 1234567890,
    "scopes": ["jobs:submit", "templates:read"],
    "token_type": "long" | "short",
    "jti": "unique_token_id"  // For revocation
  },
  "signature": "HMACSHA256(...)"
}
```

## Identified Vulnerabilities

### 1. Algorithm Confusion Attack

**Risk**: High  
**Description**: If the API accepts multiple algorithms (HS256, RS256, none), attackers could downgrade security.

**Attack Vector**:
```javascript
// Malicious token with 'none' algorithm
const maliciousToken = {
  header: { alg: "none", typ: "JWT" },
  payload: { sub: "attacker", scopes: ["*"] }
};
```

**Mitigation**:
```javascript
// Secure JWT verification
const jwt = require('jsonwebtoken');

function verifyToken(token, secret) {
  return jwt.verify(token, secret, {
    algorithms: ['HS256'], // Only allow HS256
    clockTolerance: 30,    // 30 second clock skew
    maxAge: '15m'          // Enforce max age
  });
}
```

### 2. Weak Secret Key

**Risk**: Critical  
**Description**: Using weak or default secrets enables token forgery.

**Attack Scenario**:
- Brute force weak secrets
- Rainbow table attacks
- Default secret exploitation

**Mitigation**:
```javascript
// Generate cryptographically strong secrets
const crypto = require('crypto');

function generateJWTSecret() {
  return crypto.randomBytes(64).toString('hex'); // 512-bit secret
}

// Store in secure secret management
process.env.JWT_SECRET = generateJWTSecret();
```

### 3. Token Replay Attacks

**Risk**: Medium  
**Description**: Stolen tokens can be reused until expiration.

**Attack Vector**:
1. Intercept valid token (MitM, XSS, logs)
2. Replay token for unauthorized access
3. Maintain access until expiration

**Mitigation**:
```javascript
// Implement token binding and request signatures
function generateSecureRequest(token, payload) {
  const timestamp = Date.now();
  const nonce = crypto.randomBytes(16).toString('hex');
  
  const signature = crypto
    .createHmac('sha256', token)
    .update(`${timestamp}:${nonce}:${JSON.stringify(payload)}`)
    .digest('hex');
    
  return {
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-Request-Timestamp': timestamp,
      'X-Request-Nonce': nonce,
      'X-Request-Signature': signature
    }
  };
}
```

### 4. Insufficient Token Revocation

**Risk**: Medium  
**Description**: Current revocation endpoint may not immediately invalidate tokens.

**Current Implementation**:
```
POST /auth/tokens/{tokenId}/revoke
```

**Issues**:
- Requires knowledge of tokenId
- May not work for distributed systems
- No bulk revocation capability

**Enhanced Revocation System**:
```javascript
// Implement revocation with Redis
const redis = require('redis');
const client = redis.createClient();

async function revokeToken(tokenId, jti) {
  // Add to revocation list with TTL matching token expiry
  const ttl = 90 * 24 * 60 * 60; // 90 days for long tokens
  await client.setex(`revoked:${jti}`, ttl, tokenId);
}

async function isTokenRevoked(jti) {
  const result = await client.get(`revoked:${jti}`);
  return result !== null;
}

// Check revocation on every request
async function verifyTokenWithRevocation(token) {
  const decoded = jwt.decode(token);
  
  if (await isTokenRevoked(decoded.jti)) {
    throw new Error('Token has been revoked');
  }
  
  return jwt.verify(token, process.env.JWT_SECRET);
}
```

### 5. Long Token Lifetime Exposure

**Risk**: Medium  
**Description**: 90-day tokens increase compromise impact.

**Attack Impact**:
- Extended unauthorized access
- Difficult incident response
- Compliance violations

**Mitigation Strategy**:
```javascript
// Implement progressive token lifetime reduction
const TOKEN_LIFETIMES = {
  initial: 30 * 24 * 60 * 60,        // 30 days
  refreshed: 7 * 24 * 60 * 60,      // 7 days
  high_security: 24 * 60 * 60,      // 24 hours
  short_lived: 15 * 60               // 15 minutes
};

function issueToken(clientId, context) {
  const lifetime = determineTokenLifetime(context);
  
  return jwt.sign({
    sub: clientId,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + lifetime,
    jti: generateTokenId(),
    context: context
  }, process.env.JWT_SECRET);
}
```

## Advanced Attack Scenarios

### 1. Token Sidejacking

**Scenario**: Attacker obtains valid token through various means
**Impact**: Full API access with victim's permissions

**Prevention**:
```javascript
// Bind tokens to client characteristics
function createBoundToken(clientId, request) {
  const fingerprint = crypto
    .createHash('sha256')
    .update(request.ip + request.headers['user-agent'])
    .digest('hex');
    
  return jwt.sign({
    sub: clientId,
    fingerprint: fingerprint,
    // ... other claims
  }, process.env.JWT_SECRET);
}

// Verify binding on each request
function verifyBoundToken(token, request) {
  const decoded = jwt.verify(token, process.env.JWT_SECRET);
  const currentFingerprint = crypto
    .createHash('sha256')
    .update(request.ip + request.headers['user-agent'])
    .digest('hex');
    
  if (decoded.fingerprint !== currentFingerprint) {
    throw new Error('Token binding mismatch');
  }
  
  return decoded;
}
```

### 2. Privilege Escalation

**Scenario**: Modify token scopes to gain additional permissions
**Impact**: Access to restricted operations

**Prevention**:
```javascript
// Implement scope validation with digital signatures
function createScopedToken(clientId, requestedScopes) {
  const allowedScopes = validateClientScopes(clientId, requestedScopes);
  
  const scopeSignature = crypto
    .createHmac('sha256', process.env.SCOPE_SECRET)
    .update(allowedScopes.sort().join(','))
    .digest('hex');
    
  return jwt.sign({
    sub: clientId,
    scopes: allowedScopes,
    scope_sig: scopeSignature
  }, process.env.JWT_SECRET);
}
```

## Security Testing Procedures

### 1. JWT Vulnerability Scanner

```python
import jwt
import requests
import json

class JWTSecurityTester:
    def __init__(self, base_url, valid_token):
        self.base_url = base_url
        self.valid_token = valid_token
        
    def test_algorithm_confusion(self):
        """Test for algorithm confusion vulnerability"""
        decoded = jwt.decode(self.valid_token, options={"verify_signature": False})
        
        # Try 'none' algorithm
        none_token = jwt.encode(decoded, '', algorithm='none')
        response = requests.get(
            f"{self.base_url}/api/protected",
            headers={"Authorization": f"Bearer {none_token}"}
        )
        
        if response.status_code == 200:
            return "VULNERABLE: Accepts 'none' algorithm"
        return "SECURE: Rejects 'none' algorithm"
        
    def test_expired_token(self):
        """Test expired token handling"""
        decoded = jwt.decode(self.valid_token, options={"verify_signature": False})
        decoded['exp'] = 1  # Very old timestamp
        
        # Create expired token (requires secret)
        expired_token = jwt.encode(decoded, 'dummy_secret', algorithm='HS256')
        response = requests.get(
            f"{self.base_url}/api/protected",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        if response.status_code == 401:
            return "SECURE: Properly rejects expired tokens"
        return "VULNERABLE: Accepts expired tokens"
```

### 2. Token Lifetime Analyzer

```bash
#!/bin/bash
# Analyze token lifetimes and patterns

# Extract token claims
decode_jwt() {
    echo "$1" | cut -d. -f2 | base64 -d 2>/dev/null | jq .
}

# Test token refresh patterns
test_token_refresh() {
    local long_token=$1
    local api_url=$2
    
    echo "Testing token refresh patterns..."
    
    # Get initial short token
    short_token=$(curl -s -X POST "$api_url/auth/tokens/short" \
        -H "Authorization: Bearer $long_token" | jq -r .access_token)
    
    # Decode and analyze
    echo "Short token claims:"
    decode_jwt "$short_token"
    
    # Test rapid refresh
    for i in {1..5}; do
        sleep 2
        new_token=$(curl -s -X POST "$api_url/auth/tokens/short" \
            -H "Authorization: Bearer $long_token" | jq -r .access_token)
        
        if [ "$new_token" != "$short_token" ]; then
            echo "Token $i differs - possible jti implementation"
        fi
    done
}
```

## Recommended JWT Security Configuration

```javascript
// Secure JWT configuration for C2M API
const jwtConfig = {
  // Use RS256 for better security
  algorithm: 'RS256',
  
  // Token lifetimes
  longTokenTTL: 7 * 24 * 60 * 60,  // 7 days max
  shortTokenTTL: 5 * 60,            // 5 minutes
  
  // Security options
  options: {
    issuer: 'c2m-api-v2',
    audience: 'c2m-api-clients',
    clockTolerance: 30,
    maxAge: '7d'
  },
  
  // Required claims
  requiredClaims: ['sub', 'iat', 'exp', 'jti', 'iss', 'aud'],
  
  // Rotation schedule
  keyRotationDays: 30,
  
  // Revocation check
  checkRevocation: true,
  
  // Request binding
  bindToRequest: true
};

// Implementation example
class SecureJWTManager {
  constructor(config) {
    this.config = config;
    this.keys = this.loadKeys();
    this.revocationStore = new RevocationStore();
  }
  
  async issueToken(subject, scopes, context) {
    const jti = generateSecureId();
    const iat = Math.floor(Date.now() / 1000);
    const exp = iat + this.config.longTokenTTL;
    
    const payload = {
      sub: subject,
      scopes: scopes,
      iat: iat,
      exp: exp,
      jti: jti,
      iss: this.config.options.issuer,
      aud: this.config.options.audience,
      context: context
    };
    
    return jwt.sign(payload, this.keys.private, {
      algorithm: this.config.algorithm
    });
  }
  
  async verifyToken(token, request) {
    // Check revocation first
    const decoded = jwt.decode(token);
    if (await this.revocationStore.isRevoked(decoded.jti)) {
      throw new Error('Token has been revoked');
    }
    
    // Verify with public key
    const verified = jwt.verify(token, this.keys.public, {
      algorithms: [this.config.algorithm],
      ...this.config.options
    });
    
    // Check request binding if enabled
    if (this.config.bindToRequest) {
      this.verifyRequestBinding(verified, request);
    }
    
    return verified;
  }
}
```

## Conclusion

The C2M API's JWT implementation shows good architectural decisions with the two-tier token system, but several security enhancements are critical:

1. **Immediate Actions**:
   - Switch from HS256 to RS256
   - Implement proper token revocation with Redis
   - Add request binding for sensitive operations
   - Reduce token lifetimes

2. **Short-term Improvements**:
   - Add comprehensive JWT security tests
   - Implement key rotation
   - Enhanced logging and monitoring
   - Token refresh patterns

3. **Long-term Goals**:
   - Move to OAuth 2.0 / OIDC
   - Implement Zero Trust principles
   - Add anomaly detection
   - Regular security audits

These improvements will significantly enhance the security posture of the C2M API authentication system while maintaining performance and usability.
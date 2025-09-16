# C2M API V2 Authentication Guide

> **📌 Note**: This document has been superseded by **[AUTHENTICATION_CONSOLIDATED.md](./AUTHENTICATION_CONSOLIDATED.md)** which combines all authentication documentation into a single comprehensive guide.
>
> This file is preserved for backward compatibility and will be archived in a future update.

---

*Original content below for reference:*

This guide covers the authentication system architecture and implementation for the C2M API V2.

## Overview

The C2M API V2 uses a two-tier JWT authentication system designed for security and scalability. The system provides:

- Enhanced security through token isolation
- Reduced attack surface with short-lived tokens
- Efficient token management with minimal overhead
- Provider-agnostic design (works with any auth backend)

## System Architecture

### Two-Token Design

The authentication system implements a two-token approach:

1. **Long-term tokens** - Used for authentication and token exchange
   - Configurable TTL (typically 30-90 days)
   - Stored securely by clients
   - Used only for obtaining short-term tokens

2. **Short-term tokens** - Used for actual API calls
   - Fixed 15-minute TTL
   - Automatically refreshed as needed
   - Minimizes exposure if compromised

### Provider Abstraction

The system abstracts the authentication provider behind API endpoints:

```
Client Application
       ↓
API Gateway (/auth/tokens/*)
       ↓
Lambda Functions
       ↓
Authentication Provider (Cognito, Auth0, etc.)
```

This abstraction allows:
- Switching providers without client changes
- Consistent authentication interface
- Custom business logic implementation
- Enhanced security controls

## Authentication Flow

### Initial Authentication

1. Client provides credentials to `/auth/tokens/long`
2. System validates credentials with provider
3. Long-term JWT token issued
4. Token stored in DynamoDB with TTL

### Token Exchange

1. Client presents long-term token to `/auth/tokens/short`
2. System validates long-term token
3. Short-term token issued with subset of scopes
4. Client uses short-term token for API calls

### Token Refresh

1. Client monitors token expiration
2. Proactively exchanges for new short-term token
3. Seamless API access maintained

## Security Features

### Token Isolation

- Long-term tokens never sent to API endpoints
- Short-term tokens have minimal lifetime
- Separate storage and validation paths

### Scope Management

- Granular permissions per endpoint
- Dynamic scope narrowing
- Audit trail of scope usage

### Revocation Support

- Immediate token revocation
- Cascading revocation (long → short)
- Revocation list management

## Implementation Details

### JWT Structure

Tokens follow standard JWT format with custom claims:

- `sub`: Subject (client ID)
- `scopes`: Array of granted permissions
- `token_type`: "long" or "short"
- `token_id`: Unique identifier for tracking

### Storage Strategy

- Long-term tokens: DynamoDB with TTL
- Short-term tokens: In-memory cache
- Revocation list: DynamoDB global table

### Validation Process

1. Signature verification
2. Expiration check
3. Revocation list check
4. Scope validation
5. Rate limit enforcement

## Integration Patterns

### Client Libraries

The system supports integration through:
- Native SDK implementations
- REST API direct calls
- GraphQL resolver middleware
- WebSocket authentication

### Token Management

Clients should implement:
- Automatic token refresh
- Secure token storage
- Retry logic with backoff
- Token expiration monitoring

### Error Handling

Standard error responses for:
- Invalid credentials (401)
- Insufficient permissions (403)
- Token expired (401)
- Rate limit exceeded (429)

## Best Practices

### Security

1. Store long-term tokens encrypted at rest
2. Transmit tokens only over HTTPS
3. Implement token rotation policies
4. Monitor authentication anomalies

### Performance

1. Cache tokens appropriately
2. Refresh tokens proactively
3. Batch API calls when possible
4. Use connection pooling

### Reliability

1. Implement retry with exponential backoff
2. Handle token refresh race conditions
3. Maintain fallback authentication
4. Monitor token expiration

## Monitoring and Debugging

### CloudWatch Metrics

- Authentication success/failure rates
- Token issuance volume
- API call patterns
- Latency percentiles

### Logging

- Authentication attempts
- Token exchanges
- Revocation events
- Scope usage patterns

### Troubleshooting

Common issues and solutions:
- Clock skew: Sync system time
- Token size: Check scope count
- Validation failures: Verify secret
- Rate limits: Implement backoff

---

*For implementation examples and detailed API reference, see [AUTHENTICATION_CONSOLIDATED.md](./AUTHENTICATION_CONSOLIDATED.md)*
# C2M API V2 JWT Authentication Architecture

## Overview

The C2M API V2 implements a sophisticated two-tier JWT authentication system using AWS managed services. This architecture provides secure, scalable authentication with automatic token management and revocation capabilities.

## Architecture Diagram

```
┌─────────────────────┐
│   Client Application│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│   API Gateway       │────▶│  JWT Authorizer     │
│                     │     │  Lambda Function    │
│  /auth/tokens/long  │     └──────────┬──────────┘
│  /auth/tokens/short │                │
│  /auth/tokens/revoke│                ▼
└──────────┬──────────┘     ┌─────────────────────┐
           │                │   DynamoDB          │
           ▼                │   Token Store       │
┌─────────────────────┐     │  - Token Metadata   │
│  Lambda Functions   │────▶│  - Revocation Status│
│  - Issue Long Token │     │  - TTL Management   │
│  - Issue Short Token│     └─────────────────────┘
│  - Revoke Token     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│  Cognito User Pool  │     │  Secrets Manager    │
│  - Service Accounts │     │  - Client Secrets   │
│  - OAuth2 Scopes    │     │  - JWT Signing Keys │
└─────────────────────┘     └─────────────────────┘
```

## Component Details

### 1. API Gateway

The API Gateway serves as the entry point for all authentication requests. It provides:

- **Endpoints**:
  - `POST /auth/tokens/long` - Issues long-term tokens (30-90 days)
  - `POST /auth/tokens/short` - Exchanges long tokens for short-term JWTs (15 minutes)
  - `POST /auth/tokens/{tokenId}/revoke` - Revokes existing tokens

- **Features**:
  - Request validation using JSON schemas
  - CORS support for browser-based applications
  - Custom JWT authorizer with 5-minute result caching
  - Optional WAF integration for rate limiting (10 requests/minute)
  - CloudWatch logging and X-Ray tracing

### 2. Lambda Functions

#### a) Issue Long Token Function
- **Purpose**: Authenticates clients and issues long-term refresh tokens
- **Process**:
  1. Validates client credentials against Secrets Manager
  2. Creates or updates Cognito user account
  3. Generates unique token ID
  4. Stores token metadata in DynamoDB
  5. Returns Cognito refresh token and metadata

#### b) Issue Short Token Function
- **Purpose**: Exchanges valid long tokens for short-term API access tokens
- **Process**:
  1. Validates incoming long token via JWT Authorizer
  2. Retrieves user context and validates scopes
  3. Generates custom JWT with 15-minute expiry
  4. Signs token with RSA private key from Secrets Manager
  5. Stores token reference in DynamoDB with parent relationship

#### c) Revoke Token Function
- **Purpose**: Invalidates tokens before their natural expiration
- **Process**:
  1. Updates token status to "REVOKED" in DynamoDB
  2. Records revocation metadata (who, when)
  3. Implements cascading revocation for child tokens
  4. Returns confirmation of revocation

#### d) JWT Authorizer Function
- **Purpose**: Validates tokens for all protected endpoints
- **Process**:
  1. Extracts JWT from Authorization header
  2. Validates token signature and expiration
  3. Checks revocation status in DynamoDB
  4. Generates IAM policy allowing/denying access
  5. Passes user context to downstream services

### 3. Cognito User Pool

Cognito provides the core authentication infrastructure:

- **Configuration**:
  - Service accounts only (no email/phone verification)
  - Custom attributes for storing client metadata
  - Advanced security features enabled
  - Password policy: 12+ characters, mixed case, numbers, symbols

- **OAuth2 Resource Server**:
  - Scopes defined:
    - `c2m-api/jobs:submit` - Submit print/mail jobs
    - `c2m-api/jobs:read` - Read job status
    - `c2m-api/templates:read` - Access document templates
    - `c2m-api/tokens:write` - Issue new tokens
    - `c2m-api/tokens:revoke` - Revoke existing tokens

### 4. DynamoDB Token Store

DynamoDB provides fast, scalable token metadata storage:

- **Table Structure**:
  ```
  Primary Key:
    - Partition Key: tokenId (String)
    - Sort Key: tokenType (String: "LONG" | "SHORT")
  
  Attributes:
    - userId: String (Cognito user ID)
    - clientId: String (Application identifier)
    - createdAt: Number (Unix timestamp)
    - expiresAt: Number (Unix timestamp)
    - ttl: Number (DynamoDB TTL for auto-deletion)
    - status: String ("ACTIVE" | "REVOKED" | "EXPIRED")
    - parentTokenId: String (For short tokens)
    - scopes: List<String>
    - revokedAt: Number (When revoked)
    - revokedBy: String (Who revoked it)
  ```

- **Features**:
  - TTL-based automatic cleanup of expired tokens
  - Global Secondary Index on userId for user token queries
  - Point-in-time recovery enabled
  - Encryption at rest

### 5. Secrets Manager

Secrets Manager securely stores sensitive authentication data:

- **Client Credentials Secret** (`c2m-api/{env}/client-secrets`):
  ```json
  {
    "test-client-123": {
      "secret": "super-secret-password-123",
      "name": "Test Client",
      "scopes": ["jobs:submit", "jobs:read", "templates:read"]
    },
    "prod-client-456": {
      "secret": "production-secret-key",
      "name": "Production Client",
      "scopes": ["jobs:submit", "jobs:read"]
    }
  }
  ```

- **JWT Signing Key**:
  - RSA 2048-bit key pair
  - Private key for signing tokens
  - Public key exposed via JWKS endpoint
  - Supports key rotation

## Authentication Flows

### 1. Initial Authentication (Client Credentials Flow)

```
Client                  API Gateway              Lambda                  Secrets Manager         Cognito
  │                          │                      │                          │                   │
  ├─POST /auth/tokens/long──▶│                      │                          │                   │
  │ {client_id, secret}      ├─Invoke─────────────▶│                          │                   │
  │                          │                      ├─GetSecretValue─────────▶│                   │
  │                          │                      │◀─Client Credentials──────┤                   │
  │                          │                      ├─CreateUser───────────────────────────────────▶│
  │                          │                      │◀─User Created────────────────────────────────┤
  │                          │                      ├─Store Token Metadata────▶DynamoDB            │
  │                          │◀─Token Response──────┤                                              │
  │◀─Long Token + Metadata───┤                      │                                              │
```

### 2. Short Token Exchange

```
Client                  API Gateway              JWT Authorizer          Lambda                DynamoDB
  │                          │                          │                   │                      │
  ├─POST /auth/tokens/short─▶│                          │                   │                      │
  │ Authorization: Bearer... ├─Validate Token─────────▶│                   │                      │
  │                          │                          ├─Check Revocation──────────────────────────▶│
  │                          │                          │◀─Token Valid───────────────────────────────┤
  │                          │◀─Allow + Context─────────┤                   │                      │
  │                          ├─Invoke──────────────────────────────────────▶│                      │
  │                          │                                              ├─Generate JWT─────────▶│
  │                          │                                              ├─Store Metadata───────▶│
  │                          │◀─Short Token Response────────────────────────┤                      │
  │◀─Short JWT Token─────────┤                                              │                      │
```

### 3. API Request with Token

```
Client                  API Gateway              JWT Authorizer          DynamoDB              Target Service
  │                          │                          │                   │                      │
  ├─GET /api/resource────────▶│                          │                   │                      │
  │ Authorization: Bearer... ├─Validate Token─────────▶│                   │                      │
  │                          │                          ├─Verify Signature──┤                      │
  │                          │                          ├─Check Expiry──────┤                      │
  │                          │                          ├─Check Revocation──▶│                      │
  │                          │                          │◀─Status────────────┤                      │
  │                          │◀─IAM Policy + Context────┤                   │                      │
  │                          ├─Forward Request──────────────────────────────────────────────────────▶│
  │                          │◀─Response────────────────────────────────────────────────────────────┤
  │◀─API Response────────────┤                          │                   │                      │
```

## Security Features

### 1. Two-Tier Token System
- **Long Tokens**: 30-90 day refresh tokens stored securely client-side
- **Short Tokens**: 15-minute JWTs for API calls, reducing exposure window
- **Benefits**: Compromised short tokens have minimal impact; long tokens can be revoked immediately

### 2. Token Revocation
- **Immediate Effect**: Revoked tokens fail authorization within seconds
- **Cascading Revocation**: Revoking a long token invalidates all derived short tokens
- **Audit Trail**: Complete record of who revoked tokens and when

### 3. Rate Limiting
- **WAF Rules**: 10 requests/minute per IP for authentication endpoints
- **Lambda Concurrency**: Reserved concurrency prevents runaway costs
- **DynamoDB**: On-demand scaling handles burst traffic

### 4. Encryption
- **In Transit**: TLS 1.2+ for all API communications
- **At Rest**: DynamoDB encryption, Secrets Manager encryption
- **Token Signing**: RSA 2048-bit signatures prevent tampering

### 5. Monitoring & Alerting
- **CloudWatch Dashboards**: Real-time metrics for all components
- **Alarms**: 
  - High error rates (>5% failure)
  - Throttling events
  - Unusual token issuance patterns
- **X-Ray Tracing**: End-to-end request tracking for performance analysis

## Configuration Management

### CDK Context Variables
```json
{
  "environment": "dev|staging|prod",
  "enable_monitoring": true,
  "enable_waf": true,
  "token_config": {
    "long_token_ttl_days": 30,
    "short_token_ttl_minutes": 15,
    "max_long_token_ttl_days": 90,
    "authorizer_result_ttl_seconds": 300
  },
  "rate_limit_rules": {
    "auth_endpoints": {
      "requests_per_minute": 10
    }
  },
  "cors_config": {
    "allowed_origins": ["https://app.c2m.com"],
    "allowed_headers": ["Authorization", "Content-Type"],
    "max_age_seconds": 3600
  }
}
```

### Environment Variables (Lambda Functions)
- `USER_POOL_ID`: Cognito User Pool identifier
- `USER_POOL_CLIENT_ID`: Cognito app client ID
- `TOKEN_TABLE_NAME`: DynamoDB table name
- `CLIENT_SECRETS_ARN`: Secrets Manager ARN for client credentials
- `JWT_SIGNING_KEY_ARN`: Secrets Manager ARN for JWT signing key
- `ENVIRONMENT`: Current environment (dev/staging/prod)

## Deployment & Operations

### Deployment Process
1. **CDK Synthesis**: `cdk synth` generates CloudFormation templates
2. **Deployment**: `cdk deploy` creates/updates all AWS resources
3. **Secret Setup**: Populate client credentials in Secrets Manager
4. **Testing**: Use provided test scripts to verify endpoints
5. **Monitoring**: Configure CloudWatch dashboards and alarms

### Operational Procedures

#### Adding New Clients
1. Update client secrets in Secrets Manager
2. Define required scopes for the client
3. No deployment needed - changes take effect immediately

#### Rotating JWT Signing Keys
1. Generate new RSA key pair
2. Update Secrets Manager with new keys
3. Keep old public key in JWKS for grace period
4. Remove old key after all tokens expire

#### Handling Security Incidents
1. Revoke compromised tokens via API
2. Update client secrets if compromised
3. Review CloudWatch logs for suspicious activity
4. Consider enabling WAF rules if under attack

## Cost Optimization

### Resource Costs (Monthly Estimates)
- **API Gateway**: $3.50 per million requests
- **Lambda**: $0.20 per million requests + compute time
- **DynamoDB**: On-demand pricing, ~$0.25 per million reads/writes
- **Cognito**: $0.0055 per monthly active user
- **Secrets Manager**: $0.40 per secret per month

### Optimization Strategies
1. **Caching**: 5-minute authorizer cache reduces Lambda invocations
2. **TTL**: Automatic token cleanup reduces storage costs
3. **Reserved Concurrency**: Prevents runaway Lambda costs
4. **On-Demand DynamoDB**: Pay only for actual usage

## Future Enhancements

1. **Multi-Region Support**: Replicate authentication across regions
2. **API Key Support**: Alternative authentication for simple use cases
3. **OAuth2 Authorization Code Flow**: Support for web applications
4. **Token Refresh Endpoint**: Allow refreshing short tokens without long token
5. **Enhanced Monitoring**: Custom metrics for business insights

---

This architecture provides a production-ready authentication system that balances security, performance, and operational simplicity while leveraging AWS managed services for reliability and scale.
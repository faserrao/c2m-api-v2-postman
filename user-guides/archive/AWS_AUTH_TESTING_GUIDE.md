# AWS Authentication Testing Guide

## Overview

The C2M API uses a two-tier JWT authentication system when testing against AWS endpoints. This guide explains how to configure and test with authentication enabled.

## Prerequisites

1. **Deployed AWS Infrastructure** - The auth stack must be deployed via the security repo
2. **AWS Credentials** - Client ID and secret from AWS Secrets Manager or provided by admin
3. **Postman Environment** - Properly configured with AWS endpoints

## Environment Configuration

### Step 1: Create/Update Environment Variables

In Postman, set these environment variables:

```javascript
// Required for Authentication
clientId: "your-client-id"          // e.g., "test-client-123"
clientSecret: "your-client-secret"  // e.g., "super-secret-password-123"

// API Endpoints (choose based on environment)
baseUrl: "https://your-api-gateway-url/stage"  // For AWS testing
// OR
baseUrl: "http://localhost:4010"              // For local mock testing

// Optional: Override token endpoints if different from baseUrl
authBaseUrl: "https://auth-api-gateway-url/stage"  // If auth is on different API
```

### Step 2: Environment Examples

#### Development Environment
```json
{
  "clientId": "dev-client-123",
  "clientSecret": "{{dev_client_secret}}",
  "baseUrl": "https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev"
}
```

#### Production Environment
```json
{
  "clientId": "prod-client-456",
  "clientSecret": "{{prod_client_secret}}",
  "baseUrl": "https://api.c2m.example.com/v1"
}
```

#### Mock Testing (No Auth)
```json
{
  "baseUrl": "http://localhost:4010"
  // No clientId or clientSecret needed
}
```

## How Authentication Works

### Automatic Token Management

When credentials are configured, the pre-request script automatically:

1. **First Request**: Gets long-term token (30-90 days)
2. **Subsequent Requests**: Uses cached long-term token
3. **Every Request**: Exchanges for short-term token (15 minutes)
4. **Token Expiry**: Auto-refreshes before expiration

### Token Flow Visualization

```
Client Credentials → Long Token → Short Token → API Request
     ↓                    ↓             ↓            ↓
  (Once per month)   (Cached)    (Every 15min)  (With Auth Header)
```

## Testing Scenarios

### Scenario 1: Test Without Auth (Mock Server)

1. Set environment to use mock URL
2. Leave clientId and clientSecret empty
3. Run requests normally - no auth required

### Scenario 2: Test With Auth (AWS)

1. Set environment with AWS URL
2. Add clientId and clientSecret
3. Run any request - auth happens automatically
4. Check console for auth flow messages

### Scenario 3: Test Auth Endpoints Directly

Test the auth endpoints themselves:

```bash
# Get Long Token
POST {{baseUrl}}/auth/tokens/long
{
  "grant_type": "client_credentials",
  "client_id": "{{clientId}}",
  "client_secret": "{{clientSecret}}"
}

# Get Short Token
POST {{baseUrl}}/auth/tokens/short
Headers: Authorization: Bearer {{longTermToken}}

# Revoke Token
POST {{baseUrl}}/auth/tokens/{{tokenId}}/revoke
Headers: Authorization: Bearer {{shortTermToken}}
```

## Debugging Authentication

### View Auth Flow in Console

1. Open Postman Console: View → Show Postman Console
2. Run a request
3. You'll see:
   ```
   Obtaining new long-term token...
   Long-term token obtained successfully
   Token will expire in 2592000 seconds
   Obtaining new short-term token...
   Short-term token obtained successfully
   Authorization header set
   ```

### Common Issues and Solutions

#### "Client credentials not configured"
- **Solution**: Add clientId and clientSecret to environment
- This is normal when testing with mock server

#### "401 Unauthorized" from AWS
- **Check**: Client credentials are correct
- **Check**: No extra spaces in credentials
- **Verify**: Auth infrastructure is deployed

#### "403 Forbidden" from API
- **Check**: Token has required scopes
- **Verify**: API Gateway authorizer is configured
- **Check**: Resource permissions in AWS

#### Token not refreshing
- **Clear tokens**: In console, run:
  ```javascript
  pm.environment.unset('longTermToken');
  pm.environment.unset('shortTermToken');
  pm.environment.unset('tokenExpiry');
  ```

## Security Best Practices

1. **Never commit credentials** - Use Postman environment variables
2. **Use variable masking** - Set type to "secret" for clientSecret
3. **Rotate credentials regularly** - Update in AWS Secrets Manager
4. **Monitor token usage** - Check CloudWatch logs
5. **Use least privilege** - Only grant required scopes

## Advanced Configuration

### Custom Token TTL
```javascript
// In pre-request script, modify:
ttl_seconds: 3600  // 1 hour instead of 30 days
```

### Skip Auth for Specific Requests
Add to request's pre-request script:
```javascript
pm.request.headers.remove('Authorization');
```

### Use Different Auth Endpoints
Set environment variable:
```javascript
authBaseUrl: "https://auth-specific-api.com"
```

## Monitoring and Logs

### View in AWS CloudWatch
- Lambda function logs: `/aws/lambda/c2m-auth-*`
- API Gateway logs: `API-Gateway-Execution-Logs_*`
- Custom metrics: CloudWatch → Metrics → C2M/Auth

### Key Metrics to Monitor
- Authentication success/failure rates
- Token issuance frequency
- API latency with auth enabled
- Token revocation events

## Next Steps

1. Configure your Postman environment with AWS credentials
2. Run a test request to verify auth is working
3. Monitor the console to understand token flow
4. Check CloudWatch for server-side auth logs

Remember: The auth system is designed to be transparent when configured correctly - you shouldn't need to manually manage tokens!
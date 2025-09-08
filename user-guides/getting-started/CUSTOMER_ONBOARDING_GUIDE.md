# C2M API V2 Customer Onboarding Guide

This guide walks new customers through the process of getting started with the C2M API V2, from obtaining credentials to making your first API call.

## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [Account Setup](#account-setup)
- [Authentication Setup](#authentication-setup)
- [Environment Configuration](#environment-configuration)
- [Making Your First API Call](#making-your-first-api-call)
- [Next Steps](#next-steps)
- [Support](#support)

---

## Overview

Welcome to the C2M API V2! This API allows you to programmatically submit documents for printing and mailing. Each customer receives:

- **Unique API Credentials** - Secure client ID and secret
- **Isolated Environment** - Complete separation from other customers
- **Multiple Environments** - Development, staging, and production
- **Customized Rate Limits** - Based on your subscription plan

### Available Plans

| Plan | Rate Limit | Max Recipients | Environments | Features |
|------|------------|----------------|--------------|----------|
| **Basic** | 100/hour | 100/request | Dev + Prod | Standard templates |
| **Premium** | 1000/hour | 1000/request | Dev + Stage + Prod | Custom templates, bulk operations |
| **Enterprise** | Unlimited | 10000/request | Unlimited | All features, dedicated support |

---

## Getting Started

### Prerequisites

Before beginning onboarding:
1. Signed contract with C2M
2. Designated technical contact
3. Basic understanding of REST APIs
4. Development environment ready

### What You'll Receive

After onboarding, you'll receive:
1. **Welcome Email** with secure credential link
2. **API Documentation** access
3. **Postman Collection** for testing
4. **Support Contact** information

---

## Account Setup

### Step 1: Initial Contact

Your account manager will gather:
- Company name and details
- Technical contact information
- Subscription plan selection
- Initial use case requirements
- Preferred environments (dev/staging/prod)

### Step 2: Credential Generation

Within 24 hours, you'll receive:
- Secure link to download credentials (expires in 24 hours)
- Quick start guide
- Postman environment file

### Step 3: Credential Storage

**Important Security Steps:**
1. Download credentials immediately
2. Store in secure location (password manager, vault)
3. Never commit to source control
4. Set up environment variables

Example credential structure:
```json
{
  "customerId": "CUST-acme-corp-a1b2c3",
  "environments": {
    "development": {
      "clientId": "c2m-acme-corp-dev",
      "clientSecret": "dev-secret-key-here",
      "apiUrl": "https://dev-api.c2m.example.com"
    },
    "production": {
      "clientId": "c2m-acme-corp-prod",
      "clientSecret": "prod-secret-key-here",
      "apiUrl": "https://api.c2m.example.com"
    }
  }
}
```

---

## Authentication Setup

### Understanding the Token Flow

The C2M API uses a two-tier JWT authentication system:

1. **Long-term token** (30-90 days) - Obtained with your credentials
2. **Short-term token** (15 minutes) - Used for actual API calls

### Quick Test

Test your credentials immediately:

```bash
# Set your credentials
CLIENT_ID="your-client-id"
CLIENT_SECRET="your-client-secret"
AUTH_URL="https://auth.c2m.example.com"

# Get a long-term token
curl -X POST "$AUTH_URL/auth/tokens/long" \
  -H "Content-Type: application/json" \
  -H "X-Client-Id: $CLIENT_ID" \
  -d "{
    \"grant_type\": \"client_credentials\",
    \"client_id\": \"$CLIENT_ID\",
    \"client_secret\": \"$CLIENT_SECRET\"
  }"
```

Expected response:
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 2592000,
  "expires_at": "2024-02-29T12:00:00Z"
}
```

### Integration Options

Choose your integration approach:

1. **Postman** (Easiest for testing)
   - Import provided environment file
   - Pre-request scripts handle auth automatically
   - [Postman Setup Guide](./POSTMAN_COMPLETE_GUIDE.md)

2. **SDK** (Recommended for production)
   - Available in Python, JavaScript, Java
   - Built-in token management
   - [SDK Documentation](../sdk/)

3. **Direct API** (Full control)
   - Implement token management yourself
   - [Authentication Guide](./AUTHENTICATION_GUIDE.md)

---

## Environment Configuration

### Development Environment

Start with development for initial integration:
- Lower rate limits for safety
- Test data only
- Full API functionality
- Detailed error messages

### Staging Environment (Premium/Enterprise)

Use for pre-production testing:
- Production-equivalent performance
- Integration testing
- Load testing allowed
- Mirrors production configuration

### Production Environment

For live operations:
- Full rate limits
- Real document processing
- Production SLAs apply
- Monitoring and alerts active

### Environment Variables

Set up your application environment:

```bash
# Development
export C2M_CLIENT_ID_DEV="c2m-acme-corp-dev"
export C2M_CLIENT_SECRET_DEV="dev-secret-here"
export C2M_API_URL_DEV="https://dev-api.c2m.example.com"
export C2M_AUTH_URL_DEV="https://dev-auth.c2m.example.com"

# Production
export C2M_CLIENT_ID_PROD="c2m-acme-corp-prod"
export C2M_CLIENT_SECRET_PROD="prod-secret-here"
export C2M_API_URL_PROD="https://api.c2m.example.com"
export C2M_AUTH_URL_PROD="https://auth.c2m.example.com"
```

---

## Making Your First API Call

### Step 1: Get Authentication Tokens

```python
import requests
import os

# Configuration
client_id = os.environ['C2M_CLIENT_ID_DEV']
client_secret = os.environ['C2M_CLIENT_SECRET_DEV']
auth_url = os.environ['C2M_AUTH_URL_DEV']

# Get long-term token
response = requests.post(
    f"{auth_url}/auth/tokens/long",
    json={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    },
    headers={"X-Client-Id": client_id}
)
long_token = response.json()['access_token']

# Exchange for short-term token
response = requests.post(
    f"{auth_url}/auth/tokens/short",
    headers={"Authorization": f"Bearer {long_token}"}
)
short_token = response.json()['access_token']
```

### Step 2: Submit a Test Document

```python
# Submit a simple letter
api_url = os.environ['C2M_API_URL_DEV']

response = requests.post(
    f"{api_url}/jobs/submit/templates/business-letter",
    json={
        "templateData": {
            "date": "2024-01-29",
            "recipientName": "Test Recipient",
            "body": "This is a test letter from the C2M API."
        },
        "recipientAddress": {
            "firstName": "Test",
            "lastName": "Recipient",
            "address1": "123 Test Street",
            "city": "Test City",
            "state": "CA",
            "zip": "12345"
        }
    },
    headers={"Authorization": f"Bearer {short_token}"}
)

job = response.json()
print(f"Job submitted! ID: {job['jobId']}")
print(f"Track at: {job['trackingUrl']}")
```

### Step 3: Check Job Status

```python
job_id = job['jobId']

response = requests.get(
    f"{api_url}/jobs/{job_id}/status",
    headers={"Authorization": f"Bearer {short_token}"}
)

status = response.json()
print(f"Status: {status['status']}")
print(f"Progress: {status['progress']}")
```

---

## Next Steps

### 1. Explore Available Endpoints

Key endpoints to try:
- **Templates**: `GET /templates` - List available templates
- **Single Document**: `POST /jobs/submit/single/doc` - Submit one document
- **Bulk Submit**: `POST /jobs/submit/bulk` - Submit multiple documents
- **Job Tracking**: `GET /jobs/{jobId}/tracking` - Real-time tracking

### 2. Set Up Webhooks (Optional)

Receive real-time notifications:
```json
{
  "webhookUrl": "https://your-app.com/webhooks/c2m",
  "events": ["job.completed", "job.failed", "mail.delivered"]
}
```

### 3. Implement Error Handling

Common patterns:
```python
try:
    response = make_api_call()
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        # Token expired, refresh and retry
        refresh_tokens()
        response = make_api_call()
    elif e.response.status_code == 429:
        # Rate limited, wait and retry
        time.sleep(60)
        response = make_api_call()
    else:
        # Log error and handle appropriately
        log_error(e)
        raise
```

### 4. Plan for Production

Before going live:
- [ ] Test error scenarios
- [ ] Implement retry logic
- [ ] Set up monitoring
- [ ] Plan credential rotation
- [ ] Review security checklist
- [ ] Load test within limits

---

## Support

### Resources

1. **Documentation**
   - [API Reference](../README.md)
   - [Authentication Guide](./AUTHENTICATION_GUIDE.md)
   - [Postman Guide](./POSTMAN_COMPLETE_GUIDE.md)

2. **Testing Tools**
   - [Postman Collection](../postman/)
   - [SDK Examples](../sdk/)
   - [Code Samples](../examples/)

3. **Support Channels**
   - **Email**: api-support@c2m.example.com
   - **Slack**: [Customer workspace]
   - **Phone**: Available for Enterprise customers

### Common Questions

**Q: How do I rotate credentials?**
A: Contact support 7 days before rotation. We'll provide new credentials with an overlap period.

**Q: Can I increase my rate limits?**
A: Yes, contact your account manager to discuss plan upgrades.

**Q: What happens if I exceed rate limits?**
A: You'll receive 429 responses. Implement exponential backoff to handle gracefully.

**Q: How do I test without sending real mail?**
A: Use the development environment - all mail is simulated.

**Q: Can I white-label the mail pieces?**
A: Yes, available for Premium and Enterprise plans.

### Emergency Contacts

For production issues:
- **Critical Issues**: emergency@c2m.example.com
- **Enterprise Hotline**: +1-800-C2M-HELP
- **Status Page**: https://status.c2m.example.com

---

## Appendix: Quick Reference

### Authentication Flow
```
Credentials → Long Token (30 days) → Short Token (15 min) → API Calls
```

### Environment URLs
| Environment | Auth URL | API URL |
|-------------|----------|---------|
| Development | https://dev-auth.c2m.example.com | https://dev-api.c2m.example.com |
| Staging | https://stage-auth.c2m.example.com | https://stage-api.c2m.example.com |
| Production | https://auth.c2m.example.com | https://api.c2m.example.com |

### Rate Limits by Plan
| Plan | Per Hour | Per Day | Per Month |
|------|----------|---------|-----------|
| Basic | 100 | 1,000 | 10,000 |
| Premium | 1,000 | 10,000 | 100,000 |
| Enterprise | Unlimited | Unlimited | Unlimited |

### Required Scopes
| Operation | Required Scope |
|-----------|----------------|
| Submit jobs | `jobs:submit` |
| Read job status | `jobs:read` |
| Use templates | `templates:read` |
| Manage templates | `templates:write` |
| Bulk operations | `bulk:operations` |

---

*Welcome to C2M API V2! We're excited to help you automate your mail operations.*

*Last Updated: 2025-09-08*
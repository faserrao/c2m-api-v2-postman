# Authentication Provider Interface for C2M API

## Overview
This document defines the interface that authentication providers must implement to work with the C2M API Postman collection.

## Required Interface

Any authentication provider script must implement the following behavior:

### 1. Skip Authentication for Auth Endpoints
```javascript
const currentPath = pm.request.url.getPath();
if (currentPath.includes('/auth/')) {
    console.log('Skipping auth for auth endpoint');
    return;
}
```

### 2. Check for Required Configuration
```javascript
const config = {
    baseUrl: pm.environment.get('baseUrl'),
    clientId: pm.environment.get('clientId'),
    clientSecret: pm.environment.get('clientSecret')
};

if (!config.clientId || !config.clientSecret) {
    console.warn('Client credentials not configured');
    return;
}
```

### 3. Obtain and Set Authorization Header
The provider must:
- Get a valid access token (however it implements this)
- Set the Authorization header:
```javascript
pm.request.headers.add({
    key: 'Authorization',
    value: `Bearer ${accessToken}`
});
```

### 4. Handle Errors
```javascript
// On error, set an environment variable for testing
pm.environment.set('authError', error.toString());
```

## Expected Environment Variables

### Input Variables (Provider reads these):
- `baseUrl` - The API base URL
- `clientId` - Client identifier
- `clientSecret` - Client secret

### Output Variables (Provider sets these):
- `authError` - Any error message (cleared on success)

### Provider-Specific Variables:
Providers may use additional environment variables for their implementation:
- JWT: `longTermToken`, `shortTermToken`, `tokenExpiry`, etc.
- OAuth: `accessToken`, `refreshToken`, `tokenType`, etc.
- API Key: `apiKey`, `apiSecret`, etc.

## Example Implementation Structure

```javascript
// 1. Skip auth endpoints
if (/* is auth endpoint */) return;

// 2. Check configuration
if (/* missing required config */) return;

// 3. Provider-specific token logic
async function getAccessToken() {
    // Implementation specific to your auth method
}

// 4. Set the header
getAccessToken()
    .then(token => {
        pm.request.headers.add({
            key: 'Authorization',
            value: `Bearer ${token}`
        });
    })
    .catch(error => {
        pm.environment.set('authError', error.toString());
    });
```

## Provider Examples

### JWT Two-Token (Current Implementation)
- Located at: `../c2m-api-v2-security/postman/scripts/jwt-auth-provider.js`
- Uses long-term and short-term token pattern
- Implements automatic token refresh

### OAuth 2.0 (Future)
- Standard OAuth 2.0 client credentials flow
- Could use different grant types

### API Key (Future)
- Simple API key authentication
- Could use header or query parameter
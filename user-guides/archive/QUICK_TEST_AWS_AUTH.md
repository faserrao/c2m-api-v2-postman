# Quick Test: AWS Authentication

## 1. Import the AWS Environment

1. In Postman, click **Environments** → **Import**
2. Select: `postman/environments/c2m-aws-dev.postman_environment.json`
3. Click **Import**

## 2. Get Your Credentials

From your terminal:
```bash
# If you have AWS CLI configured:
aws secretsmanager get-secret-value \
  --secret-id c2m-api/dev/client-secrets \
  --query SecretString \
  --output text | jq '.'
```

Or ask your admin for:
- Client ID (e.g., `test-client-123`)
- Client Secret (e.g., `super-secret-password-123`)

## 3. Configure Environment

1. Click the environment dropdown (top right) → **C2M AWS Dev Environment**
2. Click the eye icon to view/edit
3. Fill in:
   - `clientId`: Your client ID
   - `clientSecret`: Your client secret (set type to "secret")
4. Click **Save**

## 4. Test Authentication

### Option A: Test Auth Endpoints Directly

Create a new request:
```
POST https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev/auth/tokens/long
```

Body (raw JSON):
```json
{
  "grant_type": "client_credentials",
  "client_id": "{{clientId}}",
  "client_secret": "{{clientSecret}}"
}
```

Expected response:
```json
{
  "access_token": "ltk_...",
  "token_type": "Bearer",
  "expires_in": 2592000
}
```

### Option B: Test Regular API Endpoint

1. Use the imported test collection
2. Select any endpoint (e.g., GET `/jobs/status`)
3. Make sure environment is selected
4. Click **Send**

Watch the Postman Console (View → Show Postman Console):
```
Checking auth requirements for path: /jobs/status
Obtaining new long-term token...
Long-term token obtained successfully
Obtaining new short-term token...
Short-term token obtained successfully
Authorization header set
```

## 5. Verify Headers

After sending a request, check the **Headers** tab:
- `Authorization: Bearer stk_...` (automatically added)
- `X-Client-Id: test-client-123` (automatically added)

## 6. Switch Between Environments

- **AWS Testing**: Select "C2M AWS Dev Environment" (auth enabled)
- **Mock Testing**: Select "C2M Mock Environment" (no auth)

The same collection works for both!

## Common Test Scenarios

### Test 1: Token Expiration
```javascript
// In Console, force token expiration:
pm.environment.set('tokenExpiry', new Date(Date.now() - 60000).toISOString());
// Next request will auto-refresh
```

### Test 2: Invalid Credentials
```javascript
// Temporarily set wrong secret:
pm.environment.set('clientSecret', 'wrong-secret');
// Should get 401 Unauthorized
```

### Test 3: Token Revocation
```
POST {{baseUrl}}/auth/tokens/{{currentTokenId}}/revoke
Authorization: Bearer {{shortTermToken}}
```

## Success Indicators

✅ **Auth is working when you see:**
- Requests to `/jobs/*` endpoints return 200 (not 401/403)
- Console shows token acquisition messages
- Authorization header is automatically added
- No manual token management needed

❌ **Auth is not working if you see:**
- 401 Unauthorized errors
- "Client credentials not configured" (for AWS endpoints)
- No Authorization header in requests
- Manual token handling required

## Next Steps

1. Test all your API endpoints with auth enabled
2. Set up multiple environments (dev, staging, prod)
3. Share environment files with team (without secrets!)
4. Monitor auth metrics in CloudWatch
# 🔍 COMPLETE DETECTIVE REPORT: Authorization Header Mystery

## 📋 Summary

Investigation into why the Authorization header appears in Real World Collection requests despite console logging "Mock server detected - skipping Authorization header".

---

## 🎯 The Mystery

**Observed Behavior:**
- Console: "Mock server detected - skipping Authorization header"
- Request Headers: `Authorization: Bearer [LONG JWT TOKEN]`
- Request URL: `https://a0711c27-f596-4e45-91bb-2a7a7a16c957.mock.pstmn.io`

**Question:** Why is the header being added when the script says it's skipping?

---

## 🧪 Investigation Findings

### 1. Collection Structure Analysis

**Real World Collection:**
- ✅ No collection-level Authorization tab
- ✅ No folder-level Authorization tabs (8 folders checked)
- ✅ No request-level Authorization tabs
- ✅ No folder-level pre-request scripts (all folders: event_count = 0)
- ✅ Collection-level pre-request script exists (92 lines)
- ⚠️ Collection variable `baseUrl` = `https://api.example.com/v1` (NOT mock!)

**Test Collection:**
- ✅ No Authorization tabs
- ✅ No request-level pre-request scripts
- ✅ Collection-level pre-request script exists (220 lines)
- ✅ No collection variables (relies on environment only)

### 2. Pre-request Script Comparison

| Feature | Real World Collection | Test Collection |
|---------|----------------------|-----------------|
| Lines of code | 92 | 220 |
| Auth model | Single token | Two-token (long + short) |
| Token variable | `authToken` | `longTermToken` + `shortTermToken` |
| Async pattern | IIFE `(async function(){})()` | Named function + error handler |
| Variable fallback | Environment OR Collection | Environment ONLY |
| Mock detection | ✅ Yes (line 76-87) | ✅ Yes (line 151-165) |
| Token expiry | ❌ No | ✅ Yes with 1-min buffer |
| Utilities | ❌ No | ✅ revokeCurrentToken, refreshTokens |

### 3. Mock Detection Logic (Real World Script)

```javascript
// Line 76-87
const baseUrl = pm.environment.get('baseUrl') || pm.collectionVariables.get('baseUrl') || '';
const isMockServer = baseUrl.includes('mock.pstmn.io') ||
                   baseUrl.includes('localhost:4010') ||
                   pm.environment.get('isMockServer') === 'true';

if (!isMockServer) {
    pm.request.headers.add({
        key: 'Authorization',
        value: 'Bearer ' + token
    });
    console.log('Authorization header added');
} else {
    console.log('Mock server detected - skipping Authorization header');
}
```

### 4. Configuration Analysis

**Environment (mock-env.json):**
```json
{
  "baseUrl": "https://63ed7adc-a8e8-40bf-a588-f66b6b9da46e.mock.pstmn.io",
  "authUrl": "https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev",
  "clientId": "test-client-123",
  "clientSecret": "super-secret-password-123"
}
```

**Collection Variable (in Real World Collection):**
```json
{
  "key": "baseUrl",
  "value": "https://api.example.com/v1"  // ⚠️ NOT a mock URL!
}
```

**User's Actual Request URL:**
```
https://a0711c27-f596-4e45-91bb-2a7a7a16c957.mock.pstmn.io
                                            ^^^ Different from mock-env.json!
```

---

## 💡 The Root Cause (Smoking Gun!)

### THE BUG: Checking Variable Instead of Actual URL

The script checks:
```javascript
const baseUrl = pm.environment.get('baseUrl')  // Gets the VARIABLE value
```

But it should check:
```javascript
const requestUrl = pm.request.url.toString()  // Gets the ACTUAL resolved URL
```

### Why This Causes the Problem:

1. **Postman resolves `{{baseUrl}}`** in the request URL from some source
   - User's actual URL: `a0711c27...mock.pstmn.io`

2. **Script checks `pm.environment.get('baseUrl')`** which returns:
   - If environment is set: correct mock URL → logs "detected"
   - If environment is NOT set: falls back to collection variable `api.example.com` → adds header

3. **But the request URL is ALREADY resolved** to a different mock server!

4. **Result**: Mismatch between what script checks and what request actually uses

### The Execution Flow

```
1. Pre-request script runs
   ├─ Checks pm.environment.get('baseUrl')
   ├─ Environment returns: ??? (depends on which environment selected in Postman UI)
   ├─ If not found, falls back to: pm.collectionVariables.get('baseUrl')
   │  └─ Returns: "https://api.example.com/v1"
   ├─ Checks: "https://api.example.com/v1".includes('mock.pstmn.io')
   ├─ Result: FALSE
   └─ Adds Authorization header

2. Request is sent
   ├─ URL template: {{baseUrl}}/jobs/single-doc-job-template
   ├─ Postman resolves {{baseUrl}} from: ??? (different environment?)
   └─ Final URL: https://a0711c27...mock.pstmn.io/jobs/...
```

---

## 📝 Why Test Collection Script Won't Work in Real World

**Attempting to use Test Collection script in Real World Collection produces errors because:**

1. **Token variable mismatch**:
   - Expects: `longTermToken`, `shortTermToken`, `tokenExpiry`, `currentTokenId`
   - Real World has: `authToken`

2. **Missing config object**:
   - Test script uses `config.clientId`, `config.clientSecret`
   - These are defined at top of script, won't exist if only partially copied

3. **Different auth flow**:
   - Test: Get long-term token → Exchange for short-term token
   - Real World: Get single long-term token → Use directly

4. **Different Promise handling**:
   - Test: Callbacks with `pm.sendRequest(request, (err, response) => {})`
   - Real World: Async/await with `await pm.sendRequest(request)`

---

## ✅ The Solution

Replace variable checking with actual URL checking:

```javascript
// ❌ CURRENT (checks variable)
const baseUrl = pm.environment.get('baseUrl') || pm.collectionVariables.get('baseUrl') || '';
const isMockServer = baseUrl.includes('mock.pstmn.io');

// ✅ CORRECT (checks actual resolved URL)
const requestUrl = pm.request.url.toString();
const isMockServer = requestUrl.includes('mock.pstmn.io') ||
                   requestUrl.includes('localhost:4010');
```

**Benefits:**
- Checks the ACTUAL URL being sent
- No dependence on environment/collection variable state
- Works regardless of which environment is selected
- More reliable and predictable

---

## 🎓 Historical Context (September 29, 2025)

From CLAUDE.md:
> **JWT Authentication Fix**: Restored mock server detection to prevent auth headers on mock requests
> - Fixed issue where Authorization header was being sent to mock servers causing HTML errors

**Original Problem:**
- Mock servers returned HTML error pages when they received Authorization headers
- Solution: Add mock detection to pre-request scripts

**Current Status:**
- Mock detection IS implemented
- BUT: Detection logic is flawed (checks variable, not actual URL)
- Result: Can still send auth headers to mock servers in certain scenarios

---

## 🔍 Evidence Summary

| Evidence | Finding |
|----------|---------|
| Authorization tab | None configured at any level |
| Folder-level scripts | None (all folders: event_count = 0) |
| Request-level scripts | None |
| Collection variables | baseUrl = `api.example.com` (NOT mock) |
| Environment variables | baseUrl = mock URL (but different from user's actual URL) |
| Script logic | Checks variables, not actual resolved URL |
| User's actual URL | Different mock server ID than in our files |

---

## 🚀 Recommended Next Steps

1. **Update both pre-request scripts** to check actual URL instead of variables
2. **Test with multiple environments** to ensure it works regardless of selection
3. **Remove collection variable baseUrl** from Real World Collection (rely on environment only)
4. **Document the fix** in CLAUDE.md and POSTMAN_ISSUES_AND_SOLUTIONS.md
5. **Verify mock servers** handle auth headers gracefully (they seem to now based on 200 OK responses)

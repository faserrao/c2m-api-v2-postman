# Postman Mock Server Error Response Testing Guide

## Background

Postman mock servers **do not randomly select** from multiple response examples. When multiple examples match a request, Postman's algorithm **prioritizes 200 OK responses** by default.

## How to Get Error Responses

Use special headers to control which response the mock server returns:

### Method 1: By Status Code (Recommended)

Use `x-mock-response-code` header to request specific error codes:

```bash
# 400 Bad Request
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-mock-response-code: 400" \
  https://174cb7a7-6aca-4c93-9cd1-639c10340684.mock.pstmn.io/jobs/submit/single/doc \
  -d '{}'

# 422 Validation Error
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-mock-response-code: 422" \
  https://174cb7a7-6aca-4c93-9cd1-639c10340684.mock.pstmn.io/jobs/submit/single/doc \
  -d '{}'

# 500 Internal Server Error
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-mock-response-code: 500" \
  https://174cb7a7-6aca-4c93-9cd1-639c10340684.mock.pstmn.io/jobs/submit/single/doc \
  -d '{}'
```

### Method 2: By Response Name

Use `x-mock-response-name` header to request specific example by name:

```bash
# Missing required field (400)
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-mock-response-name: Missing required field" \
  https://174cb7a7-6aca-4c93-9cd1-639c10340684.mock.pstmn.io/jobs/submit/single/doc \
  -d '{}'

# Validation failed (422)
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-mock-response-name: Validation failed" \
  https://174cb7a7-6aca-4c93-9cd1-639c10340684.mock.pstmn.io/jobs/submit/single/doc \
  -d '{}'
```

### Method 3: Random Error Testing (Automated)

Bash script to randomly test different error responses:

```bash
#!/bin/bash

MOCK_URL="https://174cb7a7-6aca-4c93-9cd1-639c10340684.mock.pstmn.io"
ENDPOINT="/jobs/submit/single/doc"
ERROR_CODES=(200 400 400 401 403 404 422 500)

for i in {1..10}; do
    # Randomly select error code
    CODE=${ERROR_CODES[$RANDOM % ${#ERROR_CODES[@]}]}

    printf "Request %2d: " $i

    # Send request with error code header
    RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "x-mock-response-code: $CODE" \
        "$MOCK_URL$ENDPOINT" \
        -d '{}')

    # Extract status from response
    STATUS=$(echo "$RESPONSE" | jq -r '.status // "unknown"')
    ERROR_CODE=$(echo "$RESPONSE" | jq -r '.errorCode // "N/A"')

    echo "HTTP $CODE → status: $STATUS, errorCode: $ERROR_CODE"
    sleep 0.5
done
```

## Response Examples Available

Each job submission endpoint has 8 response examples:

| Status Code | Response Name | Description |
|---|---|---|
| 200 | Success | Job created successfully |
| 400 | Missing required field | Required field missing from request |
| 400 | Invalid field format | Field has invalid format |
| 401 | Missing authentication | No auth header provided |
| 403 | Insufficient permissions | User lacks required permissions |
| 404 | Resource not found | Referenced resource not found |
| 422 | Validation failed | Multiple validation errors |
| 500 | Internal server error | Server encountered error |

## Default Behavior (No Header)

Without special headers, mock server **always returns 200 OK** response because:
- All examples match request equally
- Postman prioritizes 200 status code
- First 200 response (sorted by ID) is returned

This is **intentional design**, not a bug.

## Testing Workflow

### Option 1: Manual Testing
Test each error code individually using `x-mock-response-code` header.

### Option 2: Automated Testing
Use randomization script above to test all response types.

### Option 3: Postman Collection Testing
Create test collection with pre-request scripts that set error code headers:

```javascript
// Pre-request script to randomly test error responses
const errorCodes = [200, 400, 401, 403, 404, 422, 500];
const randomCode = errorCodes[Math.floor(Math.random() * errorCodes.length)];

pm.request.headers.add({
    key: 'x-mock-response-code',
    value: randomCode.toString()
});

console.log(`Testing with status code: ${randomCode}`);
```

## Key Takeaways

1. **Postman mock servers are deterministic**, not random
2. **Use headers to control responses**: `x-mock-response-code` or `x-mock-response-name`
3. **Default behavior returns 200 OK** when no header is specified
4. **All error examples exist** in collection and work correctly when requested
5. **Client-side randomization** required for random error testing

## References

- [Postman Mock Server Matching Algorithm](https://learning.postman.com/docs/design-apis/mock-apis/matching-algorithm)
- [Mock APIs with Response Examples](https://learning.postman.com/docs/design-apis/mock-apis/tutorials/mock-with-examples)
- [Generate Dynamic Mock Responses](https://learning.postman.com/docs/design-apis/mock-apis/create-dynamic-responses)

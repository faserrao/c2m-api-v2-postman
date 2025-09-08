# C2M API SDK Guide

This guide covers SDK generation, configuration, and usage for the C2M API.

## Table of Contents
- [Overview](#overview)
- [Supported Languages](#supported-languages)
- [Generating SDKs](#generating-sdks)
- [SDK Configuration](#sdk-configuration)
- [Usage Examples](#usage-examples)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Overview

The C2M API provides auto-generated SDKs for multiple programming languages using OpenAPI Generator. These SDKs simplify integration by providing:

- Type-safe API calls
- Automatic request/response handling
- Built-in authentication
- Comprehensive error handling
- IDE autocomplete support

## Supported Languages

| Language | Package Name | Generator | Status |
|----------|--------------|-----------|--------|
| Python | `c2m_api` | python | ✅ Stable |
| JavaScript | `@c2m/api-client` | javascript | ✅ Stable |
| TypeScript | `@c2m/api-client-ts` | typescript-axios | ✅ Stable |
| Java | `com.c2m:c2m-api-client` | java | ✅ Stable |
| Go | `github.com/c2m/c2mapi` | go | ✅ Stable |
| Ruby | `c2m_api` | ruby | ✅ Stable |
| PHP | `c2m/api-client` | php | ✅ Stable |

## Generating SDKs

### Quick Start

```bash
# Interactive mode - guided SDK generation
make generate-sdk

# Generate specific language SDK
make generate-sdk LANG=python

# Generate with custom output directory
scripts/generate-sdk.sh python ~/projects/c2m-python-sdk
```

### Prerequisites

1. **OpenAPI Specification**: Ensure the spec is built
   ```bash
   make openapi-build
   ```

2. **OpenAPI Generator**: Installed automatically or manually:
   ```bash
   npm install -g @openapitools/openapi-generator-cli
   # OR
   brew install openapi-generator
   ```

### Generation Process

1. **Run Generation**:
   ```bash
   make generate-sdk LANG=python
   ```

2. **Output Location**: SDKs are generated in `sdk/<language>/`

3. **Post-Generation**: 
   - Dependencies are installed automatically
   - Example files are created
   - README with usage instructions is generated

## SDK Configuration

Advanced configuration is available in `sdk-config.yaml`:

```yaml
languages:
  python:
    packageName: c2m_api
    packageVersion: 1.0.0
    library: urllib3  # or 'requests'
```

## Usage Examples

### Python

#### Installation
```bash
pip install -r sdk/python/requirements.txt
pip install -e sdk/python/
```

#### Basic Usage
```python
import c2m_api
from c2m_api.rest import ApiException

# Configure API client
configuration = c2m_api.Configuration(
    host="https://api.c2m.com/v2",
    api_key={'Authorization': 'Bearer YOUR_API_KEY'}
)

# Create API client
with c2m_api.ApiClient(configuration) as api_client:
    # Initialize endpoints
    jobs_api = c2m_api.JobsApi(api_client)
    
    # Create a job using template
    job_request = c2m_api.SingleDocJobTemplateRequest(
        template_id="standard-letter",
        document_url="https://example.com/document.pdf",
        recipients=[
            c2m_api.Recipient(
                name="John Doe",
                address=c2m_api.Address(
                    line1="123 Main St",
                    city="New York",
                    state="NY",
                    zip="10001"
                )
            )
        ]
    )
    
    try:
        # Submit job
        response = jobs_api.create_single_doc_job_template(job_request)
        print(f"Job created: {response.job_id}")
        print(f"Status: {response.status}")
    except ApiException as e:
        print(f"Error: {e.status} - {e.body}")
```

### JavaScript/Node.js

#### Installation
```bash
cd sdk/javascript
npm install
```

#### Basic Usage
```javascript
const C2mApi = require('@c2m/api-client');

// Configure client
const client = new C2mApi.ApiClient();
client.authentications['bearerAuth'].accessToken = 'YOUR_API_KEY';
client.basePath = 'https://api.c2m.com/v2';

// Initialize API
const jobsApi = new C2mApi.JobsApi(client);

// Create job
const jobRequest = new C2mApi.SingleDocJobTemplateRequest();
jobRequest.templateId = 'standard-letter';
jobRequest.documentUrl = 'https://example.com/document.pdf';
jobRequest.recipients = [{
    name: 'John Doe',
    address: {
        line1: '123 Main St',
        city: 'New York',
        state: 'NY',
        zip: '10001'
    }
}];

// Submit job
jobsApi.createSingleDocJobTemplate(jobRequest)
    .then(response => {
        console.log('Job created:', response.jobId);
        console.log('Status:', response.status);
    })
    .catch(error => {
        console.error('Error:', error.response?.body || error);
    });
```

### TypeScript

#### Installation
```bash
cd sdk/typescript
npm install
npm run build
```

#### Basic Usage
```typescript
import { Configuration, JobsApi, SingleDocJobTemplateRequest } from '@c2m/api-client-ts';

// Configure
const config = new Configuration({
    basePath: 'https://api.c2m.com/v2',
    accessToken: 'YOUR_API_KEY'
});

// Initialize API
const jobsApi = new JobsApi(config);

// Create job
const createJob = async () => {
    const request: SingleDocJobTemplateRequest = {
        templateId: 'standard-letter',
        documentUrl: 'https://example.com/document.pdf',
        recipients: [{
            name: 'John Doe',
            address: {
                line1: '123 Main St',
                city: 'New York',
                state: 'NY',
                zip: '10001'
            }
        }]
    };
    
    try {
        const { data } = await jobsApi.createSingleDocJobTemplate(request);
        console.log('Job created:', data.jobId);
    } catch (error) {
        console.error('Error:', error);
    }
};
```

### Java

#### Installation (Maven)
```xml
<dependency>
    <groupId>com.c2m</groupId>
    <artifactId>c2m-api-client</artifactId>
    <version>1.0.0</version>
</dependency>
```

#### Basic Usage
```java
import com.c2m.api.client.*;
import com.c2m.api.*;
import com.c2m.api.model.*;

public class C2MExample {
    public static void main(String[] args) {
        // Configure
        ApiClient client = Configuration.getDefaultApiClient();
        client.setBasePath("https://api.c2m.com/v2");
        
        // Authentication
        ApiKeyAuth auth = (ApiKeyAuth) client.getAuthentication("bearerAuth");
        auth.setApiKey("YOUR_API_KEY");
        auth.setApiKeyPrefix("Bearer");
        
        // Initialize API
        JobsApi jobsApi = new JobsApi(client);
        
        // Create job
        SingleDocJobTemplateRequest request = new SingleDocJobTemplateRequest()
            .templateId("standard-letter")
            .documentUrl("https://example.com/document.pdf")
            .addRecipientsItem(new Recipient()
                .name("John Doe")
                .address(new Address()
                    .line1("123 Main St")
                    .city("New York")
                    .state("NY")
                    .zip("10001")
                )
            );
        
        try {
            JobResponse response = jobsApi.createSingleDocJobTemplate(request);
            System.out.println("Job created: " + response.getJobId());
        } catch (ApiException e) {
            System.err.println("Error: " + e.getResponseBody());
        }
    }
}
```

## Authentication

All SDKs support JWT Bearer token authentication:

### Setting Authentication

**Python**:
```python
configuration.api_key['Authorization'] = 'Bearer YOUR_TOKEN'
```

**JavaScript**:
```javascript
client.authentications['bearerAuth'].accessToken = 'YOUR_TOKEN';
```

**TypeScript**:
```typescript
const config = new Configuration({
    accessToken: 'YOUR_TOKEN'
});
```

### Token Refresh

Implement automatic token refresh:

```python
# Python example
import time

class TokenManager:
    def __init__(self, refresh_callback):
        self.refresh_callback = refresh_callback
        self.token = None
        self.expires_at = 0
    
    def get_token(self):
        if time.time() >= self.expires_at - 300:  # Refresh 5 min early
            self.token, self.expires_at = self.refresh_callback()
        return self.token

# Use with SDK
token_manager = TokenManager(your_refresh_function)
configuration.api_key['Authorization'] = f'Bearer {token_manager.get_token()}'
```

## Error Handling

### Common Error Patterns

```python
# Python
try:
    response = api.create_job(request)
except c2m_api.ApiException as e:
    if e.status == 400:
        print("Bad request:", e.body)
    elif e.status == 401:
        print("Authentication failed")
    elif e.status == 429:
        print("Rate limited, retry after:", e.headers.get('Retry-After'))
    else:
        print(f"API error {e.status}: {e.reason}")
```

```javascript
// JavaScript
jobsApi.createJob(request)
    .catch(error => {
        if (error.status === 400) {
            console.error('Bad request:', error.response.body);
        } else if (error.status === 401) {
            console.error('Authentication failed');
        } else if (error.status === 429) {
            const retryAfter = error.response.headers['retry-after'];
            console.error('Rate limited, retry after:', retryAfter);
        }
    });
```

### Retry Logic

```python
# Python with exponential backoff
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except c2m_api.ApiException as e:
            if e.status == 429 or e.status >= 500:
                if attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + random.random()
                    time.sleep(sleep_time)
                    continue
            raise
```

## Best Practices

### 1. **Use Template Endpoints**
```python
# Preferred - template endpoints
response = jobs_api.create_single_doc_job_template(template_request)

# Only when needed - custom endpoints
response = jobs_api.create_single_doc_job(custom_request)
```

### 2. **Batch Operations**
```python
# Process multiple documents efficiently
requests = [create_request(doc) for doc in documents]
responses = []

for request in requests:
    try:
        response = jobs_api.create_job(request)
        responses.append(response)
    except ApiException as e:
        # Log error, continue processing
        logger.error(f"Failed to process: {e}")
```

### 3. **Connection Pooling**
```python
# Python - reuse client
api_client = c2m_api.ApiClient(configuration)
jobs_api = c2m_api.JobsApi(api_client)

# Use for multiple requests
for data in large_dataset:
    response = jobs_api.create_job(data)
```

### 4. **Logging**
```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('c2m_api')

# Log requests/responses
configuration.debug = True  # Enables detailed logging
```

### 5. **Timeout Configuration**
```python
# Python
configuration.timeout = 30  # 30 seconds

# JavaScript
client.timeout = 30000;  // 30 seconds
```

## Testing

### Unit Tests
```python
# Python example
import unittest
from unittest.mock import Mock, patch
import c2m_api

class TestC2MIntegration(unittest.TestCase):
    @patch('c2m_api.JobsApi')
    def test_create_job(self, mock_api):
        # Mock response
        mock_response = Mock()
        mock_response.job_id = '12345'
        mock_api.create_single_doc_job_template.return_value = mock_response
        
        # Test
        result = create_job_function()
        self.assertEqual(result.job_id, '12345')
```

### Integration Tests
```bash
# Use Prism mock server
make prism-start
export API_BASE_URL=http://localhost:4010

# Run SDK tests against mock
python -m pytest sdk/python/tests/
```

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors**
   ```python
   # Python - disable SSL verification (development only!)
   configuration.verify_ssl = False
   ```

2. **Proxy Configuration**
   ```python
   # Python
   configuration.proxy = "http://proxy.company.com:8080"
   ```

3. **Large File Uploads**
   ```python
   # Increase timeout for large files
   configuration.timeout = 300  # 5 minutes
   ```

4. **Rate Limiting**
   - Check `X-RateLimit-*` headers
   - Implement exponential backoff
   - Use batch endpoints when available

## SDK Development

### Contributing

1. **Report Issues**: GitHub Issues for SDK problems
2. **Custom Templates**: Override templates in `custom-templates/`
3. **Additional Properties**: Configure in `sdk-config.yaml`

### Regenerating After API Changes

```bash
# Pull latest changes
git pull

# Rebuild OpenAPI spec
make openapi-build

# Regenerate SDKs
make generate-sdk LANG=all

# Run tests
make test-sdks
```

## Resources

- [OpenAPI Generator Documentation](https://openapi-generator.tech/docs/)
- [C2M API Reference](https://api.c2m.com/docs)
- [SDK Examples Repository](https://github.com/c2m/sdk-examples)
- [Support](mailto:support@c2m.com)
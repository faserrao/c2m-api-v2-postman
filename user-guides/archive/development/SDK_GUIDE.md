# C2M API SDK Guide

This guide covers the SDK generation system, configuration options, and integration patterns for the C2M API client libraries.

## Table of Contents
- [Overview](#overview)
- [SDK Generation System](#sdk-generation-system)
- [Supported Languages](#supported-languages)
- [Generation Process](#generation-process)
- [SDK Architecture](#sdk-architecture)
- [Integration Patterns](#integration-patterns)
- [Authentication Handling](#authentication-handling)
- [Error Management](#error-management)
- [Best Practices](#best-practices)

## Overview

The C2M API SDK system provides automatically generated client libraries for multiple programming languages. These SDKs are generated from the OpenAPI specification, ensuring consistency and completeness across all supported languages.

### Key Benefits

- **Type Safety**: Strong typing based on OpenAPI schemas
- **Automatic Updates**: Regenerated when API changes
- **Consistent Interface**: Same patterns across languages
- **Built-in Features**: Authentication, retries, error handling
- **Documentation**: Auto-generated from spec

### Design Principles

1. **Specification-Driven**: OpenAPI spec is the source of truth
2. **Zero Manual Editing**: SDKs are fully generated
3. **Language Idiomatic**: Follows conventions of each language
4. **Minimal Dependencies**: Uses standard libraries where possible

## SDK Generation System

### Architecture

```
OpenAPI Specification
        ↓
OpenAPI Generator CLI
        ↓
Language Templates
        ↓
Generated SDK Code
        ↓
Post-Processing
        ↓
Published Package
```

### Generator Configuration

The system uses OpenAPI Generator with custom configurations:

1. **Global Settings**: Applied to all languages
2. **Language-Specific**: Customizations per language
3. **Template Overrides**: Custom templates when needed
4. **Post-Processing**: Additional modifications

### Build Integration

SDK generation is integrated into the main build pipeline:

```bash
make pipeline
  → openapi-build
  → sdks-generate
  → sdks-test
  → sdks-package
```

## Supported Languages

### Primary Languages

These languages receive full support and testing:

| Language | Generator | Package Manager | Testing Framework |
|----------|-----------|-----------------|-------------------|
| Python | python | pip/poetry | pytest |
| JavaScript | javascript | npm | jest |
| TypeScript | typescript-axios | npm | jest |
| Java | java | maven/gradle | junit |
| C# | csharp | nuget | xunit |
| Go | go | go modules | go test |

### Secondary Languages

Additional languages with community support:

| Language | Generator | Status |
|----------|-----------|--------|
| Ruby | ruby | Stable |
| PHP | php | Stable |
| Swift | swift5 | Beta |
| Kotlin | kotlin | Beta |
| Rust | rust | Beta |

### Language Features

Each SDK includes:
- Full API coverage
- Type definitions
- Authentication helpers
- Example code
- Unit tests
- Documentation

## Generation Process

### Automated Generation

The build system automatically generates SDKs:

```bash
# Generate all SDKs
make sdks-generate

# Generate specific language
make sdk-python
make sdk-javascript
make sdk-java
```

### Manual Generation

For custom requirements:

```bash
# Direct generator invocation
openapi-generator-cli generate \
  -i openapi/c2mapiv2-openapi-spec-final.yaml \
  -g python \
  -o sdk/python \
  --config sdk-configs/python.yaml
```

### Configuration Files

Each language has a configuration file:

```yaml
# sdk-configs/python.yaml
packageName: c2m_api
packageVersion: "2.0.0"
projectName: c2m-api-python
library: urllib3
generateSourceCodeOnly: false
```

### Post-Processing

After generation, additional processing:

1. **Dependency Management**: Update package files
2. **Code Formatting**: Apply language standards
3. **Documentation**: Generate README
4. **Examples**: Create usage examples
5. **Tests**: Generate test stubs

## SDK Architecture

### Package Structure

Standard structure across languages:

```
sdk/python/
├── c2m_api/
│   ├── api/           # API methods
│   ├── models/        # Data models
│   ├── auth/          # Authentication
│   └── __init__.py
├── tests/             # Unit tests
├── examples/          # Usage examples
├── docs/              # API documentation
├── README.md
└── setup.py           # Package config
```

### Core Components

1. **API Clients**: One per API tag/section
2. **Models**: Request/response objects
3. **Authentication**: Token management
4. **Configuration**: Client settings
5. **Exceptions**: Error types

### Dependency Strategy

Minimal dependencies approach:
- Use standard library when possible
- Popular, well-maintained packages
- Version ranges for flexibility
- Security-verified dependencies

## Integration Patterns

### Client Initialization

Pattern consistent across languages:

```python
# Python
from c2m_api import Configuration, ApiClient, JobsApi

config = Configuration()
config.host = "https://api.c2m.example.com"
client = ApiClient(config)
jobs_api = JobsApi(client)
```

```javascript
// JavaScript
const C2MApi = require('@c2m/api-client');

const config = new C2MApi.Configuration({
  basePath: 'https://api.c2m.example.com'
});
const client = new C2MApi.ApiClient(config);
const jobsApi = new C2MApi.JobsApi(client);
```

### Request Patterns

Consistent method signatures:

```python
# Submit single document
response = jobs_api.submit_single_doc(
    body=SubmitSingleDocRequest(
        document_source=DocumentSource(url="..."),
        recipient_address=Address(...)
    )
)

# Get job status
status = jobs_api.get_job_status(job_id="job123")
```

### Response Handling

Strongly typed responses:

```python
# Response is typed model
job = response.job
print(f"Job ID: {job.job_id}")
print(f"Status: {job.status}")

# Access nested properties safely
if job.tracking:
    print(f"Tracking: {job.tracking.url}")
```

## Authentication Handling

### Built-in Token Management

SDKs include authentication helpers:

```python
from c2m_api.auth import TokenManager

# Initialize token manager
token_manager = TokenManager(
    client_id="your-client-id",
    client_secret="your-secret",
    auth_url="https://auth.c2m.example.com"
)

# Automatic token refresh
config.access_token = token_manager.get_access_token()
```

### Custom Authentication

For advanced scenarios:

```python
# Custom token provider
class CustomTokenProvider:
    def get_token(self):
        # Custom logic
        return token
    
config.access_token_provider = CustomTokenProvider()
```

### Security Best Practices

1. **Never hardcode credentials**
2. **Use environment variables**
3. **Implement token caching**
4. **Handle token expiration**
5. **Secure token storage**

## Error Management

### Exception Hierarchy

Consistent error types:

```python
from c2m_api.exceptions import (
    ApiException,      # Base exception
    ApiValueError,     # Invalid parameters
    ApiKeyError,       # Missing required fields
    ApiTypeError      # Type mismatches
)

try:
    response = jobs_api.submit_single_doc(request)
except ApiException as e:
    print(f"API error: {e.status} - {e.reason}")
    print(f"Response body: {e.body}")
```

### Error Handling Patterns

Recommended approach:

```python
def submit_with_retry(request, max_retries=3):
    for attempt in range(max_retries):
        try:
            return jobs_api.submit_single_doc(request)
        except ApiException as e:
            if e.status == 429:  # Rate limited
                time.sleep(2 ** attempt)
            elif e.status >= 500:  # Server error
                if attempt < max_retries - 1:
                    continue
            raise
```

### Logging Integration

SDKs support standard logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# SDK will log requests/responses
```

## Best Practices

### Development Workflow

1. **Generate Fresh SDKs**: After API changes
2. **Run Tests**: Validate generation
3. **Update Examples**: Keep current
4. **Version Appropriately**: Semantic versioning
5. **Document Changes**: Update changelog

### Integration Guidelines

1. **Use Type Hints**: Leverage IDE support
2. **Handle Errors**: Implement proper error handling
3. **Configure Timeouts**: Set appropriate limits
4. **Monitor Usage**: Track API calls
5. **Cache Responses**: When appropriate

### Performance Optimization

1. **Connection Pooling**: Reuse connections
2. **Async Support**: Use async variants
3. **Batch Operations**: Group requests
4. **Response Caching**: Cache when safe
5. **Timeout Tuning**: Balance reliability/speed

### Security Considerations

1. **Credential Storage**: Use secure storage
2. **TLS Verification**: Always verify certificates
3. **Input Validation**: SDK validates automatically
4. **Token Rotation**: Implement rotation strategy
5. **Audit Logging**: Log security events

---

*This guide covers the SDK generation system and best practices for integrating C2M API client libraries. For language-specific details, refer to the README in each SDK directory.*
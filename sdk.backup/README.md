# SDK Directory

This directory contains client SDKs for the C2M API in various programming languages. SDKs are automatically generated from the OpenAPI specification using OpenAPI Generator.

## Directory Structure

```
sdk/
├── python/          # Python SDK (currently available)
├── javascript/      # JavaScript/Node.js SDK (coming soon)
├── typescript/      # TypeScript SDK (coming soon)
├── java/           # Java SDK (coming soon)
├── go/             # Go SDK (coming soon)
├── ruby/           # Ruby SDK (coming soon)
└── php/            # PHP SDK (coming soon)
```

## Available SDKs

### Python SDK
Full-featured Python client library for C2M API.
- **Status**: ✅ **Available and Generated**
- **Documentation**: [Python SDK README](python/README.md)
- **Installation**: `pip install c2m-api` (or `pip install -e .` from sdk/python)
- **Minimum Version**: Python 3.9+

### JavaScript SDK
JavaScript/Node.js client library for C2M API.
- **Status**: 📁 **Directory Created, Not Yet Generated**
- **Documentation**: [JavaScript SDK README](javascript/README.md)
- **Installation**: Will be available via NPM after generation
- **Support**: Node.js 14+ and modern browsers

## SDK Generation

SDKs are generated using the OpenAPI Generator tool. To generate or update SDKs:

```bash
# Generate specific SDK
make generate-sdk LANG=python

# Interactive mode (choose language)
make generate-sdk
```

### Supported Languages
- Python
- JavaScript/Node.js
- TypeScript
- Java
- Go
- Ruby
- PHP

## Configuration

SDK generation is configured in:
- `sdk-config.yaml` - Global SDK settings
- Per-language configurations in generator script

## Common Features

All SDKs provide:
- **Type Safety**: Strongly typed request/response models
- **Authentication**: Built-in JWT token management
- **Error Handling**: Consistent error responses
- **Retry Logic**: Configurable retry mechanisms
- **Examples**: Usage examples for common operations

## Usage Pattern

Regardless of language, SDKs follow a similar pattern:

1. **Initialize Client**
   ```
   client = C2MClient(api_key="your-key")
   ```

2. **Make Requests**
   ```
   response = client.submit_single_doc_template(...)
   ```

3. **Handle Responses**
   ```
   if response.success:
       print(f"Job ID: {response.job_id}")
   ```

## Development

### Regenerating SDKs
After OpenAPI spec changes:
```bash
make generate-openapi-spec-from-ebnf-dd
make generate-sdk LANG=all
```

### Testing SDKs
Each SDK includes comprehensive test suites:
```bash
cd sdk/python
pytest
```

### Contributing
When adding new SDK languages:
1. Update `scripts/utilities/generate-sdk.sh` with language config
2. Create language directory
3. Generate initial SDK
4. Add language-specific README
5. Configure package management

## Best Practices

1. **Use Template Endpoints**: Start with template-based endpoints
2. **Handle Errors**: Always implement proper error handling
3. **Secure Credentials**: Never hardcode API keys
4. **Update Regularly**: Keep SDKs updated with API changes
5. **Test Thoroughly**: Use mock servers for testing

## Support

- **Issues**: Report SDK issues in GitHub
- **Documentation**: See language-specific READMEs
- **API Reference**: [API Documentation](../docs/README.md)
- **Examples**: [Code Examples](../examples/README.md)

## Roadmap

- [x] Python SDK
- [ ] JavaScript/Node.js SDK
- [ ] TypeScript SDK
- [ ] Java SDK
- [ ] Go SDK
- [ ] Ruby SDK
- [ ] PHP SDK
- [ ] SDK versioning automation
- [ ] SDK publishing automation
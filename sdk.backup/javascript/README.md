# JavaScript SDK

This directory is reserved for the JavaScript/Node.js SDK for the C2M API.

## Current Status

🚧 **Not Yet Generated** - The JavaScript SDK has not been generated yet. The directory exists as a placeholder.

## Generating the JavaScript SDK

To generate the JavaScript SDK, run:

```bash
# From the project root
make generate-sdk LANG=javascript
```

Or use the generation script directly:

```bash
./scripts/generate-sdk.sh javascript
```

## What Will Be Generated

When generated, this directory will contain:

```
javascript/
├── src/                      # Source code
│   ├── api/                 # API client classes
│   ├── model/               # Data models
│   ├── ApiClient.js         # Core API client
│   └── index.js             # Main entry point
├── docs/                     # API documentation
│   ├── DefaultApi.md        # Main API docs
│   ├── AuthApi.md           # Auth API docs
│   └── *.md                 # Model documentation
├── test/                     # Test suite
│   ├── api/                 # API tests
│   └── model/               # Model tests
├── dist/                     # Built/bundled code
├── node_modules/             # Dependencies
├── package.json              # NPM package config
├── README.md                 # SDK documentation
├── .babelrc                  # Babel config
├── .gitignore               # Git ignore rules
└── webpack.config.js         # Webpack bundling
```

## Planned Features

The JavaScript SDK will provide:

### Core Functionality
- Complete API coverage for all endpoints
- Promise-based async operations
- Automatic request/response transformation
- Built-in error handling
- Request retry logic

### Authentication
- JWT token management
- Automatic token refresh
- Secure credential storage
- Multiple auth methods support

### Developer Experience
- Full JSDoc documentation
- TypeScript definitions
- Browser and Node.js support
- Tree-shaking support
- Minimal dependencies

## Example Usage (After Generation)

```javascript
const C2MApi = require('c2m-api');
// or
import C2MApi from 'c2m-api';

// Configure API client
const client = new C2MApi.ApiClient();
client.authentications['bearerAuth'].accessToken = 'YOUR_JWT_TOKEN';

// Create API instance
const api = new C2MApi.DefaultApi(client);

// Use template endpoint (recommended)
const request = new C2MApi.SubmitSingleDocWithTemplateParamsRequest();
request.jobTemplate = 'standard-letter';
request.documentSourceIdentifier = 'https://example.com/document.pdf';
request.paymentDetails = {
  paymentMethod: 'purchase-order',
  purchaseOrderNumber: 'PO-12345'
};

// Submit job
api.submitSingleDocWithTemplateParams(request)
  .then(response => {
    console.log('Job created:', response.jobId);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

## Browser Support

The SDK will support modern browsers with:
- Webpack bundle for direct browser use
- ES6 module support
- Promise polyfill for older browsers
- Fetch API or XMLHttpRequest

## Node.js Support

Requirements:
- Node.js 14.x or higher
- NPM 6.x or higher

## Why Not Generated Yet?

The JavaScript SDK generation is pending:
1. Python SDK was prioritized for initial release
2. JavaScript SDK configuration needs finalization
3. Awaiting decisions on TypeScript support level
4. Browser bundling strategy being determined

## Next Steps

1. Finalize JavaScript SDK configuration in `sdk-config.yaml`
2. Run SDK generation
3. Add JavaScript-specific enhancements
4. Create comprehensive examples
5. Publish to NPM registry

## Related Documentation

- [SDK Overview](../README.md)
- [Python SDK](../python/README.md) - See the Python SDK for reference
- [SDK Generation Guide](../../SDK_GUIDE.md)
- [API Documentation](../../docs/README.md)
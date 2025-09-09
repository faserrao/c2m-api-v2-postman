# JavaScript SDK (Placeholder)

This directory is a placeholder for the future JavaScript/Node.js SDK for the C2M API.

## Status

⚠️ **Not Yet Implemented** - The active JavaScript SDK development is tracked in the main `/sdk` directory.

## Planned Features

When implemented, this SDK will provide:

### Core Features
- Full TypeScript support with type definitions
- Promise-based API with async/await
- Automatic token refresh for JWT authentication
- Request/response interceptors
- Comprehensive error handling

### Environment Support
- **Node.js**: 16.x and higher
- **Browsers**: Modern browsers (Chrome, Firefox, Safari, Edge)
- **React Native**: Compatible with RN projects

### Installation (Future)
```bash
npm install @c2m/api-client
# or
yarn add @c2m/api-client
```

### Usage Example (Planned API)
```javascript
import { C2MClient } from '@c2m/api-client';

// Initialize client
const client = new C2MClient({
  apiKey: 'your-api-key',
  environment: 'production' // or 'sandbox'
});

// Use template endpoint (recommended)
const response = await client.jobs.submitWithTemplate({
  templateId: 'monthly-invoice',
  documentUrl: 'https://example.com/invoice.pdf',
  paymentDetails: {
    method: 'purchase-order',
    poNumber: 'PO-12345'
  }
});

console.log(`Job ID: ${response.jobId}`);
```

### Planned Architecture

```
javascript/
├── src/
│   ├── client/           # Core client implementation
│   ├── models/           # TypeScript interfaces
│   ├── services/         # API endpoint services
│   ├── auth/            # Authentication handling
│   └── utils/           # Helper utilities
├── dist/                # Compiled output
│   ├── esm/            # ES modules
│   ├── cjs/            # CommonJS
│   └── browser/        # Browser bundle
├── examples/            # Usage examples
├── tests/              # Test suite
├── package.json
├── tsconfig.json
├── README.md
└── LICENSE
```

## Development Roadmap

1. **Phase 1**: Basic API implementation
2. **Phase 2**: Authentication and token management
3. **Phase 3**: Advanced features (retry, caching)
4. **Phase 4**: Framework integrations (React hooks)

## SDK Generation

To generate the JavaScript SDK:
```bash
cd /path/to/c2m-api-repo
make generate-sdk LANG=javascript
```

The generated SDK will be placed in `/sdk/javascript/`.

## Contributing

SDK development is managed through the main repository. To contribute:
1. Check the `/sdk` directory for active development
2. Follow the SDK contribution guidelines
3. Submit PRs to the main repository

## Related Documentation

- [Active SDK Directory](/sdk/README.md)
- [API Documentation](/docs/README.md)
- [TypeScript Examples](/examples/typescript/)
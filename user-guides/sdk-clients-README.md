# SDK Clients Directory

This directory contains placeholder structures for future SDK client libraries. These SDKs will be auto-generated from the OpenAPI specification to provide native language support for the C2M API.

## Directory Structure

```
sdk-clients/
├── README.md          # This file
├── javascript/        # JavaScript/Node.js SDK placeholder
│   └── README.md     
└── python/           # Python SDK placeholder
    └── README.md
```

## Purpose

This directory serves as a template structure for SDK generation. The actual SDKs are currently located in the `/sdk` directory.

### Current Status

- **Active SDKs**: Located in `/sdk` directory
- **This Directory**: Reserved for future SDK reorganization

## Planned SDKs

### JavaScript SDK (`javascript/`)
- **Target**: Browser and Node.js environments
- **Features**: 
  - Promise-based API
  - TypeScript definitions
  - Automatic retry logic
  - Browser-compatible builds

### Python SDK (`python/`)
- **Target**: Python 3.9+
- **Features**:
  - Type hints
  - Async/await support
  - Comprehensive error handling
  - pip installable

## SDK Generation

To generate SDKs, use the main SDK generation tool:

```bash
# Generate all SDKs
make generate-sdk

# Generate specific SDK
make generate-sdk LANG=javascript
```

Generated SDKs will be placed in the `/sdk` directory, not here.

## Why Two SDK Directories?

1. **`/sdk`** - Active directory containing generated SDKs
2. **`/sdk-clients`** - Template/placeholder for future reorganization

This structure allows for:
- Gradual migration to new structure
- Testing new SDK configurations
- Maintaining backward compatibility

## Migration Plan

Future plans to consolidate SDK locations:
1. Generate new SDKs in `/sdk-clients`
2. Test and validate new structure
3. Deprecate `/sdk` directory
4. Update all references

## Related Documentation

- [Active SDK Directory](/sdk/README.md)
- [SDK Generation Guide](/SDK_GUIDE.md)
- [OpenAPI Specification](/openapi/README.md)
- [Root README](/README.md)
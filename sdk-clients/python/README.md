# Python SDK (Placeholder)

This directory is a placeholder for the future Python SDK for the C2M API.

## Status

WARNING **Active SDK Available** - A fully functional Python SDK is already available in the `/sdk/python/` directory. This directory is reserved for future SDK reorganization.

## Current Python SDK

The active Python SDK is located at: `/sdk/python/`

To use the current SDK:
```bash
cd /sdk/python
pip install -e .
```

See the [Python SDK Documentation](/sdk/python/README.md) for complete details.

## Purpose of This Directory

This placeholder exists for:
- Future SDK structure reorganization
- Testing alternative SDK generation configurations
- Maintaining consistent directory structure across language SDKs

## Planned Migration

When this directory becomes active, it will mirror the structure of the current SDK:

```
python/
├── c2m_api/              # Main package
│   ├── api/             # API endpoint implementations
│   ├── models/          # Data models
│   └── auth/            # Authentication handling
├── tests/               # Test suite
├── docs/                # API documentation
├── examples/            # Usage examples
├── setup.py            # Package setup
├── requirements.txt    # Dependencies
└── README.md          # Documentation
```

## Related Resources

- [Active Python SDK](/sdk/python/README.md) - Current implementation
- [SDK Generation Guide](/SDK_GUIDE.md) - How to generate SDKs
- [API Documentation](/docs/README.md) - API reference
- [Python Examples](/examples/README.md) - Code examples
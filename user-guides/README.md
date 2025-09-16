# C2M API V2 User Guides

This directory contains comprehensive documentation for understanding and working with the C2M API v2 build system and infrastructure.

## 📚 Documentation Overview

### Core Documentation

#### [BUILD_INFRASTRUCTURE_GUIDE.md](./BUILD_INFRASTRUCTURE_GUIDE.md)
The complete technical reference for the C2M API v2 build system. This guide explains:
- How the build pipeline transforms EBNF to a complete API ecosystem
- All Makefile targets and their purposes
- GitHub Actions CI/CD workflows
- Dynamic resource management for Postman
- Test generation and execution
- Documentation and SDK generation processes

### Additional Guides

#### Security Setup
- **SECURITY_REPO_GITHUB_SETUP.md** - Instructions for configuring the security repository integration

#### File Inspection Tools
- **finspect-README.md** - Documentation for the file inspection utility
- **finspect-file-type-detection-methods.md** - Technical details on file type detection

## 🚀 Getting Started

For developers new to the C2M API v2 build system:

1. **Read the BUILD_INFRASTRUCTURE_GUIDE** to understand the complete system
2. **Run `make check-env`** to verify your local setup
3. **Execute `make pipeline`** to run the complete build
4. **Check generated artifacts** in `dist/`, `docs/`, and `postman/` directories

## 🔧 Key Concepts

### Build Pipeline
The system follows a linear transformation pipeline:
```
EBNF → OpenAPI → Postman → Tests → Docs/SDKs
```

### Dynamic Resources
All Postman collections, mock servers, and environments are created dynamically during the build process. The system tracks these using UID files that persist between builds.

### Environment Agnostic
The same Makefile targets work both locally and in CI/CD, with appropriate adaptations for each environment.

## 📁 Related Directories

- `/openapi` - OpenAPI specifications and schemas
- `/postman` - Postman collections and test results  
- `/scripts` - Build scripts and utilities
- `/docs` - Generated API documentation
- `/dist` - Build artifacts and SDKs
- `/.github/workflows` - CI/CD configurations

## 🔄 Build Commands

Quick reference for common operations:

```bash
# Complete build pipeline
make pipeline

# Check environment setup
make check-env

# Clean all artifacts
make clean-all

# Run tests only
make postman-test

# Generate documentation
make docs-build

# Create SDKs
make sdks-generate
```

## 📝 Archive

Previous versions of documentation are preserved in the `archive/` subdirectory for historical reference.

---

*Last Updated: 2025-09-15*  
*Version: 2.0 - Post-consolidation and accuracy improvements*
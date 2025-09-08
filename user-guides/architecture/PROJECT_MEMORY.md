# PROJECT_MEMORY.md - C2M API Project Knowledge Base

This document captures critical learnings, patterns, and institutional knowledge from the C2M API V2 project. It serves as a comprehensive reference for understanding the project's architecture, history, and best practices.

## Table of Contents

1. [Project Architecture & Flow](#project-architecture--flow)
2. [Key File Locations](#key-file-locations)
3. [Common Issues & Solutions](#common-issues--solutions)
4. [Makefile Patterns](#makefile-patterns)
5. [Testing Strategies](#testing-strategies)
6. [Integration Points](#integration-points)
7. [Lessons from Restoration](#lessons-from-restoration)
8. [Key Development Decisions](#key-development-decisions)
9. [Best Practices](#best-practices)

## Project Architecture & Flow

### Core Pipeline

The C2M API follows a unique data-driven pipeline:

```
EBNF Data Dictionary → OpenAPI Spec → Postman Collection → Mock Server → API Documentation
```

1. **EBNF Data Dictionary** (`data_dictionary/`)
   - Single source of truth for all data structures
   - Uses Extended Backus-Naur Form for precision
   - Converted to OpenAPI via custom Python script

2. **OpenAPI Specification** (`openapi/`)
   - Generated from EBNF, never hand-edited
   - Serves as contract for API implementation
   - Validated using Spectral linting

3. **Postman Collections** (`postman/`)
   - Auto-generated from OpenAPI spec
   - Enhanced with test data and assertions
   - Used for both testing and documentation

4. **Mock Servers**
   - Local: Prism (port 4010)
   - Cloud: Postman mock servers
   - Enables API-first development

5. **Documentation** (`docs/`)
   - Generated using Redocly
   - Hosted on GitHub Pages
   - Auto-updates via CI/CD

### Authentication Architecture

Two-repository approach:
- **c2m-api-repo**: Main API implementation
- **c2m-api-v2-security**: Authentication infrastructure (AWS CDK)

JWT two-token system:
- Long-term tokens (30-90 days)
- Short-term tokens (15 minutes)
- Token storage in DynamoDB with TTL

## Key File Locations

### Primary Configuration
- `Makefile` - Main orchestration file
- `.env` - Environment variables (API keys)
- `.postman-target` - Workspace target selector

### Data Flow Files
```
data_dictionary/
├── attributes.dd
├── endpoints.dd
└── values.dd
    
openapi/
├── c2mapiv2-openapi-spec.yaml (generated)
└── c2mapiv2-openapi-spec-final.yaml (enhanced)

postman/
├── generated/
│   ├── C2M API V2 - Jobs.postman_collection.json
│   ├── C2M API V2 - Templates.postman_collection.json
│   └── C2M API V2 - ...
├── custom/
│   └── overrides.json
└── tracking files (UIDs, URLs, etc.)
```

### Scripts
```
scripts/
├── active/
│   ├── ebnf_to_openapi_class_based.py  # Core converter
│   ├── add_tests.js                    # Test enhancement
│   └── fix_collection_urls_v2.py       # URL normalization
├── utilities/
│   └── various helper scripts
└── python_env/
    └── e2o.venv                        # Python virtual environment
```

## Common Issues & Solutions

### 1. Double-Encoding Bug in OpenAPI Spec

**Issue**: Authentication examples were double-encoded, breaking Postman imports
```json
// Bad:
"example": "{\"grant_type\":\"client_credentials\",...}"

// Good:
"example": {"grant_type":"client_credentials",...}
```

**Solution**: Fixed in `ebnf_to_openapi_class_based.py` to properly handle JSON examples

### 2. PyYAML FullLoader Deprecation

**Issue**: Warning about deprecated FullLoader
**Solution**: Run `make fix-yaml` or update to use `yaml.safe_load()`

### 3. Postman Collection URL Issues

**Issue**: Collections generated with hardcoded URLs instead of variables
**Solution**: `fix_collection_urls_v2.py` replaces URLs with `{{baseUrl}}`

### 4. GitHub Actions jq Syntax

**Issue**: Multi-line jq commands failed in GitHub Actions
**Solution**: Use single-line portable syntax without line continuations

### 5. API Deletion Only Deleting One Item

**Issue**: Cleanup only deleted first API in workspace
**Solution**: Fixed loop logic to delete all APIs before proceeding

### 6. Wrong Workspace Publishing

**Issue**: CI/CD published to wrong Postman workspace
**Solution**: Implemented `.postman-target` file system

### 7. GitHub Actions CI/CD Failures (2025-09-08)

**Issue**: Multiple CI/CD pipeline failures preventing Postman publishing and docs deployment
**Root Causes & Solutions**:

a) **Postman CLI not found (Error 127)**
   - Added explicit installation in GitHub Actions workflow:
   ```yaml
   curl -o- "https://dl-cli.pstmn.io/install/linux64.sh" | sh
   ```

b) **Prism mock server fails in CI**
   - Created CI-specific build targets that skip local testing:
   - `postman-instance-build-only` (no prism-start or docs-serve)
   - `rebuild-all-no-delete-ci` and `rebuild-all-with-delete-ci`
   - Updated publish targets to use CI versions automatically

c) **openapi-diff command hanging**
   - npm version of openapi-diff behaves differently than brew version
   - Temporarily disabled in Makefile (commented out line 691)
   - TODO: Find compatible alternative or fix command flags

## Makefile Patterns

### Orchestration Philosophy

The Makefile serves as the central command interface:

```makefile
# Primary development command
postman-collection-build-and-test: \
    generate-openapi-spec-from-dd \
    postman-collection-create \
    add-test-data \
    postman-test-validate
```

### Key Patterns

1. **Target Chaining**: Complex workflows built from simple targets
2. **Conditional Logic**: Uses shell conditionals for decision making
3. **File Tracking**: Saves UIDs/URLs for later reference
4. **Error Handling**: Explicit error checking with meaningful messages

### Smart Rebuild System

Introduced hash-based change detection:
```bash
make smart-rebuild              # Only rebuild what changed
make smart-rebuild-dry-run      # Preview changes
make smart-rebuild-status       # Show current state
```

## Testing Strategies

### 1. Mock Server Testing

**Local (Prism)**:
```bash
make prism-start
make prism-test-endpoint PRISM_TEST_ENDPOINT=/jobs/single-doc
make prism-test-select PRISM_TEST_ENDPOINT=/jobs/single-doc PRISM_TEST_INDEX=2
```

**Cloud (Postman)**:
```bash
make postman-mock-create
make postman-mock
```

### 2. Collection Testing

- Automatic test generation via `add_tests.js`
- Response validation against OpenAPI schema
- Status code verification
- Authentication flow testing

### 3. Integration Testing

- Full pipeline validation: `make postman-collection-build-and-test`
- CI/CD runs tests on every commit
- PR drift checks ensure generated files are current

## Integration Points

### 1. Between Repositories

**c2m-api-repo ↔ c2m-api-v2-security**:
- JWT configuration shared via environment variables
- Pre-request scripts handle token refresh
- Authentication endpoints defined in main OpenAPI spec

### 2. With External Services

**Postman**:
- API key authentication
- Workspace-based organization
- Mock server synchronization

**AWS**:
- CDK deployment of auth stack
- Secrets Manager for credentials
- API Gateway for endpoints

**GitHub**:
- Actions for CI/CD
- Pages for documentation hosting
- PR checks for drift detection

## Lessons from Restoration

### 1. State Management is Critical

The pre-authentication state restoration revealed:
- Need for comprehensive backup strategies
- Importance of versioned configurations
- Value of git history for recovery

### 2. Documentation as Code

- All docs generated from source files
- Manual documentation quickly becomes stale
- Automation ensures consistency

### 3. Minimal Viable Authentication

Decision to defer full auth integration was correct:
- Allowed focus on core API functionality
- Authentication can be layered on later
- Mock servers don't need real auth

### 4. File Organization Matters

Clear separation of:
- Generated vs. source files
- Active vs. archived scripts
- Configuration vs. implementation

## Key Development Decisions

### 1. EBNF as Source of Truth

**Rationale**: 
- Formal grammar prevents ambiguity
- Single source reduces drift
- Enables automated generation

**Impact**: 
- Steep learning curve
- Powerful automation capabilities
- Consistent API design

### 2. Two-Token JWT System

**Rationale**:
- Balance security and usability
- Reduce token refresh overhead
- Standard OAuth2 patterns

**Impact**:
- Complex initial setup
- Flexible authentication flows
- Industry-standard approach

### 3. Makefile as Orchestrator

**Rationale**:
- Universal availability
- Simple dependency management
- Self-documenting commands

**Impact**:
- Some complexity for advanced logic
- Excellent discoverability
- Easy CI/CD integration

### 4. Generated Documentation

**Rationale**:
- Always in sync with code
- Reduces maintenance burden
- Professional appearance

**Impact**:
- Less flexibility in formatting
- Guaranteed accuracy
- Automated updates

## Best Practices

### 1. Development Workflow

```bash
# 1. Make changes to EBNF
# 2. Run full pipeline
make postman-collection-build-and-test
# 3. Verify with mock
make prism-mock-test
# 4. Commit all generated files
git add -A && git commit -m "feat: your change"
```

### 2. Debugging

- Use `make print-openapi-vars` for variable inspection
- Check `postman/*.uid` files for resource tracking
- Run individual pipeline steps to isolate issues
- Use dry-run modes before destructive operations

### 3. Environment Management

- Never commit `.env` files
- Use `.env.example` for documentation
- Rotate API keys regularly
- Keep workspace IDs in version control

### 4. Code Organization

- Keep generated files in dedicated directories
- Archive old scripts rather than deleting
- Document decision rationale in commits
- Use semantic versioning for releases

### 5. Testing Philosophy

- Test against mocks during development
- Validate all generated artifacts
- Automate repetitive checks
- Fail fast with clear error messages

## Historical Timeline

1. **Initial Development**: EBNF-based pipeline concept
2. **Script Evolution**: Multiple iterations of conversion scripts
3. **Authentication Design**: Two-repo approach decided
4. **CI/CD Implementation**: GitHub Actions workflow
5. **Restoration Event**: Pre-auth state recovery needed
6. **Smart Rebuild**: Hash-based change detection added
7. **Documentation Overhaul**: Comprehensive guides created

## Critical Success Factors

1. **Automation First**: Every manual process should become automated
2. **Single Source of Truth**: EBNF drives everything
3. **Fail Fast**: Clear error messages at each step
4. **Version Everything**: Including generated files
5. **Document Decisions**: Not just what, but why

## Future Considerations

1. **API Implementation**: Generated specs need real backends
2. **Performance Testing**: Load testing infrastructure
3. **Monitoring**: Operational visibility
4. **SDK Evolution**: More language targets
5. **Security Hardening**: Beyond basic JWT

---

*This document represents accumulated knowledge as of 2025-09-08. Update as new patterns emerge and lessons are learned.*
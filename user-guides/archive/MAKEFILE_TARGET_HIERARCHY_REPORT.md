# Makefile Target Hierarchy Report

Generated on: September 8, 2025

## Overview

Total targets: 113
Documented targets (with ##): 25

> **Note**: This report has been updated after the Makefile cleanup that removed redundant auth-related targets.

## Primary Entry Points

### 1. `help`
- **Purpose**: Display Makefile help (default target)
- **Calls**: None
- **Type**: User-facing entry point

### 2. `postman-instance-build-and-test`
- **Purpose**: Complete pipeline: build and test with Postman
- **Calls**:
  - `postman-login`
  - `postman-import-openapi-spec`
  - `postman-create-linked-collection`
  - `postman-create-test-collection`
  - `postman-create-mock-and-env`
  - `run-postman-and-prism-tests`

### 3. `rebuild-all-with-delete`
- **Purpose**: Clean rebuild of everything
- **Calls**:
  - `postman-cleanup-all`
  - `rebuild-all-no-delete`

### 4. `rebuild-all-no-delete`
- **Purpose**: Rebuild without cleanup
- **Calls**:
  - `postman-login`
  - `openapi-build`
  - `postman-collection-build`
  - `postman-create-mock-and-env`
  - `run-postman-and-prism-tests`

### 5. `smart-rebuild`
- **Purpose**: Intelligent rebuild based on file changes
- **Calls**:
  - `smart-rebuild-check-and-run`

## Target Categories

### OpenAPI Generation

#### `generate-openapi-spec-from-dd`
- **Purpose**: Generate OpenAPI spec from data dictionary
- **Calls**:
  - `generate-openapi-spec-from-ebnf-dd`
  - `openapi-assemble-final`
  - `lint`

#### `generate-openapi-spec-from-ebnf-dd`
- **Purpose**: Convert EBNF to OpenAPI using Python
- **Calls**: None (executes Python script)
- **Note**: Includes venv creation inline

#### `openapi-assemble-final`
- **Purpose**: Merge base spec with auth overlay
- **Calls**: None (uses yq for merging)

#### `lint`
- **Purpose**: Validate OpenAPI specification
- **Calls**: None (runs linting tools)

### Postman Collection Management

#### `postman-import-openapi-spec`
- **Purpose**: Import OpenAPI as API and standalone spec
- **Calls**:
  - `postman-import-openapi-as-api`
  - `postman-spec-create-standalone`

#### `postman-create-linked-collection`
- **Purpose**: Create collection linked to API
- **Calls**:
  - `postman-api-linked-collection-generate`
  - `postman-linked-collection-flatten`
  - `postman-linked-collection-upload`
  - `postman-linked-collection-link`

#### `postman-create-test-collection`
- **Purpose**: Create test-ready collection
- **Calls**:
  - `postman-test-collection-generate`
  - `postman-test-collection-add-examples`
  - `postman-test-collection-merge-overrides`
  - `postman-test-collection-add-tests`
  - `postman-test-collection-diff-tests`
  - `postman-test-collection-auto-fix`
  - `postman-test-collection-fix-v2`
  - `postman-test-collection-validate`
  - `verify-urls`
  - `fix-urls`
  - `postman-test-collection-flatten-rename`

#### `postman-collection-build`
- **Purpose**: CI/CD alias for collection generation
- **Calls**:
  - `postman-api-linked-collection-generate`
  - `postman-linked-collection-flatten`

### Mock Server Management

#### `postman-create-mock-and-env`
- **Purpose**: Create mock server with environment
- **Calls**:
  - `postman-mock-create`
  - `postman-env-create`
  - `postman-env-upload`
  - `update-mock-env`

#### `postman-mock-create`
- **Purpose**: Create Postman mock server
- **Calls**: None (API call)

#### `prism-start`
- **Purpose**: Start local Prism mock server
- **Calls**: None (starts server process)

### Testing

#### `run-postman-and-prism-tests`
- **Purpose**: Run all mock server tests
- **Calls**:
  - `prism-start`
  - `prism-mock-test`
  - `postman-mock`

#### `postman-mock`
- **Purpose**: Run tests against Postman mock
- **Calls**: None (runs Newman)

#### `prism-mock-test`
- **Purpose**: Run tests against Prism mock
- **Calls**: None (runs Newman)

### Cleanup Operations

#### `postman-cleanup-all`
- **Purpose**: Complete Postman workspace cleanup
- **Calls**:
  - `postman-env-delete`
  - `postman-collection-delete`
  - `postman-mock-delete`
  - `postman-spec-clean-all`
  - `postman-api-clean`
  - `postman-api-clean-trash`

#### `postman-collection-delete`
- **Purpose**: Delete all collections
- **Calls**: Multiple collection deletion targets

#### `postman-env-delete`
- **Purpose**: Delete all environments
- **Calls**: None (API calls)

### Smart Rebuild System

#### `smart-rebuild`
- **Purpose**: Main smart rebuild entry point
- **Calls**:
  - `smart-rebuild-check-and-run`

#### `smart-rebuild-check-and-run`
- **Purpose**: Check changes and rebuild as needed
- **Calls**: Various targets based on detected changes

#### `smart-rebuild-dry-run`
- **Purpose**: Show what would be rebuilt
- **Calls**: None (analysis only)

### CI/CD Aliases

#### `openapi-build`
- **Purpose**: CI/CD: Generate and lint OpenAPI
- **Calls**:
  - `generate-openapi-spec-from-dd`
  - `lint`

#### `postman-publish`
- **Purpose**: CI/CD: Publish based on .postman-target
- **Calls**: Reads target file, then appropriate publish target

### Documentation

#### `docs`
- **Purpose**: Generate API documentation
- **Calls**: None (generates HTML)

#### `docs-serve`
- **Purpose**: Serve documentation locally
- **Calls**: None (starts web server)

### Utility Targets

#### `install`
- **Purpose**: Install dependencies
- **Calls**: None (runs brew and npm)

#### `venv`
- **Purpose**: Create Python virtual environment
- **Calls**: None (creates venv)

#### `fix-yaml`
- **Purpose**: Fix PyYAML issues
- **Calls**: None (reinstalls package)

## Target Dependency Tree

```
postman-instance-build-and-test
├── postman-login
├── postman-import-openapi-spec
│   ├── postman-import-openapi-as-api
│   └── postman-spec-create-standalone
├── postman-create-linked-collection
│   ├── postman-api-linked-collection-generate
│   ├── postman-linked-collection-flatten
│   ├── postman-linked-collection-upload
│   └── postman-linked-collection-link
├── postman-create-test-collection
│   ├── postman-test-collection-generate
│   ├── postman-test-collection-add-examples
│   ├── postman-test-collection-merge-overrides
│   ├── postman-test-collection-add-tests
│   ├── postman-test-collection-diff-tests
│   ├── postman-test-collection-auto-fix
│   ├── postman-test-collection-fix-v2
│   ├── postman-test-collection-validate
│   ├── verify-urls
│   ├── fix-urls
│   └── postman-test-collection-flatten-rename
├── postman-create-mock-and-env
│   ├── postman-mock-create
│   ├── postman-env-create
│   ├── postman-env-upload
│   └── update-mock-env
└── run-postman-and-prism-tests
    ├── prism-start
    ├── prism-mock-test
    └── postman-mock

rebuild-all-with-delete
├── postman-cleanup-all
│   ├── postman-env-delete
│   ├── postman-collection-delete
│   ├── postman-mock-delete
│   ├── postman-spec-clean-all
│   ├── postman-api-clean
│   └── postman-api-clean-trash
└── rebuild-all-no-delete
    ├── postman-login
    ├── openapi-build
    │   ├── generate-openapi-spec-from-dd
    │   │   ├── generate-openapi-spec-from-ebnf-dd
    │   │   ├── openapi-assemble-final
    │   │   └── lint
    │   └── lint
    ├── postman-collection-build
    │   ├── postman-api-linked-collection-generate
    │   └── postman-linked-collection-flatten
    ├── postman-collection-build-test-with-jwt
    ├── postman-upload-test-collection
    ├── postman-create-mock-and-env
    └── run-postman-and-prism-tests
```

## Key Observations

1. **Modular Design**: Targets are highly modular with clear separation of concerns
2. **Pipeline Approach**: Clear data flow from EBNF → OpenAPI → Postman → Testing
3. **Smart Rebuild**: Sophisticated change detection to minimize rebuild time
4. **CI/CD Ready**: Dedicated alias targets for GitHub Actions integration
5. **Multi-Workspace Support**: Can publish to personal or corporate workspaces
6. **Comprehensive Cleanup**: Thorough cleanup targets to maintain workspace hygiene
7. **Dual Mock Support**: Both local (Prism) and cloud (Postman) mock servers

## Most Common User Commands

1. `make help` - See available commands
2. `make postman-instance-build-and-test` - Run full pipeline
3. `make smart-rebuild` - Intelligent incremental build
4. `make rebuild-all-with-delete` - Clean full rebuild
5. `make postman-cleanup-all` - Clean up Postman workspace

## Notes

- All targets are .PHONY (no file outputs)
- Heavy use of $(MAKE) for recursive invocation
- Environment variables control workspace selection
- File-based tracking for UIDs and state
- Comprehensive error handling with fallbacks

## Cleanup Changes (September 2025)

The following targets were removed during the Makefile cleanup:
- `postman-collection-build-test-with-jwt` - JWT functionality moved to security repo
- `postman-upload-test-collection` - Redundant with other upload targets
- Various auth-specific targets that were causing bloat

The cleanup maintained all core functionality while removing redundant and auth-specific targets that belong in the separate security repository.
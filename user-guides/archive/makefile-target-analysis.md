# Makefile Target Analysis Report

## Overview
This report provides a comprehensive analysis of all targets in the C2M API V2 Makefile, including their purposes, dependencies, and hierarchical relationships.

## Target Summary
- **Total Targets**: 110
- **All targets are .PHONY** (no file targets)
- **Documented Targets**: 21 (with ## comments for help system)

## Target Hierarchy and Dependencies

### 1. Core Pipeline Targets

#### **ebnf-dd-to-openapi-spec** 
- **Purpose**: Convert EBNF data dictionary to OpenAPI specification
- **Dependencies**: venv
- **Calls**: 
  - install
  - generate-openapi-spec-from-ebnf-dd
  - openapi-merge-overlays
  - open-api-spec-lint
- **Phony**: Yes

#### **generate-and-validate-openapi-spec**
- **Purpose**: Generate and validate OpenAPI specification
- **Calls**:
  - generate-openapi-spec-from-ebnf-dd
  - open-api-spec-lint
  - open-api-spec-diff
  - clean-openapi-spec-diff
- **Phony**: Yes

### 2. Postman Collection Targets

#### **postman-create-linked-collection**
- **Purpose**: Create a linked Postman collection
- **Calls**:
  - postman-api-linked-collection-generate
  - postman-linked-collection-flatten
  - postman-linked-collection-upload
  - postman-linked-collection-link
- **Phony**: Yes

#### **postman-create-test-collection**
- **Purpose**: Create a test collection with examples and tests
- **Calls**:
  - postman-test-collection-generate
  - postman-test-collection-add-examples
  - postman-test-collection-merge-overrides
  - postman-test-collection-add-tests
  - postman-test-collection-diff-tests
  - postman-test-collection-auto-fix
  - postman-test-collection-fix-v2
  - postman-test-collection-validate (2x)
  - verify-urls
  - fix-urls
  - postman-test-collection-flatten-rename
  - postman-test-collection-upload
- **Phony**: Yes

#### **postman-create-mock-and-env**
- **Purpose**: Create Postman mock server and environment
- **Calls**:
  - postman-mock-create
  - postman-env-create
  - postman-env-upload
  - update-mock-env
- **Phony**: Yes

### 3. Build and Rebuild Targets

#### **postman-instance-build-and-test**
- **Purpose**: Complete Postman instance build and test
- **Calls**:
  - postman-login
  - postman-import-openapi-spec
  - postman-spec-create-standalone
  - postman-create-linked-collection
  - postman-create-test-collection
  - postman-create-mock-and-env
  - prism-start
  - postman-mock
  - postman-docs-build-and-serve-up
- **Phony**: Yes

#### **rebuild-all-with-delete**
- **Purpose**: Full rebuild with cleanup
- **Calls**:
  - postman-cleanup-all
  - rebuild-all-no-delete
- **Phony**: Yes

#### **rebuild-all-no-delete**
- **Purpose**: Full rebuild without cleanup
- **Calls**:
  - install
  - generate-and-validate-openapi-spec
  - rebuild-postman-instance-no-delete
- **Phony**: Yes

### 4. Smart Rebuild System

#### **smart-rebuild**
- **Purpose**: Intelligent rebuild based on file changes
- **Calls**:
  - smart-rebuild-openapi (conditional)
  - smart-check-openapi (conditional)
- **Phony**: Yes

#### **smart-rebuild-openapi**
- **Purpose**: Regenerate OpenAPI spec when data dictionary changes
- **Calls**:
  - ebnf-dd-to-openapi-spec
  - smart-check-openapi
- **Phony**: Yes

#### **smart-check-openapi**
- **Purpose**: Check if OpenAPI spec changed and cascade rebuilds
- **Calls** (conditional):
  - smart-rebuild-postman
  - smart-rebuild-sdk
  - smart-rebuild-docs
- **Phony**: Yes

### 5. Testing Targets

#### **run-postman-and-prism-tests**
- **Purpose**: Run both Postman and Prism tests
- **Calls**:
  - prism-start
  - prism-mock-test
  - postman-mock
- **Phony**: Yes

#### **prism-test-endpoint** ✓
- **Purpose**: Test specific endpoint with Prism mock server
- **Phony**: Yes

#### **prism-test-list** ✓
- **Purpose**: List available test bodies for endpoint
- **Phony**: Yes

#### **prism-test-select** ✓
- **Purpose**: Test endpoint with specific test body index
- **Phony**: Yes

### 6. Cleanup Targets

#### **postman-cleanup-all**
- **Purpose**: Complete cleanup of all Postman resources
- **Calls**:
  - postman-delete-mock-servers
  - postman-delete-collections
  - postman-delete-apis
  - postman-delete-environments
  - postman-api-clean-trash
  - postman-delete-specs
- **Phony**: Yes

#### **cleanup-all** ✓
- **Purpose**: Clean all temporary and obsolete files
- **Dependencies**: cleanup-scripts cleanup-openapi cleanup-docs
- **Phony**: Yes

### 7. Documentation Targets

#### **postman-docs-build-and-serve-up**
- **Purpose**: Build and serve API documentation
- **Calls**:
  - docs-build
  - docs-serve
- **Phony**: Yes

#### **deploy-docs** ✓
- **Purpose**: Deploy API documentation
- **Dependencies**: docs-build
- **Phony**: Yes

### 8. Publishing Targets

#### **postman-publish** ✓
- **Purpose**: Push API + collection to current workspace
- **Calls** (conditional based on POSTMAN_TARGET):
  - postman-publish-both
  - postman-publish-team
  - postman-publish-personal
  - (default) postman-import-openapi-as-api, postman-linked-collection-upload, postman-linked-collection-link
- **Phony**: Yes

#### **postman-publish-personal** ✓
- **Purpose**: Push complete suite to personal workspace
- **Calls** (all with workspace/key overrides):
  - workspace-info
  - postman-cleanup-all
  - postman-import-openapi-as-api
  - postman-spec-create-standalone
  - postman-linked-collection-upload
  - postman-linked-collection-link
  - postman-create-test-collection
  - postman-create-mock-and-env
  - postman-import-openapi-spec
- **Phony**: Yes

#### **postman-publish-team** ✓
- **Purpose**: Push complete suite to team workspace
- **Calls**: Same as postman-publish-personal but with team workspace
- **Phony**: Yes

#### **postman-publish-both** ✓
- **Purpose**: Push API + collection to BOTH workspaces
- **Calls**:
  - postman-publish-personal
  - postman-publish-team
- **Phony**: Yes

### 9. CI/CD Alias Targets

#### **openapi-build** ✓
- **Purpose**: Build OpenAPI from EBNF + overlays + lint [CI alias]
- **Dependencies**: generate-openapi-spec-from-ebnf-dd
- **Calls**: open-api-spec-lint
- **Phony**: Yes

#### **postman-collection-build** ✓
- **Purpose**: Generate and flatten the primary collection [CI alias]
- **Calls**:
  - postman-api-linked-collection-generate
  - postman-linked-collection-flatten
- **Phony**: Yes

#### **docs** ✓
- **Purpose**: Build API documentation [CI alias]
- **Dependencies**: docs-build
- **Phony**: Yes

#### **lint** ✓
- **Purpose**: Lint OpenAPI spec [CI alias]
- **Dependencies**: open-api-spec-lint
- **Phony**: Yes

#### **diff** ✓
- **Purpose**: Diff OpenAPI spec vs origin/main [CI alias]
- **Dependencies**: open-api-spec-diff
- **Phony**: Yes

### 10. Utility Targets

#### **help** ✓
- **Purpose**: Show help
- **Phony**: Yes

#### **workspace-info** ✓
- **Purpose**: Show current Postman workspace configuration
- **Phony**: Yes

#### **git-pull-rebase** ✓
- **Purpose**: Pull latest changes with rebase
- **Phony**: Yes

#### **git-save** ✓
- **Purpose**: Quick git save (requires MSG="commit message")
- **Phony**: Yes

#### **generate-sdk** ✓
- **Purpose**: Generate SDK from OpenAPI specification
- **Phony**: Yes

## Grouped by Function

### OpenAPI Generation
- ebnf-dd-to-openapi-spec
- generate-openapi-spec-from-ebnf-dd
- openapi-merge-overlays
- open-api-spec-lint
- open-api-spec-diff
- generate-and-validate-openapi-spec
- openapi-build (CI alias)
- lint (CI alias)
- diff (CI alias)

### Postman Collection Management
- postman-create-linked-collection
- postman-create-linked-collection-legacy
- postman-api-linked-collection-generate
- postman-linked-collection-flatten
- postman-linked-collection-upload
- postman-linked-collection-link
- postman-collection-build (CI alias)

### Postman Test Collections
- postman-create-test-collection
- postman-create-test-collection-legacy
- postman-test-collection-generate
- postman-test-collection-generate-from-flat
- postman-test-collection-add-examples
- postman-test-collection-merge-overrides
- postman-test-collection-add-tests
- postman-test-collection-diff-tests
- postman-test-collection-diff-tests-vscode
- postman-test-collection-auto-fix
- postman-test-collection-diff-auto-fix
- postman-test-collection-diff-auto-fix-vscode
- postman-test-collection-fix-v2
- postman-test-collection-fix-examples
- postman-test-collection-validate
- postman-test-collection-flatten
- postman-test-collection-flatten-rename
- postman-test-collection-upload

### Postman API Management
- postman-import-openapi-spec
- postman-import-openapi-flat-native
- postman-import-openapi-as-api
- postman-import-openapi-then-flatten
- postman-spec-create
- postman-spec-create-standalone
- postman-spec-list
- postman-api-full-publish
- postman-api-list-specs
- postman-apis

### Postman Mock & Environment
- postman-create-mock-and-env
- postman-mock-create
- postman-env-create
- postman-env-upload
- update-mock-env
- verify-mock
- postman-mock
- postman-link-env-to-mock-server

### Testing
- run-postman-and-prism-tests
- prism-start
- prism-stop
- prism-status
- prism-mock-test
- prism-test-endpoint
- prism-test-list
- prism-test-select
- postman-mock

### Cleanup
- postman-cleanup-all
- postman-delete-mock-servers
- postman-delete-collections
- postman-delete-apis
- postman-delete-environments
- postman-delete-specs
- postman-delete-specs-by-name
- postman-api-clean-trash
- postman-api-delete-old-specs
- postman-collections-clean
- cleanup-scripts
- cleanup-openapi
- cleanup-docs
- cleanup-all
- clean-openapi-spec-diff

### Build & Rebuild
- postman-instance-build-and-test
- rebuild-postman-instance-no-delete
- rebuild-postman-instance-with-delete
- rebuild-all-no-delete
- rebuild-all-with-delete
- rebuild-all-with-delete-flat

### Smart Rebuild System
- smart-rebuild
- smart-rebuild-openapi
- smart-check-openapi
- smart-rebuild-postman
- smart-rebuild-sdk
- smart-rebuild-docs
- smart-rebuild-status
- smart-rebuild-clean
- smart-rebuild-dry-run

### Documentation
- docs-build
- docs-serve
- docs-serve-bg
- docs-stop
- deploy-docs
- postman-docs-build-and-serve-up
- docs (CI alias)
- fix-template-banner

### Publishing
- postman-publish
- postman-publish-personal
- postman-publish-team
- postman-publish-both

### Authentication & JWT
- postman-login
- jwt-test
- postman-add-jwt-tests

### Workspace Management
- workspace-info
- use-team-workspace
- use-personal-workspace

### Utility & Debug
- install
- venv
- help
- print-openapi-vars
- print-vars
- verify-urls
- fix-urls
- fix-yaml
- postman-import-help
- postman-api-debug-A
- postman-api-debug-B
- postman-workspace-debug
- check-mock
- git-pull-rebase
- git-save
- generate-sdk
- empty-test
- test-update-mock-env-call

## Key Observations

1. **All targets are .PHONY** - No file-based targets exist in this Makefile
2. **Heavy use of target composition** - Complex operations are built from simpler targets
3. **Workspace flexibility** - Supports both personal and team workspaces with override mechanisms
4. **Smart rebuild system** - Intelligent change detection and cascading rebuilds
5. **CI/CD support** - Alias targets specifically for GitHub Actions
6. **Complete cleanup capabilities** - Thorough removal of all Postman resources
7. **Multiple test frameworks** - Both Prism (local) and Postman (cloud) testing

## Most Important Top-Level Targets

1. **rebuild-all-with-delete** - Complete rebuild from scratch
2. **smart-rebuild** - Intelligent incremental rebuild
3. **postman-publish** - Publish to Postman workspace
4. **postman-cleanup-all** - Remove all Postman resources
5. **help** - Show available commands

✓ = Documented target (appears in help)
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the C2M API V2 project that implements a unique pipeline: EBNF Data Dictionary → OpenAPI Specification → Postman Collection → Mock Server → API Documentation.

## Restoration Status (2025-09-08)

✅ **RESTORATION COMPLETE** - The c2m-api-repo has been successfully restored to its pre-auth state:
- JWT authentication code moved to separate security repository
- Makefile cleaned up (removed redundant targets, simplified publish workflow)
- Documentation reorganized into user-guides directory with symlinks
- OpenAPI spec creation in Postman fixed (was double-encoding issue)
- All 24 tests passing (including auth endpoint with 403 status allowed)
- Successfully merged to main branch

## Key Commands

### Initial Setup
```bash
make install                    # Install all dependencies (npm, Python)
python3 -m venv scripts/python_env/e2o.venv  # Create Python venv if needed
```

### Primary Development Workflow
```bash
make postman-collection-build-and-test  # Run complete pipeline (most common command)
```

### Individual Pipeline Steps
```bash
make generate-openapi-spec-from-dd      # Convert EBNF to OpenAPI
make lint                               # Validate OpenAPI spec
make prism-start                        # Start local mock server (port 4010)
make postman-mock                       # Run tests against mock
make docs-serve                         # Serve docs locally (port 8080)
```

### Cleanup
```bash
make postman-cleanup-all                # Delete all Postman resources
make prism-stop                         # Stop local mock server
```

### CI/CD Commands (GitHub Actions)
```bash
# These aliases are used by GitHub Actions workflow
make openapi-build                      # Build OpenAPI from EBNF + lint
make postman-collection-build           # Generate and flatten collection
make docs                               # Build API documentation
make lint                               # Lint OpenAPI spec
make diff                               # Diff spec vs origin/main
make postman-publish                    # Push to Postman (reads .postman-target)
make postman-publish-personal           # Explicitly publish to personal workspace
make postman-publish-corporate          # Explicitly publish to corporate workspace

# GitHub Actions specific behavior
# The workflow reads .postman-target file to determine which workspace to use
# Creates this file with: echo "personal" > .postman-target
```

### Smart Rebuild System (NEW!)
```bash
# Intelligent rebuild that only regenerates what has changed
make smart-rebuild                      # Check for changes and rebuild only what's needed
make smart-rebuild-dry-run             # Show what would be rebuilt without doing it
make smart-rebuild-status              # Show current build state and hashes
make smart-rebuild-clean               # Clear hash cache (forces full rebuild)
```

The smart rebuild system cascades through the pipeline:
1. Checks if data dictionary (EBNF) changed → regenerates OpenAPI if needed
2. Checks if OpenAPI spec changed → rebuilds Postman collections if needed
3. Checks if collections changed → regenerates SDK if needed
4. All changes trigger documentation rebuild
5. Shows diffs of what changed at each step

### Advanced Testing
```bash
# Test specific endpoints with Prism mock server
make prism-test-endpoint PRISM_TEST_ENDPOINT=/jobs/single-doc
make prism-test-list PRISM_TEST_ENDPOINT=/jobs/single-doc
make prism-test-select PRISM_TEST_ENDPOINT=/jobs/single-doc PRISM_TEST_INDEX=2
```

### Utility Commands
```bash
# SDK Generation
make generate-sdk                       # Generate SDK from OpenAPI spec

# Documentation Deployment
make deploy-docs                        # Deploy docs to hosting service

# Maintenance
make cleanup-scripts                    # Clean obsolete scripts
make cleanup-openapi                    # Clean old OpenAPI files
make cleanup-docs                       # Clean temp documentation files
make cleanup-all                        # Clean all directories

# Git Workflow
make git-pull-rebase                    # Pull with rebase
make git-save MSG="your commit message" # Quick add, commit, push
```

## Architecture

The project follows a data-driven approach where the EBNF data dictionary is the single source of truth:

1. **Data Dictionary** (`data_dictionary/`) - EBNF definitions converted to OpenAPI
2. **OpenAPI Spec** (`openapi/`) - Generated YAML specifications
3. **Postman Collections** (`postman/generated/`) - Test collections with examples
4. **Mock Servers** - Both local (Prism) and cloud (Postman) mocks
5. **Documentation** (`docs/`) - Auto-generated API documentation

## Key Directories

- **`scripts/`**: Conversion and utility scripts (Python, Node.js, Shell)
  - `active/` - Primary pipeline scripts
    - `ebnf_to_openapi_class_based.py` - Core EBNF to OpenAPI converter
    - `add_tests.js` - Adds automated tests to collections
    - `fix_collection_urls_v2.py` - Fixes URLs in collections
  - `utilities/` - Support and maintenance scripts
  - `archived/` - Legacy and deprecated scripts

- **`postman/`**: Postman-related files
  - `custom/` - User customizations and overrides
  - `generated/` - Auto-generated collections
  - Various UID/URL tracking files

- **`openapi/`**: OpenAPI specifications
  - Final spec: `c2mapiv2-openapi-spec-final.yaml`

## Environment Configuration

Create a `.env` file with:
```
POSTMAN_SERRAO_API_KEY=your-api-key
POSTMAN_C2M_API_KEY=alternate-api-key
```

## Common Development Tasks

### Running Tests
```bash
# Test against local mock
make prism-mock-test

# Test against Postman cloud mock  
make postman-mock

# Run specific endpoint test
PRISM_TEST_ENDPOINT=/your/endpoint make prism-test-select
```

### Debugging
```bash
make print-openapi-vars         # Debug OpenAPI variables
make verify-urls               # Check collection URLs
make postman-workspace-debug   # Debug Postman workspace
```

### Working with Mock Servers
```bash
# Local development (Prism)
make prism-start              # Start on port 4010
make prism-status            # Check if running
make prism-stop              # Stop server

# Postman cloud mock
make postman-mock-create     # Create new mock
make update-mock-env         # Update mock environment
```

## Important Notes

1. **Makefile $$ Escaping**: Shell variables in Makefile require `$$` not `$`
2. **Python Environment**: Uses venv at `scripts/python_env/e2o.venv`
3. **Workspace ID**: Default is Serrao workspace (`d8a1f479-a2aa-4471-869e-b12feea0a98c`)
4. **Mock URLs**: Automatically saved to tracking files in `postman/`
5. **Collection Fixes**: URLs are automatically fixed to use `{{baseUrl}}` placeholder
6. **GitHub Actions**: Uses portable jq syntax (no line continuations) for compatibility
7. **API Deletion**: Fixed to properly delete all APIs in workspace during cleanup

## Troubleshooting

- **PyYAML Issues**: Run `make fix-yaml`
- **Port Conflicts**: Prism uses 4010, docs use 8080
- **API Key Issues**: Check `.env` file and `POSTMAN_API_KEY` selection in Makefile
- **Collection Validation**: Run `make postman-test-collection-validate`
- **GitHub Actions jq errors**: Fixed - uses portable syntax without line continuations
- **Wrong workspace published**: Check `.postman-target` file content
- **Only 1 API deleted**: Fixed - now properly deletes all APIs during cleanup

## Pipeline Flow

1. Edit EBNF data dictionary
2. Run `make postman-collection-build-and-test`
3. System automatically:
   - Converts EBNF to OpenAPI
   - Generates Postman collection
   - Adds test data and tests
   - Creates mock server
   - Runs tests
   - Generates documentation

## GitHub Actions CI/CD

The project includes automated CI/CD pipelines:

### Main Workflow (`api-ci-cd.yml`)
- **Triggers**: Push to main, PRs, manual dispatch
- **Actions**: 
  - Builds OpenAPI spec from EBNF
  - Generates Postman collections
  - Builds documentation
  - Auto-commits generated files (main branch only)
  - Cleans up existing Postman resources before publishing
  - Publishes to Postman workspace based on `.postman-target` file
  - Deploys docs to GitHub Pages

### PR Drift Check (`pr-drift-check.yml`)
- **Purpose**: Ensures generated files are committed
- **Fails PR if**: Generated artifacts differ from committed versions
- **Auto-comments**: Instructions to regenerate files

### Required Secrets
Configure in GitHub Settings → Secrets:
- `POSTMAN_API_KEY`: Your Postman API key
- `POSTMAN_WORKSPACE_ID`: Target workspace UUID

### Workspace Publishing
The workflow determines which workspace to publish to:
1. Reads `.postman-target` file (contains "personal" or "corporate")
2. Runs corresponding make target: `make postman-publish-{target}`
3. Default is "personal" if file doesn't exist

To set target: `echo "personal" > .postman-target`

## Script Integration Status

### Recently Integrated Scripts
✅ `prism_test.sh` - Advanced endpoint testing with Prism (targets: prism-test-*)
✅ `generate-sdk.sh` - SDK generation placeholder (target: generate-sdk)
✅ `deploy-docs.sh` - Documentation deployment placeholder (target: deploy-docs)
✅ `cleanup-*.sh` - Directory cleanup utilities (targets: cleanup-*)
✅ `git-pull-rebase.sh` - Git workflow helper (target: git-pull-rebase)
✅ `git-push.sh` - Quick commit helper (target: git-save)

### Remaining Integration Opportunities
- `generate_openapi_from_swagger.py` - Swagger to OpenAPI conversion
- `merge_yaml_files.py` - Merge multiple YAML specs
- `api_client_generator.py` - Generate Python client from OpenAPI

## Learning Memories

- `learn`: Placeholder for learning memories related to the project
- Added a placeholder for `memorize`
- First memory added: Learning how to effectively manage and update project documentation
- Discovered the importance of dynamic pipeline generation based on source document changes
- Fixed API deletion issue where only 1 of N APIs was being deleted
- Implemented workspace-based publishing system using `.postman-target` file
- Created comprehensive build guide for non-technical users
- Fixed OpenAPI spec double-encoding bug (was using `jq -Rs .` instead of `cat`)
- Simplified publish targets to use orchestrator pattern (eliminated ~1000 lines)
- Restored repo from broken state with auth integration mixed in
- **2025-09-08**: Fixed CI/CD workflow issues:
  - Postman CLI needs explicit installation in GitHub Actions
  - Added CI-specific targets that skip local testing (prism-start, docs-serve)
  - npm version of openapi-diff behaves differently than brew version
- **2025-09-08**: Consolidated documentation from security repo:
  - Created POSTMAN_COMPLETE_GUIDE.md merging all Postman docs
  - Created AUTHENTICATION_GUIDE.md consolidating auth documentation
  - Created CUSTOMER_ONBOARDING_GUIDE.md for new customers
  - Established migration plan for remaining docs

## Project Memory & Key Patterns

### Critical Files to Remember
- **PROJECT_MEMORY.md** - Comprehensive project knowledge base
- **Makefile** - Main orchestrator (now clean and simplified)
- **data_dictionary/c2mapiv2-dd.ebnf** - Source of truth for API
- **openapi/c2mapiv2-openapi-spec-final.yaml** - Generated API spec
- **postman/scripts/jwt-pre-request.js** - JWT auth integration point

### Key Commands to Remember
```bash
# Most common development command
make postman-instance-build-and-test

# When things go wrong
make postman-cleanup-all
make prism-mock-test

# Check what's in Postman
make postman-workspace-debug
```

### Common Gotchas
1. **Double encoding bug**: Always use `cat` not `jq -Rs .` for spec content
2. **Workspace switching**: Use orchestrator pattern, not duplicate targets
3. **Auth integration**: Keep in security repo, minimal hooks only
4. **Test failures**: Check allowed status codes (now includes 403)
5. **CI/CD issues**: 
   - Postman CLI must be installed explicitly in GitHub Actions
   - Use CI-specific targets that skip local servers
   - openapi-diff npm version hangs (use npx, temporarily disabled)

### Repository Relationships
- **Main repo**: c2m-api-repo (core API functionality)
- **Security repo**: c2m-api-v2-security (JWT auth implementation)
- **Integration**: Minimal hooks, not full integration
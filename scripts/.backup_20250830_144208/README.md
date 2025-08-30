# Scripts Directory

This directory contains build automation, utility scripts, and tools for the C2M API project.

## Directory Structure

```
scripts/
├── python_env/                 # Python virtual environment configuration
│   ├── requirements.txt       # Python dependencies for scripts
│   └── e2o.venv/             # Virtual environment (git-ignored)
├── jq/                        # JSON processing scripts
│   ├── add_info.jq           # Add info section to OpenAPI
│   ├── add_tags.jq           # Add tags to operations
│   ├── auto_fix_collection.jq # Fix Postman collection URLs
│   ├── env_template.jq       # Create environment template
│   ├── extract_url.jq        # Extract URLs from collection
│   ├── filter_api_url.jq     # Filter API URLs
│   ├── fix_urls.jq           # Fix collection URLs
│   ├── flatten_collection.jq  # Flatten nested collections
│   ├── rename_apis.jq        # Rename API definitions
│   ├── sanitize_collection.jq # Clean collection data
│   └── verify_urls.jq        # Verify URL formatting
├── makefile-scripts/          # Makefile support scripts
│   ├── check_and_create_makefile_files.sh
│   ├── fix-orchestrator-v2.sh
│   └── normalize.sh
├── test_data_generator_for_collections/  # Test data for collections
├── test_data_generator_for_openapi_specs/ # Test data for OpenAPI
├── ebnf_to_openapi_dynamic_v3.py  # EBNF to OpenAPI converter
├── generate-sdk.sh            # SDK generation script
├── deploy-docs.sh             # Documentation deployment
├── prism_test.sh              # Prism mock server testing
├── cleanup-scripts-directory.sh # Clean scripts directory
├── cleanup-openapi-directory.sh # Clean OpenAPI directory
├── cleanup-docs-directory.sh  # Clean docs directory
├── git-pull-rebase.sh         # Git pull with rebase
├── git-push.sh                # Quick git commit and push
├── fix-template-banner.sh     # Fix template banners
├── inject-banner-correctly.js # Add banners to spec
├── add_tests.js               # Add tests to Postman collection
├── fix_collection_urls_v2.py  # Fix collection URLs
├── flatten_collection.js      # Flatten Postman collection
├── generate_test_data.py      # Generate test data
├── update_paths_in_spec_wrapper.js # Update spec paths
├── validate_collection.js     # Validate Postman collection
└── various other utilities    # Additional helper scripts
```

## Key Scripts

### Core Converters

#### `ebnf_to_openapi_dynamic_v3.py`
Converts EBNF data dictionary to OpenAPI specification.
- **Usage**: `python ebnf_to_openapi_dynamic_v3.py -o output.yaml input.ebnf`
- **Called by**: `make generate-openapi-spec-from-ebnf-dd`

### SDK and Documentation

#### `generate-sdk.sh`
Generates client SDKs in multiple languages using OpenAPI Generator.
- **Usage**: `./generate-sdk.sh [language]` or interactive mode
- **Languages**: python, javascript, typescript, java, go, ruby, php
- **Called by**: `make generate-sdk`

#### `deploy-docs.sh`
Deploys documentation to various hosting services.
- **Targets**: GitHub Pages, AWS S3, Netlify, local preview
- **Usage**: `./deploy-docs.sh [target]`
- **Called by**: `make deploy-docs`

### Testing

#### `prism_test.sh`
Tests API endpoints using Prism mock server with Postman collection data.
- **Usage**: `./prism_test.sh <endpoint> [--list|--select N]`
- **Called by**: `make prism-test-endpoint`

### Postman Collection Processing

#### `add_tests.js`
Adds automated tests to Postman collections.
- **Usage**: `node add_tests.js <collection.json>`
- **Called by**: `make postman-collection-add-tests`

#### `fix_collection_urls_v2.py`
Fixes URLs in Postman collections to use {{baseUrl}} placeholders.
- **Usage**: `python fix_collection_urls_v2.py <collection.json>`
- **Called by**: `make postman-fix-urls`

#### `validate_collection.js`
Validates Postman collection structure.
- **Usage**: `node validate_collection.js <collection.json>`
- **Called by**: `make postman-test-collection-validate`

### Maintenance

#### `cleanup-*.sh`
Directory cleanup scripts that move obsolete files to `possible-trash/`.
- `cleanup-scripts-directory.sh` - Cleans this directory
- `cleanup-openapi-directory.sh` - Cleans OpenAPI files
- `cleanup-docs-directory.sh` - Cleans documentation files
- **Called by**: `make cleanup-scripts`, etc.

### Git Helpers

#### `git-pull-rebase.sh`
Performs git pull with rebase and autostash.
- **Usage**: `./git-pull-rebase.sh`
- **Called by**: `make git-pull-rebase`

#### `git-push.sh`
Quick add, commit, and push changes.
- **Usage**: `./git-push.sh "commit message"`
- **Called by**: `make git-save MSG="message"`

## JQ Scripts

The `jq/` subdirectory contains JSON processing scripts used throughout the build process:

- **URL Processing**: `fix_urls.jq`, `extract_url.jq`, `verify_urls.jq`
- **Collection Management**: `flatten_collection.jq`, `sanitize_collection.jq`
- **OpenAPI Enhancement**: `add_info.jq`, `add_tags.jq`
- **Environment Setup**: `env_template.jq`

## Python Environment

Scripts use a Python virtual environment located at `python_env/e2o.venv/`.

To activate:
```bash
source scripts/python_env/e2o.venv/bin/activate
```

Dependencies are in `python_env/requirements.txt`.

## Adding New Scripts

1. Place script in appropriate location:
   - Python converters: Root of scripts/
   - JQ processors: scripts/jq/
   - Makefile helpers: scripts/makefile-scripts/

2. Make executable: `chmod +x script.sh`

3. Add to Makefile if needed

4. Document purpose and usage in this README

## Dependencies

- Python 3.9+ (for Python scripts)
- Node.js 16+ (for JavaScript scripts)
- jq 1.6+ (for JSON processing)
- bash 4+ (for shell scripts)
- curl (for API calls)

## Notes

- All scripts should be idempotent
- Use absolute paths or `$PROJECT_ROOT`
- Follow existing naming conventions
- Add error handling and validation
- Test thoroughly before committing
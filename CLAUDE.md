# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the C2M API V2 project that implements a unique pipeline: EBNF Data Dictionary → OpenAPI Specification → Postman Collection → Mock Server → API Documentation.

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

## Architecture

The project follows a data-driven approach where the EBNF data dictionary is the single source of truth:

1. **Data Dictionary** (`data_dictionary/`) - EBNF definitions converted to OpenAPI
2. **OpenAPI Spec** (`openapi/`) - Generated YAML specifications
3. **Postman Collections** (`postman/generated/`) - Test collections with examples
4. **Mock Servers** - Both local (Prism) and cloud (Postman) mocks
5. **Documentation** (`docs/`) - Auto-generated API documentation

## Key Directories

- **`scripts/`**: Conversion and utility scripts (Python, Node.js, Shell)
  - `ebnf_to_openapi_class_based.py` - Core EBNF to OpenAPI converter
  - `add_tests.js` - Adds automated tests to collections
  - `fix_collection_urls_v2.py` - Fixes URLs in collections

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

## Troubleshooting

- **PyYAML Issues**: Run `make fix-yaml`
- **Port Conflicts**: Prism uses 4010, docs use 8080
- **API Key Issues**: Check `.env` file and `POSTMAN_API_KEY` selection in Makefile
- **Collection Validation**: Run `make postman-test-collection-validate`

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

## Script Integration Opportunities

High-value scripts not yet integrated into Makefile:
- `generate_openapi_from_swagger.py` - Swagger to OpenAPI conversion
- `merge_yaml_files.py` - Merge multiple YAML specs
- `api_client_generator.py` - Generate Python client from OpenAPI
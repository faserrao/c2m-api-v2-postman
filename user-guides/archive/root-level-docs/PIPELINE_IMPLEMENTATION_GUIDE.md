# C2M API V2 Pipeline Implementation Guide

## Table of Contents
1. [Implementation Plan](#implementation-plan)
2. [Pipeline Overview](#pipeline-overview)
3. [Local Development Pipeline](#local-development-pipeline)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [OneOf Schema Implementation](#oneof-schema-implementation)
6. [Troubleshooting](#troubleshooting)

## Implementation Plan

### Problem Statement
The openapi-to-postmanv2 converter simplifies anonymous oneOf schemas to just the first type, causing Postman collections to show incorrect type placeholders (e.g., `<integer>` instead of `<oneOf>`) for union type fields like `documentSourceIdentifier`.

### Solution Architecture
1. **Post-process OpenAPI specs** to convert anonymous oneOf schemas to named schemas
2. **Fix Postman collection placeholders** to replace type-specific placeholders with `<oneOf>`
3. **Enhance test data generator** to recognize and handle `<oneOf>` placeholders
4. **Integrate all fixes into the pipeline** to ensure they run automatically

### Implementation Steps
1. Create `fix_openapi_oneOf_schemas.py` to convert anonymous schemas
2. Create `fix_oneOf_placeholders.js` to fix collection placeholders
3. Modify `addRandomDataToRaw.js` to handle `<oneOf>` placeholders
4. Update Makefile to integrate all scripts in the correct order
5. Document the implementation in project files

## Pipeline Overview

### Architecture Flow
```
EBNF Data Dictionary
    ↓
OpenAPI Specification (with anonymous oneOf)
    ↓
OneOf Schema Fix (anonymous → named)
    ↓
OpenAPI Specification (with named oneOf)
    ↓
Auth Overlay Merge
    ↓
Postman Collection Generation
    ↓
OneOf Placeholder Fix (<integer> → <oneOf>)
    ↓
Collection Flattening
    ↓
Test Data Addition (with oneOf rotation)
    ↓
Mock Server & Testing
    ↓
API Documentation
```

### Key Components

#### 1. EBNF to OpenAPI Converter (`ebnf_to_openapi_dynamic_v3.py`)
- Parses EBNF data dictionary using Lark parser
- Generates OpenAPI 3.0.3 specification dynamically
- Creates anonymous oneOf schemas for alternations
- Modified to support named schema generation (enhanced but not required)

#### 2. OneOf Schema Fixer (`fix_openapi_oneOf_schemas.py`)
- Post-processes OpenAPI specifications
- Identifies anonymous oneOf schemas
- Creates named schemas based on properties:
  - `DocumentSourceWithUpload`: uploadRequestId + documentName
  - `DocumentSourceWithUploadAndZip`: uploadRequestId + zipId + documentName  
  - `DocumentSourceFromZip`: zipId + documentName
- Updates oneOf references to use named schemas

#### 3. OneOf Placeholder Fixer (`fix_oneOf_placeholders.js`)
- Post-processes Postman collections
- Replaces type-specific placeholders with `<oneOf>` for:
  - documentSourceIdentifier
  - recipientAddressSource
  - paymentDetails
- Maintains collection structure while fixing placeholders

#### 4. Test Data Generator (`addRandomDataToRaw.js`)
- Enhanced to recognize `<oneOf>` as a placeholder
- Implements rotation logic for oneOf variants
- Tracks last used variant and increments on each run
- Generates appropriate example data for each variant

## Local Development Pipeline

### Prerequisites
- Python 3.x with virtual environment
- Node.js and npm
- Postman CLI
- Make utility
- curl, jq, and basic Unix tools

### Environment Setup
```bash
# Create Python virtual environment
python3 -m venv scripts/python_env/e2o.venv

# Install dependencies
make install

# Create .env file with API keys
echo "POSTMAN_SERRAO_API_KEY=your-api-key" > .env
```

### Complete Build Process
```bash
# Clean existing resources
make postman-cleanup-all

# Run complete pipeline
make postman-instance-build-and-test
```

### Step-by-Step Pipeline Execution

#### 1. Generate OpenAPI from EBNF
```bash
make generate-openapi-spec-from-ebnf-dd
```
This runs:
- `ebnf_to_openapi_dynamic_v3.py` to convert EBNF to OpenAPI
- `fix_openapi_oneOf_schemas.py` to fix anonymous oneOf schemas

#### 2. Merge Auth Overlay
```bash
make openapi-merge-overlays
```
Merges authentication endpoints from `openapi/overlays/auth.tokens.yaml`

#### 3. Generate Postman Collection
```bash
make postman-api-linked-collection-generate
```
This:
- Runs openapi-to-postmanv2 converter
- Adds collection metadata
- Runs `fix_oneOf_placeholders.js` to fix placeholders

#### 4. Flatten and Prepare Collections
```bash
make postman-linked-collection-flatten
make postman-test-collection-generate
```

#### 5. Add Test Data and Tests
```bash
make postman-test-collection-add-examples
make postman-test-collection-add-tests
```
The test data generator now properly handles `<oneOf>` placeholders

#### 6. Create Mock Server and Test
```bash
make postman-mock-create
make postman-env-create
make postman-mock
```

### Local Testing Commands
```bash
# Test against local Prism mock
make prism-start
make prism-mock-test

# Test specific endpoint
make prism-test-endpoint PRISM_TEST_ENDPOINT=/jobs/single-doc

# Run Postman tests
make postman-mock
```

## CI/CD Pipeline

### GitHub Actions Workflow (`api-ci-cd.yml`)

#### Triggers
- Push to main branch
- Pull requests
- Manual dispatch

#### Environment Variables
```yaml
env:
  POSTMAN_API_KEY: ${{ secrets.POSTMAN_API_KEY }}
  POSTMAN_WORKSPACE_ID: ${{ secrets.POSTMAN_WORKSPACE_ID }}
```

#### Pipeline Steps

1. **Checkout Code**
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

2. **Setup Environment**
```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'

- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.x'
```

3. **Install Dependencies**
```yaml
- name: Install dependencies
  run: |
    npm install -g @redocly/cli @apidevtools/swagger-cli
    npm install -g openapi-to-postmanv2
    sudo snap install postman-cli
```

4. **Build OpenAPI Spec**
```yaml
- name: Build OpenAPI spec from EBNF
  run: make openapi-build
```
This includes the oneOf schema fix automatically

5. **Generate Collections**
```yaml
- name: Generate Postman collections
  run: make postman-collection-build
```
This includes the oneOf placeholder fix

6. **Build Documentation**
```yaml
- name: Build documentation
  run: make docs
```

7. **Publish to Postman** (main branch only)
```yaml
- name: Publish to Postman
  if: github.ref == 'refs/heads/main'
  run: |
    make postman-cleanup-all
    make postman-publish
```

### CI-Specific Targets

The Makefile includes CI-specific aliases that skip local server operations:
- `make openapi-build` - Builds spec without starting local servers
- `make postman-collection-build` - Generates collections without testing
- `make docs` - Builds docs without serving

## OneOf Schema Implementation

### Problem Analysis

#### Original Issue
When openapi-to-postmanv2 encounters anonymous oneOf schemas like:
```yaml
documentSourceIdentifier:
  oneOf:
    - $ref: '#/components/schemas/documentId'
    - $ref: '#/components/schemas/externalUrl'
    - type: object
      properties:
        uploadRequestId:
          $ref: '#/components/schemas/uploadRequestId'
```

It simplifies to just the first type, resulting in `<integer>` placeholder.

#### Root Cause
The converter cannot properly handle anonymous inline schemas within oneOf constructs, defaulting to the first alternative.

### Solution Details

#### 1. OpenAPI Post-Processing
The `fix_openapi_oneOf_schemas.py` script:

```python
def fix_documentSourceIdentifier_oneOf(spec):
    """Fix anonymous oneOf schemas in documentSourceIdentifier"""
    # Find documentSourceIdentifier schema
    if 'documentSourceIdentifier' in schemas and 'oneOf' in schemas['documentSourceIdentifier']:
        oneOf_list = schemas['documentSourceIdentifier']['oneOf']
        
        for variant in oneOf_list:
            if 'type' in variant and variant['type'] == 'object':
                # Create named schema based on properties
                props = variant.get('properties', {})
                
                if 'uploadRequestId' in props and 'zipId' in props:
                    schema_name = 'DocumentSourceWithUploadAndZip'
                elif 'uploadRequestId' in props:
                    schema_name = 'DocumentSourceWithUpload'
                elif 'zipId' in props:
                    schema_name = 'DocumentSourceFromZip'
                
                # Add named schema and replace with reference
                schemas[schema_name] = variant
                new_oneOf.append({'$ref': f'#/components/schemas/{schema_name}'})
```

#### 2. Collection Placeholder Fix
The `fix_oneOf_placeholders.js` script:

```javascript
const oneOfFields = {
    'documentSourceIdentifier': true,
    'recipientAddressSource': true,
    'paymentDetails': true,
};

function replaceOneOfPlaceholders(obj) {
    if (typeof obj === 'string') {
        // Check if this is a oneOf field placeholder
        const match = obj.match(/"(\w+)":\s*"<(\w+)>"/);
        if (match) {
            const [fullMatch, fieldName, type] = match;
            if (oneOfFields[fieldName] && type !== 'oneOf') {
                return obj.replace(fullMatch, `"${fieldName}": "<oneOf>"`);
            }
        }
    }
}
```

#### 3. Test Data Generation
Enhanced `addRandomDataToRaw.js`:

```javascript
// Track oneOf variants
const oneOfVariants = {
    documentSourceIdentifier: [
        () => faker.number.int({ min: 1, max: 999999 }), // documentId
        () => faker.internet.url(), // externalUrl
        () => ({ // uploadRequestId + documentName
            uploadRequestId: faker.number.int({ min: 1, max: 999999 }),
            documentName: faker.system.fileName()
        }),
        // ... more variants
    ]
};

// Rotate through variants
let variantIndex = (lastIndex + 1) % variants.length;
return variants[variantIndex]();
```

### Integration Points

#### Makefile Integration
```makefile
# After EBNF to OpenAPI conversion
generate-openapi-spec-from-ebnf-dd:
	$(VENV_PYTHON) $(EBNF_TO_OPENAPI_SCRIPT) -o $(C2MAPIV2_OPENAPI_SPEC_BASE) $(DD_EBNF_FILE)
	# Fix anonymous oneOf schemas
	$(VENV_PYTHON) $(SCRIPTS_DIR)/active/fix_openapi_oneOf_schemas.py \
		$(C2MAPIV2_OPENAPI_SPEC_BASE) $(C2MAPIV2_OPENAPI_SPEC_BASE)

# After collection generation
postman-api-linked-collection-generate:
	$(GENERATOR_OFFICIAL) -s $(C2MAPIV2_OPENAPI_SPEC_WITH_EXAMPLES) \
		-o $(POSTMAN_COLLECTION_RAW) -p
	# Fix oneOf placeholders
	@node scripts/active/fix_oneOf_placeholders.js \
		$(POSTMAN_COLLECTION_RAW) $(POSTMAN_COLLECTION_RAW)
```

### Testing and Validation

#### Verify OpenAPI Fix
```bash
# Check for named schemas
grep -A5 "DocumentSourceWith" openapi/c2mapiv2-openapi-spec-base.yaml

# Should show:
# DocumentSourceWithUpload:
#   type: object
#   properties:
#     uploadRequestId:
#       $ref: '#/components/schemas/uploadRequestId'
```

#### Verify Collection Fix
```bash
# Check for oneOf placeholders
grep -o "documentSourceIdentifier.*<[^>]*>" postman/generated/*.json | uniq

# Should show:
# documentSourceIdentifier": "<oneOf>"
```

#### Verify Test Data Rotation
```bash
# Run tests multiple times
make postman-mock
make postman-mock
make postman-mock

# Check output for:
# documentSourceIdentifier: Next variant will be 1/5
# documentSourceIdentifier: Next variant will be 2/5
# etc.
```

## Troubleshooting

### Common Issues

#### 1. OneOf Placeholders Still Show Wrong Type
- Verify `fix_oneOf_placeholders.js` is running in pipeline
- Check that all oneOf fields are listed in the script
- Ensure script runs after collection generation

#### 2. Test Data Not Rotating
- Check `addRandomDataToRaw.js` includes field in oneOfVariants
- Verify variant index is being tracked and incremented
- Ensure test collection is being regenerated

#### 3. OpenAPI Schema Fix Not Applied
- Verify Python virtual environment is activated
- Check that fix script runs after EBNF conversion
- Ensure output file overwrites input file

#### 4. CI/CD Pipeline Failures
- Check Postman CLI is installed in GitHub Actions
- Verify environment variables are set
- Ensure workspace permissions are correct

### Debug Commands

```bash
# Check Python environment
make verify-python-env

# Debug OpenAPI generation
make print-openapi-vars

# Debug Postman workspace
make postman-workspace-debug

# Verify collection structure
make postman-test-collection-validate
```

### Recovery Procedures

#### Clean Rebuild
```bash
make postman-cleanup-all
make clean-openapi-build
make postman-instance-build-and-test
```

#### Reset Python Environment
```bash
rm -rf scripts/python_env/e2o.venv
python3 -m venv scripts/python_env/e2o.venv
make install
```

#### Force Regenerate Everything
```bash
make smart-rebuild-clean
make postman-cleanup-all
make postman-instance-build-and-test
```

## Appendix: File Modifications

### Files Created
1. `scripts/active/fix_openapi_oneOf_schemas.py`
2. `scripts/active/fix_oneOf_placeholders.js`

### Files Modified
1. `Makefile` - Added oneOf fix integration
2. `scripts/test_data_generator_for_collections/addRandomDataToRaw.js` - Added oneOf handling
3. `scripts/active/ebnf_to_openapi_dynamic_v3.py` - Enhanced for named schemas (optional)
4. `CLAUDE.md` - Added documentation and gotchas

### Pipeline Integration Points
1. After EBNF→OpenAPI conversion: Run oneOf schema fix
2. After collection generation: Run oneOf placeholder fix
3. During test data generation: Handle oneOf placeholders
4. In CI/CD: All fixes run automatically
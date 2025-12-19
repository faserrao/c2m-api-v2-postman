# Configuration-Driven Getting Started Collection

## Overview

This document describes the configuration-driven architecture for generating Getting Started collections with both placeholder and realistic test data.

## Architecture

### Single Source of Truth: YAML Configuration

All Getting Started patterns are defined in `config/getting-started-patterns.yaml` (420 lines):

```yaml
patterns:
  - name: "Single recipient - basic job submission"
    description: "Submit a single document to one recipient using jobTemplate"
    category: "Most Frequently Used"
    endpoint: "/jobs/submit/single/doc"
    body_template:
      jobTemplate: "<string>"
      documentSource:
        requestId: "<integer>"
      recipientAddressSource:
        singleAddress:
          firstName: "<string>"
          lastName: "<string>"
          address1: "<string>"
          city: "<string>"
          state: "<string>"
          zip: "<string>"
    filters:
      has_jobTemplate: true
      documentSourceIdentifier: "requestId"
      recipientAddressSource: "singleAddress"
      paymentDetails: "any"
```

### Two Generation Scripts

Both scripts read from the same YAML configuration but produce different outputs:

#### 1. Placeholder Version (`generate_getting_started_collection_v2.py`)

**Purpose**: Educational collection showing API structure with placeholders

**Output**: `c2mapiv2-getting-started-collection.json`

**Example**:
```json
{
  "jobTemplate": "<string>",
  "documentSource": {
    "requestId": "<integer>"
  },
  "recipientAddressSource": {
    "singleAddress": {
      "firstName": "<string>",
      "lastName": "<string>",
      "address1": "<string>",
      "city": "<string>",
      "state": "<string>",
      "zip": "<string>"
    }
  }
}
```

**Use Case**: Users learn the API structure and replace placeholders with their own values

#### 2. Realistic Data Version (`generate_getting_started_with_examples.py`)

**Purpose**: Hands-on collection with ready-to-test realistic examples

**Output**: `c2mapiv2-getting-started-with-examples-collection.json`

**Example**:
```json
{
  "jobTemplate": "medical_correspondence",
  "documentSource": {
    "requestId": 11011
  },
  "recipientAddressSource": {
    "singleAddress": {
      "firstName": "John",
      "lastName": "Brown",
      "address1": "1839 Maple Blvd",
      "city": "New York",
      "state": "IL",
      "zip": "23612"
    }
  }
}
```

**Use Case**: Users test API immediately with realistic data, then adapt to their needs

## Pattern Filters

Each pattern includes filter criteria for intelligent test data generation:

```yaml
filters:
  has_jobTemplate: true                      # Uses jobTemplate (not jobOptions)
  documentSourceIdentifier: "requestId"      # Document source type
  recipientAddressSource: "singleAddress"    # Address source type
  paymentDetails: "any"                      # Payment details type (any/creditCard/ach/invoice)
```

These filters enable:
- **Consistent test data**: Each pattern gets appropriate data for its use case
- **Future permutation filtering**: Can select matching permutations from generated test data
- **Validation**: Ensure generated examples follow pattern constraints

## Test Data Fixtures

The realistic data generator includes comprehensive fixtures:

### Document Sources
- `requestId`: Random 5-digit integer (10000-99999)
- `documentId`: Random 4-digit integer (1000-9999)
- `url`: Realistic document URL
- `documentsToMerge`: Array of mixed source types

### Recipient Address Sources
- `singleAddress`: Random realistic US address
- `addressList`: Pre-built list with merge fields (foo1, foo2)
- `addressListId`: Random ID (1000-9999)
- `addressListName`: Realistic campaign names

### Payment Details
- `creditCard`: Visa test card with random expiration
- `ach`: Sample ACH bank account
- `invoice`: Generated invoice/PO numbers

### Job Templates
Rotates through realistic template names:
- `legal_certified_mail`
- `real_estate_postcard`
- `medical_correspondence`
- `monthly_newsletter`
- `invoice_first_class`

### Tags
- Customer segments: `customer_segment_enterprise`
- Campaigns: `campaign_q1_2024`, `campaign_q2_2024`
- Priorities: `priority_high`, `priority_medium`, `priority_low`

## Benefits of Configuration-Driven Approach

### 1. Single Source of Truth
- Both scripts read same YAML configuration
- Patterns stay synchronized automatically
- No code duplication

### 2. Easy Maintenance
- Non-developers can add patterns by editing YAML
- No Python knowledge required to add new use cases
- Clear, self-documenting structure

### 3. Extensibility
- Add new patterns: Edit YAML file
- Add new filter criteria: Update filters section
- Add new test data: Extend TEST_DATA fixtures in Python

### 4. Flexibility
- Generate either placeholder or realistic versions
- Same configuration serves both use cases
- Easy to add third version (e.g., with validation errors)

### 5. Quality Assurance
- Patterns validated at load time (YAML parsing)
- Filter criteria ensure consistent test data
- Both collections guaranteed to have same structure

## Usage

### Generate Placeholder Collection
```bash
python3 scripts/active/generate_getting_started_collection_v2.py
```

Output: `postman/generated/c2mapiv2-getting-started-collection.json`

### Generate Realistic Data Collection
```bash
python3 scripts/active/generate_getting_started_with_examples.py
```

Output: `postman/generated/c2mapiv2-getting-started-with-examples-collection.json`

### Custom Configuration
```bash
python3 scripts/active/generate_getting_started_collection_v2.py \
  --config config/custom-patterns.yaml \
  --output postman/generated/custom-collection.json
```

## Pattern Categories

Both collections organize patterns into 3 categories:

### 1. Most Frequently Used (3 patterns)
Essential API calls every user needs:
- Single recipient basic submission
- Mail merge (multiple recipients)
- PDF with address capture

### 2. Bulk Operations (3 patterns)
High-volume processing patterns:
- Split PDF with address capture
- Split PDF with specified addresses
- Multiple documents from ZIP

### 3. Advanced Patterns (10 patterns)
Less common features and variations:
- Merge multiple documents
- Using jobOptions instead of template
- Using document URL instead of upload
- Adding tags for organization
- Naming an address list for reuse
- Specifying payment method
- Multiple documents from ZIP with addresses
- Multiple separate documents
- Using stored documentId
- Using saved addressListId

## Adding New Patterns

### Step 1: Edit YAML Configuration

Add new pattern to `config/getting-started-patterns.yaml`:

```yaml
- name: "Your New Pattern"
  description: "What this pattern demonstrates"
  category: "Most Frequently Used"  # or Bulk Operations / Advanced Patterns
  endpoint: "/jobs/submit/your/endpoint"
  body_template:
    # Your request body structure with placeholders
  filters:
    has_jobTemplate: true
    documentSourceIdentifier: "requestId"
    recipientAddressSource: "singleAddress"
    paymentDetails: "any"
```

### Step 2: Regenerate Collections

```bash
# Generate both versions
python3 scripts/active/generate_getting_started_collection_v2.py
python3 scripts/active/generate_getting_started_with_examples.py
```

### Step 3: Upload to Postman

Both collections are ready for upload with the new pattern included.

## File Structure

```
config/
  getting-started-patterns.yaml           # Pattern definitions (YAML)

scripts/active/
  generate_getting_started_collection_v2.py     # Placeholder generator
  generate_getting_started_with_examples.py     # Realistic data generator

postman/generated/
  c2mapiv2-getting-started-collection.json            # Placeholders
  c2mapiv2-getting-started-with-examples-collection.json  # Realistic data
```

## Implementation Timeline

- **2025-12-19**: Configuration-driven architecture implemented
- **Phase 1 Complete**: YAML configuration with 16 patterns
- **Phase 2 Complete**: Placeholder generator (v2) reading from YAML
- **Phase 3 Complete**: Realistic data generator with comprehensive fixtures
- **Status**: Production-ready, tested, verified

## Key Learnings

1. **Configuration over code**: Declarative YAML is easier to maintain than hardcoded Python
2. **Single source of truth**: Both generators read same config = guaranteed synchronization
3. **Filter criteria crucial**: Enables intelligent test data generation
4. **Realistic data valuable**: Users can test immediately without manual data entry
5. **Documentation as code**: YAML comments serve as inline documentation

## Future Enhancements

### Potential Additions:
1. **Validation error examples**: Third generator producing invalid requests for testing error handling
2. **Permutation integration**: Use filter criteria to select from pre-generated permutations
3. **Localization**: Generate examples with international addresses (UK, Australia, Canada)
4. **Custom faker profiles**: Allow users to specify preferred test data styles
5. **Schema validation**: Validate generated examples against OpenAPI spec

### Makefile Integration:
```makefile
# Generate Getting Started collections
.PHONY: postman-generate-getting-started-placeholder
postman-generate-getting-started-placeholder:
	python3 scripts/active/generate_getting_started_collection_v2.py

.PHONY: postman-generate-getting-started-examples
postman-generate-getting-started-examples:
	python3 scripts/active/generate_getting_started_with_examples.py

.PHONY: postman-generate-getting-started-all
postman-generate-getting-started-all: postman-generate-getting-started-placeholder postman-generate-getting-started-examples
	@echo "Both Getting Started collections generated"
```

## Conclusion

The configuration-driven architecture provides:
- **Maintainability**: Easy to add/modify patterns
- **Consistency**: Both versions stay synchronized
- **Flexibility**: Generate placeholders or realistic data
- **Quality**: Comprehensive test data fixtures
- **Documentation**: Self-documenting YAML configuration

This approach scales well as the API grows and makes onboarding new users significantly easier.

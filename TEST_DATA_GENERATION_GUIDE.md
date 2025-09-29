# C2M API Test Data Generation Guide

## Table of Contents
1. [Current Test Data Generation Process](#1-current-test-data-generation-process)
2. [How Examples Are Added to OpenAPI Spec](#2-how-examples-are-added-to-openapi-spec)
3. [OpenAPI Spec Files Explained](#3-openapi-spec-files-explained)
4. [How We SHOULD Generate Test Data](#4-how-we-should-generate-test-data)
5. [Real World Use Case Payloads](#5-real-world-use-case-payloads)
6. [Test Data Validation Strategy](#6-test-data-validation-strategy)

---

## 1. Current Test Data Generation Process

### Overview
Currently, test data is generated through THREE separate mechanisms, which is causing inconsistency:

### A. Static Payloads in `generate_use_case_collection.py`
**Location**: `scripts/active/generate_use_case_collection.py`

**Process**:
1. **Static Base Payloads** (lines 65-440): 
   - 8 hardcoded use cases with complete request bodies
   - These are MANUALLY written and don't reference the OpenAPI spec
   - Example:
   ```python
   "legal_firm": {
       "payload": {
           "documentSourceIdentifier": {"documentId": 1234},  # Fixed after our changes
           "recipientAddressSources": [...]
       }
   }
   ```

2. **Dynamic Variations** (lines 445-580):
   - Creates 5 variations per use case by cycling through:
     - 5 documentSourceIdentifier variants
     - 6 paymentDetails variants  
     - 3 recipientAddressSource variants
   - These variants are ALSO hardcoded:
   ```python
   doc_source_variants = [
       ("Document ID", {"documentId": 1234}),
       ("External URL", {"externalUrl": "https://..."}),
       ...
   ]
   ```

### B. Random Data Generation in `addRandomDataToRaw.js`
**Location**: `scripts/test_data_generator_for_collections/addRandomDataToRaw.js`

**Process**:
1. Reads a Postman collection
2. For each request, replaces placeholder values with random data
3. Uses `oneOfFixtures` for fields with multiple variants:
   ```javascript
   const oneOfFixtures = {
       documentSourceIdentifier: [
           { "documentId": 1234 },
           { "externalUrl": "https://..." },
           // ... other variants
       ]
   }
   ```
4. Rotates through these fixtures to create variety

### C. OpenAPI Example Generation in `add_examples_to_spec.py`
**Location**: `scripts/test_data_generator_for_openapi_specs/add_examples_to_spec.py`

**Process**:
1. Reads the OpenAPI spec
2. For each schema field, generates random values based on type
3. Adds these as examples to the spec
4. BUT: Doesn't understand oneOf schemas properly
5. Result: Examples that don't match the actual schema requirements

---

## 2. How Examples Are Added to OpenAPI Spec

### Current Process Flow:
```
1. c2mapiv2-openapi-spec-final.yaml (no examples)
   ↓
2. add_examples_to_spec.py runs
   ↓  
3. c2mapiv2-openapi-spec-final-with-examples.yaml (with auto-generated examples)
```

### Problems with Current Approach:
1. **Type-based only**: Generates examples based on primitive types (string→"John", integer→123)
2. **No schema awareness**: Doesn't understand complex schemas, oneOf, or business rules
3. **No EBNF awareness**: Doesn't know that `documentId` should be wrapped in an object for oneOf
4. **Inconsistent**: Generated examples don't match the hardcoded test data

---

## 3. OpenAPI Spec Files Explained

### Directory: `/openapi/`

1. **`c2mapiv2-openapi-spec-base.yaml`**
   - Raw output from EBNF→OpenAPI converter
   - No examples, no fixes
   - Should NOT be edited manually

2. **`c2mapiv2-openapi-spec-final.yaml`**
   - The "production" spec after all processing
   - Includes oneOf fixes from `fix_openapi_oneOf_schemas.py`
   - No examples
   - Used for documentation and API definition

3. **`c2mapiv2-openapi-spec-final-with-examples.yaml`**
   - Same as final but with auto-generated examples
   - Created by `add_examples_to_spec.py`
   - Used for Postman collection generation
   - Examples are often incorrect for complex schemas

4. **`c2mapiv2-openapi-spec-final-fixed-oneOf.yaml`**
   - Intermediate file during oneOf processing
   - Should be temporary but persists

5. **`c2mapiv2-openapi-spec-final-with-multi-examples.yaml`**
   - Attempt to add multiple examples per endpoint
   - Not currently used in pipeline

6. **`bundled.yaml`**
   - Single-file version for distribution
   - All $refs resolved inline

---

## 4. How We SHOULD Generate Test Data

### Proposed Architecture:

```
EBNF Data Dictionary
    ↓
OpenAPI Spec (with schema)
    ↓
Schema-Aware Example Generator
    ↓
Examples embedded in OpenAPI spec
    ↓
All collections use these examples
```

### Implementation Requirements:

1. **Single Source of Truth**: OpenAPI spec with embedded examples
2. **Schema-Aware Generation**:
   ```python
   def generate_example(schema):
       if 'oneOf' in schema:
           # Generate example for each variant
           return generate_oneof_example(schema['oneOf'])
       elif schema['type'] == 'object':
           # Recursively generate for each property
           return {prop: generate_example(prop_schema) 
                   for prop, prop_schema in schema['properties'].items()}
   ```

3. **EBNF Business Rules**:
   - Understand that `documentSourceIdentifier` is a discriminated union
   - Know which fields are required vs optional
   - Respect min/max values, patterns, enums

4. **Coverage Strategy**:
   - Generate at least one example per oneOf variant
   - Cover required vs optional field combinations
   - Include edge cases (min/max values, empty arrays)

---

## 5. Real World Use Case Payloads

### Legal Firm - Single Doc Job Template
```json
{
  "documentSourceIdentifier": {"documentId": 1234},
  "recipientAddressSources": [
    {
      "firstName": "John",
      "lastName": "Doe", 
      "address1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "USA"
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "certifiedMail",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {"month": 12, "year": 2025},
      "cvv": 123
    }
  },
  "tags": ["legal", "certified", "client-correspondence"]
}
```

### Construction Company - Multi PDF Address Capture
```json
{
  "addressCapturePdfs": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_001.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 50,
        "pageOffset": 0
      }
    }
  ],
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "INV-2024-001",
      "amountDue": 5000
    }
  }
}
```

### Real Estate - Single Doc Job Template (with external URL)
```json
{
  "documentSourceIdentifier": {
    "externalUrl": "https://api.example.com/v1/marketing/postcards/luxury-homes"
  },
  "recipientAddressSources": [
    {"addressListId": 100},
    {"addressListId": 101},
    {"addressListId": 102}
  ],
  "jobOptions": {
    "documentClass": "marketingMaterial",
    "layout": "landscape",
    "mailclass": "standardMail",
    "paperType": "postcard",
    "printOption": "color",
    "envelope": "postcard"
  },
  "paymentDetails": {
    "userCreditDetails": {"creditAmount": 1000}
  }
}
```

### Medical Agency - Merge Multi Doc
```json
{
  "documentsToMerge": [
    {"documentId": 1001},
    {"uploadRequestId": 300, "documentName": "patient_report.pdf"},
    {"documentId": 1002}
  ],
  "recipientAddressSource": {
    "firstName": "Patient",
    "lastName": "Name",
    "address1": "789 Health Street",
    "city": "Chicago",
    "state": "IL",
    "zip": "60601",
    "country": "USA"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {"month": 12, "year": 2025},
      "cvv": 123
    }
  }
}
```

### All DocumentSourceIdentifier Variants:
1. `{"documentId": 1234}`
2. `{"externalUrl": "https://..."}`
3. `{"uploadRequestId": 100, "documentName": "file.pdf"}`
4. `{"uploadRequestId": 100, "zipId": 10, "documentName": "file.pdf"}`
5. `{"zipId": 20, "documentName": "file.pdf"}`

### All RecipientAddressSource Variants:
1. Full address object: `{"firstName": "...", "lastName": "...", ...}`
2. Address list: `{"addressListId": 42}`
3. Single address: `{"addressId": 12345}`

### All PaymentDetails Variants:
1. Credit card: `{"creditCardDetails": {...}}`
2. Invoice: `{"invoiceDetails": {...}}`
3. ACH: `{"achDetails": {...}}`
4. User credit: `{"userCreditDetails": {...}}`
5. Apple Pay: `{"applePayDetails": {...}}`
6. Google Pay: `{"googlePayDetails": {...}}`

---

## 6. Test Data Validation Strategy

### A. Schema Validation Pipeline

```python
def validate_test_data(test_payload, endpoint_path, method):
    # 1. Load OpenAPI spec
    spec = load_openapi_spec()
    
    # 2. Find endpoint schema
    endpoint_schema = spec['paths'][endpoint_path][method]['requestBody']['content']['application/json']['schema']
    
    # 3. Validate against schema
    validate_against_schema(test_payload, endpoint_schema)
    
    # 4. Validate business rules from EBNF
    validate_business_rules(test_payload, load_ebnf_rules())
```

### B. Coverage Requirements

**Minimum Coverage**:
1. **OneOf Coverage**: 100% - Every variant must have at least one example
2. **Required Fields**: 100% - All required fields must be present
3. **Optional Fields**: 50% - Half the examples should include optional fields
4. **Edge Cases**: Include min/max values, empty arrays, null values where allowed

**Coverage Matrix Example**:
```
documentSourceIdentifier variants:
✓ documentId                     (5 examples)
✓ externalUrl                    (5 examples)
✓ uploadRequestId + documentName (5 examples)
✓ uploadRequestId + zipId + doc  (5 examples)
✓ zipId + documentName          (5 examples)
Coverage: 100% (25/25 examples)
```

### C. Validation Process

1. **Pre-Generation Validation**:
   - Verify EBNF compiles correctly
   - Ensure OpenAPI spec is valid
   - Check that all oneOf schemas have discriminators

2. **Generation-Time Validation**:
   - Each generated example is validated against schema
   - Business rules are checked (e.g., expiration date > current date)
   - Referential integrity (e.g., referenced IDs exist)

3. **Post-Generation Validation**:
   - Coverage report showing which variants are tested
   - Mock server can parse all examples
   - No 400 errors when running collections

### D. Automated Testing Strategy

```javascript
// Test that all oneOf variants are covered
describe('OneOf Coverage', () => {
  const examples = loadExamples();
  
  test('documentSourceIdentifier has all 5 variants', () => {
    const variants = examples.map(e => getVariantType(e.documentSourceIdentifier));
    expect(new Set(variants).size).toBe(5);
  });
  
  test('each variant appears at least 3 times', () => {
    const counts = countVariants(examples);
    Object.values(counts).forEach(count => {
      expect(count).toBeGreaterThanOrEqual(3);
    });
  });
});
```

### E. Continuous Validation

1. **Pre-commit hooks**: Validate that any changes to EBNF/examples maintain coverage
2. **CI/CD pipeline**: Run full validation suite
3. **Mock server tests**: Ensure all examples return 200 OK
4. **Weekly reports**: Coverage metrics and validation results

---

## Key Takeaways

1. **Current State**: Three disconnected systems generating different test data
2. **Root Cause**: No single source of truth, hardcoded values everywhere
3. **Solution**: Schema-aware generation from OpenAPI spec
4. **Validation**: Automated coverage tracking and business rule validation
5. **Next Steps**: 
   - Implement schema-aware example generator
   - Remove all hardcoded payloads
   - Add validation pipeline
   - Generate coverage reports

---

## APPENDIX: All Real World Use Case Requests

### Complete Request Listing

Each POST endpoint in the Real World Use Cases collection contains **5 example variations** demonstrating different combinations of:
- Document source types (Document ID, External URL, Upload Request, Upload + Zip, Zip Only)  
- Payment methods (Credit Card, Invoice, ACH, User Credit, Apple Pay)
- Address sources (New Address, Address List ID, Address ID)
## Legal Firm
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": 1234,
  "recipientAddressSources": [
    {
      "firstName": "John",
      "lastName": "Doe",
      "address1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "USA"
    },
    {
      "firstName": "Jane",
      "lastName": "Smith (Attorney)",
      "address1": "456 Legal Avenue",
      "city": "New York",
      "state": "NY",
      "zip": "10002",
      "country": "USA",
      "nickName": "Attorney Copy"
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {
        "month": 12,
        "year": 2025
      },
      "cvv": 123
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

## Legal Firm
### [multi-pdf-address-capture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-pdf-address-capture

```json
{
  "addressCapturePdfs": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_001.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_002.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_003.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "BATCH-2024-001",
      "amountDue": 450.0
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

## Legal Firm
### [single-pdf-split-addressCapture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split-addressCapture

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "combined_invoices.pdf"
  },
  "embeddedExtractionSpecs": [
    {
      "startPage": 1,
      "endPage": 1,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "startPage": 2,
      "endPage": 2,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

## Legal Firm
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": "https://api.example.com/v1/marketing/postcards/luxury-homes",
  "recipientAddressSources": [
    100,
    101,
    102
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "landscape",
    "mailclass": "firstClassMail",
    "paperType": "postcard",
    "printOption": "color",
    "envelope": "postcard"
  },
  "paymentDetails": {
    "creditAmount": {
      "amount": 500.0,
      "currency": "USD"
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

## Legal Firm
### [multi-doc-merge-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc-merge-job-template

```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "uploadRequestId": 300,
      "documentName": "patient_report.pdf"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "firstName": "Patient",
    "lastName": "Name",
    "address1": "789 Health Street",
    "address2": "Suite 200",
    "city": "Chicago",
    "state": "IL",
    "zip": "60601",
    "country": "USA"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "MED-2024-567",
      "amountDue": 75.0
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

## Legal Firm
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": {
    "zipId": 50,
    "documentName": "newsletter_december_2024.pdf"
  },
  "recipientAddressSources": [
    {
      "addressListId": 200
    },
    {
      "addressListId": 201
    },
    {
      "addressListId": 202
    }
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "portrait",
    "mailclass": "largeEnvelope",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "flat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "mastercard",
      "cardNumber": "5555555555554444",
      "expirationDate": {
        "month": 6,
        "year": 2026
      },
      "cvv": 456
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

## Legal Firm
### [single-pdf-split]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 400,
    "documentName": "batched_pdfs.pdf"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        301
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        302
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        303
      ]
    }
  ],
  "paymentDetails": {
    "applePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

## Legal Firm
### [multi-doc]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc

```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_01.pdf"
      },
      "recipientAddressSource": 6001
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_02.pdf"
      },
      "recipientAddressSource": 6002
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_03.pdf"
      },
      "recipientAddressSource": 6003
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "priorityMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "letter"
  },
  "paymentDetails": {
    "googlePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

## Company #1
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": 1234,
  "recipientAddressSources": [
    {
      "firstName": "John",
      "lastName": "Doe",
      "address1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "USA"
    },
    {
      "firstName": "Jane",
      "lastName": "Smith (Attorney)",
      "address1": "456 Legal Avenue",
      "city": "New York",
      "state": "NY",
      "zip": "10002",
      "country": "USA",
      "nickName": "Attorney Copy"
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {
        "month": 12,
        "year": 2025
      },
      "cvv": 123
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

## Company #1
### [multi-pdf-address-capture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-pdf-address-capture

```json
{
  "addressCapturePdfs": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_001.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_002.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_003.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "BATCH-2024-001",
      "amountDue": 450.0
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

## Company #1
### [single-pdf-split-addressCapture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split-addressCapture

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "combined_invoices.pdf"
  },
  "embeddedExtractionSpecs": [
    {
      "startPage": 1,
      "endPage": 1,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "startPage": 2,
      "endPage": 2,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

## Company #1
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": "https://api.example.com/v1/marketing/postcards/luxury-homes",
  "recipientAddressSources": [
    100,
    101,
    102
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "landscape",
    "mailclass": "firstClassMail",
    "paperType": "postcard",
    "printOption": "color",
    "envelope": "postcard"
  },
  "paymentDetails": {
    "creditAmount": {
      "amount": 500.0,
      "currency": "USD"
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

## Company #1
### [multi-doc-merge-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc-merge-job-template

```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "uploadRequestId": 300,
      "documentName": "patient_report.pdf"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "firstName": "Patient",
    "lastName": "Name",
    "address1": "789 Health Street",
    "address2": "Suite 200",
    "city": "Chicago",
    "state": "IL",
    "zip": "60601",
    "country": "USA"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "MED-2024-567",
      "amountDue": 75.0
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

## Company #1
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": {
    "zipId": 50,
    "documentName": "newsletter_december_2024.pdf"
  },
  "recipientAddressSources": [
    {
      "addressListId": 200
    },
    {
      "addressListId": 201
    },
    {
      "addressListId": 202
    }
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "portrait",
    "mailclass": "largeEnvelope",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "flat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "mastercard",
      "cardNumber": "5555555555554444",
      "expirationDate": {
        "month": 6,
        "year": 2026
      },
      "cvv": 456
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

## Company #1
### [single-pdf-split]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 400,
    "documentName": "batched_pdfs.pdf"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        301
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        302
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        303
      ]
    }
  ],
  "paymentDetails": {
    "applePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

## Company #1
### [multi-doc]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc

```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_01.pdf"
      },
      "recipientAddressSource": 6001
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_02.pdf"
      },
      "recipientAddressSource": 6002
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_03.pdf"
      },
      "recipientAddressSource": 6003
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "priorityMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "letter"
  },
  "paymentDetails": {
    "googlePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

## Company #2
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": 1234,
  "recipientAddressSources": [
    {
      "firstName": "John",
      "lastName": "Doe",
      "address1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "USA"
    },
    {
      "firstName": "Jane",
      "lastName": "Smith (Attorney)",
      "address1": "456 Legal Avenue",
      "city": "New York",
      "state": "NY",
      "zip": "10002",
      "country": "USA",
      "nickName": "Attorney Copy"
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {
        "month": 12,
        "year": 2025
      },
      "cvv": 123
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

## Company #2
### [multi-pdf-address-capture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-pdf-address-capture

```json
{
  "addressCapturePdfs": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_001.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_002.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_003.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "BATCH-2024-001",
      "amountDue": 450.0
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

## Company #2
### [single-pdf-split-addressCapture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split-addressCapture

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "combined_invoices.pdf"
  },
  "embeddedExtractionSpecs": [
    {
      "startPage": 1,
      "endPage": 1,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "startPage": 2,
      "endPage": 2,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

## Company #2
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": "https://api.example.com/v1/marketing/postcards/luxury-homes",
  "recipientAddressSources": [
    100,
    101,
    102
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "landscape",
    "mailclass": "firstClassMail",
    "paperType": "postcard",
    "printOption": "color",
    "envelope": "postcard"
  },
  "paymentDetails": {
    "creditAmount": {
      "amount": 500.0,
      "currency": "USD"
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

## Company #2
### [multi-doc-merge-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc-merge-job-template

```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "uploadRequestId": 300,
      "documentName": "patient_report.pdf"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "firstName": "Patient",
    "lastName": "Name",
    "address1": "789 Health Street",
    "address2": "Suite 200",
    "city": "Chicago",
    "state": "IL",
    "zip": "60601",
    "country": "USA"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "MED-2024-567",
      "amountDue": 75.0
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

## Company #2
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": {
    "zipId": 50,
    "documentName": "newsletter_december_2024.pdf"
  },
  "recipientAddressSources": [
    {
      "addressListId": 200
    },
    {
      "addressListId": 201
    },
    {
      "addressListId": 202
    }
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "portrait",
    "mailclass": "largeEnvelope",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "flat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "mastercard",
      "cardNumber": "5555555555554444",
      "expirationDate": {
        "month": 6,
        "year": 2026
      },
      "cvv": 456
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

## Company #2
### [single-pdf-split]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 400,
    "documentName": "batched_pdfs.pdf"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        301
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        302
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        303
      ]
    }
  ],
  "paymentDetails": {
    "applePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

## Company #2
### [multi-doc]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc

```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_01.pdf"
      },
      "recipientAddressSource": 6001
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_02.pdf"
      },
      "recipientAddressSource": 6002
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_03.pdf"
      },
      "recipientAddressSource": 6003
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "priorityMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "letter"
  },
  "paymentDetails": {
    "googlePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

## Real Estate Agent
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": 1234,
  "recipientAddressSources": [
    {
      "firstName": "John",
      "lastName": "Doe",
      "address1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "USA"
    },
    {
      "firstName": "Jane",
      "lastName": "Smith (Attorney)",
      "address1": "456 Legal Avenue",
      "city": "New York",
      "state": "NY",
      "zip": "10002",
      "country": "USA",
      "nickName": "Attorney Copy"
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {
        "month": 12,
        "year": 2025
      },
      "cvv": 123
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

## Real Estate Agent
### [multi-pdf-address-capture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-pdf-address-capture

```json
{
  "addressCapturePdfs": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_001.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_002.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_003.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "BATCH-2024-001",
      "amountDue": 450.0
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

## Real Estate Agent
### [single-pdf-split-addressCapture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split-addressCapture

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "combined_invoices.pdf"
  },
  "embeddedExtractionSpecs": [
    {
      "startPage": 1,
      "endPage": 1,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "startPage": 2,
      "endPage": 2,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

## Real Estate Agent
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": "https://api.example.com/v1/marketing/postcards/luxury-homes",
  "recipientAddressSources": [
    100,
    101,
    102
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "landscape",
    "mailclass": "firstClassMail",
    "paperType": "postcard",
    "printOption": "color",
    "envelope": "postcard"
  },
  "paymentDetails": {
    "creditAmount": {
      "amount": 500.0,
      "currency": "USD"
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

## Real Estate Agent
### [multi-doc-merge-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc-merge-job-template

```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "uploadRequestId": 300,
      "documentName": "patient_report.pdf"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "firstName": "Patient",
    "lastName": "Name",
    "address1": "789 Health Street",
    "address2": "Suite 200",
    "city": "Chicago",
    "state": "IL",
    "zip": "60601",
    "country": "USA"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "MED-2024-567",
      "amountDue": 75.0
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

## Real Estate Agent
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": {
    "zipId": 50,
    "documentName": "newsletter_december_2024.pdf"
  },
  "recipientAddressSources": [
    {
      "addressListId": 200
    },
    {
      "addressListId": 201
    },
    {
      "addressListId": 202
    }
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "portrait",
    "mailclass": "largeEnvelope",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "flat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "mastercard",
      "cardNumber": "5555555555554444",
      "expirationDate": {
        "month": 6,
        "year": 2026
      },
      "cvv": 456
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

## Real Estate Agent
### [single-pdf-split]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 400,
    "documentName": "batched_pdfs.pdf"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        301
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        302
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        303
      ]
    }
  ],
  "paymentDetails": {
    "applePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

## Real Estate Agent
### [multi-doc]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc

```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_01.pdf"
      },
      "recipientAddressSource": 6001
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_02.pdf"
      },
      "recipientAddressSource": 6002
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_03.pdf"
      },
      "recipientAddressSource": 6003
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "priorityMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "letter"
  },
  "paymentDetails": {
    "googlePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

## Medical Agency
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": 1234,
  "recipientAddressSources": [
    {
      "firstName": "John",
      "lastName": "Doe",
      "address1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "USA"
    },
    {
      "firstName": "Jane",
      "lastName": "Smith (Attorney)",
      "address1": "456 Legal Avenue",
      "city": "New York",
      "state": "NY",
      "zip": "10002",
      "country": "USA",
      "nickName": "Attorney Copy"
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {
        "month": 12,
        "year": 2025
      },
      "cvv": 123
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

## Medical Agency
### [multi-pdf-address-capture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-pdf-address-capture

```json
{
  "addressCapturePdfs": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_001.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_002.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_003.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "BATCH-2024-001",
      "amountDue": 450.0
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

## Medical Agency
### [single-pdf-split-addressCapture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split-addressCapture

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "combined_invoices.pdf"
  },
  "embeddedExtractionSpecs": [
    {
      "startPage": 1,
      "endPage": 1,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "startPage": 2,
      "endPage": 2,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

## Medical Agency
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": "https://api.example.com/v1/marketing/postcards/luxury-homes",
  "recipientAddressSources": [
    100,
    101,
    102
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "landscape",
    "mailclass": "firstClassMail",
    "paperType": "postcard",
    "printOption": "color",
    "envelope": "postcard"
  },
  "paymentDetails": {
    "creditAmount": {
      "amount": 500.0,
      "currency": "USD"
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

## Medical Agency
### [multi-doc-merge-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc-merge-job-template

```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "uploadRequestId": 300,
      "documentName": "patient_report.pdf"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "firstName": "Patient",
    "lastName": "Name",
    "address1": "789 Health Street",
    "address2": "Suite 200",
    "city": "Chicago",
    "state": "IL",
    "zip": "60601",
    "country": "USA"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "MED-2024-567",
      "amountDue": 75.0
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

## Medical Agency
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": {
    "zipId": 50,
    "documentName": "newsletter_december_2024.pdf"
  },
  "recipientAddressSources": [
    {
      "addressListId": 200
    },
    {
      "addressListId": 201
    },
    {
      "addressListId": 202
    }
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "portrait",
    "mailclass": "largeEnvelope",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "flat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "mastercard",
      "cardNumber": "5555555555554444",
      "expirationDate": {
        "month": 6,
        "year": 2026
      },
      "cvv": 456
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

## Medical Agency
### [single-pdf-split]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 400,
    "documentName": "batched_pdfs.pdf"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        301
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        302
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        303
      ]
    }
  ],
  "paymentDetails": {
    "applePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

## Medical Agency
### [multi-doc]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc

```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_01.pdf"
      },
      "recipientAddressSource": 6001
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_02.pdf"
      },
      "recipientAddressSource": 6002
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_03.pdf"
      },
      "recipientAddressSource": 6003
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "priorityMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "letter"
  },
  "paymentDetails": {
    "googlePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

## Monthly Newsletters
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": 1234,
  "recipientAddressSources": [
    {
      "firstName": "John",
      "lastName": "Doe",
      "address1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "USA"
    },
    {
      "firstName": "Jane",
      "lastName": "Smith (Attorney)",
      "address1": "456 Legal Avenue",
      "city": "New York",
      "state": "NY",
      "zip": "10002",
      "country": "USA",
      "nickName": "Attorney Copy"
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {
        "month": 12,
        "year": 2025
      },
      "cvv": 123
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

## Monthly Newsletters
### [multi-pdf-address-capture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-pdf-address-capture

```json
{
  "addressCapturePdfs": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_001.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_002.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_003.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "BATCH-2024-001",
      "amountDue": 450.0
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

## Monthly Newsletters
### [single-pdf-split-addressCapture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split-addressCapture

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "combined_invoices.pdf"
  },
  "embeddedExtractionSpecs": [
    {
      "startPage": 1,
      "endPage": 1,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "startPage": 2,
      "endPage": 2,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

## Monthly Newsletters
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": "https://api.example.com/v1/marketing/postcards/luxury-homes",
  "recipientAddressSources": [
    100,
    101,
    102
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "landscape",
    "mailclass": "firstClassMail",
    "paperType": "postcard",
    "printOption": "color",
    "envelope": "postcard"
  },
  "paymentDetails": {
    "creditAmount": {
      "amount": 500.0,
      "currency": "USD"
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

## Monthly Newsletters
### [multi-doc-merge-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc-merge-job-template

```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "uploadRequestId": 300,
      "documentName": "patient_report.pdf"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "firstName": "Patient",
    "lastName": "Name",
    "address1": "789 Health Street",
    "address2": "Suite 200",
    "city": "Chicago",
    "state": "IL",
    "zip": "60601",
    "country": "USA"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "MED-2024-567",
      "amountDue": 75.0
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

## Monthly Newsletters
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": {
    "zipId": 50,
    "documentName": "newsletter_december_2024.pdf"
  },
  "recipientAddressSources": [
    {
      "addressListId": 200
    },
    {
      "addressListId": 201
    },
    {
      "addressListId": 202
    }
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "portrait",
    "mailclass": "largeEnvelope",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "flat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "mastercard",
      "cardNumber": "5555555555554444",
      "expirationDate": {
        "month": 6,
        "year": 2026
      },
      "cvv": 456
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

## Monthly Newsletters
### [single-pdf-split]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 400,
    "documentName": "batched_pdfs.pdf"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        301
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        302
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        303
      ]
    }
  ],
  "paymentDetails": {
    "applePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

## Monthly Newsletters
### [multi-doc]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc

```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_01.pdf"
      },
      "recipientAddressSource": 6001
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_02.pdf"
      },
      "recipientAddressSource": 6002
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_03.pdf"
      },
      "recipientAddressSource": 6003
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "priorityMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "letter"
  },
  "paymentDetails": {
    "googlePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

## Reseller #1
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": 1234,
  "recipientAddressSources": [
    {
      "firstName": "John",
      "lastName": "Doe",
      "address1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "USA"
    },
    {
      "firstName": "Jane",
      "lastName": "Smith (Attorney)",
      "address1": "456 Legal Avenue",
      "city": "New York",
      "state": "NY",
      "zip": "10002",
      "country": "USA",
      "nickName": "Attorney Copy"
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {
        "month": 12,
        "year": 2025
      },
      "cvv": 123
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

## Reseller #1
### [multi-pdf-address-capture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-pdf-address-capture

```json
{
  "addressCapturePdfs": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_001.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_002.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_003.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "BATCH-2024-001",
      "amountDue": 450.0
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

## Reseller #1
### [single-pdf-split-addressCapture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split-addressCapture

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "combined_invoices.pdf"
  },
  "embeddedExtractionSpecs": [
    {
      "startPage": 1,
      "endPage": 1,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "startPage": 2,
      "endPage": 2,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

## Reseller #1
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": "https://api.example.com/v1/marketing/postcards/luxury-homes",
  "recipientAddressSources": [
    100,
    101,
    102
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "landscape",
    "mailclass": "firstClassMail",
    "paperType": "postcard",
    "printOption": "color",
    "envelope": "postcard"
  },
  "paymentDetails": {
    "creditAmount": {
      "amount": 500.0,
      "currency": "USD"
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

## Reseller #1
### [multi-doc-merge-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc-merge-job-template

```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "uploadRequestId": 300,
      "documentName": "patient_report.pdf"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "firstName": "Patient",
    "lastName": "Name",
    "address1": "789 Health Street",
    "address2": "Suite 200",
    "city": "Chicago",
    "state": "IL",
    "zip": "60601",
    "country": "USA"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "MED-2024-567",
      "amountDue": 75.0
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

## Reseller #1
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": {
    "zipId": 50,
    "documentName": "newsletter_december_2024.pdf"
  },
  "recipientAddressSources": [
    {
      "addressListId": 200
    },
    {
      "addressListId": 201
    },
    {
      "addressListId": 202
    }
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "portrait",
    "mailclass": "largeEnvelope",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "flat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "mastercard",
      "cardNumber": "5555555555554444",
      "expirationDate": {
        "month": 6,
        "year": 2026
      },
      "cvv": 456
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

## Reseller #1
### [single-pdf-split]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 400,
    "documentName": "batched_pdfs.pdf"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        301
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        302
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        303
      ]
    }
  ],
  "paymentDetails": {
    "applePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

## Reseller #1
### [multi-doc]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc

```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_01.pdf"
      },
      "recipientAddressSource": 6001
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_02.pdf"
      },
      "recipientAddressSource": 6002
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_03.pdf"
      },
      "recipientAddressSource": 6003
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "priorityMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "letter"
  },
  "paymentDetails": {
    "googlePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

## Reseller #2
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": 1234,
  "recipientAddressSources": [
    {
      "firstName": "John",
      "lastName": "Doe",
      "address1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "zip": "10001",
      "country": "USA"
    },
    {
      "firstName": "Jane",
      "lastName": "Smith (Attorney)",
      "address1": "456 Legal Avenue",
      "city": "New York",
      "state": "NY",
      "zip": "10002",
      "country": "USA",
      "nickName": "Attorney Copy"
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "4111111111111111",
      "expirationDate": {
        "month": 12,
        "year": 2025
      },
      "cvv": 123
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

## Reseller #2
### [multi-pdf-address-capture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-pdf-address-capture

```json
{
  "addressCapturePdfs": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_001.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_002.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "invoice_003.pdf"
      },
      "addressRegion": {
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "windowedFlat"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "BATCH-2024-001",
      "amountDue": 450.0
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

## Reseller #2
### [single-pdf-split-addressCapture]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split-addressCapture

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "combined_invoices.pdf"
  },
  "embeddedExtractionSpecs": [
    {
      "startPage": 1,
      "endPage": 1,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    },
    {
      "startPage": 2,
      "endPage": 2,
      "addressRegion": {
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 100,
        "pageOffset": 0
      }
    }
  ],
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

## Reseller #2
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": "https://api.example.com/v1/marketing/postcards/luxury-homes",
  "recipientAddressSources": [
    100,
    101,
    102
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "landscape",
    "mailclass": "firstClassMail",
    "paperType": "postcard",
    "printOption": "color",
    "envelope": "postcard"
  },
  "paymentDetails": {
    "creditAmount": {
      "amount": 500.0,
      "currency": "USD"
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

## Reseller #2
### [multi-doc-merge-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc-merge-job-template

```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "uploadRequestId": 300,
      "documentName": "patient_report.pdf"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "firstName": "Patient",
    "lastName": "Name",
    "address1": "789 Health Street",
    "address2": "Suite 200",
    "city": "Chicago",
    "state": "IL",
    "zip": "60601",
    "country": "USA"
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "MED-2024-567",
      "amountDue": 75.0
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

## Reseller #2
### [single-doc-job-template]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-doc-job-template

```json
{
  "documentSourceIdentifier": {
    "zipId": 50,
    "documentName": "newsletter_december_2024.pdf"
  },
  "recipientAddressSources": [
    {
      "addressListId": 200
    },
    {
      "addressListId": 201
    },
    {
      "addressListId": 202
    }
  ],
  "jobOptions": {
    "documentClass": "personalLetter",
    "layout": "portrait",
    "mailclass": "largeEnvelope",
    "paperType": "letter",
    "printOption": "color",
    "envelope": "flat"
  },
  "paymentDetails": {
    "creditCardDetails": {
      "cardType": "mastercard",
      "cardNumber": "5555555555554444",
      "expirationDate": {
        "month": 6,
        "year": 2026
      },
      "cvv": 456
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

## Reseller #2
### [single-pdf-split]
**Method**: POST
**URL**: {{baseUrl}}/jobs/single-pdf-split

```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 400,
    "documentName": "batched_pdfs.pdf"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        301
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        302
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        303
      ]
    }
  ],
  "paymentDetails": {
    "applePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

## Reseller #2
### [multi-doc]
**Method**: POST
**URL**: {{baseUrl}}/jobs/multi-doc

```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_01.pdf"
      },
      "recipientAddressSource": 6001
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_02.pdf"
      },
      "recipientAddressSource": 6002
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 500,
        "zipId": 20,
        "documentName": "document_03.pdf"
      },
      "recipientAddressSource": 6003
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "priorityMail",
    "paperType": "letter",
    "printOption": "grayscale",
    "envelope": "letter"
  },
  "paymentDetails": {
    "googlePaymentDetails": {}
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```


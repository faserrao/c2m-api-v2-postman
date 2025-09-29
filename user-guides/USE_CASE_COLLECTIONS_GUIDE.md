# Use Case Collections Guide

## Overview

The C2M API v2 pipeline now includes enhanced support for oneOf schemas and real-world use case collections. This guide explains how to use the new features that make it easier for developers to work with the API.

## What's New

### 1. Enhanced OneOf Example Extraction
- **Problem**: Postman only imports one example from oneOf schemas, even when multiple variants exist
- **Solution**: New transformer script extracts ALL oneOf examples and adds them to the Examples tab
- **Result**: Developers can see and test all variants without guessing

### 2. Curated Use Case Collection
- **Problem**: Raw API endpoints don't show real-world usage patterns
- **Solution**: Separate collection organized by business use cases
- **Result**: Developers understand how to implement specific scenarios

## Collections Available

After running `make postman-instance-build-and-test`, you'll have:

1. **Linked Collection** - Raw API reference (auto-generated from OpenAPI)
2. **Test Collection** - With test data and automated tests
3. **Enhanced Test Collection** - Test collection with ALL oneOf examples
4. **Use Case Collection** - Real-world scenarios with pre-populated data

## Using the Enhanced Test Collection

The enhanced test collection includes all oneOf variants in the Examples tab:

```
POST /jobs/single-doc
├── Examples Tab
│   ├── Using Document ID
│   ├── Using External URL
│   ├── Using Upload Request ID
│   ├── Using Upload + Zip
│   └── Using Zip ID Only
```

### How to Use:
1. Select the request you want to test
2. Click the "Examples" dropdown
3. Choose the variant that matches your use case
4. Click "Try" to load the example
5. Send the request

## Using the Use Case Collection

The use case collection is organized by real-world scenarios:

```
C2M API v2 – Real World Use Cases
├── Legal Firm – Certified Letters
│   ├── Submit Job
│   ├── Get Job Details
│   └── Get Job Status
├── Company #1 – Invoice Batch
│   ├── Submit Job
│   ├── Get Job Details
│   └── Get Job Status
├── Company #2 – Split Invoices
│   └── ...
└── (5 more use cases)
```

### Each Use Case Includes:
- **Submit Job** - Pre-populated request body for the scenario
- **Get Job Details** - Automatically uses {{jobId}} from Submit Job
- **Get Job Status** - Check processing status

### How to Use:
1. Import the "C2M API v2 – Real World Use Cases" collection
2. Set the `authToken` variable with your JWT
3. Choose a use case folder (e.g., "Legal Firm")
4. Run "Submit Job" first
5. Run follow-up requests using the saved jobId

## Available Use Cases

1. **Legal Firm – Certified Letters**
   - Endpoint: POST /jobs/single-doc
   - Features: Certified mail, copy to lawyer

2. **Company #1 – Invoice Batch**
   - Endpoint: POST /jobs/multi-doc
   - Features: Batch processing, monthly invoices

3. **Company #2 – Split Invoices**
   - Endpoint: POST /jobs/single-pdf-split-addressCapture
   - Features: PDF splitting, address capture

4. **Real Estate Agent – Postcards**
   - Endpoint: POST /jobs/single-doc
   - Features: Marketing postcards, bulk mailing

5. **Medical Agency – Reports + Boilerplate**
   - Endpoint: POST /jobs/multi-doc-merge
   - Features: Document merging, compliance

6. **Monthly Newsletters**
   - Endpoint: POST /jobs/single-doc
   - Features: Newsletter distribution

7. **Reseller #1 – Merge PDFs**
   - Endpoint: POST /jobs/multi-doc-merge
   - Features: PDF merging service

8. **Reseller #2 – Zip PDFs**
   - Endpoint: POST /jobs/multi-doc
   - Features: Zip file processing

## OneOf Field Reference

### documentSourceIdentifier
- **Option 1**: Document ID (integer)
- **Option 2**: External URL (string)
- **Option 3**: Upload Request ID + Document Name
- **Option 4**: Upload Request ID + Zip ID + Document Name
- **Option 5**: Zip ID + Document Name

### recipientAddressSource
- **Option 1**: New Address (full address object)
- **Option 2**: Address List ID (integer)
- **Option 3**: Address ID (integer)

### paymentDetails
- **Option 1**: Credit Card
- **Option 2**: Invoice
- **Option 3**: ACH
- **Option 4**: User Credit
- **Option 5**: Apple Pay
- **Option 6**: Google Pay

## Pipeline Commands

### Generate All Collections
```bash
make postman-instance-build-and-test
```

### Generate Only Enhanced Collections
```bash
make postman-extract-oneof-examples
make postman-generate-use-case-collection
make postman-upload-all-enhanced-collections
```

### Individual Commands
```bash
# Extract all oneOf examples
make postman-extract-oneof-examples

# Generate use case collection
make postman-generate-use-case-collection

# Upload enhanced test collection
make postman-upload-enhanced-collection

# Upload use case collection
make postman-upload-use-case-collection
```

## Tips for Developers

### Choosing the Right Collection

- **Need API reference?** → Use Linked Collection
- **Testing with examples?** → Use Enhanced Test Collection
- **Implementing a feature?** → Use Use Case Collection
- **Running automated tests?** → Use Test Collection

### Working with OneOf Fields

1. Look at the Examples tab to see all variants
2. Choose the variant that matches your data source
3. Modify the example values as needed
4. Test with different variants to ensure compatibility

### Creating New Use Cases

To add a new use case:

1. Edit `scripts/active/generate_use_case_collection.py`
2. Add your use case to the `USE_CASES` dictionary
3. Include endpoint, method, and realistic payload
4. Run `make postman-generate-use-case-collection`
5. Upload and test

## Troubleshooting

### Examples Don't Appear
- Ensure you're using the Enhanced Test Collection
- Check that the OpenAPI spec has examples defined
- Verify the oneOf extraction ran successfully

### Use Case Collection Missing
- Run `make postman-generate-use-case-collection`
- Check for errors in the script output
- Ensure Python environment is activated

### Variable Not Set
- Set collection variables before running requests
- Use {{baseUrl}} and {{authToken}} consistently
- Check environment is selected in Postman

## Best Practices

1. **Start with Use Cases** - Understand the business context first
2. **Test All Variants** - Don't assume one oneOf variant works for all
3. **Save Your Work** - Fork collections for custom modifications
4. **Share Examples** - Add your own examples for team members
5. **Document Changes** - Update this guide when adding use cases

## Next Steps

1. Import the Use Case Collection into Postman
2. Try each use case to understand the API
3. Create your own examples based on these patterns
4. Share feedback to improve the collections

---

*Last Updated: December 2024*
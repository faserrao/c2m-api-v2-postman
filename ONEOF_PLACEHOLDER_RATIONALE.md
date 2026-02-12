# OneOf Placeholder Rationale

## Why Use `<oneOf>` in Non-Examples Collections?

### Purpose

The `<oneOf>` placeholder is used in the **Linked Collection** and **Getting Started Collection** to indicate fields that accept multiple different structures (discriminated unions). This serves an **educational purpose** - helping API users understand the API's flexibility without overwhelming them with all possible variants.

### What is a Discriminated Union?

A discriminated union (also called tagged union or variant) is a field that can accept multiple different structures, but only ONE at a time. The EBNF data dictionary defines these using the `|` operator:

```ebnf
docSourceAll =
      documentIdSource
    | requestIdSource
    | urlSource
    | zipDocumentIdSource
    | zipRequestIdSource ;
```

This means `docSourceAll` can be:
- `{"documentId": 1234}` OR
- `{"requestId": 5678}` OR
- `{"url": "https://example.com/doc.pdf"}` OR
- `{"zipDocumentId": 9012, "filename": "letter.docx"}` OR
- `{"requestId": 3456, "zipFilename": "archive.zip", "filename": "invoice.pdf"}`

But NEVER a combination - only one structure at a time.

### Collections Strategy

We generate **three types** of collections, each serving different purposes:

#### 1. Linked Collection (Placeholders - Educational)

**Purpose**: Learn API structure without distraction

**Strategy**: Show `<oneOf>` for discriminated unions

**Example**:
```json
{
  "docSourceAll": "<oneOf>",
  "recipientAddressSource": "<oneOf>",
  "jobTemplate": "<string>",
  "paymentDetails": "<oneOf>"
}
```

**Benefits**:
- User sees which fields have multiple options
- Encourages reading documentation to understand variants
- Shows complete API surface (all optional fields included)
- Not cluttered with example data
- Clear indication: "this field requires a choice"

#### 2. Getting Started Collection (Placeholders - Onboarding)

**Purpose**: Educational patterns organized by use case

**Strategy**: Same as Linked Collection - uses `<oneOf>` placeholders

**Example**:
```json
{
  "docSourceAll": "<oneOf>",
  "recipientAddressSource": "<oneOf>"
}
```

**Benefits**:
- Organized by frequency (Most Used → Advanced)
- Friendly pattern names ("Single recipient", "Mail merge")
- Users learn API structure before diving into examples

#### 3. Test Collection & Getting Started With Examples (Realistic Data)

**Purpose**: Hands-on testing with actual data

**Strategy**: Rotate through REAL examples of each variant

**Example for requestId variant**:
```json
{
  "docSourceAll": {
    "requestId": 11011
  },
  "recipientAddressSource": {
    "addressId": 5000
  }
}
```

**Example for documentId variant**:
```json
{
  "docSourceAll": {
    "documentId": 1234
  },
  "recipientAddressSource": {
    "singleAddress": {
      "firstName": "John",
      "lastName": "Smith"
    }
  }
}
```

**Benefits**:
- Realistic faker-generated data
- Shows actual variant structures
- Ready to send (just change API key)
- Different examples across endpoints

### Why Not Show All Variants in Linked Collection?

**Problem**: Each endpoint would need 5+ duplicate requests (one per variant)

**Impact**:
- Linked Collection would have 40+ endpoints instead of 8
- Overwhelming for new users
- Harder to navigate
- Cluttered workspace

**Better Solution**:
- Linked Collection: Shows `<oneOf>` (learn structure)
- Test Collection: Shows real examples (see variants in action)
- Documentation: Explains all variants (complete reference)

### OneOf Fields in C2M API V2

The API has **8 oneOf fields** across job submission endpoints:

1. **docSourceAll** - 5 variants (documentId, requestId, url, zipDocumentId+filename, requestId+zipFilename+filename)
2. **docSourceStandard** - 3 variants (documentId, requestId, url)
3. **docSourceZipFile** - 2 variants (zipDocumentId+filename, requestId+zipFilename+filename)
4. **recipientAddressSource** - 4 variants (singleAddress, addressList, addressListId, addressListName)
5. **paymentDetails** - 3 variants (creditCardDetails, achDetails, invoiceDetails)
6. **zipDocumentSource** - 2 variants (zipDocumentId, zipRequestId)
7. **mergeDocumentSource** - 2 variants (documentsToMerge array with Standard or ZipFile sources)
8. **documentAggregationSource** - Multiple job arrays

### Implementation

The `<oneOf>` placeholders are inserted by `scripts/active/fix_oneOf_placeholders.js`:

1. Reads OpenAPI spec to discover all oneOf fields dynamically
2. Finds fields in collection that match oneOf schemas
3. Replaces with `"<oneOf>"` string placeholder
4. Handles both simple values and complex objects

**Before Fix**:
```json
{
  "docSourceAll": {
    "documentId": 0
  }
}
```

**After Fix**:
```json
{
  "docSourceAll": "<oneOf>"
}
```

### User Workflow

1. **Explore Linked Collection** → See `<oneOf>` → Understand field requires choice
2. **Read Documentation** → Learn about 5 document source variants
3. **Check Test Collection** → See real examples of each variant
4. **Test with Getting Started (Examples)** → Try realistic data
5. **Customize for Production** → Use appropriate variant for use case

### Summary

**`<oneOf>` placeholders are educational markers**:
- Indicate "this field has multiple options"
- Encourage documentation reading
- Reduce collection clutter
- Complement test collection's realistic examples
- Show complete API surface without overwhelming new users

**Two-collection strategy**:
- **Linked/Getting Started** (placeholders) = Learn structure
- **Test/Getting Started With Examples** (realistic data) = See variants in action

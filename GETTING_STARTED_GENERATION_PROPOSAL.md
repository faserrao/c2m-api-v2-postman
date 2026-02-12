# Getting Started Collection Generation - Proposed Solution

**Date**: 2026-02-11
**Problem**: Getting Started collection has hardcoded old field names that don't match current EBNF
**Solution**: Generate Getting Started FROM the linked collection instead of hardcoding

---

## Current Problem

### What's Wrong

The script `generate_getting_started_collection.py` has **hardcoded field names**:
- Uses `documentSource` instead of `docSourceAll` (current EBNF field name)
- Uses simplified nested structure instead of proper oneOf structure
- Missing optional fields: `paymentDetails`, `returnAddress`, `jobOptions`, `tags`

### Why This Happened

The script was created before the EBNF was finalized and field names changed. It doesn't read from any generated artifacts - it just hardcodes request bodies.

### User's Requirement

Getting Started collections should:
1. Have the **same endpoints** as linked/test collections
2. Have the **same field names and structure** (generated from EBNF)
3. **Only difference**: Reorganized into educational taxonomy for easier learning
4. Include **all optional fields** to show complete API surface

---

## Proposed Solution

### High-Level Approach

**Generate Getting Started BY reorganizing the Linked Collection**

```
EBNF → OpenAPI → Linked Collection → Getting Started Collection
                      ↑                        ↑
                 (auto-generated)        (reorganize only)
```

### Algorithm

1. **Read the linked collection** (`c2mapiv2-linked-collection-flat.json`)
   - This collection is correctly generated from EBNF
   - Has all the right field names and structure
   - Includes all optional fields

2. **Extract the 8 job submission endpoints**
   - POST /jobs/submit/single/doc
   - POST /jobs/submit/single/pdf/addressCapture
   - POST /jobs/submit/single/pdf/split
   - POST /jobs/submit/single/pdf/split/addressCapture
   - POST /jobs/submit/multi/doc
   - POST /jobs/submit/multi/doc/merge
   - POST /jobs/submit/multi/zip
   - POST /jobs/submit/multi/zip/addressCapture

3. **Categorize into educational groups**
   - **Most Frequently Used** (3 patterns)
     - Single recipient basic
     - Mail merge multiple recipients
     - Address capture
   - **Bulk Operations** (3 patterns)
     - Split PDF with addresses
     - Multiple documents with ZIP
     - Multiple ZIPs with addresses
   - **Advanced Patterns** (10 patterns)
     - Document merge
     - Using jobOptions instead of jobTemplate
     - URL document source
     - Payment methods
     - Tags
     - Return address
     - Stored resources (documentId, addressListId)
     - Custom merge fields
     - Complex combinations

4. **Add educational metadata**
   - Friendly pattern names
   - Descriptions explaining what each shows
   - Use case examples

5. **Output two collections**
   - Placeholder version (from linked collection - has `<string>`, `<oneOf>`)
   - Examples version (from test collection - has realistic data)

---

## Implementation Plan

### New Script: `generate_getting_started_from_linked.py`

```python
#!/usr/bin/env python3
"""
Generate Getting Started collection from the linked collection.

This ensures Getting Started has the same structure as linked/test collections
(generated from EBNF), just reorganized for educational purposes.
"""

import json
from typing import Dict, List, Any

# Educational categorization
PATTERNS = [
    {
        "category": "Most Frequently Used",
        "description": "The most common API calls for everyday use",
        "patterns": [
            {
                "endpoint": "/jobs/submit/single/doc",
                "name": "Single recipient - basic job submission",
                "description": "Submit a single document to one recipient using jobTemplate",
                "highlight": "docSourceAll (requestId variant), recipientAddressSource (singleAddress variant)"
            },
            {
                "endpoint": "/jobs/submit/single/doc",
                "name": "Mail merge - multiple recipients",
                "description": "Submit a single document to multiple recipients",
                "highlight": "recipientAddressSource (addressList variant) with custom merge fields"
            },
            {
                "endpoint": "/jobs/submit/single/pdf/addressCapture",
                "name": "Address capture - PDF with embedded addresses",
                "description": "Submit PDF where addresses are extracted from the document",
                "highlight": "No recipientAddressSource needed - addresses in PDF"
            }
        ]
    },
    {
        "category": "Bulk Operations",
        "description": "High-volume processing for multiple documents or recipients",
        "patterns": [
            # ... more patterns
        ]
    },
    {
        "category": "Advanced Patterns",
        "description": "Advanced features and edge cases",
        "patterns": [
            # ... more patterns
        ]
    }
]

def read_linked_collection(filepath: str) -> Dict:
    """Read the linked collection generated from EBNF."""
    with open(filepath, 'r') as f:
        return json.load(f)

def find_endpoint_in_collection(collection: Dict, endpoint_path: str) -> Dict:
    """Find an endpoint request in the flat collection."""
    # Search through collection.item[] for matching endpoint
    for item in collection.get('item', []):
        if endpoint_path in item.get('name', ''):
            return item
    return None

def create_pattern_request(source_request: Dict, pattern: Dict) -> Dict:
    """Create a Getting Started request from a source request."""
    # Clone the request
    request = json.loads(json.dumps(source_request))

    # Update name and description for educational purposes
    request['name'] = pattern['name']
    if 'request' in request and 'description' in pattern:
        request['request']['description'] = f"{pattern['description']}\n\n{pattern.get('highlight', '')}"

    return request

def generate_getting_started_collection(
    linked_collection_path: str,
    output_path: str
):
    """Generate Getting Started collection from linked collection."""

    # Read source collection
    linked = read_linked_collection(linked_collection_path)

    # Create new collection
    getting_started = {
        "info": {
            "name": "C2M API v2 - Getting Started",
            "description": "Educational collection organized by usage patterns to help new users get started with the C2M API.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    # Build categorized structure
    for category_def in PATTERNS:
        category_folder = {
            "name": category_def['category'],
            "description": category_def['description'],
            "item": []
        }

        for pattern in category_def['patterns']:
            # Find the source request in linked collection
            source_request = find_endpoint_in_collection(linked, pattern['endpoint'])

            if source_request:
                # Create educational version
                pattern_request = create_pattern_request(source_request, pattern)
                category_folder['item'].append(pattern_request)

        getting_started['item'].append(category_folder)

    # Write output
    with open(output_path, 'w') as f:
        json.dump(getting_started, f, indent=2)

    print(f"✅ Generated Getting Started collection: {output_path}")

if __name__ == "__main__":
    generate_getting_started_collection(
        "postman/generated/c2mapiv2-linked-collection-flat.json",
        "postman/generated/c2mapiv2-getting-started-collection.json"
    )
```

---

## Benefits of This Approach

### 1. **Guaranteed Consistency**
- Getting Started has exact same structure as linked/test collections
- All field names match current EBNF
- All optional fields included
- No hardcoded field names to get out of sync

### 2. **Maintainability**
- When EBNF changes, Getting Started automatically gets the changes
- No need to manually update hardcoded request bodies
- Single source of truth (EBNF) drives everything

### 3. **Flexibility**
- Easy to add new patterns (just add to PATTERNS list)
- Easy to reorganize categories
- Can generate multiple versions (placeholder vs examples) from same logic

### 4. **Educational Value**
- Shows real API structure (not simplified)
- Users see all optional fields and learn what's available
- Organized by common use cases for easier learning

---

## Migration Path

### Phase 1: Create New Script
1. Create `generate_getting_started_from_linked.py`
2. Test with current linked collection
3. Verify output has correct field names

### Phase 2: Update Makefile
```makefile
.PHONY: postman-generate-getting-started-collection
postman-generate-getting-started-collection: postman-api-linked-collection-generate
	@echo "📚 Generating Getting Started collection from linked collection..."
	@$(VENV_PYTHON) scripts/active/generate_getting_started_from_linked.py
	@echo "✅ Getting Started collection generated"
```

**Key Change**: Add dependency `postman-api-linked-collection-generate` to ensure linked collection exists first.

### Phase 3: Deprecate Old Script
1. Rename `generate_getting_started_collection.py` → `generate_getting_started_collection_OLD.py`
2. Add deprecation warning
3. Remove after testing new version

---

## Alternative Approach: Modify Existing Script

If you want to keep the current script structure, you could modify it to:

1. **Read from OpenAPI spec** instead of hardcoding
2. **Use same field extraction logic** as openapi-to-postmanv2

But this duplicates the OpenAPI parsing logic and is more complex. **Reading from linked collection is simpler and more reliable.**

---

## Questions to Clarify

1. **Pattern Selection**: Which specific patterns should Getting Started show?
   - Current script has 16 patterns (3 frequent + 3 bulk + 10 advanced)
   - Should we keep all 16 or reduce for simplicity?

2. **Variants**: Should each pattern show one specific variant or multiple?
   - Example: `docSourceAll` has 5 variants (documentId, requestId, url, zipDocumentId, zipRequestId)
   - Should "Single recipient" pattern show all 5 variants or just requestId?

3. **Optional Fields**: Should we show ALL optional fields or just common ones?
   - Current EBNF has 5 optional fields per endpoint
   - Should Getting Started show all 5 or just the most common (e.g., jobTemplate, paymentDetails)?

4. **Folder Structure**: Should Getting Started be flat or nested?
   - Option A: Flat - All patterns at same level with category prefixes
   - Option B: Nested - Category folders → Pattern requests

---

## Recommendation

**Use the new script approach** (generate from linked collection):
- Simpler implementation
- Guaranteed consistency with EBNF
- Easier to maintain
- Shows complete API surface (all optional fields)

**Keep all patterns** (16 total):
- Users can explore different use cases
- Shows breadth of API capabilities
- Can always create "Quick Start" subset later

**Show all optional fields**:
- Helps users discover features
- Matches linked/test collections
- Educational value of showing what's possible

**Use nested folder structure**:
- Better organization in Postman UI
- Easier to navigate by use case
- Matches current Getting Started structure

---

## Next Steps

1. Review this proposal
2. Clarify any questions above
3. Create new script `generate_getting_started_from_linked.py`
4. Test with current linked collection
5. Update Makefile dependencies
6. Deploy to Postman and verify

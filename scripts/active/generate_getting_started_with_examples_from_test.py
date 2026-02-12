#!/usr/bin/env python3
"""
Generate Getting Started collection with examples from the test collection.

This ensures the examples version has the same field names and structure as the
test collection (generated from EBNF with realistic faker data), just reorganized
for educational purposes.

The test collection is the source of truth for realistic example data. This script
reorganizes those endpoints into educational categories.
"""

import json
import sys
from typing import Dict, List, Any
from pathlib import Path

# Educational pattern organization (16 patterns across 3 categories)
# Same patterns as placeholder version, but will have realistic data
PATTERNS = [
    {
        "category": "Most Frequently Used",
        "description": "The most common API calls for everyday use",
        "patterns": [
            {
                "endpoint": "/jobs/submit/single/doc",
                "name": "Single recipient - basic job submission",
                "description": "Submit a single document to one recipient using jobTemplate",
                "highlight": "Uses docSourceAll (requestId variant) and recipientAddressSource (singleAddress variant) with realistic test data"
            },
            {
                "endpoint": "/jobs/submit/single/doc",
                "name": "Mail merge - multiple recipients",
                "description": "Submit a single document to multiple recipients",
                "highlight": "Uses recipientAddressSource (addressList variant) with custom merge fields (foo1, foo2) - realistic addresses"
            },
            {
                "endpoint": "/jobs/submit/single/pdf/addressCapture",
                "name": "Address capture - PDF with embedded addresses",
                "description": "Submit PDF where addresses are extracted from the document",
                "highlight": "No recipientAddressSource needed - addresses are captured from PDF content"
            }
        ]
    },
    {
        "category": "Bulk Operations",
        "description": "High-volume processing for multiple documents or recipients",
        "patterns": [
            {
                "endpoint": "/jobs/submit/single/pdf/split/addressCapture",
                "name": "Split PDF with address capture",
                "description": "Split a multi-page PDF and capture addresses from each section",
                "highlight": "Uses pdfSplitJobsNoAddress (startPage/endPage without recipientAddressSource) with realistic page ranges"
            },
            {
                "endpoint": "/jobs/submit/single/pdf/split",
                "name": "Split PDF with specified addresses",
                "description": "Split a multi-page PDF and provide recipient address for each section",
                "highlight": "Uses pdfSplitJobsWithAddress (startPage/endPage WITH recipientAddressSource) - realistic data"
            },
            {
                "endpoint": "/jobs/submit/multi/zip/addressCapture",
                "name": "Multiple documents from ZIP with address capture",
                "description": "Submit multiple documents from a ZIP file with embedded addresses",
                "highlight": "Uses zipDocumentSource (zip-only document sources) with realistic IDs"
            }
        ]
    },
    {
        "category": "Advanced Patterns",
        "description": "Advanced features and edge cases for complex workflows",
        "patterns": [
            {
                "endpoint": "/jobs/submit/multi/doc/merge",
                "name": "Merge multiple documents",
                "description": "Combine multiple documents into one before mailing",
                "highlight": "Uses mergeDocumentSource (documentsToMerge array) with realistic document IDs"
            },
            {
                "endpoint": "/jobs/submit/single/doc",
                "name": "Using jobOptions instead of template",
                "description": "Specify job options directly instead of using a template",
                "highlight": "Uses jobOptions (documentClass, layout, etc.) instead of jobTemplate with realistic values"
            },
            {
                "endpoint": "/jobs/submit/single/doc",
                "name": "Using document URL instead of upload",
                "description": "Reference a document by URL instead of uploading",
                "highlight": "Uses docSourceAll (url variant) to fetch document from external source - realistic URL"
            },
            {
                "endpoint": "/jobs/submit/single/doc",
                "name": "Adding tags for organization",
                "description": "Add custom tags to track and organize jobs",
                "highlight": "Uses tags array (optional field) for job categorization with realistic tag examples"
            },
            {
                "endpoint": "/jobs/submit/single/doc",
                "name": "Naming an address list for reuse",
                "description": "Create a named address list that can be referenced in future jobs",
                "highlight": "Uses addressListName (optional field) to save address list for reuse with realistic name"
            },
            {
                "endpoint": "/jobs/submit/single/doc",
                "name": "Specifying payment method",
                "description": "Specify how the job should be paid for",
                "highlight": "Uses paymentDetails (optional field) with creditCard variant - realistic test card data"
            },
            {
                "endpoint": "/jobs/submit/multi/zip",
                "name": "Multiple documents from ZIP - specify addresses",
                "description": "Submit multiple documents from ZIP with specified addresses for each",
                "highlight": "Uses multiZipJobs array with docSourceZipFile and recipientAddressSource - realistic data"
            },
            {
                "endpoint": "/jobs/submit/multi/doc",
                "name": "Multiple separate documents",
                "description": "Submit multiple different documents with different recipients",
                "highlight": "Uses multiDocJobs array with docSourceAll and recipientAddressSource per job - realistic data"
            },
            {
                "endpoint": "/jobs/submit/single/doc",
                "name": "Using stored documentId",
                "description": "Reference a previously uploaded document by its ID",
                "highlight": "Uses docSourceAll (documentId variant) to reference stored document - realistic ID"
            },
            {
                "endpoint": "/jobs/submit/single/doc",
                "name": "Using saved addressListId",
                "description": "Reference a previously saved address list by its ID",
                "highlight": "Uses recipientAddressSource (addressListId variant) to reference stored list - realistic ID"
            }
        ]
    }
]


def read_test_collection(filepath: str) -> Dict:
    """Read the test collection with realistic faker-generated data."""
    with open(filepath, 'r') as f:
        return json.load(f)


def find_endpoint_in_collection(collection: Dict, endpoint_path: str) -> Dict:
    """
    Find an endpoint request in the test collection.

    The test collection has nested folders (jobs/submit/single/doc),
    so we search recursively through all nested items.
    """
    def search_items(items: list) -> Dict:
        """Recursively search through nested items"""
        for item in items:
            # Check if this item has a request with matching path
            if 'request' in item:
                request = item['request']
                if 'url' in request and 'path' in request['url']:
                    # Build path from components
                    path = '/' + '/'.join(request['url']['path'])
                    if path == endpoint_path:
                        return item

            # Check nested items (folders)
            if 'item' in item and isinstance(item['item'], list):
                result = search_items(item['item'])
                if result:
                    return result

        return None

    return search_items(collection.get('item', []))


def create_pattern_request(source_request: Dict, pattern: Dict) -> Dict:
    """
    Create a Getting Started request from a source request.

    This clones the source request (which has realistic faker data from test collection)
    and adds educational metadata from the pattern definition.
    """
    # Deep clone the request
    request = json.loads(json.dumps(source_request))

    # Update name and description for educational purposes
    request['name'] = pattern['name']

    # Enhanced description with pattern-specific information
    enhanced_description = f"{pattern['description']}\n\n{pattern.get('highlight', '')}"

    if 'request' in request and 'description' in request['request']:
        # Preserve existing description structure
        if isinstance(request['request']['description'], dict):
            request['request']['description']['content'] = enhanced_description
        else:
            request['request']['description'] = {
                "content": enhanced_description,
                "type": "text/plain"
            }

    return request


def generate_getting_started_with_examples(
    test_collection_path: str,
    output_path: str
):
    """
    Generate Getting Started collection with examples from test collection.

    The test collection has realistic faker-generated data. We reorganize
    those endpoints into educational categories with friendly names.
    """

    # Read source collection
    test = read_test_collection(test_collection_path)

    # Create new collection with educational structure
    getting_started = {
        "info": {
            "name": "C2M API v2 - Getting Started (With Examples)",
            "description": (
                "Educational collection with realistic test data organized by usage patterns "
                "to help new users get started with the C2M API.\n\n"
                "This collection demonstrates 16 common patterns across 3 categories:\n"
                "- Most Frequently Used (3 patterns)\n"
                "- Bulk Operations (3 patterns)\n"
                "- Advanced Patterns (10 patterns)\n\n"
                "All request bodies contain realistic example data (names, addresses, IDs) "
                "that can be used for immediate testing."
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    # Build categorized structure (nested folders)
    for category_def in PATTERNS:
        category_folder = {
            "name": category_def['category'],
            "description": category_def['description'],
            "item": []
        }

        for pattern in category_def['patterns']:
            # Find the source request in test collection
            source_request = find_endpoint_in_collection(test, pattern['endpoint'])

            if source_request:
                # Create educational version with realistic data
                pattern_request = create_pattern_request(source_request, pattern)
                category_folder['item'].append(pattern_request)
            else:
                print(f"WARNING: Endpoint not found: {pattern['endpoint']}", file=sys.stderr)

        getting_started['item'].append(category_folder)

    # Write output
    with open(output_path, 'w') as f:
        json.dump(getting_started, f, indent=2)

    print(f"Getting Started collection (with examples) generated: {output_path}")

    # Summary statistics
    total_patterns = sum(len(cat['patterns']) for cat in PATTERNS)
    print(f"Categories: {len(PATTERNS)}")
    print(f"Patterns: {total_patterns}")


if __name__ == "__main__":
    # Default paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    test_collection_path = project_root / "postman" / "generated" / "c2mapiv2-test-collection-with-examples.json"
    output_path = project_root / "postman" / "generated" / "c2mapiv2-getting-started-with-examples-collection.json"

    # Allow command-line override
    if len(sys.argv) > 1:
        test_collection_path = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])

    # Verify input exists
    if not test_collection_path.exists():
        print(f"ERROR: Test collection not found: {test_collection_path}", file=sys.stderr)
        sys.exit(1)

    # Generate collection
    generate_getting_started_with_examples(str(test_collection_path), str(output_path))

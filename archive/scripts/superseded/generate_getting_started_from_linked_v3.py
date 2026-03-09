#!/usr/bin/env python3
"""
Getting Started Collection Generator (v3) - Exact Body Definitions
===================================================================
Generates Getting Started collection using exact request body definitions
per pattern (not simplification from linked collection).

This ensures each pattern shows EXACTLY the fields it should demonstrate,
with no extra optional fields.

Usage:
    python3 generate_getting_started_from_linked_v3.py

Output:
    postman/generated/c2mapiv2-getting-started-collection.json
"""

import json
import sys
from pathlib import Path

# Exact request body definitions per pattern
# These show ONLY the fields needed to demonstrate each pattern
PATTERN_BODIES = {
    "single-recipient": {
        "jobTemplate": "<string>",
        "docSourceAll": "<oneOf>",
        "recipientAddressSource": "<oneOf>"
    },
    "mail-merge": {
        "jobTemplate": "<string>",
        "docSourceAll": "<oneOf>",
        "recipientAddressSource": "<oneOf>"
    },
    "address-capture": {
        "docSourceStandard": "<oneOf>"
    },
    "split-address-capture": {
        "docSourceStandard": "<oneOf>",
        "pdfSplitJobsNoAddress": [
            {
                "startPage": "<integer>",
                "endPage": "<integer>"
            }
        ]
    },
    "multi-zip-address-capture": {
        "zipDocumentSource": "<oneOf>"
    },
    "split-with-addresses": {
        "docSourceStandard": "<oneOf>",
        "pdfSplitJobsWithAddress": [
            {
                "startPage": "<integer>",
                "endPage": "<integer>",
                "recipientAddressSource": "<oneOf>"
            }
        ]
    },
    "merge-docs": {
        "mergeDocumentSource": "<oneOf>",
        "recipientAddressSource": "<oneOf>"
    }
}

# Pattern metadata (category and descriptions)
PATTERNS = {
    "Most Frequently Used": [
        {
            "endpoint": "/jobs/submit/single/doc",
            "name": "/jobs/submit/single/doc - single recipient",
            "description": "Submit a single document to one recipient using jobTemplate",
            "body_key": "single-recipient"
        },
        {
            "endpoint": "/jobs/submit/single/doc",
            "name": "/jobs/submit/single/doc - mail merge",
            "description": "Submit a single document to multiple recipients (mail merge)",
            "body_key": "mail-merge"
        },
        {
            "endpoint": "/jobs/submit/single/pdf/addressCapture",
            "name": "/jobs/submit/single/pdf/addressCapture",
            "description": "Submit PDF where addresses are captured from the document itself",
            "body_key": "address-capture"
        }
    ],
    "Bulk": [
        {
            "endpoint": "/jobs/submit/single/pdf/split/addressCapture",
            "name": "/jobs/submit/single/pdf/split/addressCapture",
            "description": "Split a multi-page PDF and capture addresses from each section",
            "body_key": "split-address-capture"
        },
        {
            "endpoint": "/jobs/submit/multiple/zip/addressCapture",
            "name": "/jobs/submit/multiple/zip/addressCapture - using zip file",
            "description": "Submit multiple jobs from zip file with address capture",
            "body_key": "multi-zip-address-capture"
        },
        {
            "endpoint": "/jobs/submit/single/pdf/split",
            "name": "/jobs/submit/single/pdf/split",
            "description": "Split a multi-page PDF and specify recipient for each section",
            "body_key": "split-with-addresses"
        }
    ],
    "Less frequently used": [
        {
            "endpoint": "/jobs/submit/multiple/doc/merge",
            "name": "/jobs/submit/multiple/doc/merge",
            "description": "Merge multiple documents then submit to one recipient",
            "body_key": "merge-docs"
        }
    ]
}

def create_postman_item(pattern):
    """Create a Postman collection item from pattern definition"""
    # Get exact body for this pattern
    body_key = pattern["body_key"]
    body = PATTERN_BODIES.get(body_key, {})

    # Parse endpoint path into components
    path_parts = pattern["endpoint"].strip("/").split("/")

    return {
        "name": pattern["name"],
        "request": {
            "name": pattern["name"],
            "description": {
                "content": pattern["description"],
                "type": "text/plain"
            },
            "url": {
                "path": path_parts,
                "host": ["{{baseUrl}}"],
                "query": [],
                "variable": []
            },
            "header": [
                {
                    "key": "Content-Type",
                    "value": "application/json"
                },
                {
                    "key": "Accept",
                    "value": "application/json"
                }
            ],
            "method": "POST",
            "body": {
                "mode": "raw",
                "raw": json.dumps(body, indent=2),
                "options": {
                    "raw": {
                        "headerFamily": "json",
                        "language": "json"
                    }
                }
            },
            "auth": None
        },
        "response": []
    }

def generate_getting_started_collection():
    """Generate Getting Started collection with exact body definitions"""
    folders = []

    for category_name, patterns in PATTERNS.items():
        folder = {
            "name": category_name,
            "item": []
        }

        for pattern in patterns:
            item = create_postman_item(pattern)
            folder["item"].append(item)

        folders.append(folder)

    # Build final collection
    collection = {
        "info": {
            "name": "C2M API v2 - Getting Started",
            "description": "Educational collection showing common usage patterns for the C2M API v2. Organized by frequency of use.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": folders
    }

    return collection

def main():
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    output_path = project_root / "postman/generated/c2mapiv2-getting-started-collection.json"

    print("Generating Getting Started collection...")
    collection = generate_getting_started_collection()

    print(f"Writing to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(collection, f, indent=2)

    # Stats
    total_items = sum(len(folder["item"]) for folder in collection["item"])
    print(f"\nSUCCESS: Generated Getting Started collection")
    print(f"  Categories: {len(collection['item'])}")
    print(f"  Total patterns: {total_items}")
    print(f"  Output: {output_path}")

    # Show first pattern body for verification
    if collection["item"] and collection["item"][0]["item"]:
        first_item = collection["item"][0]["item"][0]
        body_str = first_item["request"]["body"]["raw"]
        print(f"\nFirst pattern body:")
        print(body_str)

if __name__ == "__main__":
    main()

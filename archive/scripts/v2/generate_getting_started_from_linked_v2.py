#!/usr/bin/env python3
"""
Getting Started Collection Generator (v2) - Read from Linked Collection
========================================================================
Generates Getting Started collection by reading from the linked collection
(which is correctly generated from EBNF), then reorganizing into educational
categories.

This ensures:
- Correct field names (docSourceAll not documentSource)
- Correct structure (matches EBNF exactly)
- All required fields present
- Automatic sync with EBNF changes

Usage:
    python3 generate_getting_started_from_linked_v2.py

Input:
    postman/generated/c2mapiv2-linked-collection-flat.json

Output:
    postman/generated/c2mapiv2-getting-started-collection.json
"""

import json
import sys
from pathlib import Path

# Educational pattern definitions
# Maps endpoint paths to pattern metadata
PATTERN_METADATA = {
    # Most Frequently Used (3 patterns)
    "/jobs/submit/single/doc": [
        {
            "name": "/jobs/submit/single/doc - single recipient",
            "description": "Submit a single document to one recipient using jobTemplate",
            "category": "Most Frequently Used",
            "simplify": ["docSourceAll", "recipientAddressSource"]  # Keep only required fields
        },
        {
            "name": "/jobs/submit/single/doc - mail merge",
            "description": "Submit a single document to multiple recipients (mail merge)",
            "category": "Most Frequently Used",
            "simplify": ["docSourceAll", "recipientAddressSource"]
        }
    ],
    "/jobs/submit/single/pdf/addressCapture": [
        {
            "name": "/jobs/submit/single/pdf/addressCapture",
            "description": "Submit PDF where addresses are captured from the document itself",
            "category": "Most Frequently Used",
            "simplify": ["docSourceStandard"]
        }
    ],

    # Bulk Operations (3 patterns)
    "/jobs/submit/single/pdf/split/addressCapture": [
        {
            "name": "/jobs/submit/single/pdf/split/addressCapture",
            "description": "Split a multi-page PDF and capture addresses from each section",
            "category": "Bulk",
            "simplify": ["docSourceStandard", "pdfSplitJobsNoAddress"]
        }
    ],
    "/jobs/submit/multiple/zip/addressCapture": [
        {
            "name": "/jobs/submit/multiple/zip/addressCapture - using zip file",
            "description": "Submit multiple jobs from zip file with address capture",
            "category": "Bulk",
            "simplify": ["zipDocumentSource"]
        }
    ],
    "/jobs/submit/single/pdf/split": [
        {
            "name": "/jobs/submit/single/pdf/split",
            "description": "Split a multi-page PDF and specify recipient for each section",
            "category": "Bulk",
            "simplify": ["docSourceStandard", "pdfSplitJobsWithAddress"]
        }
    ],

    # Advanced Patterns (10 patterns)
    "/jobs/submit/multiple/doc/merge": [
        {
            "name": "/jobs/submit/multiple/doc/merge",
            "description": "Merge multiple documents then submit to one recipient",
            "category": "Less frequently used",
            "simplify": ["mergeDocumentSource", "recipientAddressSource"]
        }
    ]
}

def read_linked_collection(filepath):
    """Read the linked collection JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Linked collection not found: {filepath}")
        print("Run 'make postman-create-linked-collection' first")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in linked collection: {e}")
        sys.exit(1)

def extract_path_from_item(item):
    """Extract endpoint path from Postman item"""
    try:
        path_parts = item["request"]["url"]["path"]
        return "/" + "/".join(path_parts)
    except (KeyError, TypeError):
        return None

def simplify_request_body(body_raw, simplify_fields):
    """
    Simplify request body to only show specified fields with placeholders.
    Keeps the structure but removes extra optional fields for clarity.
    """
    try:
        body = json.loads(body_raw)

        # For basic patterns, only keep the simplified fields
        simplified = {}
        for field in simplify_fields:
            if field in body:
                simplified[field] = body[field]

        # Always keep jobTemplate if present (shows template pattern)
        if "jobTemplate" in body and "jobTemplate" not in simplify_fields:
            simplified["jobTemplate"] = body["jobTemplate"]

        return json.dumps(simplified, indent=2)
    except:
        return body_raw

def create_getting_started_item(linked_item, pattern_meta):
    """Create a Getting Started item from a linked collection item"""
    # Deep copy the item
    new_item = json.loads(json.dumps(linked_item))

    # Update name and description
    new_item["name"] = pattern_meta["name"]
    if "request" in new_item and "description" in new_item["request"]:
        new_item["request"]["description"]["content"] = pattern_meta["description"]

    # Simplify request body if specified
    if "simplify" in pattern_meta and "request" in new_item and "body" in new_item["request"]:
        body_raw = new_item["request"]["body"].get("raw", "")
        if body_raw:
            new_item["request"]["body"]["raw"] = simplify_request_body(
                body_raw,
                pattern_meta["simplify"]
            )

    # Remove response examples (keep request clean for learning)
    if "response" in new_item:
        new_item["response"] = []

    return new_item

def organize_by_category(items_with_meta):
    """Organize items into category folders"""
    categories = {
        "Most Frequently Used": [],
        "Bulk": [],
        "Less frequently used": []
    }

    for item, meta in items_with_meta:
        category = meta["category"]
        if category in categories:
            categories[category].append(item)

    # Build folder structure
    folders = []
    for category_name, items in categories.items():
        if items:  # Only create folder if has items
            folders.append({
                "name": category_name,
                "item": items
            })

    return folders

def generate_getting_started_collection(linked_collection):
    """Generate Getting Started collection from linked collection"""

    # Find all endpoints in linked collection
    endpoint_map = {}
    for item in linked_collection.get("item", []):
        path = extract_path_from_item(item)
        if path:
            endpoint_map[path] = item

    # Generate Getting Started items based on pattern metadata
    items_with_meta = []
    for endpoint_path, patterns in PATTERN_METADATA.items():
        if endpoint_path in endpoint_map:
            linked_item = endpoint_map[endpoint_path]
            for pattern_meta in patterns:
                new_item = create_getting_started_item(linked_item, pattern_meta)
                items_with_meta.append((new_item, pattern_meta))
        else:
            print(f"WARNING: Endpoint not found in linked collection: {endpoint_path}")

    # Organize into categories
    folders = organize_by_category(items_with_meta)

    # Build final collection
    getting_started = {
        "info": {
            "name": "C2M API v2 - Getting Started",
            "description": "Educational collection showing common usage patterns for the C2M API v2. Organized by frequency of use.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": folders
    }

    return getting_started

def main():
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    linked_path = project_root / "postman/generated/c2mapiv2-linked-collection-flat.json"
    output_path = project_root / "postman/generated/c2mapiv2-getting-started-collection.json"

    print("Reading linked collection...")
    linked_collection = read_linked_collection(linked_path)

    print("Generating Getting Started collection...")
    getting_started = generate_getting_started_collection(linked_collection)

    print(f"Writing to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(getting_started, f, indent=2)

    # Stats
    total_items = sum(len(folder["item"]) for folder in getting_started["item"])
    print(f"\nSUCCESS: Generated Getting Started collection")
    print(f"  Categories: {len(getting_started['item'])}")
    print(f"  Total patterns: {total_items}")
    print(f"  Output: {output_path}")

if __name__ == "__main__":
    main()

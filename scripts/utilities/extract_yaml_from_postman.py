#!/usr/bin/env python3
"""
Extract examples from REST API V2 Postman collection and convert to YAML catalog format.

This script reads a Postman collection JSON file and transforms it into the same
YAML structure as config/curated-examples-catalog.yaml.

Usage:
    python3 extract_yaml_from_postman.py \
        --input "REST API V2.postman_collection (3).json" \
        --output getting-started-curated-test.yaml
"""

import json
import yaml
import sys
from pathlib import Path

def extract_oneof_variant(obj, parent_key=""):
    """
    Recursively detect oneOf variant selection by examining object structure.

    Returns dict of field → variant mappings.
    Example: {"docSourceAll": "documentId", "recipientAddressSource": "singleAddress"}
    """
    selections = {}

    if not isinstance(obj, dict):
        return selections

    # Known oneOf fields and their variant indicators
    oneof_fields = {
        "documentSource": ["documentId", "requestId", "url", "documentsToMerge"],
        "docSourceAll": ["documentId", "requestId", "url", "zipDocumentId", "zipRequestId"],
        "recipientAddressSource": ["singleAddress", "addressList", "addressListId", "addressListName"],
        "paymentDetails": ["creditCard", "ach", "invoice"]
    }

    for key, value in obj.items():
        # Check if this is a oneOf field
        if key in oneof_fields:
            if isinstance(value, dict):
                # Which variant is present?
                for variant in oneof_fields[key]:
                    if variant in value:
                        selections[key] = variant
                        break

        # Recurse into nested objects
        if isinstance(value, dict):
            nested = extract_oneof_variant(value, key)
            selections.update(nested)

    return selections

def extract_leaf_values(obj, parent_key="", exclude_keys=None):
    """
    Extract all leaf (primitive) values from nested object.

    Returns flat dict of field → value mappings.
    Skips oneOf wrapper objects (they're in 'select' section).
    """
    if exclude_keys is None:
        exclude_keys = set()

    values = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{parent_key}.{key}" if parent_key else key

            # Skip oneOf wrapper keys (already in select section)
            if key in ["documentSource", "docSourceAll", "recipientAddressSource", "paymentDetails"]:
                # Recurse into the variant object
                if isinstance(value, dict):
                    nested = extract_leaf_values(value, "", exclude_keys)
                    values.update(nested)
            elif isinstance(value, (str, int, float, bool)):
                # Leaf value
                if not value or str(value).startswith("<"):
                    # Skip placeholders like "<String>"
                    continue
                values[key] = value
            elif isinstance(value, list):
                # Array of primitives or objects
                values[key] = value
            elif isinstance(value, dict):
                # Nested object - recurse
                nested = extract_leaf_values(value, full_key, exclude_keys)
                values.update(nested)

    return values

def parse_postman_item(item, group_name):
    """
    Parse a Postman collection item into YAML example format.

    Returns dict with: name, method, path, group, tags, description, select, values
    """
    # Extract basic info
    name = item.get("name", "Unnamed")
    request = item.get("request", {})
    method = request.get("method", "POST")

    # Extract path from URL
    url = request.get("url", {})
    if isinstance(url, dict):
        path_parts = url.get("path", [])
        # Skip "molpro" and "v2" parts, keep everything after
        path = "/" + "/".join([p for p in path_parts if p not in ["molpro", "v2"]])
    else:
        path = "/unknown"

    # Parse request body
    body = request.get("body", {})
    raw_body = body.get("raw", "{}")

    try:
        body_obj = json.loads(raw_body)
    except json.JSONDecodeError as e:
        print(f"WARNING: Could not parse JSON body for {name}", file=sys.stderr)
        print(f"  Error: {e}", file=sys.stderr)
        print(f"  Raw body (first 500 chars): {raw_body[:500]}", file=sys.stderr)
        body_obj = {}

    # Extract oneOf selections
    select = extract_oneof_variant(body_obj)

    # Extract leaf values
    values = extract_leaf_values(body_obj)

    # Generate tags based on group
    tags = []
    if "Most Frequently Used" in group_name:
        tags = ["getting-started", "frequent", "basic"]
    elif "Bulk" in group_name:
        tags = ["bulk", "batch"]
    elif "Less frequently used" in group_name:
        tags = ["advanced"]

    # Description from name (clean up)
    description = name.replace("/jobs/submit/", "").replace("/", " - ")

    return {
        "name": name,
        "method": method,
        "path": path,
        "group": group_name.lower().replace(" ", "-"),
        "tags": tags,
        "description": description,
        "select": select,
        "values": values
    }

def extract_groups(collection):
    """
    Extract group definitions from Postman collection folders.

    Returns list of dicts with: logical_name, display_name, order, description
    """
    groups = []
    items = collection.get("item", [])

    for idx, folder in enumerate(items, start=1):
        folder_name = folder.get("name", f"Group {idx}")

        # Map folder names to logical names
        logical_name = folder_name.lower().replace(" ", "-")

        # Generate description based on folder name
        if "most frequently" in folder_name.lower():
            description = "The most common API usage patterns"
        elif "bulk" in folder_name.lower():
            description = "Processing multiple documents or recipients efficiently"
        else:
            description = "Specialized use cases and advanced features"

        groups.append({
            "logical_name": logical_name,
            "display_name": folder_name,
            "order": idx,
            "description": description
        })

    return groups

def extract_examples(collection):
    """
    Extract all examples from Postman collection folders.

    Returns list of example dicts.
    """
    examples = []
    items = collection.get("item", [])

    for folder in items:
        folder_name = folder.get("name", "Unknown")
        group_name = folder_name.lower().replace(" ", "-")

        # Process each request in the folder
        for request_item in folder.get("item", []):
            example = parse_postman_item(request_item, group_name)
            examples.append(example)

    return examples

def main():
    # Hard-coded paths for this use case
    input_file = Path("/Users/frankserrao/Dropbox/Customers/c2m/C2M-General/Invoices/022026/REST API V2.postman_collection (3).json")
    output_file = Path("/Users/frankserrao/Dropbox/Customers/c2m/projects/c2m-api/C2M_API_v2/c2m-api-v2-postman/config/getting-started-curated-test.yaml")

    # Read Postman collection
    print(f"Reading Postman collection from {input_file}...", file=sys.stderr)
    with open(input_file, 'r') as f:
        collection = json.load(f)

    # Extract groups and examples
    print("Extracting groups...", file=sys.stderr)
    groups = extract_groups(collection)
    print(f"Found {len(groups)} groups", file=sys.stderr)

    print("Extracting examples...", file=sys.stderr)
    examples = extract_examples(collection)
    print(f"Found {len(examples)} examples", file=sys.stderr)

    # Build YAML structure
    catalog = {
        "groups": groups,
        "examples": examples
    }

    # Write YAML output
    print(f"Writing YAML catalog to {output_file}...", file=sys.stderr)
    with open(output_file, 'w') as f:
        # Add header comment
        f.write("# Getting Started - Curated Examples Catalog (Extracted from Postman Collection)\n")
        f.write("# Pattern: Read structure from Postman, write to YAML catalog\n")
        f.write("# Source: REST API V2.postman_collection (3).json\n")
        f.write("\n")

        # Write YAML
        yaml.dump(catalog, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"SUCCESS: Created {output_file}", file=sys.stderr)
    print(f"  Groups: {len(groups)}", file=sys.stderr)
    print(f"  Examples: {len(examples)}", file=sys.stderr)

if __name__ == "__main__":
    main()

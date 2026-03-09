#!/usr/bin/env python3
"""
Extract Template from Bootstrap Postman Collection

This script reads a Postman collection (customer-provided bootstrap) and extracts
a template YAML that defines collection structure, folders, endpoints, and field selections.

The template becomes the editable source for generating Getting Started collections.
The OpenAPI spec (generated from EBNF) provides the metadata for validation and types.

Usage:
    python3 extract_template_from_collection.py \
        --bootstrap postman-exports/REST\ API\ V2.postman_collection.json \
        --openapi openapi/c2mapiv2-openapi-spec-base.yaml \
        --template-output config/getting-started-template.yaml

Architecture:
- EBNF Data Dictionary: Single source of truth
- OpenAPI Spec: Complete schema (types, oneOf variants, validation)
- Linked Collection: Canonical request structures (all fields)
- Bootstrap Collection: Customer example (folder structure + field selections)
- Template YAML: Editable definition of what to generate

Author: Claude Code
Date: 2026-03-08
"""

import json
import yaml
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

def load_json(filepath: str) -> Dict:
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_yaml(data: Dict, filepath: str, header_comment: str = ""):
    """Save data to YAML file with optional header comment."""
    with open(filepath, 'w') as f:
        if header_comment:
            f.write(header_comment)
            f.write("\n")
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

def extract_collection_metadata(collection: Dict) -> Dict:
    """Extract collection-level metadata."""
    info = collection.get("info", {})
    return {
        "name": info.get("name", "Unnamed Collection"),
        "description": info.get("description", ""),
        "schema": info.get("schema", "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"),
        "_postman_id": info.get("_postman_id", "")
    }

def extract_groups(collection: Dict) -> List[Dict]:
    """
    Extract folder structure as groups.

    Returns list of group definitions with:
    - logical_name (kebab-case folder name)
    - display_name (original folder name)
    - order (1-indexed position)
    - description (generated or extracted)
    """
    groups = []
    items = collection.get("item", [])

    for idx, folder in enumerate(items, start=1):
        folder_name = folder.get("name", f"Group {idx}")

        # Generate logical name (kebab-case)
        logical_name = folder_name.lower().replace(" ", "-")

        # Generate description based on folder name
        description = folder.get("description", "")
        if not description:
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

def extract_path_from_url(url: Any) -> str:
    """
    Extract path from Postman URL object.

    Normalizes paths to match EBNF/OpenAPI spec format.
    Bootstrap collection may have inconsistent paths (e.g. /multiple/ vs /multi/).
    """
    if isinstance(url, dict):
        path_parts = url.get("path", [])
        # Filter out variable placeholders and join
        path = "/" + "/".join([p for p in path_parts if p not in ["molpro", "v2", "{{baseUrl}}"]])
    elif isinstance(url, str):
        path = url
    else:
        path = "/unknown"

    # Normalize path to match EBNF/OpenAPI spec
    # Bootstrap collection uses /multiple/ but EBNF uses /multi/
    path = path.replace("/multiple/", "/multi/")

    return path

def detect_oneof_selections(body_obj: Dict) -> Dict:
    """
    Detect oneOf variant selections in request body.

    Returns dict mapping oneOf field → selected variant.
    Example: {"docSourceAll": "documentId", "recipientAddressSource": "singleAddress"}
    """
    selections = {}

    # Known oneOf fields and their possible variants
    oneof_fields = {
        "documentSource": ["documentId", "requestId", "url"],
        "docSourceAll": ["documentId", "requestId", "url", "zipDocumentId", "zipRequestId"],
        "recipientAddressSource": ["singleAddress", "addressList", "addressListId", "addressListName"],
        "paymentDetails": ["creditCard", "ach", "invoice"],
        "documentsToMerge": ["documentIds", "requestIds"]
    }

    def recurse_detect(obj, parent_key=""):
        """Recursively detect oneOf selections."""
        if not isinstance(obj, dict):
            return

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
                recurse_detect(value, key)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        recurse_detect(item, key)

    recurse_detect(body_obj)
    return selections

def extract_field_values(body_obj: Dict, oneof_selections: Dict) -> Dict:
    """
    Extract all leaf field values from request body.

    Skips oneOf wrapper objects (those are in 'select' section).
    Returns flat dict of field → type/placeholder.
    """
    values = {}

    # Fields that are oneOf wrappers (skip these)
    oneof_wrapper_keys = set(oneof_selections.keys())

    def recurse_extract(obj, parent_key=""):
        """Recursively extract leaf values."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{parent_key}.{key}" if parent_key else key

                # Skip oneOf wrapper keys
                if key in oneof_wrapper_keys:
                    # But recurse into the selected variant
                    if isinstance(value, dict):
                        recurse_extract(value, "")
                elif isinstance(value, (str, int, float, bool)):
                    # Leaf value - store the placeholder/type
                    values[key] = value
                elif isinstance(value, list):
                    # Array - store it
                    values[key] = value
                elif isinstance(value, dict):
                    # Nested object - recurse
                    recurse_extract(value, full_key)

    recurse_extract(body_obj)
    return values

def extract_examples(collection: Dict, groups: List[Dict]) -> List[Dict]:
    """
    Extract all examples from collection folders.

    Returns list of example definitions with:
    - name, method, path, group
    - description
    - select (oneOf variant selections)
    - values (field placeholders)
    """
    examples = []
    items = collection.get("item", [])

    # Map folder names to logical group names
    group_map = {g["display_name"]: g["logical_name"] for g in groups}

    for folder in items:
        folder_name = folder.get("name", "Unknown")
        group_name = group_map.get(folder_name, folder_name.lower().replace(" ", "-"))

        # Process each request in the folder
        for request_item in folder.get("item", []):
            # Extract basic info
            name = request_item.get("name", "Unnamed")
            request = request_item.get("request", {})
            method = request.get("method", "POST")

            # Extract path
            url = request.get("url", {})
            path = extract_path_from_url(url)

            # Extract description
            desc_obj = request.get("description", {})
            if isinstance(desc_obj, dict):
                description = desc_obj.get("content", "")
            elif isinstance(desc_obj, str):
                description = desc_obj
            else:
                description = ""

            # Parse request body
            body = request.get("body", {})
            raw_body = body.get("raw", "{}")

            try:
                body_obj = json.loads(raw_body)
            except json.JSONDecodeError:
                print(f"WARNING: Could not parse JSON body for {name}", file=sys.stderr)
                body_obj = {}

            # Detect oneOf selections
            select = detect_oneof_selections(body_obj)

            # Extract field values/placeholders
            values = extract_field_values(body_obj, select)

            # Build example definition
            example = {
                "name": name,
                "method": method,
                "path": path,
                "group": group_name,
                "tags": [],  # User can add tags manually
                "description": description if description else name,
                "select": select,
                "values": values
            }

            examples.append(example)

    return examples

def generate_template(bootstrap_collection: Dict, openapi_spec_path: str, linked_collection_path: str) -> Dict:
    """
    Generate template YAML structure from bootstrap collection.

    Template is editable and defines:
    - Collection metadata (name, description)
    - Schema references (OpenAPI, Linked Collection)
    - Groups (folder hierarchy)
    - Examples (endpoint + field selections)
    """
    # Extract collection metadata
    metadata = extract_collection_metadata(bootstrap_collection)

    # Override name to match desired output
    collection_name = "C2M API v2 - Getting Started"
    collection_description = "Educational collection showing common usage patterns for the C2M API v2. Organized by frequency of use."

    # Extract groups
    groups = extract_groups(bootstrap_collection)

    # Extract examples
    examples = extract_examples(bootstrap_collection, groups)

    # Build template structure
    template = {
        "collection": {
            "name": collection_name,
            "description": collection_description,
            "version": "1.0.0"
        },
        "schema_references": {
            "openapi_spec": openapi_spec_path,
            "linked_collection": linked_collection_path,
            "note": "OpenAPI spec provides types, oneOf variants, and validation. Linked collection provides canonical request structures."
        },
        "groups": groups,
        "examples": examples
    }

    return template


def main():
    parser = argparse.ArgumentParser(
        description="Extract template from bootstrap Postman collection (metadata from OpenAPI spec)"
    )
    parser.add_argument(
        "--bootstrap",
        required=True,
        help="Path to bootstrap Postman collection JSON"
    )
    parser.add_argument(
        "--openapi",
        default="openapi/c2mapiv2-openapi-spec-base.yaml",
        help="Path to OpenAPI spec (for validation/types reference)"
    )
    parser.add_argument(
        "--linked",
        default="postman/generated/c2mapiv2-linked-collection-flat.json",
        help="Path to linked collection (canonical structure reference)"
    )
    parser.add_argument(
        "--template-output",
        default="config/getting-started-template.yaml",
        help="Output path for template YAML"
    )

    args = parser.parse_args()

    # Load bootstrap collection
    print(f"Loading bootstrap collection from {args.bootstrap}...", file=sys.stderr)
    bootstrap_collection = load_json(args.bootstrap)

    # Generate template
    print("Generating template YAML...", file=sys.stderr)
    template = generate_template(bootstrap_collection, args.openapi, args.linked)

    # Save template
    print(f"Writing template to {args.template_output}...", file=sys.stderr)
    template_header = f"""# Getting Started Template - Extracted from Bootstrap Collection
# Source: {Path(args.bootstrap).name}
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
#
# This file defines the complete structure for C2M API v2 Getting Started collections.
# Edit this file to customize folder structure, endpoint selections, and field choices.
#
# Schema References (defined in template):
# - OpenAPI Spec: {args.openapi}
#   Provides: Field types, oneOf variants, validation rules
# - Linked Collection: {args.linked}
#   Provides: Canonical request structures with all possible fields
#
# Two collections will be generated from this template:
# 1. Linked Collection (placeholders like <String>) - for documentation
# 2. Test Collection (realistic values) - for actual testing

"""
    save_yaml(template, args.template_output, template_header)

    # Print summary
    print("\nSUCCESS: Template generated", file=sys.stderr)
    print(f"  Template: {args.template_output}", file=sys.stderr)
    print(f"    - Collection: {template['collection']['name']}", file=sys.stderr)
    print(f"    - Groups: {len(template['groups'])}", file=sys.stderr)
    print(f"    - Examples: {len(template['examples'])}", file=sys.stderr)
    print(f"  Schema References:", file=sys.stderr)
    print(f"    - OpenAPI: {template['schema_references']['openapi_spec']}", file=sys.stderr)
    print(f"    - Linked: {template['schema_references']['linked_collection']}", file=sys.stderr)

if __name__ == "__main__":
    main()

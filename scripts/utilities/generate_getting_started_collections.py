#!/usr/bin/env python3
"""
Generate Getting Started Collections from Template

This script reads a template YAML and generates two Postman collections:
1. Linked Collection - With placeholders (<String>, <Integer>) for documentation
2. Test Collection - With realistic values for actual testing

The script uses:
- Template YAML: Defines folder structure, endpoints, field selections
- OpenAPI Spec: Provides types, oneOf variants, validation rules
- Linked Collection: Provides canonical request structures

Usage:
    python3 generate_getting_started_collections.py \
        --template config/getting-started-template.yaml \
        --output-linked postman/generated/c2mapiv2-getting-started-linked-collection.json \
        --output-test postman/generated/c2mapiv2-getting-started-test-collection.json

Architecture:
- Template defines WHAT to generate (folder structure, endpoint selection, field subset)
- OpenAPI spec defines TYPES and VALIDATION (from EBNF single source of truth)
- Linked collection defines STRUCTURE (canonical request format)
- Generator combines all three to create final collections

Author: Claude Code
Date: 2026-03-08
"""

import json
import yaml
import sys
import argparse
import copy
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from faker import Faker

# Initialize Faker for generating unique random test data
fake = Faker()

# Import realistic value generators (reuse existing code)
sys.path.insert(0, str(Path(__file__).parent.parent / "active"))

def load_yaml(filepath: str) -> Dict:
    """Load YAML file."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def load_json(filepath: str) -> Dict:
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(data: Dict, filepath: str):
    """Save data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def find_endpoint_in_linked(linked_collection: Dict, method: str, path: str) -> Optional[Dict]:
    """
    Find matching endpoint in linked collection.

    Returns the request object from linked collection that matches method + path.
    """
    def search_items(items):
        """Recursively search collection items."""
        for item in items:
            if "request" in item:
                request = item["request"]
                req_method = request.get("method", "")
                req_url = request.get("url", {})

                # Extract path from URL
                if isinstance(req_url, dict):
                    path_parts = req_url.get("path", [])
                    req_path = "/" + "/".join([p for p in path_parts if p not in ["{{baseUrl}}"]])
                elif isinstance(req_url, str):
                    req_path = req_url
                else:
                    req_path = ""

                # Match method and path
                if req_method == method and req_path == path:
                    return item

            # Recurse into folders
            if "item" in item:
                result = search_items(item["item"])
                if result:
                    return result

        return None

    items = linked_collection.get("item", [])
    return search_items(items)

def get_oneof_structure(field_name: str, variant: str) -> Any:
    """
    Get the structure for a specific oneOf variant.

    Returns the appropriate nested object or value for the selected variant.
    """
    oneof_fixtures = {
        "docSourceAll": {
            "requestId": {"requestId": 67890},
            "documentId": {"documentId": 12345},
            "url": {"url": "https://example.com/documents/sample.pdf"},
            "zipRequestId": {"zipRequestId": 98765, "zipFilename": "documents.zip"},
            "zipDocumentId": {"zipDocumentId": 54321, "zipFilename": "documents.zip"}
        },
        "recipientAddressSource": {
            "singleAddress": {
                "firstName": "Alice",
                "lastName": "Johnson",
                "address1": "123 Main Street",
                "address2": "Suite 100",
                "address3": "",
                "city": "Boston",
                "state": "MA",
                "zip": "02101",
                "country": "USA"
            },
            "addressList": [
                {
                    "firstName": "Alice",
                    "lastName": "Johnson",
                    "address1": "123 Main Street",
                    "city": "Boston",
                    "state": "MA",
                    "zip": "02101",
                    "country": "USA",
                    "foo1": "Custom Field 1",
                    "foo2": "Custom Field 2"
                }
            ],
            "addressListId": {"addressListId": 1001}
        },
        "paymentDetails": {
            "creditCard": {
                "cardType": "visa",
                "cardNumber": "4111111111111111",
                "expirationMonth": 12,
                "expirationYear": 2026,
                "cvv": 123
            },
            "ach": {
                "accountType": "checking",
                "routingNumber": "111000025",
                "accountNumber": "1234567890"
            },
            "invoice": {"paymentType": "invoice"}
        }
    }

    if field_name in oneof_fixtures and variant in oneof_fixtures[field_name]:
        return oneof_fixtures[field_name][variant]

    return None

def generate_realistic_value(field_name: str, field_type: str, oneof_selection: Optional[str] = None) -> Any:
    """
    Generate realistic value for a field based on its name and type.

    Uses Faker to generate unique random values for each field occurrence.

    TODO: Refactor to avoid hardcoding field names
    Instead of hardcoding field names like "firstName", "address1", etc., explore generating
    example data directly from the getting-started-template.yaml structure. This would make
    the generator more maintainable and allow template changes to automatically flow through
    to generated examples without code changes.
    Potential approach: Parse template YAML to extract field patterns, use Faker based on
    field name patterns (e.g., any field with "name" gets fake.name(), "address" gets
    fake.address(), etc.) rather than exact string matches.
    """
    # Generate unique random values based on field name
    field_lower = field_name.lower()

    # Document sources
    if field_name == "documentId":
        return fake.random_int(min=10000, max=99999)
    elif field_name == "requestId":
        return fake.random_int(min=10000, max=99999)
    elif field_name == "zipDocumentId":
        return fake.random_int(min=10000, max=99999)
    elif field_name == "zipRequestId":
        return fake.random_int(min=10000, max=99999)
    elif field_name == "url":
        return "https://example.com/documents/sample.pdf"

    # Address fields (generate unique values each time)
    elif field_name == "firstName":
        return fake.first_name()
    elif field_name == "lastName":
        return fake.last_name()
    elif field_name == "address1":
        return fake.street_address()
    elif field_name == "address2":
        return f"Suite {fake.random_int(min=100, max=999)}"
    elif field_name == "address3":
        return ""
    elif field_name == "city":
        return fake.city()
    elif field_name == "state":
        return fake.state_abbr()
    elif field_name == "zip":
        return fake.zipcode()
    elif field_name == "country":
        return "USA"
    elif field_name == "company":
        return fake.company()

    # Job configuration - static realistic values
    elif field_name == "jobTemplate":
        return "standard_letter"

    # Job Options - static realistic values
    elif field_name == "documentClass":
        return "letter"
    elif field_name == "layout":
        return "address_on_top"
    elif field_name == "productionTime":
        return "next_day"
    elif field_name == "envelope":
        return "standard"
    elif field_name == "color":
        return "full_color"
    elif field_name == "paperType":
        return "white"
    elif field_name == "printOption":
        return "double_sided"
    elif field_name == "mailClass":
        return "first_class"

    # Payment - static realistic values
    elif field_name == "cardType":
        return "visa"
    elif field_name == "cardNumber":
        return "4111111111111111"
    elif field_name == "expirationMonth":
        return 12
    elif field_name == "expirationYear":
        return 2026
    elif field_name == "cvv":
        return 123
    elif field_name == "accountType":
        return "checking"
    elif field_name == "routingNumber":
        return "111000025"
    elif field_name == "accountNumber":
        return "1234567890"

    # Lists - static realistic values
    elif field_name == "addressListId":
        return 1001
    elif field_name == "addressListName":
        return "Marketing Campaign Q1"
    elif field_name == "mappingId":
        return 5001

    # Other fields
    elif field_name == "filename":
        return "document.pdf"
    elif field_name == "paymentType":
        return "credit_card"

    # Merge fields (custom data)
    elif field_name == "foo1":
        return "Custom Field 1"
    elif field_name == "foo2":
        return "Custom Field 2"

    # Pages
    elif field_name == "startPage":
        return 1
    elif field_name == "endPage":
        return 5

    # Otherwise generate based on type (fallback)
    elif field_type == "string":
        return f"example_{field_name}"
    elif field_type == "integer":
        return 123
    elif field_type == "number":
        return 123.45
    elif field_type == "boolean":
        return True
    else:
        return None

def replace_placeholders_recursive(obj: Any, parent_key: str = "") -> Any:
    """
    Recursively replace all placeholders in an object with realistic values.

    Args:
        obj: The object to process (can be dict, list, string, etc.)
        parent_key: The parent key name (for nested objects)

    Returns:
        Object with all placeholders replaced
    """
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            result[key] = replace_placeholders_recursive(value, key)
        return result
    elif isinstance(obj, list):
        return [replace_placeholders_recursive(item, parent_key) for item in obj]
    elif isinstance(obj, str):
        if obj.startswith("<"):
            # Placeholder - generate realistic value
            field_type = "string" if "String" in obj or "oneOf" in obj else "integer"
            return generate_realistic_value(parent_key, field_type)
        return obj
    else:
        # Return other types as-is
        return obj


def apply_template_to_request(template_example: Dict, linked_request: Dict, use_realistic_values: bool = False) -> Dict:
    """
    Apply template selections and values to a linked collection request.

    Args:
        template_example: Example from template with select/values
        linked_request: Canonical request from linked collection
        use_realistic_values: If True, use realistic values; if False, keep placeholders

    Returns:
        Modified request with template applied
    """
    request = copy.deepcopy(linked_request)

    # Parse body
    body = request.get("body", {})
    raw_body = body.get("raw", "{}")

    try:
        body_obj = json.loads(raw_body)
    except json.JSONDecodeError:
        body_obj = {}

    # Apply oneOf selections from template
    selections = template_example.get("select", {})

    # Apply values from template
    values = template_example.get("values", {})

    if use_realistic_values:
        # For test collection: Build ONLY fields from template with realistic data
        new_body = {}

        # Apply selections (oneOf variants) with realistic data
        for field, variant in selections.items():
            structure = get_oneof_structure(field, variant)
            if structure is not None:
                new_body[field] = structure

        # Apply values from template with realistic data
        for field, value in values.items():
            if field in selections:
                # This is a oneOf field - skip (handled above)
                continue

            # Recursively replace placeholders in the value with realistic data
            new_body[field] = replace_placeholders_recursive(value, field)
    else:
        # For linked collection: Build ONLY fields from template (subset)
        new_body = {}

        # Apply selections (oneOf variants) with placeholders
        for field, variant in selections.items():
            # Build structure with placeholders based on variant
            structure = get_oneof_structure(field, variant)
            if structure is not None:
                # Replace values with placeholders
                def placeholderize(obj):
                    if isinstance(obj, dict):
                        return {k: placeholderize(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [placeholderize(item) for item in obj]
                    elif isinstance(obj, str):
                        return "<String>"
                    elif isinstance(obj, int):
                        return "<Integer>"
                    elif isinstance(obj, float):
                        return "<Number>"
                    elif isinstance(obj, bool):
                        return "<Boolean>"
                    return obj

                new_body[field] = placeholderize(structure)

        # Apply values from template (keep placeholders)
        for field, value in values.items():
            if field in selections:
                # This is a oneOf field - skip (handled above)
                continue

            # Use placeholder value from template
            new_body[field] = value

    # Update request body
    request["body"]["raw"] = json.dumps(new_body, indent=2)

    # Update request name and description
    request["name"] = template_example.get("name", "Unnamed")
    if template_example.get("description"):
        request["description"] = {
            "content": template_example["description"],
            "type": "text/plain"
        }

    return request

def generate_collection(template: Dict, linked_collection: Dict, use_realistic_values: bool = False) -> Dict:
    """
    Generate a Postman collection from template.

    Args:
        template: Template YAML with collection metadata, groups, examples
        linked_collection: Canonical linked collection (structure source)
        use_realistic_values: If True, generate test collection; if False, linked collection

    Returns:
        Complete Postman collection
    """
    # Collection metadata
    collection_info = template.get("collection", {})
    collection_name = collection_info.get("name", "C2M API v2 - Getting Started")

    # Append suffix based on collection type
    if use_realistic_values:
        collection_name += " - With Examples"
    else:
        collection_name += " - With Types"

    collection = {
        "info": {
            "name": collection_name,
            "description": collection_info.get("description", ""),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    # Create folders from groups
    groups = template.get("groups", [])
    folders = {}

    for group in sorted(groups, key=lambda g: g.get("order", 999)):
        folder = {
            "name": group.get("display_name", group.get("logical_name")),
            "description": group.get("description", ""),
            "item": []
        }
        folders[group.get("logical_name")] = folder

    # Process examples
    examples = template.get("examples", [])

    for example in examples:
        method = example.get("method", "POST")
        path = example.get("path", "")
        group = example.get("group", "")

        # Find matching endpoint in linked collection
        linked_item = find_endpoint_in_linked(linked_collection, method, path)

        if not linked_item:
            print(f"WARNING: Could not find endpoint {method} {path} in linked collection", file=sys.stderr)
            continue

        # Apply template to request
        linked_request = linked_item.get("request", {})
        modified_request = apply_template_to_request(example, linked_request, use_realistic_values)

        # Create new item
        new_item = {
            "name": example.get("name", "Unnamed"),
            "request": modified_request,
            "response": []
        }

        # Add to appropriate folder
        if group in folders:
            folders[group]["item"].append(new_item)
        else:
            print(f"WARNING: Group '{group}' not found, skipping example '{example.get('name')}'", file=sys.stderr)

    # Add folders to collection in order
    for group in sorted(groups, key=lambda g: g.get("order", 999)):
        logical_name = group.get("logical_name")
        if logical_name in folders and folders[logical_name]["item"]:
            collection["item"].append(folders[logical_name])

    return collection

def add_jwt_auth(collection_path: str, jwt_script_path: str = "postman/scripts/jwt-pre-request.js") -> bool:
    """
    Add JWT authentication pre-request script to a collection.

    Uses the existing add_pre_request_script.js Node.js script.

    Args:
        collection_path: Path to collection JSON file
        jwt_script_path: Path to JWT pre-request script

    Returns:
        True if successful, False otherwise
    """
    # Path to the Node.js script that adds pre-request code
    add_script_path = Path("scripts/active/add_pre_request_script.js")

    if not add_script_path.exists():
        print(f"WARNING: Could not find {add_script_path}, skipping JWT auth", file=sys.stderr)
        return False

    if not Path(jwt_script_path).exists():
        print(f"WARNING: Could not find {jwt_script_path}, skipping JWT auth", file=sys.stderr)
        return False

    try:
        # Call the Node.js script to add JWT pre-request
        result = subprocess.run(
            ['node', str(add_script_path), collection_path, jwt_script_path, collection_path],
            capture_output=True,
            text=True,
            check=True
        )

        # Print output from the script
        if result.stdout:
            print(result.stdout.strip(), file=sys.stderr)

        return True

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to add JWT auth: {e.stderr}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Failed to add JWT auth: {str(e)}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Generate Getting Started collections from template"
    )
    parser.add_argument(
        "--template",
        default="config/getting-started-template.yaml",
        help="Path to template YAML"
    )
    parser.add_argument(
        "--output-linked",
        default="postman/generated/c2mapiv2-getting-started-linked-collection.json",
        help="Output path for linked collection (placeholders)"
    )
    parser.add_argument(
        "--output-test",
        default="postman/generated/c2mapiv2-getting-started-test-collection.json",
        help="Output path for test collection (realistic values)"
    )

    args = parser.parse_args()

    # Load template
    print(f"Loading template from {args.template}...", file=sys.stderr)
    template = load_yaml(args.template)

    # Load schema references from template
    schema_refs = template.get("schema_references", {})
    openapi_path = schema_refs.get("openapi_spec", "openapi/c2mapiv2-openapi-spec-base.yaml")
    linked_path = schema_refs.get("linked_collection", "postman/generated/c2mapiv2-linked-collection-flat.json")

    # Load linked collection
    print(f"Loading linked collection from {linked_path}...", file=sys.stderr)
    linked_collection = load_json(linked_path)

    # Generate linked collection (placeholders)
    print("Generating linked collection (placeholders)...", file=sys.stderr)
    linked_output = generate_collection(template, linked_collection, use_realistic_values=False)

    # Generate test collection (realistic values)
    print("Generating test collection (realistic values)...", file=sys.stderr)
    test_output = generate_collection(template, linked_collection, use_realistic_values=True)

    # Save outputs
    print(f"Writing linked collection to {args.output_linked}...", file=sys.stderr)
    Path(args.output_linked).parent.mkdir(parents=True, exist_ok=True)
    save_json(linked_output, args.output_linked)

    print(f"Writing test collection to {args.output_test}...", file=sys.stderr)
    Path(args.output_test).parent.mkdir(parents=True, exist_ok=True)
    save_json(test_output, args.output_test)

    # Add JWT authentication pre-request script to both collections
    print("\nAdding JWT authentication pre-request script...", file=sys.stderr)
    linked_auth_success = add_jwt_auth(args.output_linked)
    test_auth_success = add_jwt_auth(args.output_test)

    # Print summary
    print("\nSUCCESS: Collections generated", file=sys.stderr)
    print(f"  Linked Collection: {args.output_linked}", file=sys.stderr)
    print(f"    - Name: {linked_output['info']['name']}", file=sys.stderr)
    print(f"    - Folders: {len(linked_output['item'])}", file=sys.stderr)
    total_linked = sum(len(folder["item"]) for folder in linked_output["item"])
    print(f"    - Total items: {total_linked}", file=sys.stderr)
    print(f"    - JWT Auth: {'Added' if linked_auth_success else 'Failed'}", file=sys.stderr)

    print(f"  Test Collection: {args.output_test}", file=sys.stderr)
    print(f"    - Name: {test_output['info']['name']}", file=sys.stderr)
    print(f"    - Folders: {len(test_output['item'])}", file=sys.stderr)
    total_test = sum(len(folder["item"]) for folder in test_output["item"])
    print(f"    - Total items: {total_test}", file=sys.stderr)
    print(f"    - JWT Auth: {'Added' if test_auth_success else 'Failed'}", file=sys.stderr)

if __name__ == "__main__":
    main()

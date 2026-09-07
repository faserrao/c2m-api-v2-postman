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
sys.path.insert(0, str(Path(__file__).parent.parent))
from utilities.oneof_resolver import find_variant_by_discriminator_key, build_variant_placeholder_structure

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

def get_schema_from_openapi(openapi_spec: Dict, schema_ref: str) -> Optional[Dict]:
    """
    Resolve a $ref to get the actual schema from OpenAPI spec.

    Args:
        openapi_spec: Loaded OpenAPI spec
        schema_ref: Reference like '#/components/schemas/requestIdSource'

    Returns:
        Schema definition dict or None
    """
    if not schema_ref.startswith('#/components/schemas/'):
        return None

    schema_name = schema_ref.replace('#/components/schemas/', '')
    return openapi_spec.get('components', {}).get('schemas', {}).get(schema_name)

def build_structure_from_schema(schema: Dict, openapi_spec: Dict) -> Any:
    """
    Recursively build JSON structure from OpenAPI schema with placeholders.

    This function focuses on building the correct structure (nesting, types, arrays)
    with placeholder values. Use replace_placeholders_recursive() to generate
    realistic values based on field names.

    Args:
        schema: OpenAPI schema definition
        openapi_spec: Full OpenAPI spec (for resolving refs)

    Returns:
        JSON structure matching the schema with placeholder values
    """
    # Handle $ref
    if '$ref' in schema:
        ref_schema = get_schema_from_openapi(openapi_spec, schema['$ref'])
        if ref_schema:
            return build_structure_from_schema(ref_schema, openapi_spec)
        return None

    schema_type = schema.get('type')

    # Handle objects
    if schema_type == 'object':
        result = {}
        properties = schema.get('properties', {})

        for prop_name, prop_schema in properties.items():
            # Include all fields (required + optional) for Getting Started examples
            result[prop_name] = build_structure_from_schema(prop_schema, openapi_spec)

        return result

    # Handle arrays
    elif schema_type == 'array':
        item_schema = schema.get('items', {})
        # Return array with one example item
        item = build_structure_from_schema(item_schema, openapi_spec)
        return [item] if item is not None else []

    # Handle primitives - always return placeholders
    elif schema_type == 'string':
        return "<String>"

    elif schema_type == 'integer':
        return "<Integer>"

    elif schema_type == 'number':
        return "<Number>"

    elif schema_type == 'boolean':
        return "<Boolean>"

    # Handle enums
    elif 'enum' in schema:
        return f"<{' | '.join(schema['enum'])}>"

    return None

def get_oneof_structure_from_openapi(openapi_spec: Dict, field_name: str, variant: str) -> Any:
    """
    Get oneOf variant structure from OpenAPI spec with placeholder values.
    Replaces hardcoded variant_mappings with dynamic spec-driven lookup.
    """
    schema_name, _ = find_variant_by_discriminator_key(openapi_spec, field_name, variant)
    if schema_name is None:
        return None
    return build_variant_placeholder_structure(openapi_spec, schema_name)

def generate_realistic_value(field_name: str, field_type: str,
                              faker_hints: dict = None) -> Any:
    """
    Generate a realistic value for a field using hints from the template YAML.
    Falls back to generic type-based values if no hint is present.
    """
    if faker_hints and field_name in faker_hints:
        hint = faker_hints[field_name]
        hint_type = hint.get('type')
        if hint_type == 'static':
            return hint['value']
        elif hint_type == 'faker':
            return getattr(fake, hint['method'])()
        elif hint_type == 'random_int':
            return fake.random_int(
                min=hint.get('min', 0),
                max=hint.get('max', 9999)
            )
    # Generic fallback — degraded but not broken
    if field_type == 'integer':
        return 123
    elif field_type == 'number':
        return 123.45
    elif field_type == 'boolean':
        return True
    return f"example_{field_name}"

def replace_placeholders_recursive(obj: Any, parent_key: str = "",
                                    faker_hints: dict = None) -> Any:
    """
    Recursively replace all placeholders in an object with realistic values.
    """
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            result[key] = replace_placeholders_recursive(value, key, faker_hints)
        return result
    elif isinstance(obj, list):
        return [replace_placeholders_recursive(item, parent_key, faker_hints)
                for item in obj]
    elif isinstance(obj, str) and obj.startswith("<"):
        field_type = "string" if "String" in obj or "oneOf" in obj else "integer"
        return generate_realistic_value(parent_key, field_type, faker_hints)
    return obj


def apply_template_to_request(template_example: Dict, linked_request: Dict, openapi_spec: Dict,
                               use_realistic_values: bool = False, faker_hints: dict = None) -> Dict:
    """
    Apply template selections and values to a linked collection request.
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

    # Build body with ONLY fields from template
    new_body = {}

    # Apply selections (oneOf variants) - get structure from OpenAPI
    for field, variant in selections.items():
        # Get structure with placeholders from OpenAPI spec (source of truth)
        structure = get_oneof_structure_from_openapi(openapi_spec, field, variant)
        if structure is not None:
            if use_realistic_values:
                new_body[field] = replace_placeholders_recursive(structure, field, faker_hints)
            else:
                new_body[field] = structure

    # Apply values from template
    for field, value in values.items():
        if field in selections:
            continue

        if use_realistic_values:
            new_body[field] = replace_placeholders_recursive(value, field, faker_hints)
        else:
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

def generate_collection(template: Dict, linked_collection: Dict, openapi_spec: Dict, use_realistic_values: bool = False) -> Dict:
    """
    Generate a Postman collection from template.

    Args:
        template: Template YAML with collection metadata, groups, examples
        linked_collection: Canonical linked collection (structure source)
        openapi_spec: OpenAPI specification (structure definitions from EBNF)
        use_realistic_values: If True, generate test collection; if False, linked collection

    Returns:
        Complete Postman collection
    """
    faker_hints = template.get('faker_hints', {})

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
        modified_request = apply_template_to_request(example, linked_request, openapi_spec, use_realistic_values, faker_hints)

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

def extract_all_spec_field_names(spec: Dict) -> set:
    """Recursively collect all property names from spec component schemas."""
    names = set()

    def _collect(schema):
        if not isinstance(schema, dict):
            return
        for prop_name, prop_schema in schema.get('properties', {}).items():
            names.add(prop_name)
            _collect(prop_schema)
        for sub in schema.get('allOf', []) + schema.get('oneOf', []) + schema.get('anyOf', []):
            _collect(sub)
        if 'items' in schema:
            _collect(schema['items'])

    for schema in spec.get('components', {}).get('schemas', {}).values():
        _collect(schema)

    return names


def validate_faker_hints_keys(faker_hints: dict, spec: Dict) -> None:
    """
    Validate that faker_hints keys match known field names in the OpenAPI spec.

    Warns (does not fail) about unknown keys — some keys like foo1/foo2 are
    intentional extras not in the spec. Unknown keys fall back to type-based
    placeholder generation, so there is no build failure, only a potential
    silent quality gap if a field was renamed in the EBNF.

    If any key was renamed in the EBNF, it will appear here as unknown.
    Fix: update the faker_hints key in config/getting-started-template.yaml
    to match the new field name.
    """
    if not faker_hints:
        return

    spec_fields = extract_all_spec_field_names(spec)

    if not spec_fields:
        print("⚠️  WARNING: Could not extract field names from OpenAPI spec — skipping faker_hints validation",
              file=sys.stderr)
        return

    print(f"\n🔍 Validating faker_hints keys against OpenAPI spec ({len(spec_fields)} known fields)...",
          file=sys.stderr)

    unknown_keys = [k for k in faker_hints if k not in spec_fields]
    if unknown_keys:
        print(f"⚠️  faker_hints has {len(unknown_keys)} key(s) not found in the OpenAPI spec:", file=sys.stderr)
        for key in sorted(unknown_keys):
            hint = faker_hints[key]
            detail = hint.get('value', hint.get('method', '?'))
            print(f"   - {key}  (type={hint.get('type','?')}, value={detail})", file=sys.stderr)
        print("   These may be intentional extras (e.g. foo1/foo2) or renamed EBNF fields.", file=sys.stderr)
        print("   If a field was renamed, update faker_hints to match the new name.", file=sys.stderr)
    else:
        print(f"✓ All {len(faker_hints)} faker_hints keys are valid spec field names", file=sys.stderr)


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

    # Load OpenAPI spec
    print(f"Loading OpenAPI spec from {openapi_path}...", file=sys.stderr)
    openapi_spec = load_yaml(openapi_path)

    # Validate faker_hints keys against spec field names
    validate_faker_hints_keys(template.get('faker_hints', {}), openapi_spec)

    # Generate linked collection (placeholders)
    print("Generating linked collection (placeholders)...", file=sys.stderr)
    linked_output = generate_collection(template, linked_collection, openapi_spec, use_realistic_values=False)

    # Generate test collection (realistic values)
    print("Generating test collection (realistic values)...", file=sys.stderr)
    test_output = generate_collection(template, linked_collection, openapi_spec, use_realistic_values=True)

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

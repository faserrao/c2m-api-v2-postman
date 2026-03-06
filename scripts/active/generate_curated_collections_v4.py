#!/usr/bin/env python3
"""
Generate Curated Postman Collections from YAML Catalog (v4)

This script implements the "Read structure, write values" pattern:
1. Reads canonical request structure from Linked Collection (EBNF source of truth)
2. Reads example values from YAML catalog (business data only)
3. Applies oneOf selections and fills leaf values
4. Generates collections by tag filtering

Architecture:
- YAML catalog contains ONLY leaf values, never structure
- Linked Collection provides complete canonical structure
- OpenAPI spec provides deep oneOf variant structures
- Generator discovers structure, applies selections, fills values
- No hardcoded request structure anywhere

Validations:
1. Endpoint validation: Fail if method+path not in Linked Collection
2. Field validation: Warn if YAML value field doesn't exist after oneOf selection
3. Tag-based filtering: Generate multiple collections from one catalog

Usage:
    python3 generate_curated_collections_v4.py --config config/curated-examples-catalog.yaml --linked postman/generated/c2mapiv2-linked-collection-flat.json --openapi openapi/c2mapiv2-openapi-spec-base.yaml --output-dir postman/generated/ --tags real-world

Author: Claude Code
Date: 2026-03-05
"""

import json
import yaml
import argparse
import sys
import copy
from pathlib import Path


def load_yaml_catalog(catalog_path):
    """Load YAML catalog with examples and groups."""
    try:
        with open(catalog_path, 'r') as f:
            catalog = yaml.safe_load(f)
        return catalog.get('examples', []), catalog.get('groups', [])
    except FileNotFoundError:
        print(f"ERROR: Catalog file not found: {catalog_path}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML syntax: {e}", file=sys.stderr)
        sys.exit(1)


def load_linked_collection(linked_path):
    """Load Linked Collection (canonical request structure)."""
    try:
        with open(linked_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Linked collection not found: {linked_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in linked collection: {e}", file=sys.stderr)
        sys.exit(1)


def load_openapi_spec(openapi_path):
    """Load OpenAPI specification (for deep oneOf structures)."""
    try:
        with open(openapi_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: OpenAPI spec not found: {openapi_path}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in OpenAPI spec: {e}", file=sys.stderr)
        sys.exit(1)


def resolve_ref(spec, ref_path):
    """
    Resolve $ref pointer to actual schema in OpenAPI spec.

    Args:
        spec: OpenAPI specification dictionary
        ref_path: Reference path like '#/components/schemas/creditCardPayment'

    Returns:
        Resolved schema dictionary, or None if not found
    """
    if not ref_path.startswith('#/'):
        return None

    # Split path: '#/components/schemas/creditCardPayment' -> ['components', 'schemas', 'creditCardPayment']
    parts = ref_path[2:].split('/')

    current = spec
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]

    return current


def resolve_schema_deep(spec, schema, depth=0, max_depth=10):
    """
    Recursively resolve all $ref pointers in a schema to get complete structure.

    Args:
        spec: OpenAPI specification
        schema: Schema to resolve (may contain $ref)
        depth: Current recursion depth
        max_depth: Maximum recursion depth to prevent infinite loops

    Returns:
        Fully resolved schema with all $ref replaced by actual structures
    """
    if depth > max_depth:
        return schema  # Prevent infinite recursion

    if not isinstance(schema, dict):
        return schema

    # If this schema has a $ref, resolve it first
    if '$ref' in schema:
        resolved = resolve_ref(spec, schema['$ref'])
        if resolved is None:
            return schema
        # Recursively resolve the resolved schema
        return resolve_schema_deep(spec, resolved, depth + 1, max_depth)

    # Recursively resolve all nested schemas
    result = {}
    for key, value in schema.items():
        if key == 'properties' and isinstance(value, dict):
            # Resolve each property schema
            result[key] = {
                prop_name: resolve_schema_deep(spec, prop_schema, depth + 1, max_depth)
                for prop_name, prop_schema in value.items()
            }
        elif key == 'oneOf' and isinstance(value, list):
            # Resolve each oneOf variant
            result[key] = [
                resolve_schema_deep(spec, variant, depth + 1, max_depth)
                for variant in value
            ]
        elif key == 'items' and isinstance(value, dict):
            # Resolve array items schema
            result[key] = resolve_schema_deep(spec, value, depth + 1, max_depth)
        elif isinstance(value, dict):
            # Recursively resolve nested dictionaries
            result[key] = resolve_schema_deep(spec, value, depth + 1, max_depth)
        elif isinstance(value, list):
            # Recursively resolve lists
            result[key] = [
                resolve_schema_deep(spec, item, depth + 1, max_depth) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value

    return result


# Mapping from YAML selection values to OpenAPI schema names
VARIANT_SCHEMA_MAPPING = {
    # paymentDetails variants
    'creditCard': 'creditCardPayment',
    'invoice': 'invoicePayment',
    'ach': 'achPayment',
    'userCredit': 'userCreditPayment',

    # docSourceAll variants (via docSourceStandard)
    'documentId': 'documentIdSource',
    'requestId': 'requestIdSource',
    'url': 'urlSource',

    # docSourceZipFile variants
    'zipDocumentId': 'zipDocumentIdSource',
    'zipRequestId': 'zipRequestIdSource',

    # recipientAddressSource variants
    'singleAddress': 'recipientAddressBySingle',
    'addressList': 'recipientAddressByList',
    'addressListId': 'recipientAddressByListId',
}


def get_variant_structure_from_spec(spec, field_name, variant_name):
    """
    Get deep structure for a oneOf variant from OpenAPI spec.

    Args:
        spec: OpenAPI specification
        field_name: Field containing oneOf (e.g., 'paymentDetails')
        variant_name: Selected variant (e.g., 'creditCard')

    Returns:
        Dictionary with {variant_name: deep_structure} or None if not found
    """
    # Map YAML selection to OpenAPI schema name
    schema_name = VARIANT_SCHEMA_MAPPING.get(variant_name)
    if not schema_name:
        return None

    # Get the schema from components
    if 'components' not in spec or 'schemas' not in spec['components']:
        return None

    schemas = spec['components']['schemas']
    if schema_name not in schemas:
        return None

    # Resolve the schema completely (handle all $ref)
    schema = schemas[schema_name]
    resolved_schema = resolve_schema_deep(spec, schema)

    # Convert OpenAPI schema to example structure with placeholders
    return schema_to_example(resolved_schema)


def schema_to_example(schema):
    """
    Convert OpenAPI schema to example structure with placeholders.

    Args:
        schema: Resolved OpenAPI schema

    Returns:
        Example object with placeholders like "<string>", "<integer>"
    """
    if not isinstance(schema, dict):
        return "<unknown>"

    # Handle different schema types
    schema_type = schema.get('type')

    if schema_type == 'object':
        # Build object with all properties
        result = {}
        properties = schema.get('properties', {})
        for prop_name, prop_schema in properties.items():
            result[prop_name] = schema_to_example(prop_schema)
        return result

    elif schema_type == 'array':
        # Build array with one example item
        items_schema = schema.get('items', {})
        return [schema_to_example(items_schema)]

    elif schema_type == 'string':
        # Check if enum
        if 'enum' in schema:
            return "<enum>"
        return "<string>"

    elif schema_type == 'integer':
        return "<integer>"

    elif schema_type == 'number':
        return "<number>"

    elif schema_type == 'boolean':
        return "<boolean>"

    elif 'oneOf' in schema:
        # Nested oneOf - return placeholder
        return "<oneOf>"

    else:
        return "<unknown>"


def select_oneof_variants(template_obj, select_map, openapi_spec=None):
    """
    Materialize oneOf selections by reading actual structure from OpenAPI spec.

    Args:
        template_obj: Nested object from canonical structure (may contain "<oneOf>" placeholders)
        select_map: Dictionary mapping field_name → variant_name (e.g., {"paymentDetails": "creditCard"})
        openapi_spec: OpenAPI specification for resolving deep structures

    Returns:
        Modified template with oneOf placeholders replaced by actual variant structures
    """
    if not isinstance(template_obj, dict):
        return template_obj

    result = {}
    for key, value in template_obj.items():
        # Check if this field has a oneOf selection
        if key in select_map and value == "<oneOf>":
            variant_name = select_map[key]

            # Try to get variant structure from OpenAPI spec
            variant_structure = None
            if openapi_spec:
                variant_structure = get_variant_structure_from_spec(openapi_spec, key, variant_name)

            # Use the structure if we got it
            if variant_structure is not None:
                result[key] = {variant_name: variant_structure}
            else:
                # Fallback: Create generic nested structure
                if variant_name.endswith("Id"):
                    result[key] = {variant_name: "<integer>"}
                else:
                    result[key] = {variant_name: "<string>"}
        elif isinstance(value, dict):
            # Recurse into nested objects
            result[key] = select_oneof_variants(value, select_map, openapi_spec)
        elif isinstance(value, list):
            # Recurse into arrays
            result[key] = [select_oneof_variants(item, select_map, openapi_spec) for item in value]
        else:
            # Keep value as-is
            result[key] = value

    return result


def find_canonical_request(linked_collection, method, path):
    """
    Find canonical request template in Linked Collection.

    Returns: (item, request_body_dict) or (None, None)
    """
    for item in linked_collection.get('item', []):
        if item.get('request', {}).get('method') == method:
            url = item['request'].get('url', {})
            item_path = '/' + '/'.join(url.get('path', []))

            if item_path == path:
                # Found matching endpoint
                body_raw = item['request'].get('body', {}).get('raw', '{}')
                try:
                    body_dict = json.loads(body_raw)
                    return item, body_dict
                except json.JSONDecodeError:
                    print(f"WARNING: Cannot parse body for {method} {path}", file=sys.stderr)
                    return None, None

    return None, None


def extract_template_body(canonical_request_item):
    """
    Extract and parse request body template from canonical request item.

    Returns: Dictionary representing the canonical request body structure
    """
    try:
        body_raw = canonical_request_item['request']['body']['raw']
        return json.loads(body_raw)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot extract template body: {e}", file=sys.stderr)
        return {}


def deep_set_values_into_template(template_obj, values_obj, path="", debug=False):
    """
    Deep overlay values into template structure with validation.

    Args:
        template_obj: Nested object from canonical structure (with placeholders)
        values_obj: Flat dictionary of field_name: value from YAML
        path: Current path for error messages
        debug: Enable debug logging

    Returns:
        Modified template with values filled in

    Raises:
        ValueError: If values_obj references field not in template_obj
    """
    if not isinstance(template_obj, dict):
        return template_obj

    result = {}
    for key, value in template_obj.items():
        # Check if we have a value for this field
        if key in values_obj:
            # Direct replacement - this is a leaf value
            if debug:
                print(f"  [{path}.{key}] MATCH: Replacing {value} with {values_obj[key]}")
            result[key] = values_obj[key]
        elif isinstance(value, dict):
            # Recurse into nested object
            if debug:
                print(f"  [{path}.{key}] RECURSE into nested object")
            result[key] = deep_set_values_into_template(value, values_obj, f"{path}.{key}", debug)
        elif isinstance(value, list):
            # Recurse into array
            if debug:
                print(f"  [{path}.{key}] RECURSE into array")
            result[key] = [deep_set_values_into_template(item, values_obj, f"{path}.{key}[]", debug) for item in value]
        elif isinstance(value, str) and value.startswith('<'):
            # Placeholder - check if we have value in flat dict
            if key in values_obj:
                if debug:
                    print(f"  [{path}.{key}] PLACEHOLDER MATCH: Replacing {value} with {values_obj[key]}")
                result[key] = values_obj[key]
            else:
                # Keep placeholder (value will be filled by permutation later or left as placeholder)
                if debug:
                    print(f"  [{path}.{key}] PLACEHOLDER KEEP: {value} (no value in YAML)")
                result[key] = value
        else:
            # Keep original value
            if debug:
                print(f"  [{path}.{key}] KEEP: {value}")
            result[key] = value

    return result


def filter_to_yaml_fields(body_obj, yaml_values, yaml_select):
    """
    Filter request body to only include fields specified in YAML values or select.

    Args:
        body_obj: Nested request body from canonical collection
        yaml_values: Dictionary of field values from YAML
        yaml_select: Dictionary of oneOf selections from YAML

    Returns:
        Filtered body with only YAML-specified fields
    """
    if not isinstance(body_obj, dict):
        return body_obj

    # All field names that appear in YAML (values + select)
    yaml_fields = set(yaml_values.keys()) | set(yaml_select.keys())

    result = {}
    for key, value in body_obj.items():
        if key in yaml_fields:
            # Field is specified in YAML - keep it WITH all its nested structure
            # Do NOT recursively filter - preserve the complete nested object
            result[key] = value

    return result


def convert_values_to_placeholders(body_obj):
    """
    Convert actual values in request body to type placeholders.

    Args:
        body_obj: Request body with actual values

    Returns:
        Request body with values replaced by placeholders (<string>, <integer>, etc.)
    """
    if not isinstance(body_obj, dict):
        return body_obj

    result = {}
    for key, value in body_obj.items():
        if isinstance(value, dict):
            # Recursively convert nested objects
            result[key] = convert_values_to_placeholders(value)
        elif isinstance(value, list):
            # Recursively convert array items
            result[key] = [convert_values_to_placeholders(item) if isinstance(item, dict) else "<array_item>" for item in value]
        elif isinstance(value, str):
            result[key] = "<string>"
        elif isinstance(value, int):
            result[key] = "<integer>"
        elif isinstance(value, float):
            result[key] = "<number>"
        elif isinstance(value, bool):
            result[key] = "<boolean>"
        else:
            result[key] = "<unknown>"

    return result


def materialize_request_body(canonical_request_item, example, openapi_spec, mode='examples'):
    """
    Produce the final Postman request item:
    - Deep clone canonical request
    - Select oneOf variants (using OpenAPI spec for deep structures)
    - Overlay example values
    - Filter to only YAML-specified fields
    - (Optional) Convert to placeholders if mode='placeholders'
    - Serialize to request.body.raw JSON

    Args:
        canonical_request_item: Complete Postman request item from linked collection
        example: YAML example with 'select' and 'values' sections
        openapi_spec: OpenAPI specification for resolving deep oneOf structures
        mode: 'placeholders' or 'examples' (default 'examples')

    Returns:
        Complete Postman request item with materialized request body
    """
    # Step 1: Deep clone canonical request (don't modify original)
    request_item = copy.deepcopy(canonical_request_item)

    # Step 2: Extract template body
    template_body = extract_template_body(request_item)

    # Step 3: Select oneOf variants (using OpenAPI spec)
    selections = example.get('select', {})
    template_with_selections = select_oneof_variants(template_body, selections, openapi_spec)

    # Step 4: Overlay example values
    values = example.get('values', {})
    name = example.get('name', 'Unknown')
    print(f"\n=== Filling values for: {name} (mode={mode}) ===")
    print(f"Template after oneOf selection:")
    print(json.dumps(template_with_selections, indent=2)[:500])  # First 500 chars
    print(f"\nValues to fill:")
    print(json.dumps(values, indent=2))
    filled_body = deep_set_values_into_template(template_with_selections, values, debug=True)

    # Step 5: Filter to only YAML-specified fields
    selections = example.get('select', {})
    filtered_body = filter_to_yaml_fields(filled_body, values, selections)

    # Step 6: Convert to placeholders if in placeholder mode
    if mode == 'placeholders':
        filtered_body = convert_values_to_placeholders(filtered_body)

    # Step 7: Serialize back to request.body.raw
    request_item['request']['body']['raw'] = json.dumps(filtered_body, indent=2)

    # Step 8: Update item metadata
    request_item['name'] = example.get('name')
    request_item['request']['description'] = example.get('description', '')

    return request_item


def validate_endpoint_exists(linked_collection, method, path):
    """
    Validation 1: Endpoint Existence

    Fail if method+path not found in Linked Collection.
    """
    item, body = find_canonical_request(linked_collection, method, path)
    if item is None:
        return False, f"Endpoint not found: {method} {path}"
    return True, "OK"


def get_all_field_names(obj, prefix=""):
    """Recursively get all field names in nested structure."""
    fields = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            fields.add(key)
            if isinstance(value, dict):
                fields.update(get_all_field_names(value, f"{prefix}.{key}"))
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                fields.update(get_all_field_names(value[0], f"{prefix}.{key}[]"))
    return fields


def validate_field_patchability(template_body, values_dict, selections):
    """
    Validation 2: Field Patchability

    Warn if YAML contains field names that don't exist in canonical structure
    after oneOf selections are applied.

    Returns: (is_valid, warnings_list)
    """
    warnings = []

    # Apply selections to get actual structure
    template_with_selections = select_oneof_variants(template_body, selections)

    # Get all field names in canonical structure (after oneOf selection)
    canonical_fields = get_all_field_names(template_with_selections)

    # Check each value in YAML
    for field_name in values_dict.keys():
        if field_name not in canonical_fields and not field_name.startswith('_'):
            # Special fields (tags, jobTemplate, etc.) are always valid
            special_fields = {'tags', 'jobTemplate', 'jobOptions'}
            if field_name not in special_fields:
                warnings.append(f"Field '{field_name}' not found in canonical structure (may be unused)")

    return True, warnings


def categorize_getting_started_examples(filtered_examples, groups):
    """
    Categorize Getting Started examples into folders based on group field.

    Args:
        filtered_examples: List of examples from YAML
        groups: List of group definitions from YAML with logical_name, display_name, order, description

    Returns:
        List of tuples: [(display_name, description, order, examples), ...]
        Sorted by order for consistent folder structure
    """
    # Build mapping from logical_name to group definition
    group_map = {g['logical_name']: g for g in groups}

    # Build mapping from logical_name to examples list
    categorized = {}
    for example in filtered_examples:
        group_name = example.get('group')
        if group_name and group_name in group_map:
            if group_name not in categorized:
                categorized[group_name] = []
            categorized[group_name].append(example)

    # Convert to list of tuples with display info, sorted by order
    result = []
    for logical_name, examples in categorized.items():
        group_def = group_map[logical_name]
        result.append((
            group_def['display_name'],
            group_def.get('description', ''),
            group_def.get('order', 999),
            examples
        ))

    # Sort by order
    result.sort(key=lambda x: x[2])

    return result


def generate_collection(examples, groups, linked_collection, openapi_spec, collection_name, tag_filter=None, mode='examples'):
    """
    Generate a Postman collection from filtered examples.

    Args:
        examples: List of example dictionaries from YAML
        groups: List of group definitions from YAML (for hierarchical structure)
        linked_collection: Linked collection (canonical structure)
        openapi_spec: OpenAPI specification (for deep oneOf structures)
        collection_name: Name for generated collection
        tag_filter: List of tags to filter by (None = include all)
        mode: 'placeholders' or 'examples' (default 'examples')

    Returns:
        Postman collection dictionary
    """
    # Filter examples by tags
    filtered_examples = []
    for example in examples:
        if tag_filter is None:
            filtered_examples.append(example)
        else:
            example_tags = example.get('tags', [])
            if any(tag in example_tags for tag in tag_filter):
                filtered_examples.append(example)

    print(f"Generating '{collection_name}' with {len(filtered_examples)} examples")

    # Create collection structure
    collection = {
        "info": {
            "name": collection_name,
            "description": f"Generated from YAML catalog with tag filter: {tag_filter or 'all'}",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    # Check if this is a Getting Started collection (hierarchical folders)
    is_getting_started = tag_filter and 'getting-started' in tag_filter

    if is_getting_started:
        # Group examples by category (returns list of tuples sorted by order)
        categories = categorize_getting_started_examples(filtered_examples, groups)

        # Process each category as a folder
        for display_name, description, order, category_examples in categories:
            if not category_examples:
                continue

            print(f"  Category: {display_name} ({len(category_examples)} examples)")

            # Create folder for this category with description
            folder = {
                "name": display_name,
                "description": description,
                "item": []
            }

            # Process examples in this category
            validation_errors = []
            validation_warnings = []

            for example in category_examples:
                name = example.get('name')
                method = example.get('method')
                path = example.get('path')

                print(f"    Processing: {name}")

                # Validation 1: Endpoint exists
                valid, msg = validate_endpoint_exists(linked_collection, method, path)
                if not valid:
                    validation_errors.append(f"{name}: {msg}")
                    print(f"      ERROR: {msg}", file=sys.stderr)
                    continue

                # Find canonical request
                canonical_item, canonical_body = find_canonical_request(linked_collection, method, path)

                # Validation 2: Field patchability
                selections = example.get('select', {})
                values = example.get('values', {})
                valid, warnings = validate_field_patchability(canonical_body, values, selections)
                if warnings:
                    for warning in warnings:
                        validation_warnings.append(f"{name}: {warning}")
                        print(f"      WARNING: {warning}", file=sys.stderr)

                # Materialize request body
                request_item = materialize_request_body(canonical_item, example, openapi_spec, mode)

                # Add to folder
                folder['item'].append(request_item)

            # Add folder to collection
            collection['item'].append(folder)

    else:
        # Flat structure for other collections (e.g., Real World)
        validation_errors = []
        validation_warnings = []

        for example in filtered_examples:
            name = example.get('name')
            method = example.get('method')
            path = example.get('path')

            print(f"  Processing: {name}")

            # Validation 1: Endpoint exists
            valid, msg = validate_endpoint_exists(linked_collection, method, path)
            if not valid:
                validation_errors.append(f"{name}: {msg}")
                print(f"    ERROR: {msg}", file=sys.stderr)
                continue

            # Find canonical request
            canonical_item, canonical_body = find_canonical_request(linked_collection, method, path)

            # Validation 2: Field patchability
            selections = example.get('select', {})
            values = example.get('values', {})
            valid, warnings = validate_field_patchability(canonical_body, values, selections)
            if warnings:
                for warning in warnings:
                    validation_warnings.append(f"{name}: {warning}")
                    print(f"    WARNING: {warning}", file=sys.stderr)

            # Materialize request body (clone → select → overlay → filter → placeholders → serialize)
            request_item = materialize_request_body(canonical_item, example, openapi_spec, mode)

            # Add to collection
            collection['item'].append(request_item)

    # Report validation results
    print(f"\nValidation Results for '{collection_name}':")
    print(f"  Errors: {len(validation_errors)}")
    print(f"  Warnings: {len(validation_warnings)}")

    if validation_errors:
        print("\nERRORS (collection generation failed):", file=sys.stderr)
        for error in validation_errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    if validation_warnings:
        print("\nWARNINGS (collection generated with issues):")
        for warning in validation_warnings:
            print(f"  - {warning}")

    return collection


def main():
    parser = argparse.ArgumentParser(
        description='Generate curated Postman collections from YAML catalog (v4)'
    )
    parser.add_argument(
        '--config',
        required=True,
        help='Path to YAML catalog file'
    )
    parser.add_argument(
        '--linked',
        required=True,
        help='Path to Linked Collection (canonical structure)'
    )
    parser.add_argument(
        '--openapi',
        required=True,
        help='Path to OpenAPI specification (for deep oneOf structures)'
    )
    parser.add_argument(
        '--output-dir',
        default='postman/generated/',
        help='Output directory for generated collections'
    )
    parser.add_argument(
        '--tags',
        nargs='+',
        help='Filter examples by tags (e.g., --tags real-world getting-started)'
    )
    parser.add_argument(
        '--output-name',
        help='Output filename (without .json extension)'
    )
    parser.add_argument(
        '--mode',
        choices=['placeholders', 'examples'],
        default='examples',
        help='Generation mode: placeholders (show types) or examples (show values)'
    )

    args = parser.parse_args()

    # Load catalog, linked collection, and OpenAPI spec
    print(f"Loading YAML catalog: {args.config}")
    examples, groups = load_yaml_catalog(args.config)
    print(f"  Loaded {len(examples)} examples, {len(groups)} groups")

    print(f"\nLoading Linked Collection: {args.linked}")
    linked_collection = load_linked_collection(args.linked)
    print(f"  Loaded {len(linked_collection.get('item', []))} endpoints")

    print(f"\nLoading OpenAPI Specification: {args.openapi}")
    openapi_spec = load_openapi_spec(args.openapi)
    print(f"  Loaded {len(openapi_spec.get('components', {}).get('schemas', {}))} component schemas")

    # Generate collection
    tag_filter = args.tags
    if tag_filter:
        collection_name = f"C2M API v2 - {' + '.join(tag_filter).title()}"
        output_name = args.output_name or f"c2mapiv2-{'-'.join(tag_filter)}-collection"
    else:
        collection_name = "C2M API v2 - All Examples"
        output_name = args.output_name or "c2mapiv2-all-examples-collection"

    print(f"\nGenerating collection: {collection_name} (mode={args.mode})")
    collection = generate_collection(examples, groups, linked_collection, openapi_spec, collection_name, tag_filter, args.mode)

    # Write output
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{output_name}.json"
    print(f"\nWriting collection: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(collection, f, indent=2)

    print(f"\nSUCCESS: Generated {len(collection['item'])} requests")
    print(f"Output: {output_path}")


if __name__ == '__main__':
    main()

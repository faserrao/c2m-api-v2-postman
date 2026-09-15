#!/usr/bin/env python3
"""
oneof_resolver.py — Dynamic oneOf variant resolution from OpenAPI spec.

Replaces the hardcoded VARIANT_SCHEMA_MAPPING in generate_curated_collections_v4.py
and variant_mappings in generate_getting_started_collections.py.

Given an OpenAPI spec, a field name (e.g. 'docSourceAll'), and a discriminator key
(e.g. 'requestIdSource'), finds the matching oneOf variant schema by searching for the
discriminator key as a property in each candidate schema. No hardcoded name mappings.

Named-wrapper variants: the translator wraps each oneOf choice in its type name, so
the wire format is { "requestIdSource": { "requestId": 57683 } } rather than flat.
The discriminator_key is therefore the type name (e.g. 'requestIdSource'), not the
leaf field name (e.g. 'requestId').
"""

from typing import Any, Optional, Union


def find_variant_by_discriminator_key(
    spec: dict,
    field_name: str,
    discriminator_key: str,
    max_depth: int = 5
) -> tuple[Optional[str], Optional[dict]]:
    """
    Search the spec for the oneOf variant of `field_name` whose schema contains
    `discriminator_key` as a property.

    Returns (schema_name_or_key, resolved_schema) or (None, None) if not found.

    For named-wrapper variants (inline objects), schema_name is the discriminator_key
    itself and resolved_schema is the inline wrapper object — pass it directly to
    build_variant_placeholder_structure() to get the correct nested structure.

    Handles nested oneOf chains by recursing up to max_depth levels.
    """
    schemas = spec.get('components', {}).get('schemas', {})
    field_schema = schemas.get(field_name)
    if not field_schema:
        return None, None

    return _search_oneof(spec, schemas, field_schema, discriminator_key, max_depth, 0)


def _resolve_ref(schemas: dict, ref: str) -> Optional[dict]:
    """Resolve a $ref string to its schema dict."""
    if not ref.startswith('#/components/schemas/'):
        return None
    name = ref.split('/')[-1]
    return schemas.get(name), name


def _search_oneof(
    spec: dict,
    schemas: dict,
    schema: dict,
    discriminator_key: str,
    max_depth: int,
    depth: int
) -> tuple[Optional[str], Optional[dict]]:
    """Recursively search a schema's oneOf options for discriminator_key."""
    if depth > max_depth:
        return None, None

    oneof = schema.get('oneOf', [])
    for option in oneof:
        ref = option.get('$ref')

        if ref:
            candidate_name = ref.split('/')[-1]
            candidate_schema = schemas.get(candidate_name)
            if not candidate_schema:
                continue

            # Direct match: candidate schema has discriminator_key as a property
            if discriminator_key in candidate_schema.get('properties', {}):
                return candidate_name, candidate_schema

            # Property-prefix match: any property name starts with discriminator_key.
            # Catches renamed properties (e.g. creditCard -> creditCardDetails).
            props = candidate_schema.get('properties', {})
            if props and any(p.lower().startswith(discriminator_key.lower()) for p in props):
                return candidate_name, candidate_schema

            # $ref-alias match: candidate is a pure $ref with no properties/oneOf.
            # Catches single-value aliases: documentIdSource($ref:documentId), etc.
            if ('$ref' in candidate_schema
                    and not candidate_schema.get('properties')
                    and not candidate_schema.get('oneOf')):
                ref_target = candidate_schema['$ref'].split('/')[-1]
                if ref_target.lower() == discriminator_key.lower():
                    return candidate_name, candidate_schema

            # Schema-name match: candidate schema name equals discriminator_key.
            # Mirrors OpenAPI's native discriminator mapping convention.
            if candidate_name.lower() == discriminator_key.lower():
                return candidate_name, candidate_schema

            # Nested oneOf: recurse into this candidate's oneOf options
            if 'oneOf' in candidate_schema:
                result_name, result_schema = _search_oneof(
                    spec, schemas, candidate_schema, discriminator_key, max_depth, depth + 1
                )
                if result_name:
                    return result_name, result_schema

        elif option.get('type') == 'object' and option.get('properties'):
            # Named-wrapper variant: { type: object, properties: { variantName: {$ref} } }
            # The discriminator_key is the wrapper property name (the type name).
            props = option.get('properties', {})
            if discriminator_key in props:
                return discriminator_key, option
            # Also recurse if properties contain a $ref that itself has a oneOf
            for prop_name, prop_schema in props.items():
                if '$ref' in prop_schema:
                    inner_name = prop_schema['$ref'].split('/')[-1]
                    inner_schema = schemas.get(inner_name)
                    if inner_schema and 'oneOf' in inner_schema:
                        result_name, result_schema = _search_oneof(
                            spec, schemas, inner_schema, discriminator_key, max_depth, depth + 1
                        )
                        if result_name:
                            return result_name, result_schema

    return None, None


def build_variant_placeholder_structure(spec: dict, schema_name_or_schema: Union[str, dict]) -> Any:
    """
    Given a resolved schema name or an inline schema dict, recursively build a
    placeholder structure ({"field": "<String>"}, etc.) for use in generated collections.

    Accepts either:
    - A string schema name (looked up from components/schemas)
    - An inline schema dict (e.g. a named-wrapper variant returned by find_variant_by_discriminator_key)

    For named-wrapper variants the inline object has properties: { variantName: {$ref} },
    so _schema_to_placeholder naturally produces { "variantName": { ...fields... } }.
    """
    schemas = spec.get('components', {}).get('schemas', {})
    if isinstance(schema_name_or_schema, dict):
        schema = schema_name_or_schema
    else:
        schema = schemas.get(schema_name_or_schema)
        if not schema:
            return None
    return _schema_to_placeholder(spec, schemas, schema, depth=0, max_depth=10)


def _schema_to_placeholder(
    spec: dict,
    schemas: dict,
    schema: dict,
    depth: int,
    max_depth: int
) -> Any:
    """Recursively convert a resolved schema to a placeholder structure."""
    if depth > max_depth:
        return "<unknown>"

    # Resolve $ref
    if '$ref' in schema:
        ref_name = schema['$ref'].split('/')[-1]
        resolved = schemas.get(ref_name)
        if resolved:
            return _schema_to_placeholder(spec, schemas, resolved, depth + 1, max_depth)
        return "<unknown>"

    schema_type = schema.get('type')

    if schema_type == 'object':
        result = {}
        for prop_name, prop_schema in schema.get('properties', {}).items():
            result[prop_name] = _schema_to_placeholder(
                spec, schemas, prop_schema, depth + 1, max_depth
            )
        return result

    elif schema_type == 'array':
        item_schema = schema.get('items', {})
        item = _schema_to_placeholder(spec, schemas, item_schema, depth + 1, max_depth)
        return [item] if item is not None else []

    elif schema_type == 'string':
        if 'enum' in schema:
            return f"<{'|'.join(schema['enum'])}>"
        return "<String>"

    elif schema_type == 'integer':
        return "<Integer>"

    elif schema_type == 'number':
        return "<Number>"

    elif schema_type == 'boolean':
        return "<Boolean>"

    elif 'oneOf' in schema:
        return "<oneOf>"

    return "<unknown>"

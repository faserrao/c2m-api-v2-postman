#!/usr/bin/env python3
"""
oneof_resolver.py — Dynamic oneOf variant resolution from OpenAPI spec.

Replaces the hardcoded VARIANT_SCHEMA_MAPPING in generate_curated_collections_v4.py
and variant_mappings in generate_getting_started_collections.py.

Given an OpenAPI spec, a field name (e.g. 'docSourceAll'), and a discriminator key
(e.g. 'requestId'), finds the matching oneOf variant schema by searching for the
discriminator key as a property in each candidate schema. No hardcoded name mappings.
"""

from typing import Any, Optional


def find_variant_by_discriminator_key(
    spec: dict,
    field_name: str,
    discriminator_key: str,
    max_depth: int = 5
) -> tuple[Optional[str], Optional[dict]]:
    """
    Search the spec for the oneOf variant of `field_name` whose schema contains
    `discriminator_key` as a property.

    Returns (schema_name, resolved_schema) or (None, None) if not found.

    Handles nested oneOf chains (e.g. docSourceAll -> docSourceStandard ->
    requestIdSource) by recursing up to max_depth levels.
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
        if not ref:
            continue

        candidate_schema = schemas.get(ref.split('/')[-1])
        candidate_name = ref.split('/')[-1]
        if not candidate_schema:
            continue

        # Direct match: candidate schema has discriminator_key as a property
        if discriminator_key in candidate_schema.get('properties', {}):
            return candidate_name, candidate_schema

        # Nested oneOf: recurse into this candidate's oneOf options
        if 'oneOf' in candidate_schema:
            result_name, result_schema = _search_oneof(
                spec, schemas, candidate_schema, discriminator_key, max_depth, depth + 1
            )
            if result_name:
                return result_name, result_schema

    return None, None


def build_variant_placeholder_structure(spec: dict, schema_name: str) -> Any:
    """
    Given a resolved schema name, recursively build a placeholder structure
    ({"field": "<String>"}, etc.) for use in generated collections.

    Mirrors the schema_to_example / build_structure_from_schema logic already
    present in both generators, unified here as the single implementation.
    """
    schemas = spec.get('components', {}).get('schemas', {})
    schema = schemas.get(schema_name)
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

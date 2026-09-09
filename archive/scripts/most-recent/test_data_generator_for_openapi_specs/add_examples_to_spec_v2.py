#!/usr/bin/env python3
"""
OpenAPI Example Generator with Improved OneOf Handling
Version 2: Properly resolves $ref in oneOf schemas

This script adds placeholder examples for schemas and injects default examples
for all `200` responses of `/jobs/...` endpoints, ensuring Prism returns
consistent mock data.
"""

import json
import yaml
import sys
import os
import random
import string
import copy
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta


class RandomDataGenerator:
    """Generate random data for different types with counters to ensure uniqueness."""

    def __init__(self):
        self.counters = {k: 0 for k in ['string', 'integer', 'number', 'email', 'name', 'id', 'url', 'date', 'phone']}
        self.first_names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry']
        self.last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        self.domains = ['example.com', 'test.org', 'demo.net', 'sample.io', 'testsite.com']
        self.words = ['product', 'service', 'item', 'widget', 'component', 'element', 'feature', 'module', 'package', 'resource']

    def generate_string(self, prop_name: str = None, format_type: str = None) -> str:
        if format_type == 'email' or (prop_name and 'email' in prop_name.lower()):
            self.counters['email'] += 1
            return f"{random.choice(self.first_names).lower()}.user{self.counters['email']}@{random.choice(self.domains)}"
        elif format_type in ('uri', 'url') or (prop_name and ('url' in prop_name.lower() or 'uri' in prop_name.lower())):
            self.counters['url'] += 1
            return f"https://api.example.com/v1/resource/{self.counters['url']}"
        elif format_type == 'date' or (prop_name and 'date' in prop_name.lower()):
            return (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
        elif format_type == 'date-time' or (prop_name and 'time' in prop_name.lower()):
            return (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat() + 'Z'
        elif prop_name and ('phone' in prop_name.lower() or 'tel' in prop_name.lower()):
            return f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        elif prop_name and 'name' in prop_name.lower():
            return f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
        elif prop_name and ('id' in prop_name.lower() or 'uuid' in prop_name.lower()):
            self.counters['id'] += 1
            return f"{prop_name or 'id'}-{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        elif prop_name and ('address' in prop_name.lower()):
            return f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Elm'])} Street"
        elif prop_name and 'city' in prop_name.lower():
            return random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston'])
        elif prop_name and 'state' in prop_name.lower():
            return random.choice(['CA', 'TX', 'NY', 'PA'])
        elif prop_name and 'zip' in prop_name.lower():
            return f"{random.randint(10000, 99999)}"
        elif prop_name and 'country' in prop_name.lower():
            return random.choice(['USA', 'Canada', 'UK'])
        self.counters['string'] += 1
        return f"{prop_name or 'string'}-{self.counters['string']}"

    def generate_integer(self, prop_name: str = None, minimum: int = None, maximum: int = None) -> int:
        return random.randint(minimum or 1, maximum or 1000)

    def generate_number(self, prop_name: str = None, minimum: float = None, maximum: float = None) -> float:
        return round(random.uniform(minimum or 1.0, maximum or 1000.0), 2)

    def generate_boolean(self, prop_name: str = None) -> bool:
        return random.choice([True, False])


data_generator = RandomDataGenerator()


class SchemaResolver:
    """Resolves $ref references in OpenAPI schemas."""
    
    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec
        self._cache = {}
    
    def resolve_ref(self, ref: str) -> Optional[Dict[str, Any]]:
        """Resolve a $ref to its schema definition."""
        if ref in self._cache:
            return self._cache[ref]
        
        # Parse the reference path
        if not ref.startswith('#/'):
            return None
        
        path_parts = ref[2:].split('/')
        current = self.spec
        
        try:
            for part in path_parts:
                current = current[part]
            self._cache[ref] = current
            return current
        except (KeyError, TypeError):
            return None


def add_example_to_schema(schema: Dict[str, Any], prop_name: str = None, resolver: SchemaResolver = None) -> Dict[str, Any]:
    if not isinstance(schema, dict):
        return schema
    
    # Don't override existing examples for non-object types
    if 'example' in schema and schema.get('type') != 'object':
        return schema

    # Handle $ref
    if '$ref' in schema:
        # Don't modify $ref schemas directly, just return them
        return schema
    
    # Handle oneOf, anyOf, allOf
    if 'oneOf' in schema:
        # For oneOf, we'll process each option and create a proper example
        example_options = []
        
        for i, option in enumerate(schema['oneOf']):
            if '$ref' in option and resolver:
                # Resolve the reference
                resolved_schema = resolver.resolve_ref(option['$ref'])
                if resolved_schema:
                    # Create a copy and process it
                    resolved_copy = copy.deepcopy(resolved_schema)
                    processed = add_example_to_schema(resolved_copy, prop_name, resolver)
                    if 'example' in processed:
                        example_options.append(processed['example'])
                    elif processed.get('type') == 'string':
                        # For simple types, generate an example
                        example = data_generator.generate_string(prop_name)
                        example_options.append(example)
            else:
                # Process inline schemas
                option_copy = copy.deepcopy(option)
                # For object schemas, we need to resolve their properties' $refs
                if option_copy.get('type') == 'object' and 'properties' in option_copy:
                    # Process each property to resolve refs
                    for prop_key, prop_value in option_copy['properties'].items():
                        if '$ref' in prop_value and resolver:
                            resolved_prop = resolver.resolve_ref(prop_value['$ref'])
                            if resolved_prop:
                                # Replace the $ref with a copy of the resolved schema
                                option_copy['properties'][prop_key] = copy.deepcopy(resolved_prop)
                
                schema['oneOf'][i] = add_example_to_schema(option_copy, prop_name, resolver)
                if 'example' in schema['oneOf'][i]:
                    example_options.append(schema['oneOf'][i]['example'])
        
        # Pick the first valid example or the most complete one
        if example_options:
            # For documentSourceIdentifier, prefer object examples with the most properties
            if prop_name == 'documentSourceIdentifier':
                # Choose an object example if available
                object_examples = [ex for ex in example_options if isinstance(ex, dict) and ex]
                if object_examples:
                    # Sort by number of properties and pick the one with the most
                    schema['example'] = max(object_examples, key=lambda x: len(x))
                else:
                    schema['example'] = example_options[0]
            else:
                schema['example'] = example_options[0]
        
        return schema
    
    if 'anyOf' in schema:
        # Similar to oneOf
        example_options = []
        
        for i, option in enumerate(schema['anyOf']):
            if '$ref' in option and resolver:
                resolved_schema = resolver.resolve_ref(option['$ref'])
                if resolved_schema:
                    resolved_copy = copy.deepcopy(resolved_schema)
                    processed = add_example_to_schema(resolved_copy, prop_name, resolver)
                    if 'example' in processed:
                        example_options.append(processed['example'])
            else:
                option_copy = copy.deepcopy(option)
                schema['anyOf'][i] = add_example_to_schema(option_copy, prop_name, resolver)
                if 'example' in schema['anyOf'][i]:
                    example_options.append(schema['anyOf'][i]['example'])
        
        if example_options:
            schema['example'] = example_options[0]
        
        return schema
    
    if 'allOf' in schema:
        # For allOf, merge examples from all schemas
        merged_example = {}
        for i, option in enumerate(schema['allOf']):
            if '$ref' in option and resolver:
                resolved_schema = resolver.resolve_ref(option['$ref'])
                if resolved_schema:
                    resolved_copy = copy.deepcopy(resolved_schema)
                    processed = add_example_to_schema(resolved_copy, prop_name, resolver)
                    if 'example' in processed and isinstance(processed['example'], dict):
                        merged_example.update(processed['example'])
            else:
                option_copy = copy.deepcopy(option)
                schema['allOf'][i] = add_example_to_schema(option_copy, prop_name, resolver)
                if 'example' in schema['allOf'][i] and isinstance(schema['allOf'][i]['example'], dict):
                    merged_example.update(schema['allOf'][i]['example'])
        
        if merged_example:
            schema['example'] = merged_example
        
        return schema

    # Handle basic types
    schema_type = schema.get('type')
    if schema_type == 'string':
        schema['example'] = data_generator.generate_string(prop_name, schema.get('format'))
    elif schema_type == 'integer':
        schema['example'] = data_generator.generate_integer(prop_name, schema.get('minimum'), schema.get('maximum'))
    elif schema_type == 'number':
        schema['example'] = data_generator.generate_number(prop_name, schema.get('minimum'), schema.get('maximum'))
    elif schema_type == 'boolean':
        schema['example'] = data_generator.generate_boolean(prop_name)
    elif schema_type == 'array':
        if 'items' in schema:
            schema['items'] = add_example_to_schema(schema['items'], prop_name, resolver)
            if 'example' in schema['items']:
                schema['example'] = [schema['items']['example'] for _ in range(2)]
    elif schema_type == 'object':
        if 'properties' in schema:
            example_obj = {}
            for k, v in schema['properties'].items():
                schema['properties'][k] = add_example_to_schema(v, k, resolver)
                if 'example' in schema['properties'][k]:
                    example_obj[k] = schema['properties'][k]['example']
            schema['example'] = example_obj
    return schema


def inject_job_response_example(response: Dict[str, Any]):
    """Inject default example for job-related endpoints' 200 responses."""
    if 'content' in response and 'application/json' in response['content']:
        content = response['content']['application/json']
        content.setdefault('example', {
            "code": 200,
            "jobId": "job-12345",
            "status": "submitted",
            "message": "Job submitted successfully"
        })


def process_request_body(request_body: Dict[str, Any], resolver: SchemaResolver):
    for content_type, content in request_body.get('content', {}).items():
        if 'schema' in content:
            content['schema'] = add_example_to_schema(content['schema'], None, resolver)
            if 'example' not in content:
                content['example'] = content['schema'].get('example', {})


def process_responses(responses: Dict[str, Any], path: str, resolver: SchemaResolver) -> Dict[str, Any]:
    for status, response in responses.items():
        if isinstance(response, dict):
            if status == '200' and path.startswith("/jobs/"):
                inject_job_response_example(response)
            if 'content' in response:
                for content_type, content in response['content'].items():
                    if 'schema' in content:
                        content['schema'] = add_example_to_schema(content['schema'], None, resolver)
                        if 'example' not in content:
                            content['example'] = content['schema'].get('example', {})
    return responses


def process_openapi_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    # Create a schema resolver
    resolver = SchemaResolver(spec)
    
    # First process component schemas to ensure referenced schemas have examples
    if 'components' in spec and 'schemas' in spec['components']:
        for k, schema in spec['components']['schemas'].items():
            spec['components']['schemas'][k] = add_example_to_schema(schema, k, resolver)
    
    # Then process paths which may reference the component schemas
    if 'paths' in spec:
        for path, path_item in spec['paths'].items():
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in path_item:
                    op = path_item[method]
                    if 'responses' in op:
                        op['responses'] = process_responses(op['responses'], path, resolver)
                    if 'requestBody' in op:
                        process_request_body(op['requestBody'], resolver)

    return spec


def main():
    if len(sys.argv) != 2:
        print("Usage: python openapi_example_generator.py <openapi_spec_file>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    output_file = input_file.parent / f"{input_file.stem}-with-examples{input_file.suffix}"
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f) if input_file.suffix.lower() in ('.yaml', '.yml') else json.load(f)
        
        # Process the spec
        modified = process_openapi_spec(spec)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            if input_file.suffix.lower() in ('.yaml', '.yml'):
                yaml.dump(modified, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            else:
                json.dump(modified, f, indent=2, ensure_ascii=False)
        print(f"Successfully created: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
OpenAPI Example Generator with Job Response Defaults

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
from typing import Any, Dict
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


def add_example_to_schema(schema: Dict[str, Any], prop_name: str = None) -> Dict[str, Any]:
    if not isinstance(schema, dict):
        return schema
    if 'example' in schema and schema.get('type') != 'object':
        return schema

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
            schema['items'] = add_example_to_schema(schema['items'], prop_name)
            schema['example'] = [schema['items']['example'] for _ in range(2)]
    elif schema_type == 'object':
        if 'properties' in schema:
            example_obj = {}
            for k, v in schema['properties'].items():
                schema['properties'][k] = add_example_to_schema(v, k)
                example_obj[k] = schema['properties'][k].get('example')
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


def process_request_body(request_body: Dict[str, Any]):
    for content_type, content in request_body.get('content', {}).items():
        if 'schema' in content:
            content['schema'] = add_example_to_schema(content['schema'])
            if 'example' not in content:
                content['example'] = content['schema'].get('example', {})


def process_responses(responses: Dict[str, Any], path: str) -> Dict[str, Any]:
    for status, response in responses.items():
        if isinstance(response, dict):
            if status == '200' and path.startswith("/jobs/"):
                inject_job_response_example(response)
            if 'content' in response:
                for content_type, content in response['content'].items():
                    if 'schema' in content:
                        content['schema'] = add_example_to_schema(content['schema'])
                        if 'example' not in content:
                            content['example'] = content['schema'].get('example', {})
    return responses


def process_openapi_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    if 'paths' in spec:
        for path, path_item in spec['paths'].items():
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in path_item:
                    op = path_item[method]
                    if 'responses' in op:
                        op['responses'] = process_responses(op['responses'], path)
                    if 'requestBody' in op:
                        process_request_body(op['requestBody'])

    if 'components' in spec and 'schemas' in spec['components']:
        for k, schema in spec['components']['schemas'].items():
            spec['components']['schemas'][k] = add_example_to_schema(schema)
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
        modified = process_openapi_spec(spec)
        with open(output_file, 'w', encoding='utf-8') as f:
            if input_file.suffix.lower() in ('.yaml', '.yml'):
                yaml.dump(modified, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            else:
                json.dump(modified, f, indent=2, ensure_ascii=False)
        print(f"Successfully created: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

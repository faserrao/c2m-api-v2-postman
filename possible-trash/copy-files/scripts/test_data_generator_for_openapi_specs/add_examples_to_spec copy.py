#!/usr/bin/env python3
"""
OpenAPI Example Generator

This script takes an OpenAPI specification file (JSON or YAML) as input and adds
minimal placeholder examples for each response schema where examples are missing.
"""

import json
import yaml
import sys
import os
import random
import string
import copy
from pathlib import Path
from typing import Any, Dict, Union
from datetime import datetime, timedelta


class RandomDataGenerator:
    """Generate random data for different types with counters to ensure uniqueness."""
    
    def __init__(self):
        self.counters = {
            'string': 0,
            'integer': 0,
            'number': 0,
            'email': 0,
            'name': 0,
            'id': 0,
            'url': 0,
            'date': 0,
            'phone': 0
        }
        self.first_names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry']
        self.last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        self.domains = ['example.com', 'test.org', 'demo.net', 'sample.io', 'testsite.com']
        self.words = ['product', 'service', 'item', 'widget', 'component', 'element', 'feature', 'module', 'package', 'resource']
    
    def generate_string(self, prop_name: str = None, format_type: str = None) -> str:
        """Generate random string based on property name or format."""
        # Check for specific formats
        if format_type == 'email' or (prop_name and 'email' in prop_name.lower()):
            self.counters['email'] += 1
            first = random.choice(self.first_names).lower()
            return f"{first}.user{self.counters['email']}@{random.choice(self.domains)}"
        
        elif format_type == 'uri' or format_type == 'url' or (prop_name and ('url' in prop_name.lower() or 'uri' in prop_name.lower())):
            self.counters['url'] += 1
            return f"https://api.example.com/v1/resource/{self.counters['url']}"
        
        elif format_type == 'date' or (prop_name and 'date' in prop_name.lower()):
            self.counters['date'] += 1
            base_date = datetime.now() - timedelta(days=365)
            random_days = random.randint(0, 365)
            return (base_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        elif format_type == 'date-time' or (prop_name and 'time' in prop_name.lower()):
            self.counters['date'] += 1
            base_date = datetime.now() - timedelta(days=365)
            random_days = random.randint(0, 365)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            return (base_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)).isoformat() + 'Z'
        
        elif prop_name and ('phone' in prop_name.lower() or 'tel' in prop_name.lower()):
            self.counters['phone'] += 1
            return f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        elif prop_name and 'name' in prop_name.lower():
            self.counters['name'] += 1
            if 'first' in prop_name.lower():
                return random.choice(self.first_names)
            elif 'last' in prop_name.lower():
                return random.choice(self.last_names)
            else:
                return f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
        
        elif prop_name and ('id' in prop_name.lower() or 'uuid' in prop_name.lower()):
            self.counters['id'] += 1
            return f"{prop_name or 'id'}-{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        
        elif prop_name and ('description' in prop_name.lower() or 'desc' in prop_name.lower()):
            words = random.sample(self.words, min(5, len(self.words)))
            return f"This is a {' '.join(words)} description"
        
        elif prop_name and 'title' in prop_name.lower():
            self.counters['string'] += 1
            return f"{random.choice(self.words).capitalize()} {self.counters['string']}"
        
        elif prop_name and ('address' in prop_name.lower() or 'street' in prop_name.lower()):
            self.counters['string'] += 1
            return f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Elm', 'First', 'Second'])} Street"
        
        elif prop_name and ('city' in prop_name.lower()):
            cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego']
            return random.choice(cities)
        
        elif prop_name and ('state' in prop_name.lower() or 'province' in prop_name.lower()):
            states = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI']
            return random.choice(states)
        
        elif prop_name and ('zip' in prop_name.lower() or 'postal' in prop_name.lower()):
            return f"{random.randint(10000, 99999)}"
        
        elif prop_name and ('country' in prop_name.lower()):
            countries = ['USA', 'Canada', 'Mexico', 'UK', 'Germany', 'France', 'Spain', 'Italy']
            return random.choice(countries)
        
        else:
            # Generic string
            self.counters['string'] += 1
            if prop_name:
                return f"{prop_name}-{self.counters['string']}"
            else:
                return f"{random.choice(self.words)}-{self.counters['string']}"
    
    def generate_integer(self, prop_name: str = None, minimum: int = None, maximum: int = None) -> int:
        """Generate random integer."""
        self.counters['integer'] += 1
        
        # Set bounds
        min_val = minimum if minimum is not None else 1
        max_val = maximum if maximum is not None else 10000
        
        # Special cases based on property name
        if prop_name:
            if 'age' in prop_name.lower():
                return random.randint(18, 80)
            elif 'year' in prop_name.lower():
                return random.randint(2000, 2024)
            elif 'quantity' in prop_name.lower() or 'count' in prop_name.lower():
                return random.randint(1, 100)
            elif 'price' in prop_name.lower() or 'cost' in prop_name.lower():
                return random.randint(10, 1000)
            elif 'id' in prop_name.lower():
                return 1000 + self.counters['integer']
        
        return random.randint(min_val, max_val)
    
    def generate_number(self, prop_name: str = None, minimum: float = None, maximum: float = None) -> float:
        """Generate random float number."""
        self.counters['number'] += 1
        
        # Set bounds
        min_val = minimum if minimum is not None else 0.0
        max_val = maximum if maximum is not None else 1000.0
        
        # Special cases based on property name
        if prop_name:
            if 'price' in prop_name.lower() or 'cost' in prop_name.lower() or 'amount' in prop_name.lower():
                return round(random.uniform(10.0, 999.99), 2)
            elif 'rate' in prop_name.lower() or 'percent' in prop_name.lower():
                return round(random.uniform(0.0, 100.0), 2)
            elif 'weight' in prop_name.lower():
                return round(random.uniform(0.1, 100.0), 2)
            elif 'temperature' in prop_name.lower():
                return round(random.uniform(-20.0, 40.0), 1)
            elif 'latitude' in prop_name.lower():
                return round(random.uniform(-90.0, 90.0), 6)
            elif 'longitude' in prop_name.lower():
                return round(random.uniform(-180.0, 180.0), 6)
        
        return round(random.uniform(min_val, max_val), 2)
    
    def generate_boolean(self, prop_name: str = None) -> bool:
        """Generate random boolean."""
        # Bias based on property name
        if prop_name:
            if any(word in prop_name.lower() for word in ['active', 'enabled', 'available', 'valid']):
                return random.random() > 0.3  # 70% chance of True
            elif any(word in prop_name.lower() for word in ['deleted', 'disabled', 'expired']):
                return random.random() > 0.7  # 30% chance of True
        
        return random.choice([True, False])


# Global instance
data_generator = RandomDataGenerator()


def add_example_to_schema(schema: Dict[str, Any], prop_name: str = None) -> Dict[str, Any]:
    """
    Recursively add examples to a schema based on its type.
    """
    if not isinstance(schema, dict):
        return schema
    
    # If schema already has an example, don't override it
    if 'example' in schema:
        return schema
    
    # Handle different schema types
    schema_type = schema.get('type')
    schema_format = schema.get('format')
    minimum = schema.get('minimum')
    maximum = schema.get('maximum')
    
    if schema_type == 'string':
        schema['example'] = data_generator.generate_string(prop_name, schema_format)
    elif schema_type == 'integer':
        schema['example'] = data_generator.generate_integer(prop_name, minimum, maximum)
    elif schema_type == 'number':
        schema['example'] = data_generator.generate_number(prop_name, minimum, maximum)
    elif schema_type == 'boolean':
        schema['example'] = data_generator.generate_boolean(prop_name)
    elif schema_type == 'array':
        # Handle array items
        if 'items' in schema:
            # Generate 2-3 items for the array with different values
            array_examples = []
            for i in range(random.randint(2, 3)):
                # Create a deep copy of the items schema for each element
                item_schema_copy = copy.deepcopy(schema['items'])
                # Remove any existing example to force regeneration
                if 'example' in item_schema_copy:
                    del item_schema_copy['example']
                # Generate new example for this array item
                item_with_example = add_example_to_schema(item_schema_copy, prop_name)
                if 'example' in item_with_example:
                    array_examples.append(item_with_example['example'])
            
            schema['example'] = array_examples if array_examples else []
            # Still process the items schema for structure
            schema['items'] = add_example_to_schema(schema['items'], prop_name)
    elif schema_type == 'object':
        # Handle object properties
        if 'properties' in schema:
            example_obj = {}
            for prop_key, prop_schema in schema['properties'].items():
                schema['properties'][prop_key] = add_example_to_schema(prop_schema, prop_key)
                if 'example' in schema['properties'][prop_key]:
                    example_obj[prop_key] = schema['properties'][prop_key]['example']
            if example_obj:
                schema['example'] = example_obj
    
    # Handle allOf, oneOf, anyOf
    for keyword in ['allOf', 'oneOf', 'anyOf']:
        if keyword in schema:
            schema[keyword] = [add_example_to_schema(sub_schema, prop_name) for sub_schema in schema[keyword]]
    
    # Handle $ref (references) - we don't modify these directly
    # The referenced schemas will be processed when encountered
    
    return schema


def process_responses(responses: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process all responses in a path operation.
    """
    for status_code, response in responses.items():
        if isinstance(response, dict) and 'content' in response:
            for content_type, content in response['content'].items():
                if 'schema' in content:
                    content['schema'] = add_example_to_schema(content['schema'], None)
    
    return responses


def process_openapi_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the entire OpenAPI specification to add examples.
    """
    # Reset counters for each spec processing
    global data_generator
    data_generator = RandomDataGenerator()
    
    # Process paths
    if 'paths' in spec:
        for path, path_item in spec['paths'].items():
            if isinstance(path_item, dict):
                # Process each HTTP method
                for method in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']:
                    if method in path_item and isinstance(path_item[method], dict):
                        operation = path_item[method]
                        # Process responses
                        if 'responses' in operation:
                            operation['responses'] = process_responses(operation['responses'])
                        
                        # Process request body if present
                        if 'requestBody' in operation and 'content' in operation['requestBody']:
                            for content_type, content in operation['requestBody']['content'].items():
                                if 'schema' in content:
                                    content['schema'] = add_example_to_schema(content['schema'], None)
    
    # Process components/schemas
    if 'components' in spec and 'schemas' in spec['components']:
        for schema_name, schema in spec['components']['schemas'].items():
            spec['components']['schemas'][schema_name] = add_example_to_schema(schema, None)
    
    # Process components/responses
    if 'components' in spec and 'responses' in spec['components']:
        spec['components']['responses'] = process_responses(spec['components']['responses'])
    
    return spec


def main():
    if len(sys.argv) != 2:
        print("Usage: python add_examples.py <openapi_spec_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    # Determine file type and create output filename
    input_path = Path(input_file)
    stem = input_path.stem
    suffix = input_path.suffix.lower()
    output_file = input_path.parent / f"{stem}-with-examples{suffix}"
    
    try:
        # Load the OpenAPI specification
        with open(input_file, 'r', encoding='utf-8') as f:
            if suffix == '.yaml' or suffix == '.yml':
                spec = yaml.safe_load(f)
            elif suffix == '.json':
                spec = json.load(f)
            else:
                print(f"Error: Unsupported file type '{suffix}'. Use .yaml, .yml, or .json")
                sys.exit(1)
        
        # Process the specification to add examples
        modified_spec = process_openapi_spec(spec)
        
        # Save the modified specification
        with open(output_file, 'w', encoding='utf-8') as f:
            if suffix == '.yaml' or suffix == '.yml':
                yaml.dump(modified_spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            else:
                json.dump(modified_spec, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created: {output_file}")
        
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
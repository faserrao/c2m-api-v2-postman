#!/usr/bin/env python3
"""
OpenAPI Example Generator with Multiple Examples for OneOf
Version 3: Adds multiple examples for oneOf schemas

This script adds placeholder examples for schemas and injects default examples
for all `200` responses of `/jobs/...` endpoints, ensuring Prism returns
consistent mock data. For oneOf schemas, it creates multiple examples showing
each variant.
"""

import json
import yaml
import sys
import os
import copy
# from collections import OrderedDict

class RefResolver:
    """Simple $ref resolver for OpenAPI specs"""
    def __init__(self, spec):
        self.spec = spec
        
    def resolve_ref(self, ref_path):
        """Resolve a $ref path like #/components/schemas/something"""
        if not ref_path.startswith('#/'):
            return None
            
        # Remove the leading #/ and split by /
        path_parts = ref_path[2:].split('/')
        
        # Navigate through the spec
        current = self.spec
        for part in path_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        return current

def generate_example_value(schema_type, property_name=None, format_hint=None, enum_values=None):
    """Generate an appropriate example value based on the schema type and property name."""
    # Handle enums first
    if enum_values:
        return enum_values[0]
    
    if schema_type == "string":
        # Property name based examples
        if property_name:
            prop_lower = property_name.lower()
            if 'email' in prop_lower:
                return "user@example.com"
            elif 'name' in prop_lower:
                if 'first' in prop_lower:
                    return "John"
                elif 'last' in prop_lower:
                    return "Doe"
                elif 'full' in prop_lower or 'display' in prop_lower:
                    return "John Doe"
                else:
                    return "Sample Name"
            elif 'phone' in prop_lower:
                return "+1-555-123-4567"
            elif 'address' in prop_lower:
                if 'line1' in prop_lower or 'address1' in prop_lower:
                    return "123 Main Street"
                elif 'line2' in prop_lower or 'address2' in prop_lower:
                    return "Suite 100"
                elif 'city' in prop_lower:
                    return "San Francisco"
                elif 'state' in prop_lower:
                    return "CA"
                elif 'zip' in prop_lower or 'postal' in prop_lower:
                    return "94105"
                else:
                    return "123 Example Street"
            elif 'url' in prop_lower or 'uri' in prop_lower:
                return "https://api.example.com/v1/resource"
            elif 'id' in prop_lower:
                if 'job' in prop_lower:
                    return "job_123456"
                elif 'template' in prop_lower:
                    return "template_abc123"
                elif 'document' in prop_lower:
                    return "doc_789xyz"
                else:
                    return "id_" + "abc123"
            elif 'status' in prop_lower:
                return "active"
            elif 'type' in prop_lower:
                return "default"
            elif 'currency' in prop_lower:
                return "USD"
            elif 'country' in prop_lower:
                return "USA"
            elif 'message' in prop_lower:
                return "Operation completed successfully"
            elif 'description' in prop_lower:
                return "Sample description text"
            elif 'token' in prop_lower:
                return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        
        # Format based examples
        if format_hint:
            if format_hint == "date":
                return "2024-01-15"
            elif format_hint == "date-time":
                return "2024-01-15T10:30:00Z"
            elif format_hint == "email":
                return "user@example.com"
            elif format_hint == "uri" or format_hint == "url":
                return "https://api.example.com/v1/resource"
            elif format_hint == "uuid":
                return "123e4567-e89b-12d3-a456-426614174000"
        
        # Default string
        return "string_value"
    
    elif schema_type == "integer":
        if property_name:
            prop_lower = property_name.lower()
            if 'id' in prop_lower:
                return 12345
            elif 'count' in prop_lower or 'quantity' in prop_lower:
                return 10
            elif 'page' in prop_lower:
                return 1
            elif 'limit' in prop_lower:
                return 100
            elif 'year' in prop_lower:
                return 2024
            elif 'month' in prop_lower:
                return 12
            elif 'day' in prop_lower:
                return 15
            elif 'cvv' in prop_lower:
                return 123
            elif 'zip' in prop_lower:
                return 10001
            elif 'check' in prop_lower and 'digit' in prop_lower:
                return 7
        return 123
    
    elif schema_type == "number":
        if property_name:
            prop_lower = property_name.lower()
            if 'price' in prop_lower or 'amount' in prop_lower or 'cost' in prop_lower:
                return 99.99
            elif 'rate' in prop_lower or 'percent' in prop_lower:
                return 0.15
            elif 'latitude' in prop_lower:
                return 37.7749
            elif 'longitude' in prop_lower:
                return -122.4194
        return 123.45
    
    elif schema_type == "boolean":
        return True
    
    elif schema_type == "array":
        return []
    
    elif schema_type == "object":
        return {}
    
    return None

def add_example_to_schema(schema, prop_name=None, resolver=None):
    """Add example values to a schema, handling all schema types including oneOf."""
    if not isinstance(schema, dict):
        return schema
    
    # Handle $ref
    if '$ref' in schema:
        # Don't modify $ref schemas directly, just return them
        return schema
    
    # Handle oneOf - create multiple examples
    if 'oneOf' in schema:
        # For oneOf, we'll create examples showing each variant
        examples = {}
        
        for i, option in enumerate(schema['oneOf']):
            example_value = None
            variant_name = f"variant{i+1}"
            
            if '$ref' in option and resolver:
                # Resolve the reference
                resolved_schema = resolver.resolve_ref(option['$ref'])
                if resolved_schema:
                    # Create a copy and process it
                    resolved_copy = copy.deepcopy(resolved_schema)
                    processed = add_example_to_schema(resolved_copy, prop_name, resolver)
                    if 'example' in processed:
                        example_value = processed['example']
                    elif processed.get('type') == 'string':
                        # Special handling for simple string refs
                        example_value = generate_example_value('string', prop_name)
                    elif processed.get('type') == 'integer':
                        example_value = generate_example_value('integer', prop_name)
                    elif processed.get('type') == 'number':
                        example_value = generate_example_value('number', prop_name)
            else:
                # Process inline schema
                option_copy = copy.deepcopy(option)
                
                # If the option has properties with $ref, resolve them first
                if 'properties' in option_copy:
                    for prop_key, prop_value in option_copy['properties'].items():
                        if isinstance(prop_value, dict) and '$ref' in prop_value and resolver:
                            resolved_prop = resolver.resolve_ref(prop_value['$ref'])
                            if resolved_prop:
                                # Replace the $ref with a copy of the resolved schema
                                option_copy['properties'][prop_key] = copy.deepcopy(resolved_prop)
                
                processed = add_example_to_schema(option_copy, prop_name, resolver)
                if 'example' in processed:
                    example_value = processed['example']
            
            # Special handling for known oneOf fields
            if prop_name == 'documentSourceIdentifier':
                if i == 0:  # documentId
                    example_value = 1234
                    variant_name = "justDocumentId"
                elif i == 1:  # externalUrl
                    example_value = "https://api.example.com/v1/documents/5678"
                    variant_name = "justExternalUrl"
                elif i == 2:  # uploadRequestId + documentName
                    example_value = {
                        "uploadRequestId": 100,
                        "documentName": "invoice_2024_01.pdf"
                    }
                    variant_name = "uploadRequestWithDocument"
                elif i == 3:  # uploadRequestId + zipId + documentName
                    example_value = {
                        "uploadRequestId": 200,
                        "zipId": 10,
                        "documentName": "statement_jan.pdf"
                    }
                    variant_name = "uploadRequestWithZip"
                elif i == 4:  # zipId + documentName
                    example_value = {
                        "zipId": 20,
                        "documentName": "report_q1_2024.pdf"
                    }
                    variant_name = "justZipWithDocument"
            elif prop_name == 'paymentDetails':
                if i == 0:
                    variant_name = "creditCard"
                elif i == 1:
                    variant_name = "invoice"
                elif i == 2:
                    variant_name = "ach"
                elif i == 3:
                    variant_name = "userCredit"
                elif i == 4:
                    variant_name = "applePay"
                elif i == 5:
                    variant_name = "googlePay"
            elif prop_name == 'recipientAddressSource':
                if i == 0:
                    variant_name = "existingAddress"
                elif i == 1:
                    variant_name = "addressList"
                elif i == 2:
                    variant_name = "newAddress"
            
            if example_value is not None:
                examples[variant_name] = {
                    "summary": f"Example using {variant_name}",
                    "value": example_value
                }
        
        # Add the examples to the schema
        if examples:
            schema['examples'] = examples
            # Also add a default example (first variant)
            first_example = next(iter(examples.values()))
            schema['example'] = first_example['value']
        
        return schema
    
    # Handle anyOf similarly
    if 'anyOf' in schema:
        examples = {}
        
        for i, option in enumerate(schema['anyOf']):
            example_value = None
            variant_name = f"option{i+1}"
            
            if '$ref' in option and resolver:
                resolved_schema = resolver.resolve_ref(option['$ref'])
                if resolved_schema:
                    resolved_copy = copy.deepcopy(resolved_schema)
                    processed = add_example_to_schema(resolved_copy, prop_name, resolver)
                    if 'example' in processed:
                        example_value = processed['example']
            else:
                option_copy = copy.deepcopy(option)
                processed = add_example_to_schema(option_copy, prop_name, resolver)
                if 'example' in processed:
                    example_value = processed['example']
            
            if example_value is not None:
                examples[variant_name] = {
                    "summary": f"Example using option {i+1}",
                    "value": example_value
                }
        
        if examples:
            schema['examples'] = examples
            first_example = next(iter(examples.values()))
            schema['example'] = first_example['value']
        
        return schema
    
    # Handle allOf
    if 'allOf' in schema:
        combined_example = {}
        
        for option in schema['allOf']:
            if '$ref' in option and resolver:
                resolved_schema = resolver.resolve_ref(option['$ref'])
                if resolved_schema:
                    resolved_copy = copy.deepcopy(resolved_schema)
                    processed = add_example_to_schema(resolved_copy, prop_name, resolver)
                    if 'example' in processed and isinstance(processed['example'], dict):
                        combined_example.update(processed['example'])
            else:
                option_copy = copy.deepcopy(option)
                processed = add_example_to_schema(option_copy, prop_name, resolver)
                if 'example' in processed and isinstance(processed['example'], dict):
                    combined_example.update(processed['example'])
        
        if combined_example:
            schema['example'] = combined_example
        
        return schema
    
    # If schema already has an example, don't override
    if 'example' in schema:
        return schema
    
    # Handle different schema types
    schema_type = schema.get('type', None)
    
    if schema_type == 'object':
        if 'properties' in schema:
            example_obj = {}
            for prop, prop_schema in schema['properties'].items():
                # Handle $ref in properties
                if isinstance(prop_schema, dict) and '$ref' in prop_schema and resolver:
                    resolved_schema = resolver.resolve_ref(prop_schema['$ref'])
                    if resolved_schema:
                        prop_schema_copy = copy.deepcopy(resolved_schema)
                        prop_with_example = add_example_to_schema(prop_schema_copy, prop, resolver)
                        if 'example' in prop_with_example:
                            example_obj[prop] = prop_with_example['example']
                        else:
                            # Generate based on type
                            prop_type = prop_with_example.get('type', 'string')
                            example_obj[prop] = generate_example_value(prop_type, prop)
                else:
                    # Recursively add examples to nested schemas
                    prop_with_example = add_example_to_schema(prop_schema, prop, resolver)
                    if 'example' in prop_with_example:
                        example_obj[prop] = prop_with_example['example']
                    elif 'type' in prop_with_example:
                        example_obj[prop] = generate_example_value(
                            prop_with_example['type'], 
                            prop,
                            prop_with_example.get('format'),
                            prop_with_example.get('enum')
                        )
            
            if example_obj:
                schema['example'] = example_obj
    
    elif schema_type == 'array':
        if 'items' in schema:
            item_with_example = add_example_to_schema(schema['items'], None, resolver)
            if 'example' in item_with_example:
                schema['example'] = [item_with_example['example']]
            elif 'type' in item_with_example:
                schema['example'] = [generate_example_value(item_with_example['type'])]
    
    elif schema_type:
        # Primitive types
        schema['example'] = generate_example_value(
            schema_type, 
            prop_name, 
            schema.get('format'),
            schema.get('enum')
        )
    
    return schema

def add_examples_to_spec(spec):
    """Add examples to all schemas in the spec."""
    resolver = RefResolver(spec)
    
    # Add examples to schemas
    if 'components' in spec and 'schemas' in spec['components']:
        for schema_name, schema in spec['components']['schemas'].items():
            spec['components']['schemas'][schema_name] = add_example_to_schema(
                schema, schema_name, resolver
            )
    
    # Add examples to request bodies
    if 'components' in spec and 'requestBodies' in spec['components']:
        for rb_name, rb in spec['components']['requestBodies'].items():
            if 'content' in rb:
                for content_type, content in rb['content'].items():
                    if 'schema' in content:
                        content['schema'] = add_example_to_schema(
                            content['schema'], rb_name, resolver
                        )
    
    # Add examples to paths
    if 'paths' in spec:
        for path, path_item in spec['paths'].items():
            for method in ['get', 'post', 'put', 'delete', 'patch']:
                if method in path_item:
                    operation = path_item[method]
                    
                    # Add examples to request body
                    if 'requestBody' in operation and 'content' in operation['requestBody']:
                        for content_type, content in operation['requestBody']['content'].items():
                            if 'schema' in content:
                                content['schema'] = add_example_to_schema(
                                    content['schema'], None, resolver
                                )
                    
                    # Add examples to responses
                    if 'responses' in operation:
                        for status, response in operation['responses'].items():
                            if 'content' in response:
                                for content_type, content in response['content'].items():
                                    if 'schema' in content:
                                        content['schema'] = add_example_to_schema(
                                            content['schema'], None, resolver
                                        )
                                    
                                    # Special handling for 200 responses on /jobs endpoints
                                    if status == '200' and path.startswith('/jobs/'):
                                        if 'examples' not in content:
                                            content['examples'] = {}
                                        
                                        # Add a default example if none exists
                                        if 'default' not in content['examples']:
                                            if 'example' in content.get('schema', {}):
                                                content['examples']['default'] = {
                                                    'summary': 'Default response',
                                                    'value': content['schema']['example']
                                                }
    
    return spec

def main():
    if len(sys.argv) != 3:
        print("Usage: add_examples_to_spec_v3.py <input.yaml> <output.yaml>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Read the spec
    with open(input_file, 'r') as f:
        spec = yaml.safe_load(f)
    
    # Add examples
    spec_with_examples = add_examples_to_spec(spec)
    
    # Write the result
    with open(output_file, 'w') as f:
        yaml.dump(spec_with_examples, f, 
                  default_flow_style=False, 
                  allow_unicode=True,
                  sort_keys=False)
    
    print(f"✅ Added examples to {output_file}")

if __name__ == '__main__':
    main()
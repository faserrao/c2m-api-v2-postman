#!/usr/bin/env python3
"""
fix_openapi_oneOf_schemas.py

Post-processes OpenAPI spec to convert anonymous oneOf schemas to named schemas.
This runs after EBNF to OpenAPI conversion to ensure proper oneOf handling.
"""

import yaml
import sys
import copy

def fix_documentSourceIdentifier_oneOf(spec):
    """Fix anonymous oneOf schemas in documentSourceIdentifier"""
    if 'components' not in spec or 'schemas' not in spec['components']:
        return spec
    
    schemas = spec['components']['schemas']
    
    # Check if documentSourceIdentifier exists and has anonymous oneOf schemas
    if 'documentSourceIdentifier' in schemas and 'oneOf' in schemas['documentSourceIdentifier']:
        oneOf_list = schemas['documentSourceIdentifier']['oneOf']
        new_oneOf = []
        
        for i, variant in enumerate(oneOf_list):
            if '$ref' in variant:
                # Already a reference, keep it
                new_oneOf.append(variant)
            elif 'type' in variant and variant['type'] == 'object':
                # Anonymous object schema - create named schema
                props = variant.get('properties', {})
                
                # Determine schema name based on properties
                if 'uploadRequestId' in props and 'zipId' in props:
                    schema_name = 'DocumentSourceWithUploadAndZip'
                elif 'uploadRequestId' in props:
                    schema_name = 'DocumentSourceWithUpload'
                elif 'zipId' in props:
                    schema_name = 'DocumentSourceFromZip'
                else:
                    schema_name = f'DocumentSourceVariant{i+1}'
                
                # Add the schema if it doesn't exist
                if schema_name not in schemas:
                    schemas[schema_name] = copy.deepcopy(variant)
                    schemas[schema_name]['description'] = f'OneOf variant for documentSourceIdentifier'
                
                # Replace with reference
                new_oneOf.append({'$ref': f'#/components/schemas/{schema_name}'})
            else:
                # Keep as is
                new_oneOf.append(variant)
        
        # Update the oneOf list
        schemas['documentSourceIdentifier']['oneOf'] = new_oneOf
    
    return spec

def main():
    if len(sys.argv) < 3:
        print("Usage: python fix_openapi_oneOf_schemas.py <input.yaml> <output.yaml>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Load the OpenAPI spec
    print(f"Loading OpenAPI spec from {input_file}...")
    with open(input_file, 'r') as f:
        spec = yaml.safe_load(f)
    
    # Fix oneOf schemas
    print("Fixing anonymous oneOf schemas...")
    spec = fix_documentSourceIdentifier_oneOf(spec)
    
    # Save the fixed spec
    print(f"Saving fixed spec to {output_file}...")
    with open(output_file, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, width=1000)
    
    print("✅ OneOf schemas fixed")

if __name__ == '__main__':
    main()
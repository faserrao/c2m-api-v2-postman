#!/usr/bin/env python3
"""
Add meaningful example responses to OpenAPI spec
Specifically targets StandardResponse to provide better mock data
"""

import yaml
import sys
import copy
from datetime import datetime, timezone

def add_response_examples(spec):
    """Add example values to StandardResponse and response schemas"""
    
    # Add examples to StandardResponse schema
    if 'components' in spec and 'schemas' in spec['components']:
        schemas = spec['components']['schemas']
        
        # Add examples to StandardResponse
        if 'StandardResponse' in schemas:
            schemas['StandardResponse']['example'] = {
                'status': 'success',
                'message': 'Job created successfully',
                'jobId': 'job_20241227_123456'
            }
        
        # Don't add 'examples' to schema level - only 'example' is valid
        # Multiple examples should be added at the media type level, not schema level
    
    # Add examples to all job endpoints
    if 'paths' in spec:
        for path, methods in spec['paths'].items():
            if '/jobs/' in path:
                for method, operation in methods.items():
                    if method in ['post', 'get', 'put', 'delete']:
                        # Add examples to 200 responses
                        if 'responses' in operation and '200' in operation['responses']:
                            response = operation['responses']['200']
                            if 'content' in response and 'application/json' in response['content']:
                                json_response = response['content']['application/json']
                                
                                # Add example if it references StandardResponse
                                if 'schema' in json_response and '$ref' in json_response['schema']:
                                    if 'StandardResponse' in json_response['schema']['$ref']:
                                        # Create endpoint-specific example
                                        endpoint_name = path.split('/')[-1].replace('-', '_')
                                        json_response['example'] = {
                                            'status': 'success',
                                            'message': f'{endpoint_name} job created successfully',
                                            'jobId': f'job_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}'
                                        }
                                        
                                        # Also add multiple examples
                                        json_response['examples'] = {
                                            'success': {
                                                'summary': 'Successful job creation',
                                                'value': {
                                                    'status': 'success',
                                                    'message': f'{endpoint_name} job created successfully',
                                                    'jobId': f'{endpoint_name}_job_123456'
                                                }
                                            },
                                            'queued': {
                                                'summary': 'Job queued for processing',
                                                'value': {
                                                    'status': 'queued',
                                                    'message': f'{endpoint_name} job queued for processing',
                                                    'jobId': f'{endpoint_name}_job_789012'
                                                }
                                            }
                                        }
    
    return spec

def main():
    if len(sys.argv) != 3:
        print("Usage: python add_response_examples.py <input.yaml> <output.yaml>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Load the OpenAPI spec
    with open(input_file, 'r') as f:
        spec = yaml.safe_load(f)
    
    # Add examples
    spec = add_response_examples(spec)
    
    # Save the updated spec
    with open(output_file, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, width=1000)
    
    print(f"✅ Added response examples to {output_file}")

if __name__ == '__main__':
    main()
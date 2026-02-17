#!/usr/bin/env python3
"""
Add meaningful example responses to OpenAPI spec
Specifically targets StandardResponse to provide better mock data
Adds both SUCCESS and ERROR response examples for mock server variety
"""

import yaml
import sys
import copy
import random
import string
from datetime import datetime, timezone

def extract_error_code_enum(spec):
    """
    Extract valid errorCode enum values from OpenAPI spec.

    The OpenAPI spec is generated from EBNF data dictionary, which is the
    single source of truth for errorCode values. This function reads the
    authoritative enum to validate hardcoded examples.

    Returns:
        list: Valid errorCode enum values, or empty list if not found
    """
    try:
        if 'components' in spec and 'schemas' in spec['components']:
            if 'errorCode' in spec['components']['schemas']:
                error_code_schema = spec['components']['schemas']['errorCode']
                if 'enum' in error_code_schema:
                    return error_code_schema['enum']
    except (KeyError, TypeError):
        pass
    return []

def validate_error_examples(spec, error_examples):
    """
    Validate that all errorCode values in ERROR_EXAMPLES match the EBNF enum.

    This ensures the script stays synchronized with the EBNF data dictionary.
    If validation fails, the script will exit with a clear error message.

    Args:
        spec: OpenAPI specification dictionary
        error_examples: ERROR_EXAMPLES dictionary to validate

    Returns:
        bool: True if all errorCode values are valid

    Raises:
        SystemExit: If any errorCode values don't match EBNF enum
    """
    valid_codes = extract_error_code_enum(spec)

    if not valid_codes:
        print("⚠️  WARNING: Could not extract errorCode enum from OpenAPI spec")
        print("    Skipping validation - ensure EBNF errorCode definition exists")
        return False

    print(f"✓ Found {len(valid_codes)} valid errorCode values in EBNF enum")

    # Collect all errorCode values used in examples
    invalid_codes = []
    for http_code, examples in error_examples.items():
        for example_name, example_data in examples.items():
            error_code = example_data['value'].get('errorCode')
            if error_code and error_code not in valid_codes:
                invalid_codes.append({
                    'http_code': http_code,
                    'example': example_name,
                    'invalid_value': error_code
                })

    if invalid_codes:
        print("\n❌ ERROR: Found errorCode values that don't match EBNF enum:")
        for item in invalid_codes:
            print(f"   - HTTP {item['http_code']} ({item['example']}): '{item['invalid_value']}'")
        print(f"\nValid errorCode values from EBNF:")
        for code in valid_codes:
            print(f"   - {code}")
        print("\nFix: Update ERROR_EXAMPLES dictionary to use valid EBNF errorCode values")
        sys.exit(1)

    print(f"✓ All errorCode values in ERROR_EXAMPLES are valid")
    return True

# Error example templates (realistic data, not placeholders)
# NOTE: errorCode values MUST match the enum defined in EBNF data dictionary
# Validation runs automatically on every execution to ensure synchronization
ERROR_EXAMPLES = {
    '400': {
        'missing_field': {
            'summary': 'Missing required field',
            'value': {
                'errorType': 'ValidationError',
                'errorMessage': 'Required field is missing from request body',
                'errorCode': 'MISSING_REQUIRED_FIELD',
                'errorDetails': '{"field": "documentId", "location": "requestBody"}',
                'errorTrackingId': 'TRK-20260216-ABC123'
            }
        },
        'invalid_format': {
            'summary': 'Invalid field format',
            'value': {
                'errorType': 'ValidationError',
                'errorMessage': 'Field contains invalid format or value',
                'errorCode': 'INVALID_FORMAT',
                'errorDetails': '{"field": "postalCode", "provided": "1234", "expected": "5 or 9 digits"}',
                'errorTrackingId': 'TRK-20260216-DEF456'
            }
        }
    },
    '401': {
        'missing_token': {
            'summary': 'Missing authentication',
            'value': {
                'errorType': 'AuthenticationError',
                'errorMessage': 'Authorization header is missing or invalid',
                'errorCode': 'MISSING_AUTH_HEADER',
                'errorDetails': '{"expected": "Bearer <token>", "received": "none"}',
                'errorTrackingId': 'TRK-20260216-GHI789'
            }
        }
    },
    '403': {
        'insufficient_permissions': {
            'summary': 'Insufficient permissions',
            'value': {
                'errorType': 'AuthorizationError',
                'errorMessage': 'User does not have required permissions for this operation',
                'errorCode': 'INSUFFICIENT_PERMISSIONS',
                'errorDetails': '{"required": "jobs:write", "user": "read-only-user"}',
                'errorTrackingId': 'TRK-20260216-JKL012'
            }
        }
    },
    '404': {
        'resource_not_found': {
            'summary': 'Resource not found',
            'value': {
                'errorType': 'ResourceNotFoundError',
                'errorMessage': 'Requested resource does not exist',
                'errorCode': 'RESOURCE_NOT_FOUND',
                'errorDetails': '{"resourceType": "document", "resourceId": "DOC-12345"}',
                'errorTrackingId': 'TRK-20260216-MNO345'
            }
        }
    },
    '422': {
        'validation_failed': {
            'summary': 'Validation failed',
            'value': {
                'errorType': 'ValidationError',
                'errorMessage': 'Request validation failed for multiple fields',
                'errorCode': 'INVALID_FORMAT',
                'errorDetails': '{"errors": [{"field": "documentId", "issue": "not found"}, {"field": "recipientAddress.postalCode", "issue": "invalid format"}]}',
                'errorTrackingId': 'TRK-20260216-PQR678'
            }
        }
    },
    '500': {
        'server_error': {
            'summary': 'Internal server error',
            'value': {
                'errorType': 'ServerError',
                'errorMessage': 'An unexpected error occurred while processing the request',
                'errorCode': 'SERVER_ERROR',
                'errorDetails': '{"timestamp": "2026-02-16T18:30:45Z", "requestId": "req-abc123"}',
                'errorTrackingId': 'TRK-20260216-STU901'
            }
        }
    }
}

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
                'requestId': 'job_20241227_123456'
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
                                        
                                        # Only add 'examples' (not 'example') to avoid validation issues
                                        json_response['examples'] = {
                                            'success': {
                                                'summary': 'Successful job creation',
                                                'value': {
                                                    'status': 'success',
                                                    'message': f'{endpoint_name} job created successfully',
                                                    'requestId': f'{endpoint_name}_job_123456'
                                                }
                                            },
                                            'queued': {
                                                'summary': 'Job queued for processing',
                                                'value': {
                                                    'status': 'queued',
                                                    'message': f'{endpoint_name} job queued for processing',
                                                    'requestId': f'{endpoint_name}_job_789012'
                                                }
                                            }
                                        }

                                        # Add error examples to error responses (400, 401, 403, 404, 422, 500)
                                        for error_code in ['400', '401', '403', '404', '422', '500']:
                                            if error_code in operation['responses']:
                                                error_response = operation['responses'][error_code]
                                                if 'content' in error_response and 'application/json' in error_response['content']:
                                                    error_json = error_response['content']['application/json']

                                                    # Add error examples from ERROR_EXAMPLES dictionary
                                                    if error_code in ERROR_EXAMPLES:
                                                        error_json['examples'] = ERROR_EXAMPLES[error_code]

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

    # Validate errorCode values against EBNF enum (via OpenAPI spec)
    print("\n🔍 Validating errorCode values against EBNF data dictionary...")
    validate_error_examples(spec, ERROR_EXAMPLES)

    # Add examples
    spec = add_response_examples(spec)

    # Save the updated spec
    with open(output_file, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, width=1000)

    print(f"✅ Added response examples to {output_file}")

if __name__ == '__main__':
    main()
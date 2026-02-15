#!/usr/bin/env python3
"""
Add meaningful example responses to OpenAPI spec
Specifically targets StandardResponse and error responses to provide better mock data
"""

import yaml
import sys
import copy
import random
import string
from datetime import datetime, timezone

# Error examples dictionary - maps status codes to example lists
ERROR_EXAMPLES = {
    '400': [  # Bad Request
        {
            'errorType': 'ValidationError',
            'errorMessage': 'Missing required field in request',
            'errorCode': 'MISSING_REQUIRED_FIELD',
            'errorDetails': '{{"field": "{field}", "location": "requestBody"}}'
        },
        {
            'errorType': 'ValidationError',
            'errorMessage': 'Invalid oneOf field selection',
            'errorCode': 'INVALID_ONEOF',
            'errorDetails': '{{"field": "documentSourceIdentifier", "validOptions": ["documentId", "requestId", "url", "zipDocumentId", "zipRequestId"]}}'
        },
        {
            'errorType': 'ValidationError',
            'errorMessage': 'Malformed JSON in request body',
            'errorCode': 'INVALID_JSON',
            'errorDetails': '{{"parseError": "Unexpected token at line 5", "column": 12}}'
        }
    ],
    '401': [  # Unauthorized
        {
            'errorType': 'AuthenticationError',
            'errorMessage': 'Authentication header is missing',
            'errorCode': 'MISSING_AUTH_HEADER',
            'errorDetails': '{{"requiredHeader": "Authorization", "format": "Bearer <token>"}}'
        },
        {
            'errorType': 'AuthenticationError',
            'errorMessage': 'Invalid or expired authentication token',
            'errorCode': 'INVALID_TOKEN',
            'errorDetails': '{{"reason": "Token signature verification failed", "expiresAt": "2026-02-15T10:30:00Z"}}'
        }
    ],
    '403': [  # Forbidden
        {
            'errorType': 'AuthorizationError',
            'errorMessage': 'Insufficient permissions for this operation',
            'errorCode': 'INSUFFICIENT_PERMISSIONS',
            'errorDetails': '{{"requiredPermission": "jobs:submit", "userPermissions": ["jobs:read"]}}'
        },
        {
            'errorType': 'AuthorizationError',
            'errorMessage': 'Account has been suspended',
            'errorCode': 'ACCOUNT_SUSPENDED',
            'errorDetails': '{{"reason": "Payment overdue", "suspendedSince": "2026-02-01", "contactSupport": "support@click2mail.com"}}'
        }
    ],
    '404': [  # Not Found
        {
            'errorType': 'ResourceNotFoundError',
            'errorMessage': 'Resource not found',
            'errorCode': 'RESOURCE_NOT_FOUND',
            'errorDetails': '{{"resourceType": "{resourceType}", "resourceId": "{resourceId}"}}'
        },
        {
            'errorType': 'ResourceNotFoundError',
            'errorMessage': 'Job not found',
            'errorCode': 'JOB_NOT_FOUND',
            'errorDetails': '{{"jobId": "job_20260215_999999", "possibleReasons": ["Invalid ID", "Job expired", "Job deleted"]}}'
        }
    ],
    '422': [  # Unprocessable Entity
        {
            'errorType': 'ValidationError',
            'errorMessage': 'Validation failed for multiple fields',
            'errorCode': 'INVALID_FORMAT',
            'errorDetails': '{{"errors": [{{"field": "{field1}", "issue": "not found in document library"}}, {{"field": "recipientAddress.postalCode", "issue": "invalid format - must be 5 or 9 digits"}}]}}'
        },
        {
            'errorType': 'ValidationError',
            'errorMessage': 'Business rule violation detected',
            'errorCode': 'MUTUAL_EXCLUSION_VIOLATION',
            'errorDetails': '{{"violation": "Cannot specify both jobTemplate and jobOptions", "conflictingFields": ["jobTemplate", "jobOptions"], "resolution": "Remove one of the conflicting fields"}}'
        },
        {
            'errorType': 'ValidationError',
            'errorMessage': 'Invalid enum value provided',
            'errorCode': 'INVALID_ENUM_VALUE',
            'errorDetails': '{{"field": "paymentDetails.cardType", "providedValue": "mastercard", "validValues": ["visa", "mastercard", "discover", "americanExpress"]}}'
        }
    ],
    '500': [  # Internal Server Error
        {
            'errorType': 'ServerError',
            'errorMessage': 'An unexpected server error occurred',
            'errorCode': 'SERVER_ERROR',
            'errorDetails': '{{"message": "Internal processing error", "retryAfter": 60}}'
        },
        {
            'errorType': 'ServerError',
            'errorMessage': 'Database operation failed',
            'errorCode': 'DATABASE_ERROR',
            'errorDetails': '{{"operation": "INSERT", "table": "jobs", "retryRecommended": true}}'
        },
        {
            'errorType': 'ServerError',
            'errorMessage': 'External service temporarily unavailable',
            'errorCode': 'EXTERNAL_SERVICE_ERROR',
            'errorDetails': '{{"service": "payment-processor", "status": "timeout", "retryAfter": 120}}'
        }
    ]
}

def generate_tracking_id():
    """Generate a unique tracking ID for error responses"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TRK-{datetime.now().strftime('%Y%m%d')}-{suffix}"

def extract_endpoint_fields(spec, path):
    """Extract critical field names from endpoint's request body schema"""
    fields = {
        'field': 'docSourceAll',  # Default most common field
        'field1': 'documentId',   # Default for multi-field errors
        'resourceType': 'document',  # Default resource type
        'resourceId': 'DOC-12345'   # Default resource ID
    }

    try:
        # Navigate to the path's POST operation
        if 'paths' in spec and path in spec['paths']:
            operation = spec['paths'][path].get('post', {})
            request_body = operation.get('requestBody', {})
            content = request_body.get('content', {}).get('application/json', {})
            schema_ref = content.get('schema', {}).get('$ref', '')

            if schema_ref:
                # Extract schema name from $ref
                schema_name = schema_ref.split('/')[-1]

                # Get schema properties
                if 'components' in spec and 'schemas' in spec['components']:
                    schema = spec['components']['schemas'].get(schema_name, {})
                    properties = schema.get('properties', {})

                    # Identify document source field
                    if 'docSourceAll' in properties:
                        fields['field'] = 'docSourceAll'
                        fields['field1'] = 'documentId'
                    elif 'docSourceStandard' in properties:
                        fields['field'] = 'docSourceStandard'
                        fields['field1'] = 'documentId'
                    elif 'docSourceZipFile' in properties:
                        fields['field'] = 'docSourceZipFile'
                        fields['field1'] = 'zipDocumentId'
                    elif 'zipDocumentSource' in properties:
                        fields['field'] = 'zipDocumentSource'
                        fields['field1'] = 'zipDocumentId'

                    # Set resource type based on endpoint
                    if 'doc' in path:
                        fields['resourceType'] = 'document'
                        fields['resourceId'] = 'DOC-12345'
                    elif 'address' in path:
                        fields['resourceType'] = 'addressList'
                        fields['resourceId'] = 'ADDR-67890'
                    elif 'template' in path:
                        fields['resourceType'] = 'jobTemplate'
                        fields['resourceId'] = 'TMPL-54321'
    except Exception as e:
        # If extraction fails, use defaults
        pass

    return fields

def add_error_examples_to_response(spec, path, error_code):
    """Generate error examples for a specific status code and endpoint"""
    if error_code not in ERROR_EXAMPLES:
        return None

    # Extract endpoint-specific fields
    endpoint_fields = extract_endpoint_fields(spec, path)

    # Get examples for this error code
    examples_list = ERROR_EXAMPLES[error_code]

    # Build examples dictionary
    examples = {}
    for idx, example_template in enumerate(examples_list, 1):
        # Create a copy of the template
        example = copy.deepcopy(example_template)

        # Add tracking ID
        example['errorTrackingId'] = generate_tracking_id()

        # Replace placeholders in errorDetails
        error_details = example['errorDetails']
        for placeholder, value in endpoint_fields.items():
            error_details = error_details.replace(f'{{{placeholder}}}', value)
        example['errorDetails'] = error_details

        # Create example entry
        example_name = f'example{idx}' if len(examples_list) > 1 else 'error'
        examples[example_name] = {
            'summary': example['errorMessage'],
            'value': example
        }

    return examples

def add_response_examples(spec):
    """Add example values to StandardResponse and error response schemas"""

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

    # Add examples to all job endpoints
    if 'paths' in spec:
        for path, methods in spec['paths'].items():
            if '/jobs/' in path:
                for method, operation in methods.items():
                    if method in ['post', 'get', 'put', 'delete']:
                        if 'responses' not in operation:
                            continue

                        # Add examples to 200 responses
                        if '200' in operation['responses']:
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

                        # Add examples to error responses (400, 401, 403, 404, 422, 500)
                        for error_code in ['400', '401', '403', '404', '422', '500']:
                            if error_code in operation['responses']:
                                error_response = operation['responses'][error_code]
                                if 'content' in error_response and 'application/json' in error_response['content']:
                                    json_response = error_response['content']['application/json']

                                    # Generate and add error examples
                                    error_examples = add_error_examples_to_response(spec, path, error_code)
                                    if error_examples:
                                        json_response['examples'] = error_examples

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

    print(f"Added response examples to {output_file}")

if __name__ == '__main__':
    main()

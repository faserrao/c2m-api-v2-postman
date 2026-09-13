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
from datetime import datetime, timezone, timedelta
from pathlib import Path

def _generate_tracking_id():
    suffix = ''.join(random.choices('0123456789ABCDEF', k=6))
    return f"TRK-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{suffix}"


def _load_error_examples(examples_path):
    """Load ERROR_EXAMPLES from config/error-response-examples.yaml.

    Converts the flat YAML structure into the OpenAPI examples dict format.
    Substitutes {timestamp} with the current UTC time and {expired} with 1 hour ago.
    """
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    expired = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    request_id = f"req-{''.join(random.choices('0123456789abcdef', k=8))}"
    with open(examples_path, 'r') as f:
        raw = yaml.safe_load(f)
    result = {}
    for http_status, examples in raw.items():
        result[str(http_status)] = {}
        for ex_key, ex_data in examples.items():
            details = ex_data.get('errorDetails', '{}')
            if '{timestamp}' in details:
                details = details.replace('{timestamp}', now)
            if '{expired}' in details:
                details = details.replace('{expired}', expired)
            if '{requestId}' in details:
                details = details.replace('{requestId}', request_id)
            result[str(http_status)][ex_key] = {
                'summary': ex_data['summary'],
                'value': {
                    'errorMessage': ex_data['errorMessage'],
                    'errorCode': ex_data['errorCode'],
                    'errorDetails': details
                }
            }
    return result


def extract_http_error_map(spec):
    """Read the x-http-error-map extension from the OpenAPI spec info block.

    This extension is injected by ebnf_to_openapi_dynamic_v3.py, which parses it
    from the @http_error_map annotation block in the EBNF data dictionary.
    Returns dict keyed by HTTP status string: {'400': {'errorType': '...', 'errorCodes': [...]}}.
    """
    raw = spec.get('info', {}).get('x-http-error-map', {})
    return {str(k): v for k, v in raw.items()}


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

def extract_error_type_enum(spec):
    """
    Extract valid errorType enum values from OpenAPI spec.

    The OpenAPI spec is generated from EBNF data dictionary, which is the
    single source of truth for errorType values.

    Returns:
        list: Valid errorType enum values, or empty list if not found
    """
    try:
        if 'components' in spec and 'schemas' in spec['components']:
            if 'errorType' in spec['components']['schemas']:
                error_type_schema = spec['components']['schemas']['errorType']
                if 'enum' in error_type_schema:
                    return error_type_schema['enum']
    except (KeyError, TypeError):
        pass
    return []

def validate_error_examples(spec, error_examples):
    """Validate that errorCode values in ERROR_EXAMPLES match the EBNF enum.

    errorType is no longer validated here — it is derived from x-http-error-map
    (injected into the spec by ebnf_to_openapi_dynamic_v3.py from the EBNF
    @http_error_map block) and is never stored in ERROR_EXAMPLES.

    Raises:
        SystemExit: If any errorCode value doesn't match the EBNF enum.
    """
    valid_codes = extract_error_code_enum(spec)

    if not valid_codes:
        print("⚠️  WARNING: Could not extract errorCode enum from OpenAPI spec")
        print("    Skipping validation - ensure EBNF errorCode definition exists")
        return False

    print(f"✓ Found {len(valid_codes)} valid errorCode values in EBNF enum")

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


def build_effective_error_examples(spec, error_examples):
    """Merge ERROR_EXAMPLES with auto-generated stubs for any errorCode in
    x-http-error-map that has no hand-crafted entry.

    The spec is the authority on which codes exist. Hand-crafted entries are
    kept verbatim; missing codes get a minimal stub so no EBNF code is ever
    silently absent from generated docs.

    Returns a new dict structured identically to ERROR_EXAMPLES.
    """
    http_error_map = extract_http_error_map(spec)
    effective = {k: dict(v) for k, v in error_examples.items()}
    stubs_added = []

    for http_status, entry in http_error_map.items():
        covered = {
            ex_data['value'].get('errorCode')
            for ex_data in effective.get(http_status, {}).values()
        }
        for code in entry.get('errorCodes', []):
            if code not in covered:
                stub_key = code.lower().replace('_', '-')
                if http_status not in effective:
                    effective[http_status] = {}
                effective[http_status][stub_key] = {
                    'summary': code.replace('_', ' ').title(),
                    'value': {
                        'errorMessage': code.replace('_', ' ').capitalize(),
                        'errorCode': code,
                        'errorDetails': '{}'
                    }
                }
                stubs_added.append(f"  {http_status}: {code}")

    if stubs_added:
        print(f"✓ Auto-generated {len(stubs_added)} stub example(s) for errorCodes not in ERROR_EXAMPLES:")
        for s in stubs_added:
            print(s)
    else:
        print(f"✓ All EBNF errorCode values have hand-crafted examples")

    # Inject a fresh tracking ID into every example (hand-crafted and stubs)
    for http_status, examples in effective.items():
        for ex_key, ex_data in examples.items():
            val = dict(ex_data['value'])
            val['errorTrackingId'] = _generate_tracking_id()
            effective[http_status][ex_key] = {**ex_data, 'value': val}

    return effective

# Error example data lives in config/error-response-examples.yaml.
# errorCode values MUST match the EBNF data dictionary errorCode enum.
# errorType is NOT stored there — it is read from x-http-error-map in the spec
# (injected by ebnf_to_openapi_dynamic_v3.py from the EBNF @http_error_map block)
# and merged in at injection time. Edit data_dictionary/c2mapiv2-dd.ebnf to change
# the errorType assignment per status.
_EXAMPLES_CONFIG = Path(__file__).parent.parent.parent / 'config' / 'error-response-examples.yaml'
ERROR_EXAMPLES = _load_error_examples(_EXAMPLES_CONFIG)

def discover_job_response_schema_name(spec):
    """
    Discover the job response schema name dynamically from the spec.

    Finds the first /jobs/ POST endpoint with a 200 response whose
    application/json schema is a $ref, and returns the referenced schema name.
    Returns None if not found.
    """
    for path, methods in spec.get('paths', {}).items():
        if '/jobs/' not in path:
            continue
        operation = methods.get('post', {})
        if not operation:
            continue
        content = (operation.get('responses', {})
                             .get('200', {})
                             .get('content', {})
                             .get('application/json', {}))
        ref = content.get('schema', {}).get('$ref', '')
        if ref.startswith('#/components/schemas/'):
            return ref.split('/')[-1]
    return None


def add_response_examples(spec, error_examples=None):
    """Add example values to the job response schema and all job endpoints."""
    if error_examples is None:
        error_examples = ERROR_EXAMPLES

    http_error_map = extract_http_error_map(spec)
    if not http_error_map:
        print("⚠️  WARNING: x-http-error-map not found in spec info — errorType will be omitted from error examples")

    response_schema_name = discover_job_response_schema_name(spec)

    # Add examples to the job response schema
    if 'components' in spec and 'schemas' in spec['components']:
        schemas = spec['components']['schemas']

        if response_schema_name and response_schema_name in schemas:
            schemas[response_schema_name]['example'] = {
                'status': 'accepted',
                'message': 'Your request has been queued',
                'requestId': 123456
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

                                # Add example if it references the discovered response schema
                                if 'schema' in json_response and '$ref' in json_response['schema']:
                                    if response_schema_name and response_schema_name in json_response['schema']['$ref']:
                                        # Create endpoint-specific example
                                        endpoint_name = path.split('/')[-1].replace('-', '_')
                                        
                                        # Only add 'examples' (not 'example') to avoid validation issues
                                        json_response['examples'] = {
                                            'success': {
                                                'summary': 'Request accepted and queued',
                                                'value': {
                                                    'status': 'accepted',
                                                    'message': 'Your request has been queued',
                                                    'requestId': 123456
                                                }
                                            }
                                        }

                                        # Add error examples to all error responses defined in x-http-error-map
                                        error_statuses = (
                                            http_error_map.keys() if http_error_map
                                            else error_examples.keys()
                                        )
                                        for error_code in error_statuses:
                                            if error_code in operation['responses']:
                                                error_response = operation['responses'][error_code]
                                                if 'content' in error_response and 'application/json' in error_response['content']:
                                                    error_json = error_response['content']['application/json']

                                                    # Merge errorType from EBNF map into each example at injection time
                                                    if error_code in error_examples:
                                                        error_type = http_error_map.get(error_code, {}).get('errorType')
                                                        examples = {}
                                                        for ex_name, ex_data in error_examples[error_code].items():
                                                            merged_value = ex_data['value']
                                                            if error_type:
                                                                merged_value = {'errorType': error_type, **merged_value}
                                                            examples[ex_name] = {**ex_data, 'value': merged_value}
                                                        error_json['examples'] = examples

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

    # Validate errorCode values against EBNF enum; auto-generate stubs for any uncovered codes
    print("\n🔍 Validating errorCode values against EBNF data dictionary...")
    validate_error_examples(spec, ERROR_EXAMPLES)
    effective_examples = build_effective_error_examples(spec, ERROR_EXAMPLES)

    # Add examples
    spec = add_response_examples(spec, effective_examples)

    # Save the updated spec
    with open(output_file, 'w') as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, width=1000)

    print(f"✅ Added response examples to {output_file}")

if __name__ == '__main__':
    main()
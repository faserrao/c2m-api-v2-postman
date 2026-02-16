#!/usr/bin/env python3
"""
Transfer Error Examples from OpenAPI Spec to Postman Collection

This script reads error response examples from the OpenAPI specification and adds them
as response objects to a Postman collection. This enables mock servers to randomly
serve both success and error responses.

Traceability:
  EBNF Data Dictionary → OpenAPI Spec → add_response_examples.py → This Script → Collection → Mock Server

Usage:
  python3 add_error_examples_to_collection.py <openapi_spec.yaml> <collection.json> <output.json>

Example:
  python3 add_error_examples_to_collection.py \
    openapi/c2mapiv2-openapi-spec-final.yaml \
    postman/generated/c2mapiv2-test-collection-with-tests.json \
    postman/generated/c2mapiv2-test-collection-with-errors.json
"""

import sys
import json
import yaml
import uuid
from pathlib import Path


def load_openapi_spec(spec_path):
    """Load OpenAPI specification from YAML file"""
    print(f"📖 Reading OpenAPI spec: {spec_path}")
    with open(spec_path, 'r') as f:
        spec = yaml.safe_load(f)
    return spec


def load_collection(collection_path):
    """Load Postman collection from JSON file"""
    print(f"📖 Reading Postman collection: {collection_path}")
    with open(collection_path, 'r') as f:
        collection = json.load(f)
    return collection


def extract_error_examples(spec, path, method):
    """
    Extract error examples from OpenAPI spec for a specific endpoint

    Returns: dict of {status_code: {example_name: example_value}}
    """
    error_examples = {}

    # Navigate to the endpoint
    if 'paths' not in spec or path not in spec['paths']:
        return error_examples

    path_obj = spec['paths'][path]
    if method.lower() not in path_obj:
        return error_examples

    operation = path_obj[method.lower()]

    # Check responses
    if 'responses' not in operation:
        return error_examples

    # Error status codes we care about
    error_codes = ['400', '401', '403', '404', '422', '500']

    for status_code in error_codes:
        if status_code not in operation['responses']:
            continue

        response = operation['responses'][status_code]

        # Check for examples in application/json content
        if 'content' in response and 'application/json' in response['content']:
            json_content = response['content']['application/json']

            if 'examples' in json_content:
                error_examples[status_code] = json_content['examples']

    return error_examples


def create_postman_response(status_code, example_name, example_value, request_copy, response_description):
    """
    Create a Postman response object from an OpenAPI example

    Args:
        status_code: HTTP status code (e.g., "400")
        example_name: Name of the example (e.g., "example1")
        example_value: The example data (dict with 'summary' and 'value')
        request_copy: Copy of the original request for this response
        response_description: Description from OpenAPI spec

    Returns: Postman response object (dict)
    """
    # Extract example data
    summary = example_value.get('summary', f'{status_code} Error')
    body = example_value.get('value', {})

    # Create response object
    response = {
        "id": str(uuid.uuid4()),
        "name": summary,  # Use summary as the response name
        "originalRequest": request_copy,
        "status": response_description,  # e.g., "Bad Request"
        "code": int(status_code),
        "_postman_previewlanguage": "json",
        "header": [
            {
                "key": "Content-Type",
                "value": "application/json"
            }
        ],
        "cookie": [],
        "body": json.dumps(body, indent=2)
    }

    return response


def get_status_description(status_code):
    """Get human-readable status description"""
    descriptions = {
        '400': 'Bad Request',
        '401': 'Unauthorized',
        '403': 'Forbidden',
        '404': 'Not Found',
        '422': 'Unprocessable Entity',
        '500': 'Internal Server Error'
    }
    return descriptions.get(status_code, f'Error {status_code}')


def find_matching_items(collection, path, method='POST'):
    """
    Find all items in collection that match the given path and method

    Returns: list of (item, path_to_item) tuples
    """
    matches = []

    def search_items(items, current_path=[]):
        for idx, item in enumerate(items):
            item_path = current_path + [idx]

            # Check if this is a request item
            if 'request' in item:
                request = item['request']

                # Get the URL path
                url_path = None
                if isinstance(request.get('url'), dict):
                    url_obj = request['url']
                    if 'path' in url_obj and isinstance(url_obj['path'], list):
                        url_path = '/' + '/'.join(url_obj['path'])
                    elif 'raw' in url_obj:
                        # Extract path from raw URL
                        raw_url = url_obj['raw']
                        # Remove {{baseUrl}} and get path
                        if '{{baseUrl}}' in raw_url:
                            url_path = raw_url.split('{{baseUrl}}')[1].split('?')[0]

                # Check method
                request_method = request.get('method', 'GET').upper()

                # Match path and method
                if url_path == path and request_method == method.upper():
                    matches.append((item, item_path))

            # Recursively search sub-items (folders)
            if 'item' in item and isinstance(item['item'], list):
                search_items(item['item'], item_path + ['item'])

    if 'item' in collection and isinstance(collection['item'], list):
        search_items(collection['item'])

    return matches


def add_error_responses_to_item(item, error_examples, spec_responses):
    """
    Add error response objects to a Postman collection item

    Args:
        item: Postman collection item (dict)
        error_examples: Dict of {status_code: {example_name: example_value}}
        spec_responses: Responses section from OpenAPI spec for descriptions
    """
    if 'response' not in item:
        item['response'] = []

    # Make a copy of the request for error responses
    request_copy = item.get('request', {}).copy()

    # Add error responses
    added_count = 0
    for status_code, examples in error_examples.items():
        # Get description from spec
        description = get_status_description(status_code)
        if status_code in spec_responses:
            description = spec_responses[status_code].get('description', description)

        # Add each example as a separate response
        for example_name, example_value in examples.items():
            response_obj = create_postman_response(
                status_code,
                example_name,
                example_value,
                request_copy,
                description
            )
            item['response'].append(response_obj)
            added_count += 1

    return added_count


def process_collection(spec, collection):
    """
    Process entire collection and add error examples to all matching endpoints

    Returns: dict with statistics
    """
    stats = {
        'endpoints_processed': 0,
        'error_responses_added': 0,
        'endpoints_matched': 0
    }

    # Get all paths from OpenAPI spec
    if 'paths' not in spec:
        print("⚠️  No paths found in OpenAPI spec")
        return stats

    print(f"\n🔍 Processing {len(spec['paths'])} endpoints from OpenAPI spec...")

    for path, path_obj in spec['paths'].items():
        # Check for POST operations (most common for job submission)
        for method in ['post', 'get', 'put', 'delete', 'patch']:
            if method not in path_obj:
                continue

            operation = path_obj[method]

            # Extract error examples
            error_examples = extract_error_examples(spec, path, method.upper())

            if not error_examples:
                continue  # No error examples for this endpoint

            # Find matching items in collection
            matches = find_matching_items(collection, path, method.upper())

            if not matches:
                print(f"  ⚠️  No match found in collection for {method.upper()} {path}")
                continue

            stats['endpoints_processed'] += 1
            stats['endpoints_matched'] += len(matches)

            # Add error responses to each matching item
            for item, item_path in matches:
                spec_responses = operation.get('responses', {})
                added = add_error_responses_to_item(item, error_examples, spec_responses)
                stats['error_responses_added'] += added

                # Count error examples
                total_examples = sum(len(examples) for examples in error_examples.values())
                print(f"  ✅ {method.upper()} {path}: Added {added} error responses ({total_examples} examples)")

    return stats


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        print("\n❌ Error: Incorrect number of arguments")
        print(f"   Usage: {sys.argv[0]} <openapi_spec.yaml> <input_collection.json> <output_collection.json>")
        sys.exit(1)

    spec_path = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3]

    # Validate input files exist
    if not Path(spec_path).exists():
        print(f"❌ OpenAPI spec not found: {spec_path}")
        sys.exit(1)

    if not Path(input_path).exists():
        print(f"❌ Input collection not found: {input_path}")
        sys.exit(1)

    # Load files
    try:
        spec = load_openapi_spec(spec_path)
        collection = load_collection(input_path)
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        sys.exit(1)

    # Process collection
    print("\n🔄 Adding error examples to collection...")
    stats = process_collection(spec, collection)

    # Write output
    print(f"\n💾 Writing updated collection to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(collection, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("✅ COMPLETE - Error Examples Added to Collection")
    print("="*60)
    print(f"📊 Statistics:")
    print(f"   - Endpoints with error examples: {stats['endpoints_processed']}")
    print(f"   - Collection items matched: {stats['endpoints_matched']}")
    print(f"   - Error responses added: {stats['error_responses_added']}")
    print(f"\n📁 Output: {output_path}")
    print("="*60)

    if stats['error_responses_added'] == 0:
        print("\n⚠️  WARNING: No error responses were added!")
        print("   Check that:")
        print("   - OpenAPI spec has error examples in responses")
        print("   - Collection has matching endpoints")
        print("   - Paths in collection match paths in spec")


if __name__ == '__main__':
    main()

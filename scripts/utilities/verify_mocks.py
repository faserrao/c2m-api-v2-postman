#!/usr/bin/env python3
"""
Mock Server Verification Script
================================
Validates that Prism and Postman mock servers return correct responses
that match the OpenAPI specification schemas.

Usage:
    python verify_mocks.py [options]

Options:
    --prism-url URL         Prism mock server URL (default: http://localhost:4010)
    --postman-url URL       Postman mock server URL (from environment or arg)
    --spec PATH             OpenAPI spec file path (default: openapi/c2mapiv2-openapi-spec-final.yaml)
    --output PATH           Output JSON file path (default: stdout)
    --skip-prism            Skip Prism mock validation
    --skip-postman          Skip Postman mock validation
    --verbose               Enable verbose output

Requirements:
    pip install requests pyyaml jsonschema
"""

import argparse
import json
import sys
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    import requests
    import yaml
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Install with: pip install requests pyyaml jsonschema")
    sys.exit(1)

class MockVerifier:
    """Verifies mock server responses against OpenAPI specification."""

    def __init__(self, spec_path: str, verbose: bool = False):
        self.spec_path = spec_path
        self.verbose = verbose
        self.spec = self._load_spec()

    def _load_spec(self) -> Dict:
        """Load OpenAPI specification from YAML file."""
        try:
            with open(self.spec_path, 'r') as f:
                spec = yaml.safe_load(f)
            if self.verbose:
                print(f"✅ Loaded OpenAPI spec: {self.spec_path}")
                print(f"   Title: {spec.get('info', {}).get('title', 'Unknown')}")
                print(f"   Version: {spec.get('info', {}).get('version', 'Unknown')}")
                print(f"   Paths: {len(spec.get('paths', {}))}")
            return spec
        except Exception as e:
            print(f"❌ Failed to load OpenAPI spec: {e}")
            sys.exit(1)

    def _get_endpoints(self) -> List[Tuple[str, str]]:
        """Extract all endpoints from OpenAPI spec."""
        endpoints = []
        for path, methods in self.spec.get('paths', {}).items():
            for method in methods.keys():
                if method.upper() in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                    endpoints.append((method.upper(), path))
        return endpoints

    def _get_response_schema(self, method: str, path: str, status: str = '200') -> Optional[Dict]:
        """Get response schema for endpoint from OpenAPI spec."""
        try:
            path_item = self.spec['paths'][path]
            operation = path_item[method.lower()]
            responses = operation.get('responses', {})

            # Try exact status code, then 2xx, then default
            for status_key in [status, '2xx', 'default']:
                if status_key in responses:
                    response = responses[status_key]
                    content = response.get('content', {})

                    # Try application/json first, then any content type
                    for content_type in ['application/json', 'application/*', '*/*']:
                        if content_type in content:
                            return content[content_type].get('schema')

            return None
        except (KeyError, TypeError):
            return None

    def _send_request(self, mock_url: str, method: str, path: str) -> Dict:
        """Send request to mock server and return result."""
        url = f"{mock_url.rstrip('/')}{path}"

        try:
            # For POST/PUT/PATCH, send minimal valid body
            data = None
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer mock-test-token'  # Dummy token for mock servers
            }

            if method in ['POST', 'PUT', 'PATCH']:
                data = json.dumps({})  # Empty object as minimal body

            response = requests.request(
                method,
                url,
                data=data,
                headers=headers,
                timeout=10
            )

            # Try to parse response as JSON
            try:
                response_body = response.json()
            except:
                response_body = response.text

            return {
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'body': response_body,
                'headers': dict(response.headers)
            }
        except requests.RequestException as e:
            return {
                'status_code': None,
                'success': False,
                'error': str(e),
                'body': None,
                'headers': {}
            }

    def _validate_schema(self, response_body: any, schema: Dict) -> Tuple[bool, Optional[str]]:
        """Validate response body against JSON schema."""
        if not schema:
            return True, None

        try:
            # Handle schema references
            if '$ref' in schema:
                # Simple ref resolution (doesn't handle all cases)
                ref_path = schema['$ref'].split('/')
                resolved_schema = self.spec
                for part in ref_path:
                    if part == '#':
                        continue
                    resolved_schema = resolved_schema[part]
                schema = resolved_schema

            validate(instance=response_body, schema=schema)
            return True, None
        except ValidationError as e:
            return False, str(e.message)
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def verify_endpoint(
        self,
        mock_url: str,
        method: str,
        path: str,
        mock_name: str
    ) -> Dict:
        """Verify single endpoint on mock server."""

        if self.verbose:
            print(f"   Testing {method} {path} on {mock_name}...")

        # Send request
        result = self._send_request(mock_url, method, path)

        # Get expected schema
        schema = None
        if result['success']:
            schema = self._get_response_schema(method, path, str(result['status_code']))

        # Validate schema if response was successful
        schema_valid = True
        schema_error = None
        if result['success'] and schema and result['body']:
            schema_valid, schema_error = self._validate_schema(result['body'], schema)

        return {
            'endpoint': f"{method} {path}",
            'mock': mock_name,
            'status_code': result['status_code'],
            'success': result['success'],
            'schema_valid': schema_valid,
            'schema_error': schema_error,
            'error': result.get('error')
        }

    def verify_all_endpoints(
        self,
        prism_url: Optional[str] = None,
        postman_url: Optional[str] = None
    ) -> Dict:
        """Verify all endpoints on available mock servers."""

        endpoints = self._get_endpoints()

        print(f"\n🔬 Mock Server Verification")
        print(f"   OpenAPI Spec: {self.spec_path}")
        print(f"   Endpoints: {len(endpoints)}")

        results = {
            'spec_path': self.spec_path,
            'total_endpoints': len(endpoints),
            'mocks': {}
        }

        # Test Prism mock
        if prism_url:
            print(f"\n📊 Testing Prism Mock: {prism_url}")
            prism_results = []
            for method, path in endpoints:
                result = self.verify_endpoint(prism_url, method, path, 'prism')
                prism_results.append(result)

            passed = sum(1 for r in prism_results if r['success'] and r['schema_valid'])
            failed = len(prism_results) - passed

            results['mocks']['prism'] = {
                'url': prism_url,
                'status': 'operational' if passed > 0 else 'failed',
                'endpoints_tested': len(prism_results),
                'passed': passed,
                'failed': failed,
                'results': prism_results
            }

            print(f"   ✅ Passed: {passed}/{len(prism_results)}")
            if failed > 0:
                print(f"   ❌ Failed: {failed}/{len(prism_results)}")

        # Test Postman mock
        if postman_url:
            print(f"\n📊 Testing Postman Mock: {postman_url}")
            postman_results = []
            for method, path in endpoints:
                result = self.verify_endpoint(postman_url, method, path, 'postman')
                postman_results.append(result)

            passed = sum(1 for r in postman_results if r['success'] and r['schema_valid'])
            failed = len(postman_results) - passed

            results['mocks']['postman'] = {
                'url': postman_url,
                'status': 'operational' if passed > 0 else 'failed',
                'endpoints_tested': len(postman_results),
                'passed': passed,
                'failed': failed,
                'results': postman_results
            }

            print(f"   ✅ Passed: {passed}/{len(postman_results)}")
            if failed > 0:
                print(f"   ❌ Failed: {failed}/{len(postman_results)}")

        return results

def main():
    parser = argparse.ArgumentParser(
        description='Verify Prism and Postman mock servers against OpenAPI spec',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--prism-url',
        default='http://localhost:4010',
        help='Prism mock server URL (default: http://localhost:4010)'
    )

    parser.add_argument(
        '--postman-url',
        help='Postman mock server URL'
    )

    parser.add_argument(
        '--spec',
        default='openapi/c2mapiv2-openapi-spec-final.yaml',
        help='OpenAPI spec file path'
    )

    parser.add_argument(
        '--output',
        help='Output JSON file path (default: stdout)'
    )

    parser.add_argument(
        '--skip-prism',
        action='store_true',
        help='Skip Prism mock validation'
    )

    parser.add_argument(
        '--skip-postman',
        action='store_true',
        help='Skip Postman mock validation'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Validate that at least one mock is being tested
    if args.skip_prism and args.skip_postman:
        print("❌ Error: Cannot skip both Prism and Postman mocks")
        sys.exit(1)

    # Check if spec file exists
    if not Path(args.spec).exists():
        print(f"❌ Error: OpenAPI spec not found: {args.spec}")
        sys.exit(1)

    # Initialize verifier
    verifier = MockVerifier(args.spec, args.verbose)

    # Verify mocks
    prism_url = None if args.skip_prism else args.prism_url
    postman_url = None if args.skip_postman else args.postman_url

    results = verifier.verify_all_endpoints(prism_url, postman_url)

    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📝 Results written to: {args.output}")
    else:
        print(f"\n📄 Results (JSON):")
        print(json.dumps(results, indent=2))

    # Exit with appropriate code
    total_failed = sum(
        mock_data['failed']
        for mock_data in results['mocks'].values()
    )

    if total_failed > 0:
        print(f"\n❌ Validation failed: {total_failed} endpoint(s) failed")
        sys.exit(1)
    else:
        print(f"\n✅ Validation successful: All endpoints passed")
        sys.exit(0)

if __name__ == '__main__':
    main()

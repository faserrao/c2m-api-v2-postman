#!/usr/bin/env python3
"""
Debug Postman v10 API endpoints to understand schema handling and collection generation.
"""

import requests
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

class PostmanV10Debugger:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.postman.com"
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to Postman API and return response."""
        url = f"{self.base_url}{endpoint}"
        
        print(f"\n{'='*60}")
        print(f"{method} {url}")
        if data:
            print(f"Payload: {json.dumps(data, indent=2)}")
        
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json() if response.text else {}, indent=2)}")
        
        return {
            "status": response.status_code,
            "data": response.json() if response.text else {},
            "headers": dict(response.headers)
        }
    
    def test_api_details(self, api_id: str):
        """Get full API details."""
        print("\n\n### TESTING API DETAILS ###")
        return self.make_request("GET", f"/apis/{api_id}")
    
    def test_api_schema_endpoints(self, api_id: str):
        """Test various schema-related endpoints."""
        print("\n\n### TESTING SCHEMA ENDPOINTS ###")
        
        # Try different schema endpoints
        endpoints = [
            f"/apis/{api_id}/schemas",
            f"/apis/{api_id}/schema",
            f"/apis/{api_id}/versions",
            f"/apis/{api_id}/versions/latest",
            f"/apis/{api_id}/versions/latest/schemas",
            f"/apis/{api_id}/versions/latest/schema"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                results[endpoint] = self.make_request("GET", endpoint)
            except Exception as e:
                print(f"Error on {endpoint}: {e}")
                results[endpoint] = {"error": str(e)}
        
        return results
    
    def test_api_collection_endpoints(self, api_id: str):
        """Test collection generation endpoints."""
        print("\n\n### TESTING COLLECTION ENDPOINTS ###")
        
        endpoints = [
            f"/apis/{api_id}/collections",
            f"/apis/{api_id}/collection"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                results[endpoint] = self.make_request("GET", endpoint)
            except Exception as e:
                print(f"Error on {endpoint}: {e}")
                results[endpoint] = {"error": str(e)}
        
        return results
    
    def test_collection_from_schema(self, api_id: str):
        """Try to generate a collection from the API schema."""
        print("\n\n### TESTING COLLECTION GENERATION ###")
        
        # Method 1: POST to collections endpoint
        print("\nMethod 1: POST to /collections with API reference")
        payload1 = {
            "collection": {
                "info": {
                    "name": "Debug Collection from API",
                    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
                },
                "item": []
            },
            "apiId": api_id
        }
        result1 = self.make_request("POST", "/collections", payload1)
        
        # Method 2: Use collection generator endpoint if it exists
        print("\nMethod 2: Try collection generator endpoint")
        result2 = self.make_request("POST", f"/apis/{api_id}/generate-collection", {})
        
        # Method 3: Try to get versions and schemas
        print("\nMethod 3: Get API versions first")
        versions_result = self.make_request("GET", f"/apis/{api_id}/versions")
        
        return {
            "method1_post_collection": result1,
            "method2_generate": result2,
            "method3_versions": versions_result
        }
    
    def test_workspace_apis(self, workspace_id: str):
        """List all APIs in workspace to understand structure."""
        print("\n\n### TESTING WORKSPACE APIs ###")
        return self.make_request("GET", f"/workspaces/{workspace_id}/apis")
    
    def test_api_tasks(self, api_id: str):
        """Test API tasks endpoint which might include sync/generate."""
        print("\n\n### TESTING API TASKS ###")
        
        endpoints = [
            f"/apis/{api_id}/tasks",
            f"/apis/{api_id}/sync",
            f"/apis/{api_id}/generate"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                results[endpoint] = self.make_request("GET", endpoint)
            except Exception as e:
                print(f"Error on {endpoint}: {e}")
                results[endpoint] = {"error": str(e)}
        
        return results

def main():
    _repo_root = Path(__file__).resolve().parent.parent.parent

    # Read API key from env var or .env at repo root
    api_key = os.environ.get("POSTMAN_SERRAO_API_KEY")
    if not api_key:
        env_path = _repo_root / ".env"
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith("POSTMAN_SERRAO_API_KEY"):
                        api_key = line.split("=", 1)[1].strip()
                        break

    if not api_key:
        print("Error: POSTMAN_SERRAO_API_KEY not set in environment or .env")
        sys.exit(1)

    # Read API ID from postman/postman_api_uid.txt relative to repo root
    api_uid_path = _repo_root / "postman" / "postman_api_uid.txt"
    with open(api_uid_path, 'r') as f:
        api_id = f.read().strip()
    
    print(f"API ID: {api_id}")
    
    # Initialize debugger
    debugger = PostmanV10Debugger(api_key)
    
    # Run tests
    print("\n" + "="*80)
    print("POSTMAN V10 API DEBUGGING SESSION")
    print("="*80)
    
    # Test 1: Get API details
    api_details = debugger.test_api_details(api_id)
    
    # Test 2: Test schema endpoints
    schema_results = debugger.test_api_schema_endpoints(api_id)
    
    # Test 3: Test collection endpoints
    collection_results = debugger.test_api_collection_endpoints(api_id)
    
    # Test 4: Try to generate collection
    generation_results = debugger.test_collection_from_schema(api_id)
    
    # Test 5: List workspace APIs
    workspace_id = os.environ.get("POSTMAN_WS")
    if not workspace_id:
        env_path = _repo_root / ".env"
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith("POSTMAN_WS"):
                        workspace_id = line.split("=", 1)[1].strip()
                        break
    if not workspace_id:
        print("Error: POSTMAN_WS not set in environment or .env")
        sys.exit(1)
    workspace_apis = debugger.test_workspace_apis(workspace_id)
    
    # Test 6: Test API tasks
    task_results = debugger.test_api_tasks(api_id)
    
    # Summary
    print("\n\n" + "="*80)
    print("DEBUGGING SUMMARY")
    print("="*80)
    
    print("\n### Key Findings ###")
    
    # Check if API has versions
    if "data" in api_details and "versions" in api_details["data"]:
        print(f"- API has versions field: {api_details['data']['versions']}")
    
    # Check successful endpoints
    successful_endpoints = []
    for endpoint, result in {**schema_results, **collection_results, **task_results}.items():
        if isinstance(result, dict) and result.get("status") == 200:
            successful_endpoints.append(endpoint)
    
    if successful_endpoints:
        print(f"\n- Successful endpoints (200 OK):")
        for endpoint in successful_endpoints:
            print(f"  - {endpoint}")
    
    # Write detailed results to file next to the postman UID file
    output_path = _repo_root / "postman" / "v10_api_debug_results.json"
    
    all_results = {
        "api_id": api_id,
        "api_details": api_details,
        "schema_endpoints": schema_results,
        "collection_endpoints": collection_results,
        "generation_attempts": generation_results,
        "workspace_apis": workspace_apis,
        "task_endpoints": task_results
    }
    
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n\nDetailed results written to: {output_path}")

if __name__ == "__main__":
    main()
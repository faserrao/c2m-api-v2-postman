#!/usr/bin/env python3
"""
Extract All OneOf Examples from OpenAPI Spec into Postman Collection

This script reads an OpenAPI spec and a Postman collection, then patches
the collection to include ALL oneOf variants as named examples in the
Examples tab of each request.

Features:
- Extracts examples from oneOf schemas
- Maps use case names to variants
- Preserves existing examples
- Generates synthetic examples when needed
"""

import json
import yaml
import sys
import copy
from pathlib import Path
from typing import Dict, List, Any, Optional

# Use case mappings for better example names
USE_CASE_MAPPINGS = {
    "documentSourceIdentifier": [
        ("documentId", "Using Document ID"),
        ("externalUrl", "Using External URL"),
        ("uploadWithDocument", "Using Upload Request ID"),
        ("uploadWithZip", "Using Upload + Zip"),
        ("zipOnly", "Using Zip ID Only")
    ],
    "recipientAddressSource": [
        ("addressId", "Using Existing Address ID"),
        ("addressListId", "Using Address List"),
        ("newAddress", "Creating New Address")
    ],
    "paymentDetails": [
        ("creditCard", "Credit Card Payment"),
        ("invoice", "Invoice Payment"),
        ("ach", "ACH Payment"),
        ("userCredit", "User Credit"),
        ("applePay", "Apple Pay"),
        ("googlePay", "Google Pay")
    ]
}

def load_openapi(filepath: str) -> Dict:
    """Load OpenAPI spec from YAML or JSON file."""
    path = Path(filepath)
    if path.suffix in ['.yaml', '.yml']:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    else:
        with open(filepath, 'r') as f:
            return json.load(f)

def load_postman(filepath: str) -> Dict:
    """Load Postman collection from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_postman(collection: Dict, filepath: str):
    """Save Postman collection to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(collection, f, indent=2)

def resolve_ref(spec: Dict, ref: str) -> Optional[Dict]:
    """Resolve a $ref in the OpenAPI spec."""
    if not ref.startswith('#/'):
        return None
    
    parts = ref[2:].split('/')
    current = spec
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    
    return current

def get_oneOf_example_value(schema: Dict, variant_index: int, field_name: str) -> Any:
    """Generate example value for a specific oneOf variant."""
    # Special handling for known fields
    if field_name == "documentSourceIdentifier":
        if variant_index == 0:  # documentId
            return 1234
        elif variant_index == 1:  # externalUrl
            return "https://api.example.com/v1/documents/5678"
        elif variant_index == 2:  # uploadRequestId + documentName
            return {
                "uploadRequestId": 100,
                "documentName": "invoice_2024_01.pdf"
            }
        elif variant_index == 3:  # uploadRequestId + zipId + documentName
            return {
                "uploadRequestId": 200,
                "zipId": 10,
                "documentName": "statement_jan.pdf"
            }
        elif variant_index == 4:  # zipId + documentName
            return {
                "zipId": 20,
                "documentName": "report_q1_2024.pdf"
            }
    
    elif field_name == "recipientAddressSource":
        if variant_index == 0:  # exactlyOneNewAddress
            return {
                "firstName": "John",
                "lastName": "Smith",
                "address1": "123 Main Street",
                "address2": "Apt 4B",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA",
                "nickName": "Johnny"
            }
        elif variant_index == 1:  # exactlyOneListId
            return 100  # addressListId
        elif variant_index == 2:  # exactlyOneId
            return 5000  # addressId
    
    elif field_name == "paymentDetails":
        if variant_index == 0:  # creditCardPayment
            return {
                "creditCardDetails": {
                    "cardType": "visa",
                    "cardNumber": "4111111111111111",
                    "expirationDate": {
                        "month": 12,
                        "year": 2025
                    },
                    "cvv": 123
                }
            }
        elif variant_index == 1:  # invoicePayment
            return {
                "invoiceDetails": {
                    "invoiceNumber": "INV-2024-001",
                    "amountDue": 150.00
                }
            }
        elif variant_index == 2:  # achPayment
            return {
                "achDetails": {
                    "routingNumber": "021000021",
                    "accountNumber": "1234567890",
                    "checkDigit": 7
                }
            }
        elif variant_index == 3:  # userCreditPayment
            return {
                "creditAmount": {
                    "amount": 50.00,
                    "currency": "USD"
                }
            }
        elif variant_index == 4:  # applePayPayment
            return {
                "applePaymentDetails": {}
            }
        elif variant_index == 5:  # googlePayPayment
            return {
                "googlePaymentDetails": {}
            }
    
    # Default: generate based on schema
    return generate_example_from_schema(schema)

def generate_example_from_schema(schema: Dict) -> Any:
    """Generate a basic example from a schema definition."""
    if "example" in schema:
        return schema["example"]
    
    if "type" not in schema:
        return "example"
    
    schema_type = schema["type"]
    
    if schema_type == "string":
        if "enum" in schema:
            return schema["enum"][0]
        return "string-example"
    elif schema_type == "integer":
        return 123
    elif schema_type == "number":
        return 123.45
    elif schema_type == "boolean":
        return True
    elif schema_type == "array":
        if "items" in schema:
            return [generate_example_from_schema(schema["items"])]
        return []
    elif schema_type == "object":
        if "properties" in schema:
            result = {}
            for prop, prop_schema in schema["properties"].items():
                result[prop] = generate_example_from_schema(prop_schema)
            return result
        return {}
    
    return f"{schema_type}-example"

def extract_examples_from_request_body(spec: Dict, request_body: Dict) -> List[Dict]:
    """Extract all examples from a request body, including oneOf variants."""
    examples = []
    
    if "content" not in request_body:
        return examples
    
    for content_type, content in request_body["content"].items():
        # First, check for explicit examples
        if "examples" in content:
            for example_name, example_obj in content["examples"].items():
                if "value" in example_obj:
                    examples.append({
                        "name": f"Example – {example_name}",
                        "value": example_obj["value"],
                        "content_type": content_type
                    })
        
        # Then, check for oneOf in schema
        if "schema" in content:
            schema = content["schema"]
            
            # Resolve $ref if needed
            if "$ref" in schema:
                resolved = resolve_ref(spec, schema["$ref"])
                if resolved:
                    schema = resolved
            
            # Extract oneOf examples from schema properties
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    # Resolve property $ref if needed
                    if "$ref" in prop_schema:
                        resolved = resolve_ref(spec, prop_schema["$ref"])
                        if resolved:
                            prop_schema = resolved
                    
                    # Check if this property has oneOf
                    if "oneOf" in prop_schema:
                        # Generate examples for each oneOf variant
                        mappings = USE_CASE_MAPPINGS.get(prop_name, [])
                        
                        for idx, variant in enumerate(prop_schema["oneOf"]):
                            # Get mapping or create default name
                            if idx < len(mappings):
                                variant_key, variant_name = mappings[idx]
                            else:
                                variant_name = f"{prop_name} – Option {idx + 1}"
                            
                            # Generate full request body with this variant
                            example_body = {}
                            for p, ps in schema.get("properties", {}).items():
                                if p == prop_name:
                                    example_body[p] = get_oneOf_example_value(prop_schema, idx, prop_name)
                                else:
                                    # Generate default value for other properties
                                    example_body[p] = generate_example_from_schema(ps)
                            
                            examples.append({
                                "name": f"{variant_name}",
                                "value": example_body,
                                "content_type": content_type
                            })
    
    return examples

def patch_collection_with_examples(openapi: Dict, collection: Dict) -> Dict:
    """Patch Postman collection with all oneOf examples."""
    patched = copy.deepcopy(collection)
    
    # Process each item in the collection
    def process_item(item: Dict):
        if "request" not in item:
            return
        
        request = item["request"]
        method = request.get("method", "").upper()
        
        # Extract path from URL
        if "url" in request and isinstance(request["url"], dict) and "path" in request["url"]:
            path_parts = request["url"]["path"]
            path = "/" + "/".join(path_parts)
        else:
            return
        
        # Find matching path in OpenAPI spec
        for openapi_path, path_obj in openapi.get("paths", {}).items():
            # Simple path matching (could be improved for path parameters)
            if openapi_path == path or path.endswith(openapi_path.split('/')[-1]):
                method_lower = method.lower()
                if method_lower in path_obj:
                    operation = path_obj[method_lower]
                    
                    # Extract examples from request body
                    if "requestBody" in operation:
                        examples = extract_examples_from_request_body(openapi, operation["requestBody"])
                        
                        if examples:
                            # Initialize response array if not exists
                            if "response" not in item:
                                item["response"] = []
                            
                            # Add each example as a response
                            for example in examples:
                                # Create response object for Postman
                                response_obj = {
                                    "name": example["name"],
                                    "originalRequest": copy.deepcopy(request),
                                    "status": "OK",
                                    "code": 200,
                                    "_postman_previewlanguage": "json",
                                    "header": [
                                        {
                                            "key": "Content-Type",
                                            "value": example["content_type"]
                                        }
                                    ],
                                    "cookie": [],
                                    "body": json.dumps(example["value"], indent=2)
                                }
                                
                                # Update the originalRequest with the example body
                                if "body" not in response_obj["originalRequest"]:
                                    response_obj["originalRequest"]["body"] = {
                                        "mode": "raw",
                                        "raw": ""
                                    }
                                
                                response_obj["originalRequest"]["body"]["raw"] = json.dumps(example["value"], indent=2)
                                
                                item["response"].append(response_obj)
    
    # Process all items recursively
    def process_items(items: List[Dict]):
        for item in items:
            if "item" in item:
                # This is a folder
                process_items(item["item"])
            else:
                # This is a request
                process_item(item)
    
    if "item" in patched:
        process_items(patched["item"])
    
    return patched

def main():
    if len(sys.argv) != 4:
        print("Usage: extract_all_oneof_examples.py <openapi.yaml> <collection.json> <output.json>")
        sys.exit(1)
    
    openapi_file = sys.argv[1]
    collection_file = sys.argv[2]
    output_file = sys.argv[3]
    
    print(f"📚 Loading OpenAPI spec from {openapi_file}...")
    openapi = load_openapi(openapi_file)
    
    print(f"📦 Loading Postman collection from {collection_file}...")
    collection = load_postman(collection_file)
    
    print("🔧 Extracting oneOf examples and patching collection...")
    patched = patch_collection_with_examples(openapi, collection)
    
    # Count how many examples were added
    original_responses = sum(len(item.get("response", [])) for item in collection.get("item", []))
    patched_responses = sum(len(item.get("response", [])) for item in patched.get("item", []))
    added = patched_responses - original_responses
    
    print(f"📊 Added {added} new examples to the collection")
    
    print(f"💾 Saving enhanced collection to {output_file}...")
    save_postman(patched, output_file)
    
    print("✅ Successfully extracted all oneOf examples!")

if __name__ == "__main__":
    main()
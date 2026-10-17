#!/usr/bin/env python3
"""
Fix documentSourceIdentifier in Postman collections to use complex object examples
instead of simple strings for oneOf schemas.
"""

import json
import sys
import random

def generate_document_source_identifier():
    """Generate a complex object example for documentSourceIdentifier."""
    # Choose one of the 5 possible structures randomly
    choice = random.randint(1, 5)
    
    if choice == 1:
        # Just documentId
        return random.randint(1000, 9999)
    elif choice == 2:
        # Just externalUrl
        return f"https://api.example.com/v1/documents/{random.randint(1000, 9999)}"
    elif choice == 3:
        # uploadRequestId + documentName
        return {
            "uploadRequestId": random.randint(100, 999),
            "documentName": f"document_{random.randint(1000, 9999)}.pdf"
        }
    elif choice == 4:
        # uploadRequestId + zipId + documentName
        return {
            "uploadRequestId": random.randint(100, 999),
            "zipId": random.randint(10, 99),
            "documentName": f"document_{random.randint(1000, 9999)}.pdf"
        }
    else:
        # zipId + documentName
        return {
            "zipId": random.randint(10, 99),
            "documentName": f"document_{random.randint(1000, 9999)}.pdf"
        }

def fix_request_body(body_str):
    """Fix documentSourceIdentifier in a request body string."""
    try:
        body = json.loads(body_str)
        
        # Check if documentSourceIdentifier exists and is a simple string
        if 'documentSourceIdentifier' in body and isinstance(body['documentSourceIdentifier'], str):
            # Replace with a complex object
            body['documentSourceIdentifier'] = generate_document_source_identifier()
        
        # Also check in items array for multi-doc endpoints
        if 'items' in body and isinstance(body['items'], list):
            for item in body['items']:
                if isinstance(item, dict) and 'documentSourceIdentifier' in item:
                    if isinstance(item['documentSourceIdentifier'], str):
                        item['documentSourceIdentifier'] = generate_document_source_identifier()
        
        # Also check in documentsToMerge array
        if 'documentsToMerge' in body and isinstance(body['documentsToMerge'], list):
            new_merge_docs = []
            for doc in body['documentsToMerge']:
                if isinstance(doc, str):
                    new_merge_docs.append(generate_document_source_identifier())
                else:
                    new_merge_docs.append(doc)
            body['documentsToMerge'] = new_merge_docs
        
        return json.dumps(body, indent=2)
    except (json.JSONDecodeError, KeyError):
        # If parsing fails, return original
        return body_str

def process_item(item):
    """Recursively process a Postman collection item."""
    if isinstance(item, dict):
        # Process request body if present
        if 'request' in item and isinstance(item['request'], dict):
            if 'body' in item['request'] and isinstance(item['request']['body'], dict):
                if 'raw' in item['request']['body']:
                    item['request']['body']['raw'] = fix_request_body(item['request']['body']['raw'])
        
        # Process example requests in responses
        if 'response' in item and isinstance(item['response'], list):
            for response in item['response']:
                if 'originalRequest' in response and isinstance(response['originalRequest'], dict):
                    if 'body' in response['originalRequest'] and isinstance(response['originalRequest']['body'], dict):
                        if 'raw' in response['originalRequest']['body']:
                            response['originalRequest']['body']['raw'] = fix_request_body(response['originalRequest']['body']['raw'])
        
        # Recursively process sub-items
        if 'item' in item and isinstance(item['item'], list):
            for sub_item in item['item']:
                process_item(sub_item)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_collection.json> <output_collection.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Load the collection
    with open(input_file, 'r') as f:
        collection = json.load(f)
    
    # Process all items in the collection
    if 'item' in collection:
        for item in collection['item']:
            process_item(item)
    
    # Save the modified collection
    with open(output_file, 'w') as f:
        json.dump(collection, f, indent=2)
    
    print(f"✅ Fixed documentSourceIdentifier examples in {output_file}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Generate a report of all Real World Use Cases and their request bodies"""

import json
import sys
from datetime import datetime

def generate_report():
    # Load the use case collection
    with open('postman/generated/c2mapiv2-use-case-collection.json', 'r') as f:
        collection = json.load(f)

    print('# C2M API V2 - Real World Use Cases Report')
    print(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 80)
    print()

    # Process each use case folder
    for folder in collection['item']:
        print(f'## {folder["name"]}')
        print(f'**Description:** {folder.get("description", "No description")}')
        print()
        
        # Process each request in the folder
        for request in folder['item']:
            print(f'### Request: {request["name"]}')
            
            # Get request details
            req = request['request']
            print(f'- **Method:** {req["method"]}')
            print(f'- **Endpoint:** `{req["url"]["raw"]}`')
            
            # Check if there are examples (response array contains saved examples)
            if 'response' in request and len(request['response']) > 0:
                print(f'- **Number of examples:** {len(request["response"])}')
                print()
                
                # Print each example
                for idx, example in enumerate(request['response'], 1):
                    print(f'#### Example {idx}: {example["name"]}')
                    
                    # Get the request body from the example
                    if 'originalRequest' in example and 'body' in example['originalRequest']:
                        body_raw = example['originalRequest']['body'].get('raw', '{}')
                        try:
                            body_json = json.loads(body_raw)
                            print('```json')
                            print(json.dumps(body_json, indent=2))
                            print('```')
                        except:
                            print('```')
                            print(body_raw)
                            print('```')
                    else:
                        print('*No request body found*')
                    print()
            else:
                # No examples, get the main request body
                print()
                print('#### Request Body:')
                if 'body' in req and 'raw' in req['body']:
                    body_raw = req['body']['raw']
                    try:
                        body_json = json.loads(body_raw)
                        print('```json')
                        print(json.dumps(body_json, indent=2))
                        print('```')
                    except:
                        print('```')
                        print(body_raw)
                        print('```')
                else:
                    print('*No request body*')
                print()
        
        print('-' * 80)
        print()

if __name__ == '__main__':
    generate_report()
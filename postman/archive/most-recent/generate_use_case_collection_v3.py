#!/usr/bin/env python3
"""
Generate Curated Use Case Collection for C2M API (v3 - Dynamic from Linked Collection)

This version reads request body structure from the linked collection, ensuring
automatic synchronization with EBNF changes. Only scenario-specific values are hardcoded.

Usage: generate_use_case_collection_v3.py <output.json>
"""

import json
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Any

# Path to linked collection (source of truth for request structure)
LINKED_COLLECTION_PATH = "postman/generated/c2mapiv2-linked-collection-flat.json"

# Default base URL placeholder
BASE_URL = "{{baseUrl}}"

# Use case scenario definitions - now storing only VALUES to fill in, not structure
USE_CASE_SCENARIOS = {
    "legal_firm": {
        "name": "Legal Firm",
        "description": "We have letters that we need to send all day. Each letter is sent to a specific recipient via Certified Mail. A copy is sent to their legal representative via First Class mail. Our system generates the PDF of the letter.",
        "endpoint": "/jobs/submit/single/doc",
        "values": {
            "docSourceAll": {"documentId": 1234},
            "recipientAddressSource": {
                "firstName": "John",
                "lastName": "Doe",
                "address1": "123 Main Street",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "jobTemplate": "legal_certified_mail",
            "paymentDetails": {
                "creditCardDetails": {
                    "cardType": "visa",
                    "cardNumber": "4111111111111111",
                    "expirationDate": {"month": 12, "year": 2025},
                    "cvv": 123
                }
            },
            "tags": ["legal", "certified", "client-correspondence"]
        }
    },

    "company_invoice_batch": {
        "name": "Company #1",
        "description": "We send invoices at the end of the month. Each invoice is in its own PDF. The address of the recipient is in the invoice.",
        "endpoint": "/jobs/submit/single/pdf/addressCapture",
        "values": {
            "addressCapturePdfs": [
                {
                    "docSourceAll": {
                        "uploadRequestId": 100,
                        "documentName": "invoice_001.pdf"
                    },
                    "addressRegion": {
                        "x": 300,
                        "y": 100,
                        "width": 200,
                        "height": 100,
                        "pageOffset": 0
                    }
                }
            ],
            "jobTemplate": "invoice_template",
            "tags": ["invoices", "end-of-month"]
        }
    },

    "company_pdf_split": {
        "name": "Company #2",
        "description": "At the end of the month we have one big PDF file with all the invoices. We need to split the invoices and grab the addresses from each invoice.",
        "endpoint": "/jobs/submit/single/pdf/split/addressCapture",
        "values": {
            "docSourceAll": {"uploadRequestId": 200},
            "splitRules": {
                "splitBy": "pageRange",
                "pageRanges": [
                    {"start": 1, "end": 5},
                    {"start": 6, "end": 10}
                ]
            },
            "addressRegion": {
                "x": 300,
                "y": 100,
                "width": 200,
                "height": 100,
                "pageOffset": 0
            },
            "jobTemplate": "monthly_statements",
            "tags": ["invoices", "split", "batch"]
        }
    },

    "real_estate_agent": {
        "name": "Real Estate Agent",
        "description": "We send out statements every month to our clients.",
        "endpoint": "/jobs/submit/single/doc",
        "values": {
            "docSourceAll": {"documentId": 5678},
            "recipientAddressSource": {"addressListId": "monthly_clients"},
            "jobTemplate": "monthly_statement",
            "tags": ["real-estate", "monthly", "statements"]
        }
    },

    "medical_agency": {
        "name": "Medical Agency",
        "description": "We have patient statements that need to be mailed. Each statement consists of multiple documents that need to be merged.",
        "endpoint": "/jobs/submit/multi/doc/merge",
        "values": {
            "documentsToMerge": [
                {"documentId": 101},
                {"documentId": 102},
                {"documentId": 103}
            ],
            "recipientAddressSource": {
                "firstName": "Jane",
                "lastName": "Smith",
                "address1": "456 Oak Avenue",
                "city": "Chicago",
                "state": "IL",
                "zip": "60601",
                "country": "USA"
            },
            "jobTemplate": "patient_statement",
            "tags": ["medical", "patient-statements", "merge"]
        }
    },

    "monthly_newsletters": {
        "name": "Monthly Newsletters",
        "description": "We send newsletters to our mailing list every month.",
        "endpoint": "/jobs/submit/single/doc",
        "values": {
            "docSourceAll": {"documentId": 9012},
            "recipientAddressSource": {"addressListId": "newsletter_subscribers"},
            "jobTemplate": "newsletter_template",
            "tags": ["newsletter", "monthly", "marketing"]
        }
    },

    "reseller_pdf_split": {
        "name": "Reseller #1",
        "description": "We receive a single PDF from our customers with multiple documents. We need to split the PDF and mail each document separately.",
        "endpoint": "/jobs/submit/single/pdf/split",
        "values": {
            "docSourceAll": {"uploadRequestId": 300},
            "splitRules": {
                "splitBy": "pageRange",
                "pageRanges": [
                    {"start": 1, "end": 2},
                    {"start": 3, "end": 4}
                ]
            },
            "recipientAddressSource": {"addressListId": "customer_list"},
            "tags": ["reseller", "split", "batch"]
        }
    },

    "reseller_zip_pdfs": {
        "name": "Reseller #2",
        "description": "We receive PDFs from our customers. Each PDF is unique. We want to zip the PDFs and send them in one go.",
        "endpoint": "/jobs/submit/multi/doc",
        "values": {
            "jobs": [
                {
                    "docSourceAll": {"uploadRequestId": 400, "documentName": "doc1.pdf"},
                    "recipientAddressSource": {
                        "firstName": "Customer",
                        "lastName": "One",
                        "address1": "123 Business St",
                        "city": "Austin",
                        "state": "TX",
                        "zip": "78701",
                        "country": "USA"
                    }
                },
                {
                    "docSourceAll": {"uploadRequestId": 400, "documentName": "doc2.pdf"},
                    "recipientAddressSource": {
                        "firstName": "Customer",
                        "lastName": "Two",
                        "address1": "456 Commerce Rd",
                        "city": "Austin",
                        "state": "TX",
                        "zip": "78702",
                        "country": "USA"
                    }
                }
            ],
            "tags": ["reseller", "multi-doc", "batch"]
        }
    }
}


def load_linked_collection():
    """Load the linked collection to extract request body templates"""
    try:
        with open(LINKED_COLLECTION_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Linked collection not found at {LINKED_COLLECTION_PATH}")
        print("   Run 'make postman-create-linked-collection' first")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in linked collection: {e}")
        sys.exit(1)


def find_endpoint_template(linked_collection, endpoint_path):
    """
    Find the request template for a specific endpoint in the linked collection

    Args:
        linked_collection: The linked collection JSON
        endpoint_path: Path like "/jobs/submit/single/doc"

    Returns:
        The request item from the linked collection
    """
    # Convert path to format used in collection names
    endpoint_name = f"POST {endpoint_path}"

    for item in linked_collection['item']:
        if item['name'] == endpoint_name:
            return item

    print(f"❌ Error: Endpoint '{endpoint_name}' not found in linked collection")
    print(f"   Available endpoints:")
    for item in linked_collection['item']:
        print(f"     - {item['name']}")
    sys.exit(1)


def merge_values_into_template(template_body, scenario_values):
    """
    Merge scenario-specific values into the template body structure

    This creates a new body using ONLY the fields specified in scenario_values,
    removing all placeholder fields that aren't needed for this use case.

    Args:
        template_body: Parsed JSON from linked collection (with <oneOf>, <string>, etc.)
        scenario_values: Dict of values to fill in

    Returns:
        Merged body with ONLY scenario values (no unused placeholders)
    """
    # Use case collections should only show the fields actually used in the scenario
    # Don't include optional fields with placeholder values - that's confusing
    return scenario_values


def create_use_case_request(scenario_key, scenario, linked_collection):
    """
    Create a Postman request for a use case by merging template + scenario values

    Args:
        scenario_key: Unique key for this scenario
        scenario: Scenario definition with endpoint and values
        linked_collection: The linked collection with templates

    Returns:
        Postman request object
    """
    # Find the template for this endpoint
    template = find_endpoint_template(linked_collection, scenario['endpoint'])

    # Parse the template body
    template_body = json.loads(template['request']['body']['raw'])

    # Merge scenario values into template
    merged_body = merge_values_into_template(template_body, scenario['values'])

    # Create request based on template but with merged body
    request = {
        "name": f"POST {scenario['endpoint']}",
        "description": {
            "content": scenario['description'],
            "type": "text/plain"
        },
        "url": {
            "path": scenario['endpoint'].split('/')[1:],  # Remove leading slash
            "host": ["{{baseUrl}}"],
            "query": [],
            "variable": []
        },
        "header": [
            {"key": "Content-Type", "value": "application/json"},
            {"key": "Accept", "value": "application/json"}
        ],
        "method": "POST",
        "body": {
            "mode": "raw",
            "raw": json.dumps(merged_body, indent=2),
            "options": {
                "raw": {
                    "headerFamily": "json",
                    "language": "json"
                }
            }
        },
        "auth": None
    }

    return request


def generate_collection():
    """Generate the complete use case collection"""

    # Load linked collection
    print("📚 Loading linked collection...")
    linked_collection = load_linked_collection()

    # Create collection structure
    collection = {
        "info": {
            "name": "C2M API v2 – Real World Use Cases",
            "description": {
                "content": """This collection contains pre-populated real-world use cases to help you understand how different types of customers use the Click2Mail API.

Each folder represents a different business scenario with realistic request examples.

**How to Use This Collection:**
1. Select a use case that matches your scenario
2. Expand the folder to see the pre-configured request
3. Click the request name to open it
4. Review the request body to see how the API call is structured
5. Click Send to test the API (requires authentication)

**Use Case Categories:**
- Legal Firm: Certified mail with attorney copies
- Company #1: Monthly invoice batch with address capture
- Company #2: Split PDF invoices with address capture
- Real Estate Agent: Monthly client statements
- Medical Agency: Merged patient statement documents
- Monthly Newsletters: Mass mailing to subscriber list
- Reseller #1: Split PDF for batch mailing
- Reseller #2: Multi-document batch submission

**Important:** These examples use the production API structure. Request bodies are automatically synchronized with the current API specification.""",
                "type": "text/plain"
            },
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [],
        "variable": [
            {
                "key": "baseUrl",
                "value": "https://api.click2mail.com/v2",
                "type": "string"
            }
        ]
    }

    # Generate each use case
    print("📊 Creating use cases...")
    total_requests = 0

    for scenario_key, scenario in USE_CASE_SCENARIOS.items():
        # Create the request
        request = create_use_case_request(scenario_key, scenario, linked_collection)

        # Wrap in folder
        folder = {
            "name": scenario['name'],
            "description": {
                "content": scenario['description'],
                "type": "text/plain"
            },
            "item": [
                {
                    "id": str(uuid.uuid4()),
                    "name": request['name'],
                    "request": request,
                    "response": []
                }
            ]
        }

        collection['item'].append(folder)
        total_requests += 1

    print(f"📊 Created {len(USE_CASE_SCENARIOS)} use cases with {total_requests} total requests")

    return collection


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: generate_use_case_collection_v3.py <output.json>")
        print("\nThis script generates a curated use case collection by reading")
        print("request body structure from the linked collection and merging")
        print("scenario-specific values.")
        sys.exit(1)

    output_file = sys.argv[1]

    print("📚 Generating curated use case collection (v3 - dynamic)...")
    collection = generate_collection()

    # Save collection
    print(f"💾 Saving collection to {output_file}...")
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(collection, f, indent=2)

    print("✅ Successfully generated use case collection!")
    print("\nNext steps:")
    print("1. Import this collection into Postman")
    print("2. Set the 'authToken' variable with your JWT")
    print("3. Run any use case folder to test the API")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Permutation Generator for C2M API V2 Jobs Submit Endpoints

Generates all possible request body permutations for testing based on the EBNF data dictionary.
This version is updated for the new /jobs/submit/... endpoint structure.

Usage:
    python3 generate_endpoint_permutations.py

The script will prompt you to choose an endpoint, then generate a JSON file with all permutations
in the permutations/ directory.
"""

import itertools
import json
import os
import re
from typing import Dict, List, Any

# Path to the EBNF data dictionary (relative to script location)
EBNF_FILE = os.path.join(os.path.dirname(__file__), "c2mapiv2-dd.ebnf")
EBNF_FILE = os.path.abspath(EBNF_FILE)

OUTPUT_DIR = "permutations"


def parse_use_cases(ebnf_file: str) -> Dict[str, List[str]]:
    """
    Parse top-level endpoint parameter definitions from the EBNF file.

    Returns a dictionary mapping endpoint names (e.g., submitSingleDocParams)
    to their EBNF definition lines.
    """
    endpoints = {}
    with open(ebnf_file, "r") as f:
        lines = f.readlines()

    current_name = None
    current_def = []

    for line in lines:
        # Match endpoint parameter definitions (e.g., submitSingleDocParams =)
        match = re.match(r"^(\w+Params)\s*=", line.strip())
        if match:
            # Save previous endpoint if exists
            if current_name and current_def:
                endpoints[current_name] = current_def
            # Start new endpoint block
            current_name = match.group(1)
            current_def = [line.rstrip("\n")]
        elif current_name:
            if line.strip() == "":
                continue
            current_def.append(line.rstrip("\n"))
            if line.strip().endswith(";"):
                endpoints[current_name] = current_def
                current_name = None
                current_def = []

    return endpoints


def parse_component_options(component: str) -> List[Any]:
    """
    Return possible test data choices for each component.

    These are realistic test values that cover different variants of each component.
    Updated for new EBNF structure with docSourceAll, recipientAddressSource, etc.
    """
    mapping = {
        # Document sources (docSourceAll can be any of these)
        "docSourceAll": [
            # documentIdSource
            {"documentId": 1234},
            # urlSource
            {"url": "https://example.com/invoice.pdf"},
            # requestIdSource (single file)
            {"requestId": 5678},
            # requestIdSource (multi-file with filename)
            {"requestId": 9012, "filename": "statement.pdf"},
            # zipDocumentIdSource
            {"zipDocumentId": 3456, "filename": "contract.pdf"},
            # zipRequestIdSource
            {"requestId": 7890, "zipFilename": "archive.zip", "filename": "notice.pdf"}
        ],

        # Document sources (standard - no zip)
        "docSourceStandard": [
            {"documentId": 1234},
            {"url": "https://example.com/invoice.pdf"},
            {"requestId": 5678},
            {"requestId": 9012, "filename": "statement.pdf"}
        ],

        # Document sources (zip only)
        "docSourceZipFile": [
            {"zipDocumentId": 3456, "filename": "contract.pdf"},
            {"requestId": 7890, "zipFilename": "archive.zip", "filename": "notice.pdf"}
        ],

        # Zip document source (for addressCapture endpoints)
        "zipDocumentSource": [
            {"zipDocumentId": 3456, "filename": "batch001.pdf"},
            {"requestId": 7890, "zipFilename": "mailings.zip", "filename": "promo.pdf"}
        ],

        # Merge document source (documentsToMerge array)
        "mergeDocumentSource": [
            {
                "documentsToMerge": [
                    {"documentId": 100},
                    {"documentId": 200}
                ]
            },
            {
                "documentsToMerge": [
                    {"requestId": 300},
                    {"requestId": 400, "filename": "page2.pdf"},
                    {"documentId": 500}
                ]
            }
        ],

        # Recipient address sources (3 variants)
        "recipientAddressSource": [
            # Single address with optional mappingId
            {
                "singleAddress": {
                    "firstName": "John",
                    "lastName": "Doe",
                    "address1": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001",
                    "country": "USA"
                }
            },
            # Address list with mappingId
            {
                "mappingId": 10,
                "addressList": [
                    {
                        "firstName": "Jane",
                        "lastName": "Smith",
                        "address1": "456 Oak Ave",
                        "city": "Boston",
                        "state": "MA",
                        "zip": "02101",
                        "country": "USA"
                    }
                ],
                "addressListName": "January_Customers"
            },
            # Stored address list reference
            {"addressListId": 42}
        ],

        # Job template (string identifier)
        "jobTemplate": [
            "legal_certified_mail",
            "invoice_batch",
            "newsletter_monthly"
        ],

        # Payment details (5 variants - Apple/Google Pay excluded per EBNF)
        "paymentDetails": [
            {
                "creditCard": {
                    "cardType": "visa",
                    "cardNumber": "4111111111111111",
                    "expirationDate": {"month": 12, "year": 2025},
                    "cvv": 123
                }
            },
            {
                "invoice": {
                    "invoiceNumber": "INV-1001",
                    "amountDue": 200.50
                }
            },
            {
                "ach": {
                    "routingNumber": "111000025",
                    "accountNumber": "123456789",
                    "checkDigit": 7
                }
            },
            {
                "userCredit": {
                    "amount": 50.00,
                    "currency": "USD"
                }
            }
        ],

        # Return address (optional)
        "returnAddress": [
            {
                "firstName": "Acme",
                "lastName": "Corp",
                "address1": "100 Business Blvd",
                "city": "Chicago",
                "state": "IL",
                "zip": "60601",
                "country": "USA"
            }
        ],

        # Job options (alternative to jobTemplate)
        "jobOptions": [
            {
                "documentClass": "Letter",
                "layout": "AddressSide",
                "productionTime": "NextDay",
                "envelope": "#10",
                "color": "BW",
                "paperType": "White24",
                "printOption": "Printing_One_Side",
                "mailClass": "First"
            },
            {
                "documentClass": "Postcard",
                "layout": "6x9",
                "productionTime": "SameDay",
                "envelope": "None",
                "color": "Color",
                "paperType": "Glossy",
                "printOption": "Printing_Two_Sides",
                "mailClass": "Standard"
            }
        ],

        # Tags (array of strings)
        "tags": [
            ["legal", "certified"],
            ["batch", "invoice"],
            ["campaign", "newsletter"]
        ],

        # PDF split jobs with addresses
        "pdfSplitJobsWithAddress": [
            [
                {
                    "startPage": 1,
                    "endPage": 3,
                    "recipientAddressSource": {
                        "singleAddress": {
                            "firstName": "Recipient1",
                            "lastName": "Test",
                            "address1": "111 First St",
                            "city": "Austin",
                            "state": "TX",
                            "zip": "78701",
                            "country": "USA"
                        }
                    }
                }
            ],
            [
                {
                    "startPage": 1,
                    "endPage": 2,
                    "recipientAddressSource": {"addressListId": 50}
                },
                {
                    "startPage": 3,
                    "endPage": 5,
                    "recipientAddressSource": {
                        "singleAddress": {
                            "firstName": "Recipient2",
                            "lastName": "Test",
                            "address1": "222 Second Ave",
                            "city": "Denver",
                            "state": "CO",
                            "zip": "80201",
                            "country": "USA"
                        }
                    }
                }
            ]
        ],

        # PDF split jobs without addresses (for addressCapture)
        "pdfSplitJobsNoAddress": [
            [
                {"startPage": 1, "endPage": 3}
            ],
            [
                {"startPage": 1, "endPage": 2},
                {"startPage": 3, "endPage": 5},
                {"startPage": 6, "endPage": 8}
            ]
        ],

        # Multi-doc jobs (array of job items)
        "multiDocJobs": [
            [
                {
                    "docSourceAll": {"documentId": 1001},
                    "recipientAddressSource": {
                        "singleAddress": {
                            "firstName": "Multi1",
                            "lastName": "Test",
                            "address1": "333 Third St",
                            "city": "Seattle",
                            "state": "WA",
                            "zip": "98101",
                            "country": "USA"
                        }
                    }
                }
            ],
            [
                {
                    "jobTemplate": "custom_template_1",
                    "docSourceAll": {"documentId": 2001},
                    "recipientAddressSource": {"addressListId": 100}
                },
                {
                    "docSourceAll": {"url": "https://example.com/doc2.pdf"},
                    "recipientAddressSource": {
                        "singleAddress": {
                            "firstName": "Multi2",
                            "lastName": "Test",
                            "address1": "444 Fourth Ave",
                            "city": "Portland",
                            "state": "OR",
                            "zip": "97201",
                            "country": "USA"
                        }
                    }
                }
            ]
        ],

        # Multi-zip jobs (array of zip job items)
        "multiZipJobs": [
            [
                {
                    "docSourceZipFile": {
                        "zipDocumentId": 5001,
                        "filename": "file1.pdf"
                    },
                    "recipientAddressSource": {
                        "singleAddress": {
                            "firstName": "Zip1",
                            "lastName": "Test",
                            "address1": "555 Fifth St",
                            "city": "Miami",
                            "state": "FL",
                            "zip": "33101",
                            "country": "USA"
                        }
                    }
                }
            ],
            [
                {
                    "docSourceZipFile": {
                        "requestId": 6001,
                        "zipFilename": "batch.zip",
                        "filename": "item1.pdf"
                    },
                    "recipientAddressSource": {"addressListId": 200}
                },
                {
                    "jobTemplate": "zip_template",
                    "docSourceZipFile": {
                        "zipDocumentId": 7001,
                        "filename": "item2.pdf"
                    },
                    "recipientAddressSource": {
                        "singleAddress": {
                            "firstName": "Zip2",
                            "lastName": "Test",
                            "address1": "666 Sixth Ave",
                            "city": "Atlanta",
                            "state": "GA",
                            "zip": "30301",
                            "country": "USA"
                        }
                    }
                }
            ]
        ]
    }

    return mapping.get(component, [f"<{component}>"])


def get_endpoint_components(endpoint: str) -> List[str]:
    """
    Define which components are used by each endpoint.

    Maps endpoint parameter names to their required/optional components.
    Updated for new /jobs/submit/... endpoint structure.
    """
    endpoint_components = {
        # POST /jobs/submit/single/doc
        "submitSingleDocParams": [
            "jobTemplate",      # optional
            "docSourceAll",     # required
            "recipientAddressSource",  # required
            "paymentDetails",   # optional
            "returnAddress",    # optional
            "jobOptions",       # optional
            "tags"              # optional
        ],

        # POST /jobs/submit/single/pdf/addressCapture
        "submitSinglePdfAddressCaptureParams": [
            "jobTemplate",      # optional
            "docSourceStandard",  # required (no zip)
            "paymentDetails",   # optional
            "returnAddress",    # optional
            "jobOptions",       # optional
            "tags"              # optional
        ],

        # POST /jobs/submit/single/pdf/split
        "submitSinglePdfSplitParams": [
            "jobTemplate",      # optional
            "docSourceStandard",  # required (PDF only)
            "pdfSplitJobsWithAddress",  # required (array)
            "paymentDetails",   # optional
            "returnAddress",    # optional
            "jobOptions",       # optional
            "tags"              # optional
        ],

        # POST /jobs/submit/single/pdf/split/addressCapture
        "submitSinglePdfSplitAddressCaptureParams": [
            "jobTemplate",      # optional
            "docSourceStandard",  # required (PDF only)
            "pdfSplitJobsNoAddress",  # required (array)
            "paymentDetails",   # optional
            "returnAddress",    # optional
            "jobOptions",       # optional
            "tags"              # optional
        ],

        # POST /jobs/submit/multi/doc
        "submitMultiDocParams": [
            "jobTemplate",      # optional
            "multiDocJobs",     # required (array)
            "paymentDetails",   # optional
            "tags"              # optional
        ],

        # POST /jobs/submit/multi/doc/merge
        "submitMultiDocMergeParams": [
            "jobTemplate",      # optional
            "mergeDocumentSource",  # required (documentsToMerge array)
            "recipientAddressSource",  # required
            "paymentDetails",   # optional
            "returnAddress",    # optional
            "jobOptions",       # optional
            "tags"              # optional
        ],

        # POST /jobs/submit/multi/zip
        "submitMultiZipParams": [
            "jobTemplate",      # optional
            "multiZipJobs",     # required (array)
            "paymentDetails",   # optional
            "tags"              # optional
        ],

        # POST /jobs/submit/multi/zip/addressCapture
        "submitMultiZipAddressCaptureParams": [
            "jobTemplate",      # optional
            "zipDocumentSource",  # required (zip only)
            "paymentDetails",   # optional
            "returnAddress",    # optional
            "jobOptions",       # optional
            "tags"              # optional
        ]
    }

    return endpoint_components.get(endpoint, [])


def generate_permutations(endpoint: str) -> List[Dict[str, Any]]:
    """
    Generate all permutations of request body variants for an endpoint.

    Uses itertools.product() to create cartesian product of all component options.
    For example, if you have:
      - 6 document source variants
      - 3 recipient address variants
      - 3 job template variants
      - 4 payment variants
      - 3 tag variants

    This creates 6 × 3 × 3 × 4 × 3 = 648 permutations
    """
    components = get_endpoint_components(endpoint)
    if not components:
        raise ValueError(f"Unknown endpoint: {endpoint}")

    # Get all option lists for each component
    options = [parse_component_options(c) for c in components]

    # Create cartesian product of all options
    product = list(itertools.product(*options))

    # Build result objects
    results = []
    for combo in product:
        obj = {}
        for i, component_name in enumerate(components):
            obj[component_name] = combo[i]
        results.append(obj)

    return results


def save_permutations(endpoint: str, params_def: List[str], permutations: List[Dict[str, Any]]) -> None:
    """
    Save permutations to a JSON file.

    Creates permutations/<endpoint>.json with:
      - endpoint: parameter name
      - paramsDefinition: EBNF definition lines
      - permutations: array of all request body variants
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, f"{endpoint}.json")

    output_data = {
        "endpoint": endpoint,
        "paramsDefinition": params_def,
        "permutations": permutations
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Generated {len(permutations)} permutations for {endpoint}")
    print(f"Saved to: {output_file}")


def main():
    """Main entry point - interactive prompt for endpoint selection."""
    if not os.path.exists(EBNF_FILE):
        print(f"ERROR: EBNF file not found at {EBNF_FILE}")
        return

    endpoints = parse_use_cases(EBNF_FILE)
    if not endpoints:
        print("ERROR: No endpoint definitions found in EBNF file.")
        return

    print("=" * 60)
    print("C2M API V2 Permutation Generator")
    print("=" * 60)
    print()
    print("Available Endpoints:")
    print()

    endpoint_names = sorted(endpoints.keys())
    for i, ep in enumerate(endpoint_names, 1):
        components = get_endpoint_components(ep)
        num_variants = len(components)
        print(f"{i:2d}) {ep:<45s} ({num_variants} components)")

    print()
    choice = int(input(f"Choose endpoint (1-{len(endpoint_names)}): "))

    if choice < 1 or choice > len(endpoint_names):
        print(f"ERROR: Invalid choice. Must be 1-{len(endpoint_names)}")
        return

    endpoint = endpoint_names[choice - 1]
    params_def = endpoints[endpoint]

    print()
    print(f"Generating permutations for: {endpoint}")
    print("-" * 60)

    perms = generate_permutations(endpoint)
    save_permutations(endpoint, params_def, perms)

    print()
    print("SUCCESS: Permutation file generated")
    print()


if __name__ == "__main__":
    main()

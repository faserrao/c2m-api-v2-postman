#!/usr/bin/env python3
"""
Getting Started Collection Generator
=====================================
Generates a Postman collection organized by usage patterns to onboard new API users.

This script creates an educational collection showing different ways to use the API,
organized by frequency of use and common patterns. Based on Mahesh's collection structure.

Usage:
    python3 generate_getting_started_collection.py

Output:
    postman/generated/c2mapiv2-getting-started-collection.json
"""

import json
from typing import Dict, List, Any

# =============================================================================
# API CALL CATEGORIES - Defined upfront as data structures
# =============================================================================

# Category 1: Most Frequently Used - The bread and butter calls
MOST_FREQUENT_PATTERNS = [
    {
        "name": "Single recipient - basic job submission",
        "description": "Submit a single document to one recipient using jobTemplate",
        "endpoint": "/jobs/submit/single/doc",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "requestId": "<integer>"
            },
            "recipientAddressSource": {
                "singleAddress": {
                    "firstName": "<string>",
                    "lastName": "<string>",
                    "address1": "<string>",
                    "city": "<string>",
                    "state": "<string>",
                    "zip": "<string>"
                }
            }
        }
    },
    {
        "name": "Mail merge - multiple recipients",
        "description": "Submit a single document to multiple recipients (mail merge)",
        "endpoint": "/jobs/submit/single/doc",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "requestId": "<integer>"
            },
            "recipientAddressSource": {
                "addressList": [
                    {
                        "firstName": "<string>",
                        "lastName": "<string>",
                        "address1": "<string>",
                        "city": "<string>",
                        "state": "<string>",
                        "zip": "<string>",
                        "foo1": "<string>",  # Custom merge field
                        "foo2": "<string>"   # Custom merge field
                    },
                    {
                        "firstName": "<string>",
                        "lastName": "<string>",
                        "address1": "<string>",
                        "city": "<string>",
                        "state": "<string>",
                        "zip": "<string>",
                        "foo1": "<string>",
                        "foo2": "<string>"
                    }
                ]
            }
        }
    },
    {
        "name": "Address capture - PDF with embedded addresses",
        "description": "Submit PDF where addresses are captured from the document itself",
        "endpoint": "/jobs/submit/single/pdf/addressCapture",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "requestId": "<integer>"
            }
        }
    }
]

# Category 2: Bulk Operations - High-volume processing
BULK_PATTERNS = [
    {
        "name": "Split PDF with address capture",
        "description": "Split a multi-page PDF and capture addresses from each section",
        "endpoint": "/jobs/submit/single/pdf/split/addressCapture",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "requestId": "<integer>"
            },
            "jobs": [
                {
                    "pages": {
                        "startPage": "<integer>",
                        "endPage": "<integer>"
                    }
                },
                {
                    "pages": {
                        "startPage": "<integer>",
                        "endPage": "<integer>"
                    }
                }
            ]
        }
    },
    {
        "name": "Split PDF with specified addresses",
        "description": "Split a multi-page PDF and provide recipient address for each section",
        "endpoint": "/jobs/submit/single/pdf/split",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "requestId": "<integer>"
            },
            "jobs": [
                {
                    "pages": {
                        "startPage": "<integer>",
                        "endPage": "<integer>"
                    },
                    "recipientAddressSource": {
                        "singleAddress": {
                            "firstName": "<string>",
                            "lastName": "<string>",
                            "address1": "<string>",
                            "city": "<string>",
                            "state": "<string>",
                            "zip": "<string>"
                        }
                    }
                }
            ]
        }
    },
    {
        "name": "Multiple documents from ZIP with address capture",
        "description": "Submit multiple documents from a ZIP file with embedded addresses",
        "endpoint": "/jobs/submit/multi/zip/addressCapture",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "requestId": "<integer>"
            }
        }
    }
]

# Category 3: Less Frequently Used - Advanced features and variations
ADVANCED_PATTERNS = [
    {
        "name": "Merge multiple documents",
        "description": "Combine multiple documents into one before mailing",
        "endpoint": "/jobs/submit/multi/doc/merge",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "documentsToMerge": [
                    {"requestId": "<integer>"},
                    {"documentId": "<integer>"},
                    {"documentId": "<integer>"}
                ]
            },
            "recipientAddressSource": {
                "singleAddress": {
                    "firstName": "<string>",
                    "lastName": "<string>",
                    "address1": "<string>",
                    "city": "<string>",
                    "state": "<string>",
                    "zip": "<string>"
                }
            }
        }
    },
    {
        "name": "Using jobOptions instead of template",
        "description": "Specify job options directly instead of using a template",
        "endpoint": "/jobs/submit/single/doc",
        "body_template": {
            "jobOptions": {
                "documentClass": "<string>",
                "layout": "<string>",
                "productionTime": "<string>",
                "envelope": "<string>",
                "color": "<string>",
                "paperType": "<string>",
                "printOption": "<string>",
                "mailClass": "<string>"
            },
            "documentSource": {
                "requestId": "<integer>"
            },
            "recipientAddressSource": {
                "singleAddress": {
                    "firstName": "<string>",
                    "lastName": "<string>",
                    "address1": "<string>",
                    "city": "<string>",
                    "state": "<string>",
                    "zip": "<string>"
                }
            }
        }
    },
    {
        "name": "Using document URL instead of upload",
        "description": "Reference a document by URL instead of uploading",
        "endpoint": "/jobs/submit/single/doc",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "url": "<string>"
            },
            "recipientAddressSource": {
                "singleAddress": {
                    "firstName": "<string>",
                    "lastName": "<string>",
                    "address1": "<string>",
                    "city": "<string>",
                    "state": "<string>",
                    "zip": "<string>"
                }
            }
        }
    },
    {
        "name": "Adding tags for organization",
        "description": "Add custom tags to track and organize jobs",
        "endpoint": "/jobs/submit/single/doc",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "requestId": "<integer>"
            },
            "recipientAddressSource": {
                "singleAddress": {
                    "firstName": "<string>",
                    "lastName": "<string>",
                    "address1": "<string>",
                    "city": "<string>",
                    "state": "<string>",
                    "zip": "<string>"
                }
            },
            "tags": [
                "<string>",
                "<string>",
                "<string>"
            ]
        }
    },
    {
        "name": "Naming an address list for reuse",
        "description": "Create a named address list that can be referenced in future jobs",
        "endpoint": "/jobs/submit/single/doc",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "requestId": "<integer>"
            },
            "recipientAddressSource": {
                "addressListName": "<string>",
                "mappingId": "<integer>",
                "addressList": [
                    {
                        "firstName": "<string>",
                        "lastName": "<string>",
                        "address1": "<string>",
                        "city": "<string>",
                        "state": "<string>",
                        "zip": "<string>",
                        "foo1": "<string>",
                        "foo2": "<string>"
                    }
                ]
            }
        }
    },
    {
        "name": "Specifying payment method",
        "description": "Specify how the job should be paid for",
        "endpoint": "/jobs/submit/single/doc",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "requestId": "<integer>"
            },
            "recipientAddressSource": {
                "singleAddress": {
                    "firstName": "<string>",
                    "lastName": "<string>",
                    "address1": "<string>",
                    "city": "<string>",
                    "state": "<string>",
                    "zip": "<string>"
                }
            },
            "paymentDetails": {
                "creditCard": {
                    "cardNumber": "<string>",
                    "cardType": "<string>",
                    "cvv": "<string>",
                    "expirationMonth": "<string>",
                    "expirationYear": "<string>"
                }
            }
        }
    },
    {
        "name": "Multiple documents from ZIP - specify addresses",
        "description": "Submit multiple documents from ZIP with specified addresses for each",
        "endpoint": "/jobs/submit/multi/zip",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "requestId": "<integer>"
            },
            "jobs": [
                {
                    "filename": "<string>",
                    "recipientAddressSource": {
                        "singleAddress": {
                            "firstName": "<string>",
                            "lastName": "<string>",
                            "address1": "<string>",
                            "city": "<string>",
                            "state": "<string>",
                            "zip": "<string>"
                        }
                    }
                }
            ]
        }
    },
    {
        "name": "Multiple separate documents",
        "description": "Submit multiple different documents with different recipients",
        "endpoint": "/jobs/submit/multi/doc",
        "body_template": {
            "jobTemplate": "<string>",
            "jobs": [
                {
                    "documentSource": {
                        "documentId": "<integer>"
                    },
                    "recipientAddressSource": {
                        "singleAddress": {
                            "firstName": "<string>",
                            "lastName": "<string>",
                            "address1": "<string>",
                            "city": "<string>",
                            "state": "<string>",
                            "zip": "<string>"
                        }
                    }
                }
            ]
        }
    },
    {
        "name": "Using stored documentId",
        "description": "Reference a previously uploaded document by its ID",
        "endpoint": "/jobs/submit/single/doc",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "documentId": "<integer>"
            },
            "recipientAddressSource": {
                "singleAddress": {
                    "firstName": "<string>",
                    "lastName": "<string>",
                    "address1": "<string>",
                    "city": "<string>",
                    "state": "<string>",
                    "zip": "<string>"
                }
            }
        }
    },
    {
        "name": "Using saved addressListId",
        "description": "Reference a previously saved address list by its ID",
        "endpoint": "/jobs/submit/single/doc",
        "body_template": {
            "jobTemplate": "<string>",
            "documentSource": {
                "requestId": "<integer>"
            },
            "recipientAddressSource": {
                "addressListId": "<integer>"
            }
        }
    }
]

# =============================================================================
# COLLECTION GENERATION
# =============================================================================

def create_request_item(pattern: Dict[str, Any], base_url: str = "{{baseUrl}}") -> Dict[str, Any]:
    """
    Create a Postman request item from a pattern definition.

    Args:
        pattern: Pattern definition containing name, description, endpoint, body_template
        base_url: Base URL for the API (default: {{baseUrl}} variable)

    Returns:
        Postman request item dictionary
    """
    return {
        "name": pattern["name"],
        "request": {
            "method": "POST",
            "header": [],
            "body": {
                "mode": "raw",
                "raw": json.dumps(pattern["body_template"], indent=2),
                "options": {
                    "raw": {
                        "language": "json"
                    }
                }
            },
            "url": {
                "raw": f"{base_url}{pattern['endpoint']}",
                "host": base_url.split("://")[-1].split("/")[0] if "://" in base_url else base_url,
                "path": pattern['endpoint'].strip('/').split('/')
            },
            "description": pattern["description"]
        },
        "response": []
    }


def generate_getting_started_collection() -> Dict[str, Any]:
    """
    Generate the complete Getting Started collection.

    Returns:
        Complete Postman collection dictionary
    """
    collection = {
        "info": {
            "name": "C2M API v2 - Getting Started",
            "description": "Educational collection showing common API usage patterns organized by frequency.\n\n"
                          "**Categories:**\n"
                          "- **Most Frequently Used**: Essential calls every user needs\n"
                          "- **Bulk Operations**: High-volume and batch processing\n"
                          "- **Advanced Patterns**: Less common features and variations\n\n"
                          "**How to use:**\n"
                          "1. Set your `{{baseUrl}}` environment variable\n"
                          "2. Replace `<string>` and `<integer>` placeholders with actual values\n"
                          "3. Review the description of each request to understand the pattern\n"
                          "4. Copy the pattern and adapt it to your needs",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    # Add "Most Frequently Used" folder
    most_frequent_folder = {
        "name": "Most Frequently Used",
        "description": "The essential API calls that most users need. Start here if you're new to the API.",
        "item": [create_request_item(pattern) for pattern in MOST_FREQUENT_PATTERNS]
    }
    collection["item"].append(most_frequent_folder)

    # Add "Bulk Operations" folder
    bulk_folder = {
        "name": "Bulk Operations",
        "description": "High-volume processing patterns for handling multiple documents or recipients efficiently.",
        "item": [create_request_item(pattern) for pattern in BULK_PATTERNS]
    }
    collection["item"].append(bulk_folder)

    # Add "Advanced Patterns" folder
    advanced_folder = {
        "name": "Advanced Patterns",
        "description": "Less frequently used features and variations. Explore these once you're comfortable with the basics.",
        "item": [create_request_item(pattern) for pattern in ADVANCED_PATTERNS]
    }
    collection["item"].append(advanced_folder)

    return collection


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    print("📚 Generating Getting Started collection...")

    # Generate the collection
    collection = generate_getting_started_collection()

    # Count items for summary
    total_patterns = sum(len(folder["item"]) for folder in collection["item"])

    # Save to file
    output_path = "postman/generated/c2mapiv2-getting-started-collection.json"
    with open(output_path, 'w') as f:
        json.dump(collection, f, indent=2)

    print(f"✅ Successfully generated Getting Started collection!")
    print(f"   Output: {output_path}")
    print(f"   Categories: {len(collection['item'])}")
    print(f"   Total patterns: {total_patterns}")
    print()
    print("Next steps:")
    print("1. Upload to Postman workspace")
    print("2. Set {{baseUrl}} environment variable")
    print("3. Share with new API users for onboarding")


if __name__ == "__main__":
    main()

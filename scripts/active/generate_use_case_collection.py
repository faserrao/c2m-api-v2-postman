#!/usr/bin/env python3
"""
Generate Curated Use Case Collection for C2M API

This script generates a Postman collection organized by real-world use cases,
making it easy for developers to understand and test the API.

Each use case includes:
- Submit Job request with pre-populated payload
- Get Job Details follow-up
- Get Job Status follow-up
"""

import json
import sys
import uuid
import copy
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Default base URL placeholder
BASE_URL = "{{baseUrl}}"

# Use case definitions with their configurations
USE_CASES = {
    "legal_firm": {
        "name": "Legal Firm",
        "scenario_type": "[single-doc-job-template]",
        "description": "We have letters that we need to send all day. Each letter is sent to a specific recipient via Certified Mail. A copy is sent to their legal representative via First Class mail. Our system generates the PDF of the letter.",
        "endpoint": "/jobs/single-doc-job-template",
        "method": "POST",
        "payload": {
            "documentSourceIdentifier": {"documentId": 1234},
            "recipientAddressSources": [
                {
                    "firstName": "John",
                    "lastName": "Doe",
                    "address1": "123 Main Street",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001",
                    "country": "USA"
                },
                {
                    "firstName": "Jane",
                    "lastName": "Smith (Attorney)",
                    "address1": "456 Legal Avenue",
                    "city": "New York", 
                    "state": "NY",
                    "zip": "10002",
                    "country": "USA",
                    "nickName": "Attorney Copy"
                }
            ],
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
        "scenario_type": "[multi-pdf-address-capture]",
        "description": "We send invoices at the end of the month. Each invoice is in its own PDF. The address of the recipient is in the invoice.",
        "endpoint": "/jobs/multi-pdf-address-capture",
        "method": "POST",
        "payload": {
            "addressCapturePdfs": [
                {
                    "documentSourceIdentifier": {
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
                },
                {
                    "documentSourceIdentifier": {
                        "uploadRequestId": 100,
                        "documentName": "invoice_002.pdf"
                    },
                    "addressRegion": {
                        "x": 300,
                        "y": 100,
                        "width": 200,
                        "height": 100,
                        "pageOffset": 0
                    }
                },
                {
                    "documentSourceIdentifier": {
                        "uploadRequestId": 100,
                        "documentName": "invoice_003.pdf"
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
            "jobOptions": {
                "documentClass": "businessLetter",
                "layout": "portrait",
                "mailclass": "firstClassMail",
                "paperType": "letter",
                "printOption": "color",
                "envelope": "windowedFlat"
            },
            "paymentDetails": {
                "invoiceDetails": {
                    "invoiceNumber": "BATCH-2024-001",
                    "amountDue": 450.00
                }
            },
            "tags": ["invoices", "monthly-batch", "accounts-receivable"]
        }
    },
    
    "company_split_invoices": {
        "name": "Company #2",
        "scenario_type": "[single-pdf-split-addressCapture]", 
        "description": "We send invoices at the end of the month. All the invoices are in a single big PDF. The addresses of the recipients are in the invoices.",
        "endpoint": "/jobs/single-pdf-split-addressCapture",
        "method": "POST",
        "payload": {
            "documentSourceIdentifier": {
                "uploadRequestId": 200,
                "zipId": 10,
                "documentName": "combined_invoices.pdf"
            },
            "embeddedExtractionSpecs": [
                {
                    "startPage": 1,
                    "endPage": 1,
                    "addressRegion": {
                        "x": 50,
                        "y": 100,
                        "width": 200,
                        "height": 100,
                        "pageOffset": 0
                    }
                },
                {
                    "startPage": 2,
                    "endPage": 2,
                    "addressRegion": {
                        "x": 50,
                        "y": 100,
                        "width": 200,
                        "height": 100,
                        "pageOffset": 0
                    }
                }
            ],
            "paymentDetails": {
                "achDetails": {
                    "routingNumber": "021000021",
                    "accountNumber": "1234567890",
                    "checkDigit": 7
                }
            },
            "tags": ["split-pdf", "address-capture", "automated"]
        }
    },
    
    "real_estate_agent": {
        "name": "Real Estate Agent",
        "scenario_type": "[single-doc-job-template]",
        "description": "We send postcards as part of our campaign. The postcards have a specific template and use mail merge.",
        "endpoint": "/jobs/single-doc-job-template",
        "method": "POST",
        "payload": {
            "documentSourceIdentifier": {"externalUrl": "https://api.example.com/v1/marketing/postcards/luxury-homes"},
            "recipientAddressSources": [
                {"addressListId": 100},  # Address list ID for target neighborhood
                {"addressListId": 101},  # Address list ID for recent movers
                {"addressListId": 102}   # Address list ID for luxury buyers
            ],
            "jobTemplate": "postcard_luxury_homes",
            "paymentDetails": {
                "userCreditDetails": {
                    "creditAmount": 500.00
                }
            },
            "tags": ["marketing", "postcards", "real-estate", "bulk-mail"]
        }
    },
    
    "medical_agency": {
        "name": "Medical Agency",
        "scenario_type": "[multi-doc-merge-job-template]",
        "description": "We send medical reports to patients. Each report is a custom PDF. In addition, a few boiler-plate pages of generic medical information are sent with each report.",
        "endpoint": "/jobs/multi-doc-merge-job-template",
        "method": "POST",
        "payload": {
            "documentsToMerge": [
                {"documentId": 1001},  # Boilerplate header
                {
                    "uploadRequestId": 300,
                    "documentName": "patient_report.pdf"
                },
                {"documentId": 1002}   # Boilerplate footer with disclaimers
            ],
            "recipientAddressSource": {
                "firstName": "Patient",
                "lastName": "Name",
                "address1": "789 Health Street",
                "address2": "Suite 200",
                "city": "Chicago",
                "state": "IL", 
                "zip": "60601",
                "country": "USA"
            },
            "paymentDetails": {
                "invoiceDetails": {
                    "invoiceNumber": "MED-2024-567",
                    "amountDue": 75.00
                }
            },
            "tags": ["medical", "compliance", "patient-reports"]
        }
    },
    
    "monthly_newsletters": {
        "name": "Monthly Newsletters",
        "scenario_type": "[single-doc-job-template]",
        "description": "We are an organization that sends out flyers at the beginning of each month to our subscribers. The flyer is a static document and we have a mailing list it has to go out to.",
        "endpoint": "/jobs/single-doc-job-template",
        "method": "POST", 
        "payload": {
            "documentSourceIdentifier": {
                "zipId": 50,
                "documentName": "newsletter_december_2024.pdf"
            },
            "recipientAddressSources": [
                {"addressListId": 200},  # Subscriber list - Basic tier
                {"addressListId": 201},  # Subscriber list - Premium tier
                {"addressListId": 202}   # Subscriber list - VIP tier
            ],
            "jobTemplate": "monthly_newsletter_standard",
            "paymentDetails": {
                "creditCardDetails": {
                    "cardType": "mastercard",
                    "cardNumber": "5555555555554444",
                    "expirationDate": {"month": 6, "year": 2026},
                    "cvv": 456
                }
            },
            "tags": ["newsletter", "monthly", "subscribers", "marketing"]
        }
    },
    
    "reseller_merge_pdfs": {
        "name": "Reseller #1",
        "scenario_type": "[single-pdf-split]", 
        "description": "We receive PDFs from our customers. Each PDF is unique. We want to batch the PDFs into a single big PDF and send them in one go.",
        "endpoint": "/jobs/single-pdf-split", 
        "method": "POST",
        "payload": {
            "documentSourceIdentifier": {
                "uploadRequestId": 400,
                "documentName": "batched_pdfs.pdf"
            },
            "items": [
                {
                    "pageRange": {
                        "startPage": 1,
                        "endPage": 5
                    },
                    "recipientAddressSources": [{"addressListId": 301}]
                },
                {
                    "pageRange": {
                        "startPage": 6,
                        "endPage": 10
                    },
                    "recipientAddressSources": [{"addressListId": 302}]
                },
                {
                    "pageRange": {
                        "startPage": 11,
                        "endPage": 15
                    },
                    "recipientAddressSources": [{"addressListId": 303}]
                }
            ],
            "paymentDetails": {
                "applePayDetails": {
                    "applePaymentDetails": {}
                }
            },
            "tags": ["reseller", "pdf-merge", "b2b"]
        }
    },
    
    "reseller_zip_pdfs": {
        "name": "Reseller #2",
        "scenario_type": "[multi-doc]",
        "description": "We receive PDFs from our customers. Each PDF is unique. We want to zip the PDFs and send them in one go.",
        "endpoint": "/jobs/multi-doc",
        "method": "POST",
        "payload": {
            "items": [
                {
                    "documentSourceIdentifier": {
                        "uploadRequestId": 500,
                        "zipId": 20,
                        "documentName": "document_01.pdf"
                    },
                    "recipientAddressSource": {"addressId": 6001}
                },
                {
                    "documentSourceIdentifier": {
                        "uploadRequestId": 500,
                        "zipId": 20,
                        "documentName": "document_02.pdf"
                    },
                    "recipientAddressSource": {"addressId": 6002}
                },
                {
                    "documentSourceIdentifier": {
                        "uploadRequestId": 500,
                        "zipId": 20,
                        "documentName": "document_03.pdf"
                    },
                    "recipientAddressSource": {"addressId": 6003}
                }
            ],
            "jobOptions": {
                "documentClass": "businessLetter",
                "layout": "portrait",
                "mailclass": "priorityMail",
                "paperType": "letter",
                "printOption": "grayscale",
                "envelope": "letter"
            },
            "paymentDetails": {
                "googlePayDetails": {
                    "googlePaymentDetails": {}
                }
            },
            "tags": ["reseller", "zip-processing", "batch", "b2b"]
        }
    }
}

def create_submit_job_request(use_case_key: str, use_case: Dict) -> Dict:
    """Create a Submit Job request for a use case with ALL oneOf examples."""
    
    # Use the scenario_type as the request name
    request_name = use_case.get("scenario_type", "[unknown]")
    
    # Base request structure
    request = {
        "name": request_name,
        "event": [
            {
                "listen": "test",
                "script": {
                    "exec": [
                        "// Save jobId for follow-up requests",
                        "const response = pm.response.json();",
                        "if (response.jobId) {",
                        "    pm.collectionVariables.set('jobId', response.jobId);",
                        "    console.log('Job ID saved:', response.jobId);",
                        "}",
                        "",
                        "// Basic tests",
                        "pm.test('Status code is 200 or 201', function () {",
                        "    pm.expect(pm.response.code).to.be.oneOf([200, 201]);",
                        "});",
                        "",
                        "pm.test('Response has jobId', function () {",
                        "    pm.expect(response).to.have.property('jobId');",
                        "});"
                    ],
                    "type": "text/javascript"
                }
            }
        ],
        "request": {
            "method": use_case["method"],
            "header": [
                {
                    "key": "Content-Type",
                    "value": "application/json"
                },
                {
                    "key": "Authorization",
                    "value": "Bearer {{authToken}}",
                    "description": "JWT authentication token"
                }
            ],
            "body": {
                "mode": "raw",
                "raw": json.dumps(use_case["payload"], indent=2)
            },
            "url": {
                "raw": f"{BASE_URL}{use_case['endpoint']}",
                "host": [BASE_URL],
                "path": use_case["endpoint"].strip("/").split("/")
            },
            "description": f"Submit a job for {use_case['name']}.\n\n{use_case['description']}"
        },
        "response": []
    }
    
    # Add examples for different oneOf variants
    examples = []
    
    # Generate examples based on the use case
    base_payload = use_case["payload"].copy()
    
    # Add documentSourceIdentifier variants
    doc_source_variants = [
        ("Document ID", {"documentId": 1234}),
        ("External URL", {"externalUrl": "https://api.example.com/v1/documents/5678"}),
        ("Upload Request", {"uploadRequestId": 100, "documentName": f"{use_case_key}_document.pdf"}),
        ("Upload + Zip", {"uploadRequestId": 200, "zipId": 10, "documentName": f"{use_case_key}_doc.pdf"}),
        ("Zip Only", {"zipId": 20, "documentName": f"{use_case_key}_file.pdf"})
    ]
    
    # Add payment variants
    payment_variants = [
        ("Credit Card", {
            "creditCardDetails": {
                "cardType": "visa",
                "cardNumber": "4111111111111111",
                "expirationDate": {"month": 12, "year": 2025},
                "cvv": 123
            }
        }),
        ("Invoice", {
            "invoiceDetails": {
                "invoiceNumber": f"{use_case_key.upper()}-2024-001",
                "amountDue": 150.00
            }
        }),
        ("ACH", {
            "achDetails": {
                "routingNumber": "021000021",
                "accountNumber": "1234567890",
                "checkDigit": 7
            }
        }),
        ("User Credit", {
            "userCreditDetails": {
                "creditAmount": 50.00
            }
        }),
        ("Apple Pay", {
            "applePayDetails": {
                "applePaymentDetails": {}
            }
        }),
        ("Google Pay", {
            "googlePayDetails": {
                "googlePaymentDetails": {}
            }
        })
    ]
    
    # Create examples combining different variants
    # For endpoints with recipientAddressSources array, also vary the address types
    recipient_variants = [
        ("New Address", {
            "firstName": "John",
            "lastName": "Doe",
            "address1": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "country": "USA"
        }),
        ("Address List ID", {"addressListId": 42}),  # addressListId
        ("Address ID", {"addressId": 12345})     # addressId
    ]
    
    # Create comprehensive examples covering all variants
    example_count = 0
    for doc_idx, (doc_name, doc_value) in enumerate(doc_source_variants):
        # Cycle through payment types
        pay_idx = doc_idx % len(payment_variants)
        pay_name, pay_value = payment_variants[pay_idx]
        
        example_payload = copy.deepcopy(base_payload)
        
        # Update documentSourceIdentifier if present
        if "documentSourceIdentifier" in example_payload:
            example_payload["documentSourceIdentifier"] = doc_value
        elif "items" in example_payload and isinstance(example_payload["items"], list):
            # For multi-doc endpoints
            for item in example_payload["items"]:
                if "documentSourceIdentifier" in item:
                    item["documentSourceIdentifier"] = doc_value
        elif "documentsToMerge" in example_payload:
            # For merge endpoints - preserve boilerplate docs for medical agency
            if use_case_key == "medical_agency":
                # Keep the boilerplate header (1001) and footer (1002)
                # Only update the middle document
                example_payload["documentsToMerge"][1] = doc_value
            else:
                # For other use cases, update the first document
                example_payload["documentsToMerge"][0] = doc_value
        
        # Update payment details
        if "paymentDetails" in example_payload:
            example_payload["paymentDetails"] = pay_value
        
        # Update recipientAddressSources if present (vary the types)
        if "recipientAddressSources" in example_payload:
            # Use different recipient types for variety
            recip_idx = doc_idx % len(recipient_variants)
            recip_name, recip_value = recipient_variants[recip_idx]
            # Keep array structure but vary the content
            example_payload["recipientAddressSources"] = [recip_value]
            if isinstance(recip_value, dict):
                # Add a second address for new address type
                example_payload["recipientAddressSources"].append({
                    "firstName": "Jane",
                    "lastName": "Smith",
                    "address1": "456 Oak Avenue",
                    "city": "Boston",
                    "state": "MA",
                    "zip": "02101",
                    "country": "USA"
                })
            example_name = f"{use_case_key} - {doc_name} + {pay_name} + {recip_name}"
        elif "recipientAddressSource" in example_payload:
            # Single recipient (not array)
            recip_idx = doc_idx % len(recipient_variants)
            recip_name, recip_value = recipient_variants[recip_idx]
            example_payload["recipientAddressSource"] = recip_value
            example_name = f"{use_case_key} - {doc_name} + {pay_name} + {recip_name}"
        else:
            # Create example name without recipient
            example_name = f"{use_case_key} - {doc_name} + {pay_name}"
        
        examples.append({
                "name": example_name,
                "originalRequest": {
                    "method": use_case["method"],
                    "header": request["request"]["header"],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps(example_payload, indent=2)
                    },
                    "url": request["request"]["url"]
                },
                "status": "Success",
                "code": 200,
                "_postman_previewlanguage": "json",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "cookie": [],
                "body": json.dumps({
                    "status": "success",
                    "message": "Job created successfully",
                    "jobId": 123456
                }, indent=2)
            })
    
    # Add the examples to the request
    request["response"] = examples
    
    return request

def create_get_job_details_request() -> Dict:
    """Create a Get Job Details request."""
    return {
        "name": "Get Job Details",
        "event": [
            {
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 200', function () {",
                        "    pm.response.to.have.status(200);",
                        "});",
                        "",
                        "pm.test('Response has job details', function () {",
                        "    const response = pm.response.json();",
                        "    pm.expect(response).to.have.property('jobId');",
                        "    pm.expect(response).to.have.property('status');",
                        "});"
                    ],
                    "type": "text/javascript"
                }
            }
        ],
        "request": {
            "method": "GET",
            "header": [
                {
                    "key": "Authorization",
                    "value": "Bearer {{authToken}}",
                    "description": "JWT authentication token"
                }
            ],
            "url": {
                "raw": f"{BASE_URL}/jobs/{{{{jobId}}}}",
                "host": [BASE_URL],
                "path": ["jobs", "{{jobId}}"]
            },
            "description": "Retrieve detailed information about the job using the jobId from the Submit Job request."
        },
        "response": []
    }

def create_get_job_status_request() -> Dict:
    """Create a Get Job Status request."""
    return {
        "name": "Get Job Status",
        "event": [
            {
                "listen": "test",
                "script": {
                    "exec": [
                        "pm.test('Status code is 200', function () {",
                        "    pm.response.to.have.status(200);",
                        "});",
                        "",
                        "pm.test('Response has status field', function () {",
                        "    const response = pm.response.json();",
                        "    pm.expect(response).to.have.property('status');",
                        "    pm.expect(['queued', 'processing', 'completed', 'failed']).to.include(response.status);",
                        "});"
                    ],
                    "type": "text/javascript"
                }
            }
        ],
        "request": {
            "method": "GET",
            "header": [
                {
                    "key": "Authorization", 
                    "value": "Bearer {{authToken}}",
                    "description": "JWT authentication token"
                }
            ],
            "url": {
                "raw": f"{BASE_URL}/jobs/{{{{jobId}}}}/status",
                "host": [BASE_URL],
                "path": ["jobs", "{{jobId}}", "status"]
            },
            "description": "Check the processing status of the job (queued, processing, completed, failed)."
        },
        "response": []
    }

def create_collection() -> Dict:
    """Create the complete curated use case collection."""
    collection = {
        "info": {
            "name": "C2M API v2 – Real World Use Cases",
            "description": (
                "Real-world use cases for the C2M API v2. Each folder contains pre-populated requests for specific business scenarios.\n\n"
                "**Getting Started:**\n"
                "1. **Select Environment** (top-right dropdown) → Choose 'C2M Mock Server'\n"
                "2. **Find this collection** → In the Collections sidebar, locate 'C2M API v2 – Real World Use Cases'\n"
                "3. **Expand the collection** → Click the arrow next to 'C2M API v2 – Real World Use Cases'\n"
                "4. **Choose a use case folder** → Click arrow next to a folder (e.g., 'Legal Firm')\n"
                "5. **Expand the POST request** → Click arrow next to 'POST [single-doc-job-template]'\n"
                "6. **Select an example** → Click one of the pre-filled examples (e.g., 'legal_firm - Document ID + Credit Card + New Address')\n"
                "7. **Review the Body tab** → See the pre-populated request data for this scenario\n"
                "8. **Click Send** → Response includes jobId for the submitted job\n\n"
                "**Use Case Scenarios:**\n\n"
                "**Legal Firm** - We have letters that we need to send all day. Each letter is sent to a specific recipient via Certified Mail. A copy is sent to their legal representative via First Class mail. Our system generates the PDF of the letter.\n"
                "`[single-doc-job-template]`\n\n"
                "**Company #1** - We send invoices at the end of the month. Each invoice is in its own PDF. The address of the recipient is in the invoice.\n"
                "`[multi-pdf-address-capture]`\n\n"
                "**Company #2** - We send invoices at the end of the month. All the invoices are in a single big PDF. The addresses of the recipients are in the invoices.\n"
                "`[single-pdf-split-addressCapture]`\n\n"
                "**Real Estate Agent** - We send postcards as part of our campaign. The postcards have a specific template and use mail merge.\n"
                "`[single-doc-job-template]`\n\n"
                "**Medical Agency** - We send medical reports to patients. Each report is a custom PDF. In addition, a few boiler-plate pages of generic medical information are sent with each report.\n"
                "`[multi-doc-merge-job-template]`\n\n"
                "**Monthly Newsletters** - We are an organization that sends out flyers at the beginning of each month to our subscribers. The flyer is a static document and we have a mailing list it has to go out to.\n"
                "`[single-doc-job-template]`\n\n"
                "**Reseller #1** - We receive PDFs from our customers. Each PDF is unique. We want to batch the PDFs into a single big PDF and send them in one go.\n"
                "`[single-pdf-split]`\n\n"
                "**Reseller #2** - We receive PDFs from our customers. Each PDF is unique. We want to zip the PDFs and send them in one go.\n"
                "`[multi-doc]`\n\n"
                "**Note:** JWT tokens are handled automatically - no manual auth needed!"
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "_postman_id": str(uuid.uuid4()),
            "version": {
                "major": 1,
                "minor": 0,
                "patch": 0
            }
        },
        "item": [],
        "event": [
            {
                "listen": "prerequest",
                "script": {
                    "type": "text/javascript",
                    "exec": [
                        "// JWT Authentication Pre-request Script",
                        "// This script automatically handles JWT token acquisition and refresh",
                        "",
                        "// Skip auth for token endpoints themselves",
                        "if (pm.request.url.path.includes('auth/tokens')) {",
                        "    console.log('Skipping auth for token endpoint');",
                        "    return;",
                        "}",
                        "",
                        "// Check if we have client credentials",
                        "const clientId = pm.environment.get('clientId') || pm.collectionVariables.get('clientId');",
                        "const clientSecret = pm.environment.get('clientSecret') || pm.collectionVariables.get('clientSecret');",
                        "",
                        "if (!clientId || !clientSecret) {",
                        "    console.warn('Client credentials not configured. Set clientId and clientSecret in environment.');",
                        "    return;",
                        "}",
                        "",
                        "// Function to get a new token",
                        "async function getNewToken() {",
                        "    const authUrl = pm.environment.get('authUrl') || pm.collectionVariables.get('authUrl');",
                        "    if (!authUrl) {",
                        "        console.error('authUrl not configured');",
                        "        return null;",
                        "    }",
                        "",
                        "    const tokenRequest = {",
                        "        url: authUrl + '/auth/tokens/long',",
                        "        method: 'POST',",
                        "        header: {",
                        "            'Content-Type': 'application/json'",
                        "        },",
                        "        body: {",
                        "            mode: 'raw',",
                        "            raw: JSON.stringify({",
                        "                grant_type: 'client_credentials',",
                        "                client_id: clientId,",
                        "                client_secret: clientSecret",
                        "            })",
                        "        }",
                        "    };",
                        "",
                        "    try {",
                        "        const response = await pm.sendRequest(tokenRequest);",
                        "        if (response.code === 200 || response.code === 201) {",
                        "            const tokenData = response.json();",
                        "            return tokenData.access_token;",
                        "        } else {",
                        "            console.error('Failed to get token:', response.code, response.status);",
                        "            return null;",
                        "        }",
                        "    } catch (error) {",
                        "        console.error('Error getting token:', error);",
                        "        return null;",
                        "    }",
                        "}",
                        "",
                        "// Main authentication logic",
                        "(async function() {",
                        "    let token = pm.environment.get('authToken') || pm.collectionVariables.get('authToken');",
                        "    ",
                        "    // If no token, get a new one",
                        "    if (!token) {",
                        "        console.log('No token found, acquiring new token...');",
                        "        token = await getNewToken();",
                        "        if (token) {",
                        "            pm.environment.set('authToken', token);",
                        "            pm.collectionVariables.set('authToken', token);",
                        "        }",
                        "    }",
                        "    ",
                        "    // Add token to request if we have one",
                        "    if (token) {",
                        "        // Check if we're using a mock server - FIX: Check ACTUAL request URL",
                        "        const requestUrl = pm.request.url.toString();",
                        "        const baseUrlVar = pm.environment.get('baseUrl') || pm.collectionVariables.get('baseUrl') || '';",
                        "        const isMockServer = requestUrl.includes('mock.pstmn.io') ||",
                        "                           requestUrl.includes('localhost:4010');",
                        "        ",
                        "        // Enhanced logging for debugging",
                        "        console.log('=== JWT AUTH DEBUG ===');",
                        "        console.log('Request URL:', requestUrl);",
                        "        console.log('BaseUrl variable:', baseUrlVar);",
                        "        console.log('Is mock server:', isMockServer);",
                        "        console.log('Long-term token (last 20 chars):', token ? '...' + token.slice(-20) : 'NONE');",
                        "        ",
                        "        if (!isMockServer) {",
                        "            pm.request.headers.add({",
                        "                key: 'Authorization',",
                        "                value: 'Bearer ' + token",
                        "            });",
                        "            console.log('✅ JWT token obtained and Authorization header ADDED (real API detected)');",
                        "        } else {",
                        "            console.log('⏭️  JWT token obtained and saved, but Authorization header SKIPPED (mock server detected)');",
                        "        }",
                        "        console.log('=== END DEBUG ===');",
                        "    } else {",
                        "        console.warn('No token available - request may fail with 401');",
                        "    }",
                        "})();"
                    ]
                }
            }
        ],
        "variable": [
            {
                "key": "baseUrl",
                "value": "https://api.example.com/v1",
                "type": "string",
                "description": "Base URL for the C2M API"
            },
            {
                "key": "authUrl",
                "value": "https://j0dos52r5e.execute-api.us-east-1.amazonaws.com/dev",
                "type": "string",
                "description": "Authentication server URL"
            },
            {
                "key": "clientId",
                "value": "",
                "type": "string",
                "description": "Client ID for authentication"
            },
            {
                "key": "clientSecret",
                "value": "",
                "type": "string",
                "description": "Client secret for authentication (keep secure!)"
            },
            {
                "key": "authToken",
                "value": "",
                "type": "string",
                "description": "JWT authentication token (auto-populated)"
            },
            {
                "key": "jobId",
                "value": "",
                "type": "string",
                "description": "Current job ID (automatically set by Submit Job requests)"
            }
        ]
    }
    
    # Add each use case as a folder
    for use_case_key, use_case in USE_CASES.items():
        folder = {
            "name": use_case["name"],
            "description": use_case["description"],
            "item": [
                create_submit_job_request(use_case_key, use_case)
            ]
        }
        collection["item"].append(folder)
    
    return collection

def main():
    if len(sys.argv) != 2:
        print("Usage: generate_use_case_collection.py <output.json>")
        print("\nThis script generates a curated Postman collection with real-world use cases.")
        sys.exit(1)
    
    output_file = sys.argv[1]
    
    print("📚 Generating curated use case collection...")
    collection = create_collection()
    
    print(f"📊 Created {len(USE_CASES)} use cases with {len(USE_CASES)} total requests")
    
    print(f"💾 Saving collection to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(collection, f, indent=2)
    
    print("✅ Successfully generated use case collection!")
    print("\nNext steps:")
    print("1. Import this collection into Postman")
    print("2. Set the 'authToken' variable with your JWT")
    print("3. Run any use case folder to test the API")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Generate Curated Use Case Collection for C2M API - Version 2

This version reads permutations from the pre-generated JSON files in
data_dictionary/generate-endpoint-permutations/permutations/

It randomly selects 5 permutations for each use case to ensure variety.
"""

import json
import sys
import uuid
import random
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Default base URL placeholder
BASE_URL = "{{baseUrl}}"

# Path to permutation files
PERMUTATIONS_DIR = Path(__file__).parent.parent.parent / "data_dictionary" / "generate-endpoint-permutations" / "permutations"

# Use case definitions with their configurations and file mappings
USE_CASES = {
    "legal_firm": {
        "name": "Legal Firm",
        "scenario_type": "[single-doc-job-template]",
        "description": "We have letters that we need to send all day. Each letter is sent to a specific recipient via Certified Mail. A copy is sent to their legal representative via First Class mail. Our system generates the PDF of the letter.",
        "endpoint": "/jobs/single-doc-job-template",
        "method": "POST",
        "permutation_file": "submitSingleDocWithTemplateParams.json"
    },
    
    "company_invoice_batch": {
        "name": "Company #1",
        "scenario_type": "[multi-pdf-address-capture]",
        "description": "We send invoices at the end of the month. Each invoice is in its own PDF. The address of the recipient is in the invoice.",
        "endpoint": "/jobs/multi-pdf-address-capture",
        "method": "POST",
        "permutation_file": "multiPdfWithCaptureParams.json"
    },
    
    "company_split_invoices": {
        "name": "Company #2",
        "scenario_type": "[single-pdf-split-addressCapture]", 
        "description": "We send invoices at the end of the month. All the invoices are in a single big PDF. The addresses of the recipients are in the invoices.",
        "endpoint": "/jobs/single-pdf-split-addressCapture",
        "method": "POST",
        "permutation_file": "splitPdfWithCaptureParams.json"
    },
    
    "real_estate_agent": {
        "name": "Real Estate Agent",
        "scenario_type": "[single-doc-job-template]",
        "description": "We send postcards as part of our campaign. The postcards have a specific template and use mail merge.",
        "endpoint": "/jobs/single-doc-job-template",
        "method": "POST",
        "permutation_file": "submitSingleDocWithTemplateParams.json"
    },
    
    "medical_agency": {
        "name": "Medical Agency",
        "scenario_type": "[multi-doc-merge-job-template]",
        "description": "We send medical reports to patients. Each report is a custom PDF. In addition, a few boiler-plate pages of generic medical information are sent with each report.",
        "endpoint": "/jobs/multi-doc-merge-job-template",
        "method": "POST",
        "permutation_file": "mergeMultiDocWithTemplateParams.json"
    },
    
    "monthly_newsletters": {
        "name": "Monthly Newsletters",
        "scenario_type": "[single-doc-job-template]",
        "description": "We are an organization that sends out flyers at the beginning of each month to our subscribers. The flyer is a static document and we have a mailing list it has to go out to.",
        "endpoint": "/jobs/single-doc-job-template",
        "method": "POST",
        "permutation_file": "submitSingleDocWithTemplateParams.json"
    },
    
    "reseller_merge_pdfs": {
        "name": "Reseller #1",
        "scenario_type": "[single-pdf-split]", 
        "description": "We receive PDFs from our customers. Each PDF is unique. We want to batch the PDFs into a single big PDF and send them in one go.",
        "endpoint": "/jobs/single-pdf-split", 
        "method": "POST",
        "permutation_file": "splitPdfParams.json"
    },
    
    "reseller_zip_pdfs": {
        "name": "Reseller #2",
        "scenario_type": "[multi-doc]",
        "description": "We receive PDFs from our customers. Each PDF is unique. We want to zip the PDFs and send them in one go.",
        "endpoint": "/jobs/multi-doc",
        "method": "POST",
        "permutation_file": "submitMultiDocParams.json"
    }
}

def load_permutations(filename: str) -> List[Dict]:
    """Load permutations from a JSON file."""
    filepath = PERMUTATIONS_DIR / filename
    if not filepath.exists():
        print(f"⚠️  Warning: Permutation file not found: {filepath}")
        return []
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return data.get("permutations", [])

def select_diverse_permutations(permutations: List[Dict], count: int = 5) -> List[Dict]:
    """
    Select diverse permutations using a combination of random and strategic selection.
    
    Strategy:
    1. If we have fewer than requested, return all
    2. Otherwise, divide the list into sections and pick one from each section
    3. Add random picks if sections don't give us enough
    """
    if len(permutations) <= count:
        return permutations
    
    selected = []
    selected_indices = set()
    
    # Strategy 1: Divide into sections and pick one from each
    section_size = len(permutations) // count
    for i in range(count):
        # Pick a random index from each section
        start_idx = i * section_size
        end_idx = start_idx + section_size if i < count - 1 else len(permutations)
        
        if start_idx < len(permutations):
            idx = random.randint(start_idx, min(end_idx - 1, len(permutations) - 1))
            selected.append(permutations[idx])
            selected_indices.add(idx)
    
    # Strategy 2: If we need more, add random selections
    while len(selected) < count and len(selected) < len(permutations):
        idx = random.randint(0, len(permutations) - 1)
        if idx not in selected_indices:
            selected.append(permutations[idx])
            selected_indices.add(idx)
    
    return selected

def create_example_name(use_case_key: str, permutation: Dict, index: int) -> str:
    """Generate a descriptive name for an example based on its content."""
    parts = [use_case_key]
    
    # Add document source type
    if "documentSourceIdentifier" in permutation:
        doc_source = permutation["documentSourceIdentifier"]
        if "documentId" in doc_source:
            parts.append("DocID")
        elif "externalUrl" in doc_source:
            parts.append("ExtURL")
        elif "uploadRequestId" in doc_source and "zipId" in doc_source:
            parts.append("Upload+Zip")
        elif "uploadRequestId" in doc_source:
            parts.append("Upload")
        elif "zipId" in doc_source:
            parts.append("Zip")
    
    # Add payment type
    if "paymentDetails" in permutation:
        payment = permutation["paymentDetails"]
        if "creditCardDetails" in payment:
            parts.append("CreditCard")
        elif "invoiceDetails" in payment:
            parts.append("Invoice")
        elif "achDetails" in payment:
            parts.append("ACH")
        elif "userCreditDetails" in payment:
            parts.append("UserCredit")
        elif "applePayDetails" in payment:
            parts.append("ApplePay")
        elif "googlePayDetails" in payment:
            parts.append("GooglePay")
    
    # Add address type (if present)
    if "recipientAddressSource" in permutation:
        addr = permutation["recipientAddressSource"]
        if isinstance(addr, dict):
            if "addressId" in addr:
                parts.append("AddrID")
            elif "addressListId" in addr:
                parts.append("AddrListID")
            elif "firstName" in addr:
                parts.append("NewAddr")
    elif "recipientAddressSources" in permutation:
        # For arrays, check first element
        if permutation["recipientAddressSources"]:
            addr = permutation["recipientAddressSources"][0]
            if isinstance(addr, dict):
                if "addressId" in addr:
                    parts.append("AddrIDs")
                elif "addressListId" in addr:
                    parts.append("AddrListIDs")
                elif "firstName" in addr:
                    parts.append("NewAddrs")
    
    # Add example number
    parts.append(f"Ex{index}")
    
    return " - ".join(parts)

def create_submit_job_request(use_case_key: str, use_case: Dict, permutations: List[Dict]) -> Dict:
    """Create a Submit Job request for a use case using loaded permutations."""
    
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
                "raw": json.dumps(permutations[0] if permutations else {}, indent=2)
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
    
    # Create examples from the selected permutations
    examples = []
    for idx, permutation in enumerate(permutations, 1):
        example_name = create_example_name(use_case_key, permutation, idx)
        
        # Customize permutation based on use case
        customized_permutation = customize_permutation_for_use_case(use_case_key, permutation)
        
        examples.append({
            "name": example_name,
            "originalRequest": {
                "method": use_case["method"],
                "header": request["request"]["header"],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(customized_permutation, indent=2)
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

def customize_permutation_for_use_case(use_case_key: str, permutation: Dict) -> Dict:
    """Add use-case-specific customizations to a permutation."""
    # Make a copy to avoid modifying the original
    customized = json.loads(json.dumps(permutation))
    
    # Add use-case-specific tags
    use_case_tags = {
        "legal_firm": ["legal", "certified", "client-correspondence"],
        "company_invoice_batch": ["invoices", "monthly-batch", "accounts-receivable"],
        "company_split_invoices": ["split-pdf", "address-capture", "automated"],
        "real_estate_agent": ["marketing", "postcards", "real-estate", "bulk-mail"],
        "medical_agency": ["medical", "compliance", "patient-reports"],
        "monthly_newsletters": ["newsletter", "monthly", "subscribers", "marketing"],
        "reseller_merge_pdfs": ["reseller", "pdf-merge", "b2b"],
        "reseller_zip_pdfs": ["reseller", "zip-processing", "batch", "b2b"]
    }
    
    if use_case_key in use_case_tags:
        customized["tags"] = use_case_tags[use_case_key]
    
    # Add use-case-specific job template names where appropriate
    if "jobTemplate" in customized:
        template_mappings = {
            "legal_firm": "legal_certified_mail",
            "real_estate_agent": "postcard_luxury_homes",
            "monthly_newsletters": "monthly_newsletter_standard",
            "medical_agency": "medical_report_with_boilerplate"
        }
        if use_case_key in template_mappings:
            customized["jobTemplate"] = template_mappings[use_case_key]
    
    return customized

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
                "6. **Select an example** → Click one of the pre-filled examples (e.g., 'legal_firm - DocID - CreditCard - Ex1')\n"
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
                        "        // Check if we're using a mock server - if so, skip adding the Authorization header",
                        "        const baseUrl = pm.environment.get('baseUrl') || pm.collectionVariables.get('baseUrl') || '';",
                        "        const isMockServer = baseUrl.includes('mock.pstmn.io') || ",
                        "                           baseUrl.includes('localhost:4010') ||",
                        "                           pm.environment.get('isMockServer') === 'true';",
                        "        ",
                        "        if (!isMockServer) {",
                        "            pm.request.headers.add({",
                        "                key: 'Authorization',",
                        "                value: 'Bearer ' + token",
                        "            });",
                        "            console.log('Authorization header added');",
                        "        } else {",
                        "            console.log('Mock server detected - skipping Authorization header');",
                        "        }",
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
    
    # Seed random for reproducibility (remove this line for truly random selections)
    # random.seed(42)
    
    # Add each use case as a folder
    for use_case_key, use_case in USE_CASES.items():
        # Load permutations from file
        permutations = load_permutations(use_case["permutation_file"])
        
        if not permutations:
            print(f"⚠️  No permutations found for {use_case_key}")
            continue
        
        print(f"📁 {use_case['name']}: {len(permutations)} permutations available")
        
        # Select diverse permutations
        selected_permutations = select_diverse_permutations(permutations, 5)
        print(f"   → Selected {len(selected_permutations)} examples")
        
        folder = {
            "name": use_case["name"],
            "description": use_case["description"],
            "item": [
                create_submit_job_request(use_case_key, use_case, selected_permutations)
            ]
        }
        collection["item"].append(folder)
    
    return collection

def main():
    if len(sys.argv) != 2:
        print("Usage: generate_use_case_collection_v2.py <output.json>")
        print("\nThis script generates a curated Postman collection with real-world use cases.")
        print("It reads permutations from data_dictionary/generate-endpoint-permutations/permutations/")
        sys.exit(1)
    
    output_file = sys.argv[1]
    
    print("📚 Generating curated use case collection (v2)...")
    print(f"📂 Reading permutations from: {PERMUTATIONS_DIR}")
    
    collection = create_collection()
    
    print(f"\n📊 Created {len(USE_CASES)} use cases")
    
    print(f"\n💾 Saving collection to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(collection, f, indent=2)
    
    print("✅ Successfully generated use case collection!")
    print("\nNext steps:")
    print("1. Import this collection into Postman")
    print("2. Set the 'authToken' variable with your JWT")
    print("3. Run any use case folder to test the API")

if __name__ == "__main__":
    main()
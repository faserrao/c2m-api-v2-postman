#!/usr/bin/env python3
"""
C2M API Python SDK Comprehensive Examples

This file demonstrates usage of all available endpoints in the C2M API.
Each section includes practical examples with common use cases.
"""

import c2m_api
from c2m_api.rest import ApiException
import time
import json
from datetime import datetime, timedelta

# =============================
# CONFIGURATION
# =============================

# Basic configuration
configuration = c2m_api.Configuration(
    host="https://api.c2m.com/v2",
    api_key={'Authorization': 'Bearer YOUR_API_KEY'}
)

# Advanced configuration options
# configuration.debug = True  # Enable debug logging
# configuration.timeout = 120  # Set timeout to 120 seconds
# configuration.proxy = "http://proxy.company.com:8080"  # Use proxy
# configuration.verify_ssl = False  # Disable SSL verification (dev only!)

# =============================
# AUTHENTICATION EXAMPLES
# =============================

def auth_examples():
    """Examples for authentication endpoints"""
    
    # Create auth API instance
    with c2m_api.ApiClient(configuration) as api_client:
        auth_api = c2m_api.AuthApi(api_client)
        
        # Example 1: Issue Long-Term Token (90 days)
        print("\n=== Issue Long-Term Token Example ===")
        try:
            long_token_request = c2m_api.LongTokenRequest(
                grant_type="client_credentials",
                client_id="your_client_id",
                client_secret="your_client_secret",
                scopes=["jobs:submit", "templates:read", "jobs:read"],
                ttl_seconds=7776000  # 90 days
            )
            
            long_token_response = auth_api.issue_long_term_token(long_token_request)
            print(f"Long-term token issued: {long_token_response.access_token[:20]}...")
            print(f"Expires in: {long_token_response.expires_in} seconds")
            print(f"Token type: {long_token_response.token_type}")
            
            # Store the token for later use
            long_term_token = long_token_response.access_token
            
        except ApiException as e:
            print(f"Error issuing long-term token: {e.status} - {e.body}")
        
        # Example 2: Issue Short-Term Token (1 hour)
        print("\n=== Issue Short-Term Token Example ===")
        try:
            short_token_request = c2m_api.ShortTokenRequest(
                grant_type="client_credentials",
                client_id="your_client_id",
                client_secret="your_client_secret"
            )
            
            short_token_response = auth_api.issue_short_term_token(short_token_request)
            print(f"Short-term token issued: {short_token_response.access_token[:20]}...")
            print(f"Expires in: {short_token_response.expires_in} seconds")
            
            # Store for later use
            short_term_token = short_token_response.access_token
            
        except ApiException as e:
            print(f"Error issuing short-term token: {e.status} - {e.body}")
        
        # Example 3: Revoke Token
        print("\n=== Revoke Token Example ===")
        try:
            # In a real scenario, you'd revoke an actual token
            # auth_api.revoke_token(token="token_to_revoke")
            print("Token revocation example (commented out to prevent accidental revocation)")
            
        except ApiException as e:
            print(f"Error revoking token: {e.status} - {e.body}")

# =============================
# SINGLE DOCUMENT SUBMISSION
# =============================

def single_doc_examples():
    """Examples for single document submission endpoints"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Example 1: Submit Single Document (Basic)
        print("\n=== Submit Single Document (Basic) Example ===")
        try:
            single_doc_request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://example.com/documents/invoice.pdf",
                job_options={
                    "mailclass": "first_class",
                    "color": True,
                    "duplex": True,
                    "envelope": "standard_window",
                    "paper_type": "standard"
                },
                payment_details={
                    "payment_method": "credit_card",
                    "credit_card": {
                        "card_number": "4111111111111111",
                        "expiration_date": "12/25",
                        "cvv": "123",
                        "cardholder_name": "John Doe"
                    }
                },
                recipient_address={
                    "name": "Jane Smith",
                    "company": "Acme Corp",
                    "address_line1": "123 Main Street",
                    "address_line2": "Suite 100",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001",
                    "country": "US"
                },
                return_address={
                    "name": "Your Company",
                    "address_line1": "456 Business Ave",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94105",
                    "country": "US"
                }
            )
            
            response = api.single_doc_job_params(single_doc_request)
            print(f"Job ID: {response.job_id}")
            print(f"Status: {response.status}")
            print(f"Tracking URL: {response.tracking_url}")
            
        except ApiException as e:
            print(f"Error submitting single document: {e.status} - {e.body}")
        
        # Example 2: Submit Single Document with Template
        print("\n=== Submit Single Document with Template Example ===")
        try:
            template_request = c2m_api.SubmitSingleDocWithTemplateParamsRequest(
                template_id="invoice-template-v2",
                document_url="https://example.com/documents/invoice-raw.html",
                template_variables={
                    "invoice_number": "INV-2024-001",
                    "due_date": "2024-12-31",
                    "amount": "$1,234.56",
                    "customer_name": "John Doe",
                    "items": [
                        {"description": "Service A", "quantity": 1, "price": "$500.00"},
                        {"description": "Service B", "quantity": 2, "price": "$367.28"}
                    ]
                },
                job_options={
                    "mailclass": "first_class",
                    "color": True,
                    "duplex": False
                },
                payment_details={
                    "payment_method": "ach",
                    "ach": {
                        "account_number": "123456789",
                        "routing_number": "021000021",
                        "account_type": "checking"
                    }
                },
                recipient_address={
                    "name": "Customer Service",
                    "company": "Big Corp LLC",
                    "address_line1": "789 Corporate Blvd",
                    "city": "Chicago",
                    "state": "IL",
                    "zip": "60601"
                }
            )
            
            response = api.submit_single_doc_with_template_params(template_request)
            print(f"Template Job ID: {response.job_id}")
            print(f"Status: {response.status}")
            print(f"Estimated Delivery: {response.estimated_delivery_date}")
            
        except ApiException as e:
            print(f"Error submitting with template: {e.status} - {e.body}")

# =============================
# MULTI-DOCUMENT SUBMISSION
# =============================

def multi_doc_examples():
    """Examples for multi-document submission endpoints"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Example 1: Submit Multiple Documents (Basic)
        print("\n=== Submit Multiple Documents (Basic) Example ===")
        try:
            multi_doc_request = c2m_api.SubmitMultiDocParamsRequest(
                documents=[
                    {
                        "document_url": "https://example.com/docs/statement1.pdf",
                        "recipient_address": {
                            "name": "Alice Johnson",
                            "address_line1": "111 First St",
                            "city": "Boston",
                            "state": "MA",
                            "zip": "02101"
                        }
                    },
                    {
                        "document_url": "https://example.com/docs/statement2.pdf",
                        "recipient_address": {
                            "name": "Bob Williams",
                            "address_line1": "222 Second Ave",
                            "city": "Seattle",
                            "state": "WA",
                            "zip": "98101"
                        }
                    },
                    {
                        "document_url": "https://example.com/docs/statement3.pdf",
                        "recipient_address": {
                            "name": "Carol Davis",
                            "address_line1": "333 Third Blvd",
                            "city": "Austin",
                            "state": "TX",
                            "zip": "78701"
                        }
                    }
                ],
                job_options={
                    "mailclass": "standard",
                    "color": False,
                    "duplex": True,
                    "batch_name": f"Monthly Statements - {datetime.now().strftime('%Y-%m')}"
                },
                payment_details={
                    "payment_method": "user_credit",
                    "use_credits": True
                }
            )
            
            response = api.submit_multi_doc_params(multi_doc_request)
            print(f"Batch Job ID: {response.batch_job_id}")
            print(f"Total Documents: {response.document_count}")
            print(f"Status: {response.status}")
            
        except ApiException as e:
            print(f"Error submitting multiple documents: {e.status} - {e.body}")
        
        # Example 2: Submit Multiple Documents with Template
        print("\n=== Submit Multiple Documents with Template Example ===")
        try:
            template_multi_request = c2m_api.SubmitMultiDocWithTemplateParamsRequest(
                template_id="monthly-newsletter",
                documents=[
                    {
                        "recipient_data": {
                            "name": "David Brown",
                            "address_line1": "444 Fourth St",
                            "city": "Denver",
                            "state": "CO",
                            "zip": "80201",
                            "custom_field_1": "Premium Member",
                            "custom_field_2": "Since 2020"
                        },
                        "template_variables": {
                            "greeting": "Dear David",
                            "member_type": "Premium",
                            "special_offer": "20% off next purchase"
                        }
                    },
                    {
                        "recipient_data": {
                            "name": "Emma Wilson",
                            "address_line1": "555 Fifth Ave",
                            "city": "Phoenix",
                            "state": "AZ",
                            "zip": "85001",
                            "custom_field_1": "Standard Member",
                            "custom_field_2": "Since 2023"
                        },
                        "template_variables": {
                            "greeting": "Dear Emma",
                            "member_type": "Standard",
                            "special_offer": "Free shipping on orders over $50"
                        }
                    }
                ],
                job_options={
                    "mailclass": "marketing",
                    "color": True,
                    "paper_type": "glossy"
                },
                payment_details={
                    "payment_method": "invoice",
                    "invoice": {
                        "purchase_order": "PO-2024-12345",
                        "billing_email": "billing@company.com"
                    }
                }
            )
            
            response = api.submit_multi_doc_with_template_params(template_multi_request)
            print(f"Template Batch ID: {response.batch_job_id}")
            print(f"Documents Processed: {response.document_count}")
            
        except ApiException as e:
            print(f"Error with template batch: {e.status} - {e.body}")

# =============================
# PDF MERGING EXAMPLES
# =============================

def pdf_merge_examples():
    """Examples for PDF merging endpoints"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Example 1: Merge Multiple PDFs (Basic)
        print("\n=== Merge Multiple PDFs (Basic) Example ===")
        try:
            merge_request = c2m_api.MergeMultiDocParamsRequest(
                documents=[
                    {
                        "document_url": "https://example.com/docs/cover-letter.pdf",
                        "page_range": "1-2"  # Include only first 2 pages
                    },
                    {
                        "document_url": "https://example.com/docs/report.pdf",
                        "page_range": "1-10"  # Include first 10 pages
                    },
                    {
                        "document_url": "https://example.com/docs/appendix.pdf"
                        # No page_range means include all pages
                    }
                ],
                output_options={
                    "filename": "merged-report.pdf",
                    "compress": True,
                    "optimize_for_web": True
                },
                job_options={
                    "mailclass": "first_class",
                    "color": True,
                    "duplex": True,
                    "binding": "left"
                },
                recipient_address={
                    "name": "Report Recipient",
                    "company": "Important Company",
                    "address_line1": "666 Sixth St",
                    "city": "Las Vegas",
                    "state": "NV",
                    "zip": "89101"
                }
            )
            
            response = api.merge_multi_doc_params(merge_request)
            print(f"Merge Job ID: {response.job_id}")
            print(f"Merged Document URL: {response.merged_document_url}")
            print(f"Total Pages: {response.total_pages}")
            
        except ApiException as e:
            print(f"Error merging PDFs: {e.status} - {e.body}")
        
        # Example 2: Merge PDFs with Template
        print("\n=== Merge PDFs with Template Example ===")
        try:
            template_merge_request = c2m_api.MergeMultiDocWithTemplateParamsRequest(
                template_id="contract-package",
                documents=[
                    {
                        "document_url": "https://example.com/contracts/main-agreement.pdf",
                        "document_type": "main_contract"
                    },
                    {
                        "document_url": "https://example.com/contracts/terms.pdf",
                        "document_type": "terms_conditions"
                    },
                    {
                        "document_url": "https://example.com/contracts/schedule-a.pdf",
                        "document_type": "schedule"
                    }
                ],
                template_variables={
                    "contract_date": "2024-01-15",
                    "party_a": "ABC Corporation",
                    "party_b": "XYZ Limited",
                    "contract_value": "$500,000"
                },
                merge_options={
                    "add_page_numbers": True,
                    "add_table_of_contents": True,
                    "bookmark_sections": True
                },
                job_options={
                    "mailclass": "certified",
                    "return_receipt": True,
                    "tracking": True
                },
                recipient_address={
                    "name": "Legal Department",
                    "company": "XYZ Limited",
                    "address_line1": "777 Seventh Ave",
                    "city": "Miami",
                    "state": "FL",
                    "zip": "33101"
                }
            )
            
            response = api.merge_multi_doc_with_template_params(template_merge_request)
            print(f"Template Merge Job ID: {response.job_id}")
            print(f"Tracking Number: {response.tracking_number}")
            
        except ApiException as e:
            print(f"Error with template merge: {e.status} - {e.body}")

# =============================
# PDF SPLITTING EXAMPLES
# =============================

def pdf_split_examples():
    """Examples for PDF splitting endpoints"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Example 1: Split PDF (Basic)
        print("\n=== Split PDF (Basic) Example ===")
        try:
            split_request = c2m_api.SplitPdfParamsRequest(
                document_url="https://example.com/docs/combined-statements.pdf",
                split_rules=[
                    {
                        "pages": "1-3",
                        "recipient_address": {
                            "name": "Frank Miller",
                            "address_line1": "888 Eighth St",
                            "city": "Portland",
                            "state": "OR",
                            "zip": "97201"
                        }
                    },
                    {
                        "pages": "4-6",
                        "recipient_address": {
                            "name": "Grace Lee",
                            "address_line1": "999 Ninth Ave",
                            "city": "Atlanta",
                            "state": "GA",
                            "zip": "30301"
                        }
                    },
                    {
                        "pages": "7-9",
                        "recipient_address": {
                            "name": "Henry Taylor",
                            "address_line1": "101 Tenth Blvd",
                            "city": "Detroit",
                            "state": "MI",
                            "zip": "48201"
                        }
                    }
                ],
                job_options={
                    "mailclass": "standard",
                    "color": False,
                    "duplex": True
                },
                payment_details={
                    "payment_method": "apple_pay",
                    "apple_pay": {
                        "payment_token": "apple_pay_token_here",
                        "device_id": "device_123"
                    }
                }
            )
            
            response = api.split_pdf_params(split_request)
            print(f"Split Job ID: {response.job_id}")
            print(f"Documents Created: {response.split_count}")
            for idx, doc in enumerate(response.split_documents):
                print(f"  Document {idx+1}: {doc.document_id} - {doc.page_count} pages")
            
        except ApiException as e:
            print(f"Error splitting PDF: {e.status} - {e.body}")
        
        # Example 2: Split PDF with Address Capture
        print("\n=== Split PDF with Address Capture Example ===")
        try:
            capture_split_request = c2m_api.SplitPdfWithCaptureParamsRequest(
                document_url="https://example.com/docs/bulk-invoices.pdf",
                capture_settings={
                    "address_location": "top_right",
                    "address_format": "us_standard",
                    "ocr_enabled": True,
                    "confidence_threshold": 0.85
                },
                split_on={
                    "keyword": "INVOICE",
                    "position": "top_center",
                    "include_keyword_page": True
                },
                job_options={
                    "mailclass": "first_class",
                    "color": True,
                    "envelope": "windowed"
                },
                fallback_address={
                    "name": "Undeliverable Mail",
                    "company": "Your Company",
                    "address_line1": "PO Box 12345",
                    "city": "Anytown",
                    "state": "CA",
                    "zip": "90210"
                }
            )
            
            response = api.split_pdf_with_capture_params(capture_split_request)
            print(f"Capture Split Job ID: {response.job_id}")
            print(f"Documents Processed: {response.document_count}")
            print(f"Addresses Captured: {response.captured_count}")
            print(f"Failed Captures: {response.failed_capture_count}")
            
        except ApiException as e:
            print(f"Error with capture split: {e.status} - {e.body}")

# =============================
# MULTI-PDF WITH CAPTURE
# =============================

def multi_pdf_capture_example():
    """Example for multi-PDF with address capture"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        print("\n=== Multi-PDF with Address Capture Example ===")
        try:
            multi_capture_request = c2m_api.MultiPdfWithCaptureParamsRequest(
                documents=[
                    {
                        "document_url": "https://example.com/batch/doc1.pdf",
                        "document_id": "DOC-001",
                        "expected_recipient_count": 50
                    },
                    {
                        "document_url": "https://example.com/batch/doc2.pdf",
                        "document_id": "DOC-002",
                        "expected_recipient_count": 75
                    },
                    {
                        "document_url": "https://example.com/batch/doc3.pdf",
                        "document_id": "DOC-003",
                        "expected_recipient_count": 100
                    }
                ],
                capture_settings={
                    "address_regions": ["top_left", "top_right"],
                    "use_ai_enhancement": True,
                    "validate_addresses": True,
                    "standardize_addresses": True
                },
                processing_options={
                    "parallel_processing": True,
                    "max_workers": 5,
                    "retry_failed_captures": True,
                    "retry_attempts": 3
                },
                job_options={
                    "mailclass": "standard",
                    "sort_by_zip": True,
                    "bundle_by_zip": True
                },
                notification_settings={
                    "email": "operations@company.com",
                    "webhook_url": "https://api.company.com/webhooks/c2m",
                    "notify_on": ["completion", "errors", "warnings"]
                }
            )
            
            response = api.multi_pdf_with_capture_params(multi_capture_request)
            print(f"Multi-Capture Job ID: {response.batch_job_id}")
            print(f"Total Documents: {response.total_documents}")
            print(f"Expected Recipients: {response.expected_recipients}")
            print(f"Processing Status: {response.status}")
            print(f"Estimated Completion: {response.estimated_completion_time}")
            
        except ApiException as e:
            print(f"Error with multi-capture: {e.status} - {e.body}")

# =============================
# ERROR HANDLING & UTILITIES
# =============================

def error_handling_examples():
    """Examples of error handling and utility functions"""
    
    print("\n=== Error Handling Examples ===")
    
    # Example 1: Comprehensive Error Handling
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        try:
            # This will fail with invalid data
            invalid_request = c2m_api.SingleDocJobParamsRequest(
                document_url="not-a-valid-url",
                recipient_address={
                    "name": "",  # Invalid: empty name
                    "address_line1": "",  # Invalid: empty address
                    "city": "",
                    "state": "XX",  # Invalid state
                    "zip": "00000"
                }
            )
            
            response = api.single_doc_job_params(invalid_request)
            
        except ApiException as e:
            print(f"API Exception caught:")
            print(f"  Status Code: {e.status}")
            print(f"  Reason: {e.reason}")
            print(f"  Response Body: {e.body}")
            print(f"  Headers: {dict(e.headers)}")
            
            # Parse error details if JSON
            try:
                error_detail = json.loads(e.body)
                print(f"  Error Code: {error_detail.get('error_code')}")
                print(f"  Error Message: {error_detail.get('message')}")
                print(f"  Field Errors: {error_detail.get('field_errors', {})}")
            except:
                pass
            
            # Handle specific status codes
            if e.status == 401:
                print("  Action: Token expired or invalid. Refreshing token...")
            elif e.status == 429:
                retry_after = e.headers.get('Retry-After', '60')
                print(f"  Action: Rate limited. Retry after {retry_after} seconds")
            elif e.status == 400:
                print("  Action: Invalid request. Check your input data.")
            elif e.status >= 500:
                print("  Action: Server error. Retrying with exponential backoff...")

# Example 2: Retry Logic with Exponential Backoff
def retry_with_backoff(func, max_retries=3, base_delay=1):
    """Retry a function with exponential backoff"""
    import random
    
    for attempt in range(max_retries):
        try:
            return func()
        except ApiException as e:
            if e.status == 429 or e.status >= 500:
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Attempt {attempt + 1} failed. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
            raise
    raise Exception(f"Failed after {max_retries} attempts")

# Example 3: Batch Processing with Progress
def batch_processing_example():
    """Example of processing documents in batches with progress tracking"""
    
    print("\n=== Batch Processing Example ===")
    
    # Simulate a list of documents to process
    documents = [
        {"id": f"DOC-{i:04d}", "url": f"https://example.com/docs/doc_{i}.pdf"}
        for i in range(1, 101)  # 100 documents
    ]
    
    batch_size = 25
    total_processed = 0
    failed_documents = []
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        for batch_start in range(0, len(documents), batch_size):
            batch_end = min(batch_start + batch_size, len(documents))
            batch = documents[batch_start:batch_end]
            
            print(f"\nProcessing batch {batch_start//batch_size + 1} "
                  f"(documents {batch_start + 1}-{batch_end} of {len(documents)})")
            
            try:
                # Process batch
                batch_request = c2m_api.SubmitMultiDocParamsRequest(
                    documents=[
                        {
                            "document_url": doc["url"],
                            "document_id": doc["id"],
                            "recipient_address": {
                                "name": f"Recipient {doc['id']}",
                                "address_line1": "123 Main St",
                                "city": "Anytown",
                                "state": "CA",
                                "zip": "12345"
                            }
                        }
                        for doc in batch
                    ],
                    job_options={
                        "mailclass": "standard",
                        "batch_name": f"Batch_{batch_start//batch_size + 1}"
                    }
                )
                
                # Simulate API call (commented out to prevent actual calls)
                # response = api.submit_multi_doc_params(batch_request)
                # print(f"  Batch submitted successfully. Job ID: {response.batch_job_id}")
                
                total_processed += len(batch)
                print(f"  Progress: {total_processed}/{len(documents)} "
                      f"({100*total_processed/len(documents):.1f}%)")
                
            except ApiException as e:
                print(f"  Batch failed: {e.status} - {e.reason}")
                failed_documents.extend([doc["id"] for doc in batch])
            
            # Rate limiting - pause between batches
            if batch_end < len(documents):
                time.sleep(2)  # 2 second delay between batches
    
    print(f"\n=== Batch Processing Complete ===")
    print(f"Total Processed: {total_processed}")
    print(f"Failed Documents: {len(failed_documents)}")
    if failed_documents:
        print(f"Failed IDs: {', '.join(failed_documents[:10])}")
        if len(failed_documents) > 10:
            print(f"  ... and {len(failed_documents) - 10} more")

# Example 4: Token Management with Auto-Refresh
class TokenManager:
    """Manages API tokens with automatic refresh"""
    
    def __init__(self, client_id, client_secret, api_client):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_client = api_client
        self.auth_api = c2m_api.AuthApi(api_client)
        self.token = None
        self.expires_at = 0
    
    def get_valid_token(self):
        """Get a valid token, refreshing if necessary"""
        current_time = time.time()
        
        # Refresh if token expires in less than 5 minutes
        if not self.token or current_time >= self.expires_at - 300:
            print("Refreshing API token...")
            self._refresh_token()
        
        return self.token
    
    def _refresh_token(self):
        """Refresh the token"""
        try:
            request = c2m_api.LongTokenRequest(
                grant_type="client_credentials",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=["jobs:submit", "templates:read"],
                ttl_seconds=3600  # 1 hour
            )
            
            response = self.auth_api.issue_long_term_token(request)
            self.token = response.access_token
            self.expires_at = time.time() + response.expires_in
            
            # Update configuration
            self.api_client.configuration.api_key['Authorization'] = f'Bearer {self.token}'
            
            print(f"Token refreshed. Expires in {response.expires_in} seconds")
            
        except ApiException as e:
            print(f"Failed to refresh token: {e.status} - {e.body}")
            raise

# Example 5: Webhook Handler
def webhook_handler_example():
    """Example webhook handler for C2M notifications"""
    
    print("\n=== Webhook Handler Example ===")
    
    # This would typically be in a web framework like Flask or FastAPI
    def handle_c2m_webhook(webhook_data):
        """Process incoming webhook from C2M"""
        
        event_type = webhook_data.get('event_type')
        job_id = webhook_data.get('job_id')
        timestamp = webhook_data.get('timestamp')
        
        print(f"Webhook received: {event_type} for job {job_id} at {timestamp}")
        
        if event_type == 'job.completed':
            print(f"  Job completed successfully")
            print(f"  Tracking URL: {webhook_data.get('tracking_url')}")
            print(f"  Documents sent: {webhook_data.get('document_count')}")
            
        elif event_type == 'job.failed':
            print(f"  Job failed")
            print(f"  Error: {webhook_data.get('error_message')}")
            print(f"  Failed documents: {webhook_data.get('failed_documents', [])}")
            
        elif event_type == 'delivery.confirmed':
            print(f"  Delivery confirmed")
            print(f"  Delivered to: {webhook_data.get('recipient_name')}")
            print(f"  Delivery date: {webhook_data.get('delivery_date')}")
            
        elif event_type == 'address.undeliverable':
            print(f"  Address undeliverable")
            print(f"  Reason: {webhook_data.get('reason')}")
            print(f"  Document ID: {webhook_data.get('document_id')}")
        
        # Return acknowledgment
        return {"status": "received", "timestamp": datetime.now().isoformat()}
    
    # Example webhook payloads
    sample_webhooks = [
        {
            "event_type": "job.completed",
            "job_id": "JOB-2024-12345",
            "timestamp": "2024-01-15T10:30:00Z",
            "tracking_url": "https://track.c2m.com/JOB-2024-12345",
            "document_count": 25
        },
        {
            "event_type": "delivery.confirmed",
            "job_id": "JOB-2024-12345",
            "document_id": "DOC-001",
            "timestamp": "2024-01-18T14:45:00Z",
            "recipient_name": "John Doe",
            "delivery_date": "2024-01-18"
        }
    ]
    
    for webhook in sample_webhooks:
        response = handle_c2m_webhook(webhook)
        print(f"  Handler response: {response}\n")

# =============================
# MAIN EXECUTION
# =============================

if __name__ == "__main__":
    print("C2M API Python SDK - Comprehensive Examples")
    print("=" * 50)
    
    # Note: These examples are designed to show API usage patterns.
    # In production, you would typically run only the specific
    # operations you need, not all examples at once.
    
    # Uncomment the examples you want to run:
    
    # auth_examples()
    # single_doc_examples()
    # multi_doc_examples()
    # pdf_merge_examples()
    # pdf_split_examples()
    # multi_pdf_capture_example()
    # error_handling_examples()
    # batch_processing_example()
    # webhook_handler_example()
    
    print("\n" + "=" * 50)
    print("Examples completed. Remember to:")
    print("1. Replace 'YOUR_API_KEY' with your actual API key")
    print("2. Use real document URLs for actual submissions")
    print("3. Implement proper error handling in production")
    print("4. Consider rate limits and implement appropriate delays")
    print("5. Store sensitive credentials securely (not in code)")
#!/usr/bin/env python3
"""
C2M API Python SDK - Comprehensive Examples with All Parameter Combinations

This file demonstrates every possible parameter combination for each endpoint.
Each section shows all variations of object types like DocumentSourceIdentifier,
RecipientAddressSource, and other complex objects.

Note: Template names follow realistic naming conventions like 'acme_corp_invoice_template_v2'
rather than generic names.
"""

import c2m_api
from c2m_api.rest import ApiException
import time
import json
from datetime import datetime

# =============================
# CONFIGURATION
# =============================

configuration = c2m_api.Configuration(
    host="https://api.c2m.com/v2",
    api_key={'Authorization': 'Bearer YOUR_API_KEY'}
)

# =============================
# AUTHENTICATION EXAMPLES
# =============================

def auth_comprehensive_examples():
    """Comprehensive authentication examples"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        auth_api = c2m_api.AuthApi(api_client)
        
        # Example 1: Long-Term Token with All Scopes
        print("\n=== Long-Term Token - Full Scope Example ===")
        try:
            long_token_request = c2m_api.LongTokenRequest(
                grant_type="client_credentials",
                client_id="acme_corp_prod_client",
                client_secret="your_client_secret",
                scopes=[
                    "jobs:submit",
                    "jobs:read",
                    "jobs:cancel",
                    "templates:read",
                    "templates:write",
                    "addresses:read",
                    "addresses:write",
                    "reports:read"
                ],
                ttl_seconds=7776000  # 90 days
            )
            
            response = auth_api.issue_long_term_token(long_token_request)
            print(f"Token: {response.access_token[:20]}...")
            print(f"Expires: {response.expires_in} seconds")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 2: Long-Term Token with Minimal Scope
        print("\n=== Long-Term Token - Minimal Scope Example ===")
        try:
            minimal_token_request = c2m_api.LongTokenRequest(
                grant_type="client_credentials",
                client_id="acme_corp_readonly_client",
                client_secret="your_client_secret",
                scopes=["jobs:read"],  # Read-only access
                ttl_seconds=86400  # 24 hours
            )
            
            response = auth_api.issue_long_term_token(minimal_token_request)
            print(f"Minimal token issued: {response.access_token[:20]}...")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 3: Short-Term Token (Always 1 hour)
        print("\n=== Short-Term Token Example ===")
        try:
            short_token_request = c2m_api.ShortTokenRequest(
                grant_type="client_credentials",
                client_id="acme_corp_temp_client",
                client_secret="your_client_secret"
            )
            
            response = auth_api.issue_short_term_token(short_token_request)
            print(f"Short token: {response.access_token[:20]}...")
            print(f"Fixed expiry: {response.expires_in} seconds")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")

# =============================
# SINGLE DOCUMENT - ALL VARIATIONS
# =============================

def single_doc_all_variations():
    """Single document submission with all DocumentSourceIdentifier variations"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Variation 1: Document URL (External)
        print("\n=== Single Doc - External URL ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://corporate-docs.acme.com/invoices/2024/INV-2024-001.pdf",
                job_options={
                    "documentClass": "businessLetter",
                    "layout": "portrait",
                    "mailclass": "firstClassMail",
                    "paperType": "letter",
                    "printOption": "color",
                    "envelope": "windowedFlat"
                },
                recipient_address={
                    "firstName": "John",
                    "lastName": "Doe",
                    "company": "Tech Innovations LLC",
                    "address1": "123 Innovation Drive",
                    "address2": "Suite 500",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94105",
                    "country": "USA"
                }
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 2: Document ID (Previously Uploaded)
        print("\n=== Single Doc - Document ID ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_id=12345,  # Previously uploaded document
                job_options={
                    "documentClass": "personalLetter",
                    "layout": "portrait",
                    "mailclass": "priorityMail",
                    "paperType": "letter",
                    "printOption": "grayscale",
                    "envelope": "flat"
                },
                recipient_address={
                    "firstName": "Jane",
                    "lastName": "Smith",
                    "address1": "456 Main Street",
                    "city": "Boston",
                    "state": "MA",
                    "zip": "02101"
                }
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 3: Upload Request + Document Name
        print("\n=== Single Doc - Upload Request with Document Name ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_source={
                    "uploadRequestId": 456,
                    "documentName": "acme_corp_annual_report_2024.pdf"
                },
                job_options={
                    "documentClass": "businessLetter",
                    "layout": "landscape",
                    "mailclass": "largeEnvelope",
                    "paperType": "legal",
                    "printOption": "color",
                    "envelope": "legal"
                },
                recipient_address={
                    "company": "Investment Partners Ltd",
                    "address1": "789 Financial Plaza",
                    "address2": "Floor 15",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10004"
                }
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 4: Upload Request + Zip + Document Name
        print("\n=== Single Doc - Upload Request with Zip ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_source={
                    "uploadRequestId": 456,
                    "zipId": 789,
                    "documentName": "quarterly_reports/Q4_2024_financials.pdf"
                },
                job_options={
                    "documentClass": "businessLetter",
                    "mailclass": "firstClassMail",
                    "printOption": "color"
                },
                recipient_address_id=67890  # Using saved address ID
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 5: Zip + Document Name Only
        print("\n=== Single Doc - Zip with Document Name ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_source={
                    "zipId": 789,
                    "documentName": "contracts/service_agreement_v3.pdf"
                },
                job_options={
                    "mailclass": "certifiedMail",
                    "returnReceipt": True
                },
                address_list_id=12345  # Using address list
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")

# =============================
# RECIPIENT ADDRESS VARIATIONS
# =============================

def recipient_address_all_variations():
    """Examples showing all RecipientAddressSource variations"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Variation 1: Full Inline Address with All Fields
        print("\n=== Recipient Address - Full Inline (All Fields) ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/notices/important_notice.pdf",
                recipient_address={
                    "firstName": "Robert",
                    "lastName": "Johnson",
                    "nickName": "Bob",
                    "company": "Johnson Industries",
                    "address1": "1234 Industrial Parkway",
                    "address2": "Building A",
                    "address3": "Suite 200",
                    "city": "Chicago",
                    "state": "IL",
                    "zip": "60601",
                    "country": "USA",
                    "phoneNumber": "312-555-0123"
                },
                job_options={
                    "mailclass": "firstClassMail"
                }
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 2: Minimal Inline Address (Required Fields Only)
        print("\n=== Recipient Address - Minimal Inline ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/bills/utility_bill.pdf",
                recipient_address={
                    "firstName": "Sarah",
                    "lastName": "Williams",
                    "address1": "5678 Oak Street",
                    "city": "Denver",
                    "state": "CO",
                    "zip": "80201"
                },
                job_options={
                    "mailclass": "standardMail"
                }
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 3: Address List ID
        print("\n=== Recipient Address - Address List ID ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/marketing/summer_promo_2024.pdf",
                address_list_id=98765,  # Pre-uploaded address list
                job_options={
                    "mailclass": "marketingMail",
                    "printOption": "color"
                }
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 4: Saved Address ID
        print("\n=== Recipient Address - Saved Address ID ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/statements/monthly_statement.pdf",
                saved_address_id=54321,  # Previously saved address
                job_options={
                    "mailclass": "firstClassMail",
                    "duplex": True
                }
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")

# =============================
# PAYMENT DETAILS VARIATIONS
# =============================

def payment_details_all_variations():
    """Examples showing all PaymentDetails variations"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Variation 1: Credit Card - Visa
        print("\n=== Payment - Credit Card (Visa) ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/invoice.pdf",
                payment_details={
                    "creditCardDetails": {
                        "cardType": "visa",
                        "cardNumber": "4111111111111111",
                        "expirationDate": {
                            "month": 12,
                            "year": 2025
                        },
                        "cvv": 123
                    }
                },
                recipient_address_id=12345
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 2: Credit Card - Mastercard
        print("\n=== Payment - Credit Card (Mastercard) ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/receipt.pdf",
                payment_details={
                    "creditCardDetails": {
                        "cardType": "mastercard",
                        "cardNumber": "5555555555554444",
                        "expirationDate": {
                            "month": 6,
                            "year": 2026
                        },
                        "cvv": 456
                    }
                },
                recipient_address_id=12345
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 3: ACH Payment
        print("\n=== Payment - ACH ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/payroll.pdf",
                payment_details={
                    "achDetails": {
                        "routingNumber": "123456789",
                        "accountNumber": "987654321",
                        "checkDigit": 1
                    }
                },
                recipient_address_id=12345
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 4: Invoice Payment
        print("\n=== Payment - Invoice ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/bulk_mailing.pdf",
                payment_details={
                    "invoiceDetails": {
                        "invoiceNumber": "ACME-INV-2024-12345",
                        "amountDue": 1500.00,
                        "purchaseOrder": "PO-2024-67890",
                        "department": "Marketing",
                        "costCenter": "MKT-001"
                    }
                },
                address_list_id=98765
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 5: User Credit
        print("\n=== Payment - User Credit (USD) ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/newsletter.pdf",
                payment_details={
                    "creditAmount": {
                        "amount": 100.00,
                        "currency": "USD"
                    }
                },
                address_list_id=98765
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 6: User Credit (EUR)
        print("\n=== Payment - User Credit (EUR) ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/eu_invoice.pdf",
                payment_details={
                    "creditAmount": {
                        "amount": 85.50,
                        "currency": "EUR"
                    }
                },
                recipient_address_id=12345
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 7: Apple Pay
        print("\n=== Payment - Apple Pay ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/order_confirmation.pdf",
                payment_details={
                    "applePaymentDetails": {
                        "paymentToken": "apple_pay_token_encrypted_data",
                        "transactionId": "AP-TXN-123456"
                    }
                },
                recipient_address_id=12345
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Variation 8: Google Pay
        print("\n=== Payment - Google Pay ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/digital_receipt.pdf",
                payment_details={
                    "googlePaymentDetails": {
                        "paymentToken": "google_pay_token_encrypted_data",
                        "transactionId": "GP-TXN-789012"
                    }
                },
                recipient_address_id=12345
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")

# =============================
# TEMPLATE VARIATIONS
# =============================

def template_examples_realistic():
    """Template examples with realistic corporate naming conventions"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Example 1: Corporate Invoice Template
        print("\n=== Template - Corporate Invoice ===")
        try:
            request = c2m_api.SubmitSingleDocWithTemplateParamsRequest(
                template_id="acme_corp_invoice_template_v3",
                document_url="https://data.acme.com/invoice_data_2024_001.json",
                template_variables={
                    "companyLogo": "https://assets.acme.com/logo_2024.png",
                    "invoiceNumber": "ACME-2024-INV-001234",
                    "invoiceDate": "2024-01-15",
                    "dueDate": "2024-02-15",
                    "customerName": "TechStart Industries",
                    "customerAddress": {
                        "line1": "100 Innovation Way",
                        "line2": "Suite 500",
                        "city": "San Jose",
                        "state": "CA",
                        "zip": "95110"
                    },
                    "lineItems": [
                        {
                            "description": "Enterprise Software License - Annual",
                            "quantity": 50,
                            "unitPrice": 299.99,
                            "total": 14999.50
                        },
                        {
                            "description": "Premium Support Package",
                            "quantity": 1,
                            "unitPrice": 5000.00,
                            "total": 5000.00
                        }
                    ],
                    "subtotal": 19999.50,
                    "tax": 1749.96,
                    "total": 21749.46,
                    "paymentTerms": "Net 30",
                    "bankDetails": {
                        "name": "Acme Corporation",
                        "routingNumber": "123456789",
                        "accountNumber": "****5678"
                    }
                },
                job_options={
                    "mailclass": "firstClassMail",
                    "color": True,
                    "duplex": False,
                    "envelope": "windowedFlat"
                },
                recipient_address={
                    "company": "TechStart Industries",
                    "attn": "Accounts Payable",
                    "address1": "100 Innovation Way",
                    "address2": "Suite 500",
                    "city": "San Jose",
                    "state": "CA",
                    "zip": "95110"
                }
            )
            
            response = api.submit_single_doc_with_template_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 2: Law Firm Contract Template
        print("\n=== Template - Law Firm Contract ===")
        try:
            request = c2m_api.SubmitSingleDocWithTemplateParamsRequest(
                template_id="smithjones_law_contract_template_2024_v2",
                document_url="https://contracts.smithjones.com/data/contract_45678.xml",
                template_variables={
                    "firmName": "Smith, Jones & Associates LLP",
                    "firmAddress": "One Legal Plaza, New York, NY 10004",
                    "contractDate": datetime.now().strftime("%B %d, %Y"),
                    "clientName": "Global Manufacturing Inc.",
                    "clientRepresentative": "Jennifer Chen, CEO",
                    "scopeOfWork": [
                        "Intellectual Property Portfolio Management",
                        "Patent Filing and Prosecution",
                        "Trademark Registration and Defense",
                        "Technology Licensing Agreements"
                    ],
                    "retainerAmount": "$50,000",
                    "hourlyRates": {
                        "partner": "$650/hour",
                        "seniorAssociate": "$450/hour",
                        "associate": "$350/hour",
                        "paralegal": "$150/hour"
                    },
                    "termLength": "24 months",
                    "governingLaw": "State of New York"
                },
                job_options={
                    "mailclass": "certifiedMail",
                    "returnReceipt": True,
                    "color": False,
                    "duplex": True,
                    "binding": "left"
                },
                recipient_address={
                    "company": "Global Manufacturing Inc.",
                    "attn": "Jennifer Chen, CEO",
                    "address1": "5000 Industrial Boulevard",
                    "city": "Detroit",
                    "state": "MI",
                    "zip": "48201"
                }
            )
            
            response = api.submit_single_doc_with_template_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 3: Healthcare Provider Template
        print("\n=== Template - Healthcare EOB ===")
        try:
            request = c2m_api.SubmitSingleDocWithTemplateParamsRequest(
                template_id="healthfirst_eob_template_2024_hipaa_compliant",
                document_url="https://secure.healthfirst.com/eob/data/claim_789012.json",
                template_variables={
                    "providerName": "HealthFirst Medical Group",
                    "providerTaxId": "12-3456789",
                    "memberName": "John Q. Patient",
                    "memberId": "HF123456789",
                    "claimNumber": "2024-CL-789012",
                    "serviceDate": "2024-01-10",
                    "services": [
                        {
                            "code": "99213",
                            "description": "Office Visit - Established Patient",
                            "charged": 250.00,
                            "allowed": 150.00,
                            "copay": 25.00,
                            "deductible": 50.00,
                            "coinsurance": 15.00,
                            "paid": 60.00
                        }
                    ],
                    "totalCharged": 250.00,
                    "totalAllowed": 150.00,
                    "totalPaid": 60.00,
                    "memberResponsibility": 90.00,
                    "deductibleMet": "$500 of $1,500",
                    "outOfPocketMet": "$750 of $3,000"
                },
                job_options={
                    "mailclass": "firstClassMail",
                    "envelope": "securityTinted",
                    "duplex": True
                },
                recipient_address={
                    "firstName": "John",
                    "lastName": "Patient",
                    "address1": "123 Health Street",
                    "city": "Boston",
                    "state": "MA",
                    "zip": "02115"
                }
            )
            
            response = api.submit_single_doc_with_template_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 4: Financial Services Statement Template
        print("\n=== Template - Investment Statement ===")
        try:
            request = c2m_api.SubmitSingleDocWithTemplateParamsRequest(
                template_id="capitalwealth_quarterly_statement_q4_2024",
                document_url="https://statements.capitalwealth.com/data/account_987654.json",
                template_variables={
                    "firmName": "Capital Wealth Management",
                    "quarterEnding": "December 31, 2024",
                    "accountNumber": "****6789",
                    "accountHolder": "Elizabeth R. Investor",
                    "beginningBalance": 250000.00,
                    "contributions": 15000.00,
                    "withdrawals": 0.00,
                    "investmentGains": 18750.00,
                    "fees": 625.00,
                    "endingBalance": 283125.00,
                    "ytdReturn": "7.5%",
                    "benchmarkReturn": "6.8%",
                    "holdings": [
                        {
                            "symbol": "VTSAX",
                            "name": "Vanguard Total Stock Market Index",
                            "shares": 1500.25,
                            "price": 98.50,
                            "value": 147774.63,
                            "allocation": "52.2%"
                        },
                        {
                            "symbol": "VTIAX",
                            "name": "Vanguard Total International Stock Index",
                            "shares": 2000.00,
                            "price": 32.25,
                            "value": 64500.00,
                            "allocation": "22.8%"
                        }
                    ],
                    "advisorName": "Michael Thompson, CFP",
                    "advisorPhone": "800-555-WEALTH"
                },
                job_options={
                    "mailclass": "firstClassMail",
                    "color": True,
                    "duplex": True,
                    "paperType": "premium"
                },
                recipient_address={
                    "firstName": "Elizabeth",
                    "lastName": "Investor",
                    "address1": "450 Park Avenue",
                    "address2": "Penthouse A",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10022"
                }
            )
            
            response = api.submit_single_doc_with_template_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")

# =============================
# ADDRESS CAPTURE VARIATIONS
# =============================

def address_capture_all_variations():
    """Examples showing all address capture extraction specifications"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Example 1: Single Region Extraction
        print("\n=== Address Capture - Single Region ===")
        try:
            request = c2m_api.SplitPdfWithCaptureParamsRequest(
                document_url="https://docs.acme.com/bulk/statements_batch_001.pdf",
                extraction_spec={
                    "startPage": 1,
                    "endPage": 1,
                    "addressRegion": {
                        "x": 50.0,      # 50 points from left
                        "y": 100.0,     # 100 points from top
                        "width": 250.0,  # 250 points wide
                        "height": 100.0, # 100 points tall
                        "pageOffset": 0  # Apply to each document's first page
                    }
                },
                job_options={
                    "mailclass": "standardMail",
                    "envelope": "windowedFlat"
                }
            )
            
            response = api.split_pdf_with_capture_params(request)
            print(f"Job ID: {response.job_id}")
            print(f"Captured: {response.captured_count} addresses")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 2: Multi-Page Region Extraction
        print("\n=== Address Capture - Multi-Page Region ===")
        try:
            request = c2m_api.SplitPdfWithCaptureParamsRequest(
                document_url="https://docs.acme.com/contracts/multipage_contracts.pdf",
                extraction_spec={
                    "startPage": 1,
                    "endPage": 3,    # Check first 3 pages
                    "addressRegion": {
                        "x": 350.0,      # Top right corner
                        "y": 50.0,
                        "width": 200.0,
                        "height": 150.0,
                        "pageOffset": 0
                    }
                },
                split_on={
                    "keyword": "CONTRACT NUMBER:",
                    "position": "top_left",
                    "includeKeywordPage": True
                },
                job_options={
                    "mailclass": "certifiedMail",
                    "returnReceipt": True
                }
            )
            
            response = api.split_pdf_with_capture_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 3: Multiple Region Extraction (Different Pages)
        print("\n=== Address Capture - Multiple Regions ===")
        try:
            request = c2m_api.MultiPdfWithCaptureParamsRequest(
                documents=[
                    {
                        "document_url": "https://docs.acme.com/invoices/batch_2024_01.pdf",
                        "document_id": "INV-BATCH-2024-01",
                        "extraction_specs": [
                            {
                                "startPage": 1,
                                "endPage": 1,
                                "addressRegion": {
                                    "x": 50.0,
                                    "y": 200.0,
                                    "width": 250.0,
                                    "height": 100.0,
                                    "pageOffset": 0
                                }
                            },
                            {
                                "startPage": 2,
                                "endPage": 2,
                                "addressRegion": {
                                    "x": 300.0,
                                    "y": 100.0,
                                    "width": 200.0,
                                    "height": 100.0,
                                    "pageOffset": 0
                                }
                            }
                        ]
                    }
                ],
                capture_settings={
                    "ocrEnabled": True,
                    "ocrLanguage": "eng",
                    "confidenceThreshold": 0.85,
                    "addressValidation": True,
                    "uspsStandardization": True
                },
                job_options={
                    "mailclass": "firstClassMail"
                }
            )
            
            response = api.multi_pdf_with_capture_params(request)
            print(f"Job ID: {response.batch_job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 4: Fallback Address for Failed Captures
        print("\n=== Address Capture - With Fallback ===")
        try:
            request = c2m_api.SplitPdfWithCaptureParamsRequest(
                document_url="https://docs.acme.com/mixed_quality_scans.pdf",
                extraction_spec={
                    "startPage": 1,
                    "endPage": 1,
                    "addressRegion": {
                        "x": 100.0,
                        "y": 150.0,
                        "width": 200.0,
                        "height": 100.0,
                        "pageOffset": 0
                    }
                },
                fallback_address={
                    "company": "Acme Corp - Mail Processing Center",
                    "address1": "PO Box 99999",
                    "city": "Chicago",
                    "state": "IL",
                    "zip": "60601"
                },
                capture_settings={
                    "ocrEnabled": True,
                    "enhanceImage": True,  # Pre-process for better OCR
                    "confidenceThreshold": 0.75,  # Lower threshold
                    "allowPartialAddress": True    # Accept incomplete addresses
                },
                job_options={
                    "mailclass": "standardMail"
                }
            )
            
            response = api.split_pdf_with_capture_params(request)
            print(f"Job ID: {response.job_id}")
            print(f"Failed captures sent to fallback: {response.fallback_count}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")

# =============================
# JOB OPTIONS COMBINATIONS
# =============================

def job_options_all_combinations():
    """Examples showing various job option combinations"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Example 1: Business Letter - Color, Duplex, Windowed
        print("\n=== Job Options - Business Letter (Premium) ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/proposals/client_proposal.pdf",
                job_options={
                    "documentClass": "businessLetter",
                    "layout": "portrait",
                    "mailclass": "firstClassMail",
                    "paperType": "letter",
                    "printOption": "color",
                    "envelope": "windowedFlat",
                    "duplex": True,
                    "addressPlacement": "topLeft",
                    "returnAddressPlacement": "topLeft"
                },
                recipient_address_id=12345
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 2: Personal Letter - Grayscale, Single-sided
        print("\n=== Job Options - Personal Letter (Economy) ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/personal/thank_you_note.pdf",
                job_options={
                    "documentClass": "personalLetter",
                    "layout": "portrait",
                    "mailclass": "standardMail",
                    "paperType": "letter",
                    "printOption": "grayscale",
                    "envelope": "flat",
                    "duplex": False
                },
                recipient_address_id=12345
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 3: Legal Document - Landscape, Legal Paper
        print("\n=== Job Options - Legal Document ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/legal/contract_addendum.pdf",
                job_options={
                    "documentClass": "businessLetter",
                    "layout": "landscape",
                    "mailclass": "certifiedMail",
                    "paperType": "legal",
                    "printOption": "grayscale",
                    "envelope": "legal",
                    "duplex": True,
                    "binding": "top",  # For landscape
                    "returnReceipt": True,
                    "restrictedDelivery": True
                },
                recipient_address_id=12345
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 4: Postcard
        print("\n=== Job Options - Postcard ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/marketing/summer_sale_postcard.pdf",
                job_options={
                    "documentClass": "postcard",
                    "layout": "landscape",
                    "mailclass": "marketingMail",
                    "paperType": "postcard",
                    "printOption": "color",
                    "envelope": "postcard",  # No envelope for postcards
                    "duplex": True,  # Front and back
                    "size": "6x9"    # Postcard size
                },
                address_list_id=98765
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 5: Priority Mail - Large Envelope
        print("\n=== Job Options - Priority Mail ===")
        try:
            request = c2m_api.SingleDocJobParamsRequest(
                document_url="https://docs.acme.com/catalogs/product_catalog_2024.pdf",
                job_options={
                    "documentClass": "businessLetter",
                    "layout": "portrait",
                    "mailclass": "priorityMail",
                    "paperType": "letter",
                    "printOption": "color",
                    "envelope": "largeFlat",  # Flat rate envelope
                    "duplex": True,
                    "tracking": True,
                    "insurance": 500.00,  # $500 insurance
                    "deliveryConfirmation": True
                },
                recipient_address_id=12345
            )
            
            response = api.single_doc_job_params(request)
            print(f"Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")

# =============================
# MULTI-DOC COMBINATIONS
# =============================

def multi_doc_all_combinations():
    """Multi-document submissions with various parameter combinations"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Example 1: Mixed Document Sources
        print("\n=== Multi-Doc - Mixed Document Sources ===")
        try:
            request = c2m_api.SubmitMultiDocParamsRequest(
                documents=[
                    {
                        "document_url": "https://docs.acme.com/notice1.pdf",
                        "recipient_address": {
                            "firstName": "Alice",
                            "lastName": "Anderson",
                            "address1": "111 First Ave",
                            "city": "Seattle",
                            "state": "WA",
                            "zip": "98101"
                        }
                    },
                    {
                        "document_id": 12345,  # Previously uploaded
                        "recipient_address_id": 67890  # Saved address
                    },
                    {
                        "document_source": {
                            "uploadRequestId": 456,
                            "documentName": "notice3.pdf"
                        },
                        "address_list_id": 98765  # Address list
                    }
                ],
                job_options={
                    "mailclass": "firstClassMail",
                    "batchName": "Mixed Source Test Batch"
                },
                payment_details={
                    "invoiceDetails": {
                        "invoiceNumber": "BATCH-2024-001",
                        "amountDue": 500.00
                    }
                }
            )
            
            response = api.submit_multi_doc_params(request)
            print(f"Batch Job ID: {response.batch_job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 2: Template-Based Multi-Doc with Personalization
        print("\n=== Multi-Doc Template - Personalized Marketing ===")
        try:
            request = c2m_api.SubmitMultiDocWithTemplateParamsRequest(
                template_id="acme_corp_customer_loyalty_program_2024",
                documents=[
                    {
                        "recipient_data": {
                            "firstName": "David",
                            "lastName": "Chen",
                            "company": "Chen Enterprises",
                            "address1": "888 Business Park Dr",
                            "city": "San Diego",
                            "state": "CA",
                            "zip": "92101",
                            "customerId": "CUST-2019-0045",
                            "tierLevel": "Platinum"
                        },
                        "template_variables": {
                            "greeting": "Dear David",
                            "yearsAsCustomer": 5,
                            "totalPurchases": "$125,450",
                            "rewardPoints": 125450,
                            "tierStatus": "Platinum Elite",
                            "exclusiveOffers": [
                                "25% off all orders in February",
                                "Free shipping for life",
                                "Early access to new products"
                            ],
                            "personalizedMessage": "Thank you for 5 amazing years!"
                        }
                    },
                    {
                        "recipient_data": {
                            "firstName": "Maria",
                            "lastName": "Rodriguez",
                            "address1": "456 Oak Street",
                            "city": "Phoenix",
                            "state": "AZ",
                            "zip": "85001",
                            "customerId": "CUST-2022-0892",
                            "tierLevel": "Silver"
                        },
                        "template_variables": {
                            "greeting": "Dear Maria",
                            "yearsAsCustomer": 2,
                            "totalPurchases": "$15,230",
                            "rewardPoints": 15230,
                            "tierStatus": "Silver Member",
                            "exclusiveOffers": [
                                "15% off your next order",
                                "Free shipping on orders over $50"
                            ],
                            "personalizedMessage": "You're only $4,770 away from Gold status!"
                        }
                    }
                ],
                job_options={
                    "mailclass": "marketingMail",
                    "color": True,
                    "paperType": "glossy",
                    "envelope": "customPrinted",
                    "sortByZip": True,
                    "dropDate": "2024-02-01"
                },
                payment_details={
                    "creditAmount": {
                        "amount": 250.00,
                        "currency": "USD"
                    }
                }
            )
            
            response = api.submit_multi_doc_with_template_params(request)
            print(f"Template Batch ID: {response.batch_job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")

# =============================
# PDF OPERATIONS COMBINATIONS
# =============================

def pdf_operations_all_combinations():
    """PDF merge and split operations with all parameter combinations"""
    
    with c2m_api.ApiClient(configuration) as api_client:
        api = c2m_api.DefaultApi(api_client)
        
        # Example 1: Complex Merge with Page Selection
        print("\n=== PDF Merge - Complex with Page Selection ===")
        try:
            request = c2m_api.MergeMultiDocParamsRequest(
                documents=[
                    {
                        "document_url": "https://docs.acme.com/reports/cover.pdf",
                        "pageRange": {
                            "startPage": 1,
                            "endPage": 1  # Just the cover page
                        }
                    },
                    {
                        "document_id": 12345,  # Table of contents
                        "pageRange": {
                            "startPage": 1,
                            "endPage": 2
                        }
                    },
                    {
                        "document_source": {
                            "uploadRequestId": 789,
                            "zipId": 456,
                            "documentName": "reports/main_report.pdf"
                        },
                        "pageRange": {
                            "startPage": 1,
                            "endPage": 50  # Main content
                        }
                    },
                    {
                        "document_url": "https://docs.acme.com/reports/appendix_a.pdf"
                        # No page range - include all pages
                    },
                    {
                        "document_source": {
                            "zipId": 456,
                            "documentName": "reports/references.pdf"
                        },
                        "pageRange": {
                            "startPage": 1,
                            "endPage": 10
                        }
                    }
                ],
                merge_options={
                    "addPageNumbers": True,
                    "startingPageNumber": 1,
                    "pageNumberPosition": "bottomCenter",
                    "pageNumberFormat": "Page {page} of {total}",
                    "addTableOfContents": True,
                    "tocTitle": "Contents",
                    "bookmarkSections": True,
                    "compressOutput": True,
                    "outputFilename": "ACME_Annual_Report_2024_Final.pdf"
                },
                job_options={
                    "mailclass": "priorityMail",
                    "color": True,
                    "duplex": True,
                    "binding": "left",
                    "coverStock": "premium"
                },
                recipient_address={
                    "company": "Board of Directors",
                    "address1": "100 Executive Plaza",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10004"
                }
            )
            
            response = api.merge_multi_doc_params(request)
            print(f"Merge Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 2: Template-Based Merge with Dynamic Content
        print("\n=== PDF Merge Template - Contract Package ===")
        try:
            request = c2m_api.MergeMultiDocWithTemplateParamsRequest(
                template_id="smithjones_law_complete_contract_package_v5",
                documents=[
                    {
                        "document_url": "https://contracts.smithjones.com/base/master_agreement.pdf",
                        "documentType": "master_agreement",
                        "documentOrder": 1
                    },
                    {
                        "document_id": 98765,  # Statement of work
                        "documentType": "statement_of_work",
                        "documentOrder": 2
                    },
                    {
                        "document_source": {
                            "uploadRequestId": 111,
                            "documentName": "schedules/schedule_a_pricing.pdf"
                        },
                        "documentType": "schedule_a",
                        "documentOrder": 3
                    },
                    {
                        "document_url": "https://contracts.smithjones.com/terms/general_terms_2024.pdf",
                        "documentType": "terms_conditions",
                        "documentOrder": 4
                    }
                ],
                template_variables={
                    "contractNumber": "SJ-2024-CTR-10234",
                    "effectiveDate": "February 1, 2024",
                    "clientName": "MegaCorp Industries",
                    "clientEntity": "MegaCorp Industries, a Delaware Corporation",
                    "projectName": "Digital Transformation Initiative",
                    "totalValue": "$2,500,000",
                    "paymentTerms": "Net 30 from invoice date",
                    "milestones": [
                        {
                            "phase": "Phase 1: Assessment",
                            "deliverables": "Current State Analysis",
                            "amount": "$500,000",
                            "dueDate": "March 31, 2024"
                        },
                        {
                            "phase": "Phase 2: Design",
                            "deliverables": "Solution Architecture",
                            "amount": "$750,000",
                            "dueDate": "June 30, 2024"
                        }
                    ]
                },
                merge_options={
                    "insertCoverPage": True,
                    "insertTableOfContents": True,
                    "numberAllPages": True,
                    "addWatermark": "CONFIDENTIAL",
                    "securitySettings": {
                        "preventCopy": True,
                        "preventPrint": False,
                        "requirePassword": False
                    }
                },
                job_options={
                    "mailclass": "certifiedMail",
                    "returnReceipt": True,
                    "restrictedDelivery": True,
                    "binding": "left",
                    "tabs": ["Sign Here", "Initial Here"]
                },
                recipient_address={
                    "company": "MegaCorp Industries",
                    "attn": "Legal Department",
                    "address1": "5000 Corporate Blvd",
                    "address2": "Legal Suite 2000",
                    "city": "Chicago",
                    "state": "IL",
                    "zip": "60601"
                }
            )
            
            response = api.merge_multi_doc_with_template_params(request)
            print(f"Contract Package Job ID: {response.job_id}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 3: Advanced Split with Multiple Criteria
        print("\n=== PDF Split - Advanced Multi-Criteria ===")
        try:
            request = c2m_api.SplitPdfParamsRequest(
                document_url": "https://docs.acme.com/bulk/combined_statements_2024_01.pdf",
                split_rules=[
                    {
                        "splitType": "pageRange",
                        "pageRange": {
                            "startPage": 1,
                            "endPage": 5
                        },
                        "recipient_address": {
                            "firstName": "Account",
                            "lastName": "Holder-001",
                            "address1": "123 Main St",
                            "city": "Boston",
                            "state": "MA",
                            "zip": "02101"
                        }
                    },
                    {
                        "splitType": "pageRange",
                        "pageRange": {
                            "startPage": 6,
                            "endPage": 10
                        },
                        "recipient_address_id": 12345
                    },
                    {
                        "splitType": "pageRange",
                        "pageRange": {
                            "startPage": 11,
                            "endPage": 15
                        },
                        "saved_address_id": 67890
                    },
                    {
                        "splitType": "keyword",
                        "keyword": "ACCOUNT NUMBER: 789012",
                        "includeKeywordPage": True,
                        "pagesAfterKeyword": 4,
                        "recipient_address": {
                            "company": "Smith Holdings LLC",
                            "address1": "789 Corporate Way",
                            "city": "Dallas",
                            "state": "TX",
                            "zip": "75201"
                        }
                    }
                ],
                job_options={
                    "mailclass": "firstClassMail",
                    "duplex": True,
                    "envelope": "windowedFlat"
                },
                split_options={
                    "namingPattern": "Statement_{recipientName}_{date}",
                    "addPageNumbers": True,
                    "validatePageCounts": True
                }
            )
            
            response = api.split_pdf_params(request)
            print(f"Split Job ID: {response.job_id}")
            print(f"Documents created: {response.split_count}")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")
        
        # Example 4: Split with OCR Address Capture - Multiple Strategies
        print("\n=== PDF Split with Capture - Multiple Strategies ===")
        try:
            request = c2m_api.SplitPdfWithCaptureParamsRequest(
                document_url="https://docs.acme.com/scanned/mixed_quality_batch.pdf",
                capture_strategies=[
                    {
                        "strategy": "region",
                        "extraction_spec": {
                            "startPage": 1,
                            "endPage": 1,
                            "addressRegion": {
                                "x": 50.0,
                                "y": 100.0,
                                "width": 250.0,
                                "height": 120.0,
                                "pageOffset": 0
                            }
                        },
                        "priority": 1
                    },
                    {
                        "strategy": "keyword_proximity",
                        "keyword": "Bill To:",
                        "searchArea": {
                            "afterKeyword": True,
                            "maxDistance": 200.0
                        },
                        "priority": 2
                    },
                    {
                        "strategy": "pattern_match",
                        "patterns": [
                            r"^\d{3,5}\s+\w+\s+(Street|St|Avenue|Ave|Road|Rd)",
                            r"^[A-Z][a-z]+\s+[A-Z][a-z]+\s*\n"
                        ],
                        "priority": 3
                    }
                ],
                split_on={
                    "method": "multiCriteria",
                    "criteria": [
                        {
                            "type": "blankPage",
                            "threshold": 0.95  # 95% white space
                        },
                        {
                            "type": "keyword",
                            "keyword": "Page 1 of",
                            "position": "bottom"
                        },
                        {
                            "type": "barcode",
                            "barcodeType": "code128",
                            "position": "topRight"
                        }
                    ]
                },
                capture_settings={
                    "ocrEnabled": True,
                    "ocrEngine": "tesseract",
                    "ocrLanguages": ["eng", "spa"],  # English and Spanish
                    "preprocessImage": True,
                    "enhancementOptions": {
                        "deskew": True,
                        "removeNoise": True,
                        "increasContrast": True,
                        "resolution": 300
                    },
                    "validationLevel": "strict",
                    "addressStandardization": "usps",
                    "geocoding": True
                },
                fallback_options={
                    "fallbackAddress": {
                        "company": "ACME Mail Processing",
                        "address1": "PO Box 999999",
                        "city": "Chicago",
                        "state": "IL",
                        "zip": "60601"
                    },
                    "manualReviewQueue": True,
                    "notificationEmail": "mailroom@acme.com"
                },
                job_options={
                    "mailclass": "firstClassMail",
                    "trackingRequired": True
                }
            )
            
            response = api.split_pdf_with_capture_params(request)
            print(f"Capture Split Job ID: {response.job_id}")
            print(f"Success rate: {response.capture_success_rate}%")
            
        except ApiException as e:
            print(f"Error: {e.status} - {e.body}")

# =============================
# MAIN EXECUTION
# =============================

if __name__ == "__main__":
    print("C2M API Python SDK - Comprehensive Parameter Combination Examples")
    print("=" * 65)
    print("\nThis file demonstrates every possible parameter combination.")
    print("Each example shows different ways to specify the same type of data.")
    print("\nNOTE: Template names use realistic corporate naming conventions")
    print("like 'acme_corp_invoice_template_v3' instead of generic names.")
    print("\n" + "=" * 65)
    
    # Uncomment the examples you want to run:
    
    # auth_comprehensive_examples()
    # single_doc_all_variations()
    # recipient_address_all_variations()
    # payment_details_all_variations()
    # template_examples_realistic()
    # address_capture_all_variations()
    # job_options_all_combinations()
    # multi_doc_all_combinations()
    # pdf_operations_all_combinations()
    
    print("\n" + "=" * 65)
    print("Examples demonstrate:")
    print("- All 5 DocumentSourceIdentifier variations")
    print("- All 3 RecipientAddressSource variations")
    print("- All 8 PaymentDetails variations")
    print("- Multiple ExtractionSpec configurations")
    print("- Realistic template naming conventions")
    print("- Complex PDF operations with all options")
    print("\nRemember to replace placeholder values with real data!")
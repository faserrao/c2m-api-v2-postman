# C2M API V2 - Real World Use Cases Report
Generated: 2025-09-30 09:29:03
================================================================================

## Legal Firm
**Description:** We have letters that we need to send all day. Each letter is sent to a specific recipient via Certified Mail. A copy is sent to their legal representative via First Class mail. Our system generates the PDF of the letter.

### Request: [single-doc-job-template]
- **Method:** POST
- **Endpoint:** `{{baseUrl}}/jobs/single-doc-job-template`
- **Number of examples:** 5

#### Example 1: legal_firm - Document ID + Credit Card + New Address
```json
{
  "documentSourceIdentifier": {
    "documentId": 1234
  },
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
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "legal_certified_mail",
  "paymentDetails": {
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
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

#### Example 2: legal_firm - External URL + Invoice + Address List ID
```json
{
  "documentSourceIdentifier": {
    "externalUrl": "https://api.example.com/v1/documents/5678"
  },
  "recipientAddressSources": [
    {
      "addressListId": 42
    },
    {
      "firstName": "Jane",
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "legal_certified_mail",
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "LEGAL_FIRM-2024-001",
      "amountDue": 150.0
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

#### Example 3: legal_firm - Upload Request + ACH + Address ID
```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 100,
    "documentName": "legal_firm_document.pdf"
  },
  "recipientAddressSources": [
    {
      "addressId": 12345
    },
    {
      "firstName": "Jane",
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "legal_certified_mail",
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

#### Example 4: legal_firm - Upload + Zip + User Credit + New Address
```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "legal_firm_doc.pdf"
  },
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
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "legal_certified_mail",
  "paymentDetails": {
    "userCreditDetails": {
      "creditAmount": 50.0
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

#### Example 5: legal_firm - Zip Only + Apple Pay + Address List ID
```json
{
  "documentSourceIdentifier": {
    "zipId": 20,
    "documentName": "legal_firm_file.pdf"
  },
  "recipientAddressSources": [
    {
      "addressListId": 42
    },
    {
      "firstName": "Jane",
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "legal_certified_mail",
  "paymentDetails": {
    "applePayDetails": {
      "applePaymentDetails": {}
    }
  },
  "tags": [
    "legal",
    "certified",
    "client-correspondence"
  ]
}
```

--------------------------------------------------------------------------------

## Company #1
**Description:** We send invoices at the end of the month. Each invoice is in its own PDF. The address of the recipient is in the invoice.

### Request: [multi-pdf-address-capture]
- **Method:** POST
- **Endpoint:** `{{baseUrl}}/jobs/multi-pdf-address-capture`
- **Number of examples:** 5

#### Example 1: company_invoice_batch - Document ID + Credit Card
```json
{
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
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

#### Example 2: company_invoice_batch - External URL + Invoice
```json
{
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
      "invoiceNumber": "COMPANY_INVOICE_BATCH-2024-001",
      "amountDue": 150.0
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

#### Example 3: company_invoice_batch - Upload Request + ACH
```json
{
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
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

#### Example 4: company_invoice_batch - Upload + Zip + User Credit
```json
{
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
    "userCreditDetails": {
      "creditAmount": 50.0
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

#### Example 5: company_invoice_batch - Zip Only + Apple Pay
```json
{
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
    "applePayDetails": {
      "applePaymentDetails": {}
    }
  },
  "tags": [
    "invoices",
    "monthly-batch",
    "accounts-receivable"
  ]
}
```

--------------------------------------------------------------------------------

## Company #2
**Description:** We send invoices at the end of the month. All the invoices are in a single big PDF. The addresses of the recipients are in the invoices.

### Request: [single-pdf-split-addressCapture]
- **Method:** POST
- **Endpoint:** `{{baseUrl}}/jobs/single-pdf-split-addressCapture`
- **Number of examples:** 5

#### Example 1: company_split_invoices - Document ID + Credit Card
```json
{
  "documentSourceIdentifier": {
    "documentId": 1234
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
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

#### Example 2: company_split_invoices - External URL + Invoice
```json
{
  "documentSourceIdentifier": {
    "externalUrl": "https://api.example.com/v1/documents/5678"
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
    "invoiceDetails": {
      "invoiceNumber": "COMPANY_SPLIT_INVOICES-2024-001",
      "amountDue": 150.0
    }
  },
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

#### Example 3: company_split_invoices - Upload Request + ACH
```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 100,
    "documentName": "company_split_invoices_document.pdf"
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
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

#### Example 4: company_split_invoices - Upload + Zip + User Credit
```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "company_split_invoices_doc.pdf"
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
    "userCreditDetails": {
      "creditAmount": 50.0
    }
  },
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

#### Example 5: company_split_invoices - Zip Only + Apple Pay
```json
{
  "documentSourceIdentifier": {
    "zipId": 20,
    "documentName": "company_split_invoices_file.pdf"
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
    "applePayDetails": {
      "applePaymentDetails": {}
    }
  },
  "tags": [
    "split-pdf",
    "address-capture",
    "automated"
  ]
}
```

--------------------------------------------------------------------------------

## Real Estate Agent
**Description:** We send postcards as part of our campaign. The postcards have a specific template and use mail merge.

### Request: [single-doc-job-template]
- **Method:** POST
- **Endpoint:** `{{baseUrl}}/jobs/single-doc-job-template`
- **Number of examples:** 5

#### Example 1: real_estate_agent - Document ID + Credit Card + New Address
```json
{
  "documentSourceIdentifier": {
    "documentId": 1234
  },
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
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "postcard_luxury_homes",
  "paymentDetails": {
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
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

#### Example 2: real_estate_agent - External URL + Invoice + Address List ID
```json
{
  "documentSourceIdentifier": {
    "externalUrl": "https://api.example.com/v1/documents/5678"
  },
  "recipientAddressSources": [
    {
      "addressListId": 42
    },
    {
      "firstName": "Jane",
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "postcard_luxury_homes",
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "REAL_ESTATE_AGENT-2024-001",
      "amountDue": 150.0
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

#### Example 3: real_estate_agent - Upload Request + ACH + Address ID
```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 100,
    "documentName": "real_estate_agent_document.pdf"
  },
  "recipientAddressSources": [
    {
      "addressId": 12345
    },
    {
      "firstName": "Jane",
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "postcard_luxury_homes",
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

#### Example 4: real_estate_agent - Upload + Zip + User Credit + New Address
```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "real_estate_agent_doc.pdf"
  },
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
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "postcard_luxury_homes",
  "paymentDetails": {
    "userCreditDetails": {
      "creditAmount": 50.0
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

#### Example 5: real_estate_agent - Zip Only + Apple Pay + Address List ID
```json
{
  "documentSourceIdentifier": {
    "zipId": 20,
    "documentName": "real_estate_agent_file.pdf"
  },
  "recipientAddressSources": [
    {
      "addressListId": 42
    },
    {
      "firstName": "Jane",
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "postcard_luxury_homes",
  "paymentDetails": {
    "applePayDetails": {
      "applePaymentDetails": {}
    }
  },
  "tags": [
    "marketing",
    "postcards",
    "real-estate",
    "bulk-mail"
  ]
}
```

--------------------------------------------------------------------------------

## Medical Agency
**Description:** We send medical reports to patients. Each report is a custom PDF. In addition, a few boiler-plate pages of generic medical information are sent with each report.

### Request: [multi-doc-merge-job-template]
- **Method:** POST
- **Endpoint:** `{{baseUrl}}/jobs/multi-doc-merge-job-template`
- **Number of examples:** 5

#### Example 1: medical_agency - Document ID + Credit Card + New Address
```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "documentId": 1234
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "firstName": "John",
    "lastName": "Doe",
    "address1": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "country": "USA"
  },
  "paymentDetails": {
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
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

#### Example 2: medical_agency - External URL + Invoice + Address List ID
```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "externalUrl": "https://api.example.com/v1/documents/5678"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "addressListId": 42
  },
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "MEDICAL_AGENCY-2024-001",
      "amountDue": 150.0
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

#### Example 3: medical_agency - Upload Request + ACH + Address ID
```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "uploadRequestId": 100,
      "documentName": "medical_agency_document.pdf"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "addressId": 12345
  },
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

#### Example 4: medical_agency - Upload + Zip + User Credit + New Address
```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "uploadRequestId": 200,
      "zipId": 10,
      "documentName": "medical_agency_doc.pdf"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "firstName": "John",
    "lastName": "Doe",
    "address1": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "country": "USA"
  },
  "paymentDetails": {
    "userCreditDetails": {
      "creditAmount": 50.0
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

#### Example 5: medical_agency - Zip Only + Apple Pay + Address List ID
```json
{
  "documentsToMerge": [
    {
      "documentId": 1001
    },
    {
      "zipId": 20,
      "documentName": "medical_agency_file.pdf"
    },
    {
      "documentId": 1002
    }
  ],
  "recipientAddressSource": {
    "addressListId": 42
  },
  "paymentDetails": {
    "applePayDetails": {
      "applePaymentDetails": {}
    }
  },
  "tags": [
    "medical",
    "compliance",
    "patient-reports"
  ]
}
```

--------------------------------------------------------------------------------

## Monthly Newsletters
**Description:** We are an organization that sends out flyers at the beginning of each month to our subscribers. The flyer is a static document and we have a mailing list it has to go out to.

### Request: [single-doc-job-template]
- **Method:** POST
- **Endpoint:** `{{baseUrl}}/jobs/single-doc-job-template`
- **Number of examples:** 5

#### Example 1: monthly_newsletters - Document ID + Credit Card + New Address
```json
{
  "documentSourceIdentifier": {
    "documentId": 1234
  },
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
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "monthly_newsletter_standard",
  "paymentDetails": {
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
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

#### Example 2: monthly_newsletters - External URL + Invoice + Address List ID
```json
{
  "documentSourceIdentifier": {
    "externalUrl": "https://api.example.com/v1/documents/5678"
  },
  "recipientAddressSources": [
    {
      "addressListId": 42
    },
    {
      "firstName": "Jane",
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "monthly_newsletter_standard",
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "MONTHLY_NEWSLETTERS-2024-001",
      "amountDue": 150.0
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

#### Example 3: monthly_newsletters - Upload Request + ACH + Address ID
```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 100,
    "documentName": "monthly_newsletters_document.pdf"
  },
  "recipientAddressSources": [
    {
      "addressId": 12345
    },
    {
      "firstName": "Jane",
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "monthly_newsletter_standard",
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

#### Example 4: monthly_newsletters - Upload + Zip + User Credit + New Address
```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "monthly_newsletters_doc.pdf"
  },
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
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "monthly_newsletter_standard",
  "paymentDetails": {
    "userCreditDetails": {
      "creditAmount": 50.0
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

#### Example 5: monthly_newsletters - Zip Only + Apple Pay + Address List ID
```json
{
  "documentSourceIdentifier": {
    "zipId": 20,
    "documentName": "monthly_newsletters_file.pdf"
  },
  "recipientAddressSources": [
    {
      "addressListId": 42
    },
    {
      "firstName": "Jane",
      "lastName": "Smith",
      "address1": "456 Oak Avenue",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  ],
  "jobTemplate": "monthly_newsletter_standard",
  "paymentDetails": {
    "applePayDetails": {
      "applePaymentDetails": {}
    }
  },
  "tags": [
    "newsletter",
    "monthly",
    "subscribers",
    "marketing"
  ]
}
```

--------------------------------------------------------------------------------

## Reseller #1
**Description:** We receive PDFs from our customers. Each PDF is unique. We want to batch the PDFs into a single big PDF and send them in one go.

### Request: [single-pdf-split]
- **Method:** POST
- **Endpoint:** `{{baseUrl}}/jobs/single-pdf-split`
- **Number of examples:** 5

#### Example 1: reseller_merge_pdfs - Document ID + Credit Card
```json
{
  "documentSourceIdentifier": {
    "documentId": 1234
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        {
          "addressListId": 301
        }
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        {
          "addressListId": 302
        }
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        {
          "addressListId": 303
        }
      ]
    }
  ],
  "paymentDetails": {
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
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

#### Example 2: reseller_merge_pdfs - External URL + Invoice
```json
{
  "documentSourceIdentifier": {
    "externalUrl": "https://api.example.com/v1/documents/5678"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        {
          "addressListId": 301
        }
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        {
          "addressListId": 302
        }
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        {
          "addressListId": 303
        }
      ]
    }
  ],
  "paymentDetails": {
    "invoiceDetails": {
      "invoiceNumber": "RESELLER_MERGE_PDFS-2024-001",
      "amountDue": 150.0
    }
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

#### Example 3: reseller_merge_pdfs - Upload Request + ACH
```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 100,
    "documentName": "reseller_merge_pdfs_document.pdf"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        {
          "addressListId": 301
        }
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        {
          "addressListId": 302
        }
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        {
          "addressListId": 303
        }
      ]
    }
  ],
  "paymentDetails": {
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

#### Example 4: reseller_merge_pdfs - Upload + Zip + User Credit
```json
{
  "documentSourceIdentifier": {
    "uploadRequestId": 200,
    "zipId": 10,
    "documentName": "reseller_merge_pdfs_doc.pdf"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        {
          "addressListId": 301
        }
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        {
          "addressListId": 302
        }
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        {
          "addressListId": 303
        }
      ]
    }
  ],
  "paymentDetails": {
    "userCreditDetails": {
      "creditAmount": 50.0
    }
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

#### Example 5: reseller_merge_pdfs - Zip Only + Apple Pay
```json
{
  "documentSourceIdentifier": {
    "zipId": 20,
    "documentName": "reseller_merge_pdfs_file.pdf"
  },
  "items": [
    {
      "pageRange": {
        "startPage": 1,
        "endPage": 5
      },
      "recipientAddressSources": [
        {
          "addressListId": 301
        }
      ]
    },
    {
      "pageRange": {
        "startPage": 6,
        "endPage": 10
      },
      "recipientAddressSources": [
        {
          "addressListId": 302
        }
      ]
    },
    {
      "pageRange": {
        "startPage": 11,
        "endPage": 15
      },
      "recipientAddressSources": [
        {
          "addressListId": 303
        }
      ]
    }
  ],
  "paymentDetails": {
    "applePayDetails": {
      "applePaymentDetails": {}
    }
  },
  "tags": [
    "reseller",
    "pdf-merge",
    "b2b"
  ]
}
```

--------------------------------------------------------------------------------

## Reseller #2
**Description:** We receive PDFs from our customers. Each PDF is unique. We want to zip the PDFs and send them in one go.

### Request: [multi-doc]
- **Method:** POST
- **Endpoint:** `{{baseUrl}}/jobs/multi-doc`
- **Number of examples:** 5

#### Example 1: reseller_zip_pdfs - Document ID + Credit Card
```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "documentId": 1234
      },
      "recipientAddressSource": {
        "addressId": 6001
      }
    },
    {
      "documentSourceIdentifier": {
        "documentId": 1234
      },
      "recipientAddressSource": {
        "addressId": 6002
      }
    },
    {
      "documentSourceIdentifier": {
        "documentId": 1234
      },
      "recipientAddressSource": {
        "addressId": 6003
      }
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
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

#### Example 2: reseller_zip_pdfs - External URL + Invoice
```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "externalUrl": "https://api.example.com/v1/documents/5678"
      },
      "recipientAddressSource": {
        "addressId": 6001
      }
    },
    {
      "documentSourceIdentifier": {
        "externalUrl": "https://api.example.com/v1/documents/5678"
      },
      "recipientAddressSource": {
        "addressId": 6002
      }
    },
    {
      "documentSourceIdentifier": {
        "externalUrl": "https://api.example.com/v1/documents/5678"
      },
      "recipientAddressSource": {
        "addressId": 6003
      }
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
    "invoiceDetails": {
      "invoiceNumber": "RESELLER_ZIP_PDFS-2024-001",
      "amountDue": 150.0
    }
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

#### Example 3: reseller_zip_pdfs - Upload Request + ACH
```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "reseller_zip_pdfs_document.pdf"
      },
      "recipientAddressSource": {
        "addressId": 6001
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "reseller_zip_pdfs_document.pdf"
      },
      "recipientAddressSource": {
        "addressId": 6002
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 100,
        "documentName": "reseller_zip_pdfs_document.pdf"
      },
      "recipientAddressSource": {
        "addressId": 6003
      }
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
    "achDetails": {
      "routingNumber": "021000021",
      "accountNumber": "1234567890",
      "checkDigit": 7
    }
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

#### Example 4: reseller_zip_pdfs - Upload + Zip + User Credit
```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 200,
        "zipId": 10,
        "documentName": "reseller_zip_pdfs_doc.pdf"
      },
      "recipientAddressSource": {
        "addressId": 6001
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 200,
        "zipId": 10,
        "documentName": "reseller_zip_pdfs_doc.pdf"
      },
      "recipientAddressSource": {
        "addressId": 6002
      }
    },
    {
      "documentSourceIdentifier": {
        "uploadRequestId": 200,
        "zipId": 10,
        "documentName": "reseller_zip_pdfs_doc.pdf"
      },
      "recipientAddressSource": {
        "addressId": 6003
      }
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
    "userCreditDetails": {
      "creditAmount": 50.0
    }
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

#### Example 5: reseller_zip_pdfs - Zip Only + Apple Pay
```json
{
  "items": [
    {
      "documentSourceIdentifier": {
        "zipId": 20,
        "documentName": "reseller_zip_pdfs_file.pdf"
      },
      "recipientAddressSource": {
        "addressId": 6001
      }
    },
    {
      "documentSourceIdentifier": {
        "zipId": 20,
        "documentName": "reseller_zip_pdfs_file.pdf"
      },
      "recipientAddressSource": {
        "addressId": 6002
      }
    },
    {
      "documentSourceIdentifier": {
        "zipId": 20,
        "documentName": "reseller_zip_pdfs_file.pdf"
      },
      "recipientAddressSource": {
        "addressId": 6003
      }
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
    "applePayDetails": {
      "applePaymentDetails": {}
    }
  },
  "tags": [
    "reseller",
    "zip-processing",
    "batch",
    "b2b"
  ]
}
```

--------------------------------------------------------------------------------


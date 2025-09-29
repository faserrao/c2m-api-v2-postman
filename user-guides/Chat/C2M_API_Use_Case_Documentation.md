# C2M API – Real World Scenarios Documentation

This document provides detailed descriptions of **8 real-world use cases** for the C2M API.  
It is designed so you can copy/paste into Postman’s **Collection**, **Folder**, and **Request** description fields.  
Each use case includes:
- Business context
- Request description
- Example request and response

---

## 📂 Collection Description
```markdown
# C2M API – Real World Scenarios

This collection demonstrates **real-world use cases** for the C2M API.  
Each folder represents a business scenario (Legal Firm, Invoicing, Resellers, etc).  

You can run these against:
- A **Postman mock server** (default: `{{mockUrl}}`).
- Or your **live API endpoint** (set `{{baseUrl}}`).

Each folder follows this flow:
1. **Submit Job** → creates a new job (`jobId` returned).
2. **Get Job Details** → fetch job metadata.
3. **Get Job Status** → check progress (`queued`, `processing`, `complete`).
```

---

## 1. Legal Firm – Certified Letters
**Folder Description:**
```markdown
## Use Case: Legal Firm – Certified Letters

A legal firm needs to send letters to clients **all day long**.  
For each letter:
- The **primary recipient** receives it via **Certified Mail**.
- A **copy is sent to their legal representative** via **First Class Mail**.
- The system generates a PDF of the letter.
```

**Request Description:**
```markdown
### Submit Certified Legal Letter
Simulates a legal firm sending a client letter + copy to lawyer.

**Variables:**
- `{{baseUrl}}` → API endpoint or mock server.

**Expected:**
- `201 Created`
- Response contains new `jobId`.
```

**Example Request:**
```json
{
  "documentUrl": "https://example.com/letters/client-123.pdf",
  "recipientAddress": {
    "name": "John Doe",
    "address1": "123 Main St",
    "city": "Fairfax",
    "state": "VA",
    "zip": "22030"
  },
  "copyTo": {
    "name": "Jane Smith, Esq.",
    "address1": "456 Law Office Rd",
    "city": "Alexandria",
    "state": "VA",
    "zip": "22314"
  },
  "mailClass": "Certified"
}
```

**Example Response:**
```json
{ "jobId": "job-001", "status": "queued" }
```

---

## 2. Company #1 – Invoice Batch
**Folder Description:**
```markdown
## Use Case: Company #1 – Invoice Batch

This company sends **monthly invoices**.  
Each invoice is its own PDF, and addresses are embedded inside each PDF.  
Invoices are uploaded together in a batch for processing.
```

**Request Description:**
```markdown
### Submit Invoice Batch
Uploads multiple invoice PDFs for batch mailing.  
Enables address capture from PDF contents.

Expected output: `201 Created` with `jobId`.
```

**Example Request:**
```json
{
  "documents": [
    { "documentUrl": "https://example.com/invoices/001.pdf" },
    { "documentUrl": "https://example.com/invoices/002.pdf" }
  ],
  "addressCapture": true
}
```

**Example Response:**
```json
{ "jobId": "job-002", "status": "queued" }
```

---

## 3. Company #2 – Split Invoices
**Folder Description:**
```markdown
## Use Case: Company #2 – Split Invoices

This company produces **one big PDF** containing all invoices.  
The system must **split** the PDF by detecting recipient addresses inside.
```

**Request Description:**
```markdown
### Submit Split Invoice Job
Uploads a single bulk PDF.  
API automatically splits it into multiple jobs using address capture.
```

**Example Request:**
```json
{
  "documentUrl": "https://example.com/invoices/batch-sept.pdf",
  "splitByAddress": true
}
```

**Example Response:**
```json
{ "jobId": "job-003", "status": "queued" }
```

---

## 4. Real Estate Agent – Postcards
**Folder Description:**
```markdown
## Use Case: Real Estate Agent – Postcards

A real estate agent runs **marketing campaigns** with postcards.  
The campaign uses a **postcard template** and **mail merge** to personalize recipient names.
```

**Request Description:**
```markdown
### Submit Postcard Campaign
Sends a postcard template merged with a list of recipient names.
```

**Example Request:**
```json
{
  "documentUrl": "https://example.com/postcards/template.pdf",
  "mailMerge": {
    "field": "name",
    "values": ["Alice", "Bob", "Charlie"]
  }
}
```

**Example Response:**
```json
{ "jobId": "job-004", "status": "queued" }
```

---

## 5. Medical Agency – Reports + Boilerplate
**Folder Description:**
```markdown
## Use Case: Medical Agency – Reports with Boilerplate

A medical agency sends **individual reports** to patients.  
Each report is combined with a few pages of **standard medical information** (boilerplate).
```

**Request Description:**
```markdown
### Submit Medical Reports Batch
Uploads multiple custom patient PDFs and merges them with a boilerplate document.
```

**Example Request:**
```json
{
  "documents": [
    { "documentUrl": "https://example.com/reports/patient-001.pdf" },
    { "documentUrl": "https://example.com/reports/patient-002.pdf" },
    { "documentUrl": "https://example.com/docs/boilerplate.pdf" }
  ]
}
```

**Example Response:**
```json
{ "jobId": "job-005", "status": "queued" }
```

---

## 6. Monthly Newsletters
**Folder Description:**
```markdown
## Use Case: Monthly Newsletters

An organization sends **monthly flyers/newsletters** to all subscribers.  
The document is static, and a predefined **mailing list** is used.
```

**Request Description:**
```markdown
### Submit Newsletter Job
Uploads a static newsletter and applies a mailing list.
```

**Example Request:**
```json
{
  "documentUrl": "https://example.com/newsletters/october.pdf",
  "mailingListId": "subscribers-2025-10"
}
```

**Example Response:**
```json
{ "jobId": "job-006", "status": "queued" }
```

---

## 7. Reseller #1 – Merge PDFs
**Folder Description:**
```markdown
## Use Case: Reseller #1 – Merge PDFs

Reseller receives multiple **unique PDFs** from customers.  
All PDFs are batched into a **single big PDF** before submission.
```

**Request Description:**
```markdown
### Submit Merged PDF Job
Merges multiple PDFs into one document, then submits the job.
```

**Example Request:**
```json
{
  "documentUrl": "https://example.com/uploads/batch.pdf",
  "split": true
}
```

**Example Response:**
```json
{ "jobId": "job-007", "status": "queued" }
```

---

## 8. Reseller #2 – Zip PDFs
**Folder Description:**
```markdown
## Use Case: Reseller #2 – Zip PDFs

Reseller receives multiple **unique PDFs** from customers.  
Instead of merging, they are bundled into a **ZIP archive** for submission.
```

**Request Description:**
```markdown
### Submit Zipped Job
Uploads multiple PDFs and bundles them as a ZIP before processing.
```

**Example Request:**
```json
{
  "documents": [
    { "documentUrl": "https://example.com/uploads/file1.pdf" },
    { "documentUrl": "https://example.com/uploads/file2.pdf" }
  ],
  "bundleAs": "zip"
}
```

**Example Response:**
```json
{ "jobId": "job-008", "status": "queued" }
```

---

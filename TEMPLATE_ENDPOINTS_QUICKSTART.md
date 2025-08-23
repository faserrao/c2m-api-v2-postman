# 🚀 Template Endpoints Quick Start Guide

This guide helps you get started with the C2M API using our **recommended template endpoints**. These endpoints are designed to get you up and running in minutes!

## Why Template Endpoints?

| Feature | Template Endpoints | Custom Endpoints |
|---------|-------------------|------------------|
| **Setup Time** | 5 minutes | 30+ minutes |
| **Parameters** | 3 required | 10+ required |
| **Configuration** | Pre-optimized | Manual setup |
| **Error Rate** | Lower | Higher |
| **Support** | Priority | Standard |

## Available Templates

### 📮 standard-letter
- **Use for:** Regular business mail, statements, notices
- **Features:** First-class mail, black & white, #10 envelope
- **Delivery:** 3-5 business days

### 🎨 color-marketing
- **Use for:** Marketing materials, promotional mail
- **Features:** Full color, glossy paper, custom envelope
- **Delivery:** 5-7 business days

### 📨 certified-mail
- **Use for:** Legal documents, important notices
- **Features:** Tracking, signature required, return receipt
- **Delivery:** 3-5 business days

### ⚡ priority-express
- **Use for:** Urgent documents
- **Features:** Express mail, tracking, guaranteed delivery
- **Delivery:** 1-2 business days

## Quick Examples

### 1. Send a Single Document

```bash
curl -X POST https://api.c2m.com/v1/jobs/single-doc-job-template \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "documentSourceIdentifier": "https://yoursite.com/invoice.pdf",
    "jobTemplate": "standard-letter",
    "paymentDetails": {
      "paymentMethod": "purchase-order",
      "purchaseOrderNumber": "PO-2024-001"
    }
  }'
```

### 2. Send Multiple Documents

```bash
curl -X POST https://api.c2m.com/v1/jobs/multi-docs-job-template \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "documentSourceIdentifier": "https://yoursite.com/statement1.pdf",
        "recipientAddressSource": {
          "firstName": "John",
          "lastName": "Doe",
          "address1": "123 Main St",
          "city": "Anytown",
          "state": "CA",
          "zip": "90210"
        }
      },
      {
        "documentSourceIdentifier": "https://yoursite.com/statement2.pdf",
        "recipientAddressSource": {
          "firstName": "Jane",
          "lastName": "Smith",
          "address1": "456 Oak Ave",
          "city": "Somewhere",
          "state": "NY",
          "zip": "10001"
        }
      }
    ],
    "jobTemplate": "standard-letter",
    "paymentDetails": {
      "paymentMethod": "purchase-order",
      "purchaseOrderNumber": "PO-2024-002"
    }
  }'
```

### 3. Merge and Send Documents

```bash
curl -X POST https://api.c2m.com/v1/jobs/multi-doc-merge-job-template \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "documentsToMerge": [
      "https://yoursite.com/cover-letter.pdf",
      "https://yoursite.com/report.pdf",
      "https://yoursite.com/appendix.pdf"
    ],
    "recipientAddressSource": {
      "firstName": "Bob",
      "lastName": "Johnson",
      "address1": "789 Elm St",
      "city": "Metropolis",
      "state": "IL",
      "zip": "60601"
    },
    "jobTemplate": "standard-letter",
    "paymentDetails": {
      "paymentMethod": "purchase-order",
      "purchaseOrderNumber": "PO-2024-003"
    }
  }'
```

## Response Format

All template endpoints return a consistent response:

```json
{
  "jobId": "job_abc123",
  "status": "processing",
  "estimatedCompletionTime": "2024-01-15T14:30:00Z",
  "trackingUrl": "https://track.c2m.com/job_abc123"
}
```

## Best Practices

### ✅ DO:
- Start with `standard-letter` template for testing
- Use HTTPS URLs for document sources
- Validate addresses before submission
- Monitor job status via webhooks

### ❌ DON'T:
- Use custom endpoints unless absolutely necessary
- Submit documents larger than 25MB
- Include sensitive data in document URLs
- Retry failed requests immediately

## Migration from Custom Endpoints

If you're currently using custom endpoints, here's the mapping:

| Custom Endpoint | Template Endpoint | Template to Use |
|----------------|-------------------|-----------------|
| `/jobs/single-doc` | `/jobs/single-doc-job-template` | `standard-letter` |
| `/jobs/multi-doc` | `/jobs/multi-docs-job-template` | `standard-letter` |
| `/jobs/multi-doc-merge` | `/jobs/multi-doc-merge-job-template` | `standard-letter` |

## Common Use Cases

### Monthly Statements
```json
{
  "documentSourceIdentifier": "https://api.yourcompany.com/statements/2024-01.pdf",
  "jobTemplate": "standard-letter",
  "paymentDetails": {
    "paymentMethod": "purchase-order",
    "purchaseOrderNumber": "STMT-2024-01"
  }
}
```

### Marketing Campaign
```json
{
  "documentSourceIdentifier": "https://cdn.yourcompany.com/summer-sale.pdf",
  "jobTemplate": "color-marketing",
  "paymentDetails": {
    "paymentMethod": "purchase-order",
    "purchaseOrderNumber": "MKT-SUMMER-2024"
  }
}
```

### Legal Notice
```json
{
  "documentSourceIdentifier": "https://secure.lawfirm.com/notice-12345.pdf",
  "jobTemplate": "certified-mail",
  "paymentDetails": {
    "paymentMethod": "purchase-order",
    "purchaseOrderNumber": "LEGAL-2024-789"
  }
}
```

## Need Help?

- 📧 Email: support@c2m.com
- 📚 Full Documentation: https://docs.c2m.com
- 💬 Slack: c2m-api.slack.com

---

**Remember:** Template endpoints are the fastest, most reliable way to integrate with C2M API. Start here and only move to custom endpoints if you have specific requirements not covered by templates.
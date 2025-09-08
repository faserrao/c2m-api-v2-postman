# OpenapiClient::MultiPdfWithCaptureParams

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **address_capture_pdfs** | [**Array&lt;AddressListPdf&gt;**](AddressListPdf.md) |  |  |
| **job_template** | **String** |  |  |
| **payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] |
| **tags** | **Array&lt;String&gt;** |  | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::MultiPdfWithCaptureParams.new(
  address_capture_pdfs: null,
  job_template: null,
  payment_details: null,
  tags: null
)
```


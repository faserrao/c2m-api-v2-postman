# OpenapiClient::SplitPdfWithCaptureParams

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **document_source_identifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  |  |
| **embedded_extraction_specs** | [**Array&lt;ExtractionSpec&gt;**](ExtractionSpec.md) |  |  |
| **payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] |
| **tags** | **Array&lt;String&gt;** |  | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::SplitPdfWithCaptureParams.new(
  document_source_identifier: null,
  embedded_extraction_specs: null,
  payment_details: null,
  tags: null
)
```


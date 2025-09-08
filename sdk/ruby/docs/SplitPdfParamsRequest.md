# OpenapiClient::SplitPdfParamsRequest

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **document_source_identifier** | [**DocumentSourceIdentifier**](DocumentSourceIdentifier.md) |  |  |
| **items** | [**Array&lt;SplitPdfParamsRequestItemsInner&gt;**](SplitPdfParamsRequestItemsInner.md) |  |  |
| **payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] |
| **tags** | **Array&lt;String&gt;** |  | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::SplitPdfParamsRequest.new(
  document_source_identifier: null,
  items: null,
  payment_details: null,
  tags: null
)
```


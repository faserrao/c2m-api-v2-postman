# OpenapiClient::SubmitMultiDocParams

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **items** | [**Array&lt;SubmitMultiDocWithTemplateParamsRequestItemsInner&gt;**](SubmitMultiDocWithTemplateParamsRequestItemsInner.md) |  |  |
| **job_options** | [**JobOptions**](JobOptions.md) |  |  |
| **payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] |
| **tags** | **Array&lt;String&gt;** |  | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::SubmitMultiDocParams.new(
  items: null,
  job_options: null,
  payment_details: null,
  tags: null
)
```


# OpenapiClient::SubmitMultiDocWithTemplateParams

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **items** | [**Array&lt;SubmitMultiDocWithTemplateParamsRequestItemsInner&gt;**](SubmitMultiDocWithTemplateParamsRequestItemsInner.md) |  |  |
| **job_template** | **String** |  |  |
| **payment_details** | [**PaymentDetails**](PaymentDetails.md) |  |  |
| **tags** | **Array&lt;String&gt;** |  | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::SubmitMultiDocWithTemplateParams.new(
  items: null,
  job_template: null,
  payment_details: null,
  tags: null
)
```


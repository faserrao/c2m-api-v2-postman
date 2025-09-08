# OpenapiClient::SubmitSingleDocWithTemplateParamsRequest

## Properties

| Name | Type | Description | Notes |
| ---- | ---- | ----------- | ----- |
| **job_template** | **String** |  |  |
| **payment_details** | [**PaymentDetails**](PaymentDetails.md) |  | [optional] |
| **tags** | **Array&lt;String&gt;** |  | [optional] |

## Example

```ruby
require 'openapi_client'

instance = OpenapiClient::SubmitSingleDocWithTemplateParamsRequest.new(
  job_template: null,
  payment_details: null,
  tags: null
)
```

